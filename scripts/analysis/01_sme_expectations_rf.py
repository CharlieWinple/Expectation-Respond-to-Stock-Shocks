# === CELL 1: Imports and output helpers ===
"""SME-owner expectations reduced-form regression for the Ant platform."""

import gc
import hashlib

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from marvel.AntPrint import ant_read_data, ant_print_all
from marvel.AntPrint.sandbox.global_constant import print_envir

print_envir()


def emit(lines):
    if isinstance(lines, str):
        lines = [lines]
    ant_print_all(pd.Series([str(x) for x in lines]), model_method="unique")


def section(title):
    emit(["", "=" * 78, title, "=" * 78])


def fmt_int(x):
    return "-" if pd.isna(x) else f"{int(x):,d}"


def fmt_float(x, nd=4):
    return "-" if pd.isna(x) else f"{float(x):.{nd}f}"


def fmt_coef_stars(coef, p):
    if pd.isna(coef):
        return "-"
    stars = ""
    if not pd.isna(p):
        if p < 0.01:
            stars = "***"
        elif p < 0.05:
            stars = "**"
        elif p < 0.10:
            stars = "*"
    return f"{float(coef):.5f}{stars}"


def fmt_balance_flag(p):
    if pd.isna(p):
        return "-"
    return "FAIL" if float(p) < 0.05 else "ok"


def emit_table(title, columns, rows):
    section(f"{RUN_ID} | {title}")
    rows = [[str(v) for v in row] for row in rows]
    widths = [len(str(c)) for c in columns]
    for row in rows:
        widths = [max(w, len(v)) for w, v in zip(widths, row)]

    def line(values):
        return "  " + "  ".join(str(v).ljust(w) for v, w in zip(values, widths))

    out = [line(columns), "  " + "  ".join("-" * w for w in widths)]
    out += [line(row) for row in rows]
    emit(out)


# === CELL 2: Adjustable settings ===

######### CONFIGURE START ###########
SCRIPT_REVISION = "sme_rf_audited_v1"
RUN_ID = "r7_passive_gain_w5_positive"
RUN_PRESETS = {
    "r6_passive_gain_w5_keepzero": {
        "waves": ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"],
        "core_x_choice": "passive_gain", "keep_zero_portfolio": True,
    },
    "r7_passive_gain_w5_positive": {
        "waves": ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"],
        "core_x_choice": "passive_gain", "keep_zero_portfolio": False,
    },
    "r8_passive_gain_w4_drop2024q3_keepzero": {
        "waves": ["2024q2", "2024q4", "2025q1", "2025q2"],
        "core_x_choice": "passive_gain", "keep_zero_portfolio": True,
    },
    "r9_passive_return_w5_positive": {
        "waves": ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"],
        "core_x_choice": "passive_return", "keep_zero_portfolio": False,
    },
}
INVALID_RUN_ID = RUN_ID not in RUN_PRESETS
if INVALID_RUN_ID:
    emit([f"Unknown RUN_ID={RUN_ID}; using R7 settings only to complete diagnostics."])
    RUN_ID = "r7_passive_gain_w5_positive"
RUN_CONFIG = RUN_PRESETS[RUN_ID]
WAVES = list(RUN_CONFIG["waves"])

SE_TYPE = "cluster_user"  # cluster_user or HC1
OUTPUT_MODE = "compact"  # compact or full
TIMING_RULE = "post_window_only"  # audit_only shows timing but blocks estimates
MIN_REG_N = 30
ANSWER_SECONDS_MIN = 180
MIN_RETURN_COVERAGE = 0.999999
MIN_CONTROL_COVERAGE = 0.999999
MIN_CONTROL_MONTHS = 12

KEEP_ZERO_PORTFOLIO = RUN_CONFIG["keep_zero_portfolio"]
CORE_X_CHOICE = RUN_CONFIG["core_x_choice"]
SHOCK_PORTFOLIO_SCOPE = "usable"  # raw, usable
ENFORCE_CONTROL_COMPLETENESS = True

N_SIZE_BIN = 5
N_RISK_BIN = 3
N_ERET_BIN = 3
CELL_RANK_SCOPE = "within_wave"
CELL_RANK_METHOD = "average"
ZERO_PORTFOLIO_CELL_MODE = "separate_recorded_and_imputed"

CELL_FE_NAMES = ["analysis_portfolio_cell"]
# Positive-portfolio cells use wave-specific size x risk x expected-return ranks.
# Recorded-zero and imputed-zero portfolios enter separate wave-specific cells.
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
REG_SPECS = [
    {
        "name": "cell_fe",
        "label": "Y+X+cell FE",
        "fe_names": CELL_FE_NAMES,
        "control_names": [],
    },
    {
        "name": "cell_other_fe",
        "label": "Y+X+cell+other FE",
        "fe_names": CELL_FE_NAMES + OTHER_FE_NAMES,
        "control_names": [],
    },
    {
        "name": "cell_other_fe_controls",
        "label": "Y+X+cell+other FE+controls",
        "fe_names": CELL_FE_NAMES + OTHER_FE_NAMES,
        "control_names": CONTROL_NAMES,
    },
]
MAIN_SPEC_NAME = "cell_other_fe_controls"
REG_FE_NAMES = list(dict.fromkeys(name for spec in REG_SPECS for name in spec["fe_names"]))
REG_CONTROL_NAMES = list(dict.fromkeys(
    name for spec in REG_SPECS for name in spec["control_names"]
))

