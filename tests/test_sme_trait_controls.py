"""Primary personal/business controls: synthetic sample and mapping checks."""
import ast
import numpy as np
import pandas as pd
from test_sme_rf import environment, synthetic, SCRIPT


def check_trait_samples_and_inference():
    env, _ = environment()
    raw, _ = env['prepare_wave_cell_design'](synthetic(env, 240))
    # Exercise nonconsecutive indexes, nullable FE and each attrition layer.
    raw.index = np.arange(len(raw)) * 3 + 7
    raw['portrait_gender'] = raw['portrait_gender'].astype('string')
    raw.loc[raw.index[0], 'aer_bal_age'] = np.inf
    raw.loc[raw.index[1], 'aer_bal_college'] = np.nan
    raw.loc[raw.index[2], 'portrait_gender'] = '  '
    raw.loc[raw.index[3], 'city_level_from_yicai'] = 'NULL'
    raw.loc[raw.index[4], 'aer_bal_firm_age'] = -np.inf
    raw.loc[raw.index[5], 'aer_bal_company'] = np.nan
    raw.loc[raw.index[6], 'survey_industry'] = None
    # These unselected inputs must neither trim the sample nor enter formulas.
    raw['aer_bal_employee_n'] = np.nan
    raw['aer_bal_employee_group'] = pd.NA
    raw['portrait_risk_level'] = pd.NA
    before = raw.copy(deep=True)
    sample, audit, missing = env['select_trait_sample'](raw)
    assert sample.index.tolist() == raw.index[7:].tolist()
    assert audit[:5] == [240, 237, 233, 3, 4]
    assert all(r[1] == 1 for r in missing)
    assert audit[-1] == '-'
    pd.testing.assert_frame_equal(raw, before)
    assert sample['size_detail_cell'].tolist() == raw.loc[sample.index, 'size_detail_cell'].tolist()
    assert sample.loc[sample['portfolio_size_raw'].eq(0)].shape[0] > 0
    pd.testing.assert_frame_equal(env['select_trait_sample'](raw.loc[raw['wave'].ne('2024q3')])[0],
                                  sample.loc[sample['wave'].ne('2024q3')])
    absent, audit_absent, _ = env['select_trait_sample'](raw.drop(columns='portrait_gender'))
    assert absent.empty and 'missing_trait_columns:portrait_gender' == audit_absent[-1]
    env['RUN_BLOCKERS'] = []
    for spec in env['TRAIT_MODEL_SPECS'].values():
        row = env['estimate_rf'](absent, 'exp_cpi', spec, {})
        assert row['note'] == 'skip_n'
    # Use independent formulas, including category effects, for both SE modes.
    expected_formulas = {
        'T0': 'C(size_detail_cell)',
        'T1': 'C(size_detail_cell) + C(portrait_gender) + aer_bal_age + aer_bal_college',
        'T2': 'C(size_detail_cell) + C(portrait_gender) + C(city_level_from_yicai) + '
              'C(survey_industry) + aer_bal_age + aer_bal_college + aer_bal_firm_age + aer_bal_company',
    }
    import statsmodels.formula.api as smf
    fitted_sample = sample.dropna(subset=['exp_cpi']).copy()
    for se_type in ['cluster_user', 'HC1']:
        env['SE_TYPE'] = se_type
        for model, spec in env['TRAIT_MODEL_SPECS'].items():
            row = env['estimate_rf'](fitted_sample, 'exp_cpi', spec, {})
            ols = smf.ols('exp_cpi ~ ' + env['CORE_X_VAR'] + ' + ' + expected_formulas[model], fitted_sample)
            fit = (ols.fit(cov_type='cluster', cov_kwds={'groups': fitted_sample[env['USER_COL']]})
                   if se_type == 'cluster_user' else ols.fit(cov_type='HC1'))
            np.testing.assert_allclose([row['beta'], row['se'], row['p']],
                [fit.params[env['CORE_X_VAR']], fit.bse[env['CORE_X_VAR']], fit.pvalues[env['CORE_X_VAR']]], rtol=1e-7)
    # A degenerate categorical predictor cannot create an identified gain slope.
    aliased = fitted_sample.copy()
    aliased[env['CORE_X_VAR']] = aliased['portrait_gender'].eq('M').astype(float)
    row = env['estimate_rf'](aliased, 'exp_cpi', env['TRAIT_MODEL_SPECS']['T1'], {})
    assert row['note'] == 'gain_not_separately_identified'


def check_confirmed_industry_mapping():
    expected = {'2024q2': 'v41', '2024q3': 'v42', '2024q4': 'v28', '2025q1': 'v29', '2025q2': 'v29'}
    paths = [SCRIPT, SCRIPT.parents[1] / 'diagnostics/02_sme_expectations_diagnostics.py']
    for path in paths:
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        node = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'TRAIT_VCODES' for t in n.targets))
        assert ast.literal_eval(node.value)['industry'] == expected
    env, _ = environment()
    # Read selection must include the broad-industry column on every wave.
    for wave in expected:
        assert expected[wave] in env['get_survey_cols'](wave)
        frame = pd.DataFrame({'user_age': ['40'], 'city_level_from_yicai': ['tier2'],
                              'v43': ['service_subcategory']})
        for trait, mapping in env['TRAIT_VCODES'].items():
            frame[mapping[wave]] = {'education': '大学本科', 'firm_year': '2020',
                                    'registration': '公司制企业_工商注册的企业',
                                    'employee_n': '10_19', 'industry': 'broad_industry'}[trait]
        out = env['construct_traits'](frame, wave)
        assert out['survey_industry'].iloc[0] == 'broad_industry'


if __name__ == '__main__':
    check_trait_samples_and_inference()
    check_confirmed_industry_mapping()
    print('PASS: trait attrition, common samples, SE parity, alias and broad-industry mapping')
