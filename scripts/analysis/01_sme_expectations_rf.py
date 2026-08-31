# === CELL 1: Imports, env, 精简 log 注册器 (对齐 v7 helper 家族) ===
"""v8 SME expectations regression: reduced-form, AJS-aligned.

Identification: AJS quasi-lottery with 4 traits + portfolio-cell FE (10×5×5)
+ wave FE. Shock window = month-start to earliest submit_date per wave.
Estimation: pooled 5-wave OLS with HC1 SE. No 2SLS.

References:
- docs/Notes_Xiaohan/Notes_Xiaohan.tex (Toy § specification)
- scripts/samples/build_ant_24q3_sme_aer_passive_controls.py (AJS reference impl)
- scripts/samples/tmp_code_2024q2.py (addon merge pattern)
- scripts/20260817_v7/05_panel_and_reg_v3.py (helper 家族: emit/hr/log/pf/nf/ff/fmt_table)
"""
import gc

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from marvel.AntPrint import ant_read_data, ant_print_all, ant_plot
from marvel.AntPrint.sandbox.global_constant import envir, print_envir

print_envir()

# 格式化输出辅助函数 (对齐 v7 line 56-127)
LOGS = []


def emit(lines):
    """平台唯一文本输出通道。接受 str 或 list[str]，自动转 pd.Series + unique。"""
    if isinstance(lines, str):
        lines = [lines]
    ant_print_all(pd.Series(list(lines)), model_method="unique")


def hr(title, sub=None):
    """区块分隔符。"""
    lines = ["", "=" * 74, f"  {title}", "=" * 74]
    if sub is not None:
        ss = sub if isinstance(sub, list) else [sub]
        for s in ss:
            lines.append(f"  {s}")
    emit(lines)


def log(cid, metric, value, scope="-", detail="", fmt=None):
    """登记一条诊断项。"""
    disp = fmt(value) if fmt is not None else str(value)
    LOGS.append({"cid": cid, "scope": scope, "metric": metric,
                 "value": disp, "rule": "-", "verdict": "INFO",
                 "detail": detail})
    return "INFO"


def pf(x, nd=2):
    """percent format."""
    return "-" if x is None else f"{x:.{nd}f}%"


def nf(x):
    """integer format with thousands separator."""
    return "-" if x is None else f"{int(x):,d}"


def ff(x, nd=2, scale=1.0):
    """float format. scale=100 用于 β/se 这种小数, 让 0.0012 → 0.12 易读."""
    if x is None:
        return "-"
    return f"{x * scale:.{nd}f}"


def fmt_table(headers, rows, widths, align=None):
    """monospace 宽对齐表；widths 按列字符宽。"""
    align = align or ["<"] * len(headers)
    def line(cells):
        return "  " + " ".join(
            f"{str(c):{a}{w}s}" for c, w, a in zip(cells, widths, align)
        )
    out = [line(headers), "  " + "-" * (sum(widths) + len(widths) - 1)]
    for r in rows:
        out.append(line(r))
    return out


def render_logs():
    """渲染所有登记的诊断项 (纯 INFO 列表, 按 cid / scope 字典序)."""
    if not LOGS:
        return ["  (无登记的诊断项)"]
    keep = sorted(LOGS, key=lambda c: (c["cid"], c["scope"]))
    rows = [[c["cid"], c["scope"], c["metric"][:30],
             c["value"], c["detail"][:26]] for c in keep]
    lines = [f"共 {len(LOGS)} 项 (纯记录, 不裁决; 阈值/决策交人工审核):", ""]
    lines += fmt_table(
        ["cid", "scope", "指标", "值", "备注"],
        rows, [13, 12, 30, 14, 26],
    )
    return lines


# === CELL 2: Config ===

# ====== USER-PROVIDED TABLES (placeholders — fill before platform run) ======
SHOCK_TABLE = "<USER_FILL_SHOCK_TABLE_NAME>"
"""Fund-level shock table (per production data/shock_panel.csv, 122369 rows × 17 cols, 5 waves).
Expected: FundClassID, wave, window_start, window_end, window_days, shock_n_theory_days,
shock_n_valid_days, shock_complete_ratio, shock_accnav_baseline, shock_accnav_end,
shock_ret_rate, shock_ret_rate_pp, shock_ret_missing, shock_complete, shock_extreme,
shock_usable. Gate flag = shock_usable."""

PORT_CONTROL_TABLE = "<USER_FILL_PORT_CONTROL_TABLE_NAME>"
"""Fund-level 12-month portfolio characteristics (per production data/ctrl_panel.csv, 113654 rows × 9 cols, 5 waves).
Expected: FundClassID, wave, history_start, history_end, ctrl_expected_ret_12m,
ctrl_portfolio_risk_12m, ctrl_n_months_used, ctrl_coverage_in_history, ctrl_mean_TradingDays."""

# ====== STANDARD TABLES ======
PROJECT_ID = "202405290032751511010004"
SURVEY_TEMPLATE = (
    f"frlab_sample_project_{PROJECT_ID}_v2_sme_sp_smesurvey{{wave}}_202512"
)
HOLDING_TABLE = (
    f"frlab_sample_project_{PROJECT_ID}_v2_sme_fund_invest_202512"
)
"""User-fund month-end holding table; source of portfolio_size & weights
for fund→user aggregation (same table as build_ant_24q3_passive_20240901_0917.py
line 16's invest_tbl)."""
ADDON_2024Q2_TABLE = "sme_id3_2024q2_addExpectation"
ADDON_2024Q2_KEY = "submit_id"
ADDON_2024Q2_MACRO_COLS = {
    "macroeconomic_gdp": "exp_gdp",
    "macroeconomic_house": "exp_house",
    "macroeconomic_cpi": "exp_cpi",
    "macroeconomic_rate": "exp_rate",
}

# ====== Column name conventions ======
USER_COL = "匿名化用户id"
FUND_COL_SURVEY = "基金代码"
# FUND_COL_SHOCK: 主键 (FundClassID)。CSV sample 用 "FundClassID"，
# 但平台表可能 rename (e.g. fund_class_id / fund_id)。如果报 ValueError
# 'FundClassID'，把下面改成实际平台表的列名。
FUND_COL_SHOCK = "FundClassID"
WAVE_COL = "wave"

# Fund-level shock table column names (per data/shock_panel.csv)
SHOCK_RET_PP_COL = "shock_ret_rate_pp"        # 100 × R_passive_fund (pp)
SHOCK_COMPLETE_COL = "shock_complete"
SHOCK_MISSING_COL = "shock_ret_missing"
SHOCK_EXTREME_COL = "shock_extreme"
SHOCK_USABLE_COL = "shock_usable"            # final user-curated gate flag
SHOCK_NAVBASE_COL = "shock_accnav_baseline"
SHOCK_NAVEND_COL = "shock_accnav_end"

# Fund-level control table column names (per data/ctrl_panel.csv)
CONTROL_RISK_COL = "ctrl_portfolio_risk_12m"  # σ per fund (12m std)
CONTROL_RET_COL = "ctrl_expected_ret_12m"     # R̄ per fund (12m mean)
CONTROL_COVERAGE_COL = "ctrl_coverage_in_history"

# Holding table column names
HOLDING_AMT_COL = "当月月底日持有金额元"
HOLDING_DATE_COL = "日期"

# ====== Wave format normalization ======
# Sample fund-level tables use '24Q3' (uppercase, no '20'); survey uses '2024q3'.
WAVE_IN_FUND = {
    "24Q2": "2024q2", "24Q3": "2024q3", "24Q4": "2024q4",
    "25Q1": "2025q1", "25Q2": "2025q2",
}

