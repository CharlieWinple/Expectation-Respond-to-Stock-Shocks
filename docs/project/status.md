# Project Status

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
