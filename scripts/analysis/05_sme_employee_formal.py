# === CELL 1: Imports and output helpers ===
"""SME-employee expectations reduced-form regression for the Ant platform."""

import gc
import hashlib
import time
import textwrap

import numpy as np
import pandas as pd
from scipy.stats import norm

from marvel.AntPrint import ant_read_data, ant_print_all


TABLE_BUFFER = {}
HISTOGRAM_ROWS = []
HISTOGRAM_AUDIT = []
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
    """Buffer aggregate summaries; all output is in the final reporting cells."""
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
SCRIPT_REVISION = "sme_employee_formal_v6"
RUN_ID = "employee_formal_gain_current_traits"
WAVES = ["2024q3", "2024q4", "2025q1", "2025q2"]

SE_TYPE = "cluster_user"  # Required for this formal workflow.
OUTPUT_MODE = "compact"  # Preparation audit compatibility; final report is complete.
TIMING_RULE = "post_window_only"  # audit_only shows timing but blocks estimates
MIN_REG_N = 30  # Small samples are explicitly skipped.
HOLDING_BATCH_USERS = 5000
ANSWER_SECONDS_MIN = 100
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
OUTCOME_AUDIT = []
ROUTE_AUDIT = []
RUN_BLOCKERS = []

Y_VARS = ["exp_gdp", "exp_house", "exp_cpi", "exp_rate", "exp_stock"]
QUESTION_CODES = {
    "2024q3": ["v32", "v33", "v34", "v35", "v36"],
    "2024q4": ["v18", "v19", "v20", "v21", "v22"],
    "2025q1": ["v18", "v19", "v20", "v21", "v22"],
    "2025q2": ["v18", "v19", "v20", "v21", "v22"],
}
EDU_CODE = {"2024q3": "v39", "2024q4": "v25", "2025q1": "v26", "2025q2": "v26"}
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
# Align with 04: ambiguous education labels remain missing.
EDUCATION_REFUSAL = ["不便透露", "不愿回答", "拒绝回答", "不确定", "不清楚"]


# Sensitivity-only categories; ambiguous labels never become college=1.
EDUCATION_CATEGORY_MAP = {
    "小学及以下": "primary", "初中": "junior",
    "高中_普通高中_成人高中_职业高中_中专_技校": "upper_secondary",
    "大学专科_专科_高职高专_技师学院": "college",
    "大学专科_高职高专_技师学院": "college",
    "大学本科": "bachelor", "研究生及以上": "graduate",
    MIXED_EDUCATION: "mixed",
}
EDUCATION_CATEGORY_LEVELS = ["primary", "junior", "upper_secondary", "college",
                             "bachelor", "graduate", "mixed", "refusal", "blank", "other"]

DIAG_ROWS = []

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


def get_survey_cols(wave):
    return ["user_id", "submit_id", "submit_date", "extro_info", "v1", "v2", "v3",
            "user_age", "city_level_from_yicai", EDU_CODE[wave]] + QUESTION_CODES[wave]


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


def code_employee_survey(data, wave):
    nonowner = clean_text(data["v1"]).eq("我不是小微经营者").fillna(False)
    explicit = clean_text(data["v2"]).eq("作为小微经营户的雇员_帮助其收付款").fillna(False)
    working = clean_text(data["v3"]).eq("我在工作").fillna(False)
    employee = nonowner & (explicit | working)
    data["sme_employee"] = employee.astype(int)
    ROUTE_AUDIT.append([wave, int(nonowner.sum()), int((nonowner & explicit).sum()),
                        int((nonowner & working).sum()), int((employee & explicit & working).sum()),
                        int(employee.sum())])
    age = pd.to_numeric(data["user_age"], errors="coerce")
    data["aer_bal_age"] = age  # Same numeric conversion as 04; no employee-only age gate.
    edu = clean_text(data[EDU_CODE[wave]])
    data["aer_bal_college"] = edu.map(EDUCATION_MAP)
    data["education_category"] = edu.map(EDUCATION_CATEGORY_MAP).fillna("other")
    data.loc[edu.isin(EDUCATION_REFUSAL), "education_category"] = "refusal"
    data.loc[edu.isna(), "education_category"] = "blank"
    unknown = employee & edu.notna() & ~edu.isin(EDUCATION_REFUSAL) & ~edu.isin(EDUCATION_MAP)
    # Like 04, unknown education is audited and left missing, not a run blocker.
    TRAIT_CODING_ROWS.append([wave, int(employee.sum()), int((employee & edu.isna()).sum()),
        int((employee & edu.isin(EDUCATION_REFUSAL)).sum()), int((employee & edu.eq(MIXED_EDUCATION)).sum()),
        int(unknown.sum())])
    mappings = [GDP, HOUSE, CPI, RATE, STOCK_Q3 if wave == "2024q3" else STOCK_LATER]
    for outcome, code, mapping in zip(Y_VARS, QUESTION_CODES[wave], mappings):
        answer = clean_text(data[code])
        data[outcome] = answer.map(mapping)
        unexpected = employee & answer.notna() & ~answer.isin(UNKNOWN_ANSWERS) & data[outcome].isna()
        if unexpected.any():
            RUN_BLOCKERS.append("unmapped_" + wave + "_" + outcome)
        OUTCOME_AUDIT.append([wave, outcome, code, int((employee & data[outcome].notna()).sum()),
                              int((employee & answer.isin(UNKNOWN_ANSWERS)).sum()), int(unexpected.sum())])
    return data



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
    df_wave[USER_COL] = df_wave[USER_COL].astype("string").str.strip()
    df_wave["wave"] = wave
    surveys[wave] = df_wave
    read_rows.append([wave, "survey", df_wave.shape[0], df_wave.shape[1]])

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
    svy = code_employee_survey(extract_answer_seconds(svy), wave)
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
        fmt_int(tmp["sme_employee"].sum()), fmt_int(tmp["answer_seconds"].notna().sum()),
        fmt_int(short_answer.sum()),
    ])

