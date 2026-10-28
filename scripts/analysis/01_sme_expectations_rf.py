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
from patsy import dmatrix
from scipy.stats import norm

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
    # Unique row keys survive platform deduplication and join horizontal panels.
    columns = ["row"] + [str(c) for c in columns]
    rows = [[str(i + 1)] + [str(v) for v in row] for i, row in enumerate(rows)]
    widths = [min(24 if i == 0 else 44, max([len(c)] + [len(r[i]) for r in rows]))
              for i, c in enumerate(columns)]
    widths[0] = max(widths[0], len(str(max(1, len(rows)))) + 4)
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
                parts = wrapped(row)
                for k in range(1, len(parts)):
                    parts[k] = (row[0] + "." + str(k)).ljust(widths[0]) + parts[k][widths[0]:]
                lines += parts
            ant_print_all(pd.Series(lines), model_method="unique")


# === CELL 2: Adjustable settings ===

######### CONFIGURE START ###########
SCRIPT_REVISION = "sme_rf_v19_common_sample_audit"
RUN_BATCH = "core"  # core, tail, wave; each is a complete fresh-session submission
RUN_ID = "common_sample_" + RUN_BATCH + "_gain_keepzero"
TAIL_FRACTIONS = (0.005, 0.01)
TOP_USER_DELETIONS = 2  # each user removed separately across ALL their waves
# Prepare and rank five waves once; W4 deletes q3 without reranking or rescaling.
WAVES = ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"]
COARSE_BINS = (5, 3, 3)
SIZE_DETAIL_BINS = (10, 3, 3)
D_EXCLUDED_WAVE = "2024q3"

