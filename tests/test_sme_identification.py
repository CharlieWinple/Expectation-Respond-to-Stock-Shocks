"""v16 diagnostic checks on synthetic data only."""
import re
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from test_sme_rf import environment, synthetic, reference, SCRIPT


def check_preperiod_and_full_run():
    env, source = environment()
    raw = synthetic(env, 600)
    raw[env['USER_COL']] = ['u' + str(i % 120) for i in range(600)]
    raw['wave'] = np.repeat(env['WAVES'], 120)
    # Regenerate wave-specific cells after changing synthetic panel layout.
    raw['size_detail_cell'] = raw['wave'] + '_' + np.where(raw['portfolio_size_raw'].eq(0), 'Z', (np.arange(600) % 3).astype(str))
    starts = dict(zip(env['WAVES'], pd.to_datetime(['2024-06-01','2024-09-01','2024-12-01','2025-03-01','2025-06-01'])))
    env['SHOCK_WINDOW_START_BY_WAVE'] = starts
    raw['submit_dt'] = raw['wave'].map(starts) + pd.Timedelta(days=20)
    raw['sample_sme_owner'] = True
    raw['sample_answer_time'] = True
    raw.loc[0, 'submit_dt'] = starts['2024q3']  # equal start is not pre-shock
    raw.loc[1, 'sample_answer_time'] = False
    original = raw.copy(deep=True)
    lagged, note = env['add_preperiod_targets'](raw)
    pd.testing.assert_frame_equal(raw, original)
    assert lagged.loc[:119, env['PRE_TARGETS']].isna().all().all()
    assert lagged.loc[120:121, env['PRE_TARGETS']].isna().all().all()
    assert lagged.loc[:119, env['INVESTOR_TARGETS']].isna().all().all()
    assert lagged.loc[120:121, env['INVESTOR_TARGETS']].isna().all().all()
    np.testing.assert_allclose(lagged.loc[122, 'pre_aer_bal_age'], raw.loc[2, 'aer_bal_age'])
    np.testing.assert_allclose(lagged.loc[122, 'pre_exp_cpi'], raw.loc[2, 'exp_cpi'])
    duplicate = pd.concat([raw, raw.iloc[[2]]], ignore_index=True)
    lagged_dup, _ = env['add_preperiod_targets'](duplicate)
    assert pd.isna(lagged_dup.loc[122, 'pre_exp_cpi'])
    assert pd.isna(lagged_dup.loc[122, 'pre_aer_bal_age'])
    env.update(df=raw, RUN_BLOCKERS=[])
    for number, cell in enumerate(re.split(r'(?m)^# === CELL \d+:.*$', source)[1:], 1):
        if number >= 8:
            exec(compile(cell, str(SCRIPT) + ':cell' + str(number), 'exec'), env)
    assert len(env['model_rows']) == 132 and len(env['pre_balance']) == 48
    assert len(env['investor_balance']) == 290
    lookup = {(r['Y'], r['group'], r['trait'], r['adjustment']): r for r in env['investor_balance']}
    for r in env['investor_balance']:
        if r['adjustment'] == 'cell':
            raw_row = lookup[(r['Y'], r['group'], r['trait'], 'raw')]
            assert (r['n_obs'], r['dropped']) == (raw_row['n_obs'], raw_row['dropped'])
        if r['note']:
            continue
        if r['Y'] == 'BASE':
            full = env['base_samples'].get(r['group'], env['positive_base'])
            if r['group'] in env['WAVES']:
                full = full.loc[full['wave'].eq(r['group'])]
        else:
            full = env['sample_cache'][('exp_' + r['Y'], r['group'])]
        run = full.loc[full['portfolio_size_raw'].gt(0)].dropna(subset=[r['trait']]).copy()
        spec = env['MODEL_SPECS']['M0'] if r['adjustment'] == 'cell' else {'fe_names': [], 'control_names': []}
        fit, _ = reference(run, r['trait'], spec, env)
        np.testing.assert_allclose([r['beta'], r['se']],
                                  [fit.params[env['CORE_X_VAR']], fit.bse[env['CORE_X_VAR']]], rtol=1e-7, atol=1e-9)
        assert r['provenance'] == 'dated_previous_wave_response'
    q2 = [r for r in env['investor_balance'] if r['group'] == '2024q2']
    assert q2 and all(r['n_obs'] == 0 and r['note'] for r in q2)
    assert any(np.isfinite(r['p']) for r in env['pre_balance'])
    for r in env['pre_balance']:
        if r['note']:
            continue
        full = env['sample_cache'][('exp_' + r['Y'], r['group'])]
        run = full.loc[full['portfolio_size_raw'].gt(0)].dropna(subset=[r['trait']]).copy()
        fit, _ = reference(run, r['trait'], env['MODEL_SPECS'][r['model']], env)
        np.testing.assert_allclose([r['beta'],r['se']], [fit.params[env['CORE_X_VAR']],fit.bse[env['CORE_X_VAR']]], rtol=1e-6, atol=1e-9)
        assert r['n_obs'] + r['dropped'] == int(full['portfolio_size_raw'].gt(0).sum())
    for r in env['model_rows']:
        run = env['sample_cache'][(r['Y'], r['wave_set'])]
        fit, terms = reference(run, r['Y'], env['MODEL_SPECS'][r['model']], env)
        aux = smf.ols(env['CORE_X_VAR'] + ' ~ ' + ' + '.join(terms), run).fit()
        diag = r['identification']
        np.testing.assert_allclose(diag['totals']['residual_SS'], np.sum(aux.resid**2), rtol=1e-7)
        for kind in ['wave','size_bin']:
            groups = [g for g in diag['groups'] if g[0] == kind]
            np.testing.assert_allclose(sum(g[4] for g in groups),1,atol=1e-9)
            np.testing.assert_allclose(sum(g[5] for g in groups),r['beta'],atol=1e-8)
        if r['wave_set'] == 'W4':
            assert all('wc_2024q3' not in term for term in terms)
    rendered = '\n'.join(line for block in env['captured'] for line in block)
    assert 'pre_exp_cpi' in rendered and 'max_abs_user_score' in rendered


def check_unique_rendering_and_alias():
    env, _ = environment()
    env['render_table']('duplicate test', ['wave','target','p','note'],
        [['2024q3','a'*40,0,'-'],['2024q3','b'*40,0,'-']], max_width=35)
    for block in env['captured']:
        assert len(block) == len(set(block)), block
    raw = synthetic(env, 240)
    prepared, _ = env['prepare_wave_cell_design'](raw)
    sample = env['select_design_samples'](prepared, 'exp_cpi')[0]['W5']
    sample[env['CORE_X_VAR']] = sample['wc_2024q3_amount']
    row = env['estimate_rf'](sample,'exp_cpi',env['MODEL_SPECS']['W3'],{})
    assert row['note'] == 'gain_not_separately_identified'
    assert 'identification' not in row


if __name__ == '__main__':
    check_preperiod_and_full_run()
    check_unique_rendering_and_alias()
    print('PASS: dated preperiod joins, direct diagnostic OLS parity, FWL shares/contributions, alias and unique output')
