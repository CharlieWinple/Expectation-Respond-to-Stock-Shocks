"""Independent synthetic checks for the standalone employee formal workflow."""
import ast
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm



SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/analysis/05_sme_employee_formal.py'

def environment(source=None):
    if source is None:
        source=SCRIPT.read_text(encoding='utf-8')
    tree=ast.parse(source[:source.index('# === CELL 4:')])
    tree.body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and n.module.startswith('marvel'))]
    captured=[]
    env={'ant_print_all':lambda x,**kw:captured.append(list(dict.fromkeys(x.astype(str)))[:100])}
    exec(compile(tree,str(SCRIPT),'exec'),env)
    exec(source[source.index('# === CELL 8:'):source.index('# === CELL 9:')],env)
    return env,source,captured

def test_formal_parity():
    e,source,_=environment()
    owner=SCRIPT.with_name('04_sme_owner_formal.py').read_text(encoding='utf-8')
    for name in ['balance_rows']:
        left=next(n for n in ast.parse(owner).body if isinstance(n,ast.FunctionDef) and n.name==name)
        right=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==name)
        assert ast.dump(left)==ast.dump(right).replace('employee','owner').replace('EMPLOYEE','OWNER')
    survey=pd.DataFrame({c:[None] for c in e['get_survey_cols']('2024q3')})
    survey['v1']='我不是小微经营者'
    survey['v3']='我在工作'
    survey['user_age']=15
    survey['v39']=e['MIXED_EDUCATION']
    coded=e['code_employee_survey'](survey,'2024q3')
    assert coded.aer_bal_age.iloc[0]==15
    assert coded.aer_bal_college.isna().all() and not e['RUN_BLOCKERS']