# Holding month-end per wave (= last day of month preceding shock window start)
# 24Q2: shock Jun 1-12  → May 31 holding
# 24Q3: shock Sep 1-17 → Aug 31 holding
# 24Q4: shock Dec 1-10 → Nov 30 holding
# 25Q1: shock Mar 1-17  → Feb 28/29 holding
# 25Q2: shock Jun 1-12  → May 31 holding
WAVE_HOLDING_MONTH = {
    "2024q2": pd.Period("2024-05", freq="M"),
    "2024q3": pd.Period("2024-08", freq="M"),
    "2024q4": pd.Period("2024-11", freq="M"),
    "2025q1": pd.Period("2025-02", freq="M"),
    "2025q2": pd.Period("2025-05", freq="M"),
}

# ====== WAVES ======
WAVES = ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"]

# ====== 11 Y_VARS (11 expectations outcomes) ======
Y_MACRO_4W = ["exp_stock"]                                  # 4-wave (no 2024q2)
Y_MACRO_5W = ["exp_gdp", "exp_cpi", "exp_house", "exp_rate"]  # 5-wave (2024q2 via addon)
Y_ALL_5W = [                                                 # 5-wave (主表 employer段)
    "exp_env_local", "exp_rev", "exp_market",
    "exp_price", "exp_wage", "exp_input_cost",
]
Y_VARS = Y_MACRO_4W + Y_MACRO_5W + Y_ALL_5W  # 11 total

# ====== exp_* v-code per wave (主表; 2024q2 macro 走 addon) ======
# 来源：samples/build_ant_24q3_sme_aer_passive_controls.py + memory/sme-survey-y-vcode-reference
EXP_VCODES = {
    "exp_stock":      {"2024q3": "v196", "2024q4": "v187", "2025q1": "v181", "2025q2": "v190"},
    "exp_gdp":        {"2024q3": "v192", "2024q4": "v182", "2025q1": "v176", "2025q2": "v185"},
    "exp_cpi":        {"2024q3": "v195", "2024q4": "v186", "2025q1": "v180", "2025q2": "v189"},
    "exp_house":      {"2024q3": "v193", "2024q4": "v184", "2025q1": "v178", "2025q2": "v187"},
    "exp_rate":       {"2024q3": "v194", "2024q4": "v185", "2025q1": "v179", "2025q2": "v188"},
    "exp_env_local":  {"2024q2": "v203", "2024q3": "v212", "2024q4": "v203", "2025q1": "v198", "2025q2": "v206"},
    "exp_rev":        {"2024q2": "v104", "2024q3": "v107", "2024q4": "v93",  "2025q1": "v94",  "2025q2": "v107"},
    "exp_market":     {"2024q2": "v103", "2024q3": "v106", "2024q4": "v92",  "2025q1": "v93",  "2025q2": "v106"},
    "exp_price":      {"2024q2": "v176", "2024q3": "v189", "2024q4": "v179", "2025q1": "v173", "2025q2": "v182"},
    "exp_wage":       {"2024q2": "v177", "2024q3": "v190", "2024q4": "v180", "2025q1": "v174", "2025q2": "v183"},
    "exp_input_cost": {"2024q2": "v178", "2024q3": "v191", "2024q4": "v181", "2025q1": "v175", "2025q2": "v184"},
}

# ====== 4 traits v-code per wave ======
# 来源：data/小微调研变量映射表.xlsx (5 sheets 提取, employer段)
# 2024q3 v166/v40/v41 与 samples/build_ant_24q3_sme_aer_passive_controls.py 一致 ✓
TRAIT_VCODES = {
    "education":    {"2024q2": "v163", "2024q3": "v166", "2024q4": "v168", "2025q1": "v163", "2025q2": "v174"},
    "firm_year":    {"2024q2": "v32",  "2024q3": "v40", "2024q4": "v26",  "2025q1": "v27",  "2025q2": "v27"},
    "registration": {"2024q2": "v33",  "2024q3": "v41",  "2024q4": "v27",  "2025q1": "v28",  "2025q2": "v28"},
}

# Reference year for firm_age (= survey year, per build script line 220)
TRAIT_REFERENCE_YEAR = {
    "2024q2": 2024, "2024q3": 2024, "2024q4": 2025,
    "2025q1": 2025, "2025q2": 2025,
}

# ====== Derived trait column names (post-construction) ======
TRAIT_AGE = "aer_bal_age"
TRAIT_COLLEGE = "aer_bal_college"
TRAIT_FIRM_AGE = "aer_bal_firm_age"
TRAIT_COMPANY = "aer_bal_company"
TRAIT_NAMES = [TRAIT_AGE, TRAIT_COLLEGE, TRAIT_FIRM_AGE, TRAIT_COMPANY]

# ====== exp_* mapping dictionaries (v7-style PCT/INDEX/DIRECTION 三层) ======
# 来源：scripts/20260817_v7/05_panel_and_reg_v3.py line 240-286
PCT_DICT = {
    # v8 CHANGE-style (营收 / 市场份额)
    "基本不变": 0, "增长20_以上": 25, "增长20_以内": 10,
    "降低20_以上": -25, "降低20_以内": -10, "增长10_以上": 15,
    "增长10_以内": 5, "降低10_以上": -15, "降低10_以内": -5,
    # v8 GDP-style (GDP / CPI / 利率)
    "下降3_以上": -4.0, "下降0_3": -1.5,
    "增长0_3": 1.5, "增长3_4": 3.5, "增长4_5": 4.5,
    "增长5_6": 5.5, "增长6_8": 7.0, "增长8_以上": 9.0,
    "下降0_1": -0.5, "下降1_2": -1.5, "下降2_3": -2.5,
    "下降3_5": -4.0, "下降5_以上": -6.0, "降低5_以上": -6.0,
    "增长0_1": 0.5, "增长1_2": 1.5, "增长2_3": 2.5,
    "增长3_以上": 4.0, "上涨3_5": 4.0,
    # v8 PRICE-style (价格 / 工资 / 投入品)
    "上涨3_以内": 2.0, "上涨5_以上": 6.0, "上涨5_以内": 4.0,
    "降低3_以内": -2.0, "降低3_5": -4.0,
    # v8 HPRICE-style (房价；v7 涨幅 30+ → 35，跌幅 30+ → -35)
    "上升0_5": 2.5, "上升5_10": 7.5, "上升10_15": 12.5,
    "上升15_30": 22.5, "上升30_以上": 35.0,
    "下降0_5": -2.5, "下降5_10": -7.5, "下降10_15": -12.5,
    "下降15_30": -22.5, "下降30_以上": -35.0,
    # NA markers
    "不清楚": None, "不确定": None, "不适用": None, "关心但拿不准": None,
    "没有明显变化": 0, "不适用_去年尚未工作": None,
    '0_1': 0.5,
    '1_2': 1.5,
    '2_3': 2.5,
    '3_4': 3.5,
    '4_5': 4.5,
    '5_以上': 6.0,
}

INDEX_DICT = {
    # exp_stock 点位（v7 含 3600_3800 / 3800_4000 / 4000点以上 细分）
    "2200点以下": 2000.0, "2600点以下": 2400.0,
    "2200_2400点": 2300.0, "2400_2600点": 2500.0,
    "2600_2800点": 2700.0, "2800_3000点": 2900.0,
    "3000_3300点": 3150.0, "3300_3600点": 3450.0,
    "3600_3800点": 3700.0, "3800_4000点": 3900.0,
    "3600点以上": 3800.0, "4000点以上": 4200.0,
    "不确定": None, "不适用": None,
}

