"""Independent synthetic checks for the standalone owner formal workflow."""
import ast
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from patsy import dmatrix
from test_sme_rf import synthetic

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/analysis/04_sme_owner_formal.py'

class AntPlotStub:
    def __init__(self): self.plots=[]; self.shown=0
    def re_init(self): pass
    def figure_set(self,method,**kwargs):
        assert method in ['set_size_inches','set_dpi']
    def add_subplot(self,*args): pass
    def axes_set(self,method,**kwargs):
        assert method in ['set_xticks','set_xticklabels','set_xlabel','set_ylabel','set_title']
    def plot(self,df,method,kind,axindex,x,discrete,stat,kde,color):
        assert len(df)>=100 and list(df.columns)==['bin_index']
        assert method=='ant_plot_df' and kind=='hist' and discrete and stat=='count' and not kde
        self.plots.append(df.copy())
    def show(self):self.shown+=1

def environment():
    source=SCRIPT.read_text(encoding='utf-8')
    tree=ast.parse(source[:source.index('# === CELL 4:')])
    tree.body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and n.module.startswith('marvel'))]
    captured=[]
    env={'ant_print_all':lambda x,**kw:captured.append(list(dict.fromkeys(x.astype(str)))[:100]),'ant_plot':AntPlotStub()}
    exec(compile(tree,str(SCRIPT),'exec'),env)
    exec(source[source.index('# === CELL 8:'):source.index('# === CELL 9:')],env)
    return env,source,captured

def test_fit_parity():
    e,_,_=environment()
    # Synthetic legacy generator only needs these four names.
    e['CONTROL_NAMES']=e['OWNER_NUM']
    d=synthetic(e,600).dropna(subset=['exp_cpi'])
    for model,formula in [('No controls','1'),('Wave FE','C(wave)'),('Cell FE','C(size_detail_cell)'),
        ('Cell FE + owner controls','C(size_detail_cell)+C(portrait_gender)+C(city_level_from_yicai)+C(survey_industry)+'+'+'.join(e['OWNER_NUM']))]:
        # Reduce nuisance to independent SVD basis, making CR1 rank exact even
        # when category sets are redundant. This is independent dense-dummy OLS.
        nuisance=np.asarray(dmatrix(formula,d))
        u,s,v=np.linalg.svd(nuisance,full_matrices=False)
        z=u[:,s>max(nuisance.shape)*np.finfo(float).eps*s[0]]
        design=np.column_stack([d[e['CORE_X_VAR']],z])
        ref=sm.OLS(d.exp_cpi,design).fit(cov_type='cluster',cov_kwds={'groups':d[e['USER_COL']]})
        r=e['compact_fit'](d,'exp_cpi',model)
        assert not r['note'],r
        np.testing.assert_allclose([r['beta'],r['se'],r['p']],[ref.params.iloc[0],ref.bse.iloc[0],ref.pvalues.iloc[0]],rtol=1e-7,atol=1e-10)
    flat=d.copy(); flat[e['CORE_X_VAR']]=1
    assert e['compact_fit'](flat,'exp_cpi','Cell FE')['note']=='no_residual_gain_variation'
    collinear=d.copy();collinear['aer_bal_age']=collinear[e['CORE_X_VAR']]
    assert e['compact_fit'](collinear,'exp_cpi','Cell FE + owner controls')['note']=='gain_collinear_with_controls'