def test_full_workflow():
    e,source,captured=environment()
    n=180
    rng=np.random.default_rng(46)
    ids=[f'owner_{i}' for i in range(n)]
    tables={}; shocks=[]; history=[]; holdings=[]
    for wave in e['WAVES']:
        month=e['WAVE_HOLDING_MONTH'][wave]
        start=(month+1).start_time
        end=start+pd.Timedelta(days=20)
        survey=pd.DataFrame({c:[None]*n for c in e['get_survey_cols'](wave)})
        survey['user_id']=ids
        survey['submit_id']=[wave+'_'+str(i) for i in range(n)]
        survey['submit_date']=str((end+pd.Timedelta(days=1)).date())
        survey['extro_info']='answerSeconds=300'
        survey['user_age']=rng.integers(25,65,n)
        survey['city_level_from_yicai']=rng.choice(['tier1','tier2'],n)
        survey['v1']='我不是小微经营者'
        survey.loc[0,'v1']='我是小微经营者_我自愿参与本次调查'
        survey.loc[1::2,'v2']='作为小微经营户的雇员_帮助其收付款'
        survey.loc[::2,'v3']='我在工作'
        survey.loc[2,'v3']='退休'
        survey.loc[3,'extro_info']='answerSeconds=99'
        survey.loc[7,'extro_info']='answerSeconds=100'
        survey.loc[4,'extro_info']=None
        survey[e['EDU_CODE'][wave]]=rng.choice(['大学本科','初中'],n)
        survey.loc[5,e['EDU_CODE'][wave]]='不便透露'
        mappings=[e['GDP'],e['HOUSE'],e['CPI'],e['RATE'],
                  e['STOCK_Q3'] if wave=='2024q3' else e['STOCK_LATER']]
        for code,mapping in zip(e['QUESTION_CODES'][wave],mappings):
            survey[code]=rng.choice(list(mapping),n)
        survey.loc[6,e['QUESTION_CODES'][wave][0]]='不确定'
        tables[e['SURVEY_TEMPLATE'].format(wave=wave)]=survey
        for j in range(8):
            code=f'{j:06d}'
            shocks.append({e['FUND_COL_PANEL']:code,'wave':wave,e['SHOCK_RET_PP_COL']:rng.normal(1,4),e['SHOCK_USABLE_COL']:1,e['SHOCK_WINDOW_START_COL']:str(start.date()),e['SHOCK_WINDOW_END_COL']:str(end.date()),'return_version':e['EXPECTED_FUND_RETURN_VERSION'],'screen_pass_all_checks':1})
            for m in pd.period_range(end=month,periods=12,freq='M'):
                history.append({e['FUND_COL_PANEL']:code,'wave':wave,e['CONTROL_MONTH_COL']:str(m),e['CONTROL_MONTHLY_RET_COL']:rng.normal(0,.03),'return_version':e['EXPECTED_FUND_RETURN_VERSION'],'screen_pass_all_checks':1})
        for i,uid in enumerate(ids):
            if i%15==0: continue # unmatched zero
            for j in [i%8,(i+1)%8]:
                holdings.append({e['USER_COL']:uid,e['FUND_COL_HOLDING']:f'{j:06d}',e['HOLDING_AMT_COL']:0 if i%13==0 else float(rng.uniform(1000,500000)),e['REALIZED_GAIN_MONTH_COL']:0,e['HOLDING_DATE_COL']:month.end_time.strftime('%Y%m%d')})
    tables[e['SHOCK_TABLE']]=pd.DataFrame(shocks)
    tables[e['PORT_CONTROL_TABLE']]=pd.DataFrame(history)
    tables[e['HOLDING_TABLE']]=pd.DataFrame(holdings)
    tables[e['PORTRAIT_TABLE']]=pd.DataFrame({e['USER_COL']:ids,e['PORTRAIT_GENDER_COL']:rng.choice(['male','female'],n),e['PORTRAIT_RISK_LEVEL_COL']:'normal'})
    e['ant_read_data']=lambda name,cols:tables[name][cols].copy()
    e['HOLDING_BATCH_USERS']=37 # Force multiple chunks, including last partial.
    import re
    cells = re.split(r'(?m)^# === CELL ', source)[1:]
    assert [int(cell.split(':', 1)[0]) for cell in cells] == list(range(1, 19))
    for number, cell in enumerate(cells[3:], 4):
        exec('# === CELL ' + cell, e)
        if number <= 11:
            assert not captured, 'Computation cells must not emit output'
    assert len(captured) > 0
    assert not e['RUN_BLOCKERS'],e['RUN_BLOCKERS']
    assert len(e['model_results'])==30
    assert sum(e['common_mask'])==4*(n-4)
    assert len(e['balance_full'])>0
    assert e['WAVES'] == ['2024q3', '2024q4', '2025q1', '2025q2']
    assert set(e['df'].wave) == set(e['WAVES'])
    assert e['EDU_CODE'] == {'2024q3':'v39', '2024q4':'v25', '2025q1':'v26', '2025q2':'v26'}
    assert e['ANSWER_SECONDS_MIN'] == 100
    assert not any('addon' in line.lower() or 'five-wave' in line for block in captured for line in block)
    assert any('=== REPORT COMPLETE:' in x for block in captured for x in block)


    base=e['df'].loc[e['common_mask']]
    assert not base[e['USER_COL']].eq(ids[3]).any()  # 99 seconds excluded.
    assert base[e['USER_COL']].eq(ids[7]).sum()==4  # 100 seconds included.
    assert base[e['USER_COL']].eq(ids[4]).sum()==4  # Missing duration retained.
    assert base.recorded_zero_portfolio.any() and base.imputed_zero_portfolio.any()
    assert base.loc[base.recorded_zero_portfolio | base.imputed_zero_portfolio,'passive_gain'].eq(0).all()
    assert len(e['sample_results'])==5 and e['sample_results'][0][4]==len(base)-4
    # Independent explicit-dummy fit on the all-holdings GDP common sample.
    g=base.loc[base.exp_gdp.notna()]
    x=pd.concat([g[['passive_gain','aer_bal_age','aer_bal_college']],
                 pd.get_dummies(g[['size_detail_cell','portrait_gender','city_level_from_yicai']],
                                drop_first=True,dtype=float)],axis=1)
    fit=sm.OLS(g.exp_gdp,sm.add_constant(x).astype(float)).fit(cov_type='cluster',cov_kwds={'groups':g[e['USER_COL']]})
    row=next(r for r in e['model_results'] if r[:3]==['Common sample','exp_gdp',e['FORMAL_MODELS'][-1]])
    np.testing.assert_allclose([row[5],row[6]],[fit.params['passive_gain'],fit.bse['passive_gain']],rtol=1e-8)
    assert len(e['selection_models']) == 25
    for topic, wide_n, kept, dropped, patterns, light_n, education_loss in e['selection_checks']:
        assert wide_n == kept + dropped == patterns
        assert light_n == kept + education_loss
        stages = {r[1]: r for r in e['selection_models'] if r[0] == topic}
        assert stages['A_wide'][2] == wide_n
        assert stages['B_complete'][2] == stages['C_full_controls'][2] == kept
        assert stages['E1_light_sample'][2] == light_n
        refs = {r[1]: r for r in e['selection_variation'] if r[0] == topic}
        np.testing.assert_allclose(refs['wide'][5], refs['kept'][5]+refs['dropped'][5])
        for scope in ['wide', 'kept', 'dropped']:
            profile = next(r for r in e['selection_profile'] if r[:2] == [topic, scope])
            assert profile[2] == sum(profile[4:7])
            assert sum(r[3] for r in e['selection_wave'] if r[:2] == [topic, scope]) == profile[2]
        # E1 and E2 must use their own sample and omit education in the actual fit.
        for stage, mask in [('E1_light_sample', e['cell_mask'] & e['df'][e['LIGHT_CONTROLS']].notna().all(axis=1)),
                            ('E2_complete_light', e['common_mask'])]:
            part=e['df'].loc[mask & e['df'][topic].notna()]
            design=pd.concat([part[[e['CORE_X_VAR'],'aer_bal_age']],
                              pd.get_dummies(part[['size_detail_cell','portrait_gender','city_level_from_yicai']],
                                             drop_first=True,dtype=float)],axis=1)
            independent=sm.OLS(part[topic],sm.add_constant(design).astype(float)).fit(
                cov_type='cluster',cov_kwds={'groups':part[e['USER_COL']]})
            np.testing.assert_allclose(stages[stage][4:6],
                [independent.params[e['CORE_X_VAR']],independent.bse[e['CORE_X_VAR']]],rtol=1e-8)
    selection_calls=[call for call in captured if call and call[0].startswith('SELECTION ')]
    assert all(len(call)<=39 for call in selection_calls)
    assert sum('END SELECTION' in line for call in selection_calls for line in call)==3
    assert all('BLOCK SELECTION' not in line for call in captured for line in call)
    assert not e['REPORT_ERRORS']
    tree=ast.parse(source)
    assert not any(isinstance(node,(ast.Try,ast.Raise)) for node in ast.walk(tree))
    assert all(len(call)<=41 for block in e['REPORT_CALLS'] for call in block)
    # Empty kept sample, multiple missing controls and zero exposure variation.
    e['df']['aer_bal_college'] = np.nan
    e['df'].loc[e['df'].index[:10], 'aer_bal_age'] = np.nan
    e['df'][e['CORE_X_VAR']] = 0.
    exec(source[source.index('# === CELL 10:'):], e)
    assert all(r[2] == 0 for r in e['selection_checks'])
    assert all(r[7] == 0 for r in e['selection_variation'])
    assert all(r[-1] in ['insufficient_observations_or_clusters', 'no_residual_gain_variation']
               for r in e['selection_models'])


if __name__=='__main__':
    test_formal_parity()
    test_full_workflow()