RUN_BALANCE_CHECKS = True
BALANCE_Y_VARS = None  # None means all Y_VARS after Y_VARS is defined.
BALANCE_FE_NAMES = CELL_FE_NAMES + OTHER_FE_NAMES
BALANCE_TEST_VARS = [
    "aer_bal_age", "aer_bal_college", "aer_bal_firm_age",
    "aer_bal_company", "aer_bal_employee_n",
]
######### CONFIGURE END ###########

# table names
SHOCK_TABLE = "shock_panel_v2"
PORT_CONTROL_TABLE = "ctrl_monthly_panel"

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
CORE_X_BY_CHOICE = {
    "passive_return": PASSIVE_RET_PREDICTOR,
    "passive_gain": PASSIVE_GAIN_PREDICTOR,
    "realized_return": REALIZED_RETURN_PREDICTOR,
    "realized_gain": REALIZED_GAIN_COL,
}
CORE_X_VAR = CORE_X_BY_CHOICE.get(CORE_X_CHOICE)
if CORE_X_VAR is None:
    emit([
        f"Invalid CORE_X_CHOICE={CORE_X_CHOICE}; fallback to passive_return.",
        "Valid CORE_X_CHOICE values: passive_return, passive_gain, realized_return, realized_gain.",
    ])
    CORE_X_CHOICE = "passive_return"
    CORE_X_VAR = CORE_X_BY_CHOICE[CORE_X_CHOICE]

if SHOCK_PORTFOLIO_SCOPE not in ["raw", "usable"]:
    emit([
        f"Invalid SHOCK_PORTFOLIO_SCOPE={SHOCK_PORTFOLIO_SCOPE}; fallback to raw.",
        "Valid SHOCK_PORTFOLIO_SCOPE values: raw, usable.",
    ])
    SHOCK_PORTFOLIO_SCOPE = "raw"

DIAG_ROWS = []
ADDON_UNMAPPED_ROWS = []
RUN_BLOCKERS = []
if INVALID_RUN_ID:
    RUN_BLOCKERS.append("invalid_RUN_ID")

Y_VARS = [
    "exp_stock", "exp_gdp", "exp_cpi", "exp_house", "exp_rate",
    "exp_env_local", "exp_rev", "exp_market",
    "exp_price", "exp_wage", "exp_input_cost",
]
if BALANCE_Y_VARS is None:
    BALANCE_Y_VARS = list(Y_VARS)

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


def merge_2024q2_addon(df, addon):
    out = df.copy()
    keep_cols = [ADDON_2024Q2_KEY] + list(ADDON_2024Q2_MACRO_COLS)
    addon_keep = addon[keep_cols].drop_duplicates(ADDON_2024Q2_KEY).copy()
    out[ADDON_2024Q2_KEY] = out[ADDON_2024Q2_KEY].astype("string")
    addon_keep[ADDON_2024Q2_KEY] = addon_keep[ADDON_2024Q2_KEY].astype("string")
    survey_keys = set(out[ADDON_2024Q2_KEY].dropna().unique())
    addon_keys = set(addon_keep[ADDON_2024Q2_KEY].dropna().unique())
    n_key_overlap = len(survey_keys.intersection(addon_keys))
    out = out.merge(addon_keep, on=ADDON_2024Q2_KEY, how="left", validate="many_to_one")
    for source_col, y_name in ADDON_2024Q2_MACRO_COLS.items():
        raw = clean_text(out[source_col])
        mapping = EXP_MAPPING[y_name]
        out[y_name] = raw.map(mapping)
        unmapped = raw.loc[raw.notna() & ~raw.isin(mapping.keys())]
        for value, count in unmapped.value_counts().head(20).items():
            ADDON_UNMAPPED_ROWS.append([y_name, value, int(count)])
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


