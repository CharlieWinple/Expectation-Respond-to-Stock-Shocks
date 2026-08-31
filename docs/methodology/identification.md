# Identification

The project uses passive mutual-fund returns as quasi-lottery shocks.

For user `i`, fund `j`, and shock window or month `t`:

```text
passive_gain_ijt = holding_ij,t-1 * fund_return_jt
passive_gain_it  = sum_j passive_gain_ijt
passive_ret_it   = passive_gain_it / portfolio_size_i,t-1
```

Current v2 script uses fund-level precomputed shock and control panels. It
aggregates those fund-level objects to user level with end-of-previous-window
holdings as weights.

## Conditioning Set

The current reduced-form specification conditions on:

- wave fixed effects;
- portfolio-cell fixed effects based on beginning portfolio size, historical
  portfolio risk, and historical expected portfolio return;
- age;
- college indicator;
- firm age;
- company-registration indicator.

The portfolio-cell design follows the old v8 decision:

```text
10 portfolio-size bins
5 historical-risk bins
5 historical-expected-return bins
```

## Active Regression

```text
Y_iw = beta * X100_R_passive_iw
     + C(wave_w)
     + C(analysis_portfolio_cell_iw)
     + traits_iw
     + error_iw
```

Standard errors use HC1 in the active script.

## Sample Rule

The intended sample is:

- SME owner;
- answer time at least 180 seconds, while missing answer time is retained;
- submitted after the earliest submit date in the wave;
- positive beginning portfolio size;
- complete passive-return coverage;
- complete historical-control coverage;
- non-missing passive return.

The exact sample size must be confirmed by platform output.
