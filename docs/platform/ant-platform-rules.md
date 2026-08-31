# Ant Platform Rules

The analysis scripts run in the Ant platform notebook, not locally.

## Hard Rules

- Read platform tables with `ant_read_data`.
- Write mid-tables with `ant_write_data`.
- Print only through `ant_print_all`.
- Plot only through `ant_plot`.
- Avoid ordinary `print()`, `pd.read_csv()`, `pd.read_excel()`, and direct
  matplotlib plotting in platform scripts.
- Use `cols=` for large platform table reads.
- Use `validate=` on every merge.
- Convert numeric and date columns explicitly.
- Keep output small enough for the platform's safety limits.
- Figure size should be between 3 and 12 inches; DPI should be between 50 and
  150.
- Plot input should generally have at least 100 rows.

## Cell Workflow

Scripts should use markers like:

```python
# === CELL 1: Imports ===
```

The platform does not split cells automatically. Copy each marked block into a
notebook cell manually and run cells in order.

## Table Names

Platform code should use table names from the platform left sidebar. Do not
invent separate real-data table names. If the platform changes data access
between simulation and trusted execution, let the platform handle that unless
official documentation says otherwise.

## Mid-Tables

The platform does not support overwriting mid-tables. Any mid-table written by
future scripts must use an explicit versioned name, even though this repository
uses git for code versions.
