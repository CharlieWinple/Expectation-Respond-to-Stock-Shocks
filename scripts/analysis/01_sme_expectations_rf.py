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
    ant_print_all(pd.DataFrame({"message": [str(x) for x in lines]}))


def section(title):
    emit(["", "=" * 78, title, "=" * 78])


def fmt_int(x):
    return "-" if pd.isna(x) else f"{int(x):,d}"


def fmt_float(x, nd=4):
    return "-" if pd.isna(x) else f"{float(x):.{nd}f}"


def emit_table(title, columns, rows):
    section(title)
    ant_print_all(pd.DataFrame(rows, columns=columns))


# === CELL 2: Adjustable settings ===

SHOCK_TABLE = "shock_panel_v2"
PORT_CONTROL_TABLE = "ctrl_monthly_panel"

PROJECT_ID = "202405290032751511010004"
SURVEY_TEMPLATE = (
    f"frlab_sample_project_{PROJECT_ID}_v2_sme_sp_smesurvey{{wave}}_202512"
)
HOLDING_TABLE = (
    f"frlab_sample_project_{PROJECT_ID}_v2_sme_fund_invest_202512"
)
ADDON_2024Q2_TABLE = "sme_id3_2024q2_addExpectation"

WAVES = ["2024q2", "2024q3", "2024q4", "2025q1", "2025q2"]

SURVEY_BASE_COLS_BY_WAVE = {
    "2024q2": ["user_id", "submit_id", "submit_date", "v1", "extro_info", "user_age"],
    "2024q3": ["user_id", "submit_id", "submit_date", "v1", "extro_info", "user_age"],
    "2024q4": ["user_id", "submit_id", "submit_date", "v1", "extro_info", "user_age"],
    "2025q1": ["user_id", "submit_id", "submit_date", "v1", "extro_info", "user_age"],
    "2025q2": ["user_id", "submit_id", "submit_date", "v1", "extro_info", "user_age"],
}

USER_COL = "匿名化用户id"
SURVEY_USER_COL = "user_id"
FUND_COL_HOLDING = "基金代码"
FUND_COL_PANEL = "fund_code"
WAVE_COL = "wave"
HOLDING_AMT_COL = "当月月底日持有金额元"
HOLDING_DATE_COL = "日期"

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

ANSWER_SECONDS_MIN = 180

N_SIZE_BIN = 10
N_RISK_BIN = 5
N_ERET_BIN = 5
CELL_FE_NAME = "analysis_portfolio_cell"

PASSIVE_RET_PREDICTOR = "X100_R_passive"
SE_TYPE = "HC1"
MIN_REG_N = 30

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
    "下降3_以上": -4.0, "下降0_3": -1.5,
    "增长0_3": 1.5, "增长3_4": 3.5, "增长4_5": 4.5,
    "增长5_6": 5.5, "增长6_8": 7.0, "增长8_以上": 9.0,
    "下降0_1": -0.5, "下降1_2": -1.5, "下降2_3": -2.5,
    "下降3_5": -4.0, "下降5_以上": -6.0, "降低5_以上": -6.0,
    "增长0_1": 0.5, "增长1_2": 1.5, "增长2_3": 2.5,
    "增长3_以上": 4.0, "上涨3_5": 4.0,
    "上涨3_以内": 2.0, "上涨5_以上": 6.0, "上涨5_以内": 4.0,
    "降低3_以内": -2.0, "降低3_5": -4.0,
    "上升0_5": 2.5, "上升5_10": 7.5, "上升10_15": 12.5,
    "上升15_30": 22.5, "上升30_以上": 35.0,
    "下降0_5": -2.5, "下降5_10": -7.5, "下降10_15": -12.5,
    "下降15_30": -22.5, "下降30_以上": -35.0,
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

STOCK_INITIAL_LEVEL = 2748.92
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


def get_survey_cols(wave):
    cols = list(SURVEY_BASE_COLS_BY_WAVE[wave])
    for y_name in Y_VARS:
        v_code = EXP_VCODES.get(y_name, {}).get(wave)
        if v_code is not None:
            cols.append(v_code)
    for trait_name in ["education", "firm_year", "registration"]:
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
    out = out.merge(addon_keep, on=ADDON_2024Q2_KEY, how="left", validate="many_to_one")
    for source_col, y_name in ADDON_2024Q2_MACRO_COLS.items():
        out[y_name] = pd.to_numeric(out[source_col], errors="coerce")
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
    return out


def prepare_panel_keys(df):
    out = df.copy()
    out[WAVE_COL] = normalize_wave(out[WAVE_COL])
    out[FUND_COL_PANEL] = normalize_fund_code(out[FUND_COL_PANEL])
    return out


def holdings_for_wave(holding, wave):
    out = holding.loc[
        holding["month_p"].eq(WAVE_HOLDING_MONTH[wave]),
        [USER_COL, FUND_COL_HOLDING, HOLDING_AMT_COL],
    ].copy()
    out = (
        out.groupby([USER_COL, FUND_COL_HOLDING], as_index=False)
        .agg(holding_amt_raw=(HOLDING_AMT_COL, lambda x: x.sum(min_count=1)))
    )
    out["holding_amt"] = out["holding_amt_raw"].where(out["holding_amt_raw"].ge(0))
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
            shock_matched_holding=("shock_matched_holding", "sum"),
            shock_weighted_pp=("shock_weighted_pp", lambda x: x.sum(min_count=1)),
            n_funds=(FUND_COL_HOLDING, "nunique"),
            n_shock_matched=("shock_matched", "sum"),
            n_shock_usable=("shock_usable", "sum"),
        )
    )
    user["return_coverage"] = safe_ratio(user["shock_matched_holding"], user["portfolio_size"])
    user[PASSIVE_RET_PREDICTOR] = safe_ratio(user["shock_weighted_pp"], user["portfolio_size"])
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
    out[CELL_FE_NAME] = (
        out["analysis_size_bin"].astype("string") + "_"
        + out["analysis_risk_bin"].astype("string") + "_"
        + out["analysis_eret_bin"].astype("string")
    )
    return out


