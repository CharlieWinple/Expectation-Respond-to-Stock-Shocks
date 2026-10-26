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
    d["sample_cell_inputs"] = True
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
    d["coarsest_portfolio_cell"] = d["coarse_portfolio_cell"]
    d["size_detail_cell"] = d["coarse_portfolio_cell"] + "_" + (np.arange(n) % 2).astype(str)
    d.loc[d["wave"].eq("2024q2"), "exp_stock"] = np.nan
    return d


def reference(run, y, spec, env):
    terms = [f"C({c})" for c in spec["fe_names"] if run[c].nunique() >= 2] + env["effective_controls"](run, spec)
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
    env["RUN_MODE"] = "legacy_test"
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
    d.loc[d.index[:15], 'aer_bal_age'] = np.nan
    if missing_column:
        d = d.drop(columns=['size_detail_cell'])
    env.update(df=d, OUTPUT_MODE=output, RUN_BLOCKERS=['synthetic_block'] if blocked else [])
    cells = re.split(r'(?m)^# === CELL \d+:.*$', source)[1:]
    assert len(cells) == 16
    for number, cell in enumerate(cells, 1):
        if number >= 8:
            exec(compile(cell, f'{SCRIPT}:cell{number}', 'exec'), env)
    if blocked or missing_column:
        assert not env['model_rows'] and not env['wave_balance']
        assert not env['trait_model_rows'] and not env['trait_sample_rows']
        assert env['FIT_COUNTS']['regression'] == 0
    else:
        assert env['FIT_COUNTS']['regression'] == 198
        assert len(env['trait_model_rows']) == 66
        assert len(env['trait_sample_rows']) == 22
        assert env['FIT_COUNTS']['balance_projection'] == 59
        assert env['FIT_COUNTS']['variation_fallback'] == 0
        assert len(env['wave_balance']) == 180
        assert len(env['pre_balance']) == 48
        assert all(r['note'] for r in env['pre_balance'])
        assert len(env['sample_rows']) == 11
        base, _ = env['select_design_samples'](env['df'], None)
        pos = base['W5'].loc[base['W5']['portfolio_size_raw'].gt(0)]
        for r in env['wave_balance']:
            if r['note']:
                continue
            diagnostic = pos if r['Y'] == 'BASE' else env['sample_cache'][('exp_' + r['Y'], 'W5')]
            run = diagnostic.loc[diagnostic['wave'].eq(r['group']) & diagnostic['portfolio_size_raw'].gt(0)].copy()
            fit, _ = reference(run, r['trait'], env['MODEL_SPECS']['M0'], env)
            x = env['CORE_X_VAR']
            scale = pos[x].std() / pos[r['trait']].std()
            np.testing.assert_allclose([r['beta'], r['se'], r['std_effect']],
                [fit.params[x], fit.bse[x], fit.params[x]*scale], rtol=1e-7, atol=1e-10)
        for y in env['ACTIVE_Y_VARS']:
            samples, _ = env['select_design_samples'](env['df'], y)
            for w, run in samples.items():
                # Derive the expected common sample independently, not with the selector.
                expected = run.dropna(subset=['aer_bal_age', 'aer_bal_college',
                    'portrait_gender', 'city_level_from_yicai', 'aer_bal_firm_age',
                    'aer_bal_company', 'survey_industry'])
                primary = env['trait_sample_cache'][(y, w)]
                assert primary.index.tolist() == expected.index.tolist()
                assert primary['size_detail_cell'].tolist() == expected['size_detail_cell'].tolist()
                rows = [r for r in env['trait_model_rows'] if r['Y']==y and r['wave_set']==w]
                assert len(rows) == 3 and {r['n_obs'] for r in rows} == {len(expected)}
                for r in rows:
                    fit, _ = reference(expected, y, env['TRAIT_MODEL_SPECS'][r['model']], env)
                    np.testing.assert_allclose([r['beta'], r['se']],
                        [fit.params[env['CORE_X_VAR']], fit.bse[env['CORE_X_VAR']]], rtol=1e-7)
                rows = [r for r in env['model_rows'] if r['Y']==y and r['wave_set']==w]
                assert {r['n_obs'] for r in rows} == {len(run)}
                for r in rows:
                    fit, _ = reference(run, y, env['MODEL_SPECS'][r['model']], env)
                    np.testing.assert_allclose([r['beta'],r['se']],
                        [fit.params[env['CORE_X_VAR']],fit.bse[env['CORE_X_VAR']]], rtol=1e-7)
            pd.testing.assert_frame_equal(samples['W4'], samples['W5'].loc[samples['W4'].index])
    rendered = '\n'.join(line for block in env['captured'] for line in block)
    assert 'REPORT BEGIN' in rendered and 'REPORT END' in rendered
    for block in env['captured']:
        for line in block[1:]:
            assert len(line) <= 84, repr(line)


