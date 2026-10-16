# Scripts

## Active Analysis

```text
analysis/01_sme_expectations_rf.py
```

This is the migrated v8 reduced-form SME expectations script. It is meant to be
pasted cell-by-cell into the Ant platform notebook.

## Diagnostics

`diagnostics/02_sme_expectations_diagnostics.py` is the active platform
diagnostic. Compact mode puts the key input, flag, sample, and cell tables
together at the end for screenshots. Its defaults match 01's R7 gain and
user-clustered standard errors.

## Fund NAV build

`local/annotate_fund_nav_returns.py` produces the current full annotated panels
and the compact upload files. `local/validate_fund_nav_annotated.py` is the
active validator. The earlier total-return and screened builders remain as
upstream stages used by the current builder; their old standalone validators
have been retired. `local/audit_fund_manager_returns.py` preserves the external
fund-manager comparison.

## Local Checks

Platform scripts can be syntax-checked locally when Python is available:

```powershell
python -m py_compile .\scripts\analysis\01_sme_expectations_rf.py .\scripts\diagnostics\02_sme_expectations_diagnostics.py
```

The script imports Ant-platform modules, so full execution must happen on the
platform.
