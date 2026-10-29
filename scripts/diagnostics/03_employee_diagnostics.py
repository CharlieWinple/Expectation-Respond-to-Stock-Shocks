# === CELL 1: Imports and compact report helpers ===
"""Employee round-two identification diagnostics, no primary outcome regressions."""
import time
import textwrap
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests
from marvel.AntPrint import ant_read_data, ant_print_all

STARTED = time.perf_counter()
REPORT = []
ISSUES = []


def clean(s):
    s = s.astype("string").str.strip()
    return s.mask(s.str.lower().isin(["", "nan", "none", "null", "<na>"]))


def number(s):
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def dates(s):
    # Parse YYYYMMDD and common timestamp strings separately (no numeric epochs).
    s = clean(s).str.replace(r"\.0$", "", regex=True)
    compact = s.str.fullmatch(r"\d{8}", na=False)
    out = pd.to_datetime(s.where(~compact), errors="coerce")
    out.loc[compact] = pd.to_datetime(s.loc[compact], format="%Y%m%d", errors="coerce")
    return out.dt.normalize()


def fund(s):
    s = clean(s).str.upper().str.replace(r"\.0$", "", regex=True)
    numeric = s.str.fullmatch(r"\d+", na=False)
    s.loc[numeric] = s.loc[numeric].str.zfill(6)
    return s


def add(title, columns, rows):
    REPORT.append((title, columns, rows))


def fmt(x):
    if pd.isna(x):
        return "NA"
    if isinstance(x, (float, np.floating)):
        return f"{x:.5g}"
    return str(x)


def median(s):
    valid = s.dropna()
    return valid.median() if len(valid) else np.nan


def read_table(name, cols, label):
    # Platform read errors stop this cell; fix the source before rerunning.
    d = ant_read_data(name, cols=list(dict.fromkeys(cols)))
    if d is None:
        ISSUES.append(label + ":read_returned_none")
        return None
    missing = sorted(set(cols) - set(d.columns))
    if missing:
        ISSUES.append(label + ":missing_columns:" + ",".join(missing))
        return None
    return d.copy()


def unique_source(d, keys, label):
    """Collapse identical rows; conflicting keys are blocked, never first-selected."""
    d = d.drop_duplicates().copy()
    bad = d[keys].isna().any(axis=1)
    conflict = d.duplicated(keys, keep=False)
    if bad.any() or conflict.any():
        ISSUES.append(label + ":invalid_or_conflicting_keys")
        return None
    return d


# === CELL 2: Settings and verified questionnaire field map ===
REVISION = "employee_round2_v1"
WAVES = ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"]
PREFIX = "frlab_sample_project_202405290032751511010004_v2_sme_"
SURVEY_TEMPLATE = PREFIX + "sp_smesurvey{wave}_202512"
HOLDING_TABLE = PREFIX + "fund_invest_202512"
SHOCK_TABLE = "shock_panel_nav_annotated_v1"
CONTROL_TABLE = "ctrl_monthly_nav_annotated_v1"
RETURN_VERSION = "nav_price_annotated_v1"
OWNER_ANSWER = "我是小微经营者_我自愿参与本次调查"
NONOWNER_ANSWER = "我不是小微经营者"
EMPLOYEE_ANSWER = "作为小微经营户的雇员_帮助其收付款"
WORKING_ANSWER = "我在工作"
ANALYSIS_WAVES = WAVES[1:]  # q2 descriptive only; no q2->q3 prior expectation pooling.
MIN_DIAG_N = 50
MIN_CLUSTERS = 30
CELL_BINS = (3, 3, 3)
ALT_CELL_BINS = (5, 3, 3)  # Variation audit only, not automatic model selection.
MAX_OPTIONS = 20
MAX_LABEL_CHARS = 100
MIN_COVERAGE = 0.999999
HOLD_MONTH = dict(zip(WAVES, ["2024-05", "2024-08", "2024-11", "2025-02", "2025-05"]))
OUTCOMES = ["gdp", "house", "cpi", "rate", "stock"]
EMP_CODES = {
    "2024q2": ["v25", "v26", "v27", "v28", None],
    "2024q3": ["v32", "v33", "v34", "v35", "v36"],
    "2024q4": ["v18", "v19", "v20", "v21", "v22"],
    "2025q1": ["v18", "v19", "v20", "v21", "v22"],
    "2025q2": ["v18", "v19", "v20", "v21", "v22"],
}
OWNER_CODES = {
    "2024q2": [],  # No addon read and no substitution from employee fields.
    "2024q3": ["v192", "v193", "v195", "v194", "v196"],
    "2024q4": ["v182", "v184", "v186", "v185", "v187"],
    "2025q1": ["v176", "v178", "v180", "v179", "v181"],
    "2025q2": ["v185", "v187", "v189", "v188", "v190"],
}
OWNER_REVENUE = dict(zip(WAVES, ["v65", "v66", "v52", "v53", "v53"]))
EMP_EDUCATION = dict(zip(WAVES, ["v31", "v39", "v25", "v26", "v26"]))
EMP_CONSUMPTION = dict(zip(WAVES, ["v15", "v31", "v17", "v17", "v17"]))
VERSION_EDUCATION = {"2024q2": ["v163"], "2024q3": ["v166"],
                     "2024q4": ["v168", "v174", "v217"],
                     "2025q1": ["v163"], "2025q2": ["v174"]}
