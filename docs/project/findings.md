# Reusable Findings From The Old Project

## 2026-10-15 Annotated-NAV Diagnostic Sample (Screenshot Evidence)

- For the observed five-wave positive-portfolio passive-gain configuration
  (10/5/5 cells; portfolio-cell, city and gender FE; four basic controls),
  exact diagnostic samples are exp_stock 2,520 observations / 2,342 users,
  exp_rev 10,155 / 8,158, and exp_price 4,658 / 4,165.
- All 11 outcome counts match the preparation table. Each has zero duplicate
  user-wave rows, recorded-zero portfolios, missing holdings and incomplete
  histories. NAV event flags remain included under the chosen policy.
- Source: run_001 screenshots 001–002 and 010–011 and their transcriptions
  under CSMAR `outputs/platform_runs/sme_diagnostics_nav_annotated/`.
  These are diagnostic counts; full executed notebook provenance and
  regression estimates remain unconfirmed.
- Screenshot 012 confirms that exp_stock has no 2024q2 final observations,
  so its actual sample covers four waves despite the five-wave configuration.
  On 2026-10-16 the user confirmed that 2024q2 did not contain exp_stock:
  this is expected structural absence, not a data-processing failure. Its
  pooled outcome-missing count must not all be treated as response attrition.
  All three key outcomes' by-wave observation
  counts sum to their pooled exact counts; exp_rev and exp_price cover all
  five waves.
- Screenshot 013 shows outcome-specific cell sparsity: exp_stock has 574
  occupied cells, 144 singletons and 32.70% of observations in cells below
  five; exp_rev has 960/96/8.85%, and exp_price 801/184/20.37%.
  Each retains nonzero pooled within-cell X dispersion. This is before
  partialling out the other FE and controls, so conditional identifying
  variation still needs the subsequent diagnostic. Small-cell and constant-X
  observation counts overlap.
- Screenshot 014 confirms nonzero residual passive-gain dispersion after
  this run's FE and controls: SD .1482/.1691/.1370 (10,000 yuan) for
  stock/revenue/price samples, retaining 44.63%/62.04%/55.31% of demeaned
  raw X sum of squares. This resolves the presence of residual variation
  for this specification; it does not establish balance, exogeneity or power.
- Screenshot 015: none of the 15 individual conditional-balance tests has
  p<.05; the smallest unadjusted p is .0854 (company, revenue sample).
  Absolute standardized effects are at most .0372 in the displayed tests.
  Employee tests use only 1,250/4,973/2,288 observations in stock/revenue/price
  samples. This is limited exploratory evidence for the tested traits and
  observed specification, not a joint test or proof of exogeneity.

## 2026-09-21 R6 Keep-Zero Passive-Gain Run (Provisional)

- The 26,694-row analysis base includes 882 recorded-zero portfolios and
  11,427 unmatched-holding observations imputed to zero. Thus 46.1% of the
  base has zero passive gain, mostly without a verified zero holding.
- The user-confirmed R6 screenshots show positive `exp_cpi` and negative
  `exp_input_cost` main-specification coefficients at nominal p<0.05. Neither
  survives a Bonferroni threshold across 11 outcomes. These are provisional:
  the settings header is cropped and the result table uses an older layout.
- Corrected within-wave cells contain separate recorded/imputed zero statuses.
  The R7 positive-portfolio comparison is needed before drawing a substantive
  conclusion from R6.

## 2026-09-08 Diagnostic Priorities

- The latest positive-portfolio screenshots still include employee count,
  dropping 6,491 of 12,169 observations at that sequential funnel step (53.34%).
  They therefore do not isolate the effect of removing zero holdings relative
  to the previous four-control keep-zero run.
- Cell counts must be computed within each outcome's complete-case sample.
  The reported 937 cells and 102 singletons are pre-regression counts.
- The latest exp_price point estimate remains positive (0.06046) but is less
  precise (SE 0.07510); loss of significance does not itself imply a reversal
  or a statistically established coefficient difference.

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
