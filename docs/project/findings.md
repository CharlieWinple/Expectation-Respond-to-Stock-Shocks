# Reusable Findings From The Old Project

This file keeps conclusions that remain useful after migrating to git.

## Research Framing

- The project has two tracks: SME owners and households/job-survey respondents.
- The active track is SME owners.
- Outcomes are split into expectations and real outcomes.
- Current active outcomes are SME-owner expectations.

## Shock Construction

- `sme_fund_invest` and `sme_fund_trade` are monthly end-of-month snapshots.
- Beginning-of-month holdings for month `t` are therefore previous month-end
  holdings.
- Direct `groupby(user, fund).shift(1)` on sparse fund panels is unsafe because
  it can jump over missing months. Missing user-fund months must be reindexed
  and filled as zero before shifting.
- `fund_realized_ret_month` uses current-month realized gain divided by
  previous month-end portfolio size.
- `passive_ret_month` uses previous month-end holdings multiplied by current
  fund returns, divided by previous month-end portfolio size.
- Unmatched fund returns should not shrink the denominator. The old project
  tracked match/coverage explicitly.

## SME Survey Structure

- SME survey records split into mutually exclusive employee and employer
  branches.
- `v1` is the branch switch.
- Current SME-owner analysis should filter to the employer branch with
  `sme_owner == 1`.
- Employer-side v-codes drift across waves. Do not reuse one wave's v-code
  mapping for all waves.
- Business expectation and performance questions are employer-only.
- 2024q2 has no employer-side `exp_stock` equivalent in the available addon.

## Prior Empirical Results

- Old v5 reported a strong positive stock-expectation response:
  `exp_stock` LATE around `+32.50***` in the main AJS 2SLS+FWL specification.
- Old v5 reported `exp_cpi` around `+0.1319**` in the same specification.
- Other macro and business expectation outcomes were expected to be weak or
  insignificant, but v8 has not yet produced final platform results.
- v4 diagnostics supported the view that non-trading observations' realized
  returns are close to passive returns, while trading-month deviations reflect
  actual user trading behavior.

## 2026-09-01 Reduced-Form Platform Results

- The first completed v2 reduced-form run finds no 5 percent significant
  response of SME-owner expectations to passive mutual-fund return shocks.
- `exp_price` is the only marginal 10 percent result in the main RF summary:
  beta 0.05436, se 0.03134, p 0.0828.
- These results should be treated as preliminary until sample attrition,
  answer-time filtering, outcome mapping, and shock variation after portfolio
  cell fixed effects are diagnosed.

## Design Decisions Still In Force

- Keep analysis wave-specific.
- Keep SME-owner filtering explicit.
- Keep table reads column-limited with `cols=`.
- Keep every merge validated with `validate=`.
- Keep Ant-platform output small and explicit.
- Treat platform outputs as the source of truth for sample sizes and coefficients.
