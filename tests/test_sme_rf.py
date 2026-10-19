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
    d["wave"] = np.asarray(env["WAVES"])[np.arange(n) % 5]
    zero = np.arange(n) % 7 == 0
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
    d["coarse_portfolio_cell"] = [f'{w}_Z' if z else f'{w}_P{i % 3}'
                                  for i, (w, z) in enumerate(zip(d["wave"], zero))]
    d.loc[d["wave"].eq("2024q2"), "exp_stock"] = np.nan
    return d


def reference(run, y, spec, env):
    terms = [f"C({c})" for c in spec["fe_names"] if run[c].nunique() >= 2] + spec["control_names"]
    ols = smf.ols(f'{y} ~ ' + ' + '.join([env['CORE_X_VAR']] + terms), run)
    fit = (ols.fit(cov_type='cluster', cov_kwds={'groups': run[env['USER_COL']].astype(str)})
           if env['SE_TYPE'] == 'cluster_user' else ols.fit(cov_type='HC1'))
    return fit, terms


def check_cells_and_sample_parity():
    env, _ = environment()
    d = synthetic(env)
    d['portfolio_size'] = np.where(d['zero_history_not_applicable'], 0, 1000 + np.arange(len(d)))
    original = d.copy(deep=True)
    fine = env['build_portfolio_cells'](d)
    coarse = env['build_portfolio_cells'](d, (5, 3, 3))
    positive = d['portfolio_size'].gt(0)
    for frame, bins in [(fine, (10, 5, 5)), (coarse, (5, 3, 3))]:
        for value, name, count in [('portfolio_size', 'analysis_size_bin', bins[0]),
                                    ('portfolio_risk_12m', 'analysis_risk_bin', bins[1]),
                                    ('expected_ret_12m', 'analysis_eret_bin', bins[2])]:
            expected = np.ceil(d.loc[positive].groupby('wave')[value].rank(method='average', pct=True) * count).clip(1, count).astype('Int64')
            pd.testing.assert_series_equal(frame.loc[positive, name], expected, check_names=False)
        assert frame.loc[~positive, 'analysis_portfolio_cell'].tolist() == (d.loc[~positive, 'wave'] + '_Z').tolist()
    pd.testing.assert_frame_equal(d, original)
    d = env['add_continuous_portfolio_controls'](d)
    y = 'exp_input_cost'
    expected = d.loc[d['analysis_base_sample'].eq(1)].dropna(
        subset=[env['USER_COL'], y, env['CORE_X_VAR']] + env['REG_FE_NAMES'] + env['CONTROL_NAMES'] + env['EXT_CONTROL_NAMES'])
    samples, audit = env['select_cd_samples'](d, y)
    assert samples['C'].index.tolist() == expected.index.tolist()
    assert samples['D'].index.tolist() == expected.index[~expected['wave'].eq('2024q3')].tolist()
    pd.testing.assert_series_equal(samples['D']['analysis_portfolio_cell'],
                                  d.loc[samples['D'].index, 'analysis_portfolio_cell'])
    assert audit[3] == 0 and audit[5] == 0
    zeros = d['zero_history_not_applicable']
    assert d.loc[zeros, env['EXT_CONTROL_NAMES']].eq(0).all().all()
    assert d.loc[zeros, 'portfolio_risk_12m'].isna().all()
    # Genuine positive missing extension input is recorded as attrition, not imputed.
    target = expected.index[d.loc[expected.index, 'portfolio_size'].gt(0)][0]
    d.loc[target, env['EXT_CONTROL_NAMES'][0]] = np.nan
    samples, audit = env['select_cd_samples'](d, y)
    assert audit[3] == 1 and target not in samples['C'].index
    target2 = samples['C'].index[0]
    d.loc[target2, 'coarse_portfolio_cell'] = pd.NA
    samples, audit = env['select_cd_samples'](d, y)
    assert audit[5] == 1 and target2 in samples['C'].index
    assert env['estimate_rf'](samples['C'], y, env['CD_SPECS']['C'], {})['note'] == 'missing_model_input_no_silent_drop'


