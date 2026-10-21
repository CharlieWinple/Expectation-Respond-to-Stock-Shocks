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
    d["size_detail_cell"] = d["coarse_portfolio_cell"] + "_" + (np.arange(n) % 2).astype(str)
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
    for frame, bins in [(fine, (10, 5, 5)), (coarse, (5, 3, 3)), (env["build_portfolio_cells"](d, (10, 3, 3)), (10, 3, 3))]:
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
    assert [int(n) for n in numbers] == list(range(1, 17))
    assert 'screenshot' not in source.lower()
    for number, cell in zip(numbers, cells):
        if int(number) >= 8:
            exec(compile(cell, f'{SCRIPT}:cell{number}', 'exec'), env)
    pd.testing.assert_frame_equal(env['df'][before.columns], before)
    if missing_column:
        assert env['FIT_COUNTS']['regression'] == 0
    else:
        assert all(len(rows) == 11 for rows in env['e_results'].values())
        assert env['FIT_COUNTS']['regression'] == (0 if blocked else 44)
        assert all([r['n_obs'] for r in rows] == [r['n_obs'] for r in env['e_results']['E1']] for rows in env['e_results'].values())
        stock = {r[0]:r for r in env['e_sample_rows'] if r[1] == 'stock'}
        assert all(r[7] == 3 for r in stock.values())
        assert all('2024q3' not in r[8] for r in env['e_sample_rows'])
        if not blocked:
            from statsmodels.stats.multitest import multipletests
            for group in env['E_SPECS']:
                expected = multipletests([r['p'] for r in env['e_results'][group]], method='holm')[1]
                np.testing.assert_allclose(expected, [r['holm_p'] for r in env['e_results'][group]])
            assert len(env['balance_families']) == 16
            for group, layer, scope in env['balance_families']:
                rows = [r for r in env['balance_rows'] if (r['group'], r['layer'], r['scope']) == (group, layer, scope) and np.isfinite(r['p'])]
                if rows:
                    np.testing.assert_allclose(multipletests([r['p'] for r in rows], method='holm')[1], [r['holm_p'] for r in rows])
    rendered = '\n'.join(line for block in env['captured'] for line in block)
    assert 'REPORT BEGIN' in rendered and 'REPORT END' in rendered
    titles = [rendered.index(s) for s in ['01 Settings', '02 E1 estimates', '02 E2 estimates', '02 E3 estimates', '02 E4 estimates', '03 E1 cell density', '05 Balance families', '06 Fit counts']]
    assert titles == sorted(titles)
    for block in env['captured']:
        for line in block[1:]:
            assert len(line) <= 84, repr(line)



def check_e_design_and_balance():
    env, script = environment()
    raw = synthetic(env, 360)
    raw['sample_cell_inputs'] = True
    raw['recorded_positive_portfolio'] = raw['portfolio_size_raw'].gt(0)
    prepared = raw.drop(columns=['analysis_portfolio_cell', 'coarse_portfolio_cell', 'size_detail_cell'])
    env['df'] = prepared
    start = script.index('cell_base = df.loc[')
    end = script.index('cell_size = cell_base.groupby(', start)
    exec(script[start:end], env)
    assert all(col in env['df'].columns for col in ['analysis_portfolio_cell', 'coarse_portfolio_cell', 'size_detail_cell'])
    assert len(env['df']) == len(raw)
    for col, bins in [('analysis_portfolio_cell',(10,5,5)),('coarse_portfolio_cell',(5,3,3)),('size_detail_cell',(10,3,3))]:
        expected = env['build_portfolio_cells'](raw, bins)['analysis_portfolio_cell']
        assert env['df'][col].tolist() == expected.tolist()
    raw.index = np.arange(len(raw)) * 3 + 7  # preserve nonconsecutive indices
    source, scaling = env['prepare_e_design'](raw)
    zero = source['zero_history_not_applicable']
    assert source.loc[zero, env['POLY_NAMES']].eq(0).all().all()
    assert source.loc[zero, 'portfolio_risk_12m'].isna().all()
    sample, references, audit = env['select_e_samples'](source, 'exp_input_cost')
    assert sample.index.tolist() == references['D'].index.tolist()
    assert audit[-1] == 0
    assert not source.loc[sample.index, 'wave'].eq('2024q3').any()
    for group, spec in env['E_SPECS'].items():
        result = env['estimate_rf'](sample, 'exp_input_cost', spec, {})
        fit, _ = reference(sample, 'exp_input_cost', spec, env)
        np.testing.assert_allclose([result['beta'], result['se']], [fit.params[env['CORE_X_VAR']], fit.bse[env['CORE_X_VAR']]], rtol=1e-7)
    for se in ['cluster_user', 'HC1']:
        env['SE_TYPE'] = se
        for layer in ['cell', 'final']:
            spec = env['E_SPECS']['E1']
            rows = env['balance_diagnostics'](sample, source, 'E1', 'exp_input_cost', layer, spec, 'coarse_portfolio_cell')
            tested = [r for r in rows if np.isfinite(r['p'])]
            assert tested
            for r in tested:
                subset = sample if r['scope'] == 'all' else sample.loc[source.loc[sample.index, 'portfolio_size_raw'].gt(0)]
                subset = subset.copy()
                subset['balance_target'] = source.loc[subset.index, r['trait']]
                subset = subset.dropna(subset=['balance_target'])
                direct_spec = spec if layer == 'final' else {'fe_names': ['coarse_portfolio_cell'], 'control_names': []}
                fit, _ = reference(subset, 'balance_target', direct_spec, env)
                x = env['CORE_X_VAR']
                np.testing.assert_allclose([r['beta'], r['se'], r['p']], [fit.params[x], fit.bse[x], fit.pvalues[x]], rtol=2e-6, atol=1e-9)
            if layer == 'final':
                assert all(r['note'] == 'controlled_not_a_test' for r in rows if r['trait'] in spec['control_names'])
    rows = env['balance_diagnostics'](sample, source, 'E4', 'exp_input_cost', 'final', env['E_SPECS']['E4'], 'coarse_portfolio_cell')
    assert all(r['note'] == 'controlled_not_a_test' for r in rows if r['trait'] in env['POLY_NAMES'])
    assert any(r['dropped'] > 0 for r in rows if r['trait'] == 'aer_bal_employee_n')
    source.loc[sample.index[0], 'size_detail_cell'] = None
    changed, _, audit = env['select_e_samples'](source, 'exp_input_cost')
    assert changed.index.tolist() == sample.index.tolist() and audit[-1] == 1
    assert env['estimate_rf'](changed, 'exp_input_cost', env['E_SPECS']['E2'], {})['note'] == 'missing_model_input_no_silent_drop'

if __name__ == '__main__':
    check_cells_and_sample_parity()
    check_estimation()
    check_execution()
    check_execution(blocked=True)
    check_execution(missing_column=True)
    check_execution(output='full')
    check_e_design_and_balance()
    print('PASS: E1-E4, 44 fits, common samples, zero rules, clustered/HC1 balance parity, Holm, sequential reports')
