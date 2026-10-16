"""Local CSMAR reconstruction; never execute this file on the Ant platform.

Ordinary funds: fixed-share cash total return, (AccNAV_end-AccNAV_base)/NAV_base.
This is conditional on stable share units, not an independently verified adjusted
NAV series. Money income retains the accepted monthly delivery convention.
Original inputs are read-only. All large outputs stay in the CSMAR output root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

VERSION = "cash_total_return_v1"
DEFAULT_ROOT = Path("D:/wyp_Files/xx.Files/data/CSMAR_fund_202608")
WAVES = {
    "24Q2": ("2024-06-01", "2024-06-13"),
    "24Q3": ("2024-09-01", "2024-09-17"),
    "24Q4": ("2024-12-01", "2024-12-10"),
    "25Q1": ("2025-03-01", "2025-03-17"),
    "25Q2": ("2025-06-01", "2025-06-12"),
}
INCOME_FIELDS = ["AchieveReturn", "MillionAchieveReturn", "HundredAchieveReturn"]
KEY = ["fund_code", "wave", "history_month"]


def read_csv(path):
    return pd.read_csv(path, dtype={"fund_code": "string"})


def cash_return(nav0, acc0, acc1):
    return (acc1 - acc0) / nav0


def add_reason(frame, mask, reason):
    mask = pd.Series(mask, index=frame.index).fillna(True)
    frame.loc[mask, "quality_reason"] += reason + ";"


def static_map(outputs, root):
    raw = read_csv(outputs / "fund_static.csv")
    if raw.groupby("fund_code").FundClassID.nunique().gt(1).any():
        raise ValueError("Ambiguous code/class mapping")
    if raw.groupby("fund_code").CurrencyCode.nunique().gt(1).any():
        raise ValueError("Ambiguous currency")
    raw["is_money"] = raw.Category.eq("货币型基金")
    raw["InceptionDate_Class"] = pd.to_datetime(raw.InceptionDate_Class)
    meta = raw.groupby("fund_code", as_index=False).agg(
        FundClassID=("FundClassID", "first"), is_money=("is_money", "any"),
        currency=("CurrencyCode", "first"), inception=("InceptionDate_Class", "min"),
        inception_latest=("InceptionDate_Class", "max"),
    )
    meta.FundClassID = meta.FundClassID.astype("int64")
    units = pd.read_stata(root / "基金份额类别信息表170624779/FUND_UnitClassInfo.dta",
                         columns=["FundClassID", "ParValue"], convert_categoricals=False)
    if units.groupby("FundClassID").ParValue.nunique().gt(1).any():
        raise ValueError("Ambiguous par value")
    return meta.merge(units.drop_duplicates("FundClassID"), on="FundClassID",
                      how="left", validate="many_to_one")


def monthly_source(root):
    cols = ["FundClassID", "TradingMonth", "TradingDate", "StartDate", "NAV", "PrvNAV",
            "AccumulativeNAV", "PrvAccumulativeNAV", "ReturnAccumulativeNAV", "TradingDays"]
    paths = sorted(root.glob("基金月净值文件*/Fund_NAV_Month*.dta"))
    if not paths:
        raise FileNotFoundError("Monthly files missing")
    m = pd.concat([pd.read_stata(p, columns=cols, convert_categoricals=False)
                   for p in paths], ignore_index=True)
    for col in ["TradingMonth", "TradingDate", "StartDate"]:
        m[col] = pd.to_datetime(m[col])
    if m.duplicated(["FundClassID", "TradingMonth"]).any():
        raise ValueError("Duplicate monthly source keys")
    m["history_month"] = m.TradingMonth.dt.strftime("%Y-%m")
    prev = m[["FundClassID", "TradingMonth", "TradingDate", "NAV", "AccumulativeNAV"]].copy()
    prev.TradingMonth += pd.DateOffset(months=1)
    prev = prev.rename(columns={"TradingDate": "baseline_date", "NAV": "prev_source_nav",
                                "AccumulativeNAV": "prev_source_acc"})
    return m.merge(prev, on=["FundClassID", "TradingMonth"], how="left", validate="one_to_one")


def load_daily(root, money_ids):
    """Retain short NAV windows and money-income history; infer original calendar."""
    money_parts, nav_parts, counts = [], [], []
    cols = ["FundClassID", "TradingDate", "NAV", "AccumulativeNAV"] + INCOME_FIELDS + ["AnnualizedYield"]
    paths = sorted(root.glob("基金日净值文件*_202[345]/Fund_NAV*.dta"))
    if not paths:
        raise FileNotFoundError("Daily files missing")
    for path in paths:
        for chunk in pd.read_stata(path, columns=cols, chunksize=250_000, convert_categoricals=False):
            chunk.TradingDate = pd.to_datetime(chunk.TradingDate)
            counts.append(chunk.loc[chunk.AccumulativeNAV.notna()].groupby("TradingDate").size())
            money = chunk.loc[chunk.FundClassID.isin(money_ids)]
            if len(money):
                money_parts.append(money)
            keep = pd.Series(False, index=chunk.index)
            for start, end in WAVES.values():
                keep |= chunk.TradingDate.between(pd.Timestamp(start) - pd.Timedelta(days=16), end)
            nav_parts.append(chunk.loc[keep, ["FundClassID", "TradingDate", "NAV", "AccumulativeNAV"]])
        print("Read", path.parent.name, path.name, flush=True)
    count = pd.concat(counts).groupby(level=0).sum()
    threshold = max(1000, count.max() * .2)
    calendar = pd.DatetimeIndex(count.index[count.ge(threshold)])
    nav = pd.concat(nav_parts, ignore_index=True)
    money = pd.concat(money_parts, ignore_index=True)
    for label, frame in [("NAV", nav), ("money", money)]:
        if frame.duplicated(["FundClassID", "TradingDate"]).any():
            raise ValueError("Duplicate daily keys: " + label)
    return (nav.sort_values(["FundClassID", "TradingDate"]),
            money.sort_values(["FundClassID", "TradingDate"]), calendar)


def control_build(original, monthly, meta, supplement, anomaly):
    c = original.rename(columns={"ctrl_monthly_ret": "ctrl_monthly_ret_original"})
    c = c.merge(meta, on="fund_code", how="left", validate="many_to_one").merge(
        monthly.drop(columns="TradingDays"), on=["FundClassID", "history_month"],
        how="left", validate="many_to_one")
    c["quality_reason"] = ""
    c["return_method"] = "cash_nav_difference_over_initial_nav"
    c["ctrl_monthly_ret_candidate"] = cash_return(c.PrvNAV, c.PrvAccumulativeNAV, c.AccumulativeNAV)
    c["old_formula_exact"] = c.AccumulativeNAV / c.PrvAccumulativeNAV - 1
    # Retain all pre-existing unresolved exclusions. Resolved money rows are
    # already absent from this exclusion set.
    exc = anomaly.loc[anomaly.component.eq("control") & anomaly.exclude.eq(1), KEY + ["reason"]]
    c = c.merge(exc.rename(columns={"reason": "legacy_reason"}), on=KEY, how="left", validate="one_to_one")
    c.loc[c.legacy_reason.notna(), "quality_reason"] = "legacy:" + c.legacy_reason.dropna() + ";"
    nav_rows = ~c.is_money.fillna(False) | c.PrvNAV.gt(0)
    add_reason(c, nav_rows & ~(c.NAV.gt(0) & c.PrvNAV.gt(0)
                              & c.AccumulativeNAV.gt(0) & c.PrvAccumulativeNAV.gt(0)), "invalid_unit_or_acc_nav")
    add_reason(c, nav_rows & ((c.AccumulativeNAV + .001 < c.NAV)
                             | (c.PrvAccumulativeNAV + .001 < c.PrvNAV)), "inconsistent_nav_units")
    offset_change = c.AccumulativeNAV - c.NAV - c.PrvAccumulativeNAV + c.PrvNAV
    add_reason(c, nav_rows & offset_change.lt(-.001), "decreasing_cumulative_distribution")
    add_reason(c, nav_rows & offset_change.gt(.2 * c.PrvNAV), "large_distribution_or_share_event_unverified")
    add_reason(c, nav_rows & c.ctrl_monthly_ret_candidate.abs().gt(.5), "large_month_return_unverified")
    month_start = pd.to_datetime(c.history_month)
    month_end = month_start + pd.offsets.MonthEnd(0)
    add_reason(c, nav_rows & (c.inception.isna() | c.inception.ge(month_start)), "no_pre_month_inception")
    add_reason(c, nav_rows & (c.baseline_date.isna() | c.TradingDate.isna()), "missing_nav_date")
    add_reason(c, nav_rows & (((month_start - pd.Timedelta(days=1) - c.baseline_date).dt.days > 7)
                             | ((month_end - c.TradingDate).dt.days > 7)), "stale_month_endpoint_over_7d")
    add_reason(c, nav_rows & (c.prev_source_nav.sub(c.PrvNAV).abs().gt(.001)
                             | c.prev_source_acc.sub(c.PrvAccumulativeNAV).abs().gt(.001)), "previous_month_reference_mismatch")
    c = c.merge(supplement[KEY + ["ctrl_monthly_ret_supplement", "supplement_usable", "quality_status",
                                  "return_timing_rule"]], on=KEY, how="left", validate="one_to_one")
    has_supp = c.supplement_usable.notna()
    if not c.loc[has_supp, "is_money"].all():
        raise ValueError("Supplement contains a non-money code")
    c.loc[has_supp, "ctrl_monthly_ret_candidate"] = c.loc[has_supp, "ctrl_monthly_ret_supplement"]
    c.loc[has_supp, "return_method"] = "money_income_legacy_verified_convention"
    add_reason(c, c.is_money & ~nav_rows & ~has_supp, "money_income_not_reconstructed")
    add_reason(c, has_supp & ~c.supplement_usable.eq(True), "unresolved_money_income")
    add_reason(c, c.currency.ne("CNY"), "non_cny_without_fx_conversion")
    add_reason(c, ~np.isfinite(c.ctrl_monthly_ret_candidate), "nonfinite_return")
    c["ctrl_usable"] = c.quality_reason.eq("").astype(int)
    c["ctrl_monthly_ret"] = c.ctrl_monthly_ret_candidate.where(c.ctrl_usable.eq(1))
    c["quality_reason"] = c.quality_reason.str.rstrip(";").replace("", "usable_under_stated_convention")
    c["return_version"] = VERSION
    return c


def money_windows(daily, calendar):
    """Posted-date compound income, with coverage evidence kept separately.

    No post-window amount enters a shock. A trailing missing calendar day is
    accepted only with a later <=14-day bundled disclosure covering that day;
    this future record supports completeness, not income imputation.
    """
    d = daily.copy()
    d["field_count"] = d[INCOME_FIELDS].notna().sum(axis=1)
    d["income"] = d[INCOME_FIELDS].bfill(axis=1).iloc[:, 0]
    d["field"] = np.select([d[f].notna() for f in INCOME_FIELDS], INCOME_FIELDS, default="none")
    d = d.loc[d.income.notna()].copy()
    prev = d.groupby("FundClassID").TradingDate.shift()
    d["previous_date"] = prev
    d["gap"] = (d.TradingDate - prev).dt.days.fillna(1).astype(int)
    d["span"] = d.gap.where(d.gap.le(14), 1)
    trading_dates = calendar.sort_values().to_numpy()
    d["unexplained_gap"] = (
        np.searchsorted(trading_dates, d.TradingDate.to_numpy(), side="left")
        - np.searchsorted(trading_dates, prev.fillna(d.TradingDate).to_numpy(), side="right")
    ) > 0
    d["log_return"] = np.log1p(d.income / 10000)
    out = []
    for wave, (start, end) in WAVES.items():
        start, end = pd.Timestamp(start), pd.Timestamp(end)
        w = d.loc[d.TradingDate.between(start, end)]
        agg = w.groupby("FundClassID").agg(
            money_log=("log_return", "sum"), money_observations=("income", "size"),
            money_income_sum=("income", "sum"), money_yield_max=("AnnualizedYield", "max"),
            money_long_gap=("gap", lambda x: x.gt(14).any()),
            money_field_conflict=("field_count", lambda x: x.ne(1).any()),
            money_unexplained_gap=("unexplained_gap", "any"),
            money_fields=("field", lambda x: "|".join(sorted(set(x)))),
            money_first_date=("TradingDate", "min"), money_last_date=("TradingDate", "max"),
        ).reset_index()
        # Count calendar days evidenced by <=14-day income disclosure spans.
        evidence = d.loc[d.TradingDate.between(start, end + pd.Timedelta(days=14))].copy()
        left = (evidence.TradingDate - pd.to_timedelta(evidence.span - 1, unit="D")).clip(lower=start)
        right = evidence.TradingDate.clip(upper=end)
        evidence["covered"] = ((right - left).dt.days + 1).clip(lower=0)
        evidence["future_coverage"] = evidence.covered.where(evidence.TradingDate.gt(end), 0)
        coverage = evidence.groupby("FundClassID").agg(
            money_calendar_covered=("covered", "sum"),
            money_future_evidence_days=("future_coverage", "sum"),
        ).reset_index()
        agg = agg.merge(coverage, on="FundClassID", how="outer", validate="one_to_one")
        trailing_bad = evidence.loc[evidence.TradingDate.gt(end) & evidence.covered.gt(0)].groupby(
            "FundClassID").unexplained_gap.any()
        agg["money_unexplained_gap"] = agg.money_unexplained_gap.eq(True) | agg.FundClassID.map(trailing_bad).eq(True)
        agg["wave"] = wave
        agg["money_return"] = np.expm1(agg.money_log)
        out.append(agg)
    return pd.concat(out, ignore_index=True)


def shock_build(original, nav, money, calendar, meta, anomaly):
    frames = []
    nav = nav.loc[nav.TradingDate.isin(calendar)]
    for wave, (start, end) in WAVES.items():
        start, end = pd.Timestamp(start), pd.Timestamp(end)
        bday = calendar[calendar < start].max()
        eday = calendar[(calendar >= start) & (calendar <= end)].max()
        recent = nav.loc[nav.TradingDate.between(start - pd.Timedelta(days=16), start - pd.Timedelta(days=1))]
        window = nav.loc[nav.TradingDate.between(start, end)]
        b = recent.groupby("FundClassID").tail(1).rename(columns={
            "TradingDate": "baseline_date", "NAV": "baseline_nav", "AccumulativeNAV": "baseline_accnav"})
        e = window.groupby("FundClassID").tail(1).rename(columns={
            "TradingDate": "end_date", "NAV": "end_nav", "AccumulativeNAV": "end_accnav"})
        count = window.loc[window.NAV.gt(0) & window.AccumulativeNAV.gt(0)].groupby("FundClassID").size()
        f = original.loc[original.wave.eq(wave)].merge(meta, on="fund_code", how="left", validate="one_to_one")
        f = f.merge(b, on="FundClassID", how="left", validate="many_to_one").merge(
            e, on="FundClassID", how="left", validate="many_to_one")
        f["baseline_lag_days"] = (bday - f.baseline_date).dt.days
        f["end_lag_days"] = (eday - f.end_date).dt.days
        f["nav_valid_days"] = f.FundClassID.map(count).fillna(0)
        theory = len(calendar[(calendar >= start) & (calendar <= end)])
        if not f.shock_n_theory_days.eq(theory).all():
            raise ValueError("Original calendar cannot be reproduced")
        f["nav_coverage"] = f.nav_valid_days / theory
        f["shock_ret_candidate"] = cash_return(f.baseline_nav, f.baseline_accnav, f.end_accnav)
        f["return_method"] = "cash_nav_difference_over_initial_nav"
        f["quality_reason"] = ""
        use_income = f.is_money & ~f.baseline_nav.gt(0)
        ordinary = ~use_income
        add_reason(f, ordinary & ~(f.baseline_nav.gt(0) & f.end_nav.gt(0)
                                   & f.baseline_accnav.gt(0) & f.end_accnav.gt(0)), "invalid_unit_or_acc_nav")
        add_reason(f, ordinary & ((f.baseline_accnav + .001 < f.baseline_nav)
                                  | (f.end_accnav + .001 < f.end_nav)), "inconsistent_nav_units")
        change = f.end_accnav - f.end_nav - f.baseline_accnav + f.baseline_nav
        add_reason(f, ordinary & change.lt(-.001), "decreasing_cumulative_distribution")
        add_reason(f, ordinary & change.gt(.2 * f.baseline_nav), "large_distribution_or_share_event_unverified")
        add_reason(f, ordinary & (f.baseline_lag_days.isna() | f.baseline_lag_days.gt(7)), "stale_or_missing_baseline")
        add_reason(f, ordinary & (f.end_lag_days.isna() | f.end_lag_days.gt(3)), "stale_or_missing_endpoint")
        add_reason(f, ordinary & f.nav_coverage.lt(.8), "nav_coverage_below_80pct")
        f = f.merge(money.loc[money.wave.eq(wave)].drop(columns="wave"), on="FundClassID", how="left", validate="many_to_one")
        # merge retains row order; reset masks explicitly to the current frame.
        use_income = f.is_money & ~f.baseline_nav.gt(0)
        f.loc[use_income, "shock_ret_candidate"] = f.loc[use_income, "money_return"]
        f.loc[use_income, "return_method"] = "money_income_compound_posted_date"
        add_reason(f, use_income & f.money_calendar_covered.fillna(0).ne((end-start).days+1), "incomplete_money_calendar")
        add_reason(f, use_income & ~f.money_long_gap.eq(False), "long_money_disclosure_gap")
        add_reason(f, use_income & ~f.money_field_conflict.eq(False), "money_field_conflict")
        add_reason(f, use_income & f.money_unexplained_gap.eq(True), "missing_income_on_market_trading_day")
        add_reason(f, use_income & (f.money_income_sum.eq(0) & f.money_yield_max.eq(0)), "zero_income_unverified")
        add_reason(f, use_income & (f.money_income_sum.gt(0) & f.money_yield_max.eq(0)), "yield_conflict")
        add_reason(f, f.inception.isna() | f.inception.ge(start), "no_pre_window_inception")
        add_reason(f, f.currency.ne("CNY"), "non_cny_without_fx_conversion")
        add_reason(f, f.shock_ret_candidate.abs().gt(.2), "shock_exceeds_existing_20pct_bound")
        add_reason(f, ~np.isfinite(f.shock_ret_candidate), "nonfinite_return")
        f = f.merge(anomaly.loc[anomaly.component.eq("shock") & anomaly.exclude.eq(1),
                                ["fund_code", "wave", "reason"]].rename(columns={"reason": "legacy_reason"}),
                    on=["fund_code", "wave"], how="left", validate="one_to_one")
        legacy = f.legacy_reason.notna()
        f.loc[legacy, "quality_reason"] += "legacy:" + f.loc[legacy, "legacy_reason"] + ";"
        frames.append(f)
    s = pd.concat(frames, ignore_index=True).rename(columns={
        "shock_ret_rate": "shock_ret_original", "shock_usable": "shock_usable_original"})
    s["shock_usable"] = s.quality_reason.eq("").astype(int)
    s["shock_ret_rate"] = s.shock_ret_candidate.where(s.shock_usable.eq(1))
    s["shock_ret_rate_pp"] = s.shock_ret_rate * 100
    s["quality_reason"] = s.quality_reason.str.rstrip(";").replace("", "usable_under_stated_convention")
    s["return_version"] = VERSION
    return s


def summary_frame(c, s):
    rows = []
    for component, f, value, old, usable in [
        ("control", c, "ctrl_monthly_ret", "ctrl_monthly_ret_original", "ctrl_usable"),
        ("shock", s, "shock_ret_rate", "shock_ret_original", "shock_usable"),
    ]:
        for wave, g in f.groupby("wave", sort=True):
            common = np.isfinite(g[value]) & np.isfinite(g[old])
            delta = g[value] - g[old]
            rows.append(dict(component=component, wave=wave, rows=len(g), funds=g.fund_code.nunique(),
                             usable=int(g[usable].sum()), changed_gt_1bp=int((common & delta.abs().gt(.0001)).sum()),
                             max_abs_change_pp=float(delta[common].abs().max() * 100)))
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.root
    outputs = root / "20260823 exp stock/outputs"
    out = outputs / "fund_total_return"
    out.mkdir(exist_ok=True)
    support = out / "support"
    support.mkdir(exist_ok=True)
    orig_c, orig_s = read_csv(outputs / "ctrl_monthly_panel.csv"), read_csv(outputs / "shock_panel.csv")
    supplement = read_csv(outputs / "fund_quality_delivery/money_fund_control_supplement.csv")
    anomaly = read_csv(outputs / "fund_quality_delivery/other_ctrl_shock_anomalies.csv")
    meta = static_map(outputs, root)
    m = monthly_source(root)
    c = control_build(orig_c, m, meta, supplement, anomaly)
    assess = c.loc[c.NAV.gt(0) & c.PrvNAV.gt(0) & c.PrvAccumulativeNAV.gt(0)
                   & c.legacy_reason.isna()].copy()
    assess["definition_delta"] = cash_return(assess.PrvNAV, assess.PrvAccumulativeNAV, assess.AccumulativeNAV) - assess.old_formula_exact
    assessment = {"control_source_rows": len(c), "control_source_funds": c.fund_code.nunique()}
    for threshold, label in [(1e-8, "definition_changed"), (.0001, "definition_gt_1bp")]:
        z = assess.loc[assess.definition_delta.abs().gt(threshold)]
        assessment[label] = dict(rows=len(z), funds=z.fund_code.nunique(), fund_months=len(z[["fund_code", "history_month"]].drop_duplicates()))
    (support / "scope_assessment.json").write_text(json.dumps(assessment, indent=2), encoding="utf-8")
    print("SCOPE", assessment, flush=True)
    nav, daily_money, calendar = load_daily(root, set(meta.loc[meta.is_money, "FundClassID"]))
    mw = money_windows(daily_money, calendar)
    s = shock_build(orig_s, nav, mw, calendar, meta, anomaly)
    ccols = KEY + ["ctrl_monthly_ret", "ctrl_usable", "ctrl_monthly_ret_candidate",
                   "ctrl_monthly_ret_original", "return_method", "quality_reason", "return_version",
                   "history_start", "history_end", "currency", "baseline_date", "TradingDate",
                   "PrvNAV", "NAV", "PrvAccumulativeNAV", "AccumulativeNAV", "return_timing_rule"]
    scols = ["fund_code", "wave", "window_start", "window_end", "window_days", "shock_ret_rate",
             "shock_ret_rate_pp", "shock_usable", "shock_ret_candidate", "shock_ret_original",
             "shock_usable_original", "return_method", "quality_reason", "return_version", "currency",
             "baseline_date", "end_date", "baseline_nav", "end_nav", "baseline_accnav", "end_accnav",
             "nav_coverage", "baseline_lag_days", "end_lag_days", "money_observations",
             "money_calendar_covered", "money_future_evidence_days", "money_fields"]
    for frame, key, val, flag in [(c, KEY, "ctrl_monthly_ret", "ctrl_usable"),
                                  (s, ["fund_code", "wave"], "shock_ret_rate", "shock_usable")]:
        assert not frame.duplicated(key).any()
        assert frame[val].notna().eq(frame[flag].eq(1)).all()
        assert np.isfinite(frame.loc[frame[flag].eq(1), val]).all()
        assert frame.loc[frame[flag].eq(1), "currency"].eq("CNY").all()
    assert len(c) == len(orig_c) and len(s) == len(orig_s)
    assert c.groupby(["fund_code", "history_month"]).ctrl_monthly_ret.nunique().le(1).all()
    c[ccols].to_csv(out / "ctrl_monthly_total_return_v1.csv", index=False, encoding="utf-8-sig", float_format="%.12g")
    s[scols].to_csv(out / "shock_panel_total_return_v1.csv", index=False, encoding="utf-8-sig", float_format="%.12g")
    summ = summary_frame(c, s)
    summ.to_csv(support / "comparison_by_wave.csv", index=False)
    reason_rows = []
    for component, f in [("control", c), ("shock", s)]:
        for reason, count in f.quality_reason.str.split(";").explode().value_counts().items():
            reason_rows.append(dict(component=component, reason=reason, rows=int(count)))
    pd.DataFrame(reason_rows).to_csv(support / "quality_reason_counts.csv", index=False)
    money_audit = meta.loc[meta.is_money].merge(
        daily_money.assign(income_field=np.select([daily_money[f].notna() for f in INCOME_FIELDS], INCOME_FIELDS, default="none"))
        [["FundClassID", "income_field"]].drop_duplicates(), on="FundClassID", how="left", validate="one_to_many")
    money_audit.to_csv(support / "money_income_units.csv", index=False, encoding="utf-8-sig")
    s.loc[s.shock_usable_original.ne(s.shock_usable), scols].to_csv(support / "shock_eligibility_changes.csv", index=False, encoding="utf-8-sig")
    metadata = {"return_version": VERSION, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "source_root": str(root), "scope_assessment": assessment,
                "control_usable": int(c.ctrl_usable.sum()), "shock_usable": int(s.shock_usable.sum()),
                "money_shock_usable": int((s.shock_usable.eq(1) & s.return_method.eq("money_income_compound_posted_date")).sum()),
                "old_shock_now_unusable": int((s.shock_usable_original.eq(1) & s.shock_usable.eq(0)).sum()),
                "new_shock_usable": int((s.shock_usable_original.eq(0) & s.shock_usable.eq(1)).sum()),
                "platform_run": False}
    sources = [outputs / "ctrl_monthly_panel.csv", outputs / "shock_panel.csv", outputs / "fund_static.csv",
               outputs / "fund_quality_delivery/money_fund_control_supplement.csv",
               outputs / "fund_quality_delivery/other_ctrl_shock_anomalies.csv"]
    metadata["input_sha256"] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    metadata["output_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob("*.csv"))}
    inventory = []
    for p in sorted(root.glob("**/*.dta")):
        if "20260823 exp stock" not in str(p):
            inventory.append(dict(path=str(p.relative_to(root)), bytes=p.stat().st_size, mtime_ns=p.stat().st_mtime_ns))
    (support / "source_inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    (support / "build_manifest.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(summ.to_string(index=False), flush=True)
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
