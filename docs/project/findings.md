# Reusable Findings From The Old Project

## 2026-10-18 R6 v11 Complete Report — Initial Interpretation

Evidence: 15 preserved images and 35 CSV tables in CSMAR
`outputs/platform_runs/sme_rf_continuous_controls/run_001/`. User confirms upload
complete and authorizes analysis. Interpretation follows the earlier user
statement that platform reports supplied here are real-data outputs; there was
no fresh explicit run-specific provenance confirmation. Values are rounded
report outputs, not locally rerun microdata estimates.

- Global and addon gates PASS. All 11 baseline outcomes exactly match archived
  v9 at displayed precision for N, users, beta, SE, p, Holm p, ordinary CI and R2.
  This supports preservation of baseline estimation under the optimization;
  it is not an independent audit of every raw-data transformation.
- Fit counts: 66 regression fits, 22 balance projections, zero variation
  fallbacks. Recorded preparation/compute stages sum to 1,238.53 seconds
  (20.64 minutes): reads 212.43 (17.15%), aggregation 847.89 (68.46%), models
  165.34 (13.35%). Timers measure elapsed time between section calls and can
  include inter-cell waiting. No comparable old elapsed time establishes a
  speedup factor. Aggregation is the priority for further profiling.
- All extension samples retain baseline N and zero counts. Historical mean,
  historical SD and log-size continuous controls therefore permit same-sample
  comparisons. Historical mean is a backward-looking proxy, not observed
  subjective expected return. Continuous controls capture within-bin linear
  differences and do not test every nonlinear or omitted exposure channel.
- Input-cost beta moves from -.55783 to -.56035; SE .22827, raw p .0141,
  Holm .1550, ordinary 95% CI [-1.00775,-.11295]. Positive extension beta
  -.55315, SE .24061, raw p .0215, Holm .2366. Neither survives multiplicity
  adjustment. Extended CPI beta .34874 (p .0787, Holm .7135), wage -.38688
  (p .0713, Holm .7135). Other extended raw p-values exceed .10. No outcome
  passes Holm in any of the four reported 11-outcome families.
- Input-cost association per one extended residual-X SD (.1098 gain units,
  1,098 yuan) is approximately -.06153 mapped percentage points. A 10,000-yuan
  contrast is much larger than this typical residual variation. The result
  concerns expected costs; it does not establish lower realized costs, a
  general optimism effect, or a wealth/financing mechanism.
- Zero shares range 42.02%–46.51%. Including-zero and positive-only coefficients
  remain close, including after continuous controls. Zero portfolios have
  X=0 and distinct wave-specific zero cells; they add no raw within-zero-cell
  gain variation. They can affect shared nuisance coefficients and inference.
  This does not identify an effect on zero holders or a treated/control design.
- Positive-only cells have 1.06%–7.34% of observations in cells with no X
  variation (versus 45%–50% overall, largely from zero cells), and 9.10%–33.55%
  in cells with fewer than five observations. Median density remains 3–7.
  Positive conditional-X SS shares are .4447–.6173; extended full-sample
  shares .4466–.6183. Controls reduce full-sample retained shares by only
  .0001–.0034 in absolute units. Variation exists, but sparse cells and
  possible influential observations remain relevant.
- Balance: 55 tests, one raw p<.05 (company/revenue .0482), no Holm flags;
  all displayed adjusted p-values are 1.0000. The tests are individual
  traits plus FE on baseline samples; they do not establish joint balance,
  positive-only balance or conditional exogeneity. Employee tests use smaller
  samples due to missing numeric employee mappings.
- Remaining priorities: predetermined coarser-cell sensitivity on a fixed
  sample, positive-only/joint balance, gain/return and leave-wave-out checks,
  influence/tail and annotated-NAV quality sensitivity, and inference allowing
  common fund exposures. User-cluster SE do not cover all cross-user common
  shocks. Outcome-specific samples differ substantially; cross-outcome signs
  are not a common-sample mechanism test. Preserve zero-source convention as
  user-confirmed; zero fund holdings do not imply no other assets.
- Confirmed 2024q3 gain window is September 1–17. A later policy announcement
  can affect subsequent survey answers, but dropping q3 alone does not isolate
  that policy mechanism. No FE/bin or outcome choice should be selected for
  obtaining a smaller p-value. No analysis code changed during this review.


## 2026-10-17 R6 v9 Complete Results — Initial Interpretation

Evidence: 13 administrator real-data PDF screenshots and transcriptions in
CSMAR `outputs/platform_runs/sme_rf_addon_resolution/run_001/`. User confirms
collection complete and requests analysis. Receipt/analysis date is recorded;
actual execution date and executed commit remain unknown. CORE 0 and addon
CORE 1 PASS. This establishes successful estimation under implemented checks,
not causal identification or NAV economic accuracy.

### Main estimates and specification stability