BASE_COLS = ["user_id", "submit_id", "submit_date", "extro_info",
             "user_age", "city_level_from_yicai", "v1", "v2", "v3",
             "v5", "v9", "v10", "v11", "v12"]
SURVEYS = {}
OPTIONS = []
BRANCH = []
DUPLICATES = []
VERSIONS = []
TIMING = []
FUNNEL = []
Y_COVERAGE = []
HOLDING_SUMMARY = []
CALENDAR = []
ROUTING = []
CODING = []
QUALITY = []
EXPOSURE = []


# === CELL 3: Survey reads, branch discovery and duplicate audit ===
for wave in WAVES:
    cols = BASE_COLS + [c for c in EMP_CODES[wave] if c] + OWNER_CODES[wave]
    cols += [OWNER_REVENUE[wave], EMP_EDUCATION[wave], EMP_CONSUMPTION[wave]]
    cols += VERSION_EDUCATION[wave]
    d = read_table(SURVEY_TEMPLATE.format(wave=wave), cols, wave + "_survey")
    if d is None:
        continue
    for c in d.columns:
        d[c] = clean(d[c])
    raw_n = len(d)
    d = d.drop_duplicates().copy()
    repeated = d.user_id.notna() & d.duplicated("user_id", keep=False)
    duplicate_submit = d.submit_id.notna() & d.duplicated("submit_id", keep=False)
    response_cols = ["v1", "v3", "v10"] + [c for c in EMP_CODES[wave] if c]
    conflicts = d.loc[repeated].groupby("user_id")[response_cols].nunique(dropna=False)
    DUPLICATES.append([wave, raw_n, raw_n - len(d), int(d.user_id.isna().sum()),
                       int(repeated.sum()), int(conflicts.gt(1).any(axis=1).sum()),
                       int(duplicate_submit.sum())])
    d["unique_response"] = d.user_id.notna() & ~repeated & ~duplicate_submit
    d["emp_answers"] = d[[c for c in EMP_CODES[wave] if c]].notna().any(axis=1)
    d["emp_wage"] = d.v10.notna()
    d["owner_answers"] = (d[OWNER_CODES[wave]].notna().any(axis=1)
                            if OWNER_CODES[wave] else False)
    d["owner_revenue"] = d[OWNER_REVENUE[wave]].notna()
    d["nonowner"] = d.v1.eq(NONOWNER_ANSWER).fillna(False)
    d["route_v2"] = d.v2.eq(EMPLOYEE_ANSWER).fillna(False)
    d["route_v3"] = d.v3.eq(WORKING_ANSWER).fillna(False)
    d["candidate"] = d.nonowner & (d.route_v2 | d.route_v3)
    d["identity_conflict"] = d.route_v2 & d.v3.notna() & ~d.route_v3
    for route, mask in [("v2_only", d.route_v2 & ~d.route_v3),
                        ("v3_only", d.route_v3 & ~d.route_v2),
                        ("both", d.route_v2 & d.route_v3),
                        ("neither", ~d.route_v2 & ~d.route_v3)]:
        g = d.loc[d.nonowner & mask]
        ROUTING.append([wave, route, len(g), int(g.v3.isna().sum()),
                        int(g.v9.notna().sum()), int(g.v10.notna().sum()),
                        int(g.identity_conflict.sum())])
    if (~d.v1.isin([OWNER_ANSWER, NONOWNER_ANSWER])).any():
        ISSUES.append(wave + ":unrecognized_or_missing_identity")
    identity = d.v1.fillna("[MISSING]")
    counts = identity.value_counts()
    shown = list(counts.head(MAX_OPTIONS).index)
    if len(counts) > MAX_OPTIONS:
        ISSUES.append(wave + ":v1_categories_overflow")
    for code, answer in enumerate(shown, 1):
        g = d.loc[identity.eq(answer)]
        label = answer if len(answer) <= MAX_LABEL_CHARS else "[LABEL_WITHHELD_LONG]"
        BRANCH.append([wave, "I" + str(code), label, len(g), int(g.emp_wage.sum()),
                       int(g.emp_answers.sum()), int(g.owner_revenue.sum()),
                       int(g.owner_answers.sum()),
                       int(((g.emp_wage | g.emp_answers) & (g.owner_revenue | g.owner_answers)).sum())])
    d["submit_dt"] = dates(d.submit_date)
    matches = d.extro_info.str.findall(r"(?:^|;)answerSeconds\s*=\s*([0-9]+(?:\.[0-9]+)?)(?=;|$)")
    d["seconds"] = number(matches.str[0]).where(matches.str.len().eq(1))
    d["duration_ambiguous"] = matches.str.len().gt(1).fillna(False)
    for y, c in zip(OUTCOMES, EMP_CODES[wave]):
        d["answer_" + y] = d[c] if c else pd.Series(pd.NA, index=d.index, dtype="string")
    v = d[VERSION_EDUCATION[wave]]
    VERSIONS.append([wave, "/".join(VERSION_EDUCATION[wave]),
                     "/".join(str(int(v[c].notna().sum())) for c in v),
                     int(v.notna().sum(axis=1).gt(1).sum()),
                     int(v.nunique(axis=1, dropna=True).gt(1).sum())])
    SURVEYS[wave] = d