def run_rf(df, y_name):
    cols = [y_name, PASSIVE_RET_PREDICTOR, "wave", CELL_FE_NAME] + TRAIT_NAMES
    run = df.loc[df["analysis_base_sample"].eq(1), cols].copy()
    for col in [y_name, PASSIVE_RET_PREDICTOR] + TRAIT_NAMES:
        run[col] = pd.to_numeric(run[col], errors="coerce")
    run = run.replace([np.inf, -np.inf], np.nan).dropna()
    if len(run) < MIN_REG_N:
        return {"Y": y_name, "n_obs": len(run), "beta": np.nan, "se": np.nan, "t": np.nan, "p": np.nan, "R2": np.nan, "note": "skip_n"}
    fe_terms = []
    if run["wave"].nunique(dropna=True) >= 2:
        fe_terms.append("C(wave)")
    if run[CELL_FE_NAME].nunique(dropna=True) >= 2:
        fe_terms.append(f"C({CELL_FE_NAME})")
    formula = f"{y_name} ~ " + " + ".join([PASSIVE_RET_PREDICTOR] + fe_terms + TRAIT_NAMES)
    model = smf.ols(formula, data=run).fit(cov_type=SE_TYPE)
    return {
        "Y": y_name,
        "n_obs": int(model.nobs),
        "beta": float(model.params.get(PASSIVE_RET_PREDICTOR, np.nan)),
        "se": float(model.bse.get(PASSIVE_RET_PREDICTOR, np.nan)),
        "t": float(model.tvalues.get(PASSIVE_RET_PREDICTOR, np.nan)),
        "p": float(model.pvalues.get(PASSIVE_RET_PREDICTOR, np.nan)),
        "R2": float(model.rsquared),
        "note": "",
    }


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

holding = ant_read_data(
    HOLDING_TABLE,
    cols=[USER_COL, FUND_COL_HOLDING, HOLDING_AMT_COL, HOLDING_DATE_COL],
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
        fmt_int(tmp["portfolio_risk_12m"].notna().sum()),
    ])

emit_table(
    "User-Level Shock and Control Summary",
    [
        "wave", "rows", "users", "mean_port", "ret_cov", "ctrl_cov",
        "ctrl_min_cov", "ctrl_months", "R_nonmiss", "risk_nonmiss",
    ],
    coverage_rows,
)


# === CELL 7: Define base sample and portfolio cells ===

section("CELL 7: Define sample and portfolio cells")

df = survey_panel.merge(user_panel, on=[USER_COL, "wave"], how="left", validate="many_to_one")
df["sample_sme_owner"] = df["sme_owner"].eq(1)
df["sample_answer_time"] = df["answer_seconds"].isna() | df["answer_seconds"].ge(ANSWER_SECONDS_MIN)
df["sample_positive_portfolio"] = df["portfolio_size"].gt(0)
df["sample_passive_nonmissing"] = df[PASSIVE_RET_PREDICTOR].notna()
df["analysis_base_sample"] = (
    df["sample_sme_owner"]
    & df["sample_answer_time"]
    & df["sample_positive_portfolio"]
    & df["sample_passive_nonmissing"]
).fillna(False).astype(int)

sample_rows = []
for wave in WAVES:
    tmp = df.loc[df["wave"].eq(wave)]
    sample_rows.append([
        wave, fmt_int(len(tmp)), fmt_int(tmp["sample_sme_owner"].sum()),
        fmt_int(tmp["sample_answer_time"].sum()),
        fmt_int(tmp["sample_positive_portfolio"].sum()),
        fmt_int(tmp["sample_passive_nonmissing"].sum()),
        fmt_int(tmp["analysis_base_sample"].sum()),
    ])

emit_table(
    "Base Sample Summary",
    ["wave", "raw", "sme", "answer_ok", "port_gt0", "R_nonmiss", "base_sample"],
    sample_rows,
)

cell_base = df.loc[
    df["analysis_base_sample"].eq(1)
    & df["portfolio_size"].notna()
    & df["portfolio_risk_12m"].notna()
    & df["expected_ret_12m"].notna(),
    [USER_COL, "wave", "portfolio_size", "portfolio_risk_12m", "expected_ret_12m"],
].copy()
cell_base = build_portfolio_cells(cell_base)

df = df.merge(
    cell_base[[USER_COL, "wave", "analysis_size_bin", "analysis_risk_bin", "analysis_eret_bin", CELL_FE_NAME]],
    on=[USER_COL, "wave"],
    how="left",
    validate="many_to_one",
)

cell_size = cell_base.groupby(CELL_FE_NAME, dropna=False).size().rename("cell_n").reset_index()
emit_table(
    "Portfolio Cell Summary",
    ["metric", "value"],
    [
        ["rows_with_cell", fmt_int(len(cell_base))],
        ["n_cell", fmt_int(cell_size[CELL_FE_NAME].nunique(dropna=False))],
        ["n_singleton", fmt_int((cell_size["cell_n"] == 1).sum())],
        ["min_cell_n", fmt_int(cell_size["cell_n"].min())],
        ["max_cell_n", fmt_int(cell_size["cell_n"].max())],
    ],
)


# === CELL 8: Reduced-form regressions ===

section("CELL 8: Reduced-form regressions")

results = pd.DataFrame([run_rf(df, y_name) for y_name in Y_VARS])
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
