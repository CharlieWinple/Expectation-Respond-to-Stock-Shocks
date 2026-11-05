# === CELL 1: Imports and output helpers ===
"""Owner and employee questionnaire duration diagnostic for the Ant platform."""

import gc
import time

import numpy as np
import pandas as pd

from marvel.AntPrint import ant_read_data, ant_print_all


TABLE_BUFFER = {}
MESSAGE_BUFFER = []
STAGE_TIMES = []
STAGE_STARTED = time.perf_counter()
STAGE_NAME = "setup"


def emit(lines):
    if isinstance(lines, str):
        lines = [lines]
    MESSAGE_BUFFER.extend(str(x) for x in lines)


def section(title):
    global STAGE_STARTED, STAGE_NAME
    now = time.perf_counter()
    STAGE_TIMES.append([STAGE_NAME, now - STAGE_STARTED])
    STAGE_STARTED, STAGE_NAME = now, title
    MESSAGE_BUFFER.append(title)


def fmt_int(x):
    return "-" if pd.isna(x) else f"{int(x):,d}"


def fmt_float(x, nd=4):
    return "-" if pd.isna(x) else f"{float(x):.{nd}f}"


def emit_table(title, columns, rows):
    """Buffer aggregate summaries; all output is in the final cell."""
    TABLE_BUFFER[title] = (list(columns), [list(row) for row in rows])


# === CELL 2: Adjustable settings ===

######### CONFIGURE START ###########
SCRIPT_REVISION = "sme_duration_diagnostic_v1"
RUN_ID = "owner_employee_duration_all_holdings"
WAVES = ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"]

SE_TYPE = "cluster_user"  # Required for this formal workflow.
OUTPUT_MODE = "compact"  # Preparation audit compatibility; final report is complete.
TIMING_RULE = "post_window_only"  # audit_only shows timing but blocks estimates
MIN_REG_N = 30  # Small samples are explicitly skipped.
HOLDING_BATCH_USERS = 5000

MIN_RETURN_COVERAGE = 0.999999
MIN_CONTROL_COVERAGE = 0.999999
MIN_CONTROL_MONTHS = 12

KEEP_ZERO_PORTFOLIO = True
INCLUDE_IMPUTED_ZERO = True
CORE_X_CHOICE = "passive_gain"
SHOCK_PORTFOLIO_SCOPE = "usable"  # raw, usable
ENFORCE_CONTROL_COMPLETENESS = True

N_SIZE_BIN = 10
N_RISK_BIN = 3
N_ERET_BIN = 3
CELL_RANK_SCOPE = "within_wave"
CELL_RANK_METHOD = "average"
ZERO_PORTFOLIO_CELL_MODE = "pooled_zero_within_wave"

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

TRAIT_CODING_ROWS = []
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
    "industry": {"2024q2": "v41", "2024q3": "v42", "2024q4": "v28", "2025q1": "v29", "2025q2": "v29"},
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

COLLEGE_ANSWERS = ["大学专科_高职高专_技师学院", "大学专科_专科_高职高专_技师学院", "大学本科", "研究生及以上"]
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


QUESTION_CODES = {
    "2024q3": ["v32", "v33", "v34", "v35", "v36"],
    "2024q4": ["v18", "v19", "v20", "v21", "v22"],
    "2025q1": ["v18", "v19", "v20", "v21", "v22"],
    "2025q2": ["v18", "v19", "v20", "v21", "v22"],
}
EDU_CODE = dict(zip(WAVES[1:], ["v39", "v25", "v26", "v26"]))
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
                 "大学专科_专科_高职高专_技师学院": 1., "大学专科_高职高专_技师学院": 1., "大学本科": 1., "研究生及以上": 1.}
MIXED_EDUCATION = "大学专科_高中_高职高专_技师学院"
# Maintained interpretation by the leading college label; exclusion check below.
EDUCATION_MAP[MIXED_EDUCATION] = 1.
EDUCATION_REFUSAL = ["不便透露", "不愿回答", "拒绝回答", "不确定", "不清楚"]