# === CELL 4: Wave-specific expectation coding and compact trait dictionaries ===
GDP = {"增长0_3": 1.5, "增长3_4": 3.5, "增长4_5": 4.5,
       "增长5_6": 5.5, "增长6_8": 7., "增长8_以上": 9.,
       "下降0_3": -1.5, "下降3_以上": -4.}
HOUSE = {"上升0_5": 2.5, "上升5_10": 7.5, "上升10_15": 12.5,
         "上升15_30": 22.5, "上升30_以上": 35.,
         "下降0_5": -2.5, "下降5_10": -7.5, "下降10_15": -12.5,
         "下降15_30": -22.5, "下降30_以上": -35.}
CPI = {"增长0_1": .5, "增长1_2": 1.5, "增长2_3": 2.5, "增长3_以上": 4.,
       "下降0_1": -.5, "下降1_2": -1.5, "下降2_3": -2.5,
       "下降3_5": -4., "下降5_以上": -6.}
RATE = {"0_1": .5, "1_2": 1.5, "2_3": 2.5, "3_4": 3.5, "4_5": 4.5, "5_以上": 6.}
STOCK_Q3 = {"2200点以下": 2000., "2200_2400点": 2300., "2400_2600点": 2500.,
            "2600_2800点": 2700., "2800_3000点": 2900., "3000_3300点": 3150.,
            "3300_3600点": 3450., "3600点以上": 3800.}
STOCK_LATER = {"2600点以下": 2400., "2600_2800点": 2700., "2800_3000点": 2900.,
               "3000_3300点": 3150., "3300_3600点": 3450., "3600_3800点": 3700.,
               "3800_4000点": 3900., "4000点以上": 4200.}
UNKNOWN_ANSWERS = ["不确定", "不知道", "不清楚", "不了解", "无法判断", "不愿回答", "拒绝回答", "不适用"]
EDUCATION_MAP = {"小学及以下": 0., "初中": 0.,
                 "高中_普通高中_成人高中_职业高中_中专_技校": 0.,
                 "大学专科_专科_高职高专_技师学院": 1., "大学本科": 1., "研究生及以上": 1.}
CODING_OK = {}
OPTION_SUMMARY = []
TRAITS = []
for wave, d in SURVEYS.items():
    d["age"] = number(d.user_age).where(number(d.user_age).between(16, 100))
    d["college"] = d[EMP_EDUCATION[wave]].map(EDUCATION_MAP)
    d["path_v2"] = d.route_v2.astype(float)
    for y in OUTCOMES:
        raw = d["answer_" + y]
        mapping = {"gdp": GDP, "house": HOUSE, "cpi": CPI, "rate": RATE,
                   "stock": STOCK_Q3 if wave == "2024q3" else STOCK_LATER}[y]
        if wave == "2024q2":
            mapping = {}  # Retain raw q2 fields; not an equivalent expectation target.
        d["y_" + y] = raw.map(mapping).astype(float)
        unknown = raw.isin(UNKNOWN_ANSWERS)
        unmapped = raw.notna() & ~unknown & d["y_" + y].isna()
        CODING_OK[(wave, y)] = wave in ANALYSIS_WAVES and not unmapped.loc[d.nonowner].any()
        if wave in ANALYSIS_WAVES and not CODING_OK[(wave, y)]:
            ISSUES.append(wave + ":" + y + ":unmapped_answers_tests_blocked")
        if not CODING_OK[(wave, y)]:
            d["y_" + y] = np.nan
        # Missing, unknown and recognized answers distinguished in audit.
        d["clear_" + y] = d["y_" + y].notna().astype(float) if CODING_OK[(wave, y)] else np.nan
        g = d.loc[d.candidate]
        CODING.append([wave, y, len(g), int(raw.loc[g.index].isna().sum()),
                       int(unknown.loc[g.index].sum()),
                       int(unmapped.loc[g.index].sum()) if wave in ANALYSIS_WAVES else np.nan,
                       int(g["y_" + y].notna().sum()),
                       "OK" if CODING_OK[(wave, y)] else "Q2_SEPARATE" if wave == "2024q2" else "BLOCK"])
    candidate = d.loc[d.candidate]
    targets = [("job_type", candidate.v9), ("education", candidate[EMP_EDUCATION[wave]]),
               ("wage", candidate.v10)]
    # Only unmapped expectation labels, never repeat the round-one option dump.
    if wave in ANALYSIS_WAVES:
        for y in OUTCOMES:
            if not CODING_OK[(wave, y)]:
                targets.append(("unmapped_" + y, d.loc[d.nonowner, "answer_" + y]))
    for target, s in targets:
        counts = s.dropna().value_counts()
        numeric = number(s)
        numeric_ok = s.notna().any() and numeric.loc[s.notna()].notna().all()
        continuous = len(counts) > MAX_OPTIONS and numeric_ok
        shown = counts.iloc[:0] if continuous else counts.head(MAX_OPTIONS)
        omitted = 0 if continuous else int(counts.iloc[MAX_OPTIONS:].sum())
        OPTION_SUMMARY.append([wave, target, len(s), int(s.isna().sum()), len(counts),
                               "numeric_summary" if continuous else "options", omitted])
        if continuous:
            OPTIONS.append([wave, target, "NUMERIC:p0/p25/p50/p75/p100",
                            "/".join(fmt(x) for x in numeric.quantile([0, .25, .5, .75, 1])),
                            int(numeric.notna().sum())])
        else:
            for k, (label, n) in enumerate(shown.items(), 1):
                label = label if len(label) <= MAX_LABEL_CHARS else "[LABEL_WITHHELD_LONG]"
                OPTIONS.append([wave, target, "O" + str(k), label, int(n)])
            if omitted:
                ISSUES.append(wave + ":" + target + ":options_truncated_review_needed")
    TRAITS.append([wave, len(candidate), int(number(candidate.user_age).notna().sum()),
                   int(candidate[EMP_EDUCATION[wave]].notna().sum()),
                   int(candidate.city_level_from_yicai.notna().sum()),
                   int(candidate.v5.notna().sum()), int(candidate.v9.notna().sum()),
                   int(candidate.v10.notna().sum()), int(candidate.v11.notna().sum()),
                   int(candidate[EMP_CONSUMPTION[wave]].notna().sum())])
    SURVEYS[wave] = d


