# User-Provided Panel Schemas

## Current inputs: annotated NAV price returns (2026-10-13)

The proposed upload tables are `shock_panel_nav_annotated_v1` and
`ctrl_monthly_nav_annotated_v1`, from the corresponding CSVs in the
CSMAR `outputs/fund_nav_upload/` directory. The wider annotated files remain
under `outputs/fund_nav_annotated/`. They preserve the fund/wave and
fund/wave/month keys and operational return columns documented below, and add
`return_version=nav_price_annotated_v1`. Uncalculable ordinary returns are blank.
`shock_usable` and `ctrl_usable` identify calculable ordinary returns, NOT quality
approval. Money policy is preserved. 01 and 02 read `screen_pass_all_checks`
alongside version/operational columns; flags do not exclude by default.
Do not reapply the legacy patches.
The local `data/panels/` copies and the schema descriptions below are the
preserved original inputs. See `docs/methodology/fund-nav-annotated.md`.

The full local annotated files include audit fields `raw_return`, `screened_return`, `return_calculable`,
`review_status`, `quality_reasons`, separate `flag_*`, `additive_score`,
`multiplicative_score`, `daily_coverage`, and endpoint evidence. Raw return
means unscreened unit-NAV price return, not the original CSMAR cumulative-NAV
return. Event/jump flags can be blank for insufficient evidence/not applicable.
Confirm actual uploaded table names before running.

The legacy patch path (disabled for current inputs) reads two tables from the
CSMAR source panels. `other_ctrl_shock_anomalies` is a sparse quality table
with `fund_code`, `wave`, `component` (`shock` or `control`),
`history_month` (blank for shock), `exclude` (1 means exclude; 0 marks a
usable posted-month bridge), and `reason`. It also records `default_use`,
`anomaly_class`, `bridge_in_count`, `bridge_out_count`, normalized bridge
income, common event IDs, and the candidate/replacement monthly returns.
`money_fund_control_supplement` has one row per zero-NAV money-market
fund-wave-month and includes `ctrl_monthly_ret_supplement`,
`supplement_usable`, `quality_status`, `ctrl_monthly_ret_posted`, the older
`ctrl_monthly_ret_estimate`, `return_timing_rule`, and bridge indicators.
The older patch workflow is retired; its schema and evidence remain documented
here and in `docs/project/run-log.md`.

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