def check_e_design_and_balance():
    env, script = environment()
    raw = synthetic(env, 360)
    raw['sample_cell_inputs'] = True
    raw['recorded_positive_portfolio'] = raw['portfolio_size_raw'].gt(0)
    prepared = raw.drop(columns=['analysis_portfolio_cell', 'coarse_portfolio_cell', 'size_detail_cell', 'coarsest_portfolio_cell'])
    env['df'] = prepared
    start = script.index('cell_base = df.loc[')
    end = script.index('cell_size = cell_base.groupby(', start)
    exec(script[start:end], env)
    assert all(col in env['df'].columns for col in ['analysis_portfolio_cell', 'coarse_portfolio_cell', 'size_detail_cell'])
    assert len(env['df']) == len(raw)
    for col, bins in [('analysis_portfolio_cell',(10,5,5)),('coarse_portfolio_cell',(5,3,3)),('size_detail_cell',(10,3,3)),('coarsest_portfolio_cell',(3,3,3))]:
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


def check_wave_cell_design():
    env, script = environment()
    raw = synthetic(env, 360)
    # Optional control/FE missingness must not remove diagnostic sample rows.
    raw.loc[raw.index[:20], 'aer_bal_age'] = np.nan
    raw.loc[raw.index[:20], 'city_level_from_yicai'] = None
    raw.index = np.arange(len(raw)) * 3 + 7
    source, scaling = env['prepare_wave_cell_design'](raw)
    samples, audit = env['select_design_samples'](source, 'exp_input_cost')
    expected = raw.index[raw['exp_input_cost'].notna()]
    assert samples['W5'].index.tolist() == expected.tolist()
    assert samples['W4'].index.tolist() == expected[~raw.loc[expected, 'wave'].eq('2024q3')].tolist()
    for col in env['POLY_NAMES'] + [v[0] for v in env['DESIGN_CELLS'].values()]:
        pd.testing.assert_series_equal(samples['W4'][col], samples['W5'].loc[samples['W4'].index, col])
    positive = source['portfolio_size'].gt(0)
    for row in scaling:
        np.testing.assert_allclose(row[2], source.loc[positive, row[0]].mean())
    assert source.loc[~positive, env['POLY_NAMES']].eq(0).all().all()
    assert source.loc[~positive, 'portfolio_risk_12m'].isna().all()
    # Target-missing rows are dropped only for that diagnostic, not globally.
    for se in ['cluster_user', 'HC1']:
        env['SE_TYPE'] = se
        run = samples['W4']
        col = 'coarsest_portfolio_cell'
        spec = {'fe_names': [col], 'control_names': []}
        rows = env['balance_diagnostics'](run, source, 'W4_C1', 'exp_input_cost', 'cell', spec, col,
                                           targets=env['DESIGN_TARGETS'])
        assert any(r['dropped'] > 0 for r in rows if r['trait'] == 'aer_bal_age')
        for r in rows:
            if not np.isfinite(r['p']):
                continue
            subset = run if r['scope'] == 'all' else run.loc[run['portfolio_size_raw'].gt(0)]
            subset = subset.copy()
            subset['balance_target'] = source.loc[subset.index, r['trait']]
            subset = subset.dropna(subset=['balance_target'])
            fit, _ = reference(subset, 'balance_target', spec, env)
            x = env['CORE_X_VAR']
            np.testing.assert_allclose([r['beta'], r['se'], r['p']],
                [fit.params[x], fit.bse[x], fit.pvalues[x]], rtol=2e-6, atol=1e-9)
        variation = env['design_variation'](run, col)
        aux = smf.ols(env['CORE_X_VAR'] + ' ~ C(' + col + ')', run).fit()
        np.testing.assert_allclose(variation[2], aux.resid.std(), atol=1e-12)
    # Y magnitudes cannot affect the design diagnostic samples or targets.
    altered = raw.copy()
    altered['exp_input_cost'] *= -100
    prepared, scaling2 = env['prepare_wave_cell_design'](altered)
    samples2, audit2 = env['select_design_samples'](prepared, 'exp_input_cost')
    assert audit == audit2 and scaling == scaling2
    assert samples2['W5'].index.equals(samples['W5'].index)
    # A missing candidate label is retained by selection; execution skips it explicitly.
    source.loc[samples['W5'].index[0], 'coarsest_portfolio_cell'] = None
    changed, _ = env['select_design_samples'](source, 'exp_input_cost')
    assert changed['W5'].index.equals(samples['W5'].index)
    # Constant/no-variation cases do not masquerade as successful balance.
    run = samples['W4'].copy()
    run[env['CORE_X_VAR']] = 0.0
    assert env['design_variation'](run, col)[-1] == 'no_raw_variation'
    rows = env['balance_diagnostics'](run, source, 'W4_C1', 'exp_input_cost', 'cell', spec, col,
                                       targets=env['DESIGN_TARGETS'])
    assert all(not np.isfinite(r['p']) for r in rows)