# === CELL 5: Fund panels, source integrity and wave calendars ===
shock = read_table(SHOCK_TABLE, ["fund_code", "wave", "shock_ret_rate_pp", "shock_usable",
                   "window_start", "window_end", "return_version"], "shock")
history = read_table(CONTROL_TABLE, ["fund_code", "wave", "history_month",
                     "ctrl_monthly_ret", "return_version"], "history")
for label, panel in [("shock", shock), ("history", history)]:
    if panel is not None:
        panel["fund_code"] = fund(panel.fund_code)
        panel["wave"] = clean(panel.wave).str.lower().replace(
            {"24q2": "2024q2", "24q3": "2024q3", "24q4": "2024q4",
             "25q1": "2025q1", "25q2": "2025q2"})
        if not panel.return_version.eq(RETURN_VERSION).all():
            ISSUES.append(label + ":return_version_mismatch")
            if label == "shock":
                shock = None
            else:
                history = None
if shock is not None:
    shock["window_start"] = dates(shock.window_start)
    shock["window_end"] = dates(shock.window_end)
    shock["shock_ret_rate_pp"] = number(shock.shock_ret_rate_pp)
    shock["shock_usable"] = number(shock.shock_usable)
    shock = unique_source(shock, ["wave", "fund_code"], "shock")
if history is not None:
    history["month"] = dates(history.history_month.astype("string").str.slice(0, 7) + "-01").dt.to_period("M")
    history["ctrl_monthly_ret"] = number(history.ctrl_monthly_ret)
    history = unique_source(history.drop(columns="history_month"), ["wave", "fund_code", "month"], "history")
WINDOWS = {}
for wave in WAVES:
    hdate = pd.Period(HOLD_MONTH[wave], freq="M").end_time.normalize()
    s = shock.loc[shock.wave.eq(wave)] if shock is not None else pd.DataFrame()
    ok = (len(s) > 0 and s.window_start.notna().all() and s.window_end.notna().all()
          and s.window_start.nunique() == 1 and s.window_end.nunique() == 1)
    start = s.window_start.iloc[0] if ok else pd.NaT
    end = s.window_end.iloc[0] if ok else pd.NaT
    ok = bool(ok and hdate < start <= end)
    CALENDAR.append([wave, str(hdate.date()), str(start), str(end), "OK" if ok else "BLOCK"])
    if ok:
        WINDOWS[wave] = (start, end)
    else:
        ISSUES.append(wave + ":window_or_snapshot_timing_invalid")


# === CELL 6: Holdings coverage with raw denominators and strict history ===
holding = read_table(HOLDING_TABLE, ["匿名化用户id", "基金代码", "当月月底日持有金额元", "日期"], "holding")
PORTFOLIOS = {}
if holding is not None:
    holding = holding.rename(columns={"匿名化用户id": "user_id", "基金代码": "fund_code",
                                       "当月月底日持有金额元": "amount", "日期": "date"})
    holding["user_id"] = clean(holding.user_id)
    holding["fund_code"] = fund(holding.fund_code)
    holding["date"] = dates(holding.date)
    holding["amount"] = number(holding.amount)
    invalid_dates = int(holding.date.isna().sum())
    invalid_users = int(holding.user_id.isna().sum())
    add("HOLDING_SOURCE", ["invalid_dates", "invalid_user_ids"], [[invalid_dates, invalid_users]])
    # Unlocatable rows prevent reliable completeness claims; keep other diagnostics.
    if invalid_dates or invalid_users:
        ISSUES.append("holding:unlocatable_rows_coverage_blocked")
        holding = None