- No outcome passes Holm adjustment across 11 main outcomes. Input-cost
  expectations: beta -0.55783, SE .22962, p .0151, Holm p .1664,
  ordinary 95% CI [-1.00790, -.10777]. This is a negative exploratory signal,
  not a multiplicity-robust causal finding. CPI: .34496, p .0802,
  Holm .7645; wage expectations: -.37907, p .0764, Holm .7645.
- Other raw p-values exceed .10. Nonsignificance does not establish zero
  effects. Stock expectation beta -36.92938 index points has CI
  [-163.00994, 89.15118] per 10,000 yuan of passive gain.
- All coefficients use gain in 10,000 yuan. Percentage outcomes are mapped
  interval values (percentage-point scale), stock is index points, and local
  environment is a direction score. These are expectations, not realized
  costs, wages or sales. For input costs, one full-sample residual-X SD is
  .1099 units (1,099 yuan), giving an illustrative beta-scaled association
  of -.06131 mapped points; ordinary CI [-.11077, -.01184]. This is not a
  Y-standardized effect or a multiplicity-adjusted interval.
- On the fixed outcome-specific sample, input-cost coefficients across
  cell FE / additional FE / controls are -.55357 / -.56387 / -.55783.
  Wage and CPI coefficients are also similar across these specifications.
  Stability within these models does not test omitted confounding.

### Zero-holding comparison

- Zeros are 42.02%–46.51% of each exact sample; absent-record zeros are
  90.58%–92.91% of zeros. The user's source convention treats both recorded
  and absent holdings as genuine zero fund holdings. This is not zero total
  wealth or zero exposure through other assets.
- With positive cells fixed, input-cost beta is -.55783 including zero vs
  -.55102 positive only (N 8,533 vs 4,614; p .0151 vs .0232). Wage:
  -.37907 vs -.38417; CPI: .34496 vs .33005 (p .0802 vs .1045).
  Revenue .16054 vs .16161; stock -36.92938 vs -33.19663. Signs agree for
  all 11 outcomes. These are descriptive coefficient comparisons, not
  formal tests that the two nested-sample estimates are equal.
- Adding zeros reduces SE by only about 2.5%–8.4%, despite substantially
  increasing N. Wave-specific zero cells have constant X=0 and no direct
  within-cell shock variation. With shared controls and other FE, zeros can
  affect nuisance coefficients, residualization and precision. Keep-zero
  regression is not a treated-versus-untreated design and does not identify
  the causal effect of becoming a fund investor.
- CORE 7 shows zero positive-history-incomplete observations in every
  outcome; history-not-applicable equals the two zero-source counts combined.
  This supports implementation consistency, not validity of all NAV returns.

### Identification and remaining robustness

