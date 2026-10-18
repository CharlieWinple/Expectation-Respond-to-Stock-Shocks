"""Local synthetic checks; never reads platform data or runs the notebook."""
import ast
from pathlib import Path
import pandas as pd


def main():
    source = Path(__file__).resolve().parents[1] / "scripts/analysis/01_sme_expectations_rf.py"
    tree = ast.parse(source.read_text(encoding="utf-8-sig"))
    names = {"clean_text", "resolve_2024q2_addon", "merge_2024q2_addon"}
    module = ast.Module(body=[n for n in tree.body
                             if isinstance(n, ast.FunctionDef) and n.name in names],
                        type_ignores=[])
    env = {"pd": pd, "ADDON_2024Q2_KEY": "submit_id",
           "ADDON_2024Q2_MACRO_COLS": {"gdp": "exp_gdp", "cpi": "exp_cpi"},
           "EXP_MAPPING": {"exp_gdp": {"up": 1., "rise": 1., "down": -1.},
                           "exp_cpi": {"up": 1., "down": -1.}}, "DIAG_ROWS": []}
    exec(compile(module, str(source), "exec"), env)
    raw = pd.DataFrame([
        ["same", "up", "down"], ["same", "up", "down"],
        ["fill", None, "up"], ["fill", " up ", "up"],
        ["conflict", "up", "down"], ["conflict", "down", "down"],
        ["unknown", "other", "up"], ["unknown", "up", "up"],
        ["alias", "up", None], ["alias", "rise", None],
        [" normalized ", "up", "up"], ["normalized", "down", "up"],
        [None, "up", "up"], [" ", "down", "down"],
        ["empty", None, "NULL"],
    ], columns=["submit_id", "gdp", "cpi"])
    original = raw.copy(deep=True)
    resolve = env["resolve_2024q2_addon"]
    result = resolve(raw).set_index("submit_id")
    assert result.index.is_unique and result.index.notna().all()
    assert result.loc["same", "gdp"] == "up"
    assert result.loc["fill", "gdp"] == "up"
    assert pd.isna(result.loc["conflict", "gdp"])
    assert result.loc["conflict", "cpi"] == "down"
    assert pd.isna(result.loc["unknown", "gdp"])
    assert pd.isna(result.loc["normalized", "gdp"])
    assert result.loc["empty"].isna().all()
    assert env["EXP_MAPPING"]["exp_gdp"][result.loc["alias", "gdp"]] == 1
    pd.testing.assert_frame_equal(raw, original)
    pd.testing.assert_frame_equal(resolve(raw), resolve(raw.iloc[::-1]))
    pd.testing.assert_frame_equal(resolve(raw), resolve(resolve(raw)))
    assert resolve(raw.iloc[:0]).empty
    survey = pd.DataFrame({"submit_id": ["conflict", " fill ", None, "unmatched"],
                           "other_outcome": [1, 2, 3, 4]})
    merged = env["merge_2024q2_addon"](survey, resolve(raw))
    assert len(merged) == len(survey)
    assert pd.isna(merged.loc[0, "exp_gdp"]) and merged.loc[0, "exp_cpi"] == -1
    assert merged.loc[1, "exp_gdp"] == 1
    assert merged.loc[[2, 3], ["exp_gdp", "exp_cpi"]].isna().all().all()
    assert merged["other_outcome"].tolist() == [1, 2, 3, 4]
    print("PASS: resolution, order independence, idempotence, null keys and merge")


if __name__ == "__main__":
    main()
