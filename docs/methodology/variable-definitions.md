# Variable Definitions

## Core Shock Variables

`X100_R_passive`

: Passive return in percentage points. In the active script this is constructed
  by aggregating fund-level `shock_ret_rate_pp` with user-fund holding weights.

`portfolio_size`

: Beginning-of-period portfolio size from the holding snapshot associated with
  each wave.

`passive_complete`

: Indicator that enough of the user's portfolio has usable fund-level shock
  coverage.

## Historical Portfolio Controls

`portfolio_risk_12m`

: Holding-weighted 12-month historical risk from the fund-level control panel.

`expected_ret_12m`

: Holding-weighted 12-month historical expected return from the fund-level
  control panel.

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
