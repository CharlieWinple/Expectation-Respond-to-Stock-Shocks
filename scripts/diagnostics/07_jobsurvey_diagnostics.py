# === CELL 1: Configuration and helpers ===
"""Jobsurvey aggregate diagnostics. Copy marked cells separately into Ant.
No outcome recoding, identity selection, duration deletion or zero imputation.
Inputs confirmed against data/schema/jobsurvey_tables_schema.json.
"""
import numpy as np
import pandas as pd
from marvel.AntPrint import ant_read_data, ant_print_all

SCHEMA_CONFIRMED = True
PREFIX = "frlab_sample_project_202405290032751511010004_v2_job_"
SURVEY_TABLES = {w: PREFIX+"sp_jobsurvey"+w+"_202512" for w in ["2024q2", "2024q3", "2024q4", "2025q1"]}
HOLDING_TABLE = PREFIX+"fund_invest_202512"
PORTRAIT_TABLE = PREFIX+"portrait_202512"
SHOCK_TABLE = "shock_panel_nav_annotated_v1"
USER = "user_id"
SUBMIT = "submit_id"
DATE = "submit_date"
EXTRA = "extro_info"
CONTROLS = ["user_age", "user_gender", "city_level_from_yicai"]
BASIC = [USER, SUBMIT, DATE, EXTRA, "survey_snapshot_id", "user_province_name"]
HUSER, FUND, AMOUNT, HDATE = "匿名化用户id", "基金代码", "当月月底日持有金额元", "日期"
PORTRAIT_COLS = ["性别", "风险等级"]
MONTHS = dict(zip(SURVEY_TABLES, ["2024-05", "2024-08", "2024-11", "2025-02"]))
# Raw option support is exhaustive for <=60 distinct values. Larger fields
# emit numeric summaries only; free text values are never released.
MAX_SUPPORT = 60
BLOCKERS = []
REPORT_CELLS = 8
REPORT_CELL_BUDGET = 44000
REPORT_CALL_OVERHEAD = 512
REPORT = []
PANELS = {}

def table(name, frame):
    # Narrow vertical numeric summaries; no index, pipes or wide one-row tables.
    if len(frame)==1 and len(frame.columns)>6:
        frame=frame.T.reset_index()
        frame.columns=['metric','value']
    REPORT.append(name)
    REPORT.extend(frame.to_string(index=False, max_rows=None, max_cols=None,
                                 float_format=lambda x: format(x,'.6g')).splitlines())


def dates(s):
    # Explicit string formats, including the SME partition-prefix YYYYMMDD form.
    x=text(s)
    result=pd.Series(pd.NaT,index=s.index,dtype='datetime64[ns]')
    for fmt in ['%Y%m%d','%Y-%m-%d','%Y/%m/%d','%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f','%Y-%m-%dT%H:%M:%S']:
        result=result.fillna(pd.to_datetime(x,format=fmt,errors='coerce'))
    tail=x.str.extract(r'(?:^|[^0-9])(\d{8})$')[0]
    return result.fillna(pd.to_datetime(tail,format='%Y%m%d',errors='coerce'))


def text(s):
    return s.astype("string").str.strip().replace("", pd.NA)

def numeric(s):
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)

def distribution(label, s):
    x = numeric(s)
    q = x.quantile([0,.01,.05,.25,.5,.75,.95,.99,1])
    table(label, pd.DataFrame([dict(N=len(s), valid=x.notna().sum(), missing=x.isna().sum(),
          mean=x.mean(), sd=x.std(), negative=x.lt(0).sum(), zero=x.eq(0).sum(),
          **{str(k):v for k,v in q.items()})]))

