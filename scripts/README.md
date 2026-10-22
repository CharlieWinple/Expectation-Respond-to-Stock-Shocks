# Scripts

## Active Analysis

```text
analysis/01_sme_expectations_rf.py
```

Current revision is `sme_rf_v14_wave_cell_diagnostics`. Paste Cells 1–16 into
the Ant notebook in order. `RUN_MODE="wave_cell_design"` computes six cell-only
design diagnostics (W5/W4 x 3/3/3, 5/3/3, 10/3/3), with zero outcome fits.
`compact` reports all density/variation rows and per-target largest absolute
balance effects plus widest confidence intervals; `full` includes every balance
row and preparation appendices. See the platform report guide for definitions.

## Diagnostics

`diagnostics/02_sme_expectations_diagnostics.py` is the active platform
diagnostic. Compact mode puts the key input, flag, sample, and cell tables
together at the end for screenshots. 02 has not been aligned with 01's addon
resolution or continuous-control extension and cannot establish v10 sample parity.

## Fund NAV build

`local/annotate_fund_nav_returns.py` produces the current full annotated panels
and the compact upload files. `local/validate_fund_nav_annotated.py` is the
active validator. The earlier total-return and screened builders remain as
upstream stages used by the current builder; their old standalone validators
have been retired. `local/audit_fund_manager_returns.py` preserves the external
fund-manager comparison.

## Local Checks

Local synthetic tests live in the repository's `tests/` directory and are not
uploaded to the platform. Run `python tests/test_sme_rf.py` and
`python tests/test_addon_resolution.py` from the repository root.

Platform scripts can be syntax-checked locally when Python is available:

```powershell
python -m py_compile .\scripts\analysis\01_sme_expectations_rf.py .\scripts\diagnostics\02_sme_expectations_diagnostics.py
```

The script imports Ant-platform modules, so full execution must happen on the
platform.
