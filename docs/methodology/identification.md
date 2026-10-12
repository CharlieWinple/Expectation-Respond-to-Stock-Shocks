# Identification

The project uses passive mutual-fund returns as quasi-lottery shocks.

For user `i`, fund `j`, and shock window or month `t`:

```text
passive_gain_yuan_ijt = holding_ij,t-1 * fund_return_jt
passive_gain_yuan_it  = sum_j passive_gain_yuan_ijt
passive_ret_it        = passive_gain_yuan_it / portfolio_size_i,t-1
```

The active platform script stores both `passive_gain` and `realized_gain` in
units of 10,000 yuan for regression, so each raw yuan gain is divided by 10,000.

Current v2 script uses fund-level precomputed shock and control panels. It
aggregates those fund-level objects to user level with end-of-previous-window
holdings as weights.

## Conditioning Set

The current reduced-form specification conditions on:

- wave-by-portfolio-cell fixed effects based on beginning portfolio size,
  historical portfolio risk, and historical expected portfolio return;
- city-level, gender, employer-industry, and grouped employment-size fixed
  effects;
- age;
- college indicator;
- firm age;
- company-registration indicator.

The post-diagnostic candidate portfolio-cell design is:

```text
5 portfolio-size bins
3 historical-risk bins
3 historical-expected-return bins
```

## Audited R7 Candidate Regression

```text
Y_iw = beta * passive_gain_iw
     + C(analysis_portfolio_cell_iw)
     + C(city_iw) + C(gender_iw) + C(industry_iw) + C(employee_group_iw)
     + traits_iw
     + error_iw
```

`passive_gain` is in units of 10,000 yuan. The audited script defaults to R7:
five waves, positive observed portfolios, and user-clustered standard errors.
R6 retains recorded and imputed zero portfolios; R8 omits 2024q3 while
retaining zero portfolios; R9 uses passive return on positive portfolios.
The three model columns use the same complete-case sample for each outcome.
The 11 main-outcome p-values receive a Holm adjustment.

## Sample Rule

The intended sample is:

- SME owner;
- answer time at least 180 seconds, while missing answer time is retained;
- submitted strictly after the fund-shock window ends; missing or earlier
  submission dates are excluded;
- nonnegative beginning portfolio size in R6/R8, with recorded-zero and
  unmatched-holding/imputed-zero observations in separate wave-specific cells;
- positive beginning portfolio size in R7/R9;
- complete passive-return coverage;
- complete historical-control coverage;
- non-missing passive return.

The keep-zero runs impute unmatched holdings as zero and set their coverage
diagnostics to complete. Such observations are not verified zero investors;
their count is reported separately and R6/R8 are exploratory. The script
checks shock-window uniqueness, holding-snapshot timing, and conflicting
duplicate source keys before displaying coefficients. User clustering does not
account for dependence from common fund holdings, so fund-exposure inference
remains a limitation.

The exact sample size must be confirmed by platform output.
