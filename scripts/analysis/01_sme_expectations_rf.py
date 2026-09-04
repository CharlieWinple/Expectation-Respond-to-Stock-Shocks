# === CELL 1: Imports and output helpers ===
"""SME-owner expectations reduced-form regression for the Ant platform."""

import gc

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

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


def emit_table(title, columns, rows):
    section(title)
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
WAVES = ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"]

SE_TYPE = "HC1"
MIN_REG_N = 30
ANSWER_SECONDS_MIN = 180
MIN_RETURN_COVERAGE = 0.999999
MIN_CONTROL_COVERAGE = 0.999999
MIN_CONTROL_MONTHS = 12

STOCK_INITIAL_LEVEL = 2748.92

KEEP_ZERO_PORTFOLIO = False
CORE_X_CHOICE = "passive_return"  # passive_return, passive_gain, realized_return

N_SIZE_BIN = 10
N_RISK_BIN = 5
N_ERET_BIN = 5

REG_FE_NAMES = ["wave", "analysis_portfolio_cell"]
# Optional FE candidates: "city_level_from_yicai", "portrait_gender", "survey_industry".
REG_CONTROL_NAMES = [
    "aer_bal_age", "aer_bal_college",
    "aer_bal_firm_age", "aer_bal_company",
]
# Optional control candidate: "aer_bal_employee_n".
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
        "user_age", "city_level_from_yicai", "v5",
    ],
    "2024q3": [
        "user_id", "submit_id", "submit_date", "v1", "extro_info",
        "user_age", "city_level_from_yicai", "v5",
    ],
    "2024q4": [
        "user_id", "submit_id", "submit_date", "v1", "extro_info",
        "user_age", "city_level_from_yicai", "v5",
    ],
    "2025q1": [
        "user_id", "submit_id", "submit_date", "v1", "extro_info",
        "user_age", "city_level_from_yicai", "v5",
    ],
    "2025q2": [
        "user_id", "submit_id", "submit_date", "v1", "extro_info",
        "user_age", "city_level_from_yicai", "v5",
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

SHOCK_RET_PP_COL = "shock_ret_rate_pp"
SHOCK_USABLE_COL = "shock_usable"
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
CORE_X_BY_CHOICE = {
    "passive_return": PASSIVE_RET_PREDICTOR,
    "passive_gain": PASSIVE_GAIN_PREDICTOR,
    "realized_return": REALIZED_RETURN_PREDICTOR,
}
CORE_X_VAR = CORE_X_BY_CHOICE[CORE_X_CHOICE]

DIAG_ROWS = []
ADDON_UNMAPPED_ROWS = []

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

DETAIL_COEF_NAMES = [CORE_X_VAR] + REG_CONTROL_NAMES

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


def get_survey_cols(wave):
    cols = list(SURVEY_BASE_COLS_BY_WAVE[wave])
    for y_name in Y_VARS:
        v_code = EXP_VCODES.get(y_name, {}).get(wave)
        if v_code is not None:
            cols.append(v_code)
    for trait_name in ["education", "firm_year", "registration", "employee_n"]:
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
    out["aer_bal_employee_n"] = pd.to_numeric(
        clean_text(out[TRAIT_VCODES["employee_n"][wave]]), errors="coerce"
    )
    out["city_level_from_yicai"] = clean_text(out["city_level_from_yicai"])
    out["survey_industry"] = clean_text(out["v5"])
    return out


def map_expectations(df, wave):
    out = df.copy()
    for y_name in Y_VARS:
        v_code = EXP_VCODES.get(y_name, {}).get(wave)
        if v_code is None or v_code not in out.columns:
            continue
        mapped = clean_text(out[v_code]).map(EXP_MAPPING[y_name])
        out[y_name] = 100 * mapped / STOCK_INITIAL_LEVEL if y_name == "exp_stock" else mapped
    return out


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
    return out[[USER_COL, "portrait_gender"]].drop_duplicates(USER_COL, keep="first")


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
    merged["shock_weighted_pp"] = merged["holding_amt"] * merged[SHOCK_RET_PP_COL].where(merged["shock_usable"])
    user = (
        merged.groupby(USER_COL, as_index=False)
        .agg(
            portfolio_size=("holding_amt", lambda x: x.sum(min_count=1)),
            realized_gain=(REALIZED_GAIN_COL, lambda x: x.sum(min_count=1)),
            shock_matched_holding=("shock_matched_holding", "sum"),
            shock_weighted_pp=("shock_weighted_pp", lambda x: x.sum(min_count=1)),
            n_funds=(FUND_COL_HOLDING, "nunique"),
            n_shock_matched=("shock_matched", "sum"),
            n_shock_usable=("shock_usable", "sum"),
        )
    )
    user["return_coverage"] = safe_ratio(user["shock_matched_holding"], user["portfolio_size"])
    user[PASSIVE_RET_PREDICTOR] = safe_ratio(user["shock_weighted_pp"], user["portfolio_size"])
    user[PASSIVE_GAIN_PREDICTOR] = user["shock_weighted_pp"] / 100
    user[REALIZED_RETURN_PREDICTOR] = 100 * safe_ratio(
        user[REALIZED_GAIN_COL], user["portfolio_size"]
    )
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


def add_rank_bin(df, value_col, n_bins, out_col):
    df[out_col] = np.ceil(df[value_col].rank(method="first", pct=True) * n_bins).clip(1, n_bins).astype("Int64")
    return df


def build_portfolio_cells(df):
    out = df.copy()
    out = add_rank_bin(out, "portfolio_size", N_SIZE_BIN, "analysis_size_bin")
    out = add_rank_bin(out, "portfolio_risk_12m", N_RISK_BIN, "analysis_risk_bin")
    out = add_rank_bin(out, "expected_ret_12m", N_ERET_BIN, "analysis_eret_bin")
    out["analysis_portfolio_cell"] = (
        out["analysis_size_bin"].astype("string") + "_"
        + out["analysis_risk_bin"].astype("string") + "_"
        + out["analysis_eret_bin"].astype("string")
    )
    return out


def enabled_existing(names, df):
    return [name for name in names if name in df.columns]


def fill_zero_portfolio_rows(df):
    out = df.copy()
    zero_cols = [
        "portfolio_size", "shock_matched_holding", "shock_weighted_pp",
        "n_funds", "n_shock_matched", "n_shock_usable",
        "return_coverage", PASSIVE_RET_PREDICTOR, PASSIVE_GAIN_PREDICTOR,
        REALIZED_GAIN_COL, REALIZED_RETURN_PREDICTOR, "control_coverage",
        "control_min_coverage", "control_n_months", "portfolio_risk_12m",
        "expected_ret_12m", "n_control_matched",
    ]
    zero_portfolio = out["portfolio_size"].isna() | out["portfolio_size"].eq(0)
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


def run_rf(df, y_name):
    fe_names = enabled_existing(REG_FE_NAMES, df)
    control_names = enabled_existing(REG_CONTROL_NAMES, df)
    cols = [y_name, CORE_X_VAR] + fe_names + control_names
    run = df.loc[df["analysis_base_sample"].eq(1), cols].copy()
    for col in [y_name, CORE_X_VAR] + control_names:
        run[col] = pd.to_numeric(run[col], errors="coerce")
    for col in fe_names:
        run[col] = as_formula_object(run[col])
    run = run.replace([np.inf, -np.inf], np.nan).dropna()
    fe_terms = []
    fe_diag = {}
    for fe_name in fe_names:
        n_fe = run[fe_name].nunique(dropna=True)
        fe_diag[f"{fe_name}_fe"] = "yes" if n_fe >= 2 else "no"
        fe_diag[f"{fe_name}_n"] = n_fe
        if n_fe >= 2:
            fe_terms.append(f"C({fe_name})")
    if len(run) < MIN_REG_N:
        summary = {
            "Y": y_name, "n_obs": len(run), "beta": np.nan, "se": np.nan,
            "t": np.nan, "p": np.nan, "R2": np.nan, "note": "skip_n",
            "core_x": CORE_X_VAR,
        }
        summary.update(fe_diag)
        detail = [
            {
                "Y": y_name, "variable": name, "coef": np.nan, "se": np.nan,
                "t": np.nan, "p": np.nan, "note": "skip_n",
            }
            for name in DETAIL_COEF_NAMES
        ]
        return summary, detail
    formula = f"{y_name} ~ " + " + ".join([CORE_X_VAR] + fe_terms + control_names)
    model = smf.ols(formula, data=run).fit(cov_type=SE_TYPE)
    summary = {
        "Y": y_name,
        "n_obs": int(model.nobs),
        "beta": float(model.params.get(CORE_X_VAR, np.nan)),
        "se": float(model.bse.get(CORE_X_VAR, np.nan)),
        "t": float(model.tvalues.get(CORE_X_VAR, np.nan)),
        "p": float(model.pvalues.get(CORE_X_VAR, np.nan)),
        "R2": float(model.rsquared),
        "note": "",
        "core_x": CORE_X_VAR,
    }
    summary.update(fe_diag)
    detail = []
    for name in DETAIL_COEF_NAMES:
        detail.append({
            "Y": y_name,
            "variable": name,
            "coef": float(model.params.get(name, np.nan)),
            "se": float(model.bse.get(name, np.nan)),
            "t": float(model.tvalues.get(name, np.nan)),
            "p": float(model.pvalues.get(name, np.nan)),
            "note": "",
        })
    return summary, detail


def normalize_rf_output(y_name, output):
    if isinstance(output, tuple) and len(output) == 2:
        summary, detail = output
    elif isinstance(output, dict):
        summary = output
        detail = []
    else:
        summary = {
            "Y": y_name, "n_obs": np.nan, "beta": np.nan, "se": np.nan,
            "t": np.nan, "p": np.nan, "R2": np.nan,
            "note": "invalid_run_output",
        }
        detail = []

    if not isinstance(summary, dict):
        summary = {
            "Y": y_name, "n_obs": np.nan, "beta": np.nan, "se": np.nan,
            "t": np.nan, "p": np.nan, "R2": np.nan,
            "note": "invalid_summary",
        }
    summary.setdefault("Y", y_name)
    summary.setdefault("n_obs", np.nan)
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

shock = ant_read_data(
    SHOCK_TABLE,
    cols=[FUND_COL_PANEL, WAVE_COL, SHOCK_RET_PP_COL, SHOCK_USABLE_COL],
).copy()
shock = prepare_panel_keys(shock)
read_rows.append(["all", "shock", shock.shape[0], shock.shape[1]])

control = ant_read_data(
    PORT_CONTROL_TABLE,
    cols=[FUND_COL_PANEL, WAVE_COL, CONTROL_MONTH_COL, CONTROL_MONTHLY_RET_COL],
).copy()
control = prepare_panel_keys(control)
read_rows.append(["all", "control", control.shape[0], control.shape[1]])

portrait = ant_read_data(
    PORTRAIT_TABLE,
    cols=[USER_COL, PORTRAIT_GENDER_COL],
).copy()
portrait = prep_portrait(portrait)
read_rows.append(["all", "portrait", portrait.shape[0], portrait.shape[1]])

holding = ant_read_data(
    HOLDING_TABLE,
    cols=[
        USER_COL, FUND_COL_HOLDING, HOLDING_AMT_COL,
        REALIZED_GAIN_MONTH_COL, HOLDING_DATE_COL,
    ],
).copy()
holding = prep_holding(holding)
holding = holding.loc[holding["month_p"].isin(set(WAVE_HOLDING_MONTH.values()))].copy()
read_rows.append(["all", "holding", holding.shape[0], holding.shape[1]])

emit_table(
    "Source Read Summary",
    ["wave", "source", "rows", "cols"],
    [[w, s, fmt_int(r), fmt_int(c)] for w, s, r, c in read_rows],
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
        fmt_float(tmp["portfolio_size"].mean(), 2),
        fmt_float(tmp["return_coverage"].mean(), 4),
        fmt_float(tmp["control_coverage"].mean(), 4),
        fmt_float(tmp["control_min_coverage"].mean(), 4),
        fmt_float(tmp["control_n_months"].mean(), 2),
        fmt_int(tmp[PASSIVE_RET_PREDICTOR].notna().sum()),
        fmt_int(tmp[PASSIVE_GAIN_PREDICTOR].notna().sum()),
        fmt_int(tmp[REALIZED_RETURN_PREDICTOR].notna().sum()),
        fmt_int(tmp["portfolio_risk_12m"].notna().sum()),
    ])