emit_table(
    "Survey Construction Summary",
    ["wave", "rows", "users", "sme_employee", "answer_n", "answer_lt_min"],
    survey_summary_rows,
)

# === CELL 6: Aggregate fund-level shock and controls to users ===

section("CELL 6: Aggregate shock and controls")

# Bound the holdings x 12 months expansion by processing employee batches.
user_parts = []
for wave in WAVES:
    needed_users = survey_panel.loc[survey_panel["wave"].eq(wave) & survey_panel["sme_employee"].eq(1), USER_COL]
    month_holding = holding.loc[holding["month_p"].eq(WAVE_HOLDING_MONTH[wave]) & holding[USER_COL].isin(needed_users)]
    codes, employees = pd.factorize(month_holding[USER_COL], sort=False)
    for offset in range(0, len(employees), HOLDING_BATCH_USERS):
        batch = month_holding.loc[(codes >= offset) & (codes < offset + HOLDING_BATCH_USERS)]
        shock_user = aggregate_shock_to_user(shock, batch, wave)
        control_user = aggregate_control_to_user(control, batch, wave)
        user_wave = shock_user.merge(control_user, on=USER_COL, how="left", validate="one_to_one")
        user_wave["wave"] = wave
        user_parts.append(user_wave)
        del batch, shock_user, control_user, user_wave
    del month_holding, codes, employees
    gc.collect()
user_columns = [USER_COL, "wave", "portfolio_size_raw", "portfolio_size_usable",
    "portfolio_size", "return_coverage", "control_coverage", "control_min_coverage",
    "control_n_months", "portfolio_risk_12m", "expected_ret_12m", PASSIVE_RET_PREDICTOR,
    PASSIVE_GAIN_PREDICTOR, REALIZED_RETURN_PREDICTOR, REALIZED_GAIN_COL]
user_panel = pd.concat(user_parts, ignore_index=True) if user_parts else pd.DataFrame(columns=user_columns)
if not user_parts:
    RUN_BLOCKERS.append("no_employee_holdings_to_aggregate")
del user_parts, holding, shock, control
# Drop references to the large raw tables before regressions.
del portrait_raw, portrait_diag, portrait
for temporary in ["wave_holding", "wave_shock", "df_wave", "svy"]:
    globals().pop(temporary, None)
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

df["sample_sme_employee"] = df["sme_employee"].eq(1)
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
        df["wave"].eq(wave) & df["sample_sme_employee"] & df["sample_answer_time"]
    ]
    before_or_on_end = tmp["submit_dt"].notna() & tmp["shock_window_end"].notna() & ~tmp["timing_after_window"]
    timing_rows.append([
        wave, fmt_int(len(tmp)), fmt_int(tmp["submit_dt"].isna().sum()),
        fmt_int(before_or_on_end.sum()), fmt_int(tmp["timing_after_window"].sum()),
        fmt_int((~tmp["sample_unique_user_wave"]).sum()),
    ])