def support(label, s, free=False):
    x=text(s)
    counts=x.value_counts(dropna=False)
    table(label+' coverage',pd.DataFrame([dict(N=len(x),nonmissing=x.notna().sum(),
          distinct=x.nunique(),missing=x.isna().sum())]))
    if not free and x.nunique()<=MAX_SUPPORT:
        t=counts.rename_axis('option').reset_index(name='N')
        t['pct_all']=100*t.N/len(x) if len(x) else np.nan
        t['pct_nonmissing']=np.where(t.option.notna(),100*t.N/max(1,x.notna().sum()),np.nan)
        table(label+' options',t)
    else:
        REPORT.append(label+' values withheld: free text or high cardinality')
        distribution(label+' numeric only',s)

def fund(s):
    return text(s).str.replace(r"\.0$", "", regex=True).str.zfill(6)

# Wave order is explicit; None means unavailable, never carry another wave forward.
# Full question wording is retained in data/schema/jobsurvey_tables_schema.json.
# Q2 v53 is unresolved, not income. Hukou questions remain distinct.
# Q1 consumption ratio sources stay separate until overlap/conflicts are reviewed.
WAVES = ["2024q2", "2024q3", "2024q4", "2025q1"]
FIELD_MAP = {
    'exp_gdp': ['v94', 'v78', 'v119', 'v82'],
    'exp_cpi': ['v95', 'v79', 'v120', 'v83'],
    'exp_house': ['v96', 'v80', 'v121', 'v84'],
    'exp_stock': ['v97', 'v81', 'v122', 'v85'],
    'exp_rate': ['v98', 'v82', 'v123', None],
    'exp_income': ['v62', 'v62', 'v62', 'v62'],
    'exp_consumption': ['v93', 'v77', 'v79', 'v79'],
    'exp_employment': ['v27', 'v27', 'v27', 'v27'],
    'income_change': ['v54', 'v54', 'v54', 'v54'],
    'consumption_change': ['v81', 'v65', 'v67', 'v67'],
    'work_hours': ['v51', 'v51', 'v52', 'v52'],
    'employment_change': ['v17', 'v17', 'v17', 'v17'],
    'work_income': [None, 'v53', 'v53', 'v53'],
    'education': ['v99', 'v83', 'v124', 'v86'],
    'employment_status': ['v1', 'v1', 'v1', 'v1'],
    'work_type': ['v2', 'v2', 'v2', 'v2'],
    'contract_type': ['v3', 'v3', 'v3', 'v3'],
    'industry': ['v4', 'v4', 'v4', 'v4'],
    'organization_type': ['v7', 'v7', 'v7', 'v7'],
    'position_type': ['v8', 'v8', 'v8', 'v8'],
    'part_time': ['v9', 'v9', 'v9', 'v9'],
    'occupation': ['v10', 'v10', 'v10', 'v10'],
    'in_school': ['v29', 'v29', 'v29', 'v29'],
    'local_hukou': ['v100', None, None, None],
    'household_income': ['v101', None, None, None],
    'housing_type': ['v102', None, None, None],
    'household_size': ['v103', None, None, None],
    'housing_burden': ['v104', None, None, None],
    'consumption_income_ratio': [None, None, 'v80', 'v80'],
    'personal_spending': [None, None, 'v81', 'v81'],
    'debt_status': [None, None, 'v91', None],
    'hukou_type': [None, None, None, 'v87'],
    'consumption_income_ratio_alt': [None, None, None, 'v126'],
    'unresolved_q2_v53': ['v53', None, None, None],
}

