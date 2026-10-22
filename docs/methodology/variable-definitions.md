# Variable Definitions

## Wave-cell diagnostic additions (v14, 2026-10-21)

`coarsest_portfolio_cell` uses 3/3/3 within-wave average ranks on the same
pre-outcome eligible population as 5/3/3 and 10/3/3 candidates. W5 uses all waves;
W4 only deletes 2024q3. Assignments are fixed before outcome filtering.
`ctrl_poly_*` uses the same inputs/pairs as v13, but its center/scale reference
is now positive eligible FIVE-wave records, not four-wave records; the
transformation is shared across W5/W4 and outcomes. BASE and outcome samples
do not require optional survey controls or other FE. Finite portfolio inputs
are common requirements; survey targets use individual nonmissing masks.
Gain units and zero-history rules are unchanged.


## E design additions (2026-10-19)

size_detail_cell: 10/3/3 within-wave ranks on the same eligible population as
analysis_portfolio_cell (10/5/5) and coarse_portfolio_cell (5/3/3).
city_wave_FE / industry_wave_FE: city level or survey industry crossed with wave;
missing base labels remain missing, not string categories.
ctrl_poly_00/01/02/11/12/22: squares/pairwise products of standardized log-size,
history risk pp and history mean pp. Scaling uses positive eligible records
excluding 2024q3, before outcome-specific missingness. Zero design values stay
zero; raw history stays missing. Scale falls back to 1 for a constant input;
missing means remain missing and trigger affected-model skip rather than fill.
Final balance conditions on the relevant E controls; included variables and
absorbed targets do not count as tested/passed. Employee midpoint is a survey
association with unverified pre-shock timing. Four baseline survey traits also
lack independent timing confirmation; portfolio inputs are pre-window history.


## C/D specification columns (2026-10-19)

`analysis_portfolio_cell` retains the original five-wave 10/5/5 assignment.
`coarse_portfolio_cell` uses 5/3/3 within-wave average ranks on the same eligible
pre-outcome population. Both preserve the same wave-specific pooled zero cells.
D filters out 2024q3 after assignment; C does not filter by wave. The common
continuous controls and passive-gain units are unchanged. Current report
`basic_N`/`continuous_N` are eligibility counts, not fitted historical results.


## Core Shock Variables

`X100_R_passive`

: Passive return in percentage points. In the active script this is constructed
  by aggregating fund-level `shock_ret_rate_pp` with user-fund holding weights.
  Current inputs are the temporary `nav_price_annotated_v1` panels. Ordinary
  funds use end unit NAV divided by initial unit NAV minus one, flagging
  windows with detected relation breaks, large daily jumps or insufficient
  daily evidence without excluding calculable values by default.
  These are price returns, approximating total returns only
  when no distribution/share event occurs. Money-fund values retain the prior
  convention unchanged. See `fund-nav-annotated.md` for flagging limitations.

`portfolio_size`

: Beginning-of-period portfolio size from the holding snapshot associated with
  each wave.

`passive_gain`

: Passive gain in units of 10,000 yuan. It equals the holding-weighted fund
  shock in percentage points divided by 100 and then by 10,000. A one-unit
  increase therefore means an additional 10,000 yuan of passive gain.

`realized_return`

: Actual realized portfolio return in percentage points, constructed as
  `100 * realized_gain_yuan / portfolio_size` before the gain variable is
  rescaled to units of 10,000 yuan. This is descriptive and endogenous.

`realized_gain`

: Actual realized gain in units of 10,000 yuan, aggregated from the holding
  table's `当月累计月收益元` and divided by 10,000. This is descriptive and
  endogenous. When
  `SHOCK_PORTFOLIO_SCOPE = "usable"`, the script keeps the current convention
  of summing realized gains only over funds with usable shock coverage.

`passive_complete`

: Indicator that enough of the user's portfolio has usable fund-level shock
  coverage.

## Historical Portfolio Controls

### v10 continuous-control extension (not a replacement for baseline)

For positive portfolios, `ctrl_log_portfolio=ln(portfolio_size)` with size in
yuan, `ctrl_risk_pp=100*portfolio_risk_12m`, and
`ctrl_eret_pp=100*expected_ret_12m`. Risk/mean inputs are historical monthly
return fractions; the design controls express them in percentage points.
The same configured portfolio scope used by the cells determines size.
These are linear controls in the listed transformations; no quadratic or
wave-specific continuous slopes are introduced.

Zero-history-not-applicable rows receive zero only in these DESIGN columns.
Raw historical values remain undefined and existing wave-specific zero cells
remain in the model. Missing/nonfinite positive inputs remain missing. The
original four-control baseline sample is unchanged; extension estimates and
baseline estimates on the extension's exact sample are reported separately.
The positive-only extension uses the same preassigned positive cells.