emit_table(
    "User-Level Shock and Control Summary",
    [
        "wave", "rows", "users", "mean_port", "ret_cov", "ctrl_cov",
        "ctrl_min_cov", "ctrl_months", "R_nonmiss", "Pgain_nonmiss",
        "realR_nonmiss", "risk_nonmiss",
    ],
    coverage_rows,
)


# === CELL 7: Define base sample and portfolio cells ===

section("CELL 7: Define sample and portfolio cells")

df = survey_panel.merge(user_panel, on=[USER_COL, "wave"], how="left", validate="many_to_one")
if KEEP_ZERO_PORTFOLIO:
    df = fill_zero_portfolio_rows(df)

df["sample_sme_owner"] = df["sme_owner"].eq(1)
df["sample_answer_time"] = df["answer_seconds"].isna() | df["answer_seconds"].ge(ANSWER_SECONDS_MIN)
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
    & df["sample_portfolio_rule"]
    & df["sample_core_x_nonmissing"]
).fillna(False).astype(int)

cell_base = df.loc[
    df["analysis_base_sample"].eq(1)
    & df["portfolio_size"].notna()
    & df["portfolio_risk_12m"].notna()
    & df["expected_ret_12m"].notna(),
    [USER_COL, "wave", "portfolio_size", "portfolio_risk_12m", "expected_ret_12m"],
].copy()
cell_base_n_before_dedup = len(cell_base)
cell_base = cell_base.drop_duplicates([USER_COL, "wave"], keep="first").copy()
cell_base_n_dup = cell_base_n_before_dedup - len(cell_base)
cell_base = build_portfolio_cells(cell_base)

