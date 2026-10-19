# === CELL 1: Imports and output helpers ===
"""SME-owner expectations reduced-form regression for the Ant platform."""

import gc
import hashlib
import time
import textwrap

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from marvel.AntPrint import ant_read_data, ant_print_all
from marvel.AntPrint.sandbox.global_constant import print_envir

print_envir()

TABLE_BUFFER = {}
MESSAGE_BUFFER = []
STAGE_TIMES = []
STAGE_STARTED = time.perf_counter()
STAGE_NAME = "setup"
REGRESSION_SAMPLE_CACHE = {}
FIT_COUNTS = {"regression": 0, "variation_fallback": 0}
FIT_SECONDS = {"regression_and_variation": 0.0}


def emit(lines):
    if isinstance(lines, str):
        lines = [lines]
    MESSAGE_BUFFER.extend(str(x) for x in lines)


def section(title):
    global STAGE_STARTED, STAGE_NAME
    now = time.perf_counter()
    STAGE_TIMES.append([STAGE_NAME, now - STAGE_STARTED])
    STAGE_STARTED, STAGE_NAME = now, title
    ant_print_all(pd.Series([title]), model_method="unique")


def fmt_int(x):
    return "-" if pd.isna(x) else f"{int(x):,d}"


def fmt_float(x, nd=4):
    return "-" if pd.isna(x) else f"{float(x):.{nd}f}"


def emit_table(title, columns, rows):
    """Collect summaries during preparation; report output starts in Cell 9."""
    TABLE_BUFFER[title] = (list(columns), [list(row) for row in rows])


def render_table(title, columns, rows, max_width=84, rows_per_block=11):
    """Short blocks, repeated headers and horizontal panels; never truncate."""
    columns = [str(c) for c in columns]
    rows = [[str(v) for v in row] for row in rows]
    widths = [min(24 if i == 0 else 44, max([len(c)] + [len(r[i]) for r in rows]))
              for i, c in enumerate(columns)]
    panels, panel = [], [0]
    for i in range(1, len(columns)):
        if sum(widths[j] for j in panel + [i]) + 2 * len(panel) > max_width:
            panels.append(panel)
            panel = [0]
        panel.append(i)
    panels.append(panel)
    for start in range(0, max(1, len(rows)), rows_per_block):
        for number, indices in enumerate(panels, 1):
            def wrapped(values):
                parts = [textwrap.wrap(values[i], width=widths[i]) or [""] for i in indices]
                return ["  ".join((p[k] if k < len(p) else "").ljust(widths[i])
                                  for i, p in zip(indices, parts))
                        for k in range(max(map(len, parts)))]
            lines = [f"{title} | rows {start + 1}-{min(start + rows_per_block, len(rows))}"
                     + (f" | panel {number}" if len(panels) > 1 else "")]
            lines += wrapped(columns)
            for row in rows[start:start + rows_per_block]:
                lines += wrapped(row)
            ant_print_all(pd.Series(lines), model_method="unique")


# === CELL 2: Adjustable settings ===

######### CONFIGURE START ###########
SCRIPT_REVISION = "sme_rf_v12_cd_gain_only"
RUN_ID = "cd_passive_gain_keepzero"
# Prepare all five waves once; D is selected only after cells are assigned.
WAVES = ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"]
COARSE_BINS = (5, 3, 3)
D_EXCLUDED_WAVE = "2024q3"

SE_TYPE = "cluster_user"  # cluster_user or HC1
OUTPUT_MODE = "compact"  # compact or full
RUN_MODE = "cd_only"  # only the two new specifications; no historical refits
TIMING_RULE = "post_window_only"  # audit_only shows timing but blocks estimates
MIN_REG_N = 30
ANSWER_SECONDS_MIN = 180
MIN_RETURN_COVERAGE = 0.999999
MIN_CONTROL_COVERAGE = 0.999999
MIN_CONTROL_MONTHS = 12

KEEP_ZERO_PORTFOLIO = True
INCLUDE_IMPUTED_ZERO = True
CORE_X_CHOICE = "passive_gain"
SHOCK_PORTFOLIO_SCOPE = "usable"  # raw, usable
ENFORCE_CONTROL_COMPLETENESS = True

N_SIZE_BIN = 10
N_RISK_BIN = 5
N_ERET_BIN = 5
CELL_RANK_SCOPE = "within_wave"
CELL_RANK_METHOD = "average"
ZERO_PORTFOLIO_CELL_MODE = "pooled_zero_within_wave"

CELL_FE_NAMES = ["analysis_portfolio_cell"]
# Positive-portfolio cells use wave-specific size x risk x expected-return ranks.
# Both zero sources share one cell per wave; source flags remain available.
OTHER_FE_NAMES = [
    "city_level_from_yicai", "portrait_gender",
    "survey_industry", "aer_bal_employee_group",
]
# Optional FE candidate from portrait: "portrait_risk_level".
CONTROL_NAMES = [
    "aer_bal_age", "aer_bal_college",
    "aer_bal_firm_age", "aer_bal_company",
]
# Optional control candidate: "aer_bal_employee_n"; prefer the grouped FE above.
REG_FE_NAMES = CELL_FE_NAMES + OTHER_FE_NAMES
REG_CONTROL_NAMES = list(CONTROL_NAMES)
EXT_CONTROL_NAMES = ["ctrl_log_portfolio", "ctrl_risk_pp", "ctrl_eret_pp"]
CD_SPECS = {
    "C": {"name": "C_coarse_w5_keepzero",
          "fe_names": ["coarse_portfolio_cell"] + OTHER_FE_NAMES,
          "control_names": CONTROL_NAMES + EXT_CONTROL_NAMES},
    "D": {"name": "D_fine_drop2024q3_keepzero",
          "fe_names": CELL_FE_NAMES + OTHER_FE_NAMES,
          "control_names": CONTROL_NAMES + EXT_CONTROL_NAMES},
}
######### CONFIGURE END ###########

# table names
# Proposed upload names; confirm the actual uploaded table names before running.
# Ordinary funds: calculable NAV price returns retained with event flags.
SHOCK_TABLE = "shock_panel_nav_annotated_v1"
PORT_CONTROL_TABLE = "ctrl_monthly_nav_annotated_v1"
EXPECTED_FUND_RETURN_VERSION = "nav_price_annotated_v1"
APPLY_NAV_QUALITY_SCREEN = False  # User choice: flags only; True reproduces stricter screened sample.

PROJECT_ID = "202405290032751511010004"
SURVEY_TEMPLATE = (
    f"frlab_sample_project_{PROJECT_ID}_v2_sme_sp_smesurvey{{wave}}_202512"
)
HOLDING_TABLE = (
    f"frlab_sample_project_{PROJECT_ID}_v2_sme_fund_invest_202512"
)
PORTRAIT_TABLE = (
    f"frlab_sample_project_{PROJECT_ID}_v2_sme_portrait_202512"
)
ADDON_2024Q2_TABLE = "sme_id3_2024q2_addExpectation"

SURVEY_BASE_COLS_BY_WAVE = {
    "2024q2": [
        "user_id", "submit_id", "submit_date", "v1", "extro_info",
        "user_age", "city_level_from_yicai",
    ],
    "2024q3": [
        "user_id", "submit_id", "submit_date", "v1", "extro_info",
        "user_age", "city_level_from_yicai",
    ],
    "2024q4": [
        "user_id", "submit_id", "submit_date", "v1", "extro_info",
        "user_age", "city_level_from_yicai",
    ],
    "2025q1": [
        "user_id", "submit_id", "submit_date", "v1", "extro_info",
        "user_age", "city_level_from_yicai",
    ],
    "2025q2": [
        "user_id", "submit_id", "submit_date", "v1", "extro_info",
        "user_age", "city_level_from_yicai",
    ],
}

# column names
USER_COL = "匿名化用户id"
SURVEY_USER_COL = "user_id"
FUND_COL_HOLDING = "基金代码"
FUND_COL_PANEL = "fund_code"
WAVE_COL = "wave"
HOLDING_AMT_COL = "当月月底日持有金额元"
REALIZED_GAIN_MONTH_COL = "当月累计月收益元"
HOLDING_DATE_COL = "日期"
PORTRAIT_GENDER_COL = "性别"
PORTRAIT_RISK_LEVEL_COL = "风险等级"

SHOCK_RET_PP_COL = "shock_ret_rate_pp"
SHOCK_USABLE_COL = "shock_usable"
SHOCK_WINDOW_START_COL = "window_start"
SHOCK_WINDOW_END_COL = "window_end"
CONTROL_MONTH_COL = "history_month"
CONTROL_MONTHLY_RET_COL = "ctrl_monthly_ret"

WAVE_IN_FUND_PANEL = {
    "24Q2": "2024q2", "24Q3": "2024q3", "24Q4": "2024q4",
    "25Q1": "2025q1", "25Q2": "2025q2",
}

WAVE_HOLDING_MONTH = {
    "2024q2": pd.Period("2024-05", freq="M"),
    "2024q3": pd.Period("2024-08", freq="M"),
    "2024q4": pd.Period("2024-11", freq="M"),
    "2025q1": pd.Period("2025-02", freq="M"),
    "2025q2": pd.Period("2025-05", freq="M"),
}

PASSIVE_RET_PREDICTOR = "X100_R_passive"
PASSIVE_GAIN_PREDICTOR = "passive_gain"
REALIZED_RETURN_PREDICTOR = "realized_return"
REALIZED_GAIN_COL = "realized_gain"
GAIN_UNIT_YUAN = 10_000  # Gain regressors are measured per 10,000 yuan.
CORE_X_VAR = PASSIVE_GAIN_PREDICTOR

if SHOCK_PORTFOLIO_SCOPE not in ["raw", "usable"]:
    emit([
        f"Invalid SHOCK_PORTFOLIO_SCOPE={SHOCK_PORTFOLIO_SCOPE}; fallback to raw.",
        "Valid SHOCK_PORTFOLIO_SCOPE values: raw, usable.",
    ])
    SHOCK_PORTFOLIO_SCOPE = "raw"

DIAG_ROWS = []
RUN_BLOCKERS = []

Y_VARS = [
    "exp_stock", "exp_gdp", "exp_cpi", "exp_house", "exp_rate",
    "exp_env_local", "exp_rev", "exp_market",
    "exp_price", "exp_wage", "exp_input_cost",
]

ADDON_2024Q2_KEY = "submit_id"
ADDON_2024Q2_MACRO_COLS = {
    "macroeconomic_gdp": "exp_gdp",
    "macroeconomic_house": "exp_house",
    "macroeconomic_cpi": "exp_cpi",
    "macroeconomic_rate": "exp_rate",
}