DIRECTION_DICT = {
    # exp_env_local 经营景气方向（v7）
    "好转": 1, "不变": 0, "恶化": -1,
    "预期变差": -1, "预期不变": 0, "预期好转": 1,
    "不清楚": None, "不确定": None, "不适用": None,
}

EXP_MAPPING = {
    "exp_stock":       INDEX_DICT,
    "exp_gdp":         PCT_DICT,
    "exp_cpi":         PCT_DICT,
    "exp_house":       PCT_DICT,
    "exp_rate":        PCT_DICT,
    "exp_market":      PCT_DICT,
    "exp_price":       PCT_DICT,
    "exp_wage":        PCT_DICT,
    "exp_input_cost":  PCT_DICT,
    "exp_rev":         PCT_DICT,
    "exp_env_local":   DIRECTION_DICT,
}

STOCK_INITIAL_LEVEL = 2748.92  # baseline for exp_stock percent conversion

# ====== Trait answer mappings ======
COLLEGE_ANSWERS = [
    "大学专科_专科_高职高专_技师学院", "大学本科", "研究生及以上",
]
NONCOLLEGE_ANSWERS = [
    "小学及以下", "初中",
    "高中_普通高中_成人高中_职业高中_中专_技校",
]
COMPANY_ANSWERS = [
    "公司制企业_工商注册的企业", "公司制企业（工商注册的企业）",
]
ESTYEAR_OVERRIDE = {"2015之前": "2013"}

# ====== Cell bins (10 size × 5 risk × 5 expected return) ======
N_SIZE_BIN = 10
N_RISK_BIN = 5
N_ERET_BIN = 5
CELL_PREFIX = "analysis"

# ====== Sample filters ======
# MIN_HOLDING_COVERAGE: 真实数据用 0.999999 (学长口径，effectively 100% 覆盖)；
# sim 数据放宽到 0.8 以容忍部分 fund 缺值。
MIN_HOLDING_COVERAGE = 0.8
ANSWER_SECONDS_MIN = 180

# ====== Regression ======
SE_TYPE = "HC1"
PASSIVE_RET_PREDICTOR = "X100_R_passive"  # 100 × R_passive (pp)
WAVE_FE_NAME = "wave"
CELL_FE_NAME = "analysis_portfolio_cell"


# === CELL 3: Helpers ===
# --- text / numeric utilities (from build script) ---

def clean_text(series):
    """Normalize text: strip + map empty/NA-like to pd.NA."""
    return (
        series.astype("string")
        .str.strip()
        .replace({
            "": pd.NA, "NAN": pd.NA, "NaN": pd.NA, "nan": pd.NA,
            "None": pd.NA, "NULL": pd.NA, "<NA>": pd.NA,
        })
    )


def safe_ratio(num, denom):
    return np.where(denom > 0, num / denom, np.nan)


# --- answer_seconds extraction from extro_info (from build script line 145-156) ---

def extract_answer_seconds(svy):
    """Parse `answerSeconds=` from semistructured extro_info; keep last match.

    Wave-conditional: some waves (e.g. 2025q2 per data/addon/_schema.json)
    lack `extro_info` column. In that case, all answer_seconds are NA → the
    funnel filter 'answer_seconds.isna() | .ge(180)' keeps all rows.
    """
    svy["answer_seconds_n_matches"] = 0
    svy["answer_seconds"] = pd.NA
    if "extro_info" not in svy.columns:
        svy["answer_seconds_short"] = 0
        return svy
    matches = (
        svy["extro_info"].astype("string")
        .str.findall(r"(?:^|;)answerSeconds\s*=\s*([0-9]+(?:\.[0-9]+)?)(?=;|$)")
    )
    svy["answer_seconds_n_matches"] = matches.str.len()
    svy["answer_seconds"] = pd.to_numeric(
        matches.str[-1], errors="coerce"
    )
    svy["answer_seconds_short"] = (
        svy["answer_seconds"].notna() & svy["answer_seconds"].lt(ANSWER_SECONDS_MIN)
    ).astype(int)
    return svy


# --- sme_owner from v1 (from build script line 181-187) ---

def construct_sme_owner(svy):
    """v1 == '我是小微经营者_我自愿参与本次调查' → 1, else 0."""
    owner_answer = clean_text(svy["v1"])
    svy["sme_owner"] = (
        owner_answer.eq("我是小微经营者_我自愿参与本次调查").fillna(False).astype(int)
    )
    return svy


# --- trait construction (4 traits, per-wave v-codes + answer mappings) ---

def construct_traits(svy, wave):
    """Build aer_bal_age / aer_bal_college / aer_bal_firm_age / aer_bal_company.

    Sources (per wave, from data/小微调研变量映射表.xlsx employer段):
      age    = pd.to_numeric(user_age)
      college = 1 if education_text ∈ COLLEGE_ANSWERS, 0 if ∈ NONCOLLEGE_ANSWERS, else NA
      firm_age = TRAIT_REFERENCE_YEAR[wave] - numeric(firm_year_text)
      company = 1 if registration_text ∈ COMPANY_ANSWERS, else NA
    """
    # 1) age (numeric, field name stable across waves but may be absent in some)
    svy[TRAIT_AGE] = (
        pd.to_numeric(svy["user_age"], errors="coerce")
        if "user_age" in svy.columns else pd.NA
    )

    # 2) college (binary from categorical education)
    edu_v = TRAIT_VCODES["education"][wave]
    edu_text = clean_text(svy[edu_v])
    svy[TRAIT_COLLEGE] = np.nan
    svy.loc[edu_text.isin(NONCOLLEGE_ANSWERS), TRAIT_COLLEGE] = 0
    svy.loc[edu_text.isin(COLLEGE_ANSWERS), TRAIT_COLLEGE] = 1

    # 3) firm_age (years since business started)
    firm_v = TRAIT_VCODES["firm_year"][wave]
    firm_text = clean_text(svy[firm_v])
    firm_text = firm_text.replace(ESTYEAR_OVERRIDE)
    firm_numeric = pd.to_numeric(firm_text, errors="coerce")
    svy[TRAIT_FIRM_AGE] = TRAIT_REFERENCE_YEAR[wave] - firm_numeric

    # 4) company (binary from categorical registration)
    reg_v = TRAIT_VCODES["registration"][wave]
    reg_text = clean_text(svy[reg_v])
    svy[TRAIT_COMPANY] = np.nan
    svy.loc[reg_text.notna(), TRAIT_COMPANY] = (
        reg_text[reg_text.notna()].isin(COMPANY_ANSWERS).astype(int)
    )

    return svy


# --- exp_* numeric mapping from per-wave v-code (主表 only) ---

