# === CELL 1: Configuration and helpers ===
"""Jobsurvey aggregate diagnostics. Copy marked cells separately into Ant.
No outcome recoding, identity selection or duration deletion.
Supplement only: submission timing and candidate month-end holdings.
Completed questionnaire, control and legacy gain diagnostics are not rerun.
Inputs confirmed against data/schema/jobsurvey_tables_schema.json.
"""
import numpy as np
import pandas as pd
from marvel.AntPrint import ant_read_data, ant_print_all

SCHEMA_CONFIRMED = True
PREFIX = "frlab_sample_project_202405290032751511010004_v2_job_"
SURVEY_TABLES = {w: PREFIX+"sp_jobsurvey"+w+"_202512" for w in ["2024q2", "2024q3", "2024q4", "2025q1"]}
HOLDING_TABLE = PREFIX+"fund_invest_202512"
VERSION = 'jobsurvey_diagnostic_v7_supplement'
USER = "user_id"
SUBMIT = "submit_id"
DATE = "submit_date"
EXTRA = "extro_info"
CONTROLS = ["user_age", "user_gender", "city_level_from_yicai"]
BASIC = [USER, SUBMIT, DATE, EXTRA]
HUSER, FUND, AMOUNT, HDATE = "匿名化用户id", "基金代码", "当月月底日持有金额元", "日期"
# Raw option support is exhaustive for <=60 distinct values. Larger fields
# emit numeric summaries only; free text values are never released.
MAX_SUPPORT = 60
BLOCKERS = []
REPORT_CELLS = 3
REPORT_CELL_BUDGET = 44000
REPORT_CALL_OVERHEAD = 512
REPORT = []
PANELS = {}
WINDOWS = []
CANDIDATE_PANELS = {}
REPORT_CONTEXT = ''

def table(name, frame):
    # Narrow vertical numeric summaries; no index, pipes or wide one-row tables.
    if len(frame)==1 and len(frame.columns)>6:
        frame=frame.T.reset_index()
        frame.columns=['metric','value']
    REPORT.append(REPORT_CONTEXT+name)
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


