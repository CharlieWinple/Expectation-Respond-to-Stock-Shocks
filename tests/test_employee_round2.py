"""Synthetic platform integration and independent clustered-OLS verification."""
import ast
from pathlib import Path
import sys
import types
import unittest

import numpy as np
import pandas as pd
import statsmodels.api as sm

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/diagnostics/03_employee_diagnostics.py'
SOURCE = SCRIPT.read_text(encoding='utf-8')


def execute(broken=False):
    ns = {}
    output = []
    rng = np.random.default_rng(72)
    module = types.ModuleType('marvel.AntPrint')
    module.ant_print_all = lambda s, **kw: output.extend(s.tolist())
    module.ant_read_data = lambda *a, **kw: None
    old = {k: sys.modules.get(k) for k in ['marvel', 'marvel.AntPrint']}
    sys.modules['marvel'] = types.ModuleType('marvel')
    sys.modules['marvel.AntPrint'] = module
    setup, rest = SOURCE.split('# === CELL 3:', 1)
    exec(compile(setup, str(SCRIPT), 'exec'), ns)
    tables = {}
    shock, history, holdings = [], [], []
    for wi, wave in enumerate(ns['WAVES']):
        snapshot = pd.Period(ns['HOLD_MONTH'][wave], freq='M').end_time.normalize()
        start = snapshot + pd.Timedelta(days=1)
        end = start + pd.Timedelta(days=20)
        months = pd.period_range(end=start.to_period('M')-1, periods=12, freq='M')
        for j in range(8):
            shock.append([str(j), wave, j-3+wi, 1, start, end, ns['RETURN_VERSION']])
            for month in months:
                history.append([str(j), wave, str(month), rng.normal(.01, .02), ns['RETURN_VERSION']])
        rows = []
        for i in range(180):
            row = dict(user_id=str(i), submit_id=f'{wave}-{i}', submit_date=str((end+pd.Timedelta(days=2)).date()),
                       extro_info='answerSeconds=42;', user_age=str(25+i%40),
                       v1=ns['NONOWNER_ANSWER'], v2=ns['EMPLOYEE_ANSWER'] if i%2 else pd.NA,
                       v3=pd.NA if i%2 else ns['WORKING_ANSWER'], v10=pd.NA)
            if i == 0:  # Wage nonmissing cannot independently establish employee status.
                row.update(v2=pd.NA, v3='我没有工作', v10='5000')
            for c, value in zip(ns['EMP_CODES'][wave], ['增长3_4', '上升0_5', '增长1_2', '2_3',
                                                      '2600_2800点']):
                if c:
                    row[c] = value if i%3 else '不确定'
            row[ns['EMP_EDUCATION'][wave]] = '大学本科' if i%3 else '初中'
            if broken and wi == 2:
                row[ns['EMP_CODES'][wave][0]] = 'NEW_UNMAPPED_LABEL'
            rows.append(row)
            if i == 2:  # No source match is not zero holdings.
                continue
            for j in range(8):
                amount = 0 if i == 1 else rng.uniform(50, 8000)
                holdings.append([str(i), str(j), amount, str(snapshot.date())])
        tables[ns['SURVEY_TEMPLATE'].format(wave=wave)] = pd.DataFrame(rows)
    tables[ns['HOLDING_TABLE']] = pd.DataFrame(holdings, columns=['匿名化用户id','基金代码','当月月底日持有金额元','日期'])
    tables[ns['SHOCK_TABLE']] = pd.DataFrame(shock, columns=['fund_code','wave','shock_ret_rate_pp','shock_usable','window_start','window_end','return_version'])
    tables[ns['CONTROL_TABLE']] = pd.DataFrame(history, columns=['fund_code','wave','history_month','ctrl_monthly_ret','return_version'])
    def read(name, cols):
        return tables[name].reindex(columns=cols).copy()
    ns['ant_read_data'] = read
    exec(compile('# === CELL 3:'+rest, str(SCRIPT), 'exec'), ns)
    for key, value in old.items():
        if value is None:
            sys.modules.pop(key, None)
        else:
            sys.modules[key] = value
    return ns, output, tables