def get_survey_cols(wave):
    cols = list(SURVEY_BASE_COLS_BY_WAVE[wave])
    for y_name in Y_VARS:
        v_code = EXP_VCODES.get(y_name, {}).get(wave)
        if v_code is not None:
            cols.append(v_code)
    for trait_name in ["education", "firm_year", "registration", "employee_n", "industry"]:
        cols.append(TRAIT_VCODES[trait_name][wave])
    cols += ["v2", "v3", "v9", "v10", "v12"]
    if wave in QUESTION_CODES:
        cols += QUESTION_CODES[wave] + [EDU_CODE[wave]]
    if wave == "2024q4":
        cols += ["v174", "v217"]
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

    for label, count in education.loc[out["aer_bal_college"].isna() & out["sme_owner"].eq(1)].value_counts(dropna=False).items():
        TRAIT_CODING_ROWS.append([wave, "education_unmapped_or_missing", str(label), int(count)])
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
    df_wave[USER_COL] = clean_text(df_wave[USER_COL])
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
SHOCK_WINDOW_START_BY_WAVE = {}
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
        SHOCK_WINDOW_START_BY_WAVE[wave] = starts.iloc[0]
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
    # Four common employee waves, five owner waves. Preserve raw answers for quality.
    # fillna alone retains pandas BooleanDtype, rejected by older NumPy select.
    # Convert to native bool after resolving missing answers to False.
    nonowner = clean_text(svy.v1).eq("我不是小微经营者").fillna(False).astype(bool)
    explicit = clean_text(svy.v2).eq("作为小微经营户的雇员_帮助其收付款").fillna(False).astype(bool)
    working = clean_text(svy.v3).eq("我在工作").fillna(False).astype(bool)
    owner = svy.sme_owner.eq(1)
    employee = nonowner & (explicit | working) & (wave in QUESTION_CODES)
    svy["role"] = np.select([owner, employee], ["owner","employee"], default="other")
    svy["route"] = np.where(owner,"owner",np.where(explicit,"v2","v3"))
    if wave == "2024q4":
        versions = svy[["v168","v174","v217"]].apply(clean_text).notna()
        svy.loc[owner,"route"] = np.where(versions.sum(axis=1).eq(1),
            versions.idxmax(axis=1), "unknown_or_multiple")[owner]
    svy["anomaly"] = ((employee & explicit & clean_text(svy.v3).notna() & ~working)
                      | (owner & clean_text(svy.v10).notna())).astype(float)
    if wave == "2024q4":
        svy.loc[owner & versions.sum(axis=1).gt(1),"anomaly"] = 1.
    # Always-relevant core fields used as completeness proxies; no optional industry follow-ups.
    owner_core = [TRAIT_VCODES[k][wave] for k in ["firm_year","registration","industry"]]
    svy["core_blank"] = svy[owner_core].apply(clean_text).isna().mean(axis=1)
    svy.loc[employee,"core_blank"] = svy.loc[employee,["v9","v10","v12"]].apply(clean_text).isna().mean(axis=1)
    if wave in QUESTION_CODES:
        education = clean_text(svy[EDU_CODE[wave]])
        svy.loc[employee,"aer_bal_college"] = education[employee].map(EDUCATION_MAP)
        invalid_edu = employee & education.notna() & ~education.isin(EDUCATION_MAP) & ~education.isin(EDUCATION_REFUSAL)
        if invalid_edu.any():
            RUN_BLOCKERS.append(wave+"_unknown_employee_education")
        svy.loc[employee & ~svy.aer_bal_age.between(16,100),"aer_bal_age"] = np.nan
        for y,code,mapping in zip(["exp_gdp","exp_house","exp_cpi","exp_rate","exp_stock"],
                QUESTION_CODES[wave],[GDP,HOUSE,CPI,RATE,STOCK_Q3 if wave=="2024q3" else STOCK_LATER]):
            emp_raw = clean_text(svy[code])
            svy.loc[employee,y] = emp_raw[employee].map(mapping)
            raw = clean_text(svy[EXP_VCODES[y][wave]]).where(owner,emp_raw)
            unsure = raw.isin(["不确定","不清楚","不知道","不了解","无法判断"])
            svy["state_"+y] = np.select([raw.isna(),unsure,svy[y].notna()],
                                        ["blank","unsure","numeric"],default="other")
            if (employee & raw.notna() & ~raw.isin(UNKNOWN_ANSWERS) & svy[y].isna()).any():
                RUN_BLOCKERS.append(wave+"_unknown_employee_"+y)
    # Keep all survey rows until uniqueness is computed across roles.
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

# === CELL 6: Aggregate fund-level shock and controls to users ===

section("CELL 6: Aggregate shock and controls")