def map_exp_columns(svy, wave):
    """Apply text→numeric mappings for 主表 exp_* columns via v7-style
    EXP_MAPPING[Y → {PCT|INDEX|DIRECTION}_DICT].

    exp_stock: only in 2024q3-2025q2 (主表 v196/v187/v181/v190) → INDEX_DICT + percent conversion
    exp_gdp/cpi/house/rate: 2024q2 走 addon; 2024q3-2025q2 走主表 v-code → PCT_DICT
    exp_env_local + 5 business: 5-wave (主表 employer段) → PCT_DICT or DIRECTION_DICT
    """
    # All 11 Y in 主表 for non-2024q2 waves
    y_to_map_main = list(Y_MACRO_5W) + list(Y_ALL_5W)
    if wave != "2024q2":
        y_to_map_main = ["exp_stock"] + y_to_map_main
    for y_name in y_to_map_main:
        v_code = EXP_VCODES[y_name].get(wave)
        if v_code is None or v_code not in svy.columns:
            continue
        mapping = EXP_MAPPING.get(y_name)
        if mapping is None:
            continue
        if y_name == "exp_stock":
            level = clean_text(svy[v_code]).map(mapping)
            svy[y_name] = 100 * level / STOCK_INITIAL_LEVEL
        else:
            svy[y_name] = clean_text(svy[v_code]).map(mapping)
    return svy


# --- 2024q2 addon merge ---

def merge_2024q2_addon(svy, addon):
    """For 2024q2: merge addon on submit_id, rename macroeconomic_* → exp_*.

    Coerces submit_id to string on both sides before merge to prevent silent
    0-match when platform returns int64 in survey and string in addon (or
    vice versa). After merge, emits row counts + match rate for diagnostic.
    """
    keep_cols = [ADDON_2024Q2_KEY] + list(ADDON_2024Q2_MACRO_COLS.keys())
    addon_keep = addon[keep_cols].drop_duplicates(ADDON_2024Q2_KEY).copy()
    # Force string dtype on submit_id (defensive against platform dtype drift)
    svy.loc[:, ADDON_2024Q2_KEY] = svy[ADDON_2024Q2_KEY].astype("string")
    addon_keep.loc[:, ADDON_2024Q2_KEY] = (
        addon_keep[ADDON_2024Q2_KEY].astype("string")
    )
    svy = svy.merge(addon_keep, on=ADDON_2024Q2_KEY, validate="many_to_one", how="left")
    for addon_col, exp_name in ADDON_2024Q2_MACRO_COLS.items():
        svy[exp_name] = pd.to_numeric(svy[addon_col], errors="coerce")
    n_merged = len(svy)
    n_gdp_present = int(svy["macroeconomic_gdp"].notna().sum())
    n_gdp_missing = int(svy["macroeconomic_gdp"].isna().sum())
    emit([
        f" [diag addon merge] n_merged_rows={nf(n_merged)}  "
        f"n_macro_gdp_present={nf(n_gdp_present)}  "
        f"n_macro_gdp_missing={nf(n_gdp_missing)}"
    ])
    return svy


# --- wave format normalization (fund-level tables use '24Q3', survey uses '2024q3') ---

def normalize_wave(series):
    """Map '24Q3' → '2024q3'. Leave already-normalized values unchanged."""
    out = series.astype("string").str.strip()
    return out.map(lambda v: WAVE_IN_FUND.get(v, v))


# --- user-fund holding prep (from build_ant_24q3_passive_20240901_0917.py line 32-50) ---

def prep_holding(invest):
    """Add month_p from holding 日期 field; normalize fund codes; rename
    user_id → 匿名化用户id if needed (行为表 in production has 匿名化用户id,
    but sim may use survey-side user_id).
    Mutates invest in place. Drops rows with missing date/fund.
    """
    # Per data/data_notes.md §3.2: 行为表主键=匿名化用户id; 但 sim 可能用 user_id
    if USER_COL not in invest.columns and "user_id" in invest.columns:
        invest = invest.rename(columns={"user_id": USER_COL})
    raw_date = invest[HOLDING_DATE_COL].astype("string")
    date_str8 = raw_date.str.extract(r"(\d{8})$")[0]
    invest["date_dt"] = pd.to_datetime(
        date_str8, format="%Y%m%d", errors="coerce"
    )
    invest["month_p"] = invest["date_dt"].dt.to_period("M")
    invest[HOLDING_AMT_COL] = pd.to_numeric(
        invest[HOLDING_AMT_COL], errors="coerce"
    )
    invest[USER_COL] = invest[USER_COL].astype("string").str.strip()
    invest[FUND_COL_SURVEY] = (
        invest[FUND_COL_SURVEY].astype("string").str.strip().str.upper()
        .str.replace(r"\.0$", "", regex=True)
    )
    numeric_code = invest[FUND_COL_SURVEY].str.fullmatch(r"\d+", na=False)
    invest.loc[numeric_code, FUND_COL_SURVEY] = (
        invest.loc[numeric_code, FUND_COL_SURVEY].str.zfill(6)
    )
    return invest


# --- fund→user shock aggregation (from build_ant_24q3_passive_20240901_0917.py line 144-247) ---

def aggregate_shock_to_user(shock_fund, holding, wave):
    """For given wave: aggregate fund-level shock to user-level X100_R_passive.

    Returns df with cols: 匿名化用户id, portfolio_size, X100_R_passive,
    passive_complete (1 if user's matched_holding / portfolio_size ≥ MIN threshold).
    """
    month_p = WAVE_HOLDING_MONTH[wave]
    # Filter holding to wave's month-end, then collapse (user, fund)
    h_wave = holding.loc[
        holding["month_p"].eq(month_p),
        [USER_COL, FUND_COL_SURVEY, HOLDING_AMT_COL],
    ].copy()
    h_wave = (
        h_wave.groupby([USER_COL, FUND_COL_SURVEY], as_index=False)
        [HOLDING_AMT_COL].sum(min_count=1)
        .rename(columns={HOLDING_AMT_COL: "holding_amt_raw"})
    )
    # Filter shock to this wave; dedup (wave, fund); numeric coercion
    s_cols = [
        FUND_COL_SHOCK, SHOCK_RET_PP_COL, SHOCK_USABLE_COL,
    ]
    s_wave = (
        shock_fund.loc[shock_fund[WAVE_COL].eq(wave), s_cols]
        .drop_duplicates(FUND_COL_SHOCK).copy()
    )
    s_wave[SHOCK_RET_PP_COL] = pd.to_numeric(
        s_wave[SHOCK_RET_PP_COL], errors="coerce"
    )
    # Match holding → shock (fund-level); many holdings per fund
    matched = h_wave.merge(
        s_wave,
        left_on=FUND_COL_SURVEY,
        right_on=FUND_COL_SHOCK,
        how="left",
        validate="many_to_one",
    )
    matched["holding_clean"] = matched["holding_amt_raw"].where(
        matched["holding_amt_raw"].ge(0)
    )
    # Use SHOCK_USABLE_COL (user-pre-curated final flag) to gate return
    matched["usable"] = matched[SHOCK_USABLE_COL].eq(1)
    matched["matched_holding"] = np.where(
        matched["usable"], matched["holding_clean"], 0
    )
    matched["weighted_pp"] = (
        matched["holding_clean"]
        * matched[SHOCK_RET_PP_COL].where(matched["usable"])
    )
    # Aggregate to user
    user = matched.groupby(USER_COL, as_index=False).agg(
        portfolio_size=("holding_clean", lambda x: x.sum(min_count=1)),
        matched_holding=("matched_holding", "sum"),
        weighted_pp=("weighted_pp", lambda x: x.sum(min_count=1)),
    )
    del matched  # OOM: release (user × fund) intermediate df
    user["X100_R_passive"] = np.where(
        user["portfolio_size"] > 0,
        user["weighted_pp"] / user["portfolio_size"],
        np.nan,
    )
    user["return_coverage"] = np.where(
        user["portfolio_size"] > 0,
        user["matched_holding"] / user["portfolio_size"],
        np.nan,
    )
    user["passive_complete"] = (
        user["return_coverage"].ge(MIN_HOLDING_COVERAGE)
        & user["portfolio_size"].gt(0)
        & user["X100_R_passive"].notna()
    ).astype(int)
    return user[[USER_COL, "portfolio_size", "X100_R_passive", "passive_complete"]]