# mapping dictionaries
EXP_VCODES = {
    "exp_stock": {"2024q3": "v196", "2024q4": "v187", "2025q1": "v181", "2025q2": "v190"},
    "exp_gdp": {"2024q3": "v192", "2024q4": "v182", "2025q1": "v176", "2025q2": "v185"},
    "exp_cpi": {"2024q3": "v195", "2024q4": "v186", "2025q1": "v180", "2025q2": "v189"},
    "exp_house": {"2024q3": "v193", "2024q4": "v184", "2025q1": "v178", "2025q2": "v187"},
    "exp_rate": {"2024q3": "v194", "2024q4": "v185", "2025q1": "v179", "2025q2": "v188"},
    "exp_env_local": {"2024q2": "v203", "2024q3": "v212", "2024q4": "v203", "2025q1": "v198", "2025q2": "v206"},
    "exp_rev": {"2024q2": "v104", "2024q3": "v107", "2024q4": "v93", "2025q1": "v94", "2025q2": "v107"},
    "exp_market": {"2024q2": "v103", "2024q3": "v106", "2024q4": "v92", "2025q1": "v93", "2025q2": "v106"},
    "exp_price": {"2024q2": "v176", "2024q3": "v189", "2024q4": "v179", "2025q1": "v173", "2025q2": "v182"},
    "exp_wage": {"2024q2": "v177", "2024q3": "v190", "2024q4": "v180", "2025q1": "v174", "2025q2": "v183"},
    "exp_input_cost": {"2024q2": "v178", "2024q3": "v191", "2024q4": "v181", "2025q1": "v175", "2025q2": "v184"},
}

TRAIT_VCODES = {
    "industry": {"2024q2": "v43", "2024q3": "v42", "2024q4": "v28", "2025q1": "v29", "2025q2": "v29"},
    "education": {"2024q2": "v163", "2024q3": "v166", "2024q4": "v168", "2025q1": "v163", "2025q2": "v174"},
    "firm_year": {"2024q2": "v32", "2024q3": "v40", "2024q4": "v26", "2025q1": "v27", "2025q2": "v27"},
    "registration": {"2024q2": "v33", "2024q3": "v41", "2024q4": "v27", "2025q1": "v28", "2025q2": "v28"},
    "employee_n": {"2024q2": "v63", "2024q3": "v64", "2024q4": "v50", "2025q1": "v51", "2025q2": "v51"},
}

TRAIT_REFERENCE_YEAR = {
    "2024q2": 2024, "2024q3": 2024, "2024q4": 2025,
    "2025q1": 2025, "2025q2": 2025,
}

TRAIT_NAMES = [
    "aer_bal_age", "aer_bal_college",
    "aer_bal_firm_age", "aer_bal_company",
]

PCT_DICT = {
    "基本不变": 0, "增长20_以上": 25, "增长20_以内": 10,
    "降低20_以上": -25, "降低20_以内": -10,
    "增长10_以上": 15, "增长10_以内": 5,
    "降低10_以上": -15, "降低10_以内": -5,
    "下降3_以上": -4.0, "下降3_以下": -4.0, "下降0_3": -1.5,
    "增长0_3": 1.5, "增长3_4": 3.5, "增长4_5": 4.5,
    "增长5_6": 5.5, "增长6_8": 7.0, "增长8_以上": 9.0,
    "下降0_1": -0.5, "下降1_2": -1.5, "下降2_3": -2.5,
    "下降3_5": -4.0, "下降5_以上": -6.0, "降低5_以上": -6.0,
    "增长0_1": 0.5, "增长1_2": 1.5, "增长2_3": 2.5,
    "增长3_以上": 4.0, "上涨3_5": 4.0,
    "上涨3_以内": 2.0, "上涨5_以上": 6.0, "上涨5_以内": 4.0,
    "降低3_以内": -2.0, "降低3_5": -4.0,
    "上升0_1": 0.5, "上升1_2": 1.5, "上升2_以上": 2.5,
    "上升0_3": 1.5, "上升3_5": 4.0,
    "上升5_8": 6.5, "上升8_以上": 9.0,
    "上升0_5": 2.5, "上升5_10": 7.5, "上升10_15": 12.5,
    "上升15_30": 22.5, "上升15_以上": 22.5, "上升30_以上": 35.0,
    "下降0_5": -2.5, "下降5_10": -7.5, "下降10_15": -12.5,
    "下降15_30": -22.5, "下降15_以上": -22.5, "下降30_以上": -35.0,
    "没有明显变化": 0, "0_1": 0.5, "1_2": 1.5,
    "2_3": 2.5, "3_4": 3.5, "4_5": 4.5, "5_以上": 6.0,
    "不清楚": None, "不确定": None, "不适用": None,
    "关心但拿不准": None, "不适用_去年尚未工作": None,
}

INDEX_DICT = {
    "2200点以下": 2000.0, "2600点以下": 2400.0,
    "2200_2400点": 2300.0, "2400_2600点": 2500.0,
    "2600_2800点": 2700.0, "2800_3000点": 2900.0,
    "3000_3300点": 3150.0, "3300_3600点": 3450.0,
    "3600_3800点": 3700.0, "3800_4000点": 3900.0,
    "3600点以上": 3800.0, "4000点以上": 4200.0,
    "不确定": None, "不适用": None,
}

DIRECTION_DICT = {
    "好转": 1, "不变": 0, "恶化": -1,
    "预期变差": -1, "预期不变": 0, "预期好转": 1,
    "不清楚": None, "不确定": None, "不适用": None,
}

EXP_MAPPING = {
    "exp_stock": INDEX_DICT,
    "exp_gdp": PCT_DICT,
    "exp_cpi": PCT_DICT,
    "exp_house": PCT_DICT,
    "exp_rate": PCT_DICT,
    "exp_env_local": DIRECTION_DICT,
    "exp_rev": PCT_DICT,
    "exp_market": PCT_DICT,
    "exp_price": PCT_DICT,
    "exp_wage": PCT_DICT,
    "exp_input_cost": PCT_DICT,
}

COLLEGE_ANSWERS = ["大学专科_专科_高职高专_技师学院", "大学本科", "研究生及以上"]
NONCOLLEGE_ANSWERS = ["小学及以下", "初中", "高中_普通高中_成人高中_职业高中_中专_技校"]
COMPANY_ANSWERS = ["公司制企业_工商注册的企业", "公司制企业（工商注册的企业）"]
ESTYEAR_OVERRIDE = {"2015之前": "2013"}

EMPLOYEE_N_DICT = {
    "0": 0, "0人": 0, "0_即只有经营者": 0, "0_即只有经营者本人": 0,
    "1": 1, "1人": 1,
    "1_4": 2.5, "1_5": 3, "1_9": 5, "5_9": 7,
    "10_19": 14.5, "20_49": 34.5, "20_99": 60,
    "50_99": 74.5, "100_499": 299.5, "500_999": 749.5,
    "1000_以上": 1000, "100人以上": 100, "500人以上": 500,
}

EMPLOYEE_GROUP_DICT = {
    "0": "emp_0", "0人": "emp_0",
    "0_即只有经营者": "emp_0", "0_即只有经营者本人": "emp_0",
    "1": "emp_1_9", "1人": "emp_1_9",
    "1_4": "emp_1_9", "1_5": "emp_1_9", "1_9": "emp_1_9", "5_9": "emp_1_9",
    "10_19": "emp_10_19",
    "20_49": "emp_20_plus", "20_99": "emp_20_plus", "50_99": "emp_20_plus",
    "100_499": "emp_20_plus", "500_999": "emp_20_plus",
    "1000_以上": "emp_20_plus", "100人以上": "emp_20_plus", "500人以上": "emp_20_plus",
}


# === CELL 3: Data-construction helpers ===

def clean_text(series):
    return (
        series.astype("string")
        .str.strip()
        .replace({
            "": pd.NA, "NAN": pd.NA, "NaN": pd.NA, "nan": pd.NA,
            "None": pd.NA, "NULL": pd.NA, "<NA>": pd.NA,
        })
    )


def normalize_wave(series):
    out = series.astype("string").str.strip()
    key = out.str.upper()
    return key.map(WAVE_IN_FUND_PANEL).fillna(out.str.lower())


def normalize_fund_code(series):
    out = series.astype("string").str.strip().str.upper()
    out = out.str.replace(r"\.0$", "", regex=True)
    out = out.replace({"": pd.NA, "NAN": pd.NA, "NONE": pd.NA, "NULL": pd.NA, "<NA>": pd.NA})
    numeric_code = out.str.fullmatch(r"\d+", na=False)
    out.loc[numeric_code] = out.loc[numeric_code].str.zfill(6)
    return out


def safe_ratio(numerator, denominator):
    return np.where(denominator > 0, numerator / denominator, np.nan)


def as_formula_object(series):
    return series.astype("object").where(series.notna(), np.nan)


def map_employee_size(series):
    raw = clean_text(series)
    numeric = pd.to_numeric(raw, errors="coerce")
    mapped = raw.map(EMPLOYEE_N_DICT)
    employee_n = numeric.where(numeric.notna(), mapped)
    employee_group = raw.map(EMPLOYEE_GROUP_DICT)
    numeric_group = pd.cut(
        numeric,
        bins=[-np.inf, 0, 9, 19, np.inf],
        labels=["emp_0", "emp_1_9", "emp_10_19", "emp_20_plus"],
    ).astype("object")
    employee_group = employee_group.where(employee_group.notna(), numeric_group)
    employee_group = employee_group.where(employee_group.notna() | raw.isna(), "emp_unmapped")
    employee_group = employee_group.astype("object").where(pd.notna(employee_group), np.nan)
    return employee_n, employee_group


def get_survey_cols(wave):
    cols = list(SURVEY_BASE_COLS_BY_WAVE[wave])
    for y_name in Y_VARS:
        v_code = EXP_VCODES.get(y_name, {}).get(wave)
        if v_code is not None:
            cols.append(v_code)
    for trait_name in ["education", "firm_year", "registration", "employee_n", "industry"]:
        cols.append(TRAIT_VCODES[trait_name][wave])
    return list(dict.fromkeys(cols))


def extract_answer_seconds(df):
    out = df.copy()
    out["answer_seconds"] = np.nan
    out["answer_seconds_n_matches"] = 0
    if "extro_info" not in out.columns:
        return out
    matches = (
        out["extro_info"].astype("string")
        .str.findall(r"(?:^|;)answerSeconds\s*=\s*([0-9]+(?:\.[0-9]+)?)(?=;|$)")
    )
    out["answer_seconds_n_matches"] = matches.str.len()
    out["answer_seconds"] = pd.to_numeric(matches.str[-1], errors="coerce")
    return out


def construct_sme_owner(df):
    owner_answer = clean_text(df["v1"])
    return owner_answer.eq("我是小微经营者_我自愿参与本次调查").fillna(False).astype(int)