def check_nullable_string_formula_boundary():
    env, _ = environment()
    raw = synthetic(env, 240)
    raw['size_detail_cell'] = raw['size_detail_cell'].astype('string[python]')
    raw[env['USER_COL']] = raw[env['USER_COL']].astype('string[python]')
    prepared, _ = env['prepare_wave_cell_design'](raw)
    samples, _ = env['select_design_samples'](prepared, 'exp_input_cost')
    original_ols = smf.ols
    calls = []
    def platform_compatible_ols(formula, data, **kwargs):
        # Enforce the older platform formula boundary even on newer local Patsy.
        assert data['size_detail_cell'].dtype == object
        assert data[env['USER_COL']].dtype == object
        calls.append(len(data))
        return original_ols(formula, data=data, **kwargs)
    for se in ['cluster_user', 'HC1']:
        env['SE_TYPE'] = se
        for run in samples.values():
            before = run.copy(deep=True)
            expected = run.copy()
            for col in ['size_detail_cell', env['USER_COL']]:
                expected[col] = expected[col].astype(object)
            for spec in env['MODEL_SPECS'].values():
                fit, _ = reference(expected, 'exp_input_cost', spec, env)
                smf.ols = platform_compatible_ols
                try:
                    result = env['estimate_rf'](run, 'exp_input_cost', spec, {})
                finally:
                    smf.ols = original_ols
                np.testing.assert_allclose([result['beta'], result['se'], result['p']],
                    [fit.params[env['CORE_X_VAR']], fit.bse[env['CORE_X_VAR']],
                     fit.pvalues[env['CORE_X_VAR']]], rtol=1e-8)
            pd.testing.assert_frame_equal(run, before)
    assert len(calls) == 24
    missing = pd.Series(['cell', pd.NA], dtype='string[python]')
    converted = env['as_formula_object'](missing)
    assert converted.dtype == object and pd.isna(converted.iloc[1])


if __name__ == '__main__':
    check_nullable_string_formula_boundary()
    check_cells_and_sample_parity()
    check_estimation()
    check_execution()
    check_execution(blocked=True)
    check_execution(missing_column=True)
    check_execution(output='full')
    check_e_design_and_balance()
    check_wave_cell_design()
    print('PASS: 66 primary + 132 supplement fits, common samples, covariance parity and reports')