SE_TYPE = "cluster_user"  # cluster_user or HC1
OUTPUT_MODE = "compact"  # compact or full
RUN_MODE = "wave_controls"  # v19 bounded batch, not the legacy Cartesian grid
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
# Active grid uses positive eligible five-wave scaling; legacy E helper uses four.
POLY_PAIRS = [(i, j) for i in range(3) for j in range(i, 3)]
POLY_NAMES = ["ctrl_poly_" + str(i) + str(j) for i, j in POLY_PAIRS]
DESIGN_CELLS = {
    "C1": ("coarsest_portfolio_cell", (3, 3, 3)),
    "C2": ("coarse_portfolio_cell", (5, 3, 3)),
    "C3": ("size_detail_cell", (10, 3, 3)),
}
DESIGN_WAVES = {"W5": None, "W4": "2024q3"}
MODEL_SPECS = {
    "M0": {"name": "M0", "fe_names": ["size_detail_cell"], "control_names": []},
    "M1": {"name": "M1", "fe_names": ["size_detail_cell"], "control_names": EXT_CONTROL_NAMES},
    "M2": {"name": "M2", "fe_names": ["size_detail_cell"], "control_names": EXT_CONTROL_NAMES + POLY_NAMES},
}
WAVE_BALANCE_TARGETS = ["ctrl_log_portfolio", "ctrl_poly_00", "ctrl_poly_02"]
DIAGNOSTIC_Y_VARS = ["exp_cpi", "exp_input_cost"]
# PRE_TARGETS is defined after the full Y_VARS mapping below.
INVESTOR_SOURCES = CONTROL_NAMES + ["aer_bal_employee_n"]
INVESTOR_TARGETS = ["pre_" + name for name in INVESTOR_SOURCES]
WAVE_LINEAR = ["wc_" + w + "_" + c for w in WAVES for c in EXT_CONTROL_NAMES]
WAVE_POLY = ["wc_" + w + "_" + c for w in WAVES for c in POLY_NAMES]
WAVE_AMOUNT = ["wc_" + w + "_amount" for w in WAVES]
MODEL_SPECS.update({
    "W1": {"name": "W1", "fe_names": ["size_detail_cell"], "control_names": WAVE_LINEAR},
    "W2": {"name": "W2", "fe_names": ["size_detail_cell"], "control_names": WAVE_LINEAR + WAVE_POLY},
    "W3": {"name": "W3", "fe_names": ["size_detail_cell"], "control_names": WAVE_LINEAR + WAVE_POLY + WAVE_AMOUNT},
})
# Primary comparison: all three models use the T2 complete-case sample per Y.
# These are current-wave recorded traits, not mandatory previous-wave answers.
TRAIT_MODEL_SPECS = {
    "T0": {"name": "T0", "fe_names": ["size_detail_cell"], "control_names": []},
    "T1": {"name": "T1", "fe_names": ["size_detail_cell", "portrait_gender"],
           "control_names": ["aer_bal_age", "aer_bal_college"]},
    "T2": {"name": "T2", "fe_names": ["size_detail_cell", "portrait_gender",
           "city_level_from_yicai", "survey_industry"],
           "control_names": ["aer_bal_age", "aer_bal_college", "aer_bal_firm_age", "aer_bal_company"]},
}
DESIGN_TARGETS = EXT_CONTROL_NAMES + POLY_NAMES + CONTROL_NAMES + ["aer_bal_employee_n"]
E_SPECS = {
    "E1": {"name": "E1_coarse_fourwave", "fe_names": ["coarse_portfolio_cell"] + OTHER_FE_NAMES,
           "control_names": CONTROL_NAMES + EXT_CONTROL_NAMES},
    "E2": {"name": "E2_size_detail_fourwave", "fe_names": ["size_detail_cell"] + OTHER_FE_NAMES,
           "control_names": CONTROL_NAMES + EXT_CONTROL_NAMES},
    "E3": {"name": "E3_group_wave_FE", "fe_names": ["coarse_portfolio_cell", "city_wave_FE",
           "industry_wave_FE", "portrait_gender", "aer_bal_employee_group"],
           "control_names": CONTROL_NAMES + EXT_CONTROL_NAMES},
    "E4": {"name": "E4_nonlinear_portfolio", "fe_names": ["coarse_portfolio_cell"] + OTHER_FE_NAMES,
           "control_names": CONTROL_NAMES + EXT_CONTROL_NAMES + POLY_NAMES},
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

ACTIVE_Y_VARS = list(Y_VARS)  # All eleven outcomes, never selected by past p-values.
PRE_TARGETS = ["pre_" + y for y in ACTIVE_Y_VARS]
AUDIT_SPECS = {
    "A": dict(MODEL_SPECS["M0"], name="A"),
    "B": dict(MODEL_SPECS["M0"], name="B"),
    "C": dict(TRAIT_MODEL_SPECS["T2"], name="C"),
    "D": dict(TRAIT_MODEL_SPECS["T2"], name="D", control_names=CONTROL_NAMES + WAVE_LINEAR + WAVE_POLY),
    "E": dict(TRAIT_MODEL_SPECS["T2"], name="E", control_names=CONTROL_NAMES + WAVE_LINEAR + WAVE_POLY + WAVE_AMOUNT),
}

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


def effective_controls(run, spec):
    # Omitted-wave interactions are all zero, and must not inflate the cluster
    # finite-sample column-count correction. Keep legacy common controls intact.
    return [c for c in spec["control_names"]
            if not (c.startswith("wc_") and run[c].eq(0).all())]


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


def estimate_rf(run, y_name, spec, cache, capture=False):
    """Keep statsmodels estimation/covariance unchanged; cache small summaries.

    The cache lives for one outcome with immutable source values. Matrices and
    fitted models are released after each fit, avoiding a large model cache.
    """
    key = (y_name, capture, tuple(run.index), tuple(spec["fe_names"]), tuple(spec["control_names"]))
    if key in cache:
        return dict(cache[key], spec=spec["name"])
    row = {"Y": y_name, "spec": spec["name"], "n_obs": len(run),
           "n_users": run[USER_COL].nunique(), "note": "",
           "n_positive": int(run["portfolio_size_raw"].gt(0).sum()) if "portfolio_size_raw" in run else 0,
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
        # Platform Patsy versions may reject pandas StringDtype FE columns.
        # Normalize only model inputs on a private frame; preserve labels/index
        # and missing-value semantics, without changing the shared sample.
        diagnostic_source = run
        model_columns = list(dict.fromkeys([y_name, CORE_X_VAR, USER_COL]
                             + spec["fe_names"] + spec["control_names"]))
        run = run.loc[:, model_columns].copy()
        for name in spec["fe_names"] + [USER_COL]:
            run[name] = as_formula_object(run[name])
        terms = fe_terms_for(run, spec["fe_names"]) + effective_controls(run, spec)
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
        if RUN_MODE != "wave_controls":
            row["variation"] = variation_from_fit(fit, run, terms)
        else:
            pos = fit.model.exog_names.index(CORE_X_VAR)
            unit = np.zeros(fit.model.exog.shape[1])
            unit[pos] = 1
            if not np.allclose(fit.model.pinv_wexog[pos] @ fit.model.exog, unit, rtol=1e-7, atol=1e-8):
                row.update(beta=np.nan, se=np.nan, t=np.nan, p=np.nan, note="gain_not_separately_identified")
            elif y_name in ACTIVE_Y_VARS and "diagnostic_size_bin" in diagnostic_source:
                row["identification"] = identification_summary(fit, diagnostic_source)
                if capture:
                    weights = fit.model.pinv_wexog[pos]
                    xr = weights / float(weights @ weights)
                    row["_exposure"] = pd.Series(xr ** 2, index=diagnostic_source.index)
                    row["_user_score"] = pd.Series(xr * np.asarray(fit.resid) / float(xr @ xr),
                        index=diagnostic_source.index).groupby(diagnostic_source[USER_COL]).sum().abs()
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
    common = basic.merge(
        source.loc[basic.index, EXT_CONTROL_NAMES], how="left",
        left_index=True, right_index=True, sort=False, validate="one_to_one",
    )
    common = common.replace([np.inf, -np.inf], np.nan).dropna(subset=EXT_CONTROL_NAMES)
    c = common.merge(
        source.loc[common.index, ["coarse_portfolio_cell"]], how="left",
        left_index=True, right_index=True, sort=False, validate="one_to_one",
    )
    c["coarse_portfolio_cell"] = as_formula_object(c["coarse_portfolio_cell"])
    # Missing C labels must flag a skipped fit, never silently change its sample.
    d = common.loc[~source.loc[common.index, "wave"].eq(D_EXCLUDED_WAVE)].copy()
    audit = [short_y(y_name), len(basic), len(common), len(basic) - len(common),
             len(c), int(c["coarse_portfolio_cell"].isna().sum()), len(d), len(common) - len(d)]
    return {"C": c, "D": d}, audit


def prepare_e_design(source):
    out = add_continuous_portfolio_controls(source)
    positive = out["portfolio_size_raw"].gt(0)
    reference = positive & out["analysis_base_sample"].eq(1) & ~out["wave"].eq(D_EXCLUDED_WAVE)
    z = pd.DataFrame(index=out.index)
    scaling = []
    for name in EXT_CONTROL_NAMES:
        mean = out.loc[reference, name].mean()
        sd = out.loc[reference, name].std()
        scale = sd if np.isfinite(sd) and sd > 0 else 1.0
        z[name] = (out[name] - mean) / scale
        z.loc[out["zero_history_not_applicable"].fillna(False), name] = 0.0
        scaling.append([name, mean, scale])
    for name, (i, j) in zip(POLY_NAMES, POLY_PAIRS):
        out[name] = z[EXT_CONTROL_NAMES[i]] * z[EXT_CONTROL_NAMES[j]]
    for source_col, target in [("city_level_from_yicai", "city_wave_FE"),
                               ("survey_industry", "industry_wave_FE")]:
        out[target] = as_formula_object(out[source_col].astype("string") + "::" + out["wave"].astype("string"))
    return out, scaling


def select_e_samples(source, y_name):
    reference, old_audit = select_cd_samples(source, y_name)
    base = reference["D"]
    extra = ["coarse_portfolio_cell", "size_detail_cell", "city_wave_FE", "industry_wave_FE"] + POLY_NAMES
    common = base.merge(source.loc[base.index, extra], how="left", left_index=True,
                        right_index=True, sort=False, validate="one_to_one")
    for col in extra[:4]:
        common[col] = as_formula_object(common[col])
    # Derived inputs cannot silently alter samples. Missing inputs skip the affected fit.
    audit = [short_y(y_name), old_audit[1], old_audit[2], old_audit[3],
             len(reference["C"]), len(base), old_audit[7],
             int(common[extra].isna().any(axis=1).sum())]
    return common, reference, audit


def balance_diagnostics(run, source, group, y_name, layer, spec, cell_col, targets=None, scopes=None):
    """Batch target projections by complete-case mask, with user-cluster inference.

    Cell-only uses within-cell demeaning. Final-model checks use a single
    pseudoinverse per mask. Controlled/absorbed targets are not balance passes.
    Survey traits have unverified pre-shock timing; label them accordingly.
    """
    if targets is None:
        targets = CONTROL_NAMES + EXT_CONTROL_NAMES if layer == "cell" else CONTROL_NAMES + EXT_CONTROL_NAMES + POLY_NAMES + ["aer_bal_employee_n"]
    results = []
    for scope in (["all", "positive"] if scopes is None else scopes):
        scoped = run if scope == "all" else run.loc[source.loc[run.index, "portfolio_size_raw"].gt(0)]
        matrices = {}
        for target in targets:
            row = dict(group=group, Y=short_y(y_name), layer=layer, scope=scope, trait=target,
                       provenance="pre_window_portfolio" if target in EXT_CONTROL_NAMES + POLY_NAMES else "survey_timing_unverified",
                       n_obs=len(scoped), dropped=0, beta=np.nan, se=np.nan, p=np.nan,
                       holm_p=np.nan, std_effect=np.nan, std_low=np.nan, std_high=np.nan, note="")
            results.append(row)
            if RUN_BLOCKERS:
                row["note"] = "blocked_integrity_gate"
                continue
            if layer == "final" and target in spec["control_names"]:
                row["note"] = "controlled_not_a_test"
                continue
            if target not in source.columns:
                row["note"] = "unavailable"
                continue
            values = pd.to_numeric(source.loc[scoped.index, target], errors="coerce").replace([np.inf, -np.inf], np.nan)
            selected = scoped.loc[values.notna()]
            row["n_obs"], row["dropped"] = len(selected), len(scoped) - len(selected)
            required = [CORE_X_VAR, USER_COL, cell_col] if layer == "cell" else [CORE_X_VAR, USER_COL] + spec["fe_names"] + spec["control_names"]
            if selected[required].isna().any().any():
                row["note"] = "missing_model_input"
                continue
            if len(selected) < MIN_REG_N:
                row["note"] = "skip_n"
                continue
            key = tuple(selected.index)
            if key not in matrices:
                x = selected[CORE_X_VAR].to_numpy(dtype=float)
                codes = pd.factorize(selected[USER_COL])[0]
                if layer == "cell":
                    xr = (selected[CORE_X_VAR] - selected.groupby(cell_col, observed=True)[CORE_X_VAR].transform("mean")).to_numpy()
                    k = selected[cell_col].nunique() + 1
                    matrix, pinv = None, None
                else:
                    terms = fe_terms_for(selected, spec["fe_names"]) + effective_controls(selected, spec)
                    formula_data = selected.copy()
                    for col in spec["fe_names"]:
                        formula_data[col] = as_formula_object(formula_data[col])
                    matrix = np.asarray(dmatrix("1 + " + " + ".join(terms), formula_data, NA_action="raise"))
                    pinv = np.linalg.pinv(matrix)
                    xr = x - matrix @ (pinv @ x)
                    # statsmodels cluster correction uses column count, HC1 uses rank.
                    k = (matrix.shape[1] + 1 if SE_TYPE == "cluster_user"
                         else np.linalg.matrix_rank(matrix) + 1)
                matrices[key] = (x, xr, codes, k, matrix, pinv)
                FIT_COUNTS["balance_projection"] = FIT_COUNTS.get("balance_projection", 0) + 1
            x, xr, codes, k, matrix, pinv = matrices[key]
            z = values.loc[selected.index].to_numpy(dtype=float)
            if layer == "cell":
                zr = (values.loc[selected.index] - values.loc[selected.index].groupby(selected[cell_col], observed=True).transform("mean")).to_numpy()
            else:
                zr = z - matrix @ (pinv @ z)
            n, clusters = len(z), len(np.unique(codes))
            ss = float(xr @ xr)
            if np.std(z) == 0 or np.linalg.norm(zr) <= 1e-10 * max(1.0, np.linalg.norm(z)):
                row["note"] = "absorbed_or_constant_not_a_test"
                continue
            if ss <= 1e-16 * max(1.0, float(x @ x)):
                row["note"] = "no_conditional_X_variation"
                continue
            if n <= k or (SE_TYPE == "cluster_user" and clusters < 2):
                row["note"] = "insufficient_covariance_df"
                continue
            beta = float(xr @ zr / ss)
            influence = xr * (zr - beta * xr) / ss
            variance = (np.sum(np.bincount(codes, weights=influence) ** 2) * clusters / (clusters - 1) * (n - 1) / (n - k)
                        if SE_TYPE == "cluster_user" else np.sum(influence ** 2) * n / (n - k))
            se = float(np.sqrt(max(0, variance)))
            if not np.isfinite(se) or se <= 0:
                row["note"] = "nonfinite_or_zero_se"
                continue
            scale = np.std(x, ddof=1) / np.std(z, ddof=1)
            row.update(beta=beta, se=se, p=float(2 * norm.sf(abs(beta / se))),
                       std_effect=beta * scale, std_low=(beta - 1.96 * se) * scale,
                       std_high=(beta + 1.96 * se) * scale)
    return results


def prepare_wave_cell_design(source):
    """One five-wave pre-outcome scaling reference for every candidate/scope."""
    out = add_continuous_portfolio_controls(source)
    reference = (out["analysis_base_sample"].eq(1) & out["sample_cell_inputs"].fillna(False)
                 & out["portfolio_size"].gt(0))
    z, scaling = pd.DataFrame(index=out.index), []
    for name in EXT_CONTROL_NAMES:
        values = out.loc[reference, name]
        mean, sd = values.mean(), values.std()
        scale = sd if np.isfinite(sd) and sd > 0 else 1.0
        z[name] = (out[name] - mean) / scale
        z.loc[out["zero_history_not_applicable"].fillna(False), name] = 0.0
        scaling.append([name, int(values.notna().sum()), mean, sd, scale])
    for name, (i, j) in zip(POLY_NAMES, POLY_PAIRS):
        out[name] = z[EXT_CONTROL_NAMES[i]] * z[EXT_CONTROL_NAMES[j]]
    extra = {}
    amount = pd.to_numeric(out["portfolio_size"], errors="coerce") / GAIN_UNIT_YUAN
    for wave in WAVES:
        mask = out["wave"].eq(wave)
        for name in EXT_CONTROL_NAMES + POLY_NAMES:
            extra["wc_" + wave + "_" + name] = out[name].where(mask, 0.0)
        extra["wc_" + wave + "_amount"] = amount.where(mask, 0.0)
    out = out.drop(columns=list(extra), errors="ignore")
    out = pd.concat([out, pd.DataFrame(extra, index=out.index)], axis=1)
    # Predetermined five-wave ranks, never recomputed after outcome/wave filtering.
    ranks = out.loc[reference].groupby("wave")["portfolio_size"].rank(method="average", pct=True)
    out["diagnostic_size_bin"] = "zero"
    out.loc[reference, "diagnostic_size_bin"] = np.ceil(ranks * 10).astype(int).astype(str)
    return out, scaling


def add_preperiod_targets(source):
    """Previous scheduled wave only; never latest available/future/backfilled.

    Prior answer must be a unique owner response passing duration and strictly
    precede the current shock start. No investment eligibility is imposed on it.
    Missing prior observations never filter the main outcome sample.
    """
    out = source.copy()
    for target in PRE_TARGETS + INVESTOR_TARGETS:
        out[target] = np.nan
    needed = [USER_COL, "wave", "submit_dt", "sample_sme_owner", "sample_answer_time"]
    if any(c not in out for c in needed):
        return out, "preperiod_unavailable_missing_date_or_quality_columns"
    valid = (out["sample_sme_owner"].fillna(False) & out["sample_answer_time"].fillna(False)
             & out[USER_COL].notna() & ~out.duplicated([USER_COL, "wave"], keep=False))
    starts = globals().get("SHOCK_WINDOW_START_BY_WAVE", {})
    for previous, current in zip(WAVES[:-1], WAVES[1:]):
        start = starts.get(current)
        if pd.isna(start):
            continue
        prior = out.loc[valid & out["wave"].eq(previous)
                        & pd.to_datetime(out["submit_dt"], errors="coerce").lt(start)].set_index(USER_COL)
        mask = out["wave"].eq(current)
        for y in ACTIVE_Y_VARS + INVESTOR_SOURCES:
            if y in prior:
                out.loc[mask, "pre_" + y] = out.loc[mask, USER_COL].map(prior[y])
    return out, "previous_scheduled_wave; prior_submit_strictly_before_current_start; no_main_sample_filter"


def investor_balance_diagnostics(run, source, group, label, reference_sd):
    """Paired raw/cell associations on identical target-specific prior subsets.

    Slopes regress a prior trait on current gain (not the orientation of the
    paper's scatterplots). These are aggregate conditional diagnostics, never
    separate tests in each cell or a joint exogeneity/pass certificate.
    """
    paired = run.copy()
    paired["lottery_constant"] = "all"
    results = []
    for adjustment, cell in [("raw", "lottery_constant"), ("cell", "size_detail_cell")]:
        rows = balance_diagnostics(paired, source, group, label, "cell", MODEL_SPECS["M0"],
                                   cell, targets=INVESTOR_TARGETS, scopes=["positive"])
        for row in rows:
            row.update(adjustment=adjustment, provenance="dated_previous_wave_response")
            denominator = reference_sd.get(row["trait"], np.nan)
            numerator = reference_sd.get(CORE_X_VAR, np.nan)
            scale = numerator / denominator if np.isfinite(denominator) and denominator > 0 else np.nan
            if not np.isfinite(scale) or scale <= 0:
                row["note"] = row["note"] or "invalid_prior_reference_scale"
                scale = np.nan
            row.update(std_effect=row["beta"] * scale,
                       std_low=(row["beta"] - 1.96 * row["se"]) * scale,
                       std_high=(row["beta"] + 1.96 * row["se"]) * scale)
        # Supplemental multiplicity adjustment within the five predeclared traits.
        apply_holm(rows)
        results.extend(rows)
    return results


def identification_summary(fit, source):
    """FWL exposure shares and score concentration from the main fit, no refit.

    Scores are first-order influence numerators, NOT exact deletion effects.
    No user IDs or individual values are printed or returned.
    """
    pos = fit.model.exog_names.index(CORE_X_VAR)
    weights = fit.model.pinv_wexog[pos]
    xr = weights / float(weights @ weights)
    ss = float(xr @ xr)
    beta = float(fit.params[CORE_X_VAR])
    score = xr * np.asarray(fit.resid) / ss
    contribution = beta * xr ** 2 / ss + score
    positive = source["portfolio_size_raw"].gt(0).to_numpy()
    shares = xr ** 2 / ss
    count = max(1, int(np.ceil(positive.sum() * .01)))
    user_scores = pd.Series(score, index=source.index).groupby(source[USER_COL]).sum()
    raw_x = source[CORE_X_VAR].to_numpy(dtype=float)
    raw_ss = float(((raw_x - raw_x.mean()) ** 2).sum())
    totals = dict(residual_SS=ss, residual_SD=float(np.std(xr, ddof=1)),
                  retained_SS=ss / raw_ss if raw_ss else np.nan,
                  top1pct_positive_SS=float(np.sort(shares[positive])[-count:].sum()),
                  max_obs_SS=float(shares.max()),
                  max_abs_user_score=float(user_scores.abs().max()))
    grouped = []
    for kind, column in [("wave", "wave"), ("size_bin", "diagnostic_size_bin")]:
        labels = source[column].astype(str).to_numpy()
        for label in sorted(set(labels)):
            mask = labels == label
            grouped.append([kind, label, int(mask.sum()), float((xr[mask] ** 2).sum()),
                            float(shares[mask].sum()), float(contribution[mask].sum())])
    return dict(totals=totals, groups=grouped)


def select_design_samples(source, y_name):
    """No legacy survey-control/other-FE complete-case filter; no candidate drops."""
    eligible = source.loc[source["analysis_base_sample"].eq(1)
                          & source["sample_cell_inputs"].fillna(False)].copy()
    required = [USER_COL, CORE_X_VAR, "wave"] + EXT_CONTROL_NAMES
    if y_name is not None:
        eligible[y_name] = pd.to_numeric(eligible[y_name], errors="coerce")
        required.append(y_name)
    common = eligible.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()
    four = common.loc[~common["wave"].eq(D_EXCLUDED_WAVE)].copy()
    return {"W5": common, "W4": four}, [short_y(y_name) if y_name else "BASE",
        len(eligible), len(common), len(eligible) - len(common), len(four), len(common) - len(four)]


def select_trait_sample(run):
    """One declared T2-complete sample for T0/T1/T2; audit control attrition.

    Do not require employee size, risk ratings, prior responses or new tables.
    Do not modify the source, rerank cells or filter the portfolio-model grid.
    Missing source columns make this comparison unavailable, not an exception.
    """
    out = run.copy()
    spec = TRAIT_MODEL_SPECS["T2"]
    numeric = spec["control_names"]
    categorical = [c for c in spec["fe_names"] if c != "size_detail_cell"]
    columns = numeric + categorical
    absent = [c for c in columns if c not in out]
    for name in columns:
        if name not in out:
            out[name] = np.nan
        if name in numeric:
            out[name] = pd.to_numeric(out[name], errors="coerce").replace([np.inf, -np.inf], np.nan)
        else:
            out[name] = as_formula_object(clean_text(out[name]))
    basic = TRAIT_MODEL_SPECS["T1"]["control_names"] + ["portrait_gender"]
    n_basic = int(out[basic].notna().all(axis=1).sum())
    missing = [[c, int(out[c].isna().sum()), "missing_column" if c in absent else "-"] for c in columns]
    common = out.dropna(subset=columns).copy()
    note = "missing_trait_columns:" + ",".join(absent) if absent else "-"
    audit = [len(run), n_basic, len(common), len(run) - n_basic,
             n_basic - len(common), int(common["portfolio_size_raw"].gt(0).sum()),
             int(common["recorded_zero_portfolio"].sum()),
             int(common["imputed_zero_portfolio"].sum()), note]
    return common, audit, missing


def design_variation(run, cell_col):
    """Exact cell-FE projection by demeaning, with no outcome fit."""
    if run.empty:
        return [0, np.nan, np.nan, np.nan, 0, "empty_sample"]
    x = run[CORE_X_VAR]
    residual = x - run.groupby(cell_col, observed=True)[CORE_X_VAR].transform("mean")
    raw_ss = float(((x - x.mean()) ** 2).sum())
    residual_ss = float((residual ** 2).sum())
    note = "no_raw_variation" if raw_ss <= 0 else ("no_conditional_variation" if residual_ss <= 1e-16 * max(1.0, float((x ** 2).sum())) else "-")
    return [len(run), x.std(), residual.std(), residual_ss / raw_ss if raw_ss > 0 else np.nan,
            len(run) - run[cell_col].nunique(), note]


def apply_holm(rows):
    indices = [i for i, row in enumerate(rows) if np.isfinite(row["p"])]
    if indices:
        adjusted = multipletests([rows[i]["p"] for i in indices], method="holm")[1]
        for i, p in zip(indices, adjusted):
            rows[i]["holm_p"] = float(p)


def short_y(name):
    return name.removeprefix("exp_") if hasattr(str, "removeprefix") else name.replace("exp_", "", 1)


def audit_holm(rows, keys, family_size=11):
    """Keep unavailable outcomes in the declared family with p=1."""
    families = {}
    for row in rows:
        families.setdefault(tuple(row[k] for k in keys), []).append(row)
    for family in families.values():
        valid = [r for r in family if np.isfinite(r["p"])]
        p = [r["p"] for r in valid] + [1.0] * max(0, family_size - len(valid))
        if valid:
            for row, adjusted in zip(valid, multipletests(p, method="holm")[1]):
                row["holm_p"] = float(adjusted)


def scale_audit_balance(rows, reference_sd):
    for row in rows:
        denominator = reference_sd.get(row["trait"], np.nan)
        scale = reference_sd.get(CORE_X_VAR, np.nan) / denominator if denominator > 0 else np.nan
        if not np.isfinite(scale) or scale <= 0:
            row["note"] = row["note"] or "invalid_reference_scale"
            scale = np.nan
        row.update(std_effect=row["beta"] * scale,
                   std_low=(row["beta"] - 1.96 * row["se"]) * scale,
                   std_high=(row["beta"] + 1.96 * row["se"]) * scale)
    return rows


def tail_subsets(run, exposure, user_scores, capital_cutoffs):
    """Rank once at the baseline; no outcome-based thresholds or cell reranking.

    Capital cutoffs come from the positive pre-outcome BASE within each wave.
    Ties at the cutoff are retained. Residual tails use stable index tie breaks.
    User-score selection is outcome-dependent and explicitly diagnostic only.
    """
    positive = run["portfolio_size_raw"].gt(0)
    ranked = exposure.loc[positive].sort_values(ascending=False, kind="mergesort")
    for fraction in TAIL_FRACTIONS:
        tag = str(int(fraction * 1000))
        cutoff = run["wave"].map(capital_cutoffs[fraction])
        yield "capital_" + tag, run.loc[~positive | run["portfolio_size_raw"].le(cutoff)]
        count = int(np.ceil(positive.sum() * fraction))
        yield "residual_" + tag, run.drop(index=ranked.index[:count])
    for rank, user in enumerate(user_scores.sort_values(ascending=False, kind="mergesort").index[:TOP_USER_DELETIONS], 1):
        yield "user_" + str(rank), run.loc[run[USER_COL].ne(user)]


def wave_effects(run, y_name, spec):
    """One interaction regression and cluster-robust equality Wald test.

    Only estimable wave slopes enter equality restrictions; skipped waves are
    explicit and the test is labelled partial if a present wave is aliased.
    """
    rows = []
    joint = dict(Y=y_name, model=spec["name"], p=np.nan, holm_p=np.nan,
                 waves=0, note="", n_obs=len(run))
    if len(run) < MIN_REG_N or (SE_TYPE == "cluster_user" and run[USER_COL].nunique() < 2):
        joint["note"] = "insufficient_sample"
        return rows, joint
    data = run.copy()
    names = []
    for wave in WAVES:
        if data["wave"].eq(wave).any():
            name = "gx_" + wave
            data[name] = data[CORE_X_VAR].where(data["wave"].eq(wave), 0.0)
            names.append(name)
    for col in spec["fe_names"]:
        data[col] = as_formula_object(data[col])
    terms = names + fe_terms_for(data, spec["fe_names"]) + effective_controls(data, spec)
    ols = smf.ols(y_name + " ~ " + " + ".join(terms), data=data)
    fit = (ols.fit(cov_type="cluster", cov_kwds={"groups": data[USER_COL].astype(str)})
           if SE_TYPE == "cluster_user" else ols.fit(cov_type=SE_TYPE))
    FIT_COUNTS["regression"] += 1
    estimable = []
    for wave in WAVES:
        name = "gx_" + wave
        row = dict(Y=y_name, model=spec["name"], scenario="slope_" + wave,
                   n_obs=int(data["wave"].eq(wave).sum()), n_users=data.loc[data["wave"].eq(wave), USER_COL].nunique(),
                   beta=np.nan, se=np.nan, p=np.nan, holm_p=np.nan, note="wave_unavailable")
        if name in names:
            pos = fit.model.exog_names.index(name)
            unit = np.eye(1, fit.model.exog.shape[1], pos)[0]
            if np.allclose(fit.model.pinv_wexog[pos] @ fit.model.exog, unit, atol=1e-8, rtol=1e-7):
                row.update(beta=float(fit.params[name]), se=float(fit.bse[name]),
                           p=float(fit.pvalues[name]), note="")
                estimable.append(pos)
            else:
                row["note"] = "wave_gain_not_identified"
        rows.append(row)
    joint["waves"] = len(estimable)
    if len(estimable) >= 2:
        restriction = np.zeros((len(estimable) - 1, fit.model.exog.shape[1]))
        for i, pos in enumerate(estimable[1:]):
            restriction[i, pos], restriction[i, estimable[0]] = 1, -1
        covariance = restriction @ np.asarray(fit.cov_params()) @ restriction.T
        if np.isfinite(covariance).all() and np.linalg.matrix_rank(covariance) == len(restriction):
            joint["p"] = float(fit.wald_test(restriction, use_f=False, scalar=True).pvalue)
            joint["note"] = "partial_estimable_waves" if len(estimable) < len(names) else ""
        else:
            joint["note"] = "singular_wald_covariance"
    else:
        joint["note"] = "too_few_estimable_waves"
    return rows, joint


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
cell_base["size_detail_cell"] = build_portfolio_cells(cell_base, SIZE_DETAIL_BINS)["analysis_portfolio_cell"]
cell_base["coarsest_portfolio_cell"] = build_portfolio_cells(cell_base, (3, 3, 3))["analysis_portfolio_cell"]

df = df.merge(
    cell_base[[
        USER_COL, "wave", "analysis_size_bin", "analysis_risk_bin",
        "analysis_eret_bin", "portfolio_cell_status",
        "analysis_portfolio_cell", "coarse_portfolio_cell", "size_detail_cell", "coarsest_portfolio_cell",
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
    "Preparation funnel with legacy optional-control reference",
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
    "Legacy optional-control complete-case reference",
    ["Y", "base_n", "Y_nonmiss_n", "Y_missing_drop", "reg_ready_n", "reg_var_drop", "users"],
    outcome_sample_rows,
)


# === CELL 8: Compute fixed-cell outcome models and targeted balance ===

section("CELL 8: Compute fixed-cell models")
FIT_COUNTS = {"regression": 0, "variation_fallback": 0, "balance_projection": 0}
FIT_SECONDS = {"regression_and_variation": 0.0, "balance": 0.0}
if RUN_MODE != "wave_controls":
    RUN_BLOCKERS.append("invalid_RUN_MODE_requires_wave_controls")
if SE_TYPE not in ["cluster_user", "HC1"] or OUTPUT_MODE not in ["compact", "full"]:
    RUN_BLOCKERS.append("invalid_SE_or_output_mode")
if (CORE_X_VAR != PASSIVE_GAIN_PREDICTOR or CORE_X_CHOICE != "passive_gain"
        or not KEEP_ZERO_PORTFOLIO or not INCLUDE_IMPUTED_ZERO):
    RUN_BLOCKERS.append("design_requires_gain_and_both_zero_sources")
if WAVES != ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"] or D_EXCLUDED_WAVE != "2024q3":
    RUN_BLOCKERS.append("design_requires_five_waves_and_q3_omission")
if (DESIGN_CELLS != {"C1": ("coarsest_portfolio_cell", (3, 3, 3)),
                     "C2": ("coarse_portfolio_cell", (5, 3, 3)),
                     "C3": ("size_detail_cell", (10, 3, 3))}
        or DESIGN_WAVES != {"W5": None, "W4": "2024q3"}
        or tuple(COARSE_BINS) != (5, 3, 3) or tuple(SIZE_DETAIL_BINS) != (10, 3, 3)
        or CELL_RANK_SCOPE != "within_wave" or CELL_RANK_METHOD != "average"
        or ZERO_PORTFOLIO_CELL_MODE != "pooled_zero_within_wave"):
    RUN_BLOCKERS.append("invalid_design_grid_or_rank_policy")
if TIMING_RULE != "post_window_only" or not ENFORCE_CONTROL_COMPLETENESS:
    RUN_BLOCKERS.append("design_requires_existing_timing_and_history_rules")
required_columns = [USER_COL, CORE_X_VAR, "wave", "analysis_base_sample", "sample_cell_inputs",
    "portfolio_size", "portfolio_size_raw", "portfolio_risk_12m", "expected_ret_12m",
    "zero_history_not_applicable", "recorded_zero_portfolio", "imputed_zero_portfolio"] + Y_VARS
required_columns += ["size_detail_cell"]
missing_columns = [c for c in required_columns if c not in df.columns]
if missing_columns:
    RUN_BLOCKERS.append("missing_design_columns:" + ",".join(missing_columns))
RUN_BLOCKERS = list(dict.fromkeys(RUN_BLOCKERS))

# Bounded batches share fixed data construction, cells and scaling.
if RUN_BATCH not in ["core", "tail", "wave"]:
    RUN_BLOCKERS.append("invalid_RUN_BATCH")
if TAIL_FRACTIONS != (0.005, 0.01) or TOP_USER_DELETIONS != 2:
    RUN_BLOCKERS.append("invalid_predeclared_tail_grid")
model_rows, sample_rows, missing_rows, investor_balance, pre_balance = [], [], [], [], []
wave_rows, joint_rows, design_issues, threshold_rows = [], [], [], []
preperiod_status = "not_run"
polynomial_scaling = []
if not RUN_BLOCKERS:
    df, polynomial_scaling = prepare_wave_cell_design(df)
    df, preperiod_status = add_preperiod_targets(df)
    base_samples, _ = select_design_samples(df, None)
    positive_base = base_samples["W5"].loc[base_samples["W5"]["portfolio_size_raw"].gt(0)]
    reference_sd = positive_base[[CORE_X_VAR] + PRE_TARGETS + INVESTOR_TARGETS].std()
    capital_cutoffs = {}
    for fraction in TAIL_FRACTIONS:
        capital_cutoffs[fraction] = positive_base.groupby("wave")["portfolio_size_raw"].quantile(1 - fraction)
        threshold_rows.extend([[fraction, wave, value] for wave, value in capital_cutoffs[fraction].items()])
    for y_name in ACTIVE_Y_VARS:
        samples, _ = select_design_samples(df, y_name)
        broad = samples["W5"]
        common, audit, missing = select_trait_sample(broad)
        sample_rows.append([short_y(y_name)] + audit)
        missing_rows.extend([[short_y(y_name)] + r for r in missing if r[1] or r[2] != "-"])
        # No model-dependent dropping: invalid portfolio terms skip this outcome.
        required = ["size_detail_cell"] + WAVE_LINEAR + WAVE_POLY + WAVE_AMOUNT
        bad = common[required].isna().any(axis=1)
        bad |= ~np.isfinite(common[required[1:]].to_numpy(dtype=float)).all(axis=1)
        if bad.any():
            design_issues.append([short_y(y_name), int(bad.sum()), "invalid_common_design_all_models_skipped"])
            continue
        # core: A-E; other batches repeat only C/E anchors (22 baseline fits).
        models = list(AUDIT_SPECS) if RUN_BATCH == "core" else ["C", "E"]
        for model in models:
            spec = AUDIT_SPECS[model]
            run = broad if model == "A" else common
            baseline = estimate_rf(run, y_name, spec, {}, capture=RUN_BATCH == "tail")
            exposure = baseline.pop("_exposure", None)
            user_scores = baseline.pop("_user_score", None)
            baseline.update(model=model, scenario="base", removed_N=0, lost_cells=0)
            baseline_gain_cells = set(common.groupby("size_detail_cell", observed=True)[CORE_X_VAR].nunique().loc[lambda x: x > 1].index)
            model_rows.append(baseline)
            if model not in ["C", "E"]:
                continue
            if RUN_BATCH == "core":
                positive = common.loc[common["portfolio_size_raw"].gt(0)]
                row = estimate_rf(positive, y_name, spec, {})
                row.update(model=model, scenario="positive", removed_N=len(common)-len(positive),
                           lost_cells=common["size_detail_cell"].nunique()-positive["size_detail_cell"].nunique())
                model_rows.append(row)
                prior = "pre_" + y_name
                # Same outcome's prior only: 22 checks, not an 11x11 cross-product.
                rows = balance_diagnostics(common, df, "W5", y_name, "final", spec,
                    "size_detail_cell", targets=[prior], scopes=["positive"])
                for row in scale_audit_balance(rows, reference_sd):
                    row.update(model=model)
                pre_balance.extend(rows)
                paired = positive.loc[pd.to_numeric(positive[prior], errors="coerce").replace([np.inf, -np.inf], np.nan).notna()]
                row = estimate_rf(paired, y_name, spec, {})
                row.update(model=model, scenario="prior_subset_current", removed_N=len(common)-len(paired),
                           lost_cells=common["size_detail_cell"].nunique()-paired["size_detail_cell"].nunique())
                model_rows.append(row)
            elif RUN_BATCH == "tail" and exposure is not None:
                for scenario, trimmed in tail_subsets(common, exposure, user_scores, capital_cutoffs):
                    row = estimate_rf(trimmed, y_name, spec, {})
                    row.update(model=model, scenario=scenario, removed_N=len(common)-len(trimmed),
                        lost_cells=common["size_detail_cell"].nunique()-trimmed["size_detail_cell"].nunique(),
                        lost_gain_cells=len(baseline_gain_cells - set(trimmed.groupby("size_detail_cell", observed=True)[CORE_X_VAR].nunique().loc[lambda x: x > 1].index)))
                    model_rows.append(row)
            elif RUN_BATCH == "wave":
                for wave in WAVES:
                    reduced = common.loc[common["wave"].ne(wave)]
                    row = estimate_rf(reduced, y_name, spec, {})
                    row.update(model=model, scenario="omit_"+wave, removed_N=len(common)-len(reduced),
                        lost_cells=common["size_detail_cell"].nunique()-reduced["size_detail_cell"].nunique(),
                        lost_gain_cells=len(baseline_gain_cells - set(reduced.groupby("size_detail_cell", observed=True)[CORE_X_VAR].nunique().loc[lambda x: x > 1].index)))
                    if len(reduced) == len(common):
                        row["note"] = row["note"] or "omitted_wave_absent_no_new_evidence"
                    model_rows.append(row)
                if not baseline["note"]:
                    rows, joint = wave_effects(common, y_name, spec)
                    wave_rows.extend(rows)
                    joint_rows.append(joint)
        if RUN_BATCH == "core":
            # Independent prior traits: cell and portfolio-only adjustment on the
            # actual common sample. Do not mechanically control the trait tested.
            for adjustment, spec, layer in [("cell", MODEL_SPECS["M0"], "cell"),
                                             ("portfolio", MODEL_SPECS["W3"], "final")]:
                rows = balance_diagnostics(common, df, "W5", y_name, layer, spec,
                    "size_detail_cell", targets=INVESTOR_TARGETS, scopes=["positive"])
                for row in scale_audit_balance(rows, reference_sd):
                    row.update(adjustment=adjustment)
                audit_holm(rows, [], family_size=5)
                investor_balance.extend(rows)
        # Only one outcome's dense frame/models in memory at a time.
        del common, broad, samples
        gc.collect()
    audit_holm(model_rows, ["model", "scenario"])
    audit_holm(wave_rows, ["model", "scenario"])
    audit_holm(joint_rows, ["model"])
    audit_holm(pre_balance, ["model"])

# === CELL 9: Report - settings and integrity ===
section("CELL 9: v19 settings and integrity")
COMPUTE_STAGE_TIMES = list(STAGE_TIMES)
ant_print_all(pd.Series(["=== REPORT BEGIN ===", RUN_ID, SCRIPT_REVISION]), model_method="unique")
render_table("01 Settings", ["setting", "value"], [
    ["revision/batch", SCRIPT_REVISION + "/" + RUN_BATCH],
    ["gate", "BLOCK" if RUN_BLOCKERS else "PASS"], ["blockers", ";".join(RUN_BLOCKERS) or "none"],
    ["planned maximum fits", {"core":99, "tail":154, "wave":154}.get(RUN_BATCH, 0)],
    ["batch core", "55 A-E + 22 positive + 22 prior-subset current; 110 trait + 22 prior checks"],
    ["batch tail", "22 C/E anchors + 88 tail + 44 separate user deletions"],
    ["batch wave", "22 C/E anchors + 110 omit-wave + 22 interaction fits"],
    ["A / B", "cell only; broad / common complete sample"],
    ["C / D / E", "B + traits / C + wave polynomial / D + wave amount"],
    ["traits", "age/college/gender/city tier/firm age/registration/broad industry"],
    ["cell/scaling", "fixed five-wave 10/3/3 and BASE scaling; never rerank after deletion"],
    ["gain unit", "passive gain per 10000 yuan"], ["SE", SE_TYPE],
    ["return version / NAV screen", EXPECTED_FUND_RETURN_VERSION + "/" + str(APPLY_NAV_QUALITY_SCREEN)],
    ["timing/history", TIMING_RULE + "; full coverage; 12 months"],
    ["prior timing", preperiod_status],
    ["limits", "current trait stability assumed; user clustering does not resolve common funds"],
])
render_table("01 Design issues", ["Y", "invalid_N", "note"], design_issues)
for title in ["CORE 1 Addon Resolution Policy and Integrity", "CORE 1 Shock Window Calendar"]:
    if title in TABLE_BUFFER:
        render_table("01 " + title, *TABLE_BUFFER[title])

# === CELL 10: Report - samples and thresholds ===
section("CELL 10: Common sample audit")
render_table("02 Samples", ["Y", "broad_N", "basic_N", "common_N", "lost_basic", "lost_extension",
    "positive_N", "recorded0", "absent0", "note"], sample_rows)
render_table("02 Missing traits", ["Y", "field", "N", "note"], missing_rows)
if RUN_BATCH == "tail":
    render_table("02 Predetermined capital cutoffs", ["fraction", "wave", "yuan_cutoff"], threshold_rows)
ant_print_all(pd.Series([
    "Common sample is per outcome, not intersection of all eleven answers.",
    "Current traits require stability assumptions; no employment outcome controls.",
    "Prior responses never filter baseline; stock q2 has no outcome and is not filled.",
    "Zero holders do not supply direct gain variation but may affect shared control slopes.",
]), model_method="unique")

# === CELL 11: Report - estimates and exact refits ===
section("CELL 11: Outcome estimates")
render_table("03 Estimates", ["Y", "model", "scenario", "N", "users", "positive_N", "beta", "SE", "p", "Holm", "CI95", "note"],
    [[short_y(r["Y"]), r["model"], r["scenario"], r["n_obs"], r["n_users"], r["n_positive"]] +
     [fmt_float(r[k], 6) for k in ["beta", "se", "p", "holm_p"]] + [ci_text(r), r["note"] or "-"]
     for r in model_rows], max_width=140, rows_per_block=22)
if RUN_BATCH in ["tail", "wave"]:
    render_table("03 Deletion coverage", ["Y", "model", "scenario", "removed_N", "lost_cells", "lost_gain_cells"],
        [[short_y(r["Y"]), r["model"], r["scenario"], r["removed_N"], r["lost_cells"], r.get("lost_gain_cells", 0)]
         for r in model_rows if r["scenario"] != "base"], max_width=120, rows_per_block=22)
ant_print_all(pd.Series([
    "Holm within eleven outcomes per model/scenario; unavailable p padded with 1.",
    "No adjustment makes searching across specifications valid; report all scenarios.",
    "capital_5/10: above BASE wave 99.5/99 percentile; boundary ties retained.",
    "residual_5/10: remove ceil(0.5/1 percent positive N) largest baseline residual SS.",
    "user_1/2: separate exact refits deleting all waves of each top absolute-score user.",
    "User-score ranking uses Y: sensitivity diagnostic, not a new primary sample.",
    "No IDs released. Every deletion refits FE/controls/SE with fixed original cells.",
    "lost_gain_cells counts baseline cells losing within-cell raw gain variation (including removed cells).",
]), model_method="unique")

# === CELL 12: Report - identifying variation ===
section("CELL 12: Residual variation")
ident_rows = [r for r in model_rows if "identification" in r]
render_table("04 Variation", ["Y", "model", "scenario", "residual_SS", "residual_SD", "retained_SS", "top1pct_pos_SS", "max_obs_SS"],
    [[short_y(r["Y"]), r["model"], r["scenario"]] +
     [fmt_float(r["identification"]["totals"][k], 6) for k in
      ["residual_SS", "residual_SD", "retained_SS", "top1pct_positive_SS", "max_obs_SS"]] for r in ident_rows],
    max_width=140, rows_per_block=22)
# Group decompositions are restricted to anchors, not repeated for every refit.
render_table("04 Anchor wave contributions", ["Y", "model", "wave", "N", "SS_share", "beta_part"],
    [[short_y(r["Y"]), r["model"], g[1], g[2], fmt_float(g[4],6), fmt_float(g[5],6)]
     for r in ident_rows if r["scenario"] == "base" and r["model"] in ["C", "E"]
     for g in r["identification"]["groups"] if g[0] == "wave"], max_width=120, rows_per_block=22)
ant_print_all(pd.Series(["SS contribution is not an independent subgroup effect; top1pct counts positive holders, not gains."]), model_method="unique")

# === CELL 13: Report - investor balance on actual common samples ===
section("CELL 13: Dated investor balance, core batch")
render_table("05 Prior traits", ["Y", "adjust", "trait", "N", "missing", "std", "CI_low", "CI_high", "p", "Holm", "note"],
    [[r["Y"],r["adjustment"],r["trait"].replace("pre_aer_bal_", ""),r["n_obs"],r["dropped"]] +
     [fmt_float(r[k],6) for k in ["std_effect","std_low","std_high","p","holm_p"]] + [r["note"] or "-"]
     for r in investor_balance], max_width=140, rows_per_block=22)
ant_print_all(pd.Series([
    "Only core runs this table. Same actual common sample; positive prior-available subsets.",
    "cell vs portfolio-only W3: no tested investor trait is deliberately controlled away.",
    "Holm within five traits per outcome/adjustment. Common BASE SD, standardized slopes.",
    "No pre-q2 observations; missing/absorbed/nonsignificant is not proof of balance.",
]), model_method="unique")

# === CELL 14: Report - prior expectations or wave heterogeneity ===
section("CELL 14: Prior expectations and wave tests")
render_table("06 Own prior expectation", ["Y","model","N","missing","std","CI_low","CI_high","p","Holm","note"],
    [[r["Y"],r["model"],r["n_obs"],r["dropped"]] +
     [fmt_float(r[k],6) for k in ["std_effect","std_low","std_high","p","holm_p"]] + [r["note"] or "-"]
     for r in pre_balance], max_width=140, rows_per_block=22)
render_table("06 Wave slopes", ["Y","model","wave","N_wave","beta","SE","p","Holm","CI95","note"],
    [[short_y(r["Y"]),r["model"],r["scenario"],r["n_obs"]] +
     [fmt_float(r[k],6) for k in ["beta","se","p","holm_p"]] + [ci_text(r),r["note"] or "-"]
     for r in wave_rows], max_width=140, rows_per_block=22)
render_table("06 Equal wave slopes Wald", ["Y","model","N_total","estimable_waves","p","Holm","note"],
    [[short_y(r["Y"]),r["model"],r["n_obs"],r["waves"],fmt_float(r["p"],6),fmt_float(r["holm_p"],6),r["note"] or "-"]
     for r in joint_rows], max_width=140, rows_per_block=22)
ant_print_all(pd.Series([
    "Prior: same outcome, immediately previous scheduled answer strictly pre-shock; no backfill.",
    "Compare prior_subset_current in Cell 11 on exactly the same positive prior subset.",
    "Wave slopes are one interaction regression with shared trait slopes; cluster by user.",
    "Stock q2 absent; equality test uses estimable observed waves, never an invented zero slope.",
]), model_method="unique")

# === CELL 15: Report - compute budget ===
section("CELL 15: Timing and fit counts")
render_table("07 Fit counts", ["type","fits"], list(FIT_COUNTS.items()))
render_table("07 Timing", ["stage","seconds"], [[n,fmt_float(v,2)] for n,v in STAGE_TIMES])

# === CELL 16: Report - optional preparation appendix ===
section("CELL 16: Preparation appendix")
if OUTPUT_MODE == "full":
    for title in ["Source Read Summary", "Duplicate Key Diagnostics Before Deduplication",
                  "CORE 2 Survey Timing and Duplicate Audit", "CORE 2 Holding Match and Zero Portfolio Provenance"]:
        if title in TABLE_BUFFER:
            render_table("APPENDIX " + title, *TABLE_BUFFER[title])
else:
    ant_print_all(pd.Series(["Preparation appendix omitted; all requested results remain in batch tables."]), model_method="unique")
ant_print_all(pd.Series(["=== REPORT END ===", RUN_ID, SCRIPT_REVISION]), model_method="unique")