LABELS = {
    'exp_gdp': 'GDP预期',
    'exp_cpi': 'CPI预期',
    'exp_house': '房价预期',
    'exp_stock': '股市预期',
    'exp_rate': '借款利率预期',
    'exp_income': '收入预期',
    'exp_consumption': '消费预期',
    'exp_employment': '就业环境预期',
    'income_change': '工资收入变化',
    'consumption_change': '消费变化',
    'work_hours': '每周工时',
    'employment_change': '就业环境变化',
    'work_income': '工作月收入',
    'education': '教育',
    'employment_status': '工作状态',
    'work_type': '工作性质',
    'contract_type': '劳动合同',
    'industry': '行业',
    'organization_type': '单位性质',
    'position_type': '岗位类型',
    'part_time': '兼职情况',
    'occupation': '职业类型',
    'in_school': '在校状态',
    'local_hukou': '常住地户籍',
    'household_income': '家庭年收入',
    'housing_type': '居住方式',
    'household_size': '同住人数',
    'housing_burden': '住房支出比例',
    'consumption_income_ratio': '消费收入比',
    'personal_spending': '个人月支出',
    'debt_status': '未偿还债务',
    'hukou_type': '户籍情况',
    'consumption_income_ratio_alt': '消费收入比补充题',
    'unresolved_q2_v53': '题名待核实',
}

VARIABLE_GROUPS = {'expectations': ['exp_gdp',
                  'exp_cpi',
                  'exp_house',
                  'exp_stock',
                  'exp_rate',
                  'exp_income',
                  'exp_consumption',
                  'exp_employment'],
 'actual_outcomes': ['income_change',
                     'consumption_change',
                     'work_hours',
                     'employment_change',
                     'work_income'],
 'education': ['education'],
 'employment': ['employment_status',
                'work_type',
                'contract_type',
                'industry',
                'organization_type',
                'position_type',
                'part_time',
                'occupation',
                'in_school'],
 'family': ['local_hukou',
            'household_income',
            'housing_type',
            'household_size',
            'housing_burden',
            'consumption_income_ratio',
            'personal_spending',
            'debt_status',
            'hukou_type',
            'consumption_income_ratio_alt'],
 'unresolved': ['unresolved_q2_v53']}

# Derived indexes for existing diagnostics; only FIELD_MAP is maintained by hand.
MAP = {w: {codes[i]: LABELS[n] for n,codes in FIELD_MAP.items() if codes[i] is not None}
       for i,w in enumerate(WAVES)}
QUESTION_GROUPS = {
    w: {group: [FIELD_MAP[n][i] for n in names if FIELD_MAP[n][i] is not None]
        for group,names in VARIABLE_GROUPS.items()}
    for i,w in enumerate(WAVES)
}
EDU = dict(zip(WAVES, FIELD_MAP['education']))
TARGETS = {w: groups['expectations']+groups['actual_outcomes']
           for w,groups in QUESTION_GROUPS.items()}


def question_label(wave, code):
    return MAP[wave].get(code, code)+' ('+code+')'

# === CELL 2: Read confirmed tables ===
READY = SCHEMA_CONFIRMED and all(SURVEY_TABLES.values())
REPORT.append('jobsurvey_diagnostic_v5; selected questions four waves; observed support, not questionnaire codebook')
if not READY:
    REPORT.append('BLOCKED: confirm jobsurvey table names and common fields in Cell 1')
if READY:
    for wave, name in SURVEY_TABLES.items():
        cols=list(dict.fromkeys(BASIC+CONTROLS+list(MAP[wave])))
        PANELS[wave]=ant_read_data(name,cols=cols).copy()

