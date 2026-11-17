"""Rebuild Jobsurvey windows with the existing SME NAV-annotation algorithms.

Local-only. Reproduce all five SME windows before delivering new returns.
No SME data outputs are changed. Funds retain their original same-wave universe.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

import numpy as np
import pandas as pd

import build_fund_total_return as total
import build_fund_nav_screened as screened
import annotate_fund_nav_returns as annotated

FIRST = {'2024q2': '2024-06-27', '2024q3': '2024-09-26',
         '2024q4': '2024-12-20', '2025q1': '2025-03-22'}
SME_WAVES = dict(total.WAVES)
VERSION = 'jobsurvey_nav_price_annotated_v1'


def digest(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def windows():
    rows = []
    for wave, first in FIRST.items():
        anchor = pd.Timestamp(first)
        for lag in (1, 2):
            base = (anchor.to_period('M') - lag).end_time.normalize()
            rows.append(dict(window_id=wave+'_lag'+str(lag), wave=wave,
                             lag_months=lag, holding_date=base,
                             window_start=base+pd.Timedelta(days=1),
                             window_end=anchor-pd.Timedelta(days=1), first_submit_date=anchor))
    return pd.DataFrame(rows)


def load_sources(root, money_ids, intervals):
    """Same source columns and calendars as SME, retaining the new intervals too."""
    nav_parts, money_parts, counts = [], [], []
    cols = ['FundClassID', 'TradingDate', 'NAV', 'AccumulativeNAV'] + total.INCOME_FIELDS + ['AnnualizedYield']
    sources = sorted(root.glob('基金日净值文件*_202[345]/Fund_NAV*.dta'))
    if not sources:
        raise FileNotFoundError('No daily CSMAR files')
    for path in sources:
        for chunk in pd.read_stata(path, columns=cols, chunksize=250_000, convert_categoricals=False):
            chunk.TradingDate = pd.to_datetime(chunk.TradingDate)
            counts.append(chunk.loc[chunk.AccumulativeNAV.notna()].groupby('TradingDate').size())
            money_parts.append(chunk.loc[chunk.FundClassID.isin(money_ids)])
            keep = pd.Series(False, index=chunk.index)
            for start, end in intervals.values():
                keep |= chunk.TradingDate.between(pd.Timestamp(start)-pd.Timedelta(days=16), end)
            nav_parts.append(chunk.loc[keep, cols[:4]])
        print('Read', path.parent.name, path.name, flush=True)
    counts = pd.concat(counts).groupby(level=0).sum()
    calendar = pd.DatetimeIndex(counts.index[counts.ge(max(1000, counts.max()*.2))]).sort_values()
    year_calendars = {}
    for year in (2023, 2024, 2025):
        c = counts.loc[counts.index.year == year]
        year_calendars[year] = pd.DatetimeIndex(c.index[c.ge(max(1000, c.max()*.2))]).sort_values()
    nav = pd.concat(nav_parts, ignore_index=True).sort_values(['FundClassID', 'TradingDate'])
    money = pd.concat(money_parts, ignore_index=True).sort_values(['FundClassID', 'TradingDate'])
    for frame in (nav, money):
        assert not frame.duplicated(['FundClassID', 'TradingDate']).any()
    return nav, money, calendar, year_calendars, sources


def build(original, nav, daily_money, calendar, year_calendars, meta, anomaly, intervals):
    # Existing functions read their module-level WAVES; scoped to this local process.
    total.WAVES = intervals
    money = total.money_windows(daily_money, calendar)
    cash = total.shock_build(original, nav, money, calendar, meta, anomaly)
    req = screened.requests_for(cash, 'shock')
    parts = []
    for label, q in req.groupby('wave', sort=False):
        years = q.edate.dropna().dt.year.unique()
        assert len(years) == 1
        year = int(years[0])
        d = nav.loc[nav.TradingDate.between(q.bdate.min(), q.edate.max())]
        a = screened.screen_window(d, q.drop(columns='wave'), year_calendars[year]).reset_index()
        a['wave'] = label
        parts.append(a)
    strict = screened.rebuild(cash, pd.concat(parts, ignore_index=True), 'shock')
    result = annotated.annotate(strict, 'shock')
    return result, strict


def reproduce_sme(result, reference):
    key = ['fund_code', 'wave']
    assert not result.duplicated(key).any() and not reference.duplicated(key).any()
    a = result.sort_values(key).reset_index(drop=True)
    b = reference.sort_values(key).reset_index(drop=True)
    assert a[key].equals(b[key])
    checks = []
    for c in ['shock_ret_rate', 'shock_ret_rate_pp', 'shock_usable', 'screened_return',
              'screen_pass_all_checks', 'baseline_nav', 'end_nav', 'daily_coverage'] + [c for c in b if c.startswith('flag_')]:
        x = pd.to_numeric(a[c], errors='coerce').to_numpy(dtype=float, na_value=np.nan)
        y = pd.to_numeric(b[c], errors='coerce').to_numpy(dtype=float, na_value=np.nan)
        equal = np.isclose(x, y, rtol=2e-10, atol=1e-10, equal_nan=True)
        checks.append(dict(field=c,rows=len(a),mismatch=int((~equal).sum())))
    for c in ['baseline_date', 'end_date', 'window_start', 'window_end']:
        x, y = pd.to_datetime(a[c]), pd.to_datetime(b[c])
        checks.append(dict(field=c,rows=len(a),mismatch=int((~(x.eq(y)|(x.isna()&y.isna()))).sum())))
    checks = pd.DataFrame(checks)
    if checks.mismatch.sum():
        raise ValueError('SME reproduction failed: '+checks.loc[checks.mismatch.gt(0)].to_json(orient='records'))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=total.DEFAULT_ROOT)
    args = parser.parse_args()
    outputs = args.root/'20260823 exp stock/outputs'
    dest = outputs/'jobsurvey_fund_returns'
    dest.mkdir(exist_ok=True)
    for sub in ['upload', 'support']:
        (dest/sub).mkdir(exist_ok=True)
    config = windows()
    intervals = {r.window_id: (str(r.window_start.date()), str(r.window_end.date())) for r in config.itertuples()}
    meta = total.static_map(outputs, args.root)
    original = total.read_csv(outputs/'shock_panel.csv')
    anomaly = total.read_csv(outputs/'fund_quality_delivery/other_ctrl_shock_anomalies.csv')
    nav, daily_money, calendar, year_calendars, sources = load_sources(
        args.root, set(meta.loc[meta.is_money, 'FundClassID']), {**SME_WAVES, **intervals})
    old, _ = build(original, nav, daily_money, calendar, year_calendars, meta, anomaly, SME_WAVES)
    checks = reproduce_sme(old, total.read_csv(outputs/'fund_nav_annotated/shock_panel_nav_annotated_v1.csv'))
    checks.to_csv(dest/'support/sme_reproduction_checks.csv', index=False)
    print('SME reproduction passed:', len(old), 'rows,',len(checks),'fields', flush=True)
    # Keep exactly the existing fund-code universe for each corresponding wave.
    # Old window-specific anomalies are not blindly transferred to different dates.
    # Fresh baseline/date, inception, currency and evidence checks run above.
    frames = []
    for r in config.itertuples():
        old_wave = r.wave[2:4] + r.wave[4:].upper()
        x = original.loc[original.wave.eq(old_wave), ['fund_code']].copy()
        x['wave'] = r.window_id
        x['window_start'], x['window_end'] = r.window_start, r.window_end
        x['window_days'] = (r.window_end-r.window_start).days+1
        x['shock_n_theory_days'] = int(((calendar>=r.window_start)&(calendar<=r.window_end)).sum())
        x['shock_ret_rate'] = np.nan  # no old SME value carried to this window
        x['shock_usable'] = 0
        frames.append(x)
    fresh, strict = build(pd.concat(frames, ignore_index=True), nav, daily_money, calendar,
                          year_calendars, meta, anomaly.iloc[:0].copy(), intervals)
    fresh = fresh.rename(columns={'wave':'window_id'}).merge(config.drop(columns=['window_start','window_end']),
            on='window_id', how='left', validate='many_to_one')
    fresh['return_version'] = VERSION
    fresh['algorithm_version'] = 'nav_price_annotated_v1'
    fresh['legacy_issue_policy'] = 'new_window_checks_no_sme_date_flags_carried'
    assert not fresh.duplicated(['fund_code','wave','lag_months']).any()
    assert pd.to_datetime(fresh.baseline_date).lt(pd.to_datetime(fresh.window_start)).fillna(False)[fresh.baseline_date.notna()].all()
    assert pd.to_datetime(fresh.end_date).le(pd.to_datetime(fresh.window_end)).fillna(False)[fresh.end_date.notna()].all()
    assert fresh.shock_usable.eq(1).equals(fresh.shock_ret_rate.notna())
    assert np.allclose(fresh.shock_ret_rate_pp,fresh.shock_ret_rate*100,equal_nan=True)
    fresh.to_csv(dest/'jobsurvey_fund_returns_full_v1.csv',index=False,encoding='utf-8-sig',float_format='%.12g')
    strict.to_csv(dest/'support/jobsurvey_screening_evidence_v1.csv',index=False,encoding='utf-8-sig',float_format='%.12g')
    config.to_csv(dest/'support/window_config.csv',index=False)
    rows=[]
    for (wave,lag),g in fresh.groupby(['wave','lag_months']):
        value=g.shock_ret_rate_pp.dropna()
        row=dict(wave=wave,lag_months=int(lag),rows=len(g),calculable=int(g.shock_usable.sum()),
                 ordinary=int((~g.is_money).sum()),money=int(g.is_money.sum()),
                 ordinary_calculable=int((~g.is_money & g.shock_usable.eq(1)).sum()),
                 money_calculable=int((g.is_money & g.shock_usable.eq(1)).sum()),
                 retained_with_flags=int((g.shock_usable.eq(1)&g.screen_pass_all_checks.eq(0)).sum()),
                 mean_pp=value.mean(),min_pp=value.min(),p01_pp=value.quantile(.01),
                 median_pp=value.median(),p99_pp=value.quantile(.99),max_pp=value.max())
        rows.append(row)
    summary=pd.DataFrame(rows)
    summary.to_csv(dest/'support/summary_by_window.csv',index=False,encoding='utf-8-sig')
    flags=fresh.groupby(['wave','lag_months'])[[c for c in fresh if c.startswith('flag_')]].sum(min_count=1)
    flags.to_csv(dest/'support/flag_counts.csv',encoding='utf-8-sig')
    extreme_cols=['fund_code','wave','lag_months','shock_ret_rate_pp','baseline_nav','end_nav',
                  'baseline_date','end_date','screen_pass_all_checks','flag_nav_relation_break',
                  'flag_large_daily_jump','flag_window_return_large','quality_reasons']
    fresh.loc[fresh.shock_ret_rate_pp.abs().gt(20),extreme_cols].to_csv(
        dest/'support/returns_over_20pp.csv',index=False,encoding='utf-8-sig',float_format='%.12g')
    upload_cols=annotated.UPLOAD_COLUMNS['shock']+['lag_months','holding_date','first_submit_date','algorithm_version']
    for lag in [1,2]:
        frame=fresh.loc[fresh.lag_months.eq(lag),upload_cols]
        assert not frame.duplicated(['fund_code','wave']).any()
        frame.to_csv(dest/'upload'/f'jobsurvey_shock_lag{lag}_nav_annotated_v1.csv',index=False,encoding='utf-8-sig',float_format='%.12g')
    # Freeze a standalone copy of the exact implementation used in the external project.
    snapshot=outputs.parent/'scripts/jobsurvey'
    snapshot.mkdir(parents=True,exist_ok=True)
    code_sources=[Path(__file__).resolve(),Path(total.__file__).resolve(),Path(screened.__file__).resolve(),Path(annotated.__file__).resolve()]
    for p in code_sources:
        target=snapshot/p.name
        if p != target.resolve():
            shutil.copy2(p,target)
    input_paths=sources+[outputs/'fund_static.csv',outputs/'shock_panel.csv',
        outputs/'fund_quality_delivery/other_ctrl_shock_anomalies.csv',
        outputs/'fund_nav_annotated/shock_panel_nav_annotated_v1.csv',
        args.root/'基金份额类别信息表170624779/FUND_UnitClassInfo.dta']
    manifest=dict(return_version=VERSION,algorithm_version='nav_price_annotated_v1',platform_run=False,
                  date_source='Jobsurvey 11162137 verified submission dates',
                  sme_reproduction_rows=len(old),sme_reproduction_mismatches=int(checks.mismatch.sum()),
                  universe='same-wave SME fund-code universe; missing returns retained; no holding-weighted coverage inferred',
                  source_hashes={str(p):digest(p) for p in input_paths},
                  code_hashes={p.name:digest(p) for p in code_sources},
                  output_hashes={str(p.relative_to(dest)):digest(p) for p in dest.rglob('*.csv')})
    (dest/'support/build_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(summary.to_string(index=False),flush=True)
    print('Delivery:',dest,flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
