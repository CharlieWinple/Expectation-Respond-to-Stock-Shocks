"""Synthetic end-to-end checks for the joint duration diagnostic."""
import ast
from pathlib import Path
import numpy as np
import pandas as pd




SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/diagnostics/06_sme_duration_diagnostics.py'

def environment():
    source=SCRIPT.read_text(encoding='utf-8')
    tree=ast.parse(source[:source.index('# === CELL 4:')])
    tree.body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and n.module.startswith('marvel'))]
    captured=[]
    env={'ant_print_all':lambda x,**kw:captured.append(list(dict.fromkeys(x.astype(str)))[:100])}
    exec(compile(tree,str(SCRIPT),'exec'),env)
    return env,source,captured


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
        survey['v1']='我是小微经营者_我自愿参与本次调查'
        survey['extro_info']='answerSeconds=300'
        survey['user_age']=rng.integers(25,65,n)
        survey['city_level_from_yicai']=rng.choice(['tier1','tier2'],n)
        for field,values in [('education',e['COLLEGE_ANSWERS']+e['NONCOLLEGE_ANSWERS']),('firm_year',['2018','2020']),('registration',e['COMPANY_ANSWERS']+['个体工商户']),('industry',['制造业','服务业']),('employee_n',['1','5_9'])]:
            survey[e['TRAIT_VCODES'][field][wave]]=rng.choice(values,n)
        for outcome,codes in e['EXP_VCODES'].items():
            if wave in codes:
                survey[codes[wave]]=rng.choice(list(e['EXP_MAPPING'][outcome]),n)
        survey.loc[n//2:,'v1']='我不是小微经营者'
        survey.loc[n//2::2,'v2']='作为小微经营户的雇员_帮助其收付款'
        survey.loc[n//2+1::2,'v3']='我在工作'
        survey['extro_info']=[None if i%6==0 else 'answerSeconds='+str([0,59,60,119,120,180][i%6]) for i in range(n)]
        if wave in e['QUESTION_CODES']:
            survey.loc[n//2:,e['EDU_CODE'][wave]]='大学本科'
            for c,m in zip(e['QUESTION_CODES'][wave],[e['GDP'],e['HOUSE'],e['CPI'],e['RATE'],e['STOCK_Q3'] if wave=='2024q3' else e['STOCK_LATER']]):
                survey.loc[n//2:,c]=next(iter(m))
            survey.loc[91,e['QUESTION_CODES'][wave][0]]='不确定'
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
    addon=pd.DataFrame({e['ADDON_2024Q2_KEY']:tables[e['SURVEY_TEMPLATE'].format(wave='2024q2')].submit_id})
    for col,outcome in e['ADDON_2024Q2_MACRO_COLS'].items():addon[col]=rng.choice(list(e['EXP_MAPPING'][outcome]),n)
    tables[e['ADDON_2024Q2_TABLE']]=addon
    tables[e['SHOCK_TABLE']]=pd.DataFrame(shocks)
    tables[e['PORT_CONTROL_TABLE']]=pd.DataFrame(history)
    tables[e['HOLDING_TABLE']]=pd.DataFrame(holdings)
    tables[e['PORTRAIT_TABLE']]=pd.DataFrame({e['USER_COL']:ids,e['PORTRAIT_GENDER_COL']:rng.choice(['male','female'],n),e['PORTRAIT_RISK_LEVEL_COL']:'normal'})
    e['ant_read_data']=lambda name,cols:tables[name][cols].copy()
    e['HOLDING_BATCH_USERS']=37 # Force multiple chunks, including last partial.
    exec(source[source.index('# === CELL 4:'):],e)
    # Older platform NumPy rejects nullable pandas boolean arrays even with no NA.
    for name in ['nonowner','explicit','working','owner','employee']:
        assert np.asarray(e[name]).dtype == np.dtype(bool), name
    assert e['explicit'].iloc[90] and not e['working'].iloc[90]
    assert not e['explicit'].iloc[91] and e['working'].iloc[91]
    assert e['employee'].iloc[90] and e['employee'].iloc[91]
    assert not e['employee'].iloc[0]
    assert not e['RUN_BLOCKERS'],e['RUN_BLOCKERS']
    assert e['budget_ok'] and 'DURATION DIAGNOSTIC END' in captured[-1]
    assert all(len(call)<=41 for call in captured)
    tables=e['TABLES']
    for role,scope,total in [('owner','formal5',450),('owner','common4',360),('employee','common4',360)]:
        rows=[r for r in tables['loss'][1] if r[:3]==[role,scope,'A']]
        assert [r[6] for r in rows]==[total,total*5//6,total*3//6,total*2//6]
        bins=[r for r in tables['hist'][1] if r[:3]==[role,scope,'A']]
        assert sum(r[5] for r in bins)==total*5//6 and bins[-1][-1]==1
    items=[r for r in tables['items'][1] if r[:3]==['employee','common4','A'] and r[4]=='exp_gdp']
    assert sum(r[7] for r in items)==4
    assert all(sum(r[6:10])==r[5] for r in tables['items'][1])
    tree=ast.parse(source)
    assert not any(isinstance(node,(ast.Try,ast.Raise)) for node in ast.walk(tree))
    assert 'ant_plot' not in source
    for call in [n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='merge']:
        assert 'validate' in [k.arg for k in call.keywords]
if __name__=='__main__':
    test_full_workflow()