# === CELL 3: Raw support, response quality and sample flow ===
UNIQUE = {}
if READY:
    for wave, raw in PANELS.items():
        raw[USER]=text(raw[USER])
        raw[SUBMIT]=text(raw[SUBMIT])
        valid=raw[USER].notna() & raw[SUBMIT].notna()
        unique=valid & ~raw[USER].duplicated(False) & ~raw[SUBMIT].duplicated(False)
        d=raw.loc[unique].copy()
        d['submitted']=dates(d[DATE])
        matches=text(d[EXTRA]).str.findall(r'(?:^|;)answerSeconds\s*=\s*([^;]*)(?=;|$)')
        seconds=numeric(matches.str[0])
        d['seconds']=seconds.where(matches.str.len().eq(1) & seconds.ge(0))
        flow=[]
        previous=len(raw)
        for label,mask in [('raw',pd.Series(True,index=raw.index)),('valid IDs',valid),('unique user and submission',unique)]:
            n=int(mask.sum())
            flow.append([label,n,previous-n,100*n/len(raw) if len(raw) else np.nan])
            previous=n
        table(wave+' sequential flow',pd.DataFrame(flow,columns=['stage','N','loss_previous','pct_raw']))
        table(wave+' duplicate audit',pd.DataFrame([dict(missing_user=raw[USER].isna().sum(),
            missing_submit=raw[SUBMIT].isna().sum(),duplicate_user_rows=raw.loc[valid,USER].duplicated(False).sum(),
            duplicate_submit_rows=raw.loc[valid,SUBMIT].duplicated(False).sum(),
            duration_multiple=matches.str.len().gt(1).sum(),duration_invalid=d.seconds.isna().sum(),
            invalid_date=d.submitted.isna().sum())]))
        for code,label in MAP[wave].items():
            if code in QUESTION_GROUPS[wave]['unresolved']:
                x=text(raw[code])
                table(wave+' unresolved '+code+' label absent; coverage only',pd.DataFrame([dict(N=len(x),nonmissing=x.notna().sum(),distinct=x.nunique(),missing=x.isna().sum())]))
            else:
                support(wave+' RAW '+code+' '+label,raw[code])
        for code in QUESTION_GROUPS[wave]['family']:
            support(wave+' UNIQUE family '+question_label(wave,code),d[code])
        if wave=='2025q1':
            left,right=text(d.v80),text(d.v126)
            both=left.notna() & right.notna()
            table(wave+' consumption income ratio source audit',pd.DataFrame([dict(
                N=len(d),both=both.sum(),only_v80=(left.notna()&right.isna()).sum(),
                only_v126=(left.isna()&right.notna()).sum(),neither=(left.isna()&right.isna()).sum(),
                same=(both&left.eq(right)).sum(),different=(both&left.ne(right)).sum())]))
        for col in CONTROLS+[EDU[wave]]:
            support(wave+' UNIQUE control '+col,d[col])
            if col=='user_age': distribution(wave+' age numeric',d[col])
        distribution(wave+' duration seconds',d.seconds)
        bins=[0,15,30,60,100,120,180,240,300,600,1200,3600,np.inf]
        counts=pd.cut(d.seconds,bins,right=False).value_counts(sort=False)
        t=counts.rename_axis('seconds_left_closed').reset_index(name='N')
        t['pct_valid']=100*t.N/max(1,d.seconds.notna().sum())
        table(wave+' duration bins',t)
        rows=[]
        for cutoff in [0,30,60,100,120,180,240,300]:
            keep=d.seconds.ge(cutoff)|d.seconds.isna()
            rows.append([cutoff,int(keep.sum()),int((~keep).sum()),int(d.seconds.isna().sum())])
        table(wave+' duration sensitivity, missing retained',pd.DataFrame(rows,columns=['seconds_min','retained','lost','missing_retained']))
        available=d[TARGETS[wave]].apply(text).notna()
        pairs=available.astype(int).T.dot(available.astype(int))
        table(wave+' target co-response counts',pd.DataFrame(
            [[question_label(wave,x),question_label(wave,y),int(pairs.loc[x,y])] for i,x in enumerate(TARGETS[wave]) for y in TARGETS[wave][i:]],
            columns=['target_1','target_2','both_answered']))
        rows=[]
        complete=d[CONTROLS+[EDU[wave]]].apply(text).notna().all(axis=1)
        for c in TARGETS[wave]:
            a=available[c]
            rows.append([question_label(wave,c),len(d),int(a.sum()),int((a&complete).sum()),int((a&~complete).sum())])
        table(wave+' parallel outcome branches (nonblank is not valid coding)',pd.DataFrame(rows,columns=['target','unique_N','answered','controls_nonblank','control_loss']))
        UNIQUE[wave]=d

