"""Synthetic checks for the platform regression sample and inference."""
import ast
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_preparation():
    path = ROOT / "scripts/analysis/01_sme_expectations_rf.py"
    source = path.read_text(encoding="utf-8").split("# === CELL 4:")[0]
    tree = ast.parse(source)
    tree.body = [
        node for node in tree.body
        if not (isinstance(node, ast.ImportFrom) and node.module.startswith("marvel"))
        and not isinstance(node, ast.Expr)
    ]
    ns = {"ant_print_all": lambda *args, **kwargs: None}
    exec(compile(tree, str(path), "exec"), ns)
    return ns


def test_common_sample_and_clustered_inference():
    rf = load_preparation()
    rf["RUN_BLOCKERS"] = []
    rf["MIN_REG_N"] = 30
    rng = np.random.default_rng(4)
    n = 100
    frame = pd.DataFrame({
        rf["USER_COL"]: [str(i // 2) for i in range(n)],
        "analysis_base_sample": np.ones(n),
        "exp_cpi": rng.normal(size=n),
        rf["CORE_X_VAR"]: rng.normal(size=n),
    })
    for name in rf["REG_FE_NAMES"]:
        frame[name] = ["a", "b"] * (n // 2)
    for name in rf["REG_CONTROL_NAMES"] + rf["EXT_CONTROL_NAMES"]:
        frame[name] = rng.normal(size=n)
    frame.loc[0, "exp_cpi"] = np.nan
    frame.loc[1, rf["CORE_X_VAR"]] = np.inf
    frame.loc[2, rf["REG_FE_NAMES"][0]] = None
    frame.loc[3, rf["REG_CONTROL_NAMES"][0]] = np.nan
    frame.loc[4, "analysis_base_sample"] = 0
    sample = rf["regression_sample"](frame, "exp_cpi", rf["EXT_CONTROL_NAMES"])
    assert sample.index.tolist() == list(range(5, n))
    estimates = [rf["estimate_rf"](sample, "exp_cpi", rf["CD_SPECS"]["D"], {})]
    assert {row["n_obs"] for row in estimates} == {95}
    assert {row["n_users"] for row in estimates} == {48}
    assert all(np.isfinite(row["se"]) for row in estimates)
    rf["RUN_BLOCKERS"] = ["synthetic_source_problem"]
    assert rf["estimate_rf"](sample, "exp_cpi", rf["CD_SPECS"]["D"], {})["note"] == "blocked_integrity_gate"


def test_unmatched_holding_is_explicit_imputation():
    rf = load_preparation()
    frame = pd.DataFrame({
        "portfolio_size_raw": [np.nan, 0.0, 100.0],
        "portfolio_size": [np.nan, 0.0, 100.0],
        "return_coverage": [np.nan, np.nan, 1.0],
        "control_min_coverage": [np.nan, np.nan, 1.0],
        "control_n_months": [np.nan, np.nan, 12.0],
        "recorded_zero_portfolio": [False, True, False],
        "imputed_zero_portfolio": [True, False, False],
    })
    out = rf["fill_zero_portfolio_rows"](frame)
    assert out["portfolio_size"].tolist() == [0.0, 0.0, 100.0]
    pd.testing.assert_series_equal(out["return_coverage"], frame["return_coverage"])
    pd.testing.assert_series_equal(out["control_n_months"], frame["control_n_months"])
    assert out.loc[:1, rf["PASSIVE_GAIN_PREDICTOR"]].eq(0).all()
    assert out.loc[:1, rf["PASSIVE_RET_PREDICTOR"]].isna().all()
    assert frame["portfolio_size_raw"].isna().tolist() == [True, False, False]
    observed_only = rf["fill_zero_portfolio_rows"](frame, include_unmatched=False)
    assert pd.isna(observed_only.loc[0, "portfolio_size"])
    assert observed_only.loc[1, "portfolio_size"] == 0.0
    assert pd.isna(observed_only.loc[1, "return_coverage"])


if __name__ == "__main__":
    test_common_sample_and_clustered_inference()
    test_unmatched_holding_is_explicit_imputation()
