# User-Provided Panel Schemas

The active SME reduced-form script expects two user-provided platform tables.
The platform table name is the local CSV filename without `.csv`.

## SHOCK_TABLE

Local file:

```text
data/panels/shock_panel_v2.csv
```

Platform table:

```text
shock_panel_v2
```

Expected grain:

```text
fund_code x wave
```

Expected columns used by the script:

```text
fund_code
wave
shock_ret_rate_pp
shock_usable
```

Other available diagnostic columns:

```text
window_start
window_end
window_days
shock_n_theory_days
shock_n_valid_days
shock_complete_ratio
shock_accnav_baseline
shock_accnav_end
shock_ret_rate
shock_ret_missing
shock_complete
shock_extreme
```

The `fund_code` column is the six-digit fund trading code and is intended to
merge directly to the holding table's `基金代码` after code normalization.

## PORT_CONTROL_TABLE

Local file:

```text
data/panels/ctrl_monthly_panel.csv
```

Platform table:

```text
ctrl_monthly_panel
```

Expected grain:

```text
fund_code x wave x history_month
```

Expected columns used by the script:

```text
fund_code
wave
history_month
ctrl_monthly_ret
```

Other available diagnostic columns:

```text
history_start
history_end
TradingDays
```

The script merges these fund-month returns to each user's beginning-of-window
holdings, builds user-level fixed-portfolio monthly returns, and then computes
12-month expected return and risk from the user-level monthly series.

## Holding Table

The active script reads this standard platform table directly:

```text
frlab_sample_project_202405290032751511010004_v2_sme_fund_invest_202512
```

Expected columns used by the active script:

```text
匿名化用户id
基金代码
当月月底日持有金额元
日期
```