Holm p-values cover the 11 outcomes separately within each labeled specification
and sample, not selection across model variants. Historical v9 results are not
results for this extension; backend verification is pending.

`portfolio_risk_12m`

: Sample standard deviation of 12 historical portfolio monthly returns,
  each formed using fixed beginning-of-shock portfolio weights. This includes
  cross-fund covariance and is not the weighted average of fund volatilities.

`expected_ret_12m`

: Mean of those 12 fixed-weight portfolio monthly returns, not a compounded
  annual return.

The integrated `ctrl_monthly_nav_annotated_v1` panel retains annotations from the
two former fund-quality tables; they must not be applied again. For a money-market fund
whose income disclosure crosses calendar month-end, the default replacement
monthly return assigns the full bundled income to the CSMAR `TradingDate`
month. Both affected fund-months carry bridge annotations; this is a
recorded-month convention rather than an exact daily accrual split. The
portfolio-level mean and standard deviation therefore use the same posted
monthly return series. Unresolved income conflicts and other invalid fund
months remain missing.

Ordinary-fund months suspected of distributions/share events retain their
calculable price returns and flags. `APPLY_NAV_QUALITY_SCREEN=False` is the
user-selected default; True reapplies the stricter screen. No zero imputation
or relaxation of the 12-month requirement is made. Flags-only estimates may
include dividend/split distortions, stale or non-CNY NAV price returns.

`controls_complete`

: Indicator that enough of the user's portfolio has historical-control coverage.

## SME Owner Filter

`sme_owner`

: Derived from survey `v1`. The active script sets it to 1 when the response is
  exactly `我是小微经营者_我自愿参与本次调查`.

## Traits

`aer_bal_age`

: Numeric survey age from `user_age`, when available.

`aer_bal_college`

: 1 for college or above, 0 for below college, missing otherwise.

`aer_bal_firm_age`

: Survey-year reference minus business start year.

`aer_bal_company`

: 1 if the business is company-registered, 0 for other non-missing registration
  forms.

`survey_industry`

: Employer-industry category from the employer branch of each SME survey wave.
  The current mapping uses v43/v42/v28/v29/v29 for 2024q2 through 2025q2.

`aer_bal_employee_n`

: Numeric midpoint mapping of reported employment-size answers. This variable
  is kept for diagnostics and robustness rather than the main specification,
  because the survey records broad intervals such as `10_19` and `20_99`.

`aer_bal_employee_group`

: Coarse employment-size group used as a fixed effect in the post-diagnostic
  candidate specification. Groups are `emp_0`, `emp_1_9`, `emp_10_19`, and
  `emp_20_plus`. Nonmissing raw answers not yet covered by the mapping are
  retained as `emp_unmapped` for the fixed effect, while their numeric midpoint
  remains missing.

## Expectation Outcomes

The active script estimates 11 expectation outcomes:

```text
exp_stock
exp_gdp
exp_cpi
exp_house
exp_rate
exp_env_local
exp_rev
exp_market
exp_price
exp_wage
exp_input_cost
```

2024q2 addon usage:

- `macroeconomic_gdp` -> `exp_gdp`
- `macroeconomic_house` -> `exp_house`
- `macroeconomic_cpi` -> `exp_cpi`
- `macroeconomic_rate` -> `exp_rate`
- no 2024q2 addon equivalent is used for `exp_stock`

All other waves use wave-specific employer-side v-codes.

### 01 addon duplicate resolution (2026-10-16)

Revision `sme_rf_audited_v9_addon_resolution` cleans addon submit IDs and
answers before grouping. Missing submit IDs cannot join to the survey.
Each of the four questions is resolved independently: identical answers
collapse; missing answers plus one unique valid mapped value retain that
value; multiple valid mapped values make that question missing. Any unknown
nonempty answer also makes that question missing, even alongside a recognized
answer. Different recognized labels mapping to the same value are equivalent.
No first-row selection remains. Other questions and outcomes are retained.
Outcome-specific complete-case selection determines regression inclusion.

The resolved addon must have nonmissing unique keys and recognized nonmissing
answers. Failure blocks estimation; source-conflict gates for shock, control
and portrait remain unchanged. This policy is implemented in 01 only; 02 has
not yet been aligned and should not be assumed to reproduce its new samples.
New diagnostic output reports policy and structural integrity only, not IDs,
answer text, duplicate/conflict counts or affected-small-group sample counts.
No new real-data results are available under this policy yet.

`exp_stock` unit:

: The active script maps stock-index expectation bins to index-level midpoint
  values and runs the regression in that level unit. It does not normalize by a
  wave-specific initial stock-index level because those wave-specific initial
  levels are not currently available.