def build_portfolio_cells(df):
    out = df.copy()
    positive = out["portfolio_size"].gt(0)
    recorded_zero = out["recorded_zero_portfolio"].fillna(False)
    imputed_zero = out["imputed_zero_portfolio"].fillna(False)

    out["portfolio_cell_status"] = "zero_other"
    out.loc[recorded_zero, "portfolio_cell_status"] = "zero_recorded"
    out.loc[imputed_zero, "portfolio_cell_status"] = "zero_imputed"
    out.loc[positive, "portfolio_cell_status"] = "positive"

    out = add_within_wave_rank_bin(
        out, "portfolio_size", N_SIZE_BIN, "analysis_size_bin", positive
    )
    out = add_within_wave_rank_bin(
        out, "portfolio_risk_12m", N_RISK_BIN, "analysis_risk_bin", positive
    )
    out = add_within_wave_rank_bin(
        out, "expected_ret_12m", N_ERET_BIN, "analysis_eret_bin", positive
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
        out.loc[zero_rows, "wave"].astype("string") + "_Z_"
        + out.loc[zero_rows, "portfolio_cell_status"].astype("string")
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


def fill_zero_portfolio_rows(df):
    out = df.copy()
    zero_cols = [
        "portfolio_size", "shock_matched_holding", "shock_weighted_pp",
        "portfolio_size_raw", "portfolio_size_usable", "shock_usable_holding",
        "n_funds", "n_shock_matched", "n_shock_usable",
        "return_coverage", PASSIVE_RET_PREDICTOR, PASSIVE_GAIN_PREDICTOR,
        REALIZED_GAIN_COL, "realized_gain_usable", REALIZED_RETURN_PREDICTOR, "control_coverage",
        "control_min_coverage", "control_n_months", "portfolio_risk_12m",
        "expected_ret_12m", "n_control_matched",
    ]
    initial_portfolio = (
        out["portfolio_size_raw"] if "portfolio_size_raw" in out.columns else out["portfolio_size"]
    )
    zero_portfolio = initial_portfolio.isna() | initial_portfolio.eq(0)
    for col in zero_cols:
        if col in out.columns:
            out.loc[zero_portfolio, col] = 0
    out.loc[zero_portfolio, "return_coverage"] = 1
    out.loc[zero_portfolio, "control_coverage"] = 1
    out.loc[zero_portfolio, "control_min_coverage"] = 1
    out.loc[zero_portfolio, "control_n_months"] = MIN_CONTROL_MONTHS
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
    """Use one complete-case sample for every specification of an outcome."""
    extra_cols = extra_cols or []
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
    return run.replace([np.inf, -np.inf], np.nan).dropna(subset=cols)


def run_rf(df, y_name, spec=None):
    spec = spec or REG_SPECS[-1]
    spec_name = spec.get("name", "spec")
    fe_names = enabled_existing(spec.get("fe_names", []), df)
    control_names = enabled_existing(spec.get("control_names", []), df)
    run = regression_sample(df, y_name)
    fe_terms = []
    fe_diag = {}
    for fe_name in fe_names:
        n_fe = run[fe_name].nunique(dropna=True)
        fe_diag[f"{fe_name}_fe"] = "yes" if n_fe >= 2 else "no"
        fe_diag[f"{fe_name}_n"] = n_fe
        if n_fe >= 2:
            fe_terms.append(f"C({fe_name})")
    skip_note = ""
    if RUN_BLOCKERS:
        skip_note = "blocked_integrity_gate"
    elif len(run) < MIN_REG_N:
        skip_note = "skip_n"
    elif run[CORE_X_VAR].nunique() < 2:
        skip_note = "no_X_variation"
    elif SE_TYPE == "cluster_user" and run[USER_COL].nunique() < 2:
        skip_note = "too_few_user_clusters"
    if skip_note:
        summary = {
            "spec": spec_name, "Y": y_name, "n_obs": len(run), "beta": np.nan, "se": np.nan,
            "t": np.nan, "p": np.nan, "R2": np.nan, "note": skip_note,
            "n_users": run[USER_COL].nunique() if USER_COL in run else 0,
            "core_x": CORE_X_VAR,
        }
        summary.update(fe_diag)
        detail = [
            {
                "spec": spec_name, "Y": y_name, "variable": name,
                "coef": np.nan, "se": np.nan,
                "t": np.nan, "p": np.nan, "note": skip_note,
            }
            for name in [CORE_X_VAR] + control_names
        ]
        return summary, detail
    formula = f"{y_name} ~ " + " + ".join([CORE_X_VAR] + fe_terms + control_names)
    ols = smf.ols(formula, data=run)
    if SE_TYPE == "cluster_user":
        model = ols.fit(
            cov_type="cluster", cov_kwds={"groups": run[USER_COL].astype(str)}
        )
    else:
        model = ols.fit(cov_type=SE_TYPE)
    summary = {
        "spec": spec_name,
        "Y": y_name,
        "n_obs": int(model.nobs),
        "n_users": int(run[USER_COL].nunique()),
        "beta": float(model.params.get(CORE_X_VAR, np.nan)),
        "se": float(model.bse.get(CORE_X_VAR, np.nan)),
        "t": float(model.tvalues.get(CORE_X_VAR, np.nan)),
        "p": float(model.pvalues.get(CORE_X_VAR, np.nan)),
        "R2": float(model.rsquared),
        "note": "" if np.isfinite(model.bse.get(CORE_X_VAR, np.nan)) else "nonfinite_se",
        "core_x": CORE_X_VAR,
    }
    summary.update(fe_diag)
    detail = []
    for name in [CORE_X_VAR] + control_names:
        detail.append({
            "spec": spec_name,
            "Y": y_name,
            "variable": name,
            "coef": float(model.params.get(name, np.nan)),
            "se": float(model.bse.get(name, np.nan)),
            "t": float(model.tvalues.get(name, np.nan)),
            "p": float(model.pvalues.get(name, np.nan)),
            "note": "",
        })
    return summary, detail


def cell_diagnostics(df, y_name, spec=None):
    spec = spec or REG_SPECS[-1]
    run = regression_sample(df, y_name)
    if len(run) == 0 or "analysis_portfolio_cell" not in run.columns:
        return {
            "Y": y_name, "n": len(run), "cells": np.nan,
            "singleton_cells": np.nan, "share_obs_cell_lt5": np.nan,
            "share_obs_no_X_variation": np.nan, "cell_p10": np.nan,
            "cell_p50": np.nan, "cell_p90": np.nan,
            "within_cell_X_sd": np.nan, "raw_X_sd": np.nan,
        }
    sizes = run.groupby("analysis_portfolio_cell", observed=True).size()
    unique_x = run.groupby("analysis_portfolio_cell", observed=True)[CORE_X_VAR].nunique()
    within_x = run[CORE_X_VAR] - run.groupby(
        "analysis_portfolio_cell", observed=True
    )[CORE_X_VAR].transform("mean")
    return {
        "Y": y_name,
        "n": len(run),
        "cells": len(sizes),
        "singleton_cells": int(sizes.eq(1).sum()),
        "share_obs_cell_lt5": float(sizes.loc[sizes.lt(5)].sum() / len(run)),
        "share_obs_no_X_variation": float(sizes.loc[unique_x.le(1)].sum() / len(run)),
        "cell_p10": float(sizes.quantile(0.1)),
        "cell_p50": float(sizes.quantile(0.5)),
        "cell_p90": float(sizes.quantile(0.9)),
        "within_cell_X_sd": float(within_x.std()),
        "raw_X_sd": float(run[CORE_X_VAR].std()),
    }


def conditional_shock_variation(df, y_name, spec=None):
    spec = spec or REG_SPECS[-1]
    run = regression_sample(df, y_name)
    if len(run) < MIN_REG_N or run[CORE_X_VAR].nunique() < 2:
        return {
            "Y": y_name, "n": len(run), "raw_X_sd": np.nan,
            "residual_X_sd": np.nan, "residual_SS_share": np.nan,
            "df_resid": np.nan, "note": "insufficient_n_or_variation",
        }
    fe_names = enabled_existing(spec.get("fe_names", []), run)
    control_names = enabled_existing(spec.get("control_names", []), run)
    terms = [f"C({name})" for name in fe_names if run[name].nunique() > 1]
    terms += control_names
    rhs = " + ".join(terms) or "1"
    fit = smf.ols(f"{CORE_X_VAR} ~ {rhs}", data=run).fit()
    raw_ss = float(((run[CORE_X_VAR] - run[CORE_X_VAR].mean()) ** 2).sum())
    residual_ss = float((fit.resid ** 2).sum())
    out = {
        "Y": y_name,
        "n": len(run),
        "raw_X_sd": float(run[CORE_X_VAR].std()),
        "residual_X_sd": float(fit.resid.std()),
        "residual_SS_share": float(residual_ss / raw_ss) if raw_ss > 0 else np.nan,
        "df_resid": float(fit.df_resid),
        "note": "",
    }
    del fit
    return out


def lottery_balance_test(df, y_name, trait):
    if trait not in df.columns:
        return {
            "Y": y_name, "trait": trait, "n": 0, "beta": np.nan,
            "se": np.nan, "p": np.nan, "std_effect": np.nan,
            "note": "missing_trait",
        }
    fe_names = enabled_existing(BALANCE_FE_NAMES, df)
    run = regression_sample(df, y_name, extra_cols=[trait])
    if len(run) < MIN_REG_N or run[trait].nunique() < 2 or run[CORE_X_VAR].nunique() < 2:
        return {
            "Y": y_name, "trait": trait, "n": len(run), "beta": np.nan,
            "se": np.nan, "p": np.nan, "std_effect": np.nan,
            "note": "insufficient_n_or_variation",
        }
    terms = [f"C({name})" for name in fe_names if run[name].nunique() > 1]
    rhs = " + ".join(terms) or "1"
    trait_resid = smf.ols(f"{trait} ~ {rhs}", data=run).fit().resid
    if float((trait_resid ** 2).sum()) <= 1e-12 * max(1.0, float((run[trait] ** 2).sum())):
        return {
            "Y": y_name, "trait": trait, "n": len(run), "beta": np.nan,
            "se": np.nan, "p": np.nan, "std_effect": np.nan,
            "note": "no_conditional_trait_variation",
        }
    balance_ols = smf.ols(f"{CORE_X_VAR} ~ {trait} + {rhs}", data=run)
    if SE_TYPE == "cluster_user":
        fit = balance_ols.fit(
            cov_type="cluster", cov_kwds={"groups": run[USER_COL].astype(str)}
        )
    else:
        fit = balance_ols.fit(cov_type=SE_TYPE)
    beta = float(fit.params.get(trait, np.nan))
    std_effect = beta * float(trait_resid.std()) / float(run[CORE_X_VAR].std())
    out = {
        "Y": y_name,
        "trait": trait,
        "n": len(run),
        "beta": beta,
        "se": float(fit.bse.get(trait, np.nan)),
        "p": float(fit.pvalues.get(trait, np.nan)),
        "std_effect": float(std_effect),
        "note": "X_on_trait_plus_FE",
    }
    del fit
    return out


def normalize_rf_output(y_name, output):
    if isinstance(output, tuple) and len(output) == 2:
        summary, detail = output
    elif isinstance(output, dict):
        summary = output
        detail = []
    else:
        summary = {
            "spec": "unknown", "Y": y_name, "n_obs": np.nan, "beta": np.nan, "se": np.nan,
            "t": np.nan, "p": np.nan, "R2": np.nan,
            "note": "invalid_run_output",
        }
        detail = []

    if not isinstance(summary, dict):
        summary = {
            "spec": "unknown", "Y": y_name, "n_obs": np.nan, "beta": np.nan, "se": np.nan,
            "t": np.nan, "p": np.nan, "R2": np.nan,
            "note": "invalid_summary",
        }
    summary.setdefault("spec", "unknown")
    summary.setdefault("Y", y_name)
    summary.setdefault("n_obs", np.nan)
    summary.setdefault("n_users", np.nan)
    summary.setdefault("beta", np.nan)
    summary.setdefault("se", np.nan)
    summary.setdefault("t", np.nan)
    summary.setdefault("p", np.nan)
    summary.setdefault("R2", np.nan)
    summary.setdefault("note", "")
    summary.setdefault("core_x", CORE_X_VAR)
    for fe_name in REG_FE_NAMES:
        summary.setdefault(f"{fe_name}_fe", "no")
        summary.setdefault(f"{fe_name}_n", np.nan)

    if not isinstance(detail, list) or len(detail) == 0:
        detail = [
            {
                "spec": summary["spec"],
                "Y": y_name,
                "variable": CORE_X_VAR,
                "coef": summary["beta"],
                "se": summary["se"],
                "t": summary["t"],
                "p": summary["p"],
                "note": summary["note"],
            }
        ]
    for row in detail:
        row.setdefault("spec", summary["spec"])
        row.setdefault("Y", y_name)
        row.setdefault("variable", "")
        row.setdefault("coef", np.nan)
        row.setdefault("se", np.nan)
        row.setdefault("t", np.nan)
        row.setdefault("p", np.nan)
        row.setdefault("note", "")

    return summary, detail


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
dedup_diag_rows.append(duplicate_key_diagnostics(
    addon_2024q2,
    "2024q2_addon",
    [ADDON_2024Q2_KEY],
    list(ADDON_2024Q2_MACRO_COLS),
))
read_rows.append(["2024q2", "addon", addon_2024q2.shape[0], addon_2024q2.shape[1]])

shock = ant_read_data(
    SHOCK_TABLE,
    cols=[
        FUND_COL_PANEL, WAVE_COL, SHOCK_RET_PP_COL, SHOCK_USABLE_COL,
        SHOCK_WINDOW_START_COL, SHOCK_WINDOW_END_COL,
    ],
).copy()
shock = prepare_panel_keys(shock)
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
    cols=[FUND_COL_PANEL, WAVE_COL, CONTROL_MONTH_COL, CONTROL_MONTHLY_RET_COL],
).copy()
control = prepare_panel_keys(control)
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
            fmt_int(row["addon_submit_id"]),
            fmt_int(row["submit_id_overlap"]),
            fmt_int(row["exp_gdp_nonmiss"]),
            fmt_int(row["exp_cpi_nonmiss"]),
            fmt_int(row["exp_house_nonmiss"]),
            fmt_int(row["exp_rate_nonmiss"]),
        ])
    emit_table(
        "2024q2 Addon Merge Diagnostics",
        [
            "wave", "survey_keys", "addon_keys", "key_overlap",
            "gdp_nonmiss", "cpi_nonmiss", "house_nonmiss", "rate_nonmiss",
        ],
        addon_diag_rows,
    )

