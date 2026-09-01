# Run Log

Use this file to record platform runs after git commits.

## 2026-09-01 Migration

- Migrated the old v8 script into `scripts/analysis/01_sme_expectations_rf.py`.
- No platform run has been performed in this new git-based project yet.

## 2026-09-01 First Platform Run, Interrupted In Cell 8

Date: 2026-09-01
Commit before follow-up fix: `6d10887`
Script: `scripts/analysis/01_sme_expectations_rf.py`
Platform environment: Ant platform notebook

Inputs:
- `SHOCK_TABLE = shock_panel_v2`
- `PORT_CONTROL_TABLE = ctrl_monthly_panel`

Cell 4 source-read diagnostics:
- Surveys: 2024q2 14,876 rows/16 cols; 2024q3 12,975/21;
  2024q4 12,509/21; 2025q1 9,056/21; 2025q2 9,593/21.
- 2024q2 addon: 14,876 rows/5 cols.
- Shock panel: 122,359 rows/4 cols.
- Control panel: 1,266,578 rows/4 cols.
- Holding panel: 1,288,708 rows/6 cols.

Cell 5 survey construction:
- Rows/users/sme owners/answer observations/answer time below 180 seconds:
  2024q2 14,876/14,876/9,354/14,876/6,857;
  2024q3 12,975/12,975/7,502/12,975/5,028;
  2024q4 12,509/12,509/8,007/12,509/5,190;
  2025q1 9,056/9,056/5,324/9,056/4,126;
  2025q2 9,593/9,583/5,966/9,593/4,299.
- 2024q2 addon merge diagnostics: survey keys 14,874; addon keys 14,874;
  key overlap 14,874; `exp_gdp`, `exp_house`, `exp_cpi`, and `exp_rate`
  nonmissing counts all 0. The keys merged, but the expected macro columns did
  not produce numeric nonmissing values.

Cell 6 user-level shock/control summary:
- Rows/users/mean portfolio/return coverage/control coverage/min control
  coverage/control months/return nonmissing/risk nonmissing:
  2024q2 24,163/24,163/28,962.74/0.9996/0.9942/0.9852/11.37/22,890/22,905;
  2024q3 23,168/23,168/29,946.61/0.9996/0.9954/0.9867/11.35/21,904/21,933;
  2024q4 21,913/21,913/32,034.86/0.9996/0.9938/0.9851/11.45/20,896/20,925;
  2025q1 22,253/22,253/31,587.94/0.9997/0.9951/0.9877/11.09/20,557/20,583;
  2025q2 20,997/20,997/33,902.31/0.9995/0.9958/0.9904/11.41/19,957/19,986.

Base sample sequential funnel:
- Final sample after `R_nonmissing`: 2024q2 4,115; 2024q3 3,628;
  2024q4 3,219; 2025q1 2,299; 2025q2 2,552.
- The largest drops are the SME-owner filter, answer-time filter, and positive
  portfolio filter.

Portfolio-cell diagnostics:
- Rows with cell: 15,809.
- Duplicate user-wave rows removed: 2.
- Number of cells: 223.
- Singleton cells: 4.
- Cell size range: 1 to 243.

Cell 8 interruption:
- Error line: `results = pd.DataFrame([run_rf(df, y_name) for y_name in Y_VARS])`.
- Error message: `TypeError: Cannot interpret 'string[python]' as a data type`.
- Follow-up change: convert formula categorical variables (`wave` and
  `analysis_portfolio_cell`) from pandas nullable string dtype to ordinary
  object dtype inside `run_rf`; add a CELL 8 dtype diagnostic table before the
  regressions.

## Template

```text
Date:
Commit:
Script:
Platform environment:

Inputs:
- SHOCK_TABLE =
- PORT_CONTROL_TABLE =

Cell 4 source-read diagnostics:

Cell 5 sample funnel:

Cell 5b distribution checks:

Cell 6 regression summary:

Interpretation:

Follow-up changes:
```