if holding is not None:
    all_users = pd.concat([d.user_id for d in SURVEYS.values()], ignore_index=True).dropna().unique() if SURVEYS else []
    holding = holding.loc[holding.user_id.isin(all_users)].drop_duplicates().copy()
    for wave in WAVES:
        snapshot = pd.Period(HOLD_MONTH[wave], freq="M").end_time.normalize()
        month_mask = holding.date.dt.to_period("M").eq(pd.Period(HOLD_MONTH[wave], freq="M"))
        off_date = int((month_mask & holding.date.ne(snapshot)).sum())
        h = holding.loc[holding.date.eq(snapshot)].copy()
        if off_date:
            ISSUES.append(wave + ":non_monthend_holding_rows_coverage_blocked")
            continue
        if h.empty:
            ISSUES.append(wave + ":no_matching_snapshot_rows")
            continue
        h["bad"] = (h.amount.isna() | h.amount.lt(0) | h.fund_code.isna()
                    | h.duplicated(["user_id", "fund_code"], keep=False))
        bad_users = h.groupby("user_id").bad.any()
        users = pd.DataFrame({"user_id": bad_users.index, "bad_holding": bad_users.values})
        good = h.loc[~h.user_id.isin(bad_users[bad_users].index)].copy()
        totals = good.groupby("user_id", as_index=False).agg(capital=("amount", "sum"))
        users = users.merge(totals, on="user_id", how="left", validate="one_to_one")
        s = shock.loc[shock.wave.eq(wave), ["fund_code", "shock_ret_rate_pp", "shock_usable"]] if shock is not None else None
        hist = history.loc[history.wave.eq(wave)].copy() if history is not None else None
        if s is not None and wave in WINDOWS:
            good = good.merge(s, on="fund_code", how="left", validate="many_to_one")
            good["shock_amount"] = good.amount.where(good.shock_ret_rate_pp.notna() & good.shock_usable.eq(1), 0)
        else:
            good["shock_amount"] = np.nan
        if hist is not None and wave in WINDOWS:
            start, _ = WINDOWS[wave]
            expected = pd.period_range(end=start.to_period("M") - 1, periods=12, freq="M")
            hist = hist.loc[hist.month.isin(expected) & hist.ctrl_monthly_ret.notna()]
            count = hist.groupby("fund_code").month.nunique()
            good["history_amount"] = good.amount.where(good.fund_code.map(count).eq(12), 0)
        else:
            good["history_amount"] = np.nan
        amounts = good.groupby("user_id", as_index=False)[["shock_amount", "history_amount"]].sum(min_count=1)
        users = users.merge(amounts, on="user_id", how="left", validate="one_to_one")
        users["shock_coverage"] = users.shock_amount / users.capital.where(users.capital.gt(0))
        users["history_coverage"] = users.history_amount / users.capital.where(users.capital.gt(0))
        # Gains in 10,000 yuan: amount * percentage-point return / 100 / 10,000.
        good["gain"] = (good.amount * good.shock_ret_rate_pp / 1e6
                        if "shock_ret_rate_pp" in good else np.nan)
        gains = good.groupby("user_id", as_index=False).gain.sum(min_count=1)
        users = users.merge(gains, on="user_id", how="left", validate="one_to_one")
        users["hist_mean"] = np.nan
        users["hist_risk"] = np.nan
        if hist is not None and wave in WINDOWS and len(hist):
            wide = hist.pivot(index="fund_code", columns="month", values="ctrl_monthly_ret").reindex(columns=expected)
            wide.columns = ["m" + str(i) for i in range(12)]
            monthly_cols = list(wide.columns)
            weighted = good[["user_id", "fund_code", "amount"]].merge(
                wide.reset_index(), on="fund_code", how="left", validate="many_to_one")
            weighted[monthly_cols] = weighted[monthly_cols].mul(weighted.amount, axis=0)
            monthly = weighted.groupby("user_id")[monthly_cols].sum(min_count=1)
            monthly = monthly.div(users.set_index("user_id").capital, axis=0)
            users["hist_mean"] = users.user_id.map(monthly.mean(axis=1))
            users["hist_risk"] = users.user_id.map(monthly.std(axis=1, ddof=1))
        users.loc[users.shock_coverage.lt(MIN_COVERAGE) | users.shock_coverage.isna(), "gain"] = np.nan
        users.loc[users.history_coverage.lt(MIN_COVERAGE) | users.history_coverage.isna(),
                  ["hist_mean", "hist_risk"]] = np.nan
        users["logcapital"] = np.log(users.capital.where(users.capital.gt(0)))
        users["amount10k"] = users.capital / 10000
        PORTFOLIOS[wave] = users