# --- fund→user portfolio control aggregation ---

def aggregate_control_to_user(port_fund, holding, wave):
    """For given wave: aggregate fund-level σ / R̄ / coverage to user-level
    via holding weights.

    Returns df with cols: 匿名化用户id, portfolio_risk_12m, expected_ret_12m,
    controls_complete (1 if weighted coverage ≥ MIN threshold).
    """
    month_p = WAVE_HOLDING_MONTH[wave]
    h_wave = holding.loc[
        holding["month_p"].eq(month_p),
        [USER_COL, FUND_COL_SURVEY, HOLDING_AMT_COL],
    ].copy()
    h_wave = (
        h_wave.groupby([USER_COL, FUND_COL_SURVEY], as_index=False)
        [HOLDING_AMT_COL].sum(min_count=1)
        .rename(columns={HOLDING_AMT_COL: "holding_amt_raw"})
    )
    h_wave["holding_clean"] = h_wave["holding_amt_raw"].where(
        h_wave["holding_amt_raw"].ge(0)
    )
    p_cols = [
        FUND_COL_SHOCK, CONTROL_RISK_COL, CONTROL_RET_COL, CONTROL_COVERAGE_COL,
    ]
    p_wave = (
        port_fund.loc[port_fund[WAVE_COL].eq(wave), p_cols]
        .drop_duplicates(FUND_COL_SHOCK).copy()
    )
    p_wave[CONTROL_RISK_COL] = pd.to_numeric(p_wave[CONTROL_RISK_COL], errors="coerce")
    p_wave[CONTROL_RET_COL] = pd.to_numeric(p_wave[CONTROL_RET_COL], errors="coerce")
    p_wave[CONTROL_COVERAGE_COL] = pd.to_numeric(
        p_wave[CONTROL_COVERAGE_COL], errors="coerce"
    )
    matched = h_wave.merge(
        p_wave,
        left_on=FUND_COL_SURVEY,
        right_on=FUND_COL_SHOCK,
        how="left",
        validate="many_to_one",
    )
    # weight per (user, fund): holding_i / Σ holding
    user_totals = matched.groupby(USER_COL)["holding_clean"].transform("sum")
    matched["weight"] = np.where(
        user_totals > 0,
        matched["holding_clean"] / user_totals,
        np.nan,
    )
    matched["w_risk"] = matched["weight"] * matched[CONTROL_RISK_COL]
    matched["w_ret"] = matched["weight"] * matched[CONTROL_RET_COL]
    matched["w_cov"] = matched["weight"] * matched[CONTROL_COVERAGE_COL]
    user = matched.groupby(USER_COL, as_index=False).agg(
        portfolio_risk_12m=("w_risk", lambda x: x.sum(min_count=1)),
        expected_ret_12m=("w_ret", lambda x: x.sum(min_count=1)),
        coverage_w=("w_cov", lambda x: x.sum(min_count=1)),
    )
    del matched  # OOM: release (user × fund) intermediate df
    user["controls_complete"] = user["coverage_w"].ge(MIN_HOLDING_COVERAGE).astype(int)
    return user[[USER_COL, "portfolio_risk_12m", "expected_ret_12m", "controls_complete"]]


# --- portfolio cell construction (from build script line 111-129) ---

def add_rank_bin(df, value_col, n_bins, out_col):
    """Within-sample percentile rank × ceil + clip(1, n_bins) → discrete bin."""
    pct_rank = df[value_col].rank(method="first", pct=True)
    df[out_col] = (
        np.ceil(pct_rank * n_bins).clip(1, n_bins).astype("Int64")
    )
    return df


def make_cell_id(df, prefix):
    return (
        df[f"{prefix}_size_bin"].astype("string")
        + "_"
        + df[f"{prefix}_risk_bin"].astype("string")
        + "_"
        + df[f"{prefix}_eret_bin"].astype("string")
    )


def build_cells(df):
    """Construct 10×5×5 portfolio-cell FE (analysis_portfolio_cell)."""
    df = df.copy()
    df = add_rank_bin(df, "portfolio_size", N_SIZE_BIN, f"{CELL_PREFIX}_size_bin")
    df = add_rank_bin(df, "portfolio_risk_12m", N_RISK_BIN, f"{CELL_PREFIX}_risk_bin")
    df = add_rank_bin(df, "expected_ret_12m", N_ERET_BIN, f"{CELL_PREFIX}_eret_bin")
    df[CELL_FE_NAME] = make_cell_id(df, CELL_PREFIX)
    return df


# --- reduced-form regression (对齐 v7 run_reduced_form pattern) ---

def run_rf(df_reg, y_var):
    """Pooled RF: Y ~ X100_R_passive + C(wave) + C(cell) + 4 traits, HC1 SE.

    Per v7 line 568-602: explicit df_run dict construction + numeric coerce +
    inf→NaN + dropna + sample-size guard. Returns dict {beta, se, t, p, n, R2}
    or None if n < MIN_REG_N.
    """
    # 1) construct df_run with explicit dict (avoids Patsy column issues)
    trait_str = " + ".join(TRAIT_NAMES)
    fe_cols = [WAVE_FE_NAME, CELL_FE_NAME] if CELL_FE_NAME in df_reg.columns else [WAVE_FE_NAME]
    num_cols = [y_var, PASSIVE_RET_PREDICTOR] + TRAIT_NAMES
    fe_str = " + ".join([f"C({c})" for c in fe_cols])

    d = {
        y_var:               df_reg[y_var].values,
        PASSIVE_RET_PREDICTOR: df_reg[PASSIVE_RET_PREDICTOR].values,
        WAVE_FE_NAME:        df_reg[WAVE_FE_NAME].astype("string").values,
    }
    if CELL_FE_NAME in df_reg.columns:
        d[CELL_FE_NAME] = df_reg[CELL_FE_NAME].astype("string").values
    for t in TRAIT_NAMES:
        d[t] = df_reg[t].values
    df_run = pd.DataFrame(d)

    # 2) numeric coercion for all numeric cols (per v7 line 582-584)
    for c in [y_var, PASSIVE_RET_PREDICTOR] + TRAIT_NAMES:
        df_run[c] = pd.to_numeric(df_run[c], errors="coerce")
    # 3) inf → NaN → dropna (per v7 line 585)
    df_run = df_run.replace([np.inf, -np.inf], np.nan).dropna()
    n_pre = len(df_run)
    if n_pre < 30:
        return None

    # 4) FE singleton pre-check (defensive: 1 unique level → drop that FE
    # to avoid np.maximum zero-array error)
    used_fe_cols = []
    for c in [WAVE_FE_NAME, CELL_FE_NAME]:
        if c in df_run.columns:
            n_unique = df_run[c].nunique(dropna=True)
            if n_unique >= 2:
                used_fe_cols.append(c)
    if not used_fe_cols:
        return None
    fe_str = " + ".join([f"C({c})" for c in used_fe_cols])

    # 5) formula + OLS fit
    formula = (
        f"{y_var} ~ {PASSIVE_RET_PREDICTOR} + "
        f"{fe_str} + {trait_str}"
    )
    model = smf.ols(formula, data=df_run).fit(cov_type=SE_TYPE)
    return {
        "beta": float(model.params.get(PASSIVE_RET_PREDICTOR, np.nan)),
        "se":   float(model.bse.get(PASSIVE_RET_PREDICTOR, np.nan)),
        "t":    float(model.tvalues.get(PASSIVE_RET_PREDICTOR, np.nan)),
        "p":    float(model.pvalues.get(PASSIVE_RET_PREDICTOR, np.nan)),
        "n":    int(model.nobs),
        "R2":   float(model.rsquared),
    }