def construct_traits(df, wave):
    out = df.copy()
    out["aer_bal_age"] = pd.to_numeric(out.get("user_age"), errors="coerce")
    education = clean_text(out[TRAIT_VCODES["education"][wave]])
    out["aer_bal_college"] = np.nan
    out.loc[education.isin(NONCOLLEGE_ANSWERS), "aer_bal_college"] = 0
    out.loc[education.isin(COLLEGE_ANSWERS), "aer_bal_college"] = 1

    firm_year = clean_text(out[TRAIT_VCODES["firm_year"][wave]]).replace(ESTYEAR_OVERRIDE)
    firm_year = pd.to_numeric(firm_year, errors="coerce")
    out["aer_bal_firm_age"] = TRAIT_REFERENCE_YEAR[wave] - firm_year

    registration = clean_text(out[TRAIT_VCODES["registration"][wave]])
    out["aer_bal_company"] = np.nan
    has_registration = registration.notna()
    out.loc[has_registration, "aer_bal_company"] = (
        registration.loc[has_registration].isin(COMPANY_ANSWERS).astype(int)
    )
    out["aer_bal_employee_n"], out["aer_bal_employee_group"] = map_employee_size(
        out[TRAIT_VCODES["employee_n"][wave]]
    )
    out["city_level_from_yicai"] = clean_text(out["city_level_from_yicai"])
    out["survey_industry"] = clean_text(out[TRAIT_VCODES["industry"][wave]])
    return out


def map_expectations(df, wave):
    out = df.copy()
    for y_name in Y_VARS:
        v_code = EXP_VCODES.get(y_name, {}).get(wave)
        if v_code is None or v_code not in out.columns:
            continue
        mapped = clean_text(out[v_code]).map(EXP_MAPPING[y_name])
        out[y_name] = mapped
    return out


def duplicate_key_diagnostics(df, source_name, key_cols, value_cols):
    existing_value_cols = [col for col in value_cols if col in df.columns]
    key_label = "+".join(key_cols)
    if len(df) == 0:
        return [source_name, key_label, 0, 0, 0, 0, 0]
    dup_key_rows = df.duplicated(key_cols, keep=False)
    n_dup_key_rows = int(dup_key_rows.sum())
    n_dup_keys = int(df.loc[dup_key_rows, key_cols].drop_duplicates().shape[0])
    n_unique_keys = int(df[key_cols].drop_duplicates().shape[0])
    n_conflict_keys = 0
    if n_dup_key_rows > 0 and len(existing_value_cols) > 0:
        key_value = df.loc[dup_key_rows, key_cols + existing_value_cols].drop_duplicates()
        key_value_counts = key_value.groupby(key_cols).size()
        n_conflict_keys = int(key_value_counts.gt(1).sum())
    return [
        source_name, key_label, len(df), n_unique_keys,
        n_dup_key_rows, n_dup_keys, n_conflict_keys,
    ]


def resolve_2024q2_addon(addon):
    """Resolve each question independently, without selecting a first record.

    Unknown nonempty answers conservatively invalidate that question. Missing
    keys are excluded so pandas cannot match null keys to survey null keys.
    """
    key = ADDON_2024Q2_KEY
    cols = list(ADDON_2024Q2_MACRO_COLS)
    work = addon[[key] + cols].copy()
    work[key] = clean_text(work[key])
    work = work.loc[work[key].notna()].copy()
    for col in cols:
        work[col] = clean_text(work[col])
    rows = []
    for submit_key, group in work.groupby(key, sort=True):
        row = {key: submit_key}
        for col, outcome in ADDON_2024Q2_MACRO_COLS.items():
            answers = group[col].dropna().drop_duplicates()
            mapped = answers.map(EXP_MAPPING[outcome])
            # Exactly one valid encoded answer, with no unknown text.
            if len(answers) and mapped.notna().all() and mapped.nunique() == 1:
                row[col] = sorted(answers.tolist())[0]
            else:
                row[col] = pd.NA
        rows.append(row)
    resolved = pd.DataFrame(rows, columns=[key] + cols)
    resolved[key] = resolved[key].astype("string")
    return resolved


def merge_2024q2_addon(df, addon):
    out = df.copy()
    keep_cols = [ADDON_2024Q2_KEY] + list(ADDON_2024Q2_MACRO_COLS)
    addon_keep = addon[keep_cols].copy()
    out[ADDON_2024Q2_KEY] = clean_text(out[ADDON_2024Q2_KEY])
    addon_keep[ADDON_2024Q2_KEY] = addon_keep[ADDON_2024Q2_KEY].astype("string")
    survey_keys = set(out[ADDON_2024Q2_KEY].dropna().unique())
    addon_keys = set(addon_keep[ADDON_2024Q2_KEY].dropna().unique())
    n_key_overlap = len(survey_keys.intersection(addon_keys))
    out = out.merge(addon_keep, on=ADDON_2024Q2_KEY, how="left", validate="many_to_one")
    for source_col, y_name in ADDON_2024Q2_MACRO_COLS.items():
        raw = clean_text(out[source_col])
        mapping = EXP_MAPPING[y_name]
        out[y_name] = raw.map(mapping)
    diag = {
        "wave": "2024q2",
        "survey_submit_id": len(survey_keys),
        "addon_submit_id": len(addon_keys),
        "submit_id_overlap": n_key_overlap,
    }
    for source_col, y_name in ADDON_2024Q2_MACRO_COLS.items():
        diag[f"{y_name}_nonmiss"] = int(out[y_name].notna().sum())
    DIAG_ROWS.append(diag)
    return out


def prep_holding(df):
    out = df.copy()
    if USER_COL not in out.columns and SURVEY_USER_COL in out.columns:
        out = out.rename(columns={SURVEY_USER_COL: USER_COL})
    date_str8 = out[HOLDING_DATE_COL].astype("string").str.extract(r"(\d{8})$")[0]
    out["date_dt"] = pd.to_datetime(date_str8, format="%Y%m%d", errors="coerce")
    out["month_p"] = out["date_dt"].dt.to_period("M")
    out[USER_COL] = out[USER_COL].astype("string").str.strip()
    out[FUND_COL_HOLDING] = normalize_fund_code(out[FUND_COL_HOLDING])
    out[HOLDING_AMT_COL] = pd.to_numeric(out[HOLDING_AMT_COL], errors="coerce")
    out[REALIZED_GAIN_MONTH_COL] = pd.to_numeric(
        out[REALIZED_GAIN_MONTH_COL], errors="coerce"
    )
    return out


def prep_portrait(df):
    out = df.copy()
    if USER_COL not in out.columns and SURVEY_USER_COL in out.columns:
        out = out.rename(columns={SURVEY_USER_COL: USER_COL})
    out[USER_COL] = out[USER_COL].astype("string").str.strip()
    out["portrait_gender"] = clean_text(out[PORTRAIT_GENDER_COL])
    if PORTRAIT_RISK_LEVEL_COL in out.columns:
        out["portrait_risk_level"] = clean_text(out[PORTRAIT_RISK_LEVEL_COL])
    else:
        out["portrait_risk_level"] = pd.NA
    return out[
        [USER_COL, "portrait_gender", "portrait_risk_level"]
    ].drop_duplicates(USER_COL, keep="first")


def prepare_panel_keys(df):
    out = df.copy()
    out[WAVE_COL] = normalize_wave(out[WAVE_COL])
    out[FUND_COL_PANEL] = normalize_fund_code(out[FUND_COL_PANEL])
    return out


def holdings_for_wave(holding, wave):
    out = holding.loc[
        holding["month_p"].eq(WAVE_HOLDING_MONTH[wave]),
        [USER_COL, FUND_COL_HOLDING, HOLDING_AMT_COL, REALIZED_GAIN_MONTH_COL],
    ].copy()
    out = (
        out.groupby([USER_COL, FUND_COL_HOLDING], as_index=False)
        .agg(
            holding_amt_raw=(HOLDING_AMT_COL, lambda x: x.sum(min_count=1)),
            realized_gain=(REALIZED_GAIN_MONTH_COL, lambda x: x.sum(min_count=1)),
        )
    )
    out["holding_amt"] = out["holding_amt_raw"].where(out["holding_amt_raw"].ge(0))
    out["realized_gain"] = out["realized_gain"].fillna(0)
    return out


def aggregate_shock_to_user(shock, holding, wave):
    h = holdings_for_wave(holding, wave)
    s = shock.loc[
        shock[WAVE_COL].eq(wave),
        [FUND_COL_PANEL, SHOCK_RET_PP_COL, SHOCK_USABLE_COL],
    ].drop_duplicates(FUND_COL_PANEL).copy()
    s[SHOCK_RET_PP_COL] = pd.to_numeric(s[SHOCK_RET_PP_COL], errors="coerce")
    s[SHOCK_USABLE_COL] = pd.to_numeric(s[SHOCK_USABLE_COL], errors="coerce")
    merged = h.merge(s, left_on=FUND_COL_HOLDING, right_on=FUND_COL_PANEL, how="left", validate="many_to_one")
    merged["shock_matched"] = merged[SHOCK_RET_PP_COL].notna()
    merged["shock_usable"] = merged["shock_matched"] & merged[SHOCK_USABLE_COL].eq(1)
    merged["shock_matched_holding"] = np.where(merged["shock_matched"], merged["holding_amt"], 0)
    merged["shock_usable_holding"] = np.where(merged["shock_usable"], merged["holding_amt"], 0)
    merged["shock_weighted_pp"] = merged["holding_amt"] * merged[SHOCK_RET_PP_COL].where(merged["shock_usable"])
    merged["realized_gain_usable"] = merged[REALIZED_GAIN_COL].where(merged["shock_usable"], 0)
    user = (
        merged.groupby(USER_COL, as_index=False)
        .agg(
            portfolio_size_raw=("holding_amt", lambda x: x.sum(min_count=1)),
            portfolio_size_usable=("shock_usable_holding", "sum"),
            realized_gain=(REALIZED_GAIN_COL, lambda x: x.sum(min_count=1)),
            realized_gain_usable=("realized_gain_usable", "sum"),
            shock_matched_holding=("shock_matched_holding", "sum"),
            shock_usable_holding=("shock_usable_holding", "sum"),
            shock_weighted_pp=("shock_weighted_pp", "sum"),
            n_funds=(FUND_COL_HOLDING, "nunique"),
            n_shock_matched=("shock_matched", "sum"),
            n_shock_usable=("shock_usable", "sum"),
        )
    )
    if SHOCK_PORTFOLIO_SCOPE == "usable":
        user["portfolio_size"] = user["portfolio_size_usable"]
        user[REALIZED_GAIN_COL] = user["realized_gain_usable"]
    else:
        user["portfolio_size"] = user["portfolio_size_raw"]
    user["return_coverage"] = safe_ratio(
        user["shock_usable_holding"], user["portfolio_size_raw"]
    )
    user[PASSIVE_RET_PREDICTOR] = safe_ratio(user["shock_weighted_pp"], user["portfolio_size"])
    user[REALIZED_RETURN_PREDICTOR] = 100 * safe_ratio(
        user[REALIZED_GAIN_COL], user["portfolio_size"]
    )
    user[PASSIVE_GAIN_PREDICTOR] = user["shock_weighted_pp"] / 100 / GAIN_UNIT_YUAN
    user[REALIZED_GAIN_COL] = user[REALIZED_GAIN_COL] / GAIN_UNIT_YUAN
    user["realized_gain_usable"] = user["realized_gain_usable"] / GAIN_UNIT_YUAN
    return user