# === CELL 7: Time audit, source categories and sequential candidate funnel ===
for wave, d in SURVEYS.items():
    p = PORTFOLIOS.get(wave)
    d = d.copy()
    if p is not None:
        d = d.merge(p, on="user_id", how="left", validate="many_to_one", indicator="holding_join")
    else:
        for c in ["capital", "shock_coverage", "history_coverage", "gain", "hist_mean",
                  "hist_risk", "logcapital", "amount10k"]:
            d[c] = np.nan
        d["bad_holding"] = False
        d["holding_join"] = "unavailable"
    g = d.loc[d.candidate & d.unique_response].copy()
    sec = g.seconds
    if wave in WINDOWS:
        start, end = WINDOWS[wave]
        g["lag_days"] = (g.submit_dt - end).dt.days
        g["post"] = g.submit_dt.gt(end)
    else:
        g["lag_days"] = np.nan
        g["post"] = False
    TIMING.append([wave, len(g), int(g.submit_dt.isna().sum()), int(g.post.sum()),
                   fmt(median(g.lag_days)), int(g.lag_days.gt(30).sum()),
                   int(sec.isna().sum()), int(g.duration_ambiguous.sum()),
                   fmt(sec.quantile(.1)), fmt(median(sec)), fmt(sec.quantile(.9)),
                   int(sec.lt(60).sum()), int(sec.lt(120).sum()), int(sec.lt(180).sum())])
    matched = g.holding_join.eq("both")
    HOLDING_SUMMARY.append([wave, len(g), "available" if p is not None else "BLOCKED",
                            int(matched.sum()), int((matched & g.bad_holding.eq(True)).sum()),
                            int(g.capital.eq(0).sum()), int(g.capital.gt(0).sum()),
                            int(g.holding_join.eq("left_only").sum()),
                            fmt(median(g.loc[g.capital.gt(0), "shock_coverage"])),
                            fmt(median(g.loc[g.capital.gt(0), "history_coverage"]))])
    FUNNEL.append([wave, "candidate_all", int(d.candidate.sum()),
                   int(d.loc[d.candidate, "user_id"].nunique()), "OBSERVED"])
    masks = [("candidate_unique", pd.Series(True, index=g.index)),
             ("post_window", g.post), ("positive_valid_holding", g.capital.gt(0)),
             ("shock_complete", g.shock_coverage.ge(MIN_COVERAGE)),
             ("history12_complete", g.history_coverage.ge(MIN_COVERAGE))]
    keep = pd.Series(True, index=g.index)
    stage_ok = True
    for stage, mask in masks:
        if stage == "post_window":
            stage_ok = stage_ok and wave in WINDOWS
        elif stage == "positive_valid_holding":
            stage_ok = stage_ok and p is not None
        elif stage == "shock_complete":
            stage_ok = stage_ok and shock is not None
        elif stage == "history12_complete":
            stage_ok = stage_ok and history is not None
        keep &= mask.fillna(False)
        FUNNEL.append([wave, stage, int(keep.sum()) if stage_ok else np.nan,
                       int(g.loc[keep, "user_id"].nunique()) if stage_ok else np.nan,
                       "OBSERVED" if stage_ok else "BLOCKED"])
    for y, code in zip(OUTCOMES, EMP_CODES[wave]):
        answer = g["answer_" + y]
        unknown = answer.isin(UNKNOWN_ANSWERS)
        Y_COVERAGE.append([wave, y, code or "NOT_ASKED", len(g), int(answer.notna().sum()),
                           int(unknown.sum()), int((keep & answer.notna()).sum()) if stage_ok else np.nan,
                           int((keep & g["y_" + y].notna()).sum()) if stage_ok and CODING_OK[(wave, y)] else np.nan])
    d["eligible"] = (d.nonowner & d.unique_response & d.capital.gt(0)
                     & d.shock_coverage.ge(MIN_COVERAGE) & d.history_coverage.ge(MIN_COVERAGE)
                     & d[["gain", "hist_mean", "hist_risk"]].notna().all(axis=1))
    d["eligible"] &= d.submit_dt.gt(WINDOWS[wave][1]) if wave in WINDOWS else False
    d["wave"] = wave
    SURVEYS[wave] = d


# === CELL 8: Fixed reference cells and strictly dated previous-wave answers ===
PANELS = []
PRIOR_AUDIT = []
for wave in ANALYSIS_WAVES:
    if wave not in SURVEYS:
        continue
    d = SURVEYS[wave].loc[SURVEYS[wave].eligible].copy()
    # Reference = eligible nonowners, before employee/Y/prior filtering. Ties stay together.
    for name, bins in [("cell", CELL_BINS), ("altcell", ALT_CELL_BINS)]:
        label = pd.Series(wave, index=d.index, dtype="string")
        for col, nbin in zip(["logcapital", "hist_risk", "hist_mean"], bins):
            b = np.ceil(d[col].rank(method="average", pct=True) * nbin).clip(1, nbin)
            label = label + ":" + b.astype("Int64").astype("string")
        d[name] = label
    # Fixed pooled-reference standardization is applied below, never refit per target.
    previous = WAVES[WAVES.index(wave) - 1]
    prior_fields = ["age", "college", "path_v2"] + ["y_" + y for y in OUTCOMES]
    for c in prior_fields:
        d["pre_" + c] = np.nan
    d["prior_employee"] = False
    if previous in SURVEYS and wave in WINDOWS:
        p = SURVEYS[previous]
        p = p.loc[p.unique_response & p.candidate & p.submit_dt.lt(WINDOWS[wave][0]),
                  ["user_id"] + prior_fields].copy()
        p["prior_employee"] = True
        p = p.rename(columns={c: "pre_" + c for c in prior_fields})
        d = d.drop(columns=["pre_" + c for c in prior_fields] + ["prior_employee"]).merge(
            p, on="user_id", how="left", validate="one_to_one")
        d["prior_employee"] = d.prior_employee.eq(True)
    PRIOR_AUDIT.append([wave, len(d), int(d.candidate.sum()), int(d.prior_employee.sum()),
                        int((d.candidate & d.prior_employee).sum())])
    PANELS.append(d)
BASE = pd.concat(PANELS, ignore_index=True) if PANELS else pd.DataFrame()
CONTROL_COLS = []
if len(BASE):
    zcols = []
    for col in ["logcapital", "hist_risk", "hist_mean"]:
        sd = BASE[col].std()
        z = (BASE[col] - BASE[col].mean()) / sd if sd > 0 else BASE[col] * 0
        name = "z_" + col
        BASE[name] = z
        zcols.append(name)
    terms = zcols.copy()
    for i, a in enumerate(zcols):
        for b in zcols[i:]:
            name = a + "_x_" + b
            BASE[name] = BASE[a] * BASE[b]
            terms.append(name)
    terms += ["amount10k"]
    for wave in ANALYSIS_WAVES:
        for term in terms:
            name = wave + "_" + term
            BASE[name] = BASE[term] * BASE.wave.eq(wave)
            CONTROL_COLS.append(name)