def submit_dates(s):
    # Survey dates must match a whole date/timestamp, never an arbitrary suffix.
    x=text(s)
    result=pd.Series(pd.NaT,index=s.index,dtype='datetime64[ns]')
    for pattern,fmt in [
        (r'\d{8}','%Y%m%d'),(r'\d{4}-\d{2}-\d{2}','%Y-%m-%d'),
        (r'\d{4}/\d{2}/\d{2}','%Y/%m/%d'),
        (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}','%Y-%m-%d %H:%M:%S'),
        (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}','%Y-%m-%dT%H:%M:%S'),
        (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{1,9}','%Y-%m-%d %H:%M:%S.%f'),
        (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,9}','%Y-%m-%dT%H:%M:%S.%f')]:
        result=result.fillna(pd.to_datetime(x.where(x.str.fullmatch(pattern,na=False)),format=fmt,errors='coerce'))
    return result


def submission_audit(wave,raw,valid,unique,d):
    parsed=submit_dates(raw[DATE]); day=parsed.dt.normalize()
    first,last=parsed.min(),parsed.max()
    for scope,mask in [('RAW',pd.Series(True,index=raw.index)),('ID_VALID',valid),('UNIQUE',unique)]:
        t=parsed.loc[mask]; source=text(raw.loc[mask,DATE])
        table(wave+' submit summary '+scope,pd.DataFrame([dict(
            N=len(t),parsed=t.notna().sum(),blank=source.isna().sum(),
            unparsed_nonblank=(source.notna()&t.isna()).sum(),
            earliest=str(t.min()),latest=str(t.max()),distinct_days=t.dt.normalize().nunique(),
            timestamp_rows=(source.str.contains(r'[ T]\d{2}:',na=False)&t.notna()).sum(),
            outside_wave_quarter=(t.notna()&t.dt.to_period('Q').astype('string').str.lower().ne(wave)).sum())]))
    daily=pd.DataFrame({'day':day,'raw_N':1,'ID_valid_N':valid.astype(int),'unique_N':unique.astype(int)})
    daily=daily.loc[day.notna()].groupby('day',as_index=False).sum().sort_values('day')
    daily['pct_raw']=100*daily.raw_N/max(1,len(raw))
    daily['cum_pct_dated']=100*daily.raw_N.cumsum()/max(1,parsed.notna().sum())
    daily['gap_days']=daily.day.diff().dt.days
    table(wave+' submit daily counts; observed days only; missing dates in summary',daily)
    if parsed.notna().any():
        # Discrete order statistics, no interpolated dates.
        q=parsed.dropna().sort_values().reset_index(drop=True)
        table(wave+' submit date quantiles RAW',pd.DataFrame([
            [p,str(q.iloc[int(np.floor(p*(len(q)-1)))])] for p in [0,.01,.05,.25,.5,.75,.95,.99,1]
        ],columns=['quantile','timestamp']))
        d['days_since_first_submit']=(d.submitted.dt.normalize()-first.normalize()).dt.days
        distribution(wave+' UNIQUE days since first RAW submission',d.days_since_first_submit)
        timing=d.assign(submit_day=d.submitted.dt.normalize(),
                        seconds_valid=d.seconds.notna(),under100=d.seconds.lt(100),under180=d.seconds.lt(180))
        timing=timing.groupby('submit_day').agg(N=(USER,'size'),duration_valid=('seconds_valid','sum'),
            median_seconds=('seconds','median'),under100=('under100','sum'),under180=('under180','sum')).reset_index()
        table(wave+' UNIQUE daily duration quality',timing)
        anchor=first.normalize()
        ready=bool(parsed.notna().all())
        for lag in [1,2]:
            baseline=(anchor.to_period('M')-lag).end_time.normalize()
            end=anchor-pd.Timedelta(days=1)
            row=dict(wave=wave,lag_months=lag,first_submit=str(first),last_submit=str(last),
                     holding_date=baseline,return_start=baseline+pd.Timedelta(days=1),return_end=end,
                     return_days=(end-baseline).days,date_ready=ready,
                     status='DATE_ERRORS' if not ready else 'NO_RETURN_DAYS' if end<=baseline else 'AWAIT_JOB_RETURNS')
            WINDOWS.append(row)
            table(wave+' JOB candidate window '+str(lag),pd.DataFrame([row]))
        table(wave+' first-date audit',pd.DataFrame([dict(
            first_day_raw=day.eq(anchor).sum(),first_day_unique=(day.eq(anchor)&unique).sum(),
            first_day_bad_ID=(day.eq(anchor)&~valid).sum(),
            first_day_nonunique=(day.eq(anchor)&valid&~unique).sum(),
            unique_first_differs=bool(pd.notna(d.submitted.min()) and d.submitted.min().normalize()!=anchor))]))
    else:
        BLOCKERS.append(wave+' no parsed submission dates')
        REPORT.append(wave+' JOB windows unavailable: no parsed submission dates')


def capital_bins(label,capital):
    bins=[0,10,100,1000,10000,100000,np.inf]
    counts=pd.cut(capital.where(capital.gt(0)),bins).value_counts(sort=False)
    t=counts.rename_axis('capital_yuan_right_closed').reset_index(name='N')
    t['capital_yuan_right_closed']=t.capital_yuan_right_closed.astype(str)
    t=pd.concat([pd.DataFrame([{'capital_yuan_right_closed':'zero','N':int(capital.eq(0).sum())}]),t],ignore_index=True)
    t['pct_all']=100*t.N/max(1,len(capital))
    table(label,t)
    table(label+' missing',pd.DataFrame([dict(N=len(capital),missing=capital.isna().sum())]))


def candidate_holdings(h):
    for window in WINDOWS:
        wave,lag=window['wave'],window['lag_months']; label=wave+' JOB lag'+str(lag)
        base=window['holding_date']; hw=h.loc[h.month.eq(base.strftime('%Y-%m'))].copy()
        ok=(window['date_ready'] and window['return_days']>0 and len(hw)>0 and
            h.date.notna().all() and h[HUSER].notna().all() and
            hw.date.eq(base).all() and not hw.duplicated([HUSER,FUND]).any())
        table(label+' snapshot gate',pd.DataFrame([dict(holding_date=str(base.date()),
            rows=len(hw),dates=hw.date.nunique(),off_month_end=(~hw.date.eq(base)).sum(),
            duplicate_rows=hw.duplicated([HUSER,FUND],False).sum(),ready=ok)]))
        if ok:
            hw['bad']=hw[AMOUNT].isna()|hw[AMOUNT].lt(0)|hw[FUND].isna()
            a=hw.groupby(HUSER).agg(capital=(AMOUNT,lambda x:x.sum(min_count=1)),bad=('bad','max')).reset_index()
            a['capital']=a.capital.where(~a.bad)
            d=UNIQUE[wave].merge(a,left_on=USER,right_on=HUSER,how='left',validate='one_to_one',indicator=True)
            d.loc[d._merge.eq('left_only'),'capital']=0
            d['holding_status']=np.select([d.capital.eq(0),d.capital.gt(0)],['zero','positive'],default='invalid')
            # No SME return is ever used to populate this candidate gain.
            d['job_gain']=np.where(d.capital.eq(0),0,np.nan)
            CANDIDATE_PANELS[(wave,lag)]=d
            support(label+' holding status',d.holding_status)
            distribution(label+' capital yuan',d.capital)
            capital_bins(label+' capital bins',d.capital)
            table(label+' gain readiness',pd.DataFrame([dict(zero_gain_known=d.capital.eq(0).sum(),
                positive_await_returns=d.capital.gt(0).sum(),invalid_holdings=d.capital.isna().sum())]))
            control=d[CONTROLS+[EDU[wave]]].apply(text).notna().all(axis=1)&numeric(d.user_age).between(16,100)
            table(label+' holdings control outcome branches; BEFORE return availability',pd.DataFrame([
                [question_label(wave,c),len(d),int(d.capital.notna().sum()),int((d.capital.notna()&control).sum()),
                 int((d.capital.notna()&control&text(d[c]).notna()).sum())] for c in TARGETS[wave]
            ],columns=['target','unique_N','valid_holdings_N','controls_N','answered_N']))
        else:
            BLOCKERS.append(label+' snapshot/date gate')
            REPORT.append(label+' holdings unavailable; never infer all-zero from missing snapshot')
    for wave in UNIQUE:
        if (wave,1) in CANDIDATE_PANELS and (wave,2) in CANDIDATE_PANELS:
            a=CANDIDATE_PANELS[(wave,1)][[USER,'holding_status','capital']]
            b=CANDIDATE_PANELS[(wave,2)][[USER,'holding_status','capital']]
            t=a.merge(b,on=USER,validate='one_to_one',suffixes=('_lag1','_lag2'))
            table(wave+' JOB holding status transition lag2 to lag1',
                  t.groupby(['holding_status_lag2','holding_status_lag1']).size().reset_index(name='N'))
            distribution(wave+' JOB capital lag1 minus lag2 yuan; not passive gain',t.capital_lag1-t.capital_lag2)

# Wave order is explicit; None means unavailable, never carry another wave forward.
# Full question wording is retained in data/schema/jobsurvey_tables_schema.json.
# Q2 v53 is unresolved, not income. Hukou questions remain distinct.
# Completed family/employment option diagnostics are omitted in this supplement.
WAVES = ["2024q2", "2024q3", "2024q4", "2025q1"]
FIELD_MAP = {'exp_gdp': ['v94', 'v78', 'v119', 'v82'],
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
 'education': ['v99', 'v83', 'v124', 'v86']}

LABELS = {'exp_gdp': 'GDP预期',
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
 'education': '教育'}

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
 'education': ['education']}

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
REPORT.append(VERSION+'; supplement only; JOB windows pending new returns; no SME return input')
if not READY:
    REPORT.append('BLOCKED: confirm jobsurvey table names and common fields in Cell 1')
if READY:
    for wave, name in SURVEY_TABLES.items():
        cols=list(dict.fromkeys(BASIC+CONTROLS+TARGETS[wave]+[EDU[wave]]))
        PANELS[wave]=ant_read_data(name,cols=cols).copy()

# === CELL 3: Submission timing and minimal input audit ===
UNIQUE = {}
if READY:
    for wave, raw in PANELS.items():
        raw[USER]=text(raw[USER])
        raw[SUBMIT]=text(raw[SUBMIT])
        valid=raw[USER].notna() & raw[SUBMIT].notna()
        unique=valid & ~raw[USER].duplicated(False) & ~raw[SUBMIT].duplicated(False)
        d=raw.loc[unique].copy()
        d['submitted']=submit_dates(d[DATE])
        matches=text(d[EXTRA]).str.findall(r'(?:^|;)answerSeconds\s*=\s*([^;]*)(?=;|$)')
        seconds=numeric(matches.str[0])
        d['seconds']=seconds.where(matches.str.len().eq(1) & seconds.ge(0))
        submission_audit(wave,raw,valid,unique,d)
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
        UNIQUE[wave]=d

# === CELL 4: Candidate window holdings (new returns pending) ===
if READY and HOLDING_TABLE:
    h=ant_read_data(HOLDING_TABLE,cols=[HUSER,FUND,AMOUNT,HDATE]).copy()
    h[HUSER]=text(h[HUSER]); h[FUND]=fund(h[FUND]); h[AMOUNT]=numeric(h[AMOUNT])
    h['date']=dates(h[HDATE])
    h['month']=h.date.dt.strftime('%Y-%m')
    candidate_holdings(h)
elif READY:
    BLOCKERS.append('holding table not confirmed')
REPORT.append('COMPUTATION END status='+('BLOCKED' if BLOCKERS else 'COMPLETED')+'; issues='+','.join(BLOCKERS))

# === CELL 5: Preflight complete numeric report and emit block 1 ===
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
           'gain units: 10000 yuan; absent users in validated snapshots and recorded zero both zero',
           'JOB positive-holding gains PENDING new returns; no legacy gain calculation']
    if missing:
        lines+=['Continuation required: execute each report_page(i) in its OWN new notebook cell.',
                'Then run report_completion() in another cell.',
                'First missing index='+str(missing[0])+'; total blocks='+str(len(PAGES))]
    ant_print_all(pd.Series(lines),model_method='unique')


report_page(0)

# === CELL 6: Numeric report block 2 ===
report_page(1)

# === CELL 7: Numeric report block 3 ===
report_page(2)

# === CELL 8: Verify report completeness ===
report_completion()
