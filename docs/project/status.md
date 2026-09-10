# Project Status

## 2026-09-10 Post-Diagnostic Regression Candidate

- Recorded the 2026.09.10 compact 02 diagnostic conclusions in
  `docs/notes/Notes_Yanpeng.tex`.
- Added lightweight balance diagnostics to `01_sme_expectations_rf.py` so the
  main platform run now reports outcome-specific cell density, within-cell shock
  variation, residual shock variation after FE/controls, and lottery balance
  checks that regress the shock on predetermined traits plus fixed effects.
- 01 now defaults to the post-diagnostic candidate specification: positive
  portfolios, usable passive return, 5/3/3 portfolio cells, full return and
  historical-control completeness, city/gender/industry/employment-size FE,
  and four basic controls.
- Employee-size interval answers are now mapped instead of being coerced
  directly to numeric. The main specification uses grouped employment-size FE;
  numeric midpoint employee count is retained for diagnostics and robustness.

## 2026-09-09 Diagnostic Output Trim

- 02 now defaults to compact output. It keeps the main preparation funnel,
  portfolio-cell summary, outcome sample counts, key-Y distributions,
  configured-variable checks, employee attrition, and selected conditional
  balance tables while hiding bulk by-wave and optional-variable tables unless
  `DIAG_OUTPUT_MODE="full"`.
- Platform rules now explicitly avoid `raise`; diagnostics report missing
  configured FE/control variables through platform output instead of stopping
  with an exception.

## 2026-09-08 Screenshot Review

- Latest supplied run still filters on employee count, unlike the suggested
  four-control baseline. Active settings/commit were not supplied.
- 02 now defaults to the intended positive-portfolio four-control baseline
  and additionally audits employee selection and final-sample cell sparsity
  on fixed cells. See the run log for supplied results and their limitations.

## 2026-09-05 Diagnostic Script Update

- Corrected employer industry mapping in 01 to v43/v42/v28/v29/v29 across
  the five waves, as confirmed by the user; v5 was the wrong branch field.
- Added standalone `scripts/diagnostics/02_sme_expectations_diagnostics.py`.
  Defaults match the user's second screenshot configuration. It audits fields,
  holding provenance, exact regression samples, distributions and conditional
  balance. Usage: `docs/platform/sme-diagnostics.md`.
- Local syntax and synthetic mapping/sample-parity checks passed. Awaiting
  platform execution of the new diagnostic script; no new estimates asserted.
- The older migration status below is historical and predates completed runs
  recorded in the run log.

Last migrated: 2026-09-01.

## Active State

The project is ready for the first v2 platform run. The latest usable script
from the old project has been migrated to:

```text
scripts/analysis/01_sme_expectations_rf.py
```

The old project's v8 status was "generated / waiting for platform run". That
remains the current status here.

## Immediate To Do

1. Fill `SHOCK_TABLE` in Cell 2 with the platform table name for the fund-level
   shock panel.
2. Fill `PORT_CONTROL_TABLE` in Cell 2 with the platform table name for the
   fund-level 12-month control panel.
3. Run Cells 1-6 in order on the Ant platform.
4. Record Cell 4/5/5b/6 outputs in `docs/project/run-log.md`.
5. Interpret coefficients and update `docs/project/findings.md`.

## Waiting For Confirmation

- Exact platform table names for `SHOCK_TABLE` and `PORT_CONTROL_TABLE`.
- Whether `extro_info` consistently contains `answerSeconds=` across all five
  SME survey waves.
- Whether the current holding month map matches the user-provided shock windows
  in the production panels.

## Known Small Inconsistencies In The Old Project

- The old `TODO.md` referred to `05_panel_and_reg_v4.py`, while the actual latest
  script is `06_panel_and_reg_v4.py`.
- The old root directory is not a git repository.
- Old documentation sometimes says 2024q2 addon should not be used for employer
  macro outcomes; the latest v8 design deliberately uses the addon for
  2024q2 `exp_gdp`, `exp_house`, `exp_cpi`, and `exp_rate`, while still leaving
  2024q2 `exp_stock` missing.
