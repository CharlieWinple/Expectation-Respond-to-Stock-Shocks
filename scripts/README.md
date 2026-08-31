# Scripts

## Active Analysis

```text
analysis/01_sme_expectations_rf.py
```

This is the migrated v8 reduced-form SME expectations script. It is meant to be
pasted cell-by-cell into the Ant platform notebook.

## Diagnostics

`diagnostics/` is reserved for future checks. Do not recreate dated version
folders. Use git branches and commits for versions.

## Local Checks

Only syntax checks can be run locally:

```powershell
python -m py_compile .\scripts\analysis\01_sme_expectations_rf.py
```

The script imports Ant-platform modules, so full execution must happen on the
platform.
