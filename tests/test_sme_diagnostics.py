"""Local synthetic checks; never read platform data."""
import ast
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_preparation(path):
    source = path.read_text(encoding="utf-8").split("# === CELL 4:")[0]
    tree = ast.parse(source)
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and node.module.startswith("marvel")
    ) and not isinstance(node, ast.Expr)]
    ns = {"ant_print_all": lambda *a, **k: None}
    exec(compile(tree, str(path), "exec"), ns)
    return ns


def test_preparation_and_samples():
    rf_path = ROOT / "scripts/analysis/01_sme_expectations_rf.py"
    diag_path = ROOT / "scripts/diagnostics/02_sme_expectations_diagnostics.py"
    rf = load_preparation(rf_path)
    diag = load_preparation(diag_path)
    # All shared function bodies must remain identical.
    trees = [ast.parse(p.read_text(encoding="utf-8")) for p in [rf_path, diag_path]]
    funcs = [{n.name: ast.dump(n) for n in tree.body if isinstance(n, ast.FunctionDef)} for tree in trees]
    assert all(funcs[0][name] == funcs[1][name] for name in funcs[0])
    codes = ["v43", "v42", "v28", "v29", "v29"]
    for wave, code in zip(rf["WAVES"], codes):
        assert rf["TRAIT_VCODES"]["industry"][wave] == code
        assert code in rf["get_survey_cols"](wave)
        assert "v5" not in rf["get_survey_cols"](wave)
        assert "v5" not in diag["get_survey_cols"](wave)
        row = {c: "1" for c in rf["get_survey_cols"](wave)}
        row.update({code: "manufacturing", "v5": None})
        assert rf["construct_traits"](pd.DataFrame([row]), wave)["survey_industry"].iloc[0] == "manufacturing"
    employee_n, employee_group = rf["map_employee_size"](
        pd.Series(["0_即只有经营者", "10_19", "20_99", "unmapped_range"])
    )
    assert employee_n.tolist()[:3] == [0, 14.5, 60]
    assert employee_group.tolist()[:3] == ["emp_0", "emp_10_19", "emp_20_plus"]
    assert pd.isna(employee_n.iloc[3])
    assert employee_group.iloc[3] == "emp_unmapped"
    node = next(n for n in trees[1].body if isinstance(n, ast.FunctionDef) and n.name == "diagnostic_sample")
    exec(compile(ast.Module(body=[node], type_ignores=[]), "diagnostic_sample", "exec"), rf)
    rng = np.random.default_rng(4)
    frame = pd.DataFrame({"analysis_base_sample": 1, "exp_stock": rng.normal(size=80),
                          "X100_R_passive": rng.normal(size=80),
                          "analysis_portfolio_cell": ["a", "b"] * 40})
    for control in rf["REG_CONTROL_NAMES"]:
        frame[control] = rng.normal(size=80)
    frame.loc[0, "exp_stock"] = np.nan
    frame.loc[1, "X100_R_passive"] = np.inf
    frame.loc[2, "analysis_portfolio_cell"] = None
    frame.loc[3, rf["REG_CONTROL_NAMES"][0]] = np.nan
    frame.loc[4, "analysis_base_sample"] = 0
    rf["diag_df"] = frame
    sample = rf["diagnostic_sample"]("exp_stock")
    summary, _ = rf["run_rf"](frame, "exp_stock")
    assert len(sample) == summary["n_obs"] == 75
    assert sample.index.tolist() == list(range(5, 80))
    frame["aer_bal_employee_n"] = "12"
    frame.loc[5:7, "aer_bal_employee_n"] = "unmapped_range"
    frame.loc[8, "aer_bal_employee_n"] = np.inf
    frame["wave"] = "2024q2"
    controls = rf["REG_CONTROL_NAMES"] + ["aer_bal_employee_n"]
    assert len(rf["diagnostic_sample"]("exp_stock", controls)) == 71
    assert len(rf["diagnostic_sample"]("exp_stock", [])) == 76
    rf["Y_VARS"] = ["exp_stock"]
    rf["emit_table"] = lambda *a, **k: None
    source = diag_path.read_text(encoding="utf-8")
    selection_code = source.split('employee_control = "aer_bal_employee_n"')[1].split('# === CELL 10:')[0]
    exec('employee_control = "aer_bal_employee_n"' + selection_code, rf)
    assert rf["selection_rows"][0][2:5] == [75, 71, 4]


if __name__ == "__main__":
    test_preparation_and_samples()
    print("Synthetic industry, preparation parity and exact-sample checks passed.")