if len(ADDON_UNMAPPED_ROWS) > 0:
    emit_table(
        "2024q2 Addon Unmapped Values",
        ["Y", "raw_value", "count"],
        [[y_name, value, fmt_int(count)] for y_name, value, count in ADDON_UNMAPPED_ROWS],
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
    df = fill_zero_portfolio_rows(df)

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
    df["portfolio_size"].ge(0) if KEEP_ZERO_PORTFOLIO else df["portfolio_size"].gt(0)
)
df["sample_core_x_nonmissing"] = df[CORE_X_VAR].notna()
df["sample_return_complete"] = df["return_coverage"].ge(MIN_RETURN_COVERAGE)
df["sample_control_complete"] = (
    df["control_min_coverage"].ge(MIN_CONTROL_COVERAGE)
    & df["control_n_months"].ge(MIN_CONTROL_MONTHS)
)
df["sample_cell_inputs"] = (
    df["portfolio_size"].notna()
    & df["portfolio_risk_12m"].notna()
    & df["expected_ret_12m"].notna()
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
    & df["portfolio_size"].notna()
    & df["portfolio_risk_12m"].notna()
    & df["expected_ret_12m"].notna(),
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

df = df.merge(
    cell_base[[
        USER_COL, "wave", "analysis_size_bin", "analysis_risk_bin",
        "analysis_eret_bin", "portfolio_cell_status",
        "analysis_portfolio_cell",
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
        "3_portfolio_ge0" if KEEP_ZERO_PORTFOLIO else "3_portfolio_gt0",
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


# === CELL 8: Reduced-form regressions ===

section("CELL 8: Reduced-form regressions")

required_columns = [USER_COL, CORE_X_VAR] + REG_FE_NAMES + REG_CONTROL_NAMES + Y_VARS
missing_columns = [name for name in required_columns if name not in df.columns]
if missing_columns:
    RUN_BLOCKERS.append("missing_regression_columns:" + ",".join(missing_columns))
if SE_TYPE not in ["cluster_user", "HC1"]:
    RUN_BLOCKERS.append("invalid_SE_TYPE")
if TIMING_RULE not in ["post_window_only", "audit_only"]:
    RUN_BLOCKERS.append("invalid_TIMING_RULE")
elif TIMING_RULE == "audit_only":
    RUN_BLOCKERS.append("timing_audit_only_no_estimates")
if OUTPUT_MODE not in ["compact", "full"]:
    RUN_BLOCKERS.append("invalid_OUTPUT_MODE")
RUN_BLOCKERS = list(dict.fromkeys(RUN_BLOCKERS))
emit_table(
    "CORE 0 Run Integrity Gate",
    ["revision", "run", "gate", "blockers", "timing", "SE", "output"],
    [[SCRIPT_REVISION, RUN_ID, "BLOCK" if RUN_BLOCKERS else "PASS",
      "; ".join(RUN_BLOCKERS) or "none", TIMING_RULE, SE_TYPE, OUTPUT_MODE]],
)

emit_table(
    "Active Regression Settings",
    ["setting", "value"],
    [
        ["RUN_ID", RUN_ID],
        ["SCRIPT_REVISION", SCRIPT_REVISION],
        ["SHOCK_TABLE", SHOCK_TABLE],
        ["PORT_CONTROL_TABLE", PORT_CONTROL_TABLE],
        ["WAVES", ", ".join(WAVES)],
        ["CORE_X_CHOICE", CORE_X_CHOICE],
        ["CORE_X_VAR", CORE_X_VAR],
        ["GAIN_UNIT_YUAN", fmt_int(GAIN_UNIT_YUAN)],
        ["SHOCK_PORTFOLIO_SCOPE", SHOCK_PORTFOLIO_SCOPE],
        ["KEEP_ZERO_PORTFOLIO", str(KEEP_ZERO_PORTFOLIO)],
        ["ENFORCE_CONTROL_COMPLETENESS", str(ENFORCE_CONTROL_COMPLETENESS)],
        ["BINS", str((N_SIZE_BIN, N_RISK_BIN, N_ERET_BIN))],
        ["CELL_RANK_SCOPE", CELL_RANK_SCOPE],
        ["CELL_RANK_METHOD", CELL_RANK_METHOD],
        ["ZERO_PORTFOLIO_CELL_MODE", ZERO_PORTFOLIO_CELL_MODE],
        ["SE_TYPE", SE_TYPE],
        ["MIN_REG_N", fmt_int(MIN_REG_N)],
        ["CELL_FE_NAMES", ", ".join(CELL_FE_NAMES)],
        ["OTHER_FE_NAMES", ", ".join(OTHER_FE_NAMES)],
        ["CONTROL_NAMES", ", ".join(CONTROL_NAMES)],
        ["REG_FE_NAMES", ", ".join(REG_FE_NAMES)],
        ["REG_CONTROL_NAMES", ", ".join(REG_CONTROL_NAMES)],
        ["MAIN_SPEC_NAME", MAIN_SPEC_NAME],
        ["BALANCE_FE_NAMES", ", ".join(BALANCE_FE_NAMES)],
    ],
)

emit_table(
    "Regression Specifications",
    ["spec", "label", "FE", "controls"],
    [
        [
            spec["name"], spec["label"],
            ", ".join(spec.get("fe_names", [])) or "-",
            ", ".join(spec.get("control_names", [])) or "-",
        ]
        for spec in REG_SPECS
    ],
)

emit_table(
    "Regression Input Dtypes",
    ["variable", "dtype"],
    [[name, str(as_formula_object(df[name]).dtype)] for name in enabled_existing(REG_FE_NAMES, df)]
    + [
        [CORE_X_VAR, str(pd.to_numeric(df[CORE_X_VAR], errors="coerce").dtype)],
    ]
    + [
        [name, str(pd.to_numeric(df[name], errors="coerce").dtype)]
        for name in enabled_existing(REG_CONTROL_NAMES, df)
    ],
)

rf_outputs = [
    normalize_rf_output(y_name, run_rf(df, y_name, spec))
    for y_name in Y_VARS
    for spec in REG_SPECS
]
result_columns = [
    "spec", "Y", "n_obs", "n_users", "beta", "se", "t", "p", "R2", "note", "core_x",
]
for fe_name in REG_FE_NAMES:
    result_columns += [f"{fe_name}_fe", f"{fe_name}_n"]
results = pd.DataFrame(
    [summary for summary, _ in rf_outputs],
    columns=result_columns,
)
detail_results = pd.DataFrame(
    [row for _, detail_rows in rf_outputs for row in detail_rows],
    columns=["spec", "Y", "variable", "coef", "se", "t", "p", "note"],
)
detail_with_fit = detail_results.merge(
    results[["spec", "Y", "n_obs", "R2"]],
    on=["spec", "Y"],
    how="left",
    validate="many_to_one",
)

main_results = results.loc[results["spec"].eq(MAIN_SPEC_NAME)].copy()
main_results["holm_p"] = np.nan
valid_p = pd.to_numeric(main_results["p"], errors="coerce").notna()
if valid_p.any():
    main_results.loc[valid_p, "holm_p"] = multipletests(
        main_results.loc[valid_p, "p"].astype(float), method="holm"
    )[1]
emit_table(
    "CORE 4 Main Effects - One Row per Outcome",
    ["Y", "N", "users", "beta", "SE", "p", "Holm_p", "95%_CI", "R2", "note"],
    [[
        row["Y"], fmt_int(row["n_obs"]), fmt_int(row["n_users"]),
        fmt_float(row["beta"], 5), fmt_float(row["se"], 5),
        fmt_float(row["p"], 4), fmt_float(row["holm_p"], 4),
        f'[{fmt_float(row["beta"] - 1.96 * row["se"], 5)}, '
        f'{fmt_float(row["beta"] + 1.96 * row["se"], 5)}]'
        if pd.notna(row["beta"]) and pd.notna(row["se"]) else "-",
        fmt_float(row["R2"], 3), row["note"] or "-",
    ] for _, row in main_results.iterrows()],
)

emit_table(
    "CORE 5 Specification Stability - Same Outcome Sample",
    ["Y", "N", "cell_FE", "cell_plus_FE", "main_plus_controls"],
    [[y_name, fmt_int(main_results.loc[main_results["Y"].eq(y_name), "n_obs"].iloc[0])] + [
        fmt_coef_stars(
            results.loc[results["Y"].eq(y_name) & results["spec"].eq(spec["name"]), "beta"].iloc[0],
            results.loc[results["Y"].eq(y_name) & results["spec"].eq(spec["name"]), "p"].iloc[0],
        ) for spec in REG_SPECS
    ] for y_name in Y_VARS],
)

if OUTPUT_MODE == "full":
    comparison_rows = []
    for y_name in Y_VARS:
        row = [y_name]
        for spec in REG_SPECS:
            hit = results.loc[
                results["Y"].eq(y_name) & results["spec"].eq(spec["name"])
            ]
            if len(hit) == 0:
                row.append("-")
            else:
                r = hit.iloc[0]
                row.append(fmt_coef_stars(r["beta"], r["p"]))
        comparison_rows.append(row)

    comparison_cols = ["Y"]
    for spec in REG_SPECS:
        comparison_cols.append(spec["name"])

    emit_table(
        "X Coefficient Comparison Across Specs",
        comparison_cols,
        comparison_rows,
    )

    emit_table(
        "RF Coefficients and Fit - Estimates",
        ["spec", "Y", "variable", "n_obs", "coef", "se", "t"],
        [
            [
                row["spec"], row["Y"], row["variable"], fmt_int(row["n_obs"]),
                fmt_float(row["coef"], 5), fmt_float(row["se"], 5),
                fmt_float(row["t"], 3),
            ]
            for _, row in detail_with_fit.iterrows()
        ],
    )

    emit_table(
        "RF Coefficients and Fit - P Values, R2, and Notes",
        ["spec", "Y", "variable", "p", "R2", "note"],
        [
            [
                row["spec"], row["Y"], row["variable"],
                fmt_float(row["p"], 4), fmt_float(row["R2"], 4), row["note"],
            ]
            for _, row in detail_with_fit.iterrows()
        ],
    )

    fe_diag_rows = []
    for _, row in results.iterrows():
        for fe_name in REG_FE_NAMES:
            fe_diag_rows.append([
                row["spec"], row["Y"], fe_name,
                row[f"{fe_name}_fe"], fmt_int(row[f"{fe_name}_n"]),
            ])

    emit_table(
        "RF Fixed Effect Diagnostics - Included",
        ["spec", "Y", "FE", "included"],
        [[spec, y_name, fe_name, included] for spec, y_name, fe_name, included, _ in fe_diag_rows],
    )

    emit_table(
        "RF Fixed Effect Diagnostics - Category Counts",
        ["spec", "Y", "FE", "n_categories"],
        [[spec, y_name, fe_name, n_categories] for spec, y_name, fe_name, _, n_categories in fe_diag_rows],
    )

    n_by_wave = []
    for wave in WAVES:
        tmp = df.loc[df["wave"].eq(wave) & df["analysis_base_sample"].eq(1)]
        n_by_wave.append([wave] + [fmt_int(tmp[y_name].notna().sum()) for y_name in Y_VARS])

    emit_table("Outcome Nonmissing Counts in Base Sample", ["wave"] + Y_VARS, n_by_wave)

if RUN_BALANCE_CHECKS and not RUN_BLOCKERS:
    main_specs = [spec for spec in REG_SPECS if spec["name"] == MAIN_SPEC_NAME]
    diag_spec = main_specs[0] if len(main_specs) > 0 else REG_SPECS[-1]
    cell_diag = [cell_diagnostics(df, y_name, diag_spec) for y_name in BALANCE_Y_VARS]
    emit_table(
        "AUX 1 Cell Density and Within-Cell Shock Variation",
        [
            "Y", "n", "cells", "singleton_cells", "share_obs_cell_lt5",
            "share_obs_no_X_variation", "cell_p10", "cell_p50", "cell_p90",
            "within_cell_X_sd", "raw_X_sd",
        ],
        [
            [
                row["Y"], fmt_int(row["n"]), fmt_int(row["cells"]),
                fmt_int(row["singleton_cells"]),
                fmt_float(row["share_obs_cell_lt5"]),
                fmt_float(row["share_obs_no_X_variation"]),
                fmt_float(row["cell_p10"], 1), fmt_float(row["cell_p50"], 1),
                fmt_float(row["cell_p90"], 1),
                fmt_float(row["within_cell_X_sd"]),
                fmt_float(row["raw_X_sd"]),
            ]
            for row in cell_diag
        ],
    )

    conditional_diag = [
        conditional_shock_variation(df, y_name, diag_spec)
        for y_name in BALANCE_Y_VARS
    ]
    emit_table(
        "AUX 2 Conditional Shock Variation After FE and Controls",
        ["Y", "n", "raw_X_sd", "residual_X_sd", "residual_SS_share", "df_resid", "note"],
        [
            [
                row["Y"], fmt_int(row["n"]), fmt_float(row["raw_X_sd"]),
                fmt_float(row["residual_X_sd"]),
                fmt_float(row["residual_SS_share"]),
                fmt_float(row["df_resid"], 0), row["note"],
            ]
            for row in conditional_diag
        ],
    )

    balance_rows = []
    for y_name in BALANCE_Y_VARS:
        for trait in BALANCE_TEST_VARS:
            balance_rows.append(lottery_balance_test(df, y_name, trait))
        gc.collect()

    tested_idx = [i for i, row in enumerate(balance_rows) if pd.notna(row["p"])]
    balance_holm = multipletests(
        [float(balance_rows[i]["p"]) for i in tested_idx], method="holm"
    )[1] if tested_idx else []
    for i, adj_p in zip(tested_idx, balance_holm):
        balance_rows[i]["holm_p"] = float(adj_p)
    balance_fail_rows = sorted(
        [
            row for row in balance_rows
            if row.get("holm_p", 1) < 0.05
        ],
        key=lambda row: float(row["holm_p"]),
    )

    emit_table(
        "AUX 4 Balance Flags (Holm p<0.05)",
        ["Y", "trait", "p", "Holm_p", "std_effect", "n"],
        [
            [
                row["Y"], row["trait"], fmt_float(row["p"]),
                fmt_float(row["holm_p"]),
                fmt_float(row["std_effect"]), fmt_int(row["n"]),
            ]
            for row in balance_fail_rows
        ] or [["none", "none", "-", "-", "-", "-"]],
    )

    tested_p = [float(row["p"]) for row in balance_rows if pd.notna(row["p"])]
    emit_table(
        "AUX 3 Balance Test Summary",
        ["tested", "raw_p_lt_0.05", "Holm_p_lt_0.05", "min_p", "reading"],
        [[fmt_int(len(tested_p)), fmt_int(sum(p < 0.05 for p in tested_p)),
          fmt_int(len(balance_fail_rows)),
          fmt_float(min(tested_p), 4) if tested_p else "-",
          "diagnostic, not proof of random assignment"]],
    )
    if OUTPUT_MODE == "full":
        emit_table(
            "Lottery Balance Checks - Estimates",
            ["Y", "trait", "flag", "n", "beta", "se", "p"],
            [
                [
                    row["Y"], row["trait"], fmt_balance_flag(row["p"]), fmt_int(row["n"]),
                    fmt_float(row["beta"]), fmt_float(row["se"]),
                    fmt_float(row["p"]),
                ]
                for row in balance_rows
            ],
        )

        emit_table(
            "Lottery Balance Checks - Std Effect and Notes",
            ["Y", "trait", "flag", "std_effect", "note"],
            [
                [
                    row["Y"], row["trait"], fmt_balance_flag(row["p"]),
                    fmt_float(row["std_effect"]), row["note"],
                ]
                for row in balance_rows
            ],
        )

    emit([
        "Balance-check reading guide:",
        "If cell density is very sparse, the cell design is likely too fine.",
        "If residual_X_sd or residual_SS_share is near zero, FE/controls absorb too much identifying variation.",
        "If tested traits systematically predict X in the lottery checks, cells may be too coarse.",
    ])
