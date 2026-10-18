"""Local synthetic parity/integration checks; no platform data is read."""
import ast
import re
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/analysis/01_sme_expectations_rf.py"


def environment():
    source = SCRIPT.read_text(encoding="utf-8-sig")
    prefix = source[:source.index("# === CELL 4:")]
    tree = ast.parse(prefix)
    tree.body = [node for node in tree.body
                 if not (isinstance(node, ast.ImportFrom) and node.module.startswith("marvel"))
                 and not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                          and isinstance(node.value.func, ast.Name) and node.value.func.id == "print_envir")]
    captured = []
    env = {"ant_print_all": lambda values, **kwargs: captured.append(list(values.astype(str)))}
    exec(compile(tree, str(SCRIPT), "exec"), env)
    env["captured"] = captured
    return env, source


def synthetic(env, n=360):
    rng = np.random.default_rng(173)
    d = pd.DataFrame(index=np.arange(n))
    d[env["USER_COL"]] = [f"u{i // 2}" for i in range(n)]
    d["wave"] = np.where(np.arange(n) % 2, "2024q3", "2024q2")
    zero = np.arange(n) % 5 == 0
    d["portfolio_size"] = np.where(zero, 0, np.exp(rng.normal(8, 1, n)))
    d["portfolio_size_raw"] = d["portfolio_size"]
    d["portfolio_risk_12m"] = np.where(zero, np.nan, rng.uniform(.01, .05, n))
    d["expected_ret_12m"] = np.where(zero, np.nan, rng.normal(.004, .01, n))
    d["zero_history_not_applicable"] = zero
    d["recorded_zero_portfolio"] = zero & (np.arange(n) % 2 == 0)
    d["imputed_zero_portfolio"] = zero & ~d["recorded_zero_portfolio"]
    d["sample_control_complete"] = True
    d["analysis_base_sample"] = 1
    d["analysis_portfolio_cell"] = [f'{w}_Z' if z else f'{w}_P{i % 7}'
                                     for i, (w, z) in enumerate(zip(d["wave"], zero))]
    d["city_level_from_yicai"] = [f"c{i % 3}" for i in range(n)]
    # Redundant categorical control exercises covariance correction with rank deficiency.
    d["survey_industry"] = d["city_level_from_yicai"]
    d["portrait_gender"] = np.where(np.arange(n) % 2, "F", "M")
    d["aer_bal_employee_group"] = "one_group"
    for name in env["CONTROL_NAMES"]:
        d[name] = rng.normal(size=n)
    d["aer_bal_employee_n"] = rng.normal(10, 2, n)
    d.loc[np.arange(n) % 13 == 0, "aer_bal_employee_n"] = np.nan
    d[env["CORE_X_VAR"]] = np.where(zero, 0, rng.normal(size=n))
    for j, name in enumerate(env["Y_VARS"]):
        d[name] = .3 * d[env["CORE_X_VAR"]] + .2 * d["aer_bal_age"] + rng.normal(size=n)
        d.loc[(np.arange(n) + j) % 31 == 0, name] = np.nan
    return d


def reference(run, y, spec, env):
    terms = [f"C({c})" for c in spec["fe_names"] if run[c].nunique() >= 2]
    terms += list(spec["control_names"])
    ols = smf.ols(f'{y} ~ ' + " + ".join([env["CORE_X_VAR"]] + terms), data=run)
    fit = (ols.fit(cov_type="cluster", cov_kwds={"groups": run[env["USER_COL"]].astype(str)})
           if env["SE_TYPE"] == "cluster_user" else ols.fit(cov_type="HC1"))
    return fit, terms


def check_parity():
    env, _ = environment()
    d = synthetic(env)
    extended = env["add_continuous_portfolio_controls"](d)
    zeros = d["zero_history_not_applicable"]
    assert extended.loc[zeros, env["EXT_CONTROL_NAMES"]].eq(0).all().all()
    assert extended.loc[zeros, "portfolio_risk_12m"].isna().all()
    pd.testing.assert_frame_equal(d, extended[d.columns])
    y = env["Y_VARS"][0]
    run = env["regression_sample"](extended, y)
    assert env["regression_sample"](extended, y) is run
    for se_type in ["cluster_user", "HC1"]:
        env["SE_TYPE"] = se_type
        for spec in env["REG_SPECS"] + [env["EXT_SPEC"]]:
            sample = run if spec != env["EXT_SPEC"] else run.join(extended.loc[run.index, env["EXT_CONTROL_NAMES"]])
            result = env["estimate_rf"](sample, y, spec, {})
            fit, terms = reference(sample, y, spec, env)
            x = env["CORE_X_VAR"]
            np.testing.assert_allclose([result["beta"], result["se"], result["p"]],
                                       [fit.params[x], fit.bse[x], fit.pvalues[x]], rtol=1e-8, atol=1e-10)
            aux = smf.ols(f'{x} ~ ' + (" + ".join(terms) or "1"), data=sample).fit()
            v = result["variation"]
            np.testing.assert_allclose(v["residual_X_sd"], aux.resid.std(), rtol=1e-7, atol=1e-10)
            assert v["df_resid"] == aux.df_resid
        count = env["FIT_COUNTS"]["balance_projection"]
        rows = env["balance_tests_batched"](extended, run, y)
        assert env["FIT_COUNTS"]["balance_projection"] - count == 2
        for row in rows:
            trait = row["trait"]
            sample = run.copy()
            sample[trait] = extended.loc[run.index, trait]
            sample = sample.dropna(subset=[trait])
            rhs = " + ".join(env["fe_terms_for"](sample, env["BALANCE_FE_NAMES"])) or "1"
            ols = smf.ols(f'{env["CORE_X_VAR"]} ~ {trait} + {rhs}', data=sample)
            fit = (ols.fit(cov_type="cluster", cov_kwds={"groups": sample[env["USER_COL"]].astype(str)})
                   if se_type == "cluster_user" else ols.fit(cov_type="HC1"))
            trait_r = smf.ols(f'{trait} ~ {rhs}', data=sample).fit().resid
            standardized = fit.params[trait] * trait_r.std() / sample[env["CORE_X_VAR"]].std()
            np.testing.assert_allclose([row["beta"], row["se"], row["p"], row["std_effect"]],
                                       [fit.params[trait], fit.bse[trait], fit.pvalues[trait], standardized],
                                       rtol=1e-7, atol=1e-10)
    # Cache avoids the exact same positive-only fit under a second label.
    cache = {}
    before = env["FIT_COUNTS"]["regression"]
    a = env["estimate_rf"](run, y, env["REG_SPECS"][-1], cache)
    b = env["estimate_rf"](run.copy(), y, env["REG_SPECS"][-1], cache)
    assert a == b and env["FIT_COUNTS"]["regression"] == before + 1
    env["RUN_BLOCKERS"] = ["synthetic_block"]
    result = env["estimate_rf"](run, y, env["REG_SPECS"][-1], {})
    assert np.isnan(result["beta"]) and result["note"] == "blocked_integrity_gate"