# --- winsorize decision helper (from v7 line 606-640) ---

def winsorize_decision(arr):
    """判断 arr 是否需要 winsorize, 返回 (arr_after, note).

    三层判定 (用户 2026-08-20 要求):
      1. 样本 < 200 → 不缩尾 (太少无法判定)
      2. n_unique ≤ 30 或 n_unique/n < 0.01 → 离散分布, 不缩尾
      3. 连续分布但尾部 < 5×IQR → 分布紧凑, 不缩尾
      4. 上述都不满足 → winsorize 到 [p0.5, p99.5]
    """
    arr = np.asarray(arr, dtype=float)
    arr = arr[np.isfinite(arr)]
    n = len(arr)
    if n < 200:
        return arr, f"未缩尾 (n={n}<200)"

    n_unique = int(len(np.unique(arr)))
    if n_unique <= 30 or (n_unique / n) < 0.01:
        return arr, f"未缩尾 (离散: n_unique={n_unique})"

    p_lo, p_hi = np.percentile(arr, [0.5, 99.5])
    p1, p99 = np.percentile(arr, [1, 99])
    p25, p75 = np.percentile(arr, [25, 75])
    iqr = p75 - p25
    if iqr <= 0:
        return arr, "未缩尾 (IQR=0)"

    right_tail = (p_hi - p75) / iqr
    left_tail = (p25 - p_lo) / iqr
    if right_tail <= 5 and left_tail <= 5:
        return arr, f"未缩尾 (尾部紧: R={right_tail:.1f} L={left_tail:.1f}×IQR)"

    n_drop = int(((arr < p_lo) | (arr > p_hi)).sum())
    return (
        arr[(arr >= p_lo) & (arr <= p_hi)],
        f"winsorize [{p_lo:.4f},{p_hi:.4f}] drop={n_drop} "
        f"(R={right_tail:.1f} L={left_tail:.1f}×IQR)",
    )


# === CELL 4: Read sources + addon match-rate verify ===
hr("CELL 4: 读源表",
   "5 wave survey (rename user_id → 匿名化用户id) + 2024q2 addon + SHOCK/PORT_CONTROL/HOLDING")

def get_survey_cols(wave):
    """Build the column list needed for v8 from raw survey (per wave).

    Per data/CLAUDE.md §3.2 + data/data_notes.md line 133-138: **所有问卷表
    (`*survey*`) 主键都是 `user_id`，没有 `匿名化用户id`**（行为表才有）。
    读完后由 reading loop 做 `rename(user_id → 匿名化用户id)`。

    Wave-specific column availability (verified via data/addon/_schema.json
    for 2025q2 + samples/tmp_code_2024q2.py for 2024q2 + v7 build script
    for 2024q3):

      - All waves: user_id / submit_id / submit_date / v1 (assumed)
      - 2025q2 confirmed via _schema.json: also has user_age; lacks extro_info / index
      - 2024q2 confirmed via tmp_code_2024q2.py: also has index
      - 2024q3 confirmed via build script: also has extro_info
      - 2024q4 / 2025q1: not confirmed; best-effort inclusion of extro_info/user_age

    Optional cols (extro_info, user_age) are read best-effort; downstream
    helpers guard with column existence check.
    """
    cols = [
        "user_id", "submit_id", "submit_date", "v1",
    ]
    # extro_info: best-effort (build script extracts answerSeconds for 2024q3;
    # absence → all answer_seconds NA → funnel filter '>=180 OR NA' keeps all)
    cols.append("extro_info")
    # user_age: best-effort (2025q2 confirmed; may be missing in older waves)
    cols.append("user_age")
    # index: only present in 2024q2 (used for addon match verification)
    if wave == "2024q2":
        cols.append("index")
    # v-codes per Y (主表 only; 2024q2 macro Y 走 addon merge).
    # 包含 exp_stock (4-wave, 2024q2 缺) — 必须读 v-code 才能在 map_exp_columns
    # 创建 exp_stock 列，否则 CELL 6 回归 KeyError。
    for y in Y_VARS:
        v = EXP_VCODES[y].get(wave)
        if v:
            cols.append(v)
    # v-codes per trait (3 fields per wave)
    for t in ["education", "firm_year", "registration"]:
        v = TRAIT_VCODES[t].get(wave)
        if v:
            cols.append(v)
    return cols


# --- read all 5 wave surveys ---
# Per data/data_notes.md §3.2: 所有问卷表主键是 user_id (无 匿名化用户id)。
# v7 模式：读完后 rename(user_id → 匿名化用户id)，下游用统一 UID。
surveys = {}
for wave in WAVES:
    tbl = SURVEY_TEMPLATE.format(wave=wave)
    svy = ant_read_data(tbl, cols=get_survey_cols(wave)).copy()
    # v7 line 317-318: rename user_id → 匿名化用户id
    if "user_id" in svy.columns and USER_COL not in svy.columns:
        svy = svy.rename(columns={"user_id": USER_COL})
    svy[USER_COL] = svy[USER_COL].astype("string").str.strip()
    svy["wave"] = wave
    surveys[wave] = svy
    emit([f" [读表] survey {wave}  shape={svy.shape}, n_user_id={svy[USER_COL].notna().sum()}"])

# --- read 2024q2 addon (sme_id3_2024q2_addExpectation) ---
addon_2024q2 = ant_read_data(
    ADDON_2024Q2_TABLE,
    cols=["submit_id", "index"] + list(ADDON_2024Q2_MACRO_COLS.keys()),
).copy()
emit([f" [读表] addon 2024q2  shape={addon_2024q2.shape}, n_submit_id={addon_2024q2['submit_id'].notna().sum()}"])

# --- addon match-rate verify (from samples/tmp_code_2024q2.py) ---
# Only 2024q2 survey has the `index` column used by the addon for join.
if "index" in surveys["2024q2"].columns:
    svy_24q2 = surveys["2024q2"].sort_values("index").reset_index(drop=True)
    svy_24q2["index"] = range(1, len(svy_24q2) + 1)
    addon_idx_map = (
        addon_2024q2.drop_duplicates("index").set_index("index")["submit_id"]
    )
    svy_24q2["submit_id_check"] = svy_24q2["index"].map(addon_idx_map)
    svy_24q2["submit_id_match"] = (
        svy_24q2["submit_id"].astype("string")
        == svy_24q2["submit_id_check"].astype("string")
    ).astype(int)
    n_obs = int(svy_24q2["submit_id_match"].notna().sum())
    match_rate = float(svy_24q2["submit_id_match"].mean())
    emit([f" [addon verify] submit_id match (2024q2 survey ↔ addon)  "
          f"n_obs={nf(n_obs)}  match_rate={pf(match_rate, nd=3)}"])
else:
    emit([f" [addon verify] 2024q2 survey missing 'index' column — skipped"])