# Bound the holdings x 12 months expansion by processing owner batches.
user_parts = []
for wave in WAVES:
    needed_users = survey_panel.loc[survey_panel["wave"].eq(wave) & survey_panel["role"].isin(["owner","employee"]), USER_COL]
    month_holding = holding.loc[holding["month_p"].eq(WAVE_HOLDING_MONTH[wave]) & holding[USER_COL].isin(needed_users)]
    codes, owners = pd.factorize(month_holding[USER_COL], sort=False)
    for offset in range(0, len(owners), HOLDING_BATCH_USERS):
        batch = month_holding.loc[(codes >= offset) & (codes < offset + HOLDING_BATCH_USERS)]
        shock_user = aggregate_shock_to_user(shock, batch, wave)
        control_user = aggregate_control_to_user(control, batch, wave)
        user_wave = shock_user.merge(control_user, on=USER_COL, how="left", validate="one_to_one")
        user_wave["wave"] = wave
        user_parts.append(user_wave)
        del batch, shock_user, control_user, user_wave
    del month_holding, codes, owners
    gc.collect()
user_columns = [USER_COL, "wave", "portfolio_size_raw", "portfolio_size_usable",
    "portfolio_size", "return_coverage", "control_coverage", "control_min_coverage",
    "control_n_months", "portfolio_risk_12m", "expected_ret_12m", PASSIVE_RET_PREDICTOR,
    PASSIVE_GAIN_PREDICTOR, REALIZED_RETURN_PREDICTOR, REALIZED_GAIN_COL]
user_panel = pd.concat(user_parts, ignore_index=True) if user_parts else pd.DataFrame(columns=user_columns)
if not user_parts:
    RUN_BLOCKERS.append("no_owner_holdings_to_aggregate")
del user_parts, holding, shock, control
# Drop references to the large raw tables before regressions.
del portrait_raw, portrait_diag, portrait, addon_2024q2
for temporary in ["wave_holding", "wave_shock", "df_wave", "svy"]:
    globals().pop(temporary, None)
gc.collect()

# === CELL 7: Define base sample and portfolio cells ===

section("CELL 7: Define sample and portfolio cells")

df = survey_panel.merge(user_panel, on=[USER_COL, "wave"], how="left", validate="many_to_one")
del survey_panel, user_panel
gc.collect()

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