def check_estimation():
    env, _ = environment()
    d = env['add_continuous_portfolio_controls'](synthetic(env, 240))
    y = 'exp_input_cost'
    samples, _ = env['select_cd_samples'](d, y)
    for se in ['cluster_user', 'HC1']:
        env['SE_TYPE'] = se
        for group in ['C', 'D']:
            run = samples[group]
            result = env['estimate_rf'](run, y, env['CD_SPECS'][group], {})
            fit, terms = reference(run, y, env['CD_SPECS'][group], env)
            x = env['CORE_X_VAR']
            np.testing.assert_allclose([result['beta'], result['se'], result['p'], result['R2']],
                                       [fit.params[x], fit.bse[x], fit.pvalues[x], fit.rsquared], rtol=1e-8, atol=1e-10)
            aux = smf.ols(f'{x} ~ ' + ' + '.join(terms), run).fit()
            np.testing.assert_allclose(result['variation']['residual_X_sd'], aux.resid.std(), rtol=1e-8, atol=1e-10)
    cache = {}
    before = env['FIT_COUNTS']['regression']
    a = env['estimate_rf'](samples['C'], y, env['CD_SPECS']['C'], cache)
    b = env['estimate_rf'](samples['C'].copy(), y, env['CD_SPECS']['C'], cache)
    assert a == b and env['FIT_COUNTS']['regression'] == before + 1
    env['RUN_BLOCKERS'] = ['synthetic_source_block']
    assert env['estimate_rf'](samples['D'], y, env['CD_SPECS']['D'], {})['note'] == 'blocked_integrity_gate'


def check_execution(blocked=False, missing_column=False, output='compact'):
    env, source = environment()
    d = synthetic(env, 240)
    if missing_column:
        d = d.drop(columns=['coarse_portfolio_cell'])
    before = d.copy(deep=True)
    env['df'] = d
    env['OUTPUT_MODE'] = output
    env['RUN_BLOCKERS'] = ['synthetic_block'] if blocked else []
    env['TABLE_BUFFER'] = {'Source Read Summary': (['table', 'rows'], [['synthetic', len(d)]])}
    numbers = re.findall(r'(?m)^# === CELL (\d+):', source)
    cells = re.split(r'(?m)^# === CELL \d+:.*$', source)[1:]
    assert [int(n) for n in numbers] == list(range(1, 14))
    assert 'screenshot' not in source.lower()
    for number, cell in zip(numbers, cells):
        if int(number) >= 8:
            exec(compile(cell, f'{SCRIPT}:cell{number}', 'exec'), env)
    pd.testing.assert_frame_equal(env['df'][before.columns], before)
    if missing_column:
        assert env['FIT_COUNTS']['regression'] == 0
    else:
        assert len(env['cd_results']['C']) == len(env['cd_results']['D']) == 11
        assert env['FIT_COUNTS']['regression'] == (0 if blocked else 22)
        assert all(row['n_obs'] <= env['cd_results']['C'][i]['n_obs'] for i, row in enumerate(env['cd_results']['D']))
        stock = {r[0]:r for r in env['cd_sample_rows'] if r[1] == 'stock'}
        assert stock['C'][7] == 4 and stock['D'][7] == 3
        assert all('2024q3' not in r[8] for r in env['cd_sample_rows'] if r[0] == 'D')
        if not blocked:
            from statsmodels.stats.multitest import multipletests
            for group in ['C', 'D']:
                expected = multipletests([r['p'] for r in env['cd_results'][group]], method='holm')[1]
                np.testing.assert_allclose(expected, [r['holm_p'] for r in env['cd_results'][group]])
    rendered = '\n'.join(line for block in env['captured'] for line in block)
    assert 'REPORT BEGIN' in rendered and 'REPORT END' in rendered
    titles = [rendered.index(s) for s in ['01 Settings', '02 C estimates', '02 D estimates', '03 C cell density', '04 Fit counts']]
    assert titles == sorted(titles)
    for block in env['captured']:
        for line in block[1:]:
            assert len(line) <= 84, repr(line)


if __name__ == '__main__':
    check_cells_and_sample_parity()
    check_estimation()
    check_execution()
    check_execution(blocked=True)
    check_execution(missing_column=True)
    check_execution(output='full')
    print('PASS: C/D only, 22 fits, fixed samples/cells, zero rules, clustered/HC1 parity, Holm, sequential reports')
