"""Verify delivery files, observed window anchors and preservation of SME files."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
from build_fund_total_return import DEFAULT_ROOT


def main():
    project=DEFAULT_ROOT/'20260823 exp stock'
    dest=project/'outputs/jobsurvey_fund_returns'
    def read(p):
        return pd.read_csv(p,dtype={'fund_code':'string'},low_memory=False)
    full=read(dest/'jobsurvey_fund_returns_full_v1.csv')
    assert not full.duplicated(['fund_code','wave','lag_months']).any()
    evidence=Path(__file__).resolve().parents[2]/'outputs/platform_runs/jobsurvey_diagnostics/run_11162137/verified/candidate_windows.json'
    config=pd.DataFrame(json.loads(evidence.read_text(encoding='utf-8')))
    for r in config.itertuples():
        g=full.loc[full.wave.eq(r.wave)&full.lag_months.eq(r.lag_months)]
        assert len(g)>0
        for col,expected in [('holding_date',r.holding_date),('window_start',r.return_start),('window_end',r.return_end)]:
            assert pd.to_datetime(g[col]).eq(pd.Timestamp(expected)).all()
        assert g.window_days.eq(r.return_days).all()
    assert full.shock_ret_rate.notna().equals(full.shock_usable.eq(1))
    ordinary=full.loc[~full.is_money & full.shock_usable.eq(1)]
    np.testing.assert_allclose(ordinary.shock_ret_rate,ordinary.end_nav/ordinary.baseline_nav-1,rtol=1e-9,atol=1e-10)
    counts=[]
    for lag in [1,2]:
        upload=read(dest/'upload'/f'jobsurvey_shock_lag{lag}_nav_annotated_v1.csv')
        expected=full.loc[full.lag_months.eq(lag),upload.columns].reset_index(drop=True)
        pd.testing.assert_frame_equal(upload,expected,check_dtype=False)
        counts.append(dict(lag_months=lag,rows=len(upload),calculable=int(upload.shock_usable.sum())))
    inv=json.loads((project/'docs/inventory_before_jobsurvey.json').read_text(encoding='utf-8'))
    exempt={'outputs/build_csmar_v2.py','outputs/build_csmar_window_returns.py','outputs/build_panel.py'}
    preserved=0
    for row in inv:
        if row['path'].replace('\\','/') in exempt:
            continue
        p=project/row['path']
        with p.open('rb') as f:
            assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256'],str(p)
        preserved+=1
    checks=read(dest/'support/sme_reproduction_checks.csv')
    assert checks.mismatch.eq(0).all()
    result=dict(windows_verified_against_report=len(config),upload_checks=counts,
                original_files_unchanged=preserved,sme_reproduction_columns=len(checks),
                sme_reproduction_rows=int(checks.rows.iloc[0]),all_checks_passed=True)
    (dest/'support/delivery_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
