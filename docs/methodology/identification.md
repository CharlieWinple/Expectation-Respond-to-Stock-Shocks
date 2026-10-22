# Identification

## 2026-10-21 Wave-by-cell diagnostic grid implemented — awaiting platform run

User authorized only design diagnostics: W5 all waves and W4 omit 2024q3,
each with 3/3/3, 5/3/3 and 10/3/3 cells. Revision
`sme_rf_v14_wave_cell_diagnostics`; wave_cell_design/compact; Cells 1–16.
Zero outcome regressions. Cell FE only; nine pre-window portfolio targets
(three linear plus six polynomial) and five supplementary survey targets.
BASE plus 11 outcome-availability samples, all/positive scopes. Fixed five-wave
cell construction and polynomial scaling; no re-ranking/rescaling after q3
omission. No automatic wave/cell selection or p-value pass gate.

Optional survey-control/other-FE missingness no longer excludes common samples;
per-target survey missingness is reported separately. Hence v13 N need not match.
Candidate missing/nonfinite designs skip with explicit notes, never silent drops.
Reports emphasize effect size/CI, density and variation. Compact target detail
shows max absolute effect and widest CI; Holm is supplemental, separated by
portfolio/survey and BASE/outcome families. No new platform results yet.


## 2026-10-19 E1-E4 implementation (awaiting platform run)

User approved the four-model design, explicitly excluding the proposed new
policy/response-date audit. Revision sme_rf_v13_e_design_checks; e_design +
compact; Cells 1–16. E1 coarse 5/3/3; E2 10/3/3; E3 city-level/industry x wave
FE; E4 six standardized portfolio polynomial terms. All include zero holders,
exclude 2024q3, and use a common outcome-specific sample. No historical outcome
refits; C/D only supply cell-balance diagnostic references. Normally 44 outcome
fits, plus batched balance projections. Preprocessing/coverage/NAV conventions
unchanged; adds one cell assignment. No new data tables or timing splits.
Balance distinguishes cell-only/final layers and full/positive scopes, with
standardized effects, CI, raw p, Holm and explicit controlled/absorbed/skipped
statuses. Survey measurement timing remains unverified. Full mode prints all
diagnostics; compact ranks top three absolute effects per family plus Holm flags.
Runtime and real estimates pending platform execution; prior result records
remain historical evidence, not outputs of this code revision.


## Current C/D Plan (2026-10-19; pending platform execution)

The next run estimates only two include-zero passive-gain specifications, both
with the existing continuous portfolio controls and non-portfolio FE. C varies
fine 10/5/5 to coarse 5/3/3 cells on the same pre-outcome population and original
complete-case rules. D excludes 2024q3 from the original fine-cell sample; cell
assignments are retained. C and D are not compared as if only one dimension
separated them: each is compared locally with the archived five-wave fine-cell
include-zero continuous-control result. The platform contains no old estimates
and does not refit that reference. Return and broad wave-omission grids are not
part of this plan. Full/positive cell density is descriptive, not a new slope
estimate for zero holders. Holm is within each outcome family, not across model
selection. Wave omission is not identification of a policy effect.


## Current Zero-Holding Convention (2026-10-16)

The user confirms that both a recorded zero and no holding record for the
relevant snapshot imply zero fund holdings. Invalid recorded amounts are
not expected under this source convention. Accordingly, 01 now defaults to
R6, retaining both sources with separate flags but one shared zero cell per wave.
Positive holdings without fund-return coverage do not qualify as zeros.
This supersedes the older default and absent-record interpretation below;
it is a user-confirmed data convention, not a new empirical validation.

Current 01 and 02 settings use 10/5/5 positive-portfolio bins ranked separately
within each wave, with wave included in every cell label. Both retain city,
gender, industry and employment-group FE and the four basic controls.
Zero portfolios have zero passive gain, undefined return/risk/expected return,
and an explicit exemption from historical coverage requirements; their history
counts are not fabricated. Positive portfolios retain full coverage and
12-month requirements. 01 also compares the main sample with positive-only
observations using the same preassigned positive cells. These current settings
supersede the older candidate bin counts below.


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
R10 keeps positive and recorded-zero portfolios but excludes unmatched
holdings. Observed zero fund holdings imply zero measured fund gain, not
absence of other financial assets or an exchangeable untreated group.
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
offers R10 to isolate the influence of verified zero fund balances without
equating missing holdings with zero. The script
checks shock-window uniqueness, holding-snapshot timing, and conflicting
duplicate source keys before displaying coefficients. User clustering does not
account for dependence from common fund holdings, so fund-exposure inference
remains a limitation.

The exact sample size must be confirmed by platform output.
