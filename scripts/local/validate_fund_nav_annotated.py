"""All-row return retention and actual platform policy/aggregation checks."""
import ast
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from annotate_fund_nav_returns import TARGET, UPLOAD, UPLOAD_COLUMNS
from build_fund_nav_screened import DEST,read,KEY

REPO = Path(__file__).resolve().parents[2]

def platform_env(path):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    names = {'safe_ratio', 'holdings_for_wave', 'aggregate_shock_to_user',
             'aggregate_control_to_user'}
    module = ast.Module(body=[n for n in tree.body
                              if isinstance(n, ast.FunctionDef) and n.name in names],
                        type_ignores=[])
    env = dict(pd=pd, np=np, USER_COL='uid', FUND_COL_HOLDING='fund_code',
               FUND_COL_PANEL='fund_code', WAVE_COL='wave', HOLDING_AMT_COL='amount',
               REALIZED_GAIN_MONTH_COL='realized_gain', REALIZED_GAIN_COL='realized_gain',
               WAVE_HOLDING_MONTH={'2024q2': pd.Period('2024-05')},
               SHOCK_RET_PP_COL='shock_ret_rate_pp', SHOCK_USABLE_COL='shock_usable',
               SHOCK_PORTFOLIO_SCOPE='usable', PASSIVE_RET_PREDICTOR='passive_return',
               PASSIVE_GAIN_PREDICTOR='passive_gain',
               REALIZED_RETURN_PREDICTOR='realized_return', GAIN_UNIT_YUAN=10000,
               CONTROL_MONTH_COL='history_month', CONTROL_MONTHLY_RET_COL='ctrl_monthly_ret')
    exec(compile(module, str(path), 'exec'), env)
    return env

def main():
    frames={}
    checks=[]
    for component,name,source,val,flag,keys in [
        ('control','ctrl_monthly_nav_annotated_v1.csv','ctrl_monthly_nav_screened_v1.csv','ctrl_monthly_ret','ctrl_usable',KEY),
        ('shock','shock_panel_nav_annotated_v1.csv','shock_panel_nav_screened_v1.csv','shock_ret_rate','shock_usable',KEY[:2])]:
        a=read(TARGET/name);old=read(DEST/source)
        upload=read(UPLOAD/name)
        assert list(upload.columns)==UPLOAD_COLUMNS[component]
        assert len(upload)==len(a)
        assert a[UPLOAD_COLUMNS[component]].reset_index(drop=True).equals(upload)
        assert len(a)==len(old) and not a.duplicated(keys).any()
        assert a[keys].equals(old[keys])
        assert a.return_version.eq('nav_price_annotated_v1').all()
        assert np.allclose(a[val],a.raw_return,equal_nan=True,atol=0,rtol=0)
        assert a[val].notna().eq(a[flag].eq(1)).all()
        assert np.isfinite(a.loc[a[flag].eq(1),val]).all()
        assert np.allclose(a.screened_return,old[val],equal_nan=True,atol=0,rtol=0)
        assert np.allclose(a.loc[a.is_money,val],old.loc[old.is_money,val],equal_nan=True,atol=0,rtol=0)
        restored=a.loc[a.screen_pass_all_checks.eq(0)&a.return_calculable.eq(1)]
        assert restored[val].notna().all() and len(restored)>0
        frames[component]=a
        checks.append(component+'_keys_raw_retention_screened_copy_money_unchanged_and_upload_projection')
    c,s=frames['control'],frames['shock']
    merger=c.loc[c.fund_code.eq('159925')&c.history_month.eq('2024-01')]
    assert len(merger)>0 and merger.ctrl_usable.eq(1).all() and merger.screen_pass_all_checks.eq(0).all()
    assert merger.flag_nav_relation_break.eq(1).all() and merger.ctrl_monthly_ret.gt(.8).all()
    dividend=c.loc[c.fund_code.isin(['110007','110008'])&c.history_month.eq('2025-01')]
    assert len(dividend)>0 and dividend.ctrl_usable.eq(1).all() and dividend.flag_nav_relation_break.eq(1).all()
    checks.append('confirmed_merger_and_dividend_values_retained_and_flagged')
    # Execute the exact platform if block in both switch states, then actual
    # aggregators on a portfolio with an event month.
    for file in ['scripts/analysis/01_sme_expectations_rf.py','scripts/diagnostics/02_sme_expectations_diagnostics.py']:
        path=REPO/file;tree=ast.parse(path.read_text(encoding='utf-8'))
        blocks=[x for x in tree.body if isinstance(x,ast.If) and isinstance(x.test,ast.Name) and x.test.id=='APPLY_NAV_QUALITY_SCREEN']
        assert len(blocks)==1
        assert any(isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='APPLY_NAV_QUALITY_SCREEN' for t in x.targets) and isinstance(x.value,ast.Constant) and x.value.value is False for x in tree.body)
        holding=pd.DataFrame(dict(uid=['test'],fund_code=['159925'],amount=[10000.],realized_gain=[0.],month_p=[pd.Period('2024-05')]))
        for switch in [False,True]:
            env=platform_env(path)
            cs=c.loc[c.fund_code.eq('159925')&c.wave.eq('24Q2')].copy();ss=s.loc[s.fund_code.eq('159925')&s.wave.eq('24Q2')].copy()
            cs['wave']=ss['wave']='2024q2'
            env.update(shock=ss,control=cs,APPLY_NAV_QUALITY_SCREEN=switch)
            exec(compile(ast.Module(body=blocks,type_ignores=[]),str(path),'exec'),env)
            returned=env['aggregate_control_to_user'](env['control'],holding,'2024q2').iloc[0]
            if switch:
                assert env['control'].loc[env['control'].history_month.eq('2024-01'),'ctrl_monthly_ret'].isna().all()
                assert returned.control_min_coverage<1
            else:
                assert returned.control_n_months==12 and np.isclose(returned.control_min_coverage,1)
                assert np.isclose(returned.expected_ret_12m,cs.ctrl_monthly_ret.mean())
                assert np.isclose(returned.portfolio_risk_12m,cs.ctrl_monthly_ret.std(ddof=1))
    checks.append('actual_01_02_default_retention_and_optional_screen_aggregation')
    result=dict(status='PASS',checks=checks,platform_run=False,
        sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in TARGET.glob('*.csv')},
        upload_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in UPLOAD.glob('*.csv')})
    (TARGET/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
