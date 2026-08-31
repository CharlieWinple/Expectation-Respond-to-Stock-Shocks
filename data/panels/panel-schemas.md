# User-Provided Panel Schemas

The active SME reduced-form script expects two user-provided fund-level platform
tables. Fill their platform table names in Cell 2 of
`scripts/analysis/01_sme_expectations_rf.py`.

## SHOCK_TABLE

Expected grain:

```text
FundClassID x wave
```

Expected columns:

```text
FundClassID
wave
window_start
window_end
window_days
shock_n_theory_days
shock_n_valid_days
shock_complete_ratio
shock_accnav_baseline
shock_accnav_end
shock_ret_rate
shock_ret_rate_pp
shock_ret_missing
shock_complete
shock_extreme
shock_usable
```

Old local reference size:

```text
122,369 data rows
17 columns including FundClassID and wave
wave format like 24Q2, 24Q3, 24Q4, 25Q1, 25Q2
```

## PORT_CONTROL_TABLE

Expected grain:

```text
FundClassID x wave
```

Expected columns:

```text
FundClassID
wave
history_start
history_end
ctrl_expected_ret_12m
ctrl_portfolio_risk_12m
ctrl_n_months_used
ctrl_coverage_in_history
ctrl_mean_TradingDays
```

Old local reference size:

```text
113,654 data rows
9 columns including FundClassID and wave
wave format like 24Q2, 24Q3, 24Q4, 25Q1, 25Q2
```

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