emit_table(
    "CORE 2 Survey Timing and Duplicate Audit",
    ["wave", "employees_after_answer", "missing_submit", "on_or_before_end", "after_end", "duplicate_rows"],
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
    df["sample_sme_employee"]
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
# Fixed cell ranks before outcome or employee-control selection.
cell_base["size_detail_cell"] = cell_base["analysis_portfolio_cell"]

df = df.merge(
    cell_base[[
        USER_COL, "wave", "analysis_size_bin", "analysis_risk_bin",
        "analysis_eret_bin", "portfolio_cell_status",
        "analysis_portfolio_cell", "size_detail_cell",
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


# === CELL 8: Memory-bounded estimation and report helpers ===

EMPLOYEE_NUM = ["aer_bal_age", "aer_bal_college"]
EMPLOYEE_CAT = ["portrait_gender", "city_level_from_yicai"]
EMPLOYEE_COLS = EMPLOYEE_NUM + EMPLOYEE_CAT
FORMAL_MODELS = ["Wave FE", "Cell FE", "Cell FE + employee controls"]
BALANCE_MODELS = ["No controls", "Wave FE", "Cell FE"]
MAX_CATEGORY_LEVELS = 80


def within_array(values, groups):
    """Absorb a single FE partition without materializing its dummy matrix."""
    counts = np.bincount(groups)
    sums = np.zeros((len(counts), values.shape[1]), dtype=float)
    np.add.at(sums, groups, values)
    return values - (sums / counts[:, None])[groups]


def compact_fit(data, outcome, model, numeric_controls=None, categorical_controls=None):
    """OLS with absorbed FE and exact full-design rank CR1 correction.

    Gain is first column. SVD handles collinear employee dummies; inference is
    skipped if gain is not estimable. Only small aggregate results are returned.
    """
    n = len(data)
    result = dict(N=n, users=data[USER_COL].nunique(), beta=np.nan, se=np.nan,
                  p=np.nan, low=np.nan, high=np.nan, note="", rank=0)
    if n < MIN_REG_N or result["users"] < 2:
        result["note"] = "insufficient_observations_or_clusters"
        return result
    gain = data[CORE_X_VAR].to_numpy(dtype=float)
    y = data[outcome].to_numpy(dtype=float)
    columns = [gain]
    if model == "Cell FE + employee controls":
        for col in (EMPLOYEE_NUM if numeric_controls is None else numeric_controls):
            columns.append(data[col].to_numpy(dtype=float))
        for col in (EMPLOYEE_CAT if categorical_controls is None else categorical_controls):
            labels = data[col].astype(str)
            levels = sorted(labels.unique())
            if len(levels) > MAX_CATEGORY_LEVELS:
                result["note"] = "unexpected_category_count:" + col
                return result
            columns.extend(labels.eq(level).to_numpy(dtype=float) for level in levels[1:])
    x = np.column_stack(columns)
    if model == "No controls":
        groups = np.zeros(n, dtype=int)
    else:
        fe = "wave" if model == "Wave FE" else "size_detail_cell"
        groups = pd.factorize(data[fe], sort=False)[0]
    if not np.isfinite(x).all() or not np.isfinite(y).all() or (groups < 0).any():
        result["note"] = "invalid_estimation_inputs"
        return result
    x = within_array(x, groups)
    y = within_array(y[:, None], groups)[:, 0]
    # Normalize columns for reliable rank detection across units.
    scale = np.sqrt(np.sum(x*x, axis=0))
    if scale[0] <= 1e-12 * max(1.0, np.linalg.norm(gain)):
        result["note"] = "no_residual_gain_variation"
        return result
    scale[scale < 1e-14] = 1.0
    x /= scale
    u, singular, vt = np.linalg.svd(x, full_matrices=False)
    keep = singular > max(x.shape) * np.finfo(float).eps * singular[0]
    rank = int(keep.sum())
    full_rank = len(np.unique(groups)) + rank
    result["rank"] = full_rank
    basis = vt[keep]
    e0 = np.zeros(x.shape[1]); e0[0] = 1.0
    if not np.allclose(basis.T @ basis[:, 0], e0, atol=1e-8):
        result["note"] = "gain_collinear_with_controls"
        return result
    if n <= full_rank:
        result["note"] = "no_residual_degrees_of_freedom"
        return result
    coefficients = basis.T @ ((u[:, keep].T @ y) / singular[keep])
    residual = y - x @ coefficients
    # First row of the pseudoinverse; cluster only the gain influence scores.
    gain_weights = (u[:, keep] @ (basis[:, 0] / singular[keep])) / scale[0]
    cluster = pd.factorize(data[USER_COL], sort=False)[0]
    scores = np.bincount(cluster, weights=gain_weights * residual)
    correction = result["users"] / (result["users"] - 1) * (n - 1) / (n - full_rank)
    beta = float(coefficients[0] / scale[0])
    se = float(np.sqrt(np.sum(scores*scores) * correction))
    p = float(2*norm.sf(abs(beta/se))) if se > 0 else np.nan
    result.update(beta=beta, se=se, p=p, low=beta-1.96*se, high=beta+1.96*se)
    if not np.isfinite(p):
        result["note"] = "degenerate_cluster_variance"
    return result


def distribution_rows(data, scope, variables):
    rows = []
    for variable in variables:
        v = pd.to_numeric(data[variable], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        q = v.quantile([.01,.10,.50,.90,.99])
        rows.append([scope, variable, len(v), len(data)-len(v), v.mean(), v.std()] + q.tolist())
    return rows


def model_row(scope, outcome, model, result):
    return [scope, outcome, model] + [result[k] for k in ["N","users","beta","se","p","low","high","note"]]


def balance_rows(data, scope, target_specs):
    """Contemporaneous traits; all holdings in the common sample; identical rows across 3 models.

    Per-trait SD scaling is computed before adjustment and held across columns.
    All category levels are tested as indicators, never ordinal category codes.
    """
    rows = []
    for trait, level in target_specs:
        sample = data.loc[data[trait].notna(), [USER_COL, CORE_X_VAR, "wave", "size_detail_cell", trait]].copy()
        if level is None:
            sample["balance_target"] = pd.to_numeric(sample[trait], errors="coerce")
            label = trait
        else:
            sample["balance_target"] = sample[trait].astype(str).eq(level).astype(float)
            label = trait + "=" + str(level)
        sd_y = sample["balance_target"].std()
        sd_g = sample[CORE_X_VAR].std()
        factor = sd_g/sd_y if pd.notna(sd_y) and sd_y > 0 else np.nan
        for model in BALANCE_MODELS:
            r = compact_fit(sample, "balance_target", model)
            rows.append([scope, label, model, r["N"], r["users"],
                         r["beta"], r["se"], r["p"], r["beta"]*factor,
                         r["low"]*factor, r["high"]*factor,
                         "constant_trait" if not np.isfinite(factor) else r["note"]])
        del sample
    return rows


def final_table(title, headers, rows):
    formatted = [[fmt_float(v,6) if isinstance(v,(float,np.floating)) else str(v) for v in row] for row in rows]
    render_table(title, headers, formatted, max_width=136, rows_per_block=18)


def prepare_exposure_histograms(base):
    """One integer bin per actual employee-wave; never expand aggregate counts."""
    rows, audit = [], []
    positive = base["portfolio_size_raw"].gt(0)
    for variable, column, factor in [("gain", CORE_X_VAR, 10000.0),
                                      ("holding", "portfolio_size_raw", 1.0)]:
        values = pd.to_numeric(base.loc[positive, column], errors="coerce").to_numpy(dtype=float) * factor
        finite = np.isfinite(values)
        missing = int((~finite).sum())
        values = values[finite]
        for scale in ["RMB", "signed_log10_1p" if variable == "gain" else "log10_RMB"]:
            key = variable + "_" + scale
            status = "reported" if len(values) else "empty"
            audit.append([key, int(positive.sum()), len(values), missing,
                          int((values == 0).sum()), status])
            if not len(values):
                continue
            transformed = (np.sign(values) * np.log10(1 + np.abs(values))
                           if scale == "signed_log10_1p" else
                           np.log10(values) if scale == "log10_RMB" else values)
            lo, hi = float(transformed.min()), float(transformed.max())
            edges = (np.linspace(lo, hi, 21) if hi > lo else np.array([lo - .5, hi + .5]))
            codes = np.searchsorted(edges[1:-1], transformed, side="right").astype(np.int16)
            counts = np.bincount(codes, minlength=len(edges)-1)
            for j, count in enumerate(counts):
                rows.append([key, j+1, format(edges[j], ".17g"), format(edges[j+1], ".17g"), int(count), count/len(values)])
    return rows, audit


# === CELL 9: Sample accounting, distributions, regressions and balance ===
section("CELL 9: Compute employee analysis")
# Only slim employee-wave data survive into estimation. No fitted model cache.
retain = list(dict.fromkeys([USER_COL, "wave", CORE_X_VAR, "size_detail_cell",
    "portfolio_size_raw", "portfolio_risk_12m", "expected_ret_12m",
    "recorded_zero_portfolio", "imputed_zero_portfolio", "analysis_base_sample",
    "sample_sme_employee", "sample_answer_time", "sample_unique_user_wave", "sample_timing",
    "sample_portfolio_rule", "sample_core_x_nonmissing", "sample_return_complete",
    "sample_control_complete", "sample_cell_inputs", "education_category"] + EMPLOYEE_COLS + Y_VARS))
df = df[retain].copy()
for col in EMPLOYEE_NUM + Y_VARS + [CORE_X_VAR]:
    df[col] = pd.to_numeric(df[col], errors="coerce").replace([np.inf,-np.inf],np.nan)
for col in EMPLOYEE_CAT:
    df[col] = clean_text(df[col])
# Drop lingering construction-frame aliases.
for temporary in ["tmp", "base_tmp", "cell_base", "cell_size", "wave_base"]:
    globals().pop(temporary, None)
gc.collect()

model_results, sample_results, sample_wave_results = [], [], []
numeric_distributions, category_distributions, gain_by_outcome = [], [], []
missing_controls, balance_full, balance_summary = [], [], []
flow_rows = []
employee_mask = df["sample_sme_employee"].fillna(False).copy()
flow_rows.append(["employees", int(employee_mask.sum())])
for flag in ["sample_answer_time","sample_unique_user_wave","sample_timing",
             "sample_portfolio_rule","sample_core_x_nonmissing","sample_return_complete"]:
    employee_mask &= df[flag].fillna(False)
    flow_rows.append([flag, int(employee_mask.sum())])
wave_mask = employee_mask & df[USER_COL].notna() & df["wave"].notna()
cell_mask = wave_mask & df["sample_control_complete"].fillna(False) & df["sample_cell_inputs"].fillna(False) & df["size_detail_cell"].notna()
common_mask = cell_mask & df[EMPLOYEE_COLS].notna().all(axis=1)
flow_rows += [["cell_eligible",int(cell_mask.sum())],["employee_controls_complete",int(common_mask.sum())]]
balance_specs = [(name, None) for name in EMPLOYEE_NUM]
expected_balance_labels = set(EMPLOYEE_NUM)
for category_column in EMPLOYEE_CAT:
    observed_categories = sorted(df.loc[cell_mask, category_column].dropna().astype(str).unique())
    if len(observed_categories) > MAX_CATEGORY_LEVELS:
        RUN_BLOCKERS.append("unexpected_category_count:" + category_column)
    for category_value in observed_categories:
        balance_specs.append((category_column, category_value))
        expected_balance_labels.add(category_column + "=" + category_value)
for c in EMPLOYEE_COLS:
    missing_controls.append([c,int(cell_mask.sum()),int((cell_mask & df[c].isna()).sum())])
if (CORE_X_VAR != PASSIVE_GAIN_PREDICTOR or not ENFORCE_CONTROL_COMPLETENESS
        or TIMING_RULE != "post_window_only" or SE_TYPE != "cluster_user"
        or (N_SIZE_BIN,N_RISK_BIN,N_ERET_BIN) != (10,3,3)):
    RUN_BLOCKERS.append("invalid_formal_design_settings")
RUN_BLOCKERS = list(dict.fromkeys(RUN_BLOCKERS))
if not common_mask.any():
    RUN_BLOCKERS.append("empty_employee_common_sample")
if not RUN_BLOCKERS:
    base = df.loc[common_mask]
    HISTOGRAM_ROWS, HISTOGRAM_AUDIT = prepare_exposure_histograms(base)
    core_variables = [CORE_X_VAR,"portfolio_size_raw","portfolio_risk_12m","expected_ret_12m"]
    numeric_distributions.extend(distribution_rows(base,"BASE_all",core_variables + ["aer_bal_age"]))
    numeric_distributions.extend(distribution_rows(base.loc[base["portfolio_size_raw"].gt(0)],"BASE_positive",core_variables))
    for wave in WAVES:
        for label, mask in [("all",base["wave"].eq(wave)),("positive",base["wave"].eq(wave) & base["portfolio_size_raw"].gt(0))]:
            numeric_distributions.extend(distribution_rows(base.loc[mask],wave+"_"+label,[CORE_X_VAR]))
    for c in EMPLOYEE_CAT + ["aer_bal_college"]:
        for level, n in base[c].value_counts(dropna=False).items():
            category_distributions.append(["BASE",c,str(level),int(n),n/len(base) if len(base) else np.nan])
    for scope, mask in [("BASE",common_mask)] + [(y,common_mask & df[y].notna()) for y in Y_VARS]:
        common = df.loc[mask]
        if scope == "BASE":
            gain_by_outcome.append(["BASE",len(common),int(common["portfolio_size_raw"].gt(0).sum()),
                int(common["recorded_zero_portfolio"].sum()),int(common["imputed_zero_portfolio"].sum())])
        if scope != "BASE":
            y = scope
            available_wave = wave_mask & df[y].notna()
            available_cell = cell_mask & df[y].notna()
            sample_results.append([y,int(available_wave.sum()),int(available_cell.sum()),len(common),len(common),common[USER_COL].nunique(),int(available_wave.sum()-available_cell.sum()),int(available_cell.sum()-len(common))])
            for w in WAVES:
                wm = df["wave"].eq(w)
                sample_wave_results.append([y,w,int((available_wave & wm).sum()),int((available_cell & wm).sum()),int((mask & wm).sum())])
            numeric_distributions.extend(distribution_rows(common,y,[y]))
            numeric_distributions.extend(distribution_rows(common,y+"_gain",[CORE_X_VAR]))
            gain_by_outcome.append([y,len(common),int(common["portfolio_size_raw"].gt(0).sum()),int(common["recorded_zero_portfolio"].sum()),int(common["imputed_zero_portfolio"].sum())])
            for model, available in zip(FORMAL_MODELS,[available_wave,available_cell,mask]):
                result = compact_fit(common,y,model)
                model_results.append(model_row("Common sample",y,model,result))
                if available.equals(mask):
                    own = result
                else:
                    own = compact_fit(df.loc[available],y,model)
                model_results.append(model_row("Available sample",y,model,own))
        rows = balance_rows(common, scope, balance_specs)
        for adjustment in BALANCE_MODELS:
            labels_fitted = [r[1] for r in rows if r[2] == adjustment]
            if set(labels_fitted) != expected_balance_labels or len(labels_fitted) != len(expected_balance_labels):
                RUN_BLOCKERS.append("balance_target_mismatch:" + scope + ":" + adjustment)
        if RUN_BLOCKERS:
            break
        balance_full.extend(rows)
        for model in BALANCE_MODELS:
            selected = [r for r in rows if r[2]==model]
            valid = [r for r in selected if np.isfinite(r[7]) and np.isfinite(r[8]) and not r[11]]
            balance_summary.append([scope,model,len(selected),len(valid),sum(r[7]<.05 for r in valid),max([abs(r[8]) for r in valid],default=np.nan),min([r[3] for r in valid],default=0),max([r[3] for r in valid],default=0)])
        del common, rows
        gc.collect()
    del base


# === CELL 10: Control completeness and education selection diagnostics ===
# All diagnostics use the original fixed cells and the four-wave 100-second mask.
SELECTION_CONTROL_ORDER = ["aer_bal_age", "aer_bal_college", "portrait_gender", "city_level_from_yicai"]
LIGHT_CONTROLS = ["aer_bal_age", "portrait_gender", "city_level_from_yicai"]
selection_missing, selection_wave, selection_profile = [], [], []
selection_variation, selection_models = [], []
selection_checks = []


def selection_fit_row(topic, stage, sample, numeric_controls=None):
    model = "Cell FE" if stage in ["A_wide", "B_complete"] else "Cell FE + employee controls"
    fit = compact_fit(sample, topic, model, numeric_controls=numeric_controls)
    return [topic, stage, fit["N"], fit["users"], fit["beta"], fit["se"],
            fit["p"], fit["low"], fit["high"], fit["note"] or "ok"]


if not RUN_BLOCKERS:
    for topic in Y_VARS:
        wide = df.loc[cell_mask & df[topic].notna()].copy()
        missing = wide[SELECTION_CONTROL_ORDER].isna()
        # Exact mutually exclusive pattern; 1 means missing in age/college/gender/city order.
        pattern = missing.astype(int).astype(str).agg("".join, axis=1)
        for code, count in pattern.value_counts().sort_index().items():
            selection_missing.append([topic, code, int(count)])
        complete = ~missing.any(axis=1)
        light = wide[LIGHT_CONTROLS].notna().all(axis=1)
        selection_checks.append([topic, len(wide), int(complete.sum()), int((~complete).sum()),
                                 int(pattern.value_counts().sum()), int(light.sum()),
                                 int((light & ~complete).sum())])
        # Reference residuals use the full wide outcome sample, then partition that same SS.
        ref_residual = wide[CORE_X_VAR] - wide.groupby("size_detail_cell")[CORE_X_VAR].transform("mean")
        ref_ss = ref_residual.pow(2).sum()
        for scope, mask in [("wide", pd.Series(True, index=wide.index)),
                            ("kept", complete), ("dropped", ~complete)]:
            sample = wide.loc[mask]
            for wave in WAVES:
                part = sample.loc[sample.wave.eq(wave)]
                selection_wave.append([topic, scope, wave, len(part)])
            gain = sample[CORE_X_VAR]
            quantiles = gain.quantile([.01, .5, .99])
            selection_profile.append([
                topic, scope, len(sample), sample[USER_COL].nunique(),
                int(sample.portfolio_size_raw.gt(0).sum()),
                int(sample.recorded_zero_portfolio.sum()), int(sample.imputed_zero_portfolio.sum()),
                sample[topic].mean(), gain.mean(), gain.std(),
                quantiles.loc[.01], quantiles.loc[.5], quantiles.loc[.99]])
            own_residual = gain - sample.groupby("size_detail_cell")[CORE_X_VAR].transform("mean")
            own_ss = own_residual.pow(2).sum()
            users_ss = own_residual.pow(2).groupby(sample[USER_COL]).sum().sort_values(ascending=False)
            sizes = sample.groupby("size_detail_cell").size()
            reference_part = ref_residual.loc[mask].pow(2).sum()
            selection_variation.append([
                topic, scope, len(sizes), int(sizes.eq(1).sum()),
                int(sample.groupby("size_detail_cell")[CORE_X_VAR].nunique().gt(1).sum()),
                reference_part, reference_part/ref_ss if ref_ss > 0 else np.nan,
                own_ss, users_ss.iloc[0]/own_ss if own_ss > 0 else np.nan,
                users_ss.head(5).sum()/own_ss if own_ss > 0 else np.nan])
        # A/B/C isolate sample selection and control adjustment. E1/E2 isolate education.
        for stage, mask, numeric in [
            ("A_wide", pd.Series(True, index=wide.index), None),
            ("B_complete", complete, None),
            ("C_full_controls", complete, None),
            ("E1_light_sample", light, ["aer_bal_age"]),
            ("E2_complete_light", complete, ["aer_bal_age"]),
        ]:
            selection_models.append(selection_fit_row(topic, stage, wide.loc[mask], numeric))


# Education sensitivity: preserve the same fixed cells, outcomes and light masks.
# Codes only are released; no raw labels or respondent-level answers are emitted.
education_counts, education_models = [], []
if not RUN_BLOCKERS:
    for topic in Y_VARS:
        wide = df.loc[cell_mask & df[topic].notna()].copy()
        light = wide[LIGHT_CONTROLS].notna().all(axis=1)
        complete = wide[EMPLOYEE_COLS].notna().all(axis=1)
        for wave in WAVES:
            for category in EDUCATION_CATEGORY_LEVELS:
                mask = wide.wave.eq(wave) & wide.education_category.eq(category)
                # Include zeros so each stage has a fixed, auditable denominator.
                education_counts.append([topic, wave, category, int(mask.sum()),
                    int((mask & light).sum()), int((mask & complete).sum())])
        for stage, mask, cats in [
            ("R1_light_noedu", light, EMPLOYEE_CAT),
            ("R2_light_categories", light, EMPLOYEE_CAT + ["education_category"]),
            ("R3_complete_noedu", complete, EMPLOYEE_CAT),
            ("R4_complete_categories", complete, EMPLOYEE_CAT + ["education_category"]),
        ]:
            fit = compact_fit(wide.loc[mask], topic, "Cell FE + employee controls",
                              numeric_controls=["aer_bal_age"], categorical_controls=cats)
            education_models.append([topic, stage] + [fit[k] for k in
                ["N", "users", "beta", "se", "p", "low", "high"]] + [fit["note"] or "ok"])


# === CELL 11: Prepare reports and output helpers ===
# Fixed four reporting cells, no cursor, continuation or manual repetition.
# Cells 1-10 compute aggregates; Cells 12-20 emit all reports.
REPORT_BLOCKS = [[], [], [], []]
REPORT_LIMIT = 36000  # UTF-8 payload; leaves headroom below platform 50KB.
REPORT_ROWS_PER_CALL = 40  # unique output observed to truncate at 100 items.
REPORT_CALL_OVERHEAD = 512  # Conservative reserve per platform output call.
REPORT_CELL_BUDGET = 44000  # Payload + chunk headers + per-call reserve.
REPORT_ERRORS = []


def report_value(value):
    if isinstance(value, (float, np.floating)):
        return format(value, ".4g") if np.isfinite(value) else "NA"
    return str(value).replace("\n", " ").replace("|", "/")


def compact_table(block, title, headers, rows):
    lines = REPORT_BLOCKS[block]
    rows = [[report_value(v) for v in row] for row in rows]
    # As in script 01: small tables with aligned columns and repeated headers.
    # Use local widths per page to avoid padding every page for one long label.
    for start in range(0, max(1, len(rows)), 12):
        page = rows[start:start + 12]
        widths = [max([len(str(h))] + [len(r[j]) for r in page])
                  for j, h in enumerate(headers)]
        lines.append(f"{title} ({start+1}-{start+len(page)} of {len(rows)})")
        lines.append("  ".join(str(h).ljust(w) for h,w in zip(headers,widths)).rstrip())
        for row in page:
            lines.append("  ".join(v.ljust(w) for v,w in zip(row,widths)).rstrip())


# Codes eliminate repeated long labels without changing targets or estimates.
OUTCOME_CODES = {y: "Y"+str(i+1) for i,y in enumerate(Y_VARS)}
TRAIT_CODES = {t: "T"+str(i+1) for i,t in enumerate(dict.fromkeys(r[1] for r in balance_full))}
MODEL_CODES = {"No controls":"Raw", "Wave FE":"Wave", "Cell FE":"Cell",
               "Cell FE + employee controls":"Employee"}
REPORT_BLOCKS[0] += ["=== EMPLOYEE FORMAL REPORT ===", SCRIPT_REVISION, "Waves: 2024q3, 2024q4, 2025q1, 2025q2; all five expectations",
    f"Minimum observed answer time = {ANSWER_SECONDS_MIN} seconds (inclusive). Missing durations retained.",
    "N=employee-wave observations; U=employees; gain unit=RMB10,000; user-cluster CR1 SE.",
    "Main samples common within outcome. Available samples supplementary. No cross-outcome intersection.",
    "Balance=current traits, common sample including both zero sources; Raw/Wave/Cell; no previous-wave restriction.",
    "Employee controls: age, college, gender and city tier. Current survey traits.",
    "Numeric output: 4 significant digits; p=NA means unavailable, not a pass.",
    "STATUS="+("BLOCKED" if RUN_BLOCKERS else "COMPLETED")]
compact_table(0,"Outcome key",["code","outcome"],[[code,y] for y,code in OUTCOME_CODES.items()])
compact_table(0,"Blocking issues",["issue"],[[x] for x in RUN_BLOCKERS] or [["none"]])
compact_table(0,"Funnel",["step","N"],flow_rows)
compact_table(0,"Sample accounting",["Y","WaveN","CellN","EmployeeN","CommonN","U","historyDrop","employeeDrop"],
    [[OUTCOME_CODES[r[0]]]+r[1:] for r in sample_results])
compact_table(0,"Sample by wave",["Y","wave","WaveN","CellN","CommonN"],
    [[OUTCOME_CODES[r[0]]]+r[1:] for r in sample_wave_results])
compact_table(0,"Control missingness (not additive)",["control","cellN","missing"],missing_controls)
compact_table(0,"Holdings",["Y","N","positive","recorded0","unmatched0"],
    [[OUTCOME_CODES.get(r[0],r[0])]+r[1:] for r in gain_by_outcome])
compact_table(0,"All formal regressions",["sample","Y","model","N","U","beta","SE","p","note"],
    [["Main" if r[0]=="Common sample" else "Available",OUTCOME_CODES[r[1]],MODEL_CODES[r[2]]]+r[3:8]+[r[10]] for r in model_results])
REPORT_BLOCKS[0].append("95% coefficient CI = beta +/- 1.96 SE. No repeated CI columns.")

compact_table(1,"Distributions",["scope","variable","N","missing","mean","SD","P1","P10","P50","P90","P99"],numeric_distributions)
compact_table(1,"Category shares",["scope","variable","category","N","share"],category_distributions)
compact_table(1,"Histogram eligibility (positive complete-control BASE)",
    ["panel","positiveN","finiteN","missing","zeros","status"], HISTOGRAM_AUDIT)
REPORT_BLOCKS[1] += ["Histograms: full finite positive-holder BASE; no trimming or winsorization; gain converted to RMB.",
    "Recorded-zero and unmatched-as-zero holdings excluded; their counts remain in Holdings/distributions.",
    "20 equal-width bins per plotted scale (one if constant). Counts include all finite observations.",
    "Bins [lower,upper), final bin includes upper. Log panels are transformed-variable counts, not RMB density.",
    "signed_log10_1p = sign(gain_RMB)*log10(1+abs(gain_RMB)); holding transform=log10(RMB).",
    "Rebuild charts locally from these printed bin edges and counts."]
compact_table(1,"Histogram bins (bounds on named scale)",
    ["panel","bin","lower","upper","N","share"], HISTOGRAM_ROWS)
compact_table(1,"Identity routes",["wave","nonowner","v2","v3","both","employee"],ROUTE_AUDIT)
compact_table(1,"Education coding",["wave","N","missing","refusal","mixed","unmapped"],TRAIT_CODING_ROWS)
compact_table(1,"Outcome coding",["wave","outcome","code","mapped","uncertain","unmapped"],OUTCOME_AUDIT)
REPORT_BLOCKS[1].append("History mean/risk missing for zero holdings; raw holdings missing for unmatched users. Gain is zero-coded.")

compact_table(2,"Balance target key",["code","target"],[[code,trait] for trait,code in TRAIT_CODES.items()])
REPORT_BLOCKS[2] += ["BASE balance: current traits in the full common BASE. Category indicators tested separately.",
    "Each fit shows unscaled beta, employee-clustered SE and p per RMB 10,000 higher gain.",
    "Age in years. Indicator beta x 100 gives percentage points."]
base_rows = [r for r in balance_full if r[0]=="BASE"]
base_compact = []
base_standardized = []
for trait in dict.fromkeys(r[1] for r in base_rows):
    rr = [r for r in base_rows if r[1]==trait]
    values = []
    standardized = []
    for model in BALANCE_MODELS:
        r = next(r for r in rr if r[2]==model)
        values += [r[5],r[6],r[7]]
        standardized += [r[8], (r[10]-r[9])/3.92, r[7]]
    notes = ";".join(dict.fromkeys(r[11] for r in rr if r[11]))
    base_standardized.append([TRAIT_CODES[trait],rr[0][3],rr[0][4]]+standardized+[notes])
    base_compact.append([TRAIT_CODES[trait],rr[0][3],rr[0][4]]+values+[notes])
compact_table(2,"BASE balance",["T","N","U","Raw_b","Raw_se","Raw_p","Wave_b","Wave_se","Wave_p","Cell_b","Cell_se","Cell_p","note"],base_compact)

compact_table(2,"BASE balance standardized: SD(gain)/SD(trait)",
    ["T","N","U","Raw_b","Raw_se","Raw_p","Wave_b","Wave_se","Wave_p","Cell_b","Cell_se","Cell_p","note"],
    base_standardized)

REPORT_BLOCKS[3] += ["Outcome-specific balance summary: all tests retained in computation; detailed BASE above.",
    "Counts use unadjusted p-values. Category tests are dependent."]
compact_table(3,"Balance coverage",["Y","model","planned","valid","p<.05","maxAbsStdB","minN","maxN"],
    [[OUTCOME_CODES.get(r[0],r[0]),MODEL_CODES[r[1]]] + r[2:] for r in balance_summary])
# Preserve missing/constant/failed-test coverage in aggregate without listing
# the same status hundreds of times.
failures = {}
for r in balance_full:
    if r[11]:
        key = (OUTCOME_CODES.get(r[0],r[0]),r[11])
        failures[key] = failures.get(key,0)+1
compact_table(3,"Balance unavailable checks",["Y","reason","fits"],[list(k)+[v] for k,v in failures.items()])
# Full preparation tables duplicate facts above. Retain integrity status, cell
# construction and timing, not raw-read and repeated coverage descriptions.
for title,(headers,rows) in TABLE_BUFFER.items():
    if title in ["CORE 1 Shock Window Calendar","CORE 1 Holding Snapshot Date Audit",
                 "CORE 2 Survey Timing and Duplicate Audit","Portfolio Cell Construction Audit"]:
        compact_table(3,title,headers,rows)
compact_table(3,"Stage seconds",["stage","seconds"],STAGE_TIMES)
REPORT_BLOCKS[3].append("=== REPORT COMPLETE: FOUR FIXED OUTPUT CELLS ===")
# Balance the expanded, readable report across four physical cells. Preserve
# order; numbered rows and repeated table headings identify continuation.
all_report_lines = [line for block in REPORT_BLOCKS for line in block]
target_bytes = sum(len(line.encode("utf-8")) + 12 for line in all_report_lines) / 4
REPORT_BLOCKS = [[], [], [], []]
block_index, block_bytes = 0, 0
for line in all_report_lines:
    line_bytes = len(line.encode("utf-8")) + 12
    if block_index < 3 and block_bytes >= target_bytes:
        block_index += 1
        block_bytes = 0
    REPORT_BLOCKS[block_index].append(line)
    block_bytes += line_bytes
# Preflight every call and the cumulative cell budget before any output.
# Platform unique output can silently cap each call at 100 items: bytes alone
# are insufficient. All numbered result lines are retained in batches of 40.
REPORT_CALLS = []
for i,lines in enumerate(REPORT_BLOCKS):
    numbered = [f"{i+1}.{j+1}|{line}" for j,line in enumerate(lines)]
    REPORT_BLOCKS[i] = numbered
    size = len("\n".join(numbered).encode("utf-8"))
    if size > REPORT_LIMIT:
        REPORT_ERRORS.append(f"Report block {i+1}: {size} UTF-8 bytes exceeds {REPORT_LIMIT}; report layout requires revision.")
    calls = []
    chunks = (len(numbered) + REPORT_ROWS_PER_CALL - 1) // REPORT_ROWS_PER_CALL
    for offset in range(0, len(numbered), REPORT_ROWS_PER_CALL):
        end = min(offset + REPORT_ROWS_PER_CALL, len(numbered))
        header = f"REPORT BLOCK {i+1}/4 CHUNK {len(calls)+1}/{chunks} ROWS {offset+1}-{end}/{len(numbered)}"
        calls.append([header] + numbered[offset:end])
    budget = sum(len("\n".join(call).encode("utf-8")) + REPORT_CALL_OVERHEAD for call in calls)
    if budget > REPORT_CELL_BUDGET:
        REPORT_ERRORS.append(f"Report block {i+1}: {budget} bytes including call reserves exceeds {REPORT_CELL_BUDGET}.")
    REPORT_CALLS.append(calls)


def emit_report_block(index):
    if REPORT_ERRORS:
        if index == 0:
            ant_print_all(pd.Series(["REPORT PREFLIGHT FAILED; no partial success report."]+REPORT_ERRORS),model_method="unique")
    else:
        # Multiple short calls in the SAME physical cell; no manual repetition.
        for call in REPORT_CALLS[index]:
            ant_print_all(pd.Series(call),model_method="unique")



def emit_selection_report(block, tables):
    lines = [SCRIPT_REVISION + " SELECTION " + block,
             "Fixed four-wave 100s cells. Gain unit RMB10000. Employee-cluster CR1.",
             "Y1=GDP Y2=house Y3=CPI Y4=rate Y5=stock; raw p-values."]
    if RUN_BLOCKERS:
        lines.append("BLOCKED: see formal report issues")
    else:
        for title, headers, rows in tables:
            lines.append(title)
            for start in range(0, max(1, len(rows)), 12):
                lines.append(" ".join(headers))
                for row in rows[start:start+12]:
                    values = [OUTCOME_CODES.get(v, v) if isinstance(v, str) else v for v in row]
                    lines.append(" ".join(report_value(v) for v in values))
        lines.append("END SELECTION " + block)
    # Reserve space for every call header as well as payload.
    budget = sum(len(line.encode("utf-8")) + 12 for line in lines) + 512*((len(lines)+37)//38)
    if budget > REPORT_CELL_BUDGET:
        ant_print_all(pd.Series(["BLOCK SELECTION "+block+": output budget exceeded"]), model_method="unique")
        return
    for start in range(0, len(lines), 38):
        numbered = [str(i+1)+" "+line for i,line in enumerate(lines[start:start+38], start)]
        ant_print_all(pd.Series(["SELECTION "+block+" rows "+str(start+1)+"-"+str(start+len(numbered))+
                                 "/"+str(len(lines))] + numbered), model_method="unique")


# === CELL 12: Formal report 1 of 4 ===
emit_report_block(0)

# === CELL 13: Formal report 2 of 4 ===
emit_report_block(1)

# === CELL 14: Formal report 3 of 4 ===
emit_report_block(2)

# === CELL 15: Formal report 4 of 4 ===
emit_report_block(3)

# === CELL 16: Selection report S1 - counts, missing patterns and waves ===
emit_selection_report("S1", [
    ("Accounting", ["Y","wide","kept","dropped","pattern_total","light","light_loses_education"], selection_checks),
    ("Missing pattern: age college gender city; 1=missing", ["Y","pattern","N"], selection_missing),
    ("Wave composition", ["Y","scope","wave","N"], selection_wave)])


# === CELL 17: Selection report S2 - composition and gain variation ===
emit_selection_report("S2", [
    ("Gain/expectation profiles", ["Y","scope","N","U","positive","recorded0","unmatched0",
                                  "Ymean","gain_mean","gain_sd","gain_p01","gain_p50","gain_p99"], selection_profile),
    ("Reference SS partition uses wide-cell means; own SS and top shares re-demean within each scope",
     ["Y","scope","cells","singletons","varying_cells","refSS","refSS_share","ownSS","top1_user_share","top5_user_share"],
     selection_variation)])


# === CELL 18: Selection report S3 - sample and education decomposition ===
emit_selection_report("S3", [
    ("A/B: pure Cell; C: full controls; E1: light sample+age/gender/city; E2: complete sample+age/gender/city",
     ["Y","stage","N","U","beta","SE","p","CI_low","CI_high","note"], selection_models)])


# === CELL 19: Education report S4 - categories by wave and sample stage ===
emit_selection_report("S4", [
    ("Education categories by wave; wide/light/complete are nested, not additive. Zero rows retained.",
     ["Y", "wave", "education", "wide", "light", "complete"], education_counts),
    ("Codes: primary/junior/upper_secondary/college/bachelor/graduate are explicit categories; mixed is ambiguous.",
     ["code", "meaning"], [["refusal", "nonresponse_or_uncertain"], ["blank", "empty_field"],
                            ["other", "unreviewed_label"]])])


# === CELL 20: Education report S5 - fixed-sample categorical education sensitivity ===
emit_selection_report("S5", [
    ("All fits: Cell+age/gender/city. R1/R2 same light sample; R3/R4 same complete sample.",
     ["Y", "stage", "N", "U", "beta", "SE", "p", "CI_low", "CI_high", "note"], education_models),
    ("R2/R4 add education category dummies. R2 retains mixed/refusal/blank/other separately; no numeric ordering.",
     ["comparison", "meaning"], [["R1_to_R2", "same_sample_category_adjustment"],
                                ["R2_to_R4", "complete_case_selection_same_category_spec"],
                                ["R3_to_R4", "same_complete_sample_category_adjustment"],
                                ["C_full_controls", "unchanged_binary_college_main_spec_in_S3"]])])
