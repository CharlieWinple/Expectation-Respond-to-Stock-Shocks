"""v19 exact refits, interaction inference and output safety on synthetic data."""
import re
import numpy as np
from scipy.stats import chi2
from test_sme_rf import environment, synthetic, reference, SCRIPT


def check_batch(batch):
    env, source = environment()
    raw = synthetic(env, 300)
    env.update(df=raw, RUN_BATCH=batch, RUN_BLOCKERS=[])
    for number, cell in enumerate(re.split(r'(?m)^# === CELL \d+:.*$', source)[1:], 1):
        if number >= 8:
            exec(compile(cell, str(SCRIPT), 'exec'), env)
    assert env['FIT_COUNTS']['regression'] == 154
    assert len(env['model_rows']) == (154 if batch == 'tail' else 132)
    assert {r['Y'] for r in env['model_rows']} == set(env['Y_VARS'])
    assert all(not k.startswith('_') for r in env['model_rows'] for k in r)
    y = 'exp_cpi'
    broad = env['select_design_samples'](env['df'], y)[0]['W5']
    common = env['select_trait_sample'](broad)[0]
    for model in ['C', 'E']:
        spec = env['AUDIT_SPECS'][model]
        fit, terms = reference(common, y, spec, env)
        if batch == 'tail':
            # Independent FWL projection for exposure selection.
            import statsmodels.formula.api as smf
            aux = smf.ols(env['CORE_X_VAR']+' ~ '+' + '.join(terms), common).fit()
            xr = aux.resid
            positive = common['portfolio_size_raw'].gt(0)
            order = (xr[positive]**2).sort_values(ascending=False, kind='mergesort')
            scores = (xr * fit.resid / (xr @ xr)).groupby(common[env['USER_COL']]).sum().abs()
            for fraction in [.005, .01]:
                scenario = 'residual_' + str(int(fraction*1000))
                trimmed = common.drop(index=order.index[:int(np.ceil(fraction*positive.sum()))])
                assert_refit(env, trimmed, y, spec, scenario)
            for i, user in enumerate(scores.sort_values(ascending=False, kind='mergesort').index[:2], 1):
                trimmed = common.loc[common[env['USER_COL']].ne(user)]
                assert_refit(env, trimmed, y, spec, 'user_'+str(i))
            # Predetermined capital cutoffs do not depend on which outcome is observed.
            for fraction in [.005, .01]:
                cutoff = common['wave'].map(env['capital_cutoffs'][fraction])
                trimmed = common.loc[~positive | common['portfolio_size_raw'].le(cutoff)]
                assert_refit(env, trimmed, y, spec, 'capital_'+str(int(fraction*1000)))
        else:
            for wave in env['WAVES']:
                assert_refit(env, common.loc[common['wave'].ne(wave)], y, spec, 'omit_'+wave)
            # Independent numeric design for per-wave gains and equality covariance.
            import statsmodels.api as sm
            from patsy import dmatrix
            nuisance = np.asarray(dmatrix('1 + '+' + '.join(terms), common))
            gains = np.column_stack([common[env['CORE_X_VAR']].where(common['wave'].eq(w),0)
                                     for w in env['WAVES']])
            direct = sm.OLS(common[y], np.column_stack([gains,nuisance])).fit(
                cov_type='cluster',cov_kwds={'groups':common[env['USER_COL']]})
            slopes = [r for r in env['wave_rows'] if r['Y']==y and r['model']==model]
            np.testing.assert_allclose([r['beta'] for r in slopes],direct.params.iloc[:5],rtol=1e-7)
            np.testing.assert_allclose([r['se'] for r in slopes],direct.bse.iloc[:5],rtol=1e-7)
            R = np.zeros((4,len(direct.params)))
            R[:,0]=-1
            R[np.arange(4),np.arange(1,5)]=1
            delta=R@direct.params
            expected=chi2.sf(delta@np.linalg.solve(R@direct.cov_params()@R.T,delta),4)
            joint=next(r for r in env['joint_rows'] if r['Y']==y and r['model']==model)
            np.testing.assert_allclose(joint['p'],expected,rtol=1e-7)
    rendered='\n'.join(line for block in env['captured'] for line in block)
    assert not any(user in rendered.split() for user in raw[env['USER_COL']].unique())
    if batch=='wave':
        assert len(env['wave_rows'])==110 and len(env['joint_rows'])==22
        q2=[r for r in env['wave_rows'] if r['Y']=='exp_stock' and r['scenario']=='slope_2024q2']
        assert len(q2)==2 and all(r['note']=='wave_unavailable' for r in q2)


def assert_refit(env, run, y, spec, scenario):
    fit,_=reference(run,y,spec,env)
    row=next(r for r in env['model_rows'] if r['Y']==y and r['model']==spec['name'] and r['scenario']==scenario)
    np.testing.assert_allclose([row['beta'],row['se']],
        [fit.params[env['CORE_X_VAR']],fit.bse[env['CORE_X_VAR']]],rtol=1e-7)
    assert row['n_obs']==len(run)


if __name__=='__main__':
    check_batch('tail')
    check_batch('wave')
    env,_=environment()
    rows=[dict(model='C',p=.001,holm_p=np.nan),dict(model='C',p=np.nan,holm_p=np.nan)]
    env['audit_holm'](rows,['model'])
    assert rows[0]['holm_p']==.011
    print('PASS: tail/wave full batches, exact refits, independent wave Wald, absent waves, fixed family Holm, no IDs')