df["shock_window_end"] = pd.to_datetime(
    df["wave"].map(SHOCK_WINDOW_END_BY_WAVE), errors="coerce"
)
df["timing_after_window"] = df["submit_dt"].gt(df["shock_window_end"])
df["sample_timing"] = (
    df["timing_after_window"] if TIMING_RULE == "post_window_only"
    else pd.Series(True, index=df.index)
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

# === CELL 8: Duration diagnostics and aggregate plotting data ===
MACRO = ["exp_gdp","exp_house","exp_cpi","exp_rate","exp_stock"]
OWNER_CONTROLS = ["aer_bal_age","aer_bal_college","aer_bal_firm_age","aer_bal_company",
                  "portrait_gender","city_level_from_yicai","survey_industry"]
PERSON = ["aer_bal_age","aer_bal_college","portrait_gender","city_level_from_yicai"]
BANDS = ["lt60","60_119","120_179","ge180","missing"]
CUTS = [0,60,120,180]
TABLES = {}


def table(key, headers, row):
    TABLES.setdefault(key,(headers.split(),[]))[1].append(row)


def keep_time(g, cutoff):
    return g.seconds.isna() | g.seconds.ge(cutoff)


def mean_or_na(values):
    return values.mean() if len(values) else np.nan


def distribution(g, role, scope, sample):
    observed = g.seconds.dropna()
    quantiles = observed.quantile([.1,.25,.5,.75,.9]).tolist() if len(observed) else [np.nan]*5
    table("quantiles","role scope sample N U timed missing p10 p25 p50 p75 p90",
          [role,scope,sample,len(g),g[USER_COL].nunique(),len(observed),len(g)-len(observed),*quantiles])
    # Left closed bins; the last bin retains the complete upper tail.
    edges = list(range(0,301,15)) + [360,480,600,900,1800,np.inf]
    counts = np.histogram(observed.to_numpy(dtype=float),bins=edges)[0]
    cumulative = 0
    for lo,hi,n in zip(edges,edges[1:],counts):
        cumulative += n
        denom = len(observed)
        table("hist","role scope sample lo hi N timed share cum_share",
              [role,scope,sample,lo,hi if np.isfinite(hi) else "inf",n,denom,
               n/denom if denom else np.nan,cumulative/denom if denom else np.nan])


def quality(g, role, scope, sample, wave="all", route="all"):
    for band in BANDS:
        h = g.loc[g.band.eq(band)]
        table("quality","role scope sample wave route band N U core_fields blank_fields flags",
              [role,scope,sample,wave,route,band,len(h),h[USER_COL].nunique(),3*len(h),
               int(round(3*h.core_blank.sum())),int(h.anomaly.sum())])


def contrast(g,role,scope,sample,low,high,metric,adjust):
    h = g.loc[g.band.isin([low,high]),[USER_COL,"band","stratum",metric]].dropna().copy()
    if adjust and len(h):
        overlap = h.groupby("stratum").band.transform("nunique").eq(2)
        h = h.loc[overlap].copy()
    x = h.band.eq(low).astype(float)
    y = h[metric]
    strata = h.stratum if adjust else pd.Series("all",index=h.index)
    x = x-x.groupby(strata).transform("mean")
    y = y-y.groupby(strata).transform("mean")
    n,u,k = len(h),h[USER_COL].nunique(),strata.nunique()
    ss = x.dot(x)
    b = se = left = right = np.nan
    status = "no_overlap_or_df"
    if ss>0 and u>1 and n>k+1:
        b = x.dot(y)/ss
        scores = (x*(y-b*x)).groupby(h[USER_COL]).sum()
        se = np.sqrt(u/(u-1)*(n-1)/(n-k-1)*scores.dot(scores))/ss
        status = "zero_variance" if se==0 else "ok"
        if se>0:
            left,right = b-1.96*se,b+1.96*se
    table("differences","role scope sample low high metric adjust N U strata diff_pp se_pp lo_pp hi_pp status",
          [role,scope,sample,low,high,metric,"wave_route" if adjust else "raw",n,u,k,
           100*b,100*se,100*left,100*right,status])


def summarize(g,role,scope):
    controls = OWNER_CONTROLS if role=="owner" else PERSON
    outcomes = Y_VARS if role=="owner" else MACRO
    unique = g[USER_COL].notna() & g.unique_user_wave
    a = g.loc[unique]
    b = a.loc[a.candidate_B]
    c = b.loc[b[controls].notna().all(axis=1)]
    for band in BANDS:
        h=g.loc[g.band.eq(band)]
        table("audit","role scope band rawN missingID duplicateUserWave conflictingRoleRows duplicateSubmit multipleTime malformedTime",
              [role,scope,band,len(h),int(h[USER_COL].isna().sum()),int((~h.unique_user_wave).sum()),
               int(h.conflicting_role.sum()),int(h.duplicate_submit.sum()),int(h.answer_seconds_n_matches.gt(1).sum()),int(h.malformed_time.sum())])
    for sample,data in [("A",a),("B",b)]:
        distribution(data,role,scope,sample)
        quality(data,role,scope,sample)
        for (wave,route),sub in data.groupby(["wave","route"]):
            quality(sub,role,scope,sample,wave,route)
        # Owner 2024q2 addon coverage and random module assignment do not identify skipped items.
        comparable = data.loc[data.wave.ne("2024q2")]
        for band in BANDS:
            h=comparable.loc[comparable.band.eq(band)]
            for y in MACRO:
                counts=h["state_"+y].value_counts()
                table("items","role scope sample band item N numeric unsure blank_or_unshown other",
                      [role,scope,sample,band,y,len(h),*[int(counts.get(k,0)) for k in
                       ["numeric","unsure","blank","other"]]])
        pairs = [("lt60","60_119"),("60_119","120_179"),("120_179","ge180")]
        for low,high in pairs:
            for metric in ["core_blank","anomaly"]:
                for adjust in [False,True]:
                    contrast(data,role,scope,sample,low,high,metric,adjust)
    for cutoff in CUTS:
        for stage,data in [("A",a),("B",b),("controls",c)]+[(y,c.loc[c[y].notna()]) for y in outcomes]:
            kept=data.loc[keep_time(data,cutoff)]
            table("loss","role scope stage seconds N0 U0 N U lostN lostU",
                  [role,scope,stage,cutoff,len(data),data[USER_COL].nunique(),len(kept),
                   kept[USER_COL].nunique(),len(data)-len(kept),data[USER_COL].nunique()-kept[USER_COL].nunique()])
        kept=b.loc[keep_time(b,cutoff)]
        table("composition","role scope seconds N ageN mean_age eduN college_share gainN mean_gain positive median_pos_RMB recorded0 unmatched0",
              [role,scope,cutoff,len(kept),kept.aer_bal_age.count(),mean_or_na(kept.aer_bal_age),
               kept.aer_bal_college.count(),mean_or_na(kept.aer_bal_college),kept.passive_gain.count(),
               mean_or_na(kept.passive_gain),int(kept.recorded_positive_portfolio.sum()),
               kept.loc[kept.recorded_positive_portfolio,"portfolio_size_raw"].median(),
               int(kept.recorded_zero_portfolio.sum()),int(kept.imputed_zero_portfolio.sum())])
        for trait in ["wave","route","city_level_from_yicai","portrait_gender","holding_type","age_band","aer_bal_college"]:
            for level,sub in b.groupby(trait,dropna=False,observed=True):
                n_keep = int(keep_time(sub,cutoff).sum())
                table("retention","role scope seconds trait level N kept share",
                      [role,scope,cutoff,trait,level,len(sub),n_keep,n_keep/len(sub)])


df["seconds"] = df.answer_seconds.where(np.isfinite(df.answer_seconds))
df["malformed_time"] = df.extro_info.astype("string").str.contains("answerSeconds",na=False) & df.seconds.isna()
df["band"] = pd.cut(df.seconds,[-np.inf,60,120,180,np.inf],right=False,labels=BANDS[:4]).astype("string").fillna("missing")
df["stratum"] = df.wave.astype(str)+"|"+df.route
df["conflicting_role"] = df.groupby([USER_COL,"wave"]).role.transform("nunique").gt(1)
submit=clean_text(df.submit_id)
df["duplicate_submit"] = submit.notna() & pd.DataFrame({"wave":df.wave,"s":submit}).duplicated(keep=False)
df["candidate_B"] = (df.sample_timing & df.sample_portfolio_rule & df.sample_core_x_nonmissing &
                     df.sample_return_complete & df.sample_control_complete & df.sample_cell_inputs)
df["holding_type"] = np.select([df.recorded_positive_portfolio,df.recorded_zero_portfolio,
                                df.imputed_zero_portfolio],["positive","recorded0","unmatched0"],default="other")
df["age_band"] = pd.cut(df.aer_bal_age,[-np.inf,30,45,60,np.inf],right=False,
                        labels=["lt30","30_44","45_59","ge60"]).astype("string").fillna("missing")
if not RUN_BLOCKERS:
    for role in ["owner","employee"]:
        group=df.loc[df.role.eq(role)]
        summarize(group.loc[group.wave.ne("2024q2")],role,"common4")
        if role=="owner":
            summarize(group,role,"formal5")


# === CELL 9: Data report 1 of 4 ===
def display_value(v):
    if pd.isna(v):
        return "NA"
    return format(v,".6g") if isinstance(v,(float,np.floating)) else str(v)


lines=["DURATION DIAGNOSTIC BEGIN | "+SCRIPT_REVISION,
       "status="+("BLOCKED" if RUN_BLOCKERS else "COMPLETED"),
       "issues="+",".join(sorted(set(RUN_BLOCKERS))),
       "A=unique survey; B=eligible all holdings before controls/Y; thresholds inclusive; missing time retained.",
       "Hist [lo,hi), share and cumulative share among timed only. Items exclude owner q2 addon.",
       "Core blank denominators: three core questions per record. Flags are routing inconsistencies.",
       "Difference=low minus high; percentage points; user-clustered normal 95% CI."]
for name,(headers,rows) in TABLES.items():
    lines.append(name+" | "+" | ".join(headers))
    for i,row in enumerate(rows,1):
        lines.append(name+"."+str(i)+" | "+" | ".join(display_value(v) for v in row))
lines.append("DURATION DIAGNOSTIC END")
blocks=[[] for _ in range(4)]
total=sum(len(t.encode("utf-8"))+12 for t in lines)
block=0
used=0
for line in lines:
    if used>=total/4 and block<3:
        block+=1
        used=0
    blocks[block].append(line)
    used+=len(line.encode("utf-8"))+12
budget_ok=all(sum(len(t.encode("utf-8"))+12 for t in part)+512*((len(part)+39)//40)<=44000 for part in blocks)


def emit_block(k):
    if budget_ok:
        for start in range(0,len(blocks[k]),40):
            batch=blocks[k][start:start+40]
            ant_print_all(pd.Series([f"Duration block {k+1}/4 lines {start+1}-{start+len(batch)}/{len(blocks[k])}"]+batch),model_method="unique")
    elif k==0:
        ant_print_all(pd.Series(["Duration report exceeds budget; revise output layout."]),model_method="unique")


emit_block(0)

# === CELL 10: Data report 2 of 4 ===
emit_block(1)

# === CELL 11: Data report 3 of 4 ===
emit_block(2)

# === CELL 12: Data report 4 of 4 ===
emit_block(3)