# === CELL 9: Residual variation and auxiliary conditional-association tests ===
def residualize(d, values, cell_col, model):
    """FWL with absorbed cell intercepts and rank-aware SVD; no dense FE matrix."""
    a = pd.DataFrame(np.asarray(values, dtype=float), index=d.index)
    a = (a - a.groupby(d[cell_col]).transform("mean")).to_numpy()
    rank = 0
    if model == "F" and len(d):
        c = d[CONTROL_COLS].astype(float)
        c = (c - c.groupby(d[cell_col]).transform("mean")).to_numpy()
        scale = np.sqrt((c * c).sum(axis=0))
        c = c[:, scale > 1e-12] / scale[scale > 1e-12]
        if c.shape[1]:
            u, sv, _ = np.linalg.svd(c, full_matrices=False)
            rank = int((sv > sv[0] * max(c.shape) * np.finfo(float).eps).sum())
            q = u[:, :rank]
            a -= q @ (q.T @ a)
    return a, int(d[cell_col].nunique()) + rank


VARIATION = []
TESTS = []
WAVE_SHARE = []


def variation(d, scope, sample, model, cell_col="cell"):
    if d.empty:
        VARIATION.append([scope, sample, model, cell_col, 0, 0, 0] + [np.nan] * 6)
        return
    r, k = residualize(d, d[["gain"]], cell_col, model)
    ss = r[:, 0] ** 2
    total = ss.sum()
    raw = ((d.gain - d.gain.mean()) ** 2).sum()
    sizes = d.groupby(cell_col).size()
    VARIATION.append([scope, sample, model, cell_col, len(d), d.user_id.nunique(), len(sizes),
                      int(sizes.eq(1).sum()), np.sqrt(total / len(d)), total / raw if raw > 0 else np.nan,
                      np.sort(ss)[-max(1, int(np.ceil(.01 * len(d)))):].sum() / total if total > 1e-20 else np.nan,
                      ss.max() / total if total > 1e-20 else np.nan, len(d) - k - 1])
    if scope == "pooled" and sample == "BASE" and cell_col == "cell":
        t = d[["wave"]].copy()
        t["ss"] = ss
        for w, g in t.groupby("wave"):
            WAVE_SHARE.append([model, w, len(g), g.ss.sum() / total if total > 1e-20 else np.nan])


def association(d, target, family, model):
    g = d.loc[d[target].notna()].copy()
    n, clusters = len(g), g.user_id.nunique()
    row = dict(family=family, target=target, model=model, N=n, users=clusters,
               missing=len(d)-n, beta=np.nan, se=np.nan, lo=np.nan, hi=np.nan,
               p=np.nan, holm=np.nan, sd_effect=np.nan, status="SMALL_SAMPLE")
    if n < MIN_DIAG_N or clusters < MIN_CLUSTERS:
        TESTS.append(row)
        return
    r, k = residualize(g, g[["gain", target]], "cell", model)
    x, y = r[:, 0], r[:, 1]
    xx = x @ x
    if n <= k + 1 or xx <= max(1e-20, float(g.gain.var()) * n * 1e-12):
        row["status"] = "NO_GAIN_OR_DF"
    elif y @ y <= max(1e-20, float(g[target].var()) * n * 1e-12):
        row["status"] = "TARGET_ABSORBED"
    else:
        beta = (x @ y) / xx
        score = pd.Series(x * (y - beta * x), index=g.index).groupby(g.user_id).sum()
        correction = clusters / (clusters - 1) * (n - 1) / (n - k - 1)
        se = np.sqrt(correction * (score @ score)) / xx
        sd_y = g[target].std()
        row.update(beta=beta, se=se, lo=beta-1.96*se, hi=beta+1.96*se,
                   p=2*norm.sf(abs(beta/se)) if se > 0 else np.nan,
                   sd_effect=beta*g.gain.std()/sd_y if sd_y > 0 else np.nan,
                   status="OK" if se > 0 else "ZERO_SE")
    TESTS.append(row)


if len(BASE):
    employees = BASE.loc[BASE.candidate].copy()
    for scope in ["pooled"] + ANALYSIS_WAVES:
        g = employees if scope == "pooled" else employees.loc[employees.wave.eq(scope)]
        for model in ["C", "F"]:
            variation(g, scope, "BASE", model)
        variation(g, scope, "BASE", "C", "altcell")
    for y in OUTCOMES:
        for model in ["C", "F"]:
            variation(employees.loc[employees["y_"+y].notna()], "pooled", y, model)
    for model in ["C", "F"]:
        for c in ["age", "college", "path_v2"]:
            association(employees, "pre_"+c, "prior_trait", model)
        for y in OUTCOMES:
            association(employees, "pre_y_"+y, "prior_expectation", model)
            association(employees, "clear_"+y, "clear_response", model)
        # Only current nonowner respondents with dated previous employee status.
        g = BASE.loc[BASE.prior_employee].copy()
        g["current_employee"] = g.candidate.astype(float)
        association(g, "current_employee", "identity_selection", model)
    # Holdings overlap is descriptive; user clustering does not correct common fund shocks.
    for wave in ANALYSIS_WAVES:
        g = employees.loc[employees.wave.eq(wave)]
        if holding is not None and len(g):
            snapshot = pd.Period(HOLD_MONTH[wave], freq="M").end_time.normalize()
            h = holding.loc[holding.date.eq(snapshot) & holding.user_id.isin(g.user_id) & holding.amount.gt(0)]
            h = h.merge(g[["user_id", "capital"]], on="user_id", validate="many_to_one")
            h["weight"] = h.amount / h.capital
            byfund = h.groupby("fund_code").weight.sum() / len(g)
            reach = h.groupby("fund_code").user_id.nunique() / len(g)
            EXPOSURE.append([wave, len(g), len(byfund), byfund.max(),
                             byfund.nlargest(5).sum(), (byfund**2).sum(), reach.max()])
    add("DISTINCT_EMPLOYEES", ["sample", "rows", "users"],
        [["eligible_four_wave", len(employees), employees.user_id.nunique()]])
