"""All-row review tables: raw returns, screened returns, and separate flags.

No inference that a suspected event is confirmed. Calculable ordinary price
returns populate primary columns; quality flags do not mask these values.
"""
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from build_fund_nav_screened import DEST, OUT, KEY, read

TARGET=OUT/'fund_nav_annotated'
UPLOAD=OUT/'fund_nav_upload'
UPLOAD_COMMON=['fund_code','wave','return_version','screen_pass_all_checks',
               'flag_nav_relation_break','flag_large_daily_jump',
               'flag_daily_evidence_insufficient','flag_window_return_large',
               'flag_date_or_inception','flag_currency','flag_legacy_issue']
UPLOAD_COLUMNS={
    'control':['fund_code','wave','history_month','ctrl_monthly_ret']
              +UPLOAD_COMMON[2:],
    'shock':['fund_code','wave','shock_ret_rate_pp','shock_usable',
             'window_start','window_end']+UPLOAD_COMMON[2:],
}

def annotate(f,component):
    control=component=='control'
    value='ctrl_monthly_ret' if control else 'shock_ret_rate'
    usable='ctrl_usable' if control else 'shock_usable'
    candidate='ctrl_monthly_ret_candidate' if control else 'shock_ret_candidate'
    n0,n1=('PrvNAV','NAV') if control else ('baseline_nav','end_nav')
    keys=KEY if control else KEY[:2]
    a=f[keys].copy()
    a['is_money']=f.is_money
    a['screened_return']=f[value]
    a['screen_pass_all_checks']=f[usable]
    # Ordinary raw price returns require positive finite endpoints only.
    valid=f[n0].gt(0)&f[n1].gt(0)&np.isfinite(f[n0])&np.isfinite(f[n1])
    a['raw_return']=(f[n1]/f[n0]-1).where(valid)
    # Money policy is unchanged; unresolved money candidates remain audit-only.
    a.loc[f.is_money,'raw_return']=f.loc[f.is_money,value]
    a['return_calculable']=a.raw_return.notna().astype(int)
    observed=(~f.is_money)&np.isfinite(f.additive_score)&np.isfinite(f.multiplicative_score)
    a['flag_nav_relation_break']=pd.Series(pd.NA,index=f.index,dtype='Int64')
    a.loc[observed,'flag_nav_relation_break']=(f.loc[observed,'additive_score'].gt(1)&f.loc[observed,'multiplicative_score'].gt(1)).astype(int)
    a['flag_large_daily_jump']=pd.Series(pd.NA,index=f.index,dtype='Int64')
    measured=(~f.is_money)&f.daily_max_log_jump.notna()
    a.loc[measured,'flag_large_daily_jump']=f.loc[measured,'daily_max_log_jump'].gt(np.log(1.25)).astype(int)
    reasons=f.quality_reason.fillna('')
    for name,pattern in {
        'flag_daily_evidence_insufficient':'missing_daily_screen|daily_coverage_below_80pct|missing_internal_trading_day|daily_endpoint_mismatch|invalid_daily_nav',
        'flag_window_return_large':'large_month_return_unverified|shock_exceeds_existing_20pct_bound',
        'flag_date_or_inception':'stale|missing_nav_date|no_pre_|previous_month_reference_mismatch',
        'flag_currency':'non_cny_without_fx_conversion',
        'flag_legacy_issue':'legacy:',
    }.items():
        a[name]=reasons.str.contains(pattern,regex=True).astype(int)
    a['quality_reasons']=reasons
    a['review_status']=np.select([a.return_calculable.eq(0),f.is_money,f[usable].eq(1)],
        ['return_unavailable','money_policy_preserved','no_flag_under_current_screen'],default='return_retained_with_flags')
    for col in [n0,n1,'baseline_date','TradingDate' if control else 'end_date','additive_score','multiplicative_score',
                'daily_coverage','daily_expected','daily_market_observations','daily_internal_gap','endpoint_matches_daily']:
        a[col]=f[col]
    a['source_version']=f.return_version
    a['annotation_version']='nav_annotation_v1'
    a['return_version']='nav_price_annotated_v1'
    a[value]=a.raw_return
    a[usable]=a.return_calculable
    a['currency']=f.currency
    a['return_method']=np.where(f.is_money,f.return_method,'unit_nav_price_return_flags_only')
    original='ctrl_monthly_ret_original' if control else 'shock_ret_original'
    a[original]=f[original]
    if not control:
        a['shock_ret_rate_pp']=a.raw_return*100
        for col in ['window_start','window_end','window_days']:
            a[col]=f[col]
    else:
        for col in ['history_start','history_end']:
            a[col]=f[col]
    assert len(a)==len(f) and not a.duplicated(keys).any()
    assert np.isfinite(a.loc[a.return_calculable.eq(1),'raw_return']).all()
    assert np.allclose(a.screened_return,f[value],equal_nan=True,atol=0,rtol=0)
    return a

def main():
    TARGET.mkdir(exist_ok=True)
    UPLOAD.mkdir(exist_ok=True)
    summary={}
    for component,filename in [('control','ctrl_monthly_nav_screened_v1.csv'),('shock','shock_panel_nav_screened_v1.csv')]:
        f=read(DEST/filename);a=annotate(f,component)
        name='ctrl_monthly_nav_annotated_v1.csv' if component=='control' else 'shock_panel_nav_annotated_v1.csv'
        a.to_csv(TARGET/name,index=False,encoding='utf-8-sig',float_format='%.12g')
        # Platform upload keeps every row and the quality flags; review fields
        # remain in the full annotated delivery above.
        a[UPLOAD_COLUMNS[component]].to_csv(
            UPLOAD/name,index=False,encoding='utf-8-sig',float_format='%.12g')
        summary[component]=dict(rows=len(a),calculable=int(a.return_calculable.sum()),
            statuses={str(k):int(v) for k,v in a.review_status.value_counts().items()})
    (TARGET/'annotation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