class EmployeeRound2(unittest.TestCase):
    def test_platform_contract(self):
        tree = ast.parse(SOURCE)
        self.assertFalse(any(isinstance(n, (ast.Try, ast.Raise)) for n in ast.walk(tree)))
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'merge':
                self.assertIn('validate', [k.arg for k in n.keywords])
        self.assertEqual(SOURCE.count('# === CELL '), 10)

    def test_workflow_and_units(self):
        ns, out, tables = execute()
        self.assertIn('ROUND2 REPORT END', out[-1])
        self.assertEqual(len(ns['TESTS']), 28)
        self.assertEqual(len(ns['VARIATION']), 25)
        d = ns['SURVEYS']['2024q3'].set_index('user_id')
        self.assertFalse(d.loc['0','candidate'])
        self.assertTrue(d.loc['3','candidate'])  # Missing wage and v3 do not exclude v2 route.
        self.assertFalse(d.loc['1','eligible'])
        self.assertTrue(pd.isna(d.loc['2','capital']))
        self.assertTrue(d.loc['3','eligible'])  # 42-second answers retained.
        self.assertEqual(d.loc['3','clear_gdp'], 0)
        self.assertTrue(pd.isna(d.loc['3','y_gdp']))
        h = tables[ns['HOLDING_TABLE']]
        h = h.loc[h['匿名化用户id'].eq('3') & h['日期'].eq('2024-08-31')]
        expected = sum(h['当月月底日持有金额元'] * (h['基金代码'].astype(int)-2)) / 1e6
        self.assertAlmostEqual(d.loc['3','gain'], expected)
        base = ns['BASE']
        self.assertTrue(base.loc[base.wave.eq('2024q3'), 'pre_y_gdp'].isna().all())
        self.assertTrue(base.loc[base.wave.eq('2024q3') & base.candidate, 'pre_age'].notna().all())
        self.assertTrue(base.loc[base.user_id.eq('0'), 'pre_age'].isna().all())
        self.assertFalse(any('tests_blocked' in s for s in ns['ISSUES']))

    def test_unmapped_blocks_without_zero_imputation(self):
        ns, _, _ = execute(broken=True)
        d = ns['SURVEYS']['2024q4']
        self.assertTrue(d.y_gdp.isna().all())
        self.assertTrue(d.clear_gdp.isna().all())
        self.assertTrue(d.y_house.notna().any())

    def test_clustered_fwl_matches_independent_dummy_ols(self):
        ns, _, _ = execute()
        rng = np.random.default_rng(51)
        n = 450
        d = pd.DataFrame(dict(user_id=np.repeat(np.arange(150),3), cell=np.tile(np.arange(9),50),
                              gain=rng.normal(size=n), c=rng.normal(size=n)))
        d['target'] = .7*d.gain+2*d.c+rng.normal(size=n)
        ns['CONTROL_COLS'] = ['c', 'twice_c']
        d['twice_c'] = 2*d.c
        ns['association'](d, 'target', 'validation', 'F')
        row = ns['TESTS'][-1]
        x = pd.concat([d[['gain','c']], pd.get_dummies(d.cell, dtype=float)], axis=1)
        fit = sm.OLS(d.target, x).fit(cov_type='cluster', cov_kwds={'groups': d.user_id})
        self.assertAlmostEqual(row['beta'], fit.params['gain'], places=10)
        self.assertAlmostEqual(row['se'], fit.bse['gain'], places=10)
        d['target'] = 1.
        ns['association'](d, 'target', 'validation', 'F')
        self.assertEqual(ns['TESTS'][-1]['status'], 'TARGET_ABSORBED')


if __name__ == '__main__':
    unittest.main()