if TESTS:
    tests = pd.DataFrame(TESTS)
    for _, idx in tests.groupby(["family", "model"]).groups.items():
        adjusted = multipletests(tests.loc[idx, "p"].fillna(1), method="holm")[1]
        tests.loc[idx, "holm"] = np.where(tests.loc[idx, "p"].notna(), adjusted, np.nan)
else:
    tests = pd.DataFrame(columns=["family", "target", "model", "N", "users", "missing",
                                  "beta", "se", "lo", "hi", "p", "holm", "sd_effect", "status"])


# === CELL 10: Compact final report (copy complete REPORT BEGIN to END) ===
add("SETTINGS", ["item", "value"], [
    ["revision", REVISION], ["identity", "nonowner AND (v2 employee OR v3 working)"],
    ["duration", "audit only; no exclusion"], ["main_waves", "2024q3--2025q2; q2 descriptive"],
    ["gain", "passive gain / 10000 yuan; raw holding weights; flags-only NAV"],
    ["models", "C=cell FE; F=C+wave linear/poly portfolio controls+amount"],
    ["cells", "fixed eligible-nonowner wave ranks 3/3/3; alternate 5/3/3 variation only"],
    ["inference", "user CR1; normal CI/p; Holm within family/model; no common-fund correction"],
    ["scope", "28 auxiliary fits maximum; no current expectation effect regression"],
    ["prior", "immediately previous scheduled employee response strictly before shock; no backfill"],
    ["evidence", "online simulated; submit full workflow for backend real-data report"],
])
add("DUPLICATES", ["wave", "raw", "exact_removed", "no_user", "repeat_rows", "conflict_users", "repeat_submit"], DUPLICATES)
add("IDENTITY_ROUTES", ["wave", "route", "N", "v3_missing", "job_nonblank", "wage_nonblank", "conflict"], ROUTING)
add("CODING", ["wave", "Y", "employee_N", "missing", "unknown", "unmapped", "mapped", "gate"], CODING)
add("OPTIONS", ["wave", "target", "option", "label", "N"], OPTIONS)
add("CALENDAR", ["wave", "snapshot", "start", "end", "gate"], CALENDAR)
add("TIME", ["wave", "N", "no_date", "post", "lag_p50", "lag_gt30", "no_seconds", "ambiguous", "s_p10", "s_p50", "s_p90", "lt60", "lt120", "lt180"], TIMING)
add("HOLDINGS", ["wave", "N", "source", "matched", "invalid", "zero", "positive", "unmatched", "shock_cov", "history_cov"], HOLDING_SUMMARY)
add("FUNNEL", ["wave", "stage", "N", "users", "status"], FUNNEL)
add("OUTCOME_SAMPLES", ["wave", "Y", "code", "employee_unique", "nonblank", "unknown", "eligible_nonblank", "eligible_mapped"], Y_COVERAGE)
add("PRIOR_LINK", ["wave", "nonowner_eligible", "employee_eligible", "prior_employee", "current_and_prior"], PRIOR_AUDIT)
add("VARIATION", ["scope", "sample", "model", "cells", "N", "users", "groups", "singletons", "resid_SD", "SS_retained", "top1pct_SS", "max_SS", "resid_df"], VARIATION)
add("WAVE_SS_SHARE", ["model", "wave", "N", "share"], WAVE_SHARE)
add("FUND_OVERLAP", ["wave", "N", "funds", "max_weight_share", "top5_share", "HHI", "max_user_reach"], EXPOSURE)
add("AUXILIARY_TESTS", list(tests.columns), tests.values.tolist())
add("ISSUES", ["issue"], [[s] for s in sorted(set(ISSUES))] or [["none_detected_not_a_causal_validation"]])
ant_print_all(pd.Series(["EMPLOYEE ROUND2 REPORT BEGIN | " + REVISION]), model_method="unique")
for ti, (title, cols, rows) in enumerate(REPORT, 1):
    lines = [f"T{ti:02d} {title} rows={len(rows)}"]
    for li, part in enumerate(textwrap.wrap("columns: " + " | ".join(cols), width=100), 1):
        lines.append(f"T{ti:02d}H{li} " + part)
    for ri, row in enumerate(rows, 1):
        packed = " | ".join(fmt(v) for v in row)
        for li, part in enumerate(textwrap.wrap(packed, width=100, break_long_words=True), 1):
            lines.append(f"T{ti:02d}R{ri:03d}L{li} " + part)
    for start in range(0, len(lines), 25):
        ant_print_all(pd.Series(lines[start:start+25]), model_method="unique")
ant_print_all(pd.Series([f"EMPLOYEE ROUND2 REPORT END | seconds={time.perf_counter()-STARTED:.1f} | issues={len(set(ISSUES))}"]), model_method="unique")