def test_compute_and_report():
    e,source,captured=environment();e['CONTROL_NAMES']=e['OWNER_NUM']
    d=synthetic(e,600)
    for c in ['aer_bal_college','aer_bal_company']: d[c]=d[c].gt(0).astype(float)
    for c in ['sample_sme_owner','sample_answer_time','sample_unique_user_wave','sample_timing','sample_portfolio_rule','sample_core_x_nonmissing','sample_return_complete']:
        d[c]=True
    # Owner-control and history attrition are distinct and outcome-specific.
    d.loc[3,'aer_bal_age']=np.nan
    d.loc[4,'sample_control_complete']=False
    d.loc[4,'size_detail_cell']=np.nan
    d.loc[5,'sample_sme_owner']=False
    e['df']=d
    exec(source[source.index('# === CELL 9:'):source.index('# === CELL 10:')],e)
    assert captured==[], 'Output escaped before final report'
    assert len(e['model_results'])==66
    assert len(e['sample_results'])==11
    for y in e['Y_VARS']:
        rows=[r for r in e['model_results'] if r[0]=='Common sample' and r[1]==y]
        assert len({r[3] for r in rows})==1
        assert len({r[4] for r in rows})==1
    cpi=next(r for r in e['sample_results'] if r[0]=='exp_cpi')
    assert cpi[-2:]==[1,1],cpi
    assert e['common_mask'].loc[5]==False
    assert (e['df'].loc[e['common_mask'],'wave']=='2024q2').any()
    for scope in ['BASE']+e['Y_VARS']:
        br=[r for r in e['balance_full'] if r[0]==scope]
        for trait in {r[1] for r in br}:
            rr=[r for r in br if r[1]==trait]
            assert len(rr)==3 and len({r[3] for r in rr})==1
    exec(source[source.index('# === CELL 10:'):],e)
    rendered='\n'.join(x for block in captured for x in block)
    assert not e['REPORT_ERRORS'],e['REPORT_ERRORS']
    assert '=== REPORT COMPLETE:' in rendered
    assert [line for call in captured for line in call[1:]]==[line for block in e['REPORT_BLOCKS'] for line in block]
    words=[line.split('|',1)[-1].split() for call in captured for line in call]
    assert sum(len(w)>2 and w[0] in ['Main','Available'] and w[1] in e['OUTCOME_CODES'].values() for w in words)==66
    assert 'pre_aer_' not in rendered
    assert not any(uid in rendered.split() for uid in d[e['USER_COL']].unique())

def test_platform_structure():
    _,s,_=environment();tree=ast.parse(s)
    assert not any(isinstance(n,(ast.Try,ast.Raise)) for n in ast.walk(tree))
    for n in ast.walk(tree):
        if isinstance(n,ast.Call):
            if isinstance(n.func,ast.Name):
                assert n.func.id!='print'
                if n.func.id=='ant_read_data': assert 'cols' in {k.arg for k in n.keywords}
            if isinstance(n.func,ast.Attribute) and n.func.attr=='merge':
                assert 'validate' in {k.arg for k in n.keywords}

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
    assert not e['RUN_BLOCKERS'],e['RUN_BLOCKERS']
    assert len(e['model_results'])==66
    assert sum(e['common_mask'])==5*n
    assert len(e['balance_full'])>0
    assert any('=== REPORT COMPLETE:' in x for block in captured for x in block)

    # Chunked aggregation must equal the original whole-wave aggregation.
    h=e['prep_holding'](tables[e['HOLDING_TABLE']])
    shock=e['prepare_panel_keys'](tables[e['SHOCK_TABLE']])
    hist=e['prepare_panel_keys'](tables[e['PORT_CONTROL_TABLE']])
    for wave in e['WAVES']:
        expected=e['aggregate_shock_to_user'](shock,h,wave).merge(
            e['aggregate_control_to_user'](hist,h,wave),on=e['USER_COL'],validate='one_to_one')
        actual=e['df'].loc[e['df']['wave'].eq(wave)]
        paired=actual.merge(expected,on=e['USER_COL'],suffixes=('_chunk','_whole'),validate='one_to_one')
        for col in [e['CORE_X_VAR'],'portfolio_size_raw','expected_ret_12m','portfolio_risk_12m']:
            np.testing.assert_allclose(paired[col+'_chunk'],paired[col+'_whole'],rtol=1e-12,atol=1e-12,equal_nan=True)