df = df.merge(
    cell_base[[
        USER_COL, "wave", "analysis_size_bin", "analysis_risk_bin",
        "analysis_eret_bin", "analysis_portfolio_cell",
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

for fe_name in REG_FE_NAMES:
    if fe_name in df.columns:
        df[f"sample_fe_{fe_name}"] = df[fe_name].notna()
for control_name in REG_CONTROL_NAMES:
    if control_name in df.columns:
        df[f"sample_control_{control_name}"] = df[control_name].notna()

base_steps = [
    ("1_sme_owner", df["sample_sme_owner"]),
    ("2_answer_time", df["sample_answer_time"]),
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
for wave in WAVES:
    wave_base = df.loc[df["wave"].eq(wave)]
    for step, n_remaining, n_dropped in sample_after_steps(wave_base, base_steps):
        dropped_text = "-" if n_dropped == "-" else fmt_int(n_dropped)
        sample_rows.append([wave, step, fmt_int(n_remaining), dropped_text])

emit_table(
    "Sample Size Sequential Funnel",
    ["scope", "step", "n_remaining", "n_dropped"],
    sample_rows,
)

outcome_sample_rows = []
reg_variable_cols = [CORE_X_VAR] + enabled_existing(REG_CONTROL_NAMES, df) + enabled_existing(REG_FE_NAMES, df)
for y_name in Y_VARS:
    run_base = df.loc[df["analysis_base_sample"].eq(1)].copy()
    y_nonmiss = run_base.loc[run_base[y_name].notna()]
    all_reg_vars = y_nonmiss.loc[
        y_nonmiss[reg_variable_cols].replace([np.inf, -np.inf], np.nan).notna().all(axis=1)
    ]
    outcome_sample_rows.append([
        y_name,
        fmt_int(len(run_base)),
        fmt_int(len(y_nonmiss)),
        fmt_int(len(run_base) - len(y_nonmiss)),
        fmt_int(len(all_reg_vars)),
        fmt_int(len(y_nonmiss) - len(all_reg_vars)),
    ])

emit_table(
    "Outcome Regression Sample Size",
    ["Y", "base_n", "Y_nonmiss_n", "Y_missing_drop", "reg_ready_n", "reg_var_drop"],
    outcome_sample_rows,
)


# === CELL 8: Reduced-form regressions ===

section("CELL 8: Reduced-form regressions")

emit_table(
    "Active Regression Settings",
    ["setting", "value"],
    [
        ["CORE_X_CHOICE", CORE_X_CHOICE],
        ["CORE_X_VAR", CORE_X_VAR],
        ["KEEP_ZERO_PORTFOLIO", str(KEEP_ZERO_PORTFOLIO)],
        ["SE_TYPE", SE_TYPE],
        ["MIN_REG_N", fmt_int(MIN_REG_N)],
        ["REG_FE_NAMES", ", ".join(REG_FE_NAMES)],
        ["REG_CONTROL_NAMES", ", ".join(REG_CONTROL_NAMES)],
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

rf_outputs = [normalize_rf_output(y_name, run_rf(df, y_name)) for y_name in Y_VARS]
result_columns = [
    "Y", "n_obs", "beta", "se", "t", "p", "R2", "note", "core_x",
]
for fe_name in REG_FE_NAMES:
    result_columns += [f"{fe_name}_fe", f"{fe_name}_n"]
results = pd.DataFrame(
    [summary for summary, _ in rf_outputs],
    columns=result_columns,
)
detail_results = pd.DataFrame(
    [row for _, detail_rows in rf_outputs for row in detail_rows],
    columns=["Y", "variable", "coef", "se", "t", "p", "note"],
)

emit_table(
    "Detailed RF Coefficients",
    ["Y", "variable", "coef", "se", "t", "p", "note"],
    [
        [
            row["Y"], row["variable"], fmt_float(row["coef"], 5),
            fmt_float(row["se"], 5), fmt_float(row["t"], 3),
            fmt_float(row["p"], 4), row["note"],
        ]
        for _, row in detail_results.iterrows()
    ],
)

fe_diag_rows = []
for _, row in results.iterrows():
    for fe_name in REG_FE_NAMES:
        fe_diag_rows.append([
            row["Y"], fe_name, row[f"{fe_name}_fe"], fmt_int(row[f"{fe_name}_n"]),
        ])

emit_table(
    "RF Fixed Effect Diagnostics",
    ["Y", "FE", "included", "n_categories"],
    fe_diag_rows,
)

emit_table(
    "Main RF Results",
    ["Y", "n_obs", "beta", "se", "t", "p", "R2", "note"],
    [
        [
            row["Y"], fmt_int(row["n_obs"]), fmt_float(row["beta"], 5),
            fmt_float(row["se"], 5), fmt_float(row["t"], 3),
            fmt_float(row["p"], 4), fmt_float(row["R2"], 4), row["note"],
        ]
        for _, row in results.iterrows()
    ],
)

n_by_wave = []
for wave in WAVES:
    tmp = df.loc[df["wave"].eq(wave) & df["analysis_base_sample"].eq(1)]
    n_by_wave.append([wave] + [fmt_int(tmp[y_name].notna().sum()) for y_name in Y_VARS])

emit_table("Outcome Nonmissing Counts in Base Sample", ["wave"] + Y_VARS, n_by_wave)