# --- read user-provided fund-level SHOCK_TABLE + PORT_CONTROL_TABLE ---
# Both at fund level (FundClassID key); wave format normalized '24Q3' → '2024q3'.
# OOM safety: explicit cols= to avoid pulling platform-side extra columns.
# Schema probe first: read full table to dump actual column names (helps if
# platform renames columns vs CSV sample, e.g. fund_class_id vs FundClassID).
shock_probe = ant_read_data(SHOCK_TABLE).copy()
emit([f" [shock schema probe] cols in platform table: {list(shock_probe.columns)}"])
del shock_probe
gc.collect()

SHOCK_READ_COLS = [
    FUND_COL_SHOCK, WAVE_COL, SHOCK_RET_PP_COL, SHOCK_USABLE_COL,
    SHOCK_COMPLETE_COL, SHOCK_EXTREME_COL, SHOCK_MISSING_COL,
]
shock = ant_read_data(SHOCK_TABLE, cols=SHOCK_READ_COLS).copy()
shock[WAVE_COL] = normalize_wave(shock[WAVE_COL])
emit([f" [读表] shock  shape={shock.shape}, n_wave={shock[WAVE_COL].nunique()}, "
      f"n_fund={shock[FUND_COL_SHOCK].nunique()}, usable_rate={(shock[SHOCK_USABLE_COL]==1).mean():.3f}"])

ctrl_probe = ant_read_data(PORT_CONTROL_TABLE).copy()
emit([f" [ctrl schema probe] cols in platform table: {list(ctrl_probe.columns)}"])
del ctrl_probe
gc.collect()

PORT_CONTROL_READ_COLS = [
    FUND_COL_SHOCK, WAVE_COL, CONTROL_RISK_COL, CONTROL_RET_COL, CONTROL_COVERAGE_COL,
]
port_control = ant_read_data(PORT_CONTROL_TABLE, cols=PORT_CONTROL_READ_COLS).copy()
port_control[WAVE_COL] = normalize_wave(port_control[WAVE_COL])
emit([f" [读表] ctrl   shape={port_control.shape}, n_wave={port_control[WAVE_COL].nunique()}, "
      f"n_fund={port_control[FUND_COL_SHOCK].nunique()}"])

# --- read user-fund month-end holding table (for fund→user aggregation) ---
holding = ant_read_data(
    HOLDING_TABLE,
    cols=[USER_COL, FUND_COL_SURVEY, HOLDING_AMT_COL, HOLDING_DATE_COL],
).copy()
holding = prep_holding(holding)
# OOM safety: holding table contains all months' snapshots but v8 only needs
# 5 month-end snapshots (one per wave). Drop everything else before aggregation.
needed_months = set(WAVE_HOLDING_MONTH.values())
n_before = len(holding)
holding = holding.loc[holding["month_p"].isin(needed_months)].copy()
gc.collect()
emit([f" [读表] holding shape={holding.shape} (filtered {n_before}→{len(holding)}, "
      f"n_user={holding[USER_COL].nunique()}, n_fund={holding[FUND_COL_SURVEY].nunique()}, "
      f"n_month={holding['month_p'].nunique()})"])


# === CELL 5: Sample funnel (per wave) + 5-wave pool ===
hr("CELL 5: sample funnel (per wave) + 5-wave pool",
   "9-step funnel per Notes_Xiaohan §Toy §488-490 → pooled RF regression input")

def construct_sample_wave(wave):
    """Process one wave: merge addon, derive traits/exp, merge shock/port,
    apply sample filters; return processed df + funnel counts DataFrame.
    """
    svy = surveys[wave].copy()
    funnel_rows = [("0_raw", len(svy))]

    # 1) merge 2024q2 addon (macro expectations補)
    if wave == "2024q2":
        svy = merge_2024q2_addon(svy, addon_2024q2)

    # 2) construct sme_owner + filter
    svy = construct_sme_owner(svy)
    svy = svy.loc[svy["sme_owner"].eq(1)].copy()
    funnel_rows.append(("1_sme_owner_eq_1", len(svy)))

    # 3) extract answer_seconds + filter ≥180 (NA 保留)
    svy = extract_answer_seconds(svy)
    svy = svy.loc[
        svy["answer_seconds"].isna() | svy["answer_seconds"].ge(ANSWER_SECONDS_MIN)
    ].copy()
    funnel_rows.append(("2_answer_ge_180_or_na", len(svy)))

    # 4) construct traits + map 主表 exp_*
    svy = construct_traits(svy, wave)
    svy = map_exp_columns(svy, wave)

    # 5) aggregate fund-level shock + control to user-level via holding weights
    shock_user = aggregate_shock_to_user(shock, holding, wave)
    port_user = aggregate_control_to_user(port_control, holding, wave)
    # diag: dump per-wave merge inputs to diagnose step 2→3 drops (sim 常见)
    n_svy_before = len(svy)
    n_shock_user = len(shock_user)
    n_port_user = len(port_user)
    # 额外diag: svy∩holding_user (不限 shock) 区分 user_id 问题 vs shock 覆盖
    holding_users = set(
        holding.loc[holding["month_p"].eq(WAVE_HOLDING_MONTH[wave]), USER_COL]
        .dropna().unique()
    )
    n_svy_in_holding = int(svy[USER_COL].isin(holding_users).sum())
    # 抽样 user_id 前 3 个对比格式
    svy_sample = svy[USER_COL].dropna().head(3).tolist()
    holding_sample = list(holding_users)[:3] if holding_users else []
    svy = svy.merge(shock_user, on=USER_COL, validate="many_to_one")
    svy = svy.merge(port_user, on=USER_COL, validate="many_to_one")
    n_after_merge = len(svy)
    emit([
        f" [diag {wave}] step3  svy_n={nf(n_svy_before)}  "
        f"holding_users={nf(len(holding_users))}  "
        f"svy∩holding={nf(n_svy_in_holding)}  "
        f"shock_user={nf(n_shock_user)}  "
        f"svy∩shock={nf(n_after_merge)}",
        f" [diag {wave}] svy_sample={svy_sample}  holding_sample={holding_sample}",
    ])
    funnel_rows.append(("3_aggregated_user_shock_port", n_after_merge))

    # 6) earliest submit_date in this wave + filter
    svy["submit_date"] = pd.to_datetime(svy["submit_date"], errors="coerce")
    earliest = svy["submit_date"].min()
    svy = svy.loc[svy["submit_date"].gt(earliest)].copy()
    funnel_rows.append(("4_submit_after_earliest", len(svy)))

    # 7) portfolio_size > 0
    svy = svy.loc[svy["portfolio_size"].gt(0)].copy()
    funnel_rows.append(("5_portfolio_size_gt_0", len(svy)))

    # 8) passive_complete = 1
    svy = svy.loc[svy["passive_complete"].eq(1)].copy()
    funnel_rows.append(("6_passive_complete_eq_1", len(svy)))

    # 9) controls_complete = 1
    svy = svy.loc[svy["controls_complete"].eq(1)].copy()
    funnel_rows.append(("7_controls_complete_eq_1", len(svy)))

    # 10) X100_R_passive not NA
    svy = svy.loc[svy["X100_R_passive"].notna()].copy()
    funnel_rows.append(("8_final_R_passive_notna", len(svy)))

    funnel_df = pd.DataFrame(funnel_rows, columns=["step", "n"])
    funnel_df["wave"] = wave
    return svy, funnel_df


samples = []
funnel_dfs = []
for wave in WAVES:
    svy_w, funnel_w = construct_sample_wave(wave)
    samples.append(svy_w)
    funnel_dfs.append(funnel_w)
    del svy_w
    # OOM: drop survey source df after this wave is processed so 5-wave dict
    # doesn't accumulate all 5 raw surveys in memory simultaneously.
    del surveys[wave]
    gc.collect()