# === CELL 4: Holdings and passive gain, optional confirmed inputs ===
if READY and HOLDING_TABLE:
    h=ant_read_data(HOLDING_TABLE,cols=[HUSER,FUND,AMOUNT,HDATE]).copy()
    h[HUSER]=text(h[HUSER]); h[FUND]=fund(h[FUND]); h[AMOUNT]=numeric(h[AMOUNT])
    h['date']=dates(h[HDATE])
    h['month']=h.date.dt.strftime('%Y-%m')
    shock=ant_read_data(SHOCK_TABLE,cols=['fund_code','wave','shock_ret_rate_pp','shock_usable','window_start','window_end','return_version']).copy()
    shock['fund_code']=fund(shock.fund_code)
    shock['wave']=text(shock.wave).str.lower().replace({'24q2':'2024q2','24q3':'2024q3','24q4':'2024q4','25q1':'2025q1'})
    for c in ['window_start','window_end']: shock[c]=dates(shock[c])
    shock['r']=numeric(shock.shock_ret_rate_pp).where(numeric(shock.shock_usable).eq(1))
    table('holding invalid date/key audit',pd.DataFrame([dict(invalid_date=h.date.isna().sum(),missing_user=h[HUSER].isna().sum(),missing_fund=h[FUND].isna().sum())]))
    for wave,d in UNIQUE.items():
        hw=h.loc[h.month.eq(MONTHS[wave])].copy()
        sw=shock.loc[shock.wave.eq(wave)].copy()
        ok=(h.date.notna().all() and len(hw)>0 and len(sw)>0 and hw.date.nunique()==1 and
            not hw.duplicated([HUSER,FUND]).any() and not sw.fund_code.duplicated().any() and
            sw.fund_code.notna().all() and sw.window_start.notna().all() and sw.window_end.notna().all() and
            sw.window_start.nunique()==1 and sw.window_end.nunique()==1 and
            sw.return_version.eq('nav_price_annotated_v1').all())
        if ok:
            start,end=sw.window_start.iloc[0],sw.window_end.iloc[0]
            ok=hw.date.max()==pd.Period(MONTHS[wave],freq='M').end_time.normalize() and hw.date.max()<start<=end
        table(wave+' holdings input gate',pd.DataFrame([dict(ok=ok,rows=len(hw),snapshots=hw.date.nunique(),duplicate_holding_rows=hw.duplicated([HUSER,FUND],False).sum(),duplicate_shock_rows=sw.fund_code.duplicated(False).sum())]))
        if ok:
            hw['bad']=hw[AMOUNT].isna()|hw[AMOUNT].lt(0)|hw[FUND].isna()
            z=hw.loc[hw[HUSER].notna()].merge(sw[['fund_code','r']],left_on=FUND,right_on='fund_code',how='left',validate='many_to_one')
            z['covered']=z[AMOUNT].where(z.r.notna(),0)
            z['gain']=z[AMOUNT]*z.r/1e6
            a=z.groupby(HUSER).agg(capital=(AMOUNT,lambda x:x.sum(min_count=1)),covered=('covered','sum'),bad=('bad','max'),gain=('gain',lambda x:x.sum(min_count=1)),funds=(FUND,'nunique')).reset_index()
            a['coverage']=a.covered/a.capital
            a['gain']=numeric(a.gain).where(~a.bad & a.coverage.ge(.999999))
            a['capital']=a.capital.where(~a.bad)
            a['coverage']=a.coverage.where(~a.bad)
            a.loc[~a.bad&a.capital.eq(0),'gain']=0
            d=d.merge(a,left_on=USER,right_on=HUSER,how='left',validate='one_to_one',indicator=True)
            d['holding_status']=np.select([x.fillna(False).to_numpy(dtype=bool) for x in [d._merge.eq('left_only'),d.bad.eq(True),d.capital.eq(0),d.capital.gt(0)]],['unmatched','invalid','recorded_zero','positive'],default='unknown')
            support(wave+' holding status',d.holding_status)
            for c in ['capital','coverage','gain','funds']: distribution(wave+' '+c+' (gain: 10000 yuan)',d[c])
            table(wave+' calendar',pd.DataFrame([[str(hw.date.max().date()),str(start.date()),str(end.date())]],columns=['holding_date','shock_start','shock_end']))
            base=d.submitted.dt.normalize().gt(end.normalize())
            masks=[('unique',pd.Series(True,index=d.index)),('post shock',base),('matched',base & d._merge.eq('both')),('valid holdings',base & d._merge.eq('both') & d.bad.eq(False)),('gain covered',base & d.gain.notna())]
            previous=len(d); rows=[]
            for label,mask in masks:
                n=int(mask.sum()); rows.append([label,n,previous-n]); previous=n
            table(wave+' exposure sequential losses',pd.DataFrame(rows,columns=['stage','N','loss_previous']))
            eligible=base & d.gain.notna()
            control_ok=d[CONTROLS+[EDU[wave]]].apply(text).notna().all(axis=1) & numeric(d.user_age).between(16,100)
            rows=[]
            for target in TARGETS[wave]:
                answer=text(d[target]).notna()
                rows.append([question_label(wave,target),int(eligible.sum()),int((eligible&control_ok).sum()),int((eligible&control_ok&answer).sum()),int((eligible&control_ok&~answer).sum())])
            table(wave+' exposure control outcome branches',pd.DataFrame(rows,columns=['target','exposure_N','controls_N','answered_N','answer_loss']))
            for cutoff in [0,30,60,100,120,180,240,300]:
                keep=d.seconds.ge(cutoff)|d.seconds.isna()
                table(wave+' exposure duration '+str(cutoff),pd.DataFrame([[int(eligible.sum()),int((eligible&keep).sum()),int((eligible&~keep).sum())]],columns=['before','retained','lost']))
            for scope, subset in [('positive',d.loc[d.capital.gt(0)]),('post_window',d.loc[base])]:
                for c in ['capital','gain']: distribution(wave+' '+scope+' '+c,subset[c])
            x=d.gain.dropna().abs().sort_values(ascending=False)
            table(wave+' absolute gain concentration',pd.DataFrame([
                dict(top_fraction=f, n=int(np.ceil(len(x)*f)), share=x.iloc[:int(np.ceil(len(x)*f))].sum()/x.sum() if x.sum()>0 else np.nan)
                for f in [.01,.05,.10]]))
            for status,g in d.groupby('holding_status'):
                distribution(wave+' duration by '+status,g.seconds)
                for c in CONTROLS+[EDU[wave]]: support(wave+' control by '+status+' '+c,g[c])
            UNIQUE[wave]=d
        else:
            BLOCKERS.append(wave+' exposure input gate')
            REPORT.append(wave+' gain BLOCKED: date, snapshot, duplicate, version or window gate failed')