Follow-up timing check (2026-10-17): local compact upload
`outputs/fund_nav_upload/shock_panel_nav_annotated_v1.csv` and the earlier
02 real-data `shock_window_calendar.csv` both give 2024q3 window
2024-09-01 through 2024-09-17. The PBOC dates the incremental policy-package
announcement to September 24 (official governor speech:
https://www.pbc.gov.cn/en/3688110/3688175/2025080817533781528/index.html).
Thus the documented shock window precedes this announcement; do not label
its gain as the realized gain from that announcement. Current-run calendar
was not among these 13 screenshots, so verify parity and respondent submission
dates against September 24 in the next approved diagnostic. Post-window-only
allows answers both before and after September 24. Policy effects on answers
and intervening portfolio returns are possible only if timing permits them;
they have not been established. Dropping 2024q3 checks wave dependence, not
by itself a causal policy mechanism. Stock outcome covers four observed waves
initially and three after dropping q3, because 2024q2 stock was not asked.

- Conditional residual X SD is .0995–.1273 units (995–1,273 yuan), retaining
  44.67%–61.85% of demeaned X SS. The full model has usable variation.
  Neither this ratio nor residual degrees of freedom establishes exogeneity.
- Cells remain sparse: stock 578 cells/144 singletons, 18.96% of full-sample
  observations in cells smaller than five; revenue 964/101 and 5.05%.
  Median cell size is 3–7 across outcomes. Full-sample constant-X shares
  (45.08%–49.96%) include structural zero cells; they should not be read as
  the positive-investor loss of variation. Report density/balance separately
  for the positive-only sample before changing bins; pooled zero observations
  can make full-sample density percentages look more favorable.
- Balance summary: 55 individual tests, one raw p<.05 (minimum .0482), none
  after Holm. This is limited reassurance. Current tests regress X on each
  trait plus FE, on outcome-specific complete cases; screenshots do not show
  standardized effects, each test's N or a joint test. Positive-only balance
  is needed because zeros may dilute full-sample associations. Timing of
  employer traits/employee-group controls needs checking before calling all
  of them predetermined.
- User clustering addresses repeat users, not necessarily dependence across
  users with common fund exposures. Fund/asset-class shock concentration and
  suitable shock-level inference need evaluation. Conventional wave clustering
  with only five waves is not a sufficient fix. Related methodological basis:
  Adao, Kolesar and Morales, https://www.nber.org/papers/w24944 ; applicability
  to this portfolio design must be established rather than assumed.
- NAV inputs are unit-price returns, not fully corporate-action-adjusted total
  returns. Current source policy/default retains calculable flagged values;
  the supplied settings screenshots do not display the quality-screen switch.
  Verify its actual run value. Historical risk/mean and current gains can both
  be affected by NAV events. Compare screened returns/coverage, common samples
  and gain-tail influence before a wealth-effect interpretation.
- Selection remains material: answer-time filter drops 8,009 of 36,153 owners;
  college completeness drops 4,620 of 26,705 at that step. Outcome complete
  cases vary. Stock lacks 2024q2 by questionnaire design, not nonresponse.
  Do not interpret pooled outcome-missing counts as attrition alone or compare
  coefficients across outcomes as if samples/scales were identical.
- Recommended next submission: positive-only exact-sample density and full
  balance summaries; shock leverage/tail and NAV-screen sensitivity; leave-one-
  wave-out (including 2024q3) and supported wave-by-industry/geography controls;
  prespecified cell-coarsening and continuous portfolio controls; mapped-Y and
  selection sensitivity. Test roles and outcome families should be fixed before
  inspecting new p-values. Common-shock inference remains a separate priority.

Current conclusion: zero inclusion does not drive the main observed coefficient
patterns; no multiplicity-robust main effect is established. Retain all 11
outcomes and the positive-only benchmark, with input costs labeled exploratory.

### Follow-up design advice (proposals, not implemented)

- The pattern is not broad optimism: stock/revenue/demand/environment do not
  show clear effects. Lower input-cost expectations could reflect perceived
  cost relief, but lower wage/product-price coefficients can also fit weaker
  demand; positive CPI does not establish a common disinflation mechanism.
  Wealth/cushion, information/attention and portfolio-exposure confounding are
  competing hypotheses, not identified mechanisms.
- Keep current specification as reference; prioritize 10/3/3 and 5/3/3
  candidate cells against 10/5/5 on fixed outcome samples. Preserve separate
  wave-specific zero cells and rank only positives. Select coarseness using
  density, balance and overlap, not p-values. Add flexible predetermined size,
  risk and expected-return controls where support permits. Use the same cell
  assignments for the positive-only versus keep-zero comparison.
- Wave-by-portfolio-cell FE already absorb wave intercepts. Prioritize
  wave-by-industry and wave-by-city-tier over indiscriminate additional FE;
  `city_level_from_yicai` is city tier, not individual-city FE. Check actual
  city identifiers if finer geography is contemplated. Employee groups must
  be predetermined before being treated as baseline controls. Individual FE
  require checking repeat participation and within-user support first.
- Because G=H*r, gain and return have different scales and weighting. Compare
  both on identical positive-only observations, FE, controls and cells; zero
  portfolio return is undefined and must not be filled with zero. A significant
  gain coefficient and insignificant return coefficient do not identify a
  wealth channel. At fixed H the regressors are proportional; joint models
  require size variation, adequate support and explicit interpretation.
- Preferred first comparison matrix: positive-only gain/return crossed with
  five configured waves / dropping 2024q3. Keep-zero gain is the existing
  benchmark (and optional corresponding four-wave comparison). Examine beta,
  intervals, standardized/common-unit magnitudes and wave interactions rather
  than changes in stars. Event-date-aligned diagnosis precedes policy claims.
- For zero robustness, cell-FE-only slopes should coincide on identical
  positive observations. Fully interacting the other FE/control coefficients
  with zero/positive status can diagnose effects of shared nuisance slopes.
  Zero observations cannot identify a gain-response slope of zero holders.

## 2026-10-16 Missing 01 Coefficients Are a Global Integrity Block

- User confirmed that all screenshots supplied in this diagnostic exchange
  are real-data backend results. The conflict and counts below are therefore
  real-data evidence. Online cells use simulation and cannot inspect these
  records; further diagnostics require the complete approval/backend workflow.

- The supplied R6 screenshots identify `conflicting_source_keys_2024q2_addon`
  as the blocker; all 11 outcomes have `blocked_integrity_gate` notes.
  Missing coefficients are not estimated null effects or evidence of failed
  identification. Regression-ready counts range from 4,346 to 17,519.
- Current 01 checks raw answer tuples by addon `submit_id` and blocks all
  outcomes, including those not using addon answers. The screenshots do not
  establish whether conflicts survive answer normalization or intersect
  the final analysis sample. Resolve this before interpreting estimates.
- Evidence and configuration: 2026-10-16 blocked R6 entry in the run log.

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