def check_execution(mode, positive_only=False, blocked=False):
    env, source = environment()
    d = synthetic(env, 160)
    if positive_only:
        d = d.loc[d["portfolio_size_raw"].gt(0)].copy()
    # A genuinely missing extension input must not change the baseline sample.
    candidates = d.index[d["portfolio_size_raw"].gt(0) & d[env["Y_VARS"][0]].notna()]
    d.loc[candidates[0], "portfolio_risk_12m"] = np.nan
    env["df"] = d
    env["RUN_MODE"] = mode
    env["RUN_BLOCKERS"] = ["synthetic_block"] if blocked else []
    env["TABLE_BUFFER"] = {
        "AUX 0 Sample Size Sequential Funnel": (["step", "N"], [["test", len(d)]]),
        "CORE 3 Outcome Regression Sample Size": (["Y", "N"], [["test", len(d)]]),
    }
    cells = re.split(r"(?m)^# === CELL \d+:.*$", source)
    markers = re.findall(r"(?m)^# === CELL (\d+):", source)
    assert [int(n) for n in markers] == list(range(1, 15))
    assert "screenshot" not in source.lower()
    # Execute each marked notebook cell separately, as the platform does.
    for number, cell in zip(markers, cells[1:]):
        if int(number) >= 8:
            exec(compile(cell, f"{SCRIPT}:cell{number}", "exec"), env)
    assert len(env["main_rows"]) == len(env["extension_rows"]) == 11
    assert env["comparison_sample_rows"][0][3] == 1
    assert all(r[4] == r[5] for r in env["comparison_sample_rows"])
    if mode == "main_results":
        assert not env["balance_rows"] and not env["stability_rows"]
        assert env["FIT_COUNTS"]["balance_projection"] == 0
        assert not env["variation_rows"]
    elif not blocked:
        assert len(env["balance_rows"]) == 55
        assert len(env["stability_rows"]) == 11
    if blocked:
        assert not env["balance_rows"] and all(v == 0 for v in env["FIT_COUNTS"].values())
    if positive_only:
        # Per outcome: base + extension, with a common-sample baseline only when needed.
        assert env["FIT_COUNTS"]["regression"] < 44
    output = "\n".join(line for block in env["captured"] for line in block)
    assert "=== REPORT BEGIN ===" in output and "=== REPORT END ===" in output
    positions = [output.index(label) for label in ["01 Run", "02a Main", "03a Zero", "04a", "05a", "06a"]]
    assert positions == sorted(positions)
    if mode == "main_results":
        assert "NOT_RUN(main_results)" in output
    # Rendering never emits data lines wider than the configured 84 characters.
    for block in env["captured"]:
        for line in block[1:]:
            assert len(line) <= 84, repr(line)


def check_degeneracy_and_rendering():
    env, _ = environment()
    d = synthetic(env, 160)
    y = env["Y_VARS"][0]
    # Aliased X must use the direct auxiliary-regression fallback.
    d[env["CORE_X_VAR"]] = pd.factorize(d["analysis_portfolio_cell"])[0].astype(float)
    run = env["regression_sample"](d, y)
    result = env["estimate_rf"](run, y, env["REG_SPECS"][-1], {})
    assert env["FIT_COUNTS"]["variation_fallback"] == 1
    assert result["variation"]["residual_X_sd"] < 1e-10
    env["render_table"]("wide", ["id", "a", "b", "c"], [["key", "x" * 100, "y" * 100, "z" * 100]])
    rendered = "\n".join(line for block in env["captured"] for line in block)
    for char in "xyz":
        assert rendered.count(char) >= 100


if __name__ == "__main__":
    check_parity()
    check_execution("main_results")
    check_execution("full_diagnostics")
    check_execution("main_results", positive_only=True)
    check_execution("full_diagnostics", blocked=True)
    check_degeneracy_and_rendering()
    print("PASS: v9 formula parity, clustered/HC1 SE, FWL diagnostics, modes, zero exemption, report order/width")