elif READY: REPORT.append('Holdings/gain BLOCKED: HOLDING_TABLE not confirmed; no unmatched-as-zero assumption')

# === CELL 5: Portrait and repeated participation ===
if READY and PORTRAIT_TABLE:
    p=ant_read_data(PORTRAIT_TABLE,cols=[HUSER]+PORTRAIT_COLS).copy()
    p[HUSER]=text(p[HUSER])
    table('portrait keys',pd.DataFrame([dict(rows=len(p),missing=p[HUSER].isna().sum(),duplicate_rows=p[HUSER].duplicated(False).sum())]))
    p=p.loc[p[HUSER].notna() & ~p[HUSER].duplicated(False)]
    for wave,d in UNIQUE.items():
        g=d[[USER]].merge(p,left_on=USER,right_on=HUSER,how='left',validate='one_to_one')
        for c in PORTRAIT_COLS: support(wave+' portrait '+c,g[c])
if READY:
    rows=[]
    for w,a in UNIQUE.items():
        for v,b in UNIQUE.items():
            rows.append([w,v,len(set(a[USER])&set(b[USER])),len(a)])
    table('participation overlap; denominator=row wave unique users',pd.DataFrame(rows,columns=['wave','other_wave','overlap','denominator']))
REPORT.append('COMPUTATION END status='+('BLOCKED' if BLOCKERS else 'COMPLETED')+'; issues='+','.join(BLOCKERS))

