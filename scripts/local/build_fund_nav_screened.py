"""Temporary NAV price returns with daily, direction-symmetric event screens.

Money-fund rows are copied from the previous delivery without recalculation.
Ordinary rows retain independent legacy/date/currency checks, replacing the
invalid cumulative-NAV unit and distribution screens. No platform execution.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
from build_fund_total_return import DEFAULT_ROOT, static_map

VERSION = 'nav_price_screened_v1'
OUT = DEFAULT_ROOT / '20260823 exp stock/outputs'
DEST = OUT / 'fund_nav_screened'
KEY = ['fund_code', 'wave', 'history_month']
REMOVED = {'usable_under_stated_convention', 'inconsistent_nav_units',
           'decreasing_cumulative_distribution', 'large_distribution_or_share_event_unverified',
           'large_month_return_unverified', 'shock_exceeds_existing_20pct_bound', 'nonfinite_return'}

def read(p):
    return pd.read_csv(p, dtype={'fund_code': 'string'}, low_memory=False)

def precision(values):
    # At least four decimals when any observation requires it; otherwise three.
    # Use only baseline + current window, never subsequent periods.
    return np.where(np.abs(values * 1000 - np.round(values * 1000)) > 1e-5, .0001, .001)

def screen_window(daily, requests, calendar):
    """One requested interval per fund. Test fixed baseline models throughout.

    Additive residual = |A_t - N_t - (A_0 - N_0)|.
    Multiplicative residual = |A_t - (A_0/N_0)*N_t|.
    Both tolerances cover rounding at baseline and observation; 5% headroom.
    Passing a different model on every day is expressly not sufficient.
    """
    q = requests.set_index('FundClassID', verify_integrity=True)
    d = daily.merge(requests, on='FundClassID', how='inner', validate='many_to_one')
    d = d.loc[d.TradingDate.gt(d.bdate) & d.TradingDate.le(d.edate)].copy()
    if d.empty:
        return pd.DataFrame(index=q.index)
    valid = d.NAV.gt(0) & d.AccumulativeNAV.gt(0) & np.isfinite(d.NAV) & np.isfinite(d.AccumulativeNAV)
    d['bad_nav'] = ~valid
    # Invalid records are not allowed to silently disappear from coverage.
    d['eps_n'] = precision(d.NAV)
    d['eps_a'] = precision(d.AccumulativeNAV)
    gn = d.groupby('FundClassID').eps_n.transform('min')
    ga = d.groupby('FundClassID').eps_a.transform('min')
    en = np.minimum(gn, precision(d.n0))
    ea = np.minimum(ga, precision(d.a0))
    k = d.a0 / d.n0
    d['add_score'] = ((d.AccumulativeNAV-d.NAV)-(d.a0-d.n0)).abs() / (1.05*(ea+en))
    d['mult_score'] = (d.AccumulativeNAV-k*d.NAV).abs() / (1.05*(ea+k.abs()*en))
    d['eps_n_used'], d['eps_a_used'] = en, ea
    prev_n = d.groupby('FundClassID').NAV.shift().fillna(d.n0)
    prev_date = d.groupby('FundClassID').TradingDate.shift().fillna(d.bdate)
    # Reciprocal-symmetric guard: a factor above 1.25 or below 0.8.
    d['daily_log_jump'] = np.abs(np.log(d.NAV/prev_n))
    cal = calendar.to_numpy()
    d['internal_gap'] = (np.searchsorted(cal, d.TradingDate.to_numpy(), side='left')
                         - np.searchsorted(cal, prev_date.to_numpy(), side='right')) > 0
    d['valid_market_day'] = valid & d.TradingDate.isin(calendar)
    agg = d.groupby('FundClassID').agg(
        additive_score=('add_score','max'), multiplicative_score=('mult_score','max'),
        daily_max_log_jump=('daily_log_jump','max'), daily_invalid=('bad_nav','any'),
        daily_internal_gap=('internal_gap','any'), daily_market_observations=('valid_market_day','sum'),
        daily_observations=('NAV','size'), daily_last_date=('TradingDate','last'),
        daily_last_nav=('NAV','last'), daily_last_acc=('AccumulativeNAV','last'),
        nav_rounding_step=('eps_n_used','first'), acc_rounding_step=('eps_a_used','first'))
    agg = agg.join(q[['bdate','edate','n1','a1']])
    agg['daily_expected'] = (np.searchsorted(cal, agg.edate.to_numpy(), side='right')
                             - np.searchsorted(cal, agg.bdate.to_numpy(), side='right'))
    agg['daily_coverage'] = agg.daily_market_observations / agg.daily_expected.replace(0,np.nan)
    agg['endpoint_matches_daily'] = (agg.daily_last_date.eq(agg.edate)
        & (agg.daily_last_nav-agg.n1).abs().le(1e-8)
        & (agg.daily_last_acc-agg.a1).abs().le(1e-8))
    agg['event_screen_pass'] = agg.additive_score.le(1) | agg.multiplicative_score.le(1)
    agg['event_screen_model'] = np.select(
        [agg.additive_score.le(1)&agg.multiplicative_score.le(1), agg.additive_score.le(1), agg.multiplicative_score.le(1)],
        ['both','additive','multiplicative'], default='neither')
    return agg.drop(columns=['bdate','edate','n1','a1'])

def requests_for(frame, component):
    if component == 'control':
        names = {'baseline_date':'bdate','TradingDate':'edate','PrvNAV':'n0','NAV':'n1',
                 'PrvAccumulativeNAV':'a0','AccumulativeNAV':'a1'}
        keys = ['FundClassID','history_month']
    else:
        names = {'baseline_date':'bdate','end_date':'edate','baseline_nav':'n0','end_nav':'n1',
                 'baseline_accnav':'a0','end_accnav':'a1'}
        keys = ['FundClassID','wave']
    q = frame.loc[~frame.is_money, keys+list(names)].rename(columns=names).drop_duplicates()
    assert not q.duplicated(keys).any()
    for col in ['bdate','edate']:
        q[col] = pd.to_datetime(q[col])
    return q

def make_screens(c, s):
    cq, sq = requests_for(c,'control'), requests_for(s,'shock')
    results = {'control':[], 'shock':[]}
    ids = set(cq.FundClassID) | set(sq.FundClassID)
    for year in [2023,2024,2025]:
        chunks, dates = [], []
        for p in sorted(DEFAULT_ROOT.glob(f'基金日净值文件*_{year}/Fund_NAV*.dta')):
            x = pd.read_stata(p, columns=['FundClassID','TradingDate','NAV','AccumulativeNAV'], convert_categoricals=False)
            x.TradingDate = pd.to_datetime(x.TradingDate)
            dates.append(x.loc[x.AccumulativeNAV.notna()].groupby('TradingDate').size())
            chunks.append(x.loc[x.FundClassID.isin(ids)])
        d = pd.concat(chunks,ignore_index=True).sort_values(['FundClassID','TradingDate'])
        assert not d.duplicated(['FundClassID','TradingDate']).any()
        counts = pd.concat(dates).groupby(level=0).sum()
        calendar = pd.DatetimeIndex(counts.index[counts.ge(max(1000,counts.max()*.2))]).sort_values()
        for component, req, period in [('control',cq,'history_month'),('shock',sq,'wave')]:
            for label, q in req.loc[req.edate.dt.year.eq(year)].groupby(period):
                lo, hi = q.bdate.min(), q.edate.max()
                sample = d.loc[d.TradingDate.gt(lo) & d.TradingDate.le(hi)]
                a = screen_window(sample,q.drop(columns=period),calendar).reset_index()
                a[period] = label
                results[component].append(a)
        print('Screened daily data',year,len(d),flush=True)
        del d, chunks, x
    return {k:pd.concat(v,ignore_index=True) for k,v in results.items()}

def rebuild(f, screen, component):
    ctrl = component == 'control'
    keys = ['FundClassID','history_month' if ctrl else 'wave']
    f = f.merge(screen,on=keys,how='left',validate='many_to_one')
    flag = 'ctrl_usable' if ctrl else 'shock_usable'
    val = 'ctrl_monthly_ret' if ctrl else 'shock_ret_rate'
    cand = 'ctrl_monthly_ret_candidate' if ctrl else 'shock_ret_candidate'
    f['previous_usable'], f['previous_return'] = f[flag], f[val]
    f['previous_quality_reason'] = f.quality_reason
    ordinary = ~f.is_money
    n0,n1 = ('PrvNAV','NAV') if ctrl else ('baseline_nav','end_nav')
    f.loc[ordinary,cand] = f.loc[ordinary,n1]/f.loc[ordinary,n0]-1
    reasons = f.loc[ordinary,'quality_reason'].fillna('').map(
        lambda x: ';'.join(z for z in x.split(';') if z and z not in REMOVED))
    f.loc[ordinary,'quality_reason'] = reasons
    def reject(mask,reason):
        m = ordinary & mask.fillna(True)
        f.loc[m,'quality_reason'] += ';'+reason
    reject(~f.event_screen_pass.eq(True),'suspected_event_or_unclassified_nav_relation')
    reject(f.daily_observations.isna() | f.daily_expected.fillna(0).le(0),'missing_daily_screen')
    reject(~f.endpoint_matches_daily.eq(True),'daily_endpoint_mismatch')
    reject(f.daily_coverage.fillna(0).lt(.8),'daily_coverage_below_80pct')
    reject(f.daily_internal_gap.eq(True),'missing_internal_trading_day')
    reject(f.daily_invalid.eq(True),'invalid_daily_nav')
    reject(f.daily_max_log_jump.gt(np.log(1.25)),'large_daily_nav_jump')
    reject(~np.isfinite(f[cand]),'nonfinite_return')
    reject(f[cand].abs().gt(.5 if ctrl else .2),'large_month_return_unverified' if ctrl else 'shock_exceeds_existing_20pct_bound')
    f.loc[ordinary,'quality_reason'] = f.loc[ordinary,'quality_reason'].str.strip(';')
    f.loc[ordinary,flag] = f.loc[ordinary,'quality_reason'].eq('').astype(int)
    f.loc[ordinary,val] = f.loc[ordinary,cand].where(f.loc[ordinary,flag].eq(1))
    f.loc[ordinary,'return_method'] = 'unit_nav_price_return_screened'
    f.loc[ordinary & f[flag].eq(1),'quality_reason'] = 'screened_no_event_detected'
    f['return_version'] = VERSION
    if not ctrl:
        f['shock_ret_rate_pp'] = f[val]*100
    return f

def summaries(c,s):
    rows=[]
    for component,f,flag in [('control',c,'ctrl_usable'),('shock',s,'shock_usable')]:
        for wave,g in f.groupby('wave'):
            rows.append(dict(component=component,wave=wave,rows=len(g),v1_usable=int(g.previous_usable.sum()),
                usable=int(g[flag].sum()),lost=int((g.previous_usable.eq(1)&g[flag].eq(0)).sum()),
                recovered=int((g.previous_usable.eq(0)&g[flag].eq(1)).sum()),
                ordinary_usable=int((~g.is_money&g[flag].eq(1)).sum()),money_usable=int((g.is_money&g[flag].eq(1)).sum())))
    pd.DataFrame(rows).to_csv(DEST/'support/coverage_by_wave.csv',index=False)
    complete = c.groupby(['fund_code','wave']).agg(rows=('history_month','size'),
        usable_months=('ctrl_usable','sum'),v1_usable_months=('previous_usable','sum'),is_money=('is_money','first')).reset_index()
    complete['complete_12m'] = complete.rows.eq(12)&complete.usable_months.eq(12)
    complete['v1_complete_12m'] = complete.rows.eq(12)&complete.v1_usable_months.eq(12)
    complete.to_csv(DEST/'support/control_completeness.csv',index=False,encoding='utf-8-sig')
    bywave = complete.groupby('wave').agg(fund_windows=('fund_code','size'),complete_12m=('complete_12m','sum'),
        v1_complete_12m=('v1_complete_12m','sum'))
    bywave.to_csv(DEST/'support/control_completeness_by_wave.csv')
    joint=complete.merge(s[['fund_code','wave','shock_usable','previous_usable']],
        on=['fund_code','wave'],how='left',validate='one_to_one')
    joint['joint']=joint.complete_12m & joint.shock_usable.eq(1)
    joint['v1_joint']=joint.v1_complete_12m & joint.previous_usable.eq(1)
    joint.groupby('wave').agg(joint_fund_windows=('joint','sum'),
        v1_joint_fund_windows=('v1_joint','sum')).to_csv(DEST/'support/joint_coverage_by_wave.csv')
    reason=[]
    for component,f in [('control',c),('shock',s)]:
        for name,count in f.quality_reason.str.split(';').explode().value_counts().items():
            reason.append(dict(component=component,reason=name,rows=int(count)))
    pd.DataFrame(reason).to_csv(DEST/'support/quality_reason_counts.csv',index=False)
    incremental=[]
    for component,f,flag in [('control',c,'ctrl_usable'),('shock',s,'shock_usable')]:
        lost=f.loc[f.previous_usable.eq(1)&f[flag].eq(0)]
        for name,count in lost.quality_reason.str.split(';').explode().value_counts().items():
            incremental.append(dict(component=component,reason=name,rows=int(count)))
    pd.DataFrame(incremental).to_csv(DEST/'support/new_loss_reason_counts.csv',index=False)
    c.loc[c.fund_code.isin(['000001','110022','159915','159925','110007','110008'])].drop_duplicates(
        ['fund_code','history_month']).to_csv(DEST/'support/representative_funds.csv',index=False,encoding='utf-8-sig')
    print(pd.DataFrame(rows).to_string(index=False),flush=True)
    print(bywave.to_string(),flush=True)

def main():
    (DEST/'support').mkdir(parents=True,exist_ok=True)
    meta = static_map(OUT,DEFAULT_ROOT)[['fund_code','FundClassID','is_money']]
    paths=[OUT/'fund_total_return/ctrl_monthly_total_return_v1.csv',OUT/'fund_total_return/shock_panel_total_return_v1.csv']
    c,s = [read(p).merge(meta,on='fund_code',how='left',validate='many_to_one') for p in paths]
    assert c.is_money.notna().all() and s.is_money.notna().all()
    screens = make_screens(c,s)
    for kind,df in screens.items():
        df.to_csv(DEST/f'support/{kind}_daily_screen.csv',index=False,encoding='utf-8-sig')
    c,s = rebuild(c,screens['control'],'control'),rebuild(s,screens['shock'],'shock')
    for f,keys,val,flag,name in [(c,KEY,'ctrl_monthly_ret','ctrl_usable','ctrl_monthly_nav_screened_v1.csv'),
            (s,KEY[:2],'shock_ret_rate','shock_usable','shock_panel_nav_screened_v1.csv')]:
        assert not f.duplicated(keys).any()
        assert f[val].notna().eq(f[flag].eq(1)).all()
        assert np.isfinite(f.loc[f[flag].eq(1),val]).all()
        assert f.loc[f.is_money,flag].eq(f.loc[f.is_money,'previous_usable']).all()
        assert np.allclose(f.loc[f.is_money,val],f.loc[f.is_money,'previous_return'],equal_nan=True,atol=0,rtol=0)
        f.to_csv(DEST/name,index=False,encoding='utf-8-sig',float_format='%.12g')
    assert c.groupby(['fund_code','history_month']).ctrl_monthly_ret.nunique().le(1).all()
    summaries(c,s)
    manifest=dict(return_version=VERSION,control_rows=len(c),control_usable=int(c.ctrl_usable.sum()),
        shock_rows=len(s),shock_usable=int(s.shock_usable.sum()),platform_run=False,
        ordinary_method='NAV_end/NAV_base-1; daily additive OR multiplicative whole-window screen',
        tolerance='1.05 times the rounding bound, three/four decimals inferred within each window',
        limits=dict(min_daily_coverage=.8,max_daily_log_jump=float(np.log(1.25)),shock_abs_return=.2,month_abs_return=.5),
        money_policy='All is_money rows preserved exactly from v1, including legacy NAV-based money funds',
        input_sha256={str(p.relative_to(DEFAULT_ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DEST.glob('*.csv')})
    (DEST/'support/build_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    inventory=[dict(path=str(p.relative_to(DEFAULT_ROOT)),bytes=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns)
        for year in [2023,2024,2025] for p in sorted(DEFAULT_ROOT.glob(f'基金日净值文件*_{year}/Fund_NAV*.dta'))]
    (DEST/'support/source_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k.endswith('usable') or k.endswith('rows')},indent=2),flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if '--summaries-only' in sys.argv:
        summaries(read(DEST/'ctrl_monthly_nav_screened_v1.csv'),read(DEST/'shock_panel_nav_screened_v1.csv'))
    else:
        main()