def test_report_output_budget():
    e,source,captured=environment()
    for name in ['flow_rows','sample_results','sample_wave_results','missing_controls',
                 'gain_by_outcome','numeric_distributions','category_distributions',
                 'model_results','balance_summary','balance_full']:
        e[name]=[]
    # All 80 admitted levels for each of the three categorical traits, plus
    # numeric traits, in all 12 scopes. No manual output calls after full run.
    traits=[c+'='+chr(0x4e2d)+str(i) for c in e['OWNER_CAT'] for i in range(80)]+e['OWNER_NUM']+['aer_bal_employee_n']
    for scope in ['BASE']+e['Y_VARS']:
        for trait in traits:
            for model in e['BALANCE_MODELS']:
                e['balance_full'].append([scope,trait,model,10000,8000,.123456,.012345,.012345,.123456,.099999,.199999,''])
        for model in e['BALANCE_MODELS']:
            e['balance_summary'].append([scope,model,len(traits)-1,len(traits)-1,len(traits)-1,.123456,10000,10000])
    e['category_distributions']=[['BASE',c,chr(0x4e2d)+str(i),100,.012345] for c in e['OWNER_CAT'] for i in range(80)]
    hist_base=pd.DataFrame({e['CORE_X_VAR']:np.linspace(-3,4,200),
                            'portfolio_size_raw':np.geomspace(.1,1e7,200)})
    e['HISTOGRAMS'],e['HISTOGRAM_ROWS'],e['HISTOGRAM_AUDIT']=e['prepare_exposure_histograms'](hist_base)
    exec(source[source.index('# === CELL 10:'):],e)
    assert not e['REPORT_ERRORS'],e['REPORT_ERRORS']
    assert len(captured)>4
    assert all(len(call)<=41 for call in captured)
    recovered=[line for call in captured for line in call[1:]]
    assert recovered==[line for block in e['REPORT_BLOCKS'] for line in block]
    for calls in e['REPORT_CALLS']:
        budget=sum(len(('\n'.join(call)).encode('utf-8'))+e['REPORT_CALL_OVERHEAD'] for call in calls)
        assert budget<=e['REPORT_CELL_BUDGET']<50000
    assert 'REPORT COMPLETE' in captured[-1][-1]
    # Oversized unexpected labels fail preflight explicitly, never truncate and
    # announce success or request manual continuation in backend execution.
    captured.clear()
    e['category_distributions']=[['BASE','industry',chr(0x4e2d)*20000,1,1.]]
    exec(source[source.index('# === CELL 10:'):],e)
    assert e['REPORT_ERRORS'] and len(captured)==1
    assert 'PREFLIGHT FAILED' in captured[0][0]


def test_histograms():
    e,_,_=environment()
    gains=np.tile([-100.,-1.,0.,1.,100.],40)
    amounts=np.geomspace(.1,1e6,200)
    base=pd.DataFrame({e['CORE_X_VAR']:np.r_[gains/10000,0,0,np.nan],
                       'portfolio_size_raw':np.r_[amounts,0,np.nan,10.]})
    panels,rows,audit=e['prepare_exposure_histograms'](base)
    assert len(panels)==4 and len(audit)==4
    for panel in panels:
        rr=[r for r in rows if r[0]==panel['key']]
        expected=gains if panel['variable']=='gain' else np.r_[amounts,10.]
        if panel['scale']=='signed_log10_1p':expected=np.sign(expected)*np.log10(1+np.abs(expected))
        elif panel['scale']=='log10_RMB':expected=np.log10(expected)
        counts,_=np.histogram(expected,bins=panel['edges'])
        assert [r[4] for r in rr]==counts.tolist()
        assert sum(r[4] for r in rr)==panel['N'] and abs(sum(r[5] for r in rr)-1)<1e-12
        assert len(panel['data'])==len(expected)
    assert audit[0][1:5]==[201,200,1,40]
    e['render_exposure_histograms'](panels)
    assert len(e['ant_plot'].plots)==4 and e['ant_plot'].shown==2
    small=pd.DataFrame({e['CORE_X_VAR']:[0.]*99,'portfolio_size_raw':[1.]*99})
    p,r,a=e['prepare_exposure_histograms'](small)
    assert all(x['status']=='skip_N_lt_100' for x in p)
    assert len(r)==4 and all(x[4]==99 for x in r)
    e['render_exposure_histograms'](p)
    assert e['ant_plot'].shown==2

if __name__=='__main__':
    test_fit_parity(); test_compute_and_report(); test_platform_structure(); test_full_workflow(); test_report_output_budget(); test_histograms()
    print('PASS: absorbed OLS/CR1 parity, guards, sample accounting, same-wave balance, final-only report, source integration and chunk parity')