# === CELL 6: Preflight complete numeric report and emit block 1 ===
# <=40 data lines/call; actual UTF-8 text plus 512-byte reserve/call.
# Multiple calls share a cell budget. Never discard lines to fit a fixed count.
def call_bytes(call):
    return len("\n".join(call).encode('utf-8'))+REPORT_CALL_OVERHEAD


def prepare_report(lines):
    calls=[]
    batch=[]
    errors=[]
    for line in lines:
        # A repeated string must go to a different unique-mode call.
        candidate=['REPORT']+batch+[line]
        if batch and (len(batch)==40 or line in batch or call_bytes(candidate)>REPORT_CELL_BUDGET):
            calls.append(['REPORT']+batch)
            batch=[]
        if call_bytes(['REPORT',line])>REPORT_CELL_BUDGET:
            errors.append('single report line exceeds cell budget')
        batch.append(line)
    if batch:
        calls.append(['REPORT']+batch)
    blocks=[[]]
    budgets=[0]
    for call in calls:
        cost=call_bytes(call)
        if blocks[-1] and budgets[-1]+cost>REPORT_CELL_BUDGET:
            blocks.append([])
            budgets.append(0)
        blocks[-1].append(call)
        budgets[-1]+=cost
    if any(b>REPORT_CELL_BUDGET for b in budgets):
        errors.append('report cell budget exceeded')
    return blocks,budgets,errors


REPORT_CALLS,REPORT_BYTES,REPORT_ERRORS=prepare_report(REPORT)
# Compatibility indexes also enable checks of line preservation and completeness.
PAGES=[[line for call in calls for line in call[1:]] for calls in REPORT_CALLS]
EMITTED_PAGES=set()


def report_page(i):
    if REPORT_ERRORS:
        if i==0:
            ant_print_all(pd.Series(['REPORT PREFLIGHT FAILED; no partial report']+
                                    sorted(set(REPORT_ERRORS))),model_method='unique')
    elif i<len(REPORT_CALLS):
        for call in REPORT_CALLS[i]:
            ant_print_all(pd.Series(call),model_method='unique')
        EMITTED_PAGES.add(i)


def report_completion():
    missing=sorted(set(range(len(PAGES)))-EMITTED_PAGES)
    complete=not REPORT_ERRORS and not missing
    lines=['REPORT COMPLETE' if complete else 'REPORT INCOMPLETE',
           'blocks='+str(len(PAGES))+' emitted='+str(len(EMITTED_PAGES)),
           'data_lines='+str(len(REPORT)),
           'status='+('BLOCKED' if BLOCKERS or REPORT_ERRORS else 'COMPLETED' if complete else 'INCOMPLETE'),
           'gain units: 10000 yuan; unmatched holdings remain missing']
    if missing:
        lines+=['Continuation required: execute each report_page(i) in its OWN new notebook cell.',
                'Then run report_completion() in another cell.',
                'First missing index='+str(missing[0])+'; total blocks='+str(len(PAGES))]
    ant_print_all(pd.Series(lines),model_method='unique')


report_page(0)

# === CELL 7: Numeric report block 2 ===
report_page(1)

# === CELL 8: Numeric report block 3 ===
report_page(2)

# === CELL 9: Numeric report block 4 ===
report_page(3)

# === CELL 10: Numeric report block 5 ===
report_page(4)

# === CELL 11: Numeric report block 6 ===
report_page(5)

# === CELL 12: Numeric report block 7 ===
report_page(6)

# === CELL 13: Numeric report block 8 ===
report_page(7)

# === CELL 14: Verify report completeness ===
report_completion()