funnel_pool = pd.concat(funnel_dfs, ignore_index=True)
del funnel_dfs  # OOM: release the per-wave funnel DataFrames after concat
# v7-style: emit funnel as monospace fmt_table (5 wave × 9 step wide format)
emit(fmt_table(
    ["wave", "step", "n"],
    [[row["wave"], row["step"], nf(row["n"])] for _, row in funnel_pool.iterrows()],
    [10, 32, 14],
))

df_reg = pd.concat(samples, ignore_index=True)
df_reg["wave"] = df_reg["wave"].astype("string")
del samples  # OOM: release per-wave processed df list after concat
gc.collect()
emit([
    f" [pool] 5_wave_pool  n_total={nf(len(df_reg))}  n_user={nf(df_reg[USER_COL].nunique())}",
])


# === CELL 5b: shock + 3 cell-bin 变量分布 (回归前 sanity) ===
hr("CELL 5b: 数值变量分布 (回归前 sanity)",
   "DIST_VARS = [X100_R_passive, portfolio_size, portfolio_risk_12m, expected_ret_12m];"
   " 三层防 OOM (kde=False / 新 df_plot / sample 50k)")

# v3.5/3.7 四层防 OOM (沿用 v7 line 779-784 + 803-805):
#  1) drop kde=True — seaborn histplot + scipy gaussian_kde 在大 N 下 OOM
#  2) numpy array → 新 DataFrame 切断 df_reg 视图引用
#  3) sample 5 万行 (hist 形态够, 不需 KDE 平滑)
#  4) gc.collect() 释 matplotlib 内部对象, 避免 4 张图累积
DIST_VARS = [
    "X100_R_passive",     # shock (pp)
    "portfolio_size",     # 持仓规模
    "portfolio_risk_12m", # σ (12m)
    "expected_ret_12m",   # R̄ (12m)
]

for col in DIST_VARS:
    if col not in df_reg.columns:
        emit([f"  [跳过] {col}: 不在 df_reg"])
        continue
    arr_full = df_reg[col].to_numpy()
    n_total_full = int(np.isfinite(arr_full).sum())
    # 主动判定是否缩尾 (离散/紧凑分布跳过)
    arr, clip_note = winsorize_decision(arr_full)
    n_after = int(len(arr))
    if n_after < 100:
        emit([f"  [跳过] {col}: winsorize 后有效样本 {n_after} < 100"])
        continue
    if n_after > 50000:
        rng = np.random.default_rng(0)
        arr = rng.choice(arr, 50000, replace=False)
    df_plot = pd.DataFrame({col: arr})
    ant_plot.re_init()
    ant_plot.figure_set(method="set_size_inches", w=8, h=4)
    ant_plot.figure_set(method="set_dpi", val=100)
    ant_plot.add_subplot(1, 1, 1)
    ant_plot.plot(
        df=df_plot,
        method="ant_plot_df",
        kind="hist",
        x=col,
        kde=False,
        bins=50,
    )
    ant_plot.axes_set(
        method="set_title",
        axindex=0,
        label=f"{col}  n={nf(n_total_full)} → {nf(n_after)}  ({clip_note})",
    )
    ant_plot.axes_set(method="set_xlabel", axindex=0, xlabel=col)
    ant_plot.show()
    emit([f"  5b 画完 {col} 分布  "
          f"(n={nf(n_total_full)} → {nf(n_after)}; {clip_note})"])
    del df_plot
    gc.collect()


# === CELL 6: Portfolio cell construction + main regression ===
hr("CELL 6: portfolio-cell FE + main RF regression (11 Y × 1 spec)")

# --- cell construction ---
# diag: check input bin columns for NA / unique-counts (1 cell + 388 user 通常是这三列全 NA)
emit([
    f" [diag bin input] portfolio_size  n_NA={int(df_reg['portfolio_size'].isna().sum())}  n_unique={int(df_reg['portfolio_size'].nunique(dropna=True))}",
    f" [diag bin input] portfolio_risk_12m  n_NA={int(df_reg['portfolio_risk_12m'].isna().sum())}  n_unique={int(df_reg['portfolio_risk_12m'].nunique(dropna=True))}",
    f" [diag bin input] expected_ret_12m  n_NA={int(df_reg['expected_ret_12m'].isna().sum())}  n_unique={int(df_reg['expected_ret_12m'].nunique(dropna=True))}",
    f" [diag bin input] X100_R_passive  n_NA={int(df_reg['X100_R_passive'].isna().sum())}  n_unique={int(df_reg['X100_R_passive'].nunique(dropna=True))}",
])
df_reg = build_cells(df_reg)

cell_size = (
    df_reg.groupby(CELL_FE_NAME, dropna=False).size()
    .rename("cell_n").reset_index()
)
emit([f" [cell size] n_cell={cell_size[CELL_FE_NAME].nunique(dropna=False)}  "
      f"n_singleton={int((cell_size['cell_n']==1).sum())}  "
      f"min={nf(int(cell_size['cell_n'].min()))}  "
      f"max={nf(int(cell_size['cell_n'].max()))}"])

# --- main regression: 11 Y × 1 spec (pooled RF, v7 run_reduced_form style) ---
results_rows = []
for y_var in Y_VARS:
    sub = df_reg.loc[df_reg[y_var].notna()].copy()
    n_pre_y = int(len(sub))
    if n_pre_y < 30:
        results_rows.append({
            "Y": y_var, "n_obs": n_pre_y,
            "beta": np.nan, "se": np.nan,
            "t_stat": np.nan, "p_value": np.nan, "R2": np.nan,
            "note": "skipped (n<30)",
        })
        continue
    res = run_rf(sub, y_var)
    if res is None:
        results_rows.append({
            "Y": y_var, "n_obs": n_pre_y,
            "beta": np.nan, "se": np.nan,
            "t_stat": np.nan, "p_value": np.nan, "R2": np.nan,
            "note": "skipped (run_rf returned None)",
        })
        continue
    results_rows.append({
        "Y": y_var, "n_obs": res["n"],
        "beta": res["beta"], "se": res["se"],
        "t_stat": res["t"], "p_value": res["p"],
        "R2": res["R2"],
        "note": "",
    })

results_df = pd.DataFrame(results_rows)
# v7-style: emit coef summary as monospace fmt_table
emit(fmt_table(
    ["Y", "n_obs", "beta", "se", "t", "p", "R2"],
    [[r["Y"], nf(int(r["n_obs"])),
      ff(r["beta"], nd=4), ff(r["se"], nd=4),
      ff(r["t_stat"], nd=2), ff(r["p_value"], nd=3),
      ff(r["R2"], nd=3)] for _, r in results_df.iterrows()],
    [18, 10, 9, 9, 7, 7, 7],
))

# --- per-Y n_obs by wave (sanity: check whether each Y has all 5 waves) ---
n_by_wave = (
    df_reg.groupby("wave")[Y_VARS].apply(lambda x: x.notna().sum())
    .reset_index()
)
# v7-style: emit n_by_wave as fmt_table (5 rows × 12 cols)
n_rows_table = []
for _, row in n_by_wave.iterrows():
    line = [str(row["wave"])] + [nf(int(row[y])) for y in Y_VARS]
    n_rows_table.append(line)
emit(fmt_table(
    ["wave"] + Y_VARS,
    n_rows_table,
    [10] + [9] * len(Y_VARS),
))

# v7-style: render LOGS registry at the end
emit(render_logs())