def aggregate_control_to_user(control, holding, wave):
    h = holdings_for_wave(holding, wave)
    h["portfolio_size"] = h.groupby(USER_COL)["holding_amt"].transform(
        lambda x: x.sum(min_count=1)
    )
    c = control.loc[
        control[WAVE_COL].eq(wave),
        [FUND_COL_PANEL, CONTROL_MONTH_COL, CONTROL_MONTHLY_RET_COL],
    ].drop_duplicates([FUND_COL_PANEL, CONTROL_MONTH_COL]).copy()
    c[CONTROL_MONTHLY_RET_COL] = pd.to_numeric(
        c[CONTROL_MONTHLY_RET_COL], errors="coerce"
    )
    merged = h.merge(
        c,
        left_on=FUND_COL_HOLDING,
        right_on=FUND_COL_PANEL,
        how="left",
        validate="many_to_many",
    )
    merged["control_matched"] = merged[CONTROL_MONTHLY_RET_COL].notna()
    merged["control_matched_holding"] = np.where(merged["control_matched"], merged["holding_amt"], 0)
    merged["weighted_monthly_ret"] = (
        merged["holding_amt"]
        * merged[CONTROL_MONTHLY_RET_COL].where(merged["control_matched"])
    )

    user_month = (
        merged.groupby([USER_COL, CONTROL_MONTH_COL], as_index=False)
        .agg(
            control_portfolio_size=("portfolio_size", "first"),
            control_matched_holding=("control_matched_holding", "sum"),
            weighted_monthly_ret=("weighted_monthly_ret", lambda x: x.sum(min_count=1)),
            n_control_matched=("control_matched", "sum"),
        )
    )
    months = c[[CONTROL_MONTH_COL]].drop_duplicates().copy()
    users = h[[USER_COL, "portfolio_size"]].drop_duplicates().copy()
    months["_tmp_key"] = 1
    users["_tmp_key"] = 1
    user_month_grid = users.merge(months, on="_tmp_key", how="outer", validate="many_to_many")
    user_month_grid = user_month_grid.drop(columns=["_tmp_key"])
    user_month = user_month_grid.merge(
        user_month,
        on=[USER_COL, CONTROL_MONTH_COL],
        how="left",
        validate="one_to_one",
    )
    user_month["control_portfolio_size"] = user_month[
        "control_portfolio_size"
    ].fillna(user_month["portfolio_size"])
    user_month["control_matched_holding"] = user_month[
        "control_matched_holding"
    ].fillna(0)
    user_month["n_control_matched"] = user_month["n_control_matched"].fillna(0)
    user_month["control_month_coverage"] = safe_ratio(
        user_month["control_matched_holding"],
        user_month["control_portfolio_size"],
    )
    user_month["portfolio_ret_month"] = safe_ratio(
        user_month["weighted_monthly_ret"],
        user_month["control_portfolio_size"],
    )

    user = (
        user_month.groupby(USER_COL, as_index=False)
        .agg(
            expected_ret_12m=("portfolio_ret_month", "mean"),
            portfolio_risk_12m=("portfolio_ret_month", "std"),
            control_coverage=("control_month_coverage", "mean"),
            control_min_coverage=("control_month_coverage", "min"),
            control_n_months=("portfolio_ret_month", "count"),
            n_control_matched=("n_control_matched", "sum"),
        )
    )
    return user[
        [
            USER_COL,
            "control_coverage",
            "control_min_coverage",
            "control_n_months",
            "portfolio_risk_12m",
            "expected_ret_12m",
            "n_control_matched",
        ]
    ]


def add_within_wave_rank_bin(df, value_col, n_bins, out_col, eligible_mask):
    out = df.copy()
    out[out_col] = pd.Series(pd.NA, index=out.index, dtype="Int64")
    ranks = (
        out.loc[eligible_mask]
        .groupby("wave", dropna=False)[value_col]
        .rank(method=CELL_RANK_METHOD, pct=True)
    )
    bins = np.ceil(ranks * n_bins).clip(1, n_bins).astype("Int64")
    out.loc[bins.index, out_col] = bins
    return out


def build_portfolio_cells(df, bins=None):
    out = df.copy()
    size_bins, risk_bins, mean_bins = bins or (N_SIZE_BIN, N_RISK_BIN, N_ERET_BIN)
    positive = out["portfolio_size"].gt(0)
    recorded_zero = out["recorded_zero_portfolio"].fillna(False)
    imputed_zero = out["imputed_zero_portfolio"].fillna(False)

    out["portfolio_cell_status"] = "zero_other"
    out.loc[recorded_zero, "portfolio_cell_status"] = "zero_recorded"
    out.loc[imputed_zero, "portfolio_cell_status"] = "zero_imputed"
    out.loc[positive, "portfolio_cell_status"] = "positive"

    out = add_within_wave_rank_bin(
        out, "portfolio_size", size_bins, "analysis_size_bin", positive
    )
    out = add_within_wave_rank_bin(
        out, "portfolio_risk_12m", risk_bins, "analysis_risk_bin", positive
    )
    out = add_within_wave_rank_bin(
        out, "expected_ret_12m", mean_bins, "analysis_eret_bin", positive
    )

    out["analysis_portfolio_cell"] = pd.Series(pd.NA, index=out.index, dtype="string")
    out.loc[positive, "analysis_portfolio_cell"] = (
        out.loc[positive, "wave"].astype("string") + "_P_"
        + out.loc[positive, "analysis_size_bin"].astype("string") + "_"
        + out.loc[positive, "analysis_risk_bin"].astype("string") + "_"
        + out.loc[positive, "analysis_eret_bin"].astype("string")
    )
    zero_rows = ~positive
    out.loc[zero_rows, "analysis_portfolio_cell"] = (
        out.loc[zero_rows, "wave"].astype("string") + "_Z"
    )
    return out


def cell_assignment_hash(df):
    assignments = (
        df[[USER_COL, "analysis_portfolio_cell"]]
        .astype("string")
        .sort_values([USER_COL, "analysis_portfolio_cell"])
    )
    payload = "|".join(
        assignments[USER_COL].fillna("<NA>")
        + "="
        + assignments["analysis_portfolio_cell"].fillna("<NA>")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def enabled_existing(names, df):
    return [name for name in names if name in df.columns]


def fill_zero_portfolio_rows(df, include_unmatched=True):
    out = df.copy()
    zero_portfolio = out["recorded_zero_portfolio"].fillna(False) | (
        out["imputed_zero_portfolio"].fillna(False) & include_unmatched
    )
    # Only the fixed-starting-portfolio amount and passive gain are zero.
    # Preserve observed realized gains and original history diagnostics.
    for col in ["portfolio_size", "portfolio_size_usable", PASSIVE_GAIN_PREDICTOR]:
        out.loc[zero_portfolio, col] = 0.0
    for col in [PASSIVE_RET_PREDICTOR, "portfolio_risk_12m", "expected_ret_12m"]:
        out.loc[zero_portfolio, col] = np.nan
    return out


def sample_after_steps(base, steps):
    out = base.copy()
    rows = [["0_raw", len(out), "-"]]
    prev_n = len(out)
    for step_name, mask in steps:
        out = out.loc[mask.loc[out.index].fillna(False)]
        rows.append([step_name, len(out), prev_n - len(out)])
        prev_n = len(out)
    return rows


def regression_sample(df, y_name, extra_cols=None):
    """Cache complete cases after preparation is frozen; clear on Cell 7 rerun."""
    extra_cols = extra_cols or []
    key = (id(df), y_name, tuple(extra_cols))
    if key in REGRESSION_SAMPLE_CACHE:
        return REGRESSION_SAMPLE_CACHE[key]
    cols = list(dict.fromkeys(
        [USER_COL, y_name, CORE_X_VAR] + REG_FE_NAMES + REG_CONTROL_NAMES + extra_cols
    ))
    if any(col not in df.columns for col in cols):
        return pd.DataFrame(columns=cols)
    run = df.loc[df["analysis_base_sample"].eq(1), cols].copy()
    for col in list(dict.fromkeys([y_name, CORE_X_VAR] + REG_CONTROL_NAMES + extra_cols)):
        run[col] = pd.to_numeric(run[col], errors="coerce")
    for col in REG_FE_NAMES:
        run[col] = as_formula_object(run[col])
    run[USER_COL] = as_formula_object(run[USER_COL])
    run = run.replace([np.inf, -np.inf], np.nan).dropna(subset=cols)
    REGRESSION_SAMPLE_CACHE[key] = run
    return run


def add_continuous_portfolio_controls(df):
    """Design columns only: zeros exempt; underlying history stays missing."""
    out = df.copy()
    size = pd.to_numeric(out["portfolio_size"], errors="coerce")
    positive = size.gt(0) & np.isfinite(size)
    zero = out["zero_history_not_applicable"].fillna(False).astype(bool)
    for name in EXT_CONTROL_NAMES:
        out[name] = np.nan
        out.loc[zero, name] = 0.0
    out.loc[positive, "ctrl_log_portfolio"] = np.log(size.loc[positive])
    for source, target in [("portfolio_risk_12m", "ctrl_risk_pp"),
                           ("expected_ret_12m", "ctrl_eret_pp")]:
        values = pd.to_numeric(out[source], errors="coerce")
        out.loc[positive, target] = 100 * values.loc[positive]
    out[EXT_CONTROL_NAMES] = out[EXT_CONTROL_NAMES].replace([np.inf, -np.inf], np.nan)
    return out


def fe_terms_for(run, names):
    return [f"C({name})" for name in names if run[name].nunique() >= 2]


def variation_from_fit(fit, run, terms):
    """FWL residual of X from its fitted pseudoinverse row; no extra fit normally.

    Reuse only when X is separately estimable. Aliased designs use a direct
    nuisance regression, preserving the old diagnostic even in degeneracy.
    """
    x = run[CORE_X_VAR].to_numpy(dtype=float)
    pos = fit.model.exog_names.index(CORE_X_VAR)
    weights = fit.model.pinv_wexog[pos]
    target = np.zeros(fit.model.exog.shape[1])
    target[pos] = 1
    if np.allclose(weights @ fit.model.exog, target, rtol=1e-7, atol=1e-8):
        resid = weights / np.dot(weights, weights)
        df_resid = fit.df_resid + 1
    else:
        auxiliary = smf.ols(f"{CORE_X_VAR} ~ " + (" + ".join(terms) or "1"), data=run).fit()
        FIT_COUNTS["variation_fallback"] += 1
        resid, df_resid = auxiliary.resid, auxiliary.df_resid
    raw_ss = float(np.sum((x - x.mean()) ** 2))
    return {"raw_X_sd": float(np.std(x, ddof=1)),
            "residual_X_sd": float(np.std(resid, ddof=1)),
            "residual_SS_share": float(np.sum(np.asarray(resid) ** 2) / raw_ss) if raw_ss else np.nan,
            "df_resid": float(df_resid)}


def estimate_rf(run, y_name, spec, cache):
    """Keep statsmodels estimation/covariance unchanged; cache small summaries.

    The cache lives for one outcome with immutable source values. Matrices and
    fitted models are released after each fit, avoiding a large model cache.
    """
    key = (tuple(run.index), tuple(spec["fe_names"]), tuple(spec["control_names"]))
    if key in cache:
        return dict(cache[key], spec=spec["name"])
    row = {"Y": y_name, "spec": spec["name"], "n_obs": len(run),
           "n_users": run[USER_COL].nunique(), "note": "",
           **dict.fromkeys(["beta", "se", "t", "p", "R2", "holm_p"], np.nan)}
    if RUN_BLOCKERS:
        row["note"] = "blocked_integrity_gate"
    elif run[[y_name, CORE_X_VAR] + spec["fe_names"] + spec["control_names"]].isna().any().any():
        row["note"] = "missing_model_input_no_silent_drop"
    elif len(run) < MIN_REG_N:
        row["note"] = "skip_n"
    elif run[CORE_X_VAR].nunique() < 2:
        row["note"] = "no_X_variation"
    elif SE_TYPE == "cluster_user" and row["n_users"] < 2:
        row["note"] = "too_few_user_clusters"
    if not row["note"]:
        started = time.perf_counter()
        terms = fe_terms_for(run, spec["fe_names"]) + list(spec["control_names"])
        # Same term ordering and fitting API as v9 for coefficient/SE parity.
        ols = smf.ols(f"{y_name} ~ " + " + ".join([CORE_X_VAR] + terms), data=run)
        fit = (ols.fit(cov_type="cluster", cov_kwds={"groups": run[USER_COL].astype(str)})
               if SE_TYPE == "cluster_user" else ols.fit(cov_type=SE_TYPE))
        FIT_COUNTS["regression"] += 1
        row.update(beta=float(fit.params.get(CORE_X_VAR, np.nan)),
                   se=float(fit.bse.get(CORE_X_VAR, np.nan)),
                   t=float(fit.tvalues.get(CORE_X_VAR, np.nan)),
                   p=float(fit.pvalues.get(CORE_X_VAR, np.nan)), R2=float(fit.rsquared))
        if not np.isfinite(row["se"]):
            row["note"] = "nonfinite_se"
        row["variation"] = variation_from_fit(fit, run, terms)
        del fit, ols
        FIT_SECONDS["regression_and_variation"] += time.perf_counter() - started
    cache[key] = row.copy()
    return row


def cell_diagnostics_sample(run, cell_col="analysis_portfolio_cell"):
    if run.empty:
        return dict.fromkeys(["cells", "singleton_cells", "share_obs_cell_lt5",
                              "share_obs_no_X_variation", "cell_p50", "within_cell_X_sd"], np.nan)
    grouped = run.groupby(cell_col, observed=True)
    sizes = grouped.size()
    unique_x = grouped[CORE_X_VAR].nunique()
    within = run[CORE_X_VAR] - grouped[CORE_X_VAR].transform("mean")
    return {"cells": len(sizes), "singleton_cells": int(sizes.eq(1).sum()),
            "share_obs_cell_lt5": float(sizes.loc[sizes.lt(5)].sum() / len(run)),
            "share_obs_no_X_variation": float(sizes.loc[unique_x.le(1)].sum() / len(run)),
            "cell_p50": float(sizes.median()), "within_cell_X_sd": float(within.std())}


def select_cd_samples(source, y_name):
    """Preserve v11 eligibility; C changes cells only, D drops one wave only."""
    basic = regression_sample(source, y_name)
    common = basic.join(source.loc[basic.index, EXT_CONTROL_NAMES], validate="one_to_one")
    common = common.replace([np.inf, -np.inf], np.nan).dropna(subset=EXT_CONTROL_NAMES)
    c = common.join(source.loc[common.index, ["coarse_portfolio_cell"]], validate="one_to_one")
    c["coarse_portfolio_cell"] = as_formula_object(c["coarse_portfolio_cell"])
    # Missing C labels must flag a skipped fit, never silently change its sample.
    d = common.loc[~source.loc[common.index, "wave"].eq(D_EXCLUDED_WAVE)].copy()
    audit = [short_y(y_name), len(basic), len(common), len(basic) - len(common),
             len(c), int(c["coarse_portfolio_cell"].isna().sum()), len(d), len(common) - len(d)]
    return {"C": c, "D": d}, audit


def apply_holm(rows):
    indices = [i for i, row in enumerate(rows) if np.isfinite(row["p"])]
    if indices:
        adjusted = multipletests([rows[i]["p"] for i in indices], method="holm")[1]
        for i, p in zip(indices, adjusted):
            rows[i]["holm_p"] = float(p)


def short_y(name):
    return name.removeprefix("exp_") if hasattr(str, "removeprefix") else name.replace("exp_", "", 1)


def ci_text(row):
    if not np.isfinite(row["beta"]) or not np.isfinite(row["se"]):
        return "-"
    return f'{row["beta"] - 1.96 * row["se"]:.5f}, {row["beta"] + 1.96 * row["se"]:.5f}'


# === CELL 4: Read source tables ===

section("CELL 4: Read source tables")

surveys = {}
read_rows = []
dedup_diag_rows = []
for wave in WAVES:
    table_name = SURVEY_TEMPLATE.format(wave=wave)
    df_wave = ant_read_data(table_name, cols=get_survey_cols(wave)).copy()
    if USER_COL not in df_wave.columns and SURVEY_USER_COL in df_wave.columns:
        df_wave = df_wave.rename(columns={SURVEY_USER_COL: USER_COL})
    df_wave[USER_COL] = df_wave[USER_COL].astype("string").str.strip()
    df_wave["wave"] = wave
    surveys[wave] = df_wave
    read_rows.append([wave, "survey", df_wave.shape[0], df_wave.shape[1]])

addon_2024q2 = ant_read_data(
    ADDON_2024Q2_TABLE,
    cols=[ADDON_2024Q2_KEY] + list(ADDON_2024Q2_MACRO_COLS),
).copy()
read_rows.append(["2024q2", "addon", addon_2024q2.shape[0], addon_2024q2.shape[1]])
addon_2024q2 = resolve_2024q2_addon(addon_2024q2)
addon_resolution_ok = (
    addon_2024q2[ADDON_2024Q2_KEY].notna().all()
    and not addon_2024q2[ADDON_2024Q2_KEY].duplicated().any()
    and all(
        addon_2024q2[col].dropna().isin(EXP_MAPPING[outcome]).all()
        for col, outcome in ADDON_2024Q2_MACRO_COLS.items()
    )
)
if not addon_resolution_ok:
    RUN_BLOCKERS.append("invalid_resolved_addon")
# Only execution/integrity status: no duplicate-group counts, answers or IDs.
emit_table(
    "CORE 1 Addon Resolution Policy and Integrity",
    ["check", "result"],
    [["policy", "per_question_unique_mapped_answer"],
     ["missing_plus_unique_valid", "retain_valid"],
     ["conflicting_or_unknown_answer", "question_missing"],
     ["missing_submit_id", "exclude_from_addon_merge"],
     ["resolved_keys_and_values", "PASS" if addon_resolution_ok else "BLOCK"],
     ["small_group_details", "not_output"]],
)

shock = ant_read_data(
    SHOCK_TABLE,
    cols=[
        FUND_COL_PANEL, WAVE_COL, SHOCK_RET_PP_COL, SHOCK_USABLE_COL,
        SHOCK_WINDOW_START_COL, SHOCK_WINDOW_END_COL,
        "return_version", "screen_pass_all_checks",
    ],
).copy()
shock = prepare_panel_keys(shock)
if not shock["return_version"].eq(EXPECTED_FUND_RETURN_VERSION).all():
    RUN_BLOCKERS.append("unexpected_shock_return_version")
for col in [SHOCK_WINDOW_START_COL, SHOCK_WINDOW_END_COL]:
    shock[col] = pd.to_datetime(shock[col], errors="coerce").dt.normalize()
SHOCK_WINDOW_END_BY_WAVE = {}
shock_window_rows = []
for wave in WAVES:
    wave_shock = shock.loc[shock[WAVE_COL].eq(wave)]
    starts = wave_shock[SHOCK_WINDOW_START_COL].dropna().drop_duplicates()
    ends = wave_shock[SHOCK_WINDOW_END_COL].dropna().drop_duplicates()
    valid = (
        len(wave_shock) > 0 and len(starts) == 1 and len(ends) == 1
        and wave_shock[SHOCK_WINDOW_START_COL].notna().all()
        and wave_shock[SHOCK_WINDOW_END_COL].notna().all()
        and starts.iloc[0] <= ends.iloc[0]
    )
    if valid:
        SHOCK_WINDOW_END_BY_WAVE[wave] = ends.iloc[0]
    else:
        RUN_BLOCKERS.append(f"ambiguous_shock_window_{wave}")
    shock_window_rows.append([
        wave, fmt_int(len(wave_shock)), fmt_int(len(starts)), fmt_int(len(ends)),
        starts.iloc[0].date() if len(starts) == 1 else "-",
        ends.iloc[0].date() if len(ends) == 1 else "-",
        "PASS" if valid else "BLOCK",
    ])
emit_table(
    "CORE 1 Shock Window Calendar",
    ["wave", "fund_rows", "n_starts", "n_ends", "start", "end", "gate"],
    shock_window_rows,
)
dedup_diag_rows.append(duplicate_key_diagnostics(
    shock,
    "shock",
    [WAVE_COL, FUND_COL_PANEL],
    [SHOCK_RET_PP_COL, SHOCK_USABLE_COL],
))
read_rows.append(["all", "shock", shock.shape[0], shock.shape[1]])

control = ant_read_data(
    PORT_CONTROL_TABLE,
    cols=[FUND_COL_PANEL, WAVE_COL, CONTROL_MONTH_COL, CONTROL_MONTHLY_RET_COL, "return_version", "screen_pass_all_checks"],
).copy()
control = prepare_panel_keys(control)
if not control["return_version"].eq(EXPECTED_FUND_RETURN_VERSION).all():
    RUN_BLOCKERS.append("unexpected_control_return_version")
if APPLY_NAV_QUALITY_SCREEN:
    shock.loc[~pd.to_numeric(shock['screen_pass_all_checks'], errors='coerce').eq(1), SHOCK_USABLE_COL] = 0
    control.loc[~pd.to_numeric(control['screen_pass_all_checks'], errors='coerce').eq(1), CONTROL_MONTHLY_RET_COL] = np.nan
emit(f"Fund NAV quality screen applied: {APPLY_NAV_QUALITY_SCREEN}; default retains calculable flagged price returns.")
control[CONTROL_MONTH_COL] = control[CONTROL_MONTH_COL].astype("string").str.strip().str.slice(0, 7)
dedup_diag_rows.append(duplicate_key_diagnostics(
    control,
    "control",
    [WAVE_COL, FUND_COL_PANEL, CONTROL_MONTH_COL],
    [CONTROL_MONTHLY_RET_COL],
))
read_rows.append(["all", "control", control.shape[0], control.shape[1]])


portrait_raw = ant_read_data(
    PORTRAIT_TABLE,
    cols=[USER_COL, PORTRAIT_GENDER_COL, PORTRAIT_RISK_LEVEL_COL],
).copy()
if USER_COL not in portrait_raw.columns and SURVEY_USER_COL in portrait_raw.columns:
    portrait_diag = portrait_raw.rename(columns={SURVEY_USER_COL: USER_COL})
else:
    portrait_diag = portrait_raw
dedup_diag_rows.append(duplicate_key_diagnostics(
    portrait_diag,
    "portrait",
    [USER_COL],
    [PORTRAIT_GENDER_COL, PORTRAIT_RISK_LEVEL_COL],
))
portrait = prep_portrait(portrait_raw)
read_rows.append(["all", "portrait", portrait.shape[0], portrait.shape[1]])

holding = ant_read_data(
    HOLDING_TABLE,
    cols=[
        USER_COL, FUND_COL_HOLDING, HOLDING_AMT_COL,
        REALIZED_GAIN_MONTH_COL, HOLDING_DATE_COL,
    ],
).copy()
holding = prep_holding(holding)
invalid_holding_dates = int(holding["date_dt"].isna().sum())
if invalid_holding_dates:
    RUN_BLOCKERS.append(f"unparsed_holding_dates_{invalid_holding_dates}")
emit_table(
    "CORE 1 Holding Date Parse Audit",
    ["all_holding_rows", "unparsed_dates", "gate"],
    [[fmt_int(len(holding)), fmt_int(invalid_holding_dates),
      "BLOCK" if invalid_holding_dates else "PASS"]],
)
holding = holding.loc[holding["month_p"].isin(set(WAVE_HOLDING_MONTH.values()))].copy()
read_rows.append(["all", "holding", holding.shape[0], holding.shape[1]])

holding_date_rows = []
for wave in WAVES:
    month = WAVE_HOLDING_MONTH[wave]
    wave_holding = holding.loc[holding["month_p"].eq(month)]
    dates = wave_holding["date_dt"].dropna().dt.normalize().drop_duplicates()
    end = SHOCK_WINDOW_END_BY_WAVE.get(wave)
    first_day_of_shock = shock.loc[
        shock[WAVE_COL].eq(wave), SHOCK_WINDOW_START_COL
    ].dropna().min()
    valid = (
        len(wave_holding) > 0 and len(dates) == 1
        and pd.notna(first_day_of_shock) and dates.iloc[0] < first_day_of_shock
        and pd.notna(end)
    )
    if not valid:
        RUN_BLOCKERS.append(f"holding_snapshot_date_{wave}")
    holding_date_rows.append([
        wave, str(month), fmt_int(len(wave_holding)), fmt_int(len(dates)),
        dates.iloc[0].date() if len(dates) == 1 else "-",
        "PASS" if valid else "BLOCK",
    ])
emit_table(
    "CORE 1 Holding Snapshot Date Audit",
    ["wave", "month", "rows", "n_dates", "snapshot_date", "gate"],
    holding_date_rows,
)
for source, _, _, _, _, _, conflict_keys in dedup_diag_rows:
    if conflict_keys > 0:
        RUN_BLOCKERS.append(f"conflicting_source_keys_{source}")

emit_table(
    "Source Read Summary",
    ["wave", "source", "rows", "cols"],
    [[w, s, fmt_int(r), fmt_int(c)] for w, s, r, c in read_rows],
)

emit_table(
    "Duplicate Key Diagnostics Before Deduplication",
    [
        "source", "key", "rows", "unique_keys",
        "dup_key_rows", "dup_keys", "conflict_keys",
    ],
    [
        [source, key, fmt_int(rows), fmt_int(unique_keys), fmt_int(dup_rows),
         fmt_int(dup_keys), fmt_int(conflict_keys)]
        for source, key, rows, unique_keys, dup_rows, dup_keys, conflict_keys
        in dedup_diag_rows
    ],
)


# === CELL 5: Build survey panel ===

section("CELL 5: Build survey panel")

survey_parts = []
for wave in WAVES:
    svy = surveys[wave].copy()
    if wave == "2024q2":
        svy = merge_2024q2_addon(svy, addon_2024q2)
    svy = extract_answer_seconds(svy)
    svy["sme_owner"] = construct_sme_owner(svy)
    svy = construct_traits(svy, wave)
    svy = map_expectations(svy, wave)
    survey_parts.append(svy)
    del surveys[wave]
    gc.collect()

survey_panel = pd.concat(survey_parts, ignore_index=True)
survey_panel = survey_panel.merge(portrait, on=USER_COL, how="left", validate="many_to_one")
survey_panel["submit_dt"] = pd.to_datetime(
    survey_panel["submit_date"], errors="coerce"
).dt.normalize()
survey_panel["unique_user_wave"] = ~survey_panel.duplicated(
    [USER_COL, "wave"], keep=False
)
del survey_parts
gc.collect()

survey_summary_rows = []
for wave in WAVES:
    tmp = survey_panel.loc[survey_panel["wave"].eq(wave)]
    short_answer = tmp["answer_seconds"].notna() & tmp["answer_seconds"].lt(ANSWER_SECONDS_MIN)
    survey_summary_rows.append([
        wave, fmt_int(len(tmp)), fmt_int(tmp[USER_COL].nunique()),
        fmt_int(tmp["sme_owner"].sum()), fmt_int(tmp["answer_seconds"].notna().sum()),
        fmt_int(short_answer.sum()),
    ])

emit_table(
    "Survey Construction Summary",
    ["wave", "rows", "users", "sme_owner", "answer_n", "answer_lt_min"],
    survey_summary_rows,
)

if len(DIAG_ROWS) > 0:
    addon_diag_rows = []
    for row in DIAG_ROWS:
        addon_diag_rows.append([
            row["wave"],
            fmt_int(row["survey_submit_id"]),
            fmt_int(row["submit_id_overlap"]),
            fmt_int(row["exp_gdp_nonmiss"]),
            fmt_int(row["exp_cpi_nonmiss"]),
            fmt_int(row["exp_house_nonmiss"]),
            fmt_int(row["exp_rate_nonmiss"]),
        ])
    emit_table(
        "2024q2 Addon Merge Diagnostics",
        [
            "wave", "survey_keys", "key_overlap",
            "gdp_nonmiss", "cpi_nonmiss", "house_nonmiss", "rate_nonmiss",
        ],
        addon_diag_rows,
    )

# === CELL 6: Aggregate fund-level shock and controls to users ===

section("CELL 6: Aggregate shock and controls")

user_parts = []
for wave in WAVES:
    shock_user = aggregate_shock_to_user(shock, holding, wave)
    control_user = aggregate_control_to_user(control, holding, wave)
    user_wave = shock_user.merge(control_user, on=USER_COL, how="left", validate="one_to_one")
    user_wave["wave"] = wave
    user_parts.append(user_wave)

user_panel = pd.concat(user_parts, ignore_index=True)
del user_parts
gc.collect()

coverage_rows = []
for wave in WAVES:
    tmp = user_panel.loc[user_panel["wave"].eq(wave)]
    coverage_rows.append([
        wave, fmt_int(len(tmp)), fmt_int(tmp[USER_COL].nunique()),
        fmt_float(tmp["portfolio_size_raw"].mean(), 2),
        fmt_float(tmp["portfolio_size_usable"].mean(), 2),
        fmt_float(tmp["portfolio_size"].mean(), 2),
        fmt_float(tmp["return_coverage"].mean(), 4),
        fmt_float(tmp["control_coverage"].mean(), 4),
        fmt_float(tmp["control_min_coverage"].mean(), 4),
        fmt_float(tmp["control_n_months"].mean(), 2),
        fmt_int(tmp[PASSIVE_RET_PREDICTOR].notna().sum()),
        fmt_int(tmp[PASSIVE_GAIN_PREDICTOR].notna().sum()),
        fmt_int(tmp[REALIZED_RETURN_PREDICTOR].notna().sum()),
        fmt_int(tmp[REALIZED_GAIN_COL].notna().sum()),
        fmt_int(tmp["portfolio_risk_12m"].notna().sum()),
    ])

emit_table(
    "User-Level Shock and Control Summary",
    [
        "wave", "rows", "users", "mean_port_raw", "mean_port_usable",
        "mean_port_reg", "ret_cov", "ctrl_cov", "ctrl_min_cov",
        "ctrl_months", "R_nonmiss", "Pgain_nonmiss", "realR_nonmiss", "realG_nonmiss",
        "risk_nonmiss",
    ],
    coverage_rows,
)


# === CELL 7: Define base sample and portfolio cells ===

section("CELL 7: Define sample and portfolio cells")
REGRESSION_SAMPLE_CACHE.clear()

df = survey_panel.merge(user_panel, on=[USER_COL, "wave"], how="left", validate="many_to_one")
df["holding_record_matched"] = df["portfolio_size_raw"].notna()
df["recorded_zero_portfolio"] = (
    df["holding_record_matched"] & df["portfolio_size_raw"].eq(0)
)
df["imputed_zero_portfolio"] = ~df["holding_record_matched"]
df["recorded_positive_portfolio"] = (
    df["holding_record_matched"] & df["portfolio_size_raw"].gt(0)
)
if KEEP_ZERO_PORTFOLIO:
    df = fill_zero_portfolio_rows(df, include_unmatched=INCLUDE_IMPUTED_ZERO)

df["sample_sme_owner"] = df["sme_owner"].eq(1)
df["sample_answer_time"] = df["answer_seconds"].isna() | df["answer_seconds"].ge(ANSWER_SECONDS_MIN)
df["sample_unique_user_wave"] = df["unique_user_wave"].fillna(False)
df["shock_window_end"] = pd.to_datetime(
    df["wave"].map(SHOCK_WINDOW_END_BY_WAVE), errors="coerce"
)
df["timing_after_window"] = df["submit_dt"].gt(df["shock_window_end"])
df["sample_timing"] = (
    df["timing_after_window"] if TIMING_RULE == "post_window_only"
    else pd.Series(True, index=df.index)
)
if TIMING_RULE not in ["post_window_only", "audit_only"]:
    RUN_BLOCKERS.append("invalid_timing_rule")
if SE_TYPE not in ["cluster_user", "HC1"]:
    RUN_BLOCKERS.append("invalid_se_type")
if OUTPUT_MODE not in ["compact", "full"]:
    RUN_BLOCKERS.append("invalid_output_mode")
timing_rows = []
for wave in WAVES:
    tmp = df.loc[
        df["wave"].eq(wave) & df["sample_sme_owner"] & df["sample_answer_time"]
    ]
    before_or_on_end = tmp["submit_dt"].notna() & tmp["shock_window_end"].notna() & ~tmp["timing_after_window"]
    timing_rows.append([
        wave, fmt_int(len(tmp)), fmt_int(tmp["submit_dt"].isna().sum()),
        fmt_int(before_or_on_end.sum()), fmt_int(tmp["timing_after_window"].sum()),
        fmt_int((~tmp["sample_unique_user_wave"]).sum()),
    ])
emit_table(
    "CORE 2 Survey Timing and Duplicate Audit",
    ["wave", "owners_after_answer", "missing_submit", "on_or_before_end", "after_end", "duplicate_rows"],
    timing_rows,
)
df["sample_portfolio_rule"] = (
    df["portfolio_size"].gt(0)
    | (KEEP_ZERO_PORTFOLIO & df["recorded_zero_portfolio"])
    | (KEEP_ZERO_PORTFOLIO & INCLUDE_IMPUTED_ZERO & df["imputed_zero_portfolio"])
)
df["zero_history_not_applicable"] = (
    KEEP_ZERO_PORTFOLIO & (
        df["recorded_zero_portfolio"]
        | (INCLUDE_IMPUTED_ZERO & df["imputed_zero_portfolio"])
    )
)
df["sample_core_x_nonmissing"] = df[CORE_X_VAR].notna()
df["sample_return_complete"] = (
    df["zero_history_not_applicable"] | df["return_coverage"].ge(MIN_RETURN_COVERAGE)
)
df["sample_control_complete"] = (
    df["zero_history_not_applicable"] | (
        df["control_min_coverage"].ge(MIN_CONTROL_COVERAGE)
        & df["control_n_months"].ge(MIN_CONTROL_MONTHS)
    )
)
df["sample_cell_inputs"] = (
    df["zero_history_not_applicable"] | (
        df["portfolio_size"].gt(0)
        & df["portfolio_risk_12m"].notna()
        & df["expected_ret_12m"].notna()
    )
)
df["analysis_base_sample"] = (
    df["sample_sme_owner"]
    & df["sample_answer_time"]
    & df["sample_unique_user_wave"]
    & df["sample_timing"]
    & df["sample_portfolio_rule"]
    & df["sample_core_x_nonmissing"]
    & df["sample_return_complete"]
    & ((not ENFORCE_CONTROL_COMPLETENESS) | df["sample_control_complete"])
).fillna(False).astype(int)

holding_provenance_rows = []
for scope, tmp in [["all", df]] + [
    [wave, df.loc[df["wave"].eq(wave)]] for wave in WAVES
]:
    base_tmp = tmp.loc[tmp["analysis_base_sample"].eq(1)]
    holding_provenance_rows.append([
        scope,
        fmt_int(len(tmp)),
        fmt_int(tmp["holding_record_matched"].sum()),
        fmt_int(tmp["recorded_positive_portfolio"].sum()),
        fmt_int(tmp["recorded_zero_portfolio"].sum()),
        fmt_int(tmp["imputed_zero_portfolio"].sum()),
        fmt_int(len(base_tmp)),
        fmt_int(base_tmp["recorded_zero_portfolio"].sum()),
        fmt_int(base_tmp["imputed_zero_portfolio"].sum()),
    ])

emit_table(
    "CORE 2 Holding Match and Zero Portfolio Provenance",
    [
        "scope", "rows", "matched", "record_pos", "record_zero",
        "imputed_zero", "base_n", "base_record_zero", "base_imputed_zero",
    ],
    holding_provenance_rows,
)

cell_base = df.loc[
    df["analysis_base_sample"].eq(1)
    & df["sample_cell_inputs"],
    [
        USER_COL, "wave", "portfolio_size", "portfolio_risk_12m",
        "expected_ret_12m", "recorded_zero_portfolio",
        "imputed_zero_portfolio", "recorded_positive_portfolio",
    ],
].copy()
cell_base_n_before_dedup = len(cell_base)
cell_base = cell_base.drop_duplicates([USER_COL, "wave"], keep="first").copy()
cell_base_n_dup = cell_base_n_before_dedup - len(cell_base)
cell_base = build_portfolio_cells(cell_base)
# Same pre-outcome population and zero labels; no re-ranking after D omission.
cell_base["coarse_portfolio_cell"] = build_portfolio_cells(cell_base, COARSE_BINS)["analysis_portfolio_cell"]

df = df.merge(
    cell_base[[
        USER_COL, "wave", "analysis_size_bin", "analysis_risk_bin",
        "analysis_eret_bin", "portfolio_cell_status",
        "analysis_portfolio_cell", "coarse_portfolio_cell",
    ]],
    on=[USER_COL, "wave"],
    how="left",
    validate="many_to_one",
)

cell_size = cell_base.groupby(
    "analysis_portfolio_cell", dropna=False
).size().rename("cell_n").reset_index()
emit_table(
    "Portfolio Cell Summary",
    ["metric", "value"],
    [
        ["rows_with_cell", fmt_int(len(cell_base))],
        ["duplicate_user_wave_removed", fmt_int(cell_base_n_dup)],
        ["n_cell", fmt_int(cell_size["analysis_portfolio_cell"].nunique(dropna=False))],
        ["n_singleton", fmt_int((cell_size["cell_n"] == 1).sum())],
        ["min_cell_n", fmt_int(cell_size["cell_n"].min())],
        ["max_cell_n", fmt_int(cell_size["cell_n"].max())],
    ],
)

cell_audit_rows = []
for wave in WAVES:
    wave_cells = cell_base.loc[cell_base["wave"].eq(wave)]
    for status in ["positive", "zero_recorded", "zero_imputed", "zero_other"]:
        tmp = wave_cells.loc[wave_cells["portfolio_cell_status"].eq(status)]
        if len(tmp) == 0:
            continue
        cell_audit_rows.append([
            wave,
            status,
            fmt_int(len(tmp)),
            fmt_int(tmp["analysis_size_bin"].nunique(dropna=True)),
            fmt_int(tmp["analysis_risk_bin"].nunique(dropna=True)),
            fmt_int(tmp["analysis_eret_bin"].nunique(dropna=True)),
            fmt_int(tmp["analysis_portfolio_cell"].nunique(dropna=True)),
            cell_assignment_hash(tmp),
        ])

emit_table(
    "Portfolio Cell Construction Audit",
    [
        "wave", "status", "n", "size_bins", "risk_bins", "eret_bins",
        "cells", "assignment_hash",
    ],
    cell_audit_rows,
)

for fe_name in REG_FE_NAMES:
    if fe_name in df.columns:
        df[f"sample_fe_{fe_name}"] = df[fe_name].notna()
for control_name in REG_CONTROL_NAMES:
    if control_name in df.columns:
        df[f"sample_control_{control_name}"] = df[control_name].notna()

base_steps = [
    ("1_sme_owner", df["sample_sme_owner"]),
    ("2_answer_time", df["sample_answer_time"]),
    ("2b_unique_user_wave", df["sample_unique_user_wave"]),
    ("2c_post_window_timing", df["sample_timing"]),
    (
        ("3_portfolio_ge0_including_imputed" if INCLUDE_IMPUTED_ZERO
         else "3_portfolio_ge0_recorded_only" if KEEP_ZERO_PORTFOLIO
         else "3_portfolio_gt0"),
        df["sample_portfolio_rule"],
    ),
    (f"4_{CORE_X_VAR}_nonmissing", df["sample_core_x_nonmissing"]),
    ("5_return_complete_diag", df["sample_return_complete"]),
    ("6_control_complete_diag", df["sample_control_complete"]),
    ("7_cell_inputs_diag", df["sample_cell_inputs"]),
]
for control_name in REG_CONTROL_NAMES:
    sample_col = f"sample_control_{control_name}"
    if sample_col in df.columns:
        base_steps.append((f"control_{control_name}_nonmissing", df[sample_col]))
for fe_name in REG_FE_NAMES:
    sample_col = f"sample_fe_{fe_name}"
    if sample_col in df.columns:
        base_steps.append((f"fe_{fe_name}_nonmissing", df[sample_col]))

sample_rows = []
for step, n_remaining, n_dropped in sample_after_steps(df, base_steps):
    dropped_text = "-" if n_dropped == "-" else fmt_int(n_dropped)
    sample_rows.append(["all", step, fmt_int(n_remaining), dropped_text])
if OUTPUT_MODE == "full":
    for wave in WAVES:
        wave_base = df.loc[df["wave"].eq(wave)]
        for step, n_remaining, n_dropped in sample_after_steps(wave_base, base_steps):
            dropped_text = "-" if n_dropped == "-" else fmt_int(n_dropped)
            sample_rows.append([wave, step, fmt_int(n_remaining), dropped_text])

emit_table(
    "AUX 0 Sample Size Sequential Funnel",
    ["scope", "step", "n_remaining", "n_dropped"],
    sample_rows,
)

outcome_sample_rows = []
for y_name in Y_VARS:
    run_base = df.loc[df["analysis_base_sample"].eq(1)].copy()
    y_nonmiss = run_base.loc[run_base[y_name].notna()]
    all_reg_vars = regression_sample(df, y_name)
    outcome_sample_rows.append([
        y_name,
        fmt_int(len(run_base)),
        fmt_int(len(y_nonmiss)),
        fmt_int(len(run_base) - len(y_nonmiss)),
        fmt_int(len(all_reg_vars)),
        fmt_int(len(y_nonmiss) - len(all_reg_vars)),
        fmt_int(all_reg_vars[USER_COL].nunique()),
    ])

emit_table(
    "CORE 3 Outcome Regression Sample Size",
    ["Y", "base_n", "Y_nonmiss_n", "Y_missing_drop", "reg_ready_n", "reg_var_drop", "users"],
    outcome_sample_rows,
)


# === CELL 8: Estimate C and D only ===

section("CELL 8: Estimate C and D only")
FIT_COUNTS = {"regression": 0, "variation_fallback": 0}
FIT_SECONDS = {"regression_and_variation": 0.0}
if RUN_MODE != "cd_only":
    RUN_BLOCKERS.append("invalid_RUN_MODE_requires_cd_only")
if SE_TYPE not in ["cluster_user", "HC1"]:
    RUN_BLOCKERS.append("invalid_SE_TYPE")
if OUTPUT_MODE not in ["compact", "full"]:
    RUN_BLOCKERS.append("invalid_OUTPUT_MODE")
if (CORE_X_VAR != PASSIVE_GAIN_PREDICTOR or CORE_X_CHOICE != "passive_gain"
        or not KEEP_ZERO_PORTFOLIO or not INCLUDE_IMPUTED_ZERO):
    RUN_BLOCKERS.append("cd_requires_gain_and_both_zero_sources")
if WAVES != ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"] or D_EXCLUDED_WAVE != "2024q3":
    RUN_BLOCKERS.append("cd_requires_five_preparation_waves_and_omit_2024q3")
if (N_SIZE_BIN, N_RISK_BIN, N_ERET_BIN) != (10, 5, 5) or tuple(COARSE_BINS) != (5, 3, 3):
    RUN_BLOCKERS.append("cd_requires_fine_10_5_5_and_coarse_5_3_3")
if TIMING_RULE != "post_window_only":
    RUN_BLOCKERS.append("timing_not_post_window_only")
required_columns = list(dict.fromkeys(
    [USER_COL, CORE_X_VAR, "wave", "coarse_portfolio_cell", "portfolio_size", "portfolio_size_raw",
     "portfolio_risk_12m", "expected_ret_12m", "zero_history_not_applicable",
     "recorded_zero_portfolio", "imputed_zero_portfolio"] + REG_FE_NAMES + REG_CONTROL_NAMES + Y_VARS
))
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    RUN_BLOCKERS.append("missing_analysis_columns:" + ",".join(missing_columns))
RUN_BLOCKERS = list(dict.fromkeys(RUN_BLOCKERS))
cd_results = {"C": [], "D": []}
cd_sample_rows, cd_density_rows, cd_variation_rows, cd_selection_rows = [], [], [], []
if not missing_columns:
    continuous_frame = add_continuous_portfolio_controls(df)
    df[EXT_CONTROL_NAMES] = continuous_frame[EXT_CONTROL_NAMES]
    del continuous_frame
    for y_name in Y_VARS:
        samples, selection = select_cd_samples(df, y_name)
        cd_selection_rows.append(selection)
        cache = {}
        for group in ["C", "D"]:
            sample = samples[group]
            result = estimate_rf(sample, y_name, CD_SPECS[group], cache)
            cd_results[group].append(result)
            audit = df.loc[sample.index]
            positive = audit["portfolio_size_raw"].gt(0)
            active_waves = [wave for wave in WAVES if audit["wave"].eq(wave).any()]
            cd_sample_rows.append([
                group, short_y(y_name), len(sample), sample[USER_COL].nunique(), int(positive.sum()),
                int(audit["recorded_zero_portfolio"].sum()), int(audit["imputed_zero_portfolio"].sum()),
                len(active_waves), ",".join(active_waves) or "none",
            ])
            cell_col = "coarse_portfolio_cell" if group == "C" else "analysis_portfolio_cell"
            for scope, subset in [("all", sample), ("positive", sample.loc[positive])]:
                density = cell_diagnostics_sample(subset, cell_col)
                cd_density_rows.append([
                    group, scope, short_y(y_name), len(subset), fmt_int(density["cells"]),
                    fmt_int(density["singleton_cells"]), fmt_float(density["share_obs_cell_lt5"]),
                    fmt_float(density["share_obs_no_X_variation"]), fmt_float(density["cell_p50"], 1),
                ])
            variation = result.get("variation", {})
            cd_variation_rows.append([
                group, short_y(y_name), result["n_obs"],
                fmt_float(variation.get("raw_X_sd", np.nan)),
                fmt_float(variation.get("residual_X_sd", np.nan)),
                fmt_float(variation.get("residual_SS_share", np.nan)),
                fmt_int(variation.get("df_resid", np.nan)), result["note"] or "-",
            ])
        del cache
for group in ["C", "D"]:
    apply_holm(cd_results[group])  # one outcome family per specification, not across C/D selection


# === CELL 9: Report - settings, integrity and sample construction ===

section("CELL 9: Report - settings, integrity and sample construction")
COMPUTE_STAGE_TIMES = list(STAGE_TIMES)
ant_print_all(pd.Series(["=== REPORT BEGIN ===", RUN_ID, SCRIPT_REVISION]), model_method="unique")
render_table("01 Settings and integrity", ["setting", "value"], [
    ["revision", SCRIPT_REVISION], ["run", RUN_ID], ["mode", RUN_MODE], ["output", OUTPUT_MODE],
    ["gate", "BLOCK" if RUN_BLOCKERS else "PASS"], ["blockers", "; ".join(RUN_BLOCKERS) or "none"],
    ["C", "gain; include zeros; five waves; 5/3/3 cells; continuous controls"],
    ["D", "gain; include zeros; omit 2024q3; original 10/5/5 cells; continuous controls"],
    ["preparation_waves", ", ".join(WAVES)], ["X", CORE_X_VAR], ["gain_unit_yuan", GAIN_UNIT_YUAN],
    ["cell_ranks", CELL_RANK_SCOPE + "/" + CELL_RANK_METHOD], ["zero_cell", ZERO_PORTFOLIO_CELL_MODE],
    ["keep_zero", KEEP_ZERO_PORTFOLIO], ["include_absent_zero", INCLUDE_IMPUTED_ZERO],
    ["SE", SE_TYPE], ["timing", TIMING_RULE], ["min_answer_seconds", ANSWER_SECONDS_MIN],
    ["min_reg_N", MIN_REG_N], ["min_return_coverage", MIN_RETURN_COVERAGE],
    ["min_history_coverage", MIN_CONTROL_COVERAGE], ["min_history_months", MIN_CONTROL_MONTHS],
    ["portfolio_scope", SHOCK_PORTFOLIO_SCOPE], ["require_history", ENFORCE_CONTROL_COMPLETENESS],
    ["return_version", EXPECTED_FUND_RETURN_VERSION], ["NAV_quality_screen", APPLY_NAV_QUALITY_SCREEN],
    ["shock_table", SHOCK_TABLE], ["control_table", PORT_CONTROL_TABLE],
    ["other_FE", ", ".join(OTHER_FE_NAMES)], ["basic_controls", ", ".join(CONTROL_NAMES)],
    ["continuous_controls", "ln(portfolio yuan), historical monthly SD pp, historical monthly mean pp"],
    ["zero_design", "continuous design columns=0; raw history remains not applicable"],
    ["Holm", "within C and within D, among estimable outcomes; not across specification search"],
    ["Y_units", "stock=index points; env_local=direction; others=mapped percentage points"],
])
addon_title = "CORE 1 Addon Resolution Policy and Integrity"
if addon_title in TABLE_BUFFER:
    render_table("01b Addon integrity", *TABLE_BUFFER[addon_title])
if "CORE 1 Shock Window Calendar" in TABLE_BUFFER:
    render_table("01c Shock windows", ["wave", "start", "end", "gate"],
                 [[r[0], r[4], r[5], r[6]] for r in TABLE_BUFFER["CORE 1 Shock Window Calendar"][1]])
if MESSAGE_BUFFER:
    render_table("01d Preparation messages", ["item", "message"],
                 [[i + 1, msg] for i, msg in enumerate(MESSAGE_BUFFER)])
render_table("01e Current sample selection", ["Y", "basic_N", "continuous_N", "control_drop", "C_N", "C_cell_missing", "D_N", "q3_drop"], cd_selection_rows)


def report_cd_results(group):
    rows = cd_results[group]
    render_table("02 " + group + " estimates", ["Y", "N", "beta", "SE", "p", "Holm_p"], [
        [short_y(r["Y"]), r["n_obs"], fmt_float(r["beta"], 5), fmt_float(r["se"], 5),
         fmt_float(r["p"]), fmt_float(r["holm_p"])] for r in rows])
    render_table("02 " + group + " intervals and fit", ["Y", "users", "95% CI", "R2", "note"], [
        [short_y(r["Y"]), r["n_users"], ci_text(r), fmt_float(r["R2"], 3), r["note"] or "-"] for r in rows])
    render_table("02 " + group + " sample composition", ["Y", "N", "users", "positive", "record0", "absent0", "n_waves", "waves"],
                 [r[1:] for r in cd_sample_rows if r[0] == group])


# === CELL 10: Report - C coarse cells with all five waves ===

section("CELL 10: Report - C coarse cells with all five waves")
report_cd_results("C")


# === CELL 11: Report - D original cells excluding 2024q3 ===

section("CELL 11: Report - D original cells excluding 2024q3")
report_cd_results("D")


# === CELL 12: Report - cell density, shock variation and timing ===

section("CELL 12: Report - cell density, shock variation and timing")
for group in ["C", "D"]:
    for scope in ["all", "positive"]:
        render_table("03 " + group + " cell density: " + scope,
                     ["Y", "N", "cells", "single", "share_lt5", "share_noX", "median"],
                     [r[2:] for r in cd_density_rows if r[0] == group and r[1] == scope])
    render_table("03 " + group + " conditional gain variation",
                 ["Y", "N", "raw_sd", "resid_sd", "SS_share", "df_resid", "note"],
                 [r[1:] for r in cd_variation_rows if r[0] == group])
render_table("04 Compute timing (seconds; report rendering excluded)", ["stage", "seconds"],
             [[name, fmt_float(seconds, 2)] for name, seconds in COMPUTE_STAGE_TIMES])
render_table("04 Fit counts", ["type", "fits"], list(FIT_COUNTS.items()))
render_table("04 Fit time (included above)", ["component", "seconds"],
             [[name, fmt_float(seconds, 2)] for name, seconds in FIT_SECONDS.items()])
ant_print_all(pd.Series(["C and D share one preparation; only two outcome families are estimated.",
                        "D retains original cell assignments. It is a wave sensitivity, not a policy design.",
                        "Positive cell-density rows are descriptive; no positive-only regression is added."]), model_method="unique")


# === CELL 13: Report - optional preparation appendix ===

section("CELL 13: Report - optional preparation appendix")
if OUTPUT_MODE == "full":
    for title in ["Source Read Summary", "Duplicate Key Diagnostics Before Deduplication",
                  "CORE 1 Holding Date Parse Audit", "CORE 1 Holding Snapshot Date Audit",
                  "CORE 2 Survey Timing and Duplicate Audit", "CORE 2 Holding Match and Zero Portfolio Provenance",
                  "Portfolio Cell Summary", "AUX 0 Sample Size Sequential Funnel", "CORE 3 Outcome Regression Sample Size"]:
        if title in TABLE_BUFFER:
            render_table("APPENDIX " + title, *TABLE_BUFFER[title])
else:
    ant_print_all(pd.Series(["Preparation appendix omitted: OUTPUT_MODE=compact"]), model_method="unique")
ant_print_all(pd.Series(["=== REPORT END ===", RUN_ID, SCRIPT_REVISION]), model_method="unique")
