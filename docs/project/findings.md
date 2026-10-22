# Reusable Findings From The Old Project

## 2026-10-21 Wave-cell design analysis — Cells 9–13 plus targeted Cell 14 verification

User authorized interpretation before the missing tail arrives. Evidence is the
archived v14 run_001 report, not a local microdata rerun. Cells 9–13 CSVs are
verified. Nine selected Cell 14 rows were visually checked against PDF pages
16–18 and 33–34, saved in balance_targeted_verified.csv; other OCR remains
unverified except the previously certified rows 67–78. Original pages 118–121
and actual Cell 15 counters remain pending. Run-specific simulation/backend
provenance remains unconfirmed; conclusions are conditional on report provenance.

Main assessment: W5_C3 (five waves, 10/3/3) is the strongest current candidate
for further estimation, not a certified quasi-random design. W5_C2 is a useful
coarser sensitivity. W4 remains necessary as a wave-sensitivity comparison;
the current balance evidence does not support deleting q3 to improve design.
No outcome coefficients are available in this run and no scripts were changed.

Positive-scope comparisons (outcome ranges exclude BASE):

| Design | BASE max absolute portfolio std | 99 outcome/portfolio pairs max abs std | Outcome sparse share range | Cell median range |
|---|---:|---:|---:|---:|
| W5_C1 | .109149 | .145151 | .04%–.53% | 23–72 |
| W5_C2 | .077678 | .099796 | .10%–1.97% | 14–44 |
| W5_C3 | .046766 | .075347 | .38%–8.24% | 7–22 |
| W4_C1 | .244125 | .414766 | .05%–.67% | 21–73.5 |
| W4_C2 | .179697 | .315510 | .10%–2.45% | 13–44 |
| W4_C3 | .111372 | .213812 | .37%–10.25% | 6–23 |

- These are maxima over predefined targets, not average imbalance or partial
  correlations. Standardization uses raw gain and trait SD in each diagnostic
  sample. W5/W4 scales and sample composition differ, so differences in maxima
  are descriptive, not a formal test of equal slopes or an effect of q3.
- Coarsening buys density and variation but leaves larger portfolio dependence.
  The opposite change in balance maxima and sparsity is a real design tradeoff;
  no balance-equivalence tolerance was prespecified, and smaller effects alone
  do not establish adequate exogeneity. 3/3/3 is useful as a benchmark, not the
  preferred cell-only causal specification on current evidence.
- W5_C3 positive BASE's maximum is standardized log-size x history mean:
  .046766, CI [.020520,.073012], raw p .000479, Holm .004309. It is precisely
  nonzero even though much smaller than coarser alternatives. The maximum
  outcome-sample slope is stock/log-size squared .075347, CI [-.011259,.161954],
  p .088159. Non-rejection here does not exclude moderately sized imbalance.
- W4_C3 stock/log-size squared is .213812, CI [.174180,.253444]; its stock
  linear log-size association is .061876, CI [.050140,.073612]. W4_C3 BASE
  log-size squared is .111372, CI [.058277,.164467]. Thus the W4 problem is
  not only lower power/wider intervals. Rounded p=0.000000 is not exact zero.
- W5_C3 outcome/portfolio raw flags are 15/99, despite zero Holm flags; BASE
  has one Holm flag among nine targets. Different test-family sizes and sample
  composition explain why outcome-family Holm is not a blanket balance pass.
  Survey max slopes are smaller (positive W5_C3 BASE .010608, outcomes .043765),
  but timing is unverified and missingness is target-specific. Empty skipped
  output means every attempted test ran, not that no observations were dropped.
- Targeted cost diagnostics still show small nonzero associations: W5_C3
  history mean -.018814, CI [-.033789,-.003838], raw p .013805; historical
  risk x mean -.034678, CI [-.061102,-.008255], p .010102. W4_C3 history mean
  -.024966, CI [-.041710,-.008222], p .003473. These are balance slopes, NOT
  cost outcome coefficients, and do not identify bias direction/magnitude.
- BASE W5/W4 N=26,740/20,868; positive N=14,431/11,127. Cost N=10,328/7,763,
  positive=5,659/4,233. Current samples omit legacy optional-control/other-FE
  complete-case filtering, so v13 outcome estimates cannot be transplanted
  or compared as if only cells/waves changed. Stock has four/three waves.
- Conditional gain variation survives every candidate. Positive outcome SS
  shares: W5_C3 .520876–.665074; W4_C3 .595221–.745712. Higher retained fractions
  after q3 removal do not mean more absolute information: cost residual SD
  .152279 -> .148869 gain units (about 1,523 -> 1,489 yuan), while positive N
  falls 5,659 -> 4,233. Approximate conditional SS=(N-1)*resid_sd^2 falls 28.5%.
  BASE conditional SS falls 34.1%; stock 39.5%. These are regressor-variation
  measures, not complete precision calculations under clustered inference.
- C3 cost sparsity remains limited: positive below-five share 3.32%/3.78%,
  median 10 in both W5/W4. Stock 7.57%/9.36%, house 8.24%/10.25%; stronger
  caution is warranted for these smaller outcome samples. Full-sample no-X
  shares mainly reflect structural zero cells; zeros are not a randomized
  control group and do not provide direct within-cell shock variation.
- Better pooled W5 balance is not proof that q3 is clean: cell FE remove wave
  means but impose a common diagnostic slope. Opposite within-wave associations
  can cancel, and removing q3 changes the weights and raw SD standardization.
  Next check fixed-cell balance by wave (signed raw slope and uncertainty,
  common-reference effect scaling if comparing waves), especially BASE/stock/
  cost, for 5/3/3 and 10/3/3. No arbitrary wave omission should be chosen by
  outcome significance or pooled balance alone.
- Next estimation proposal, not implemented: use 10/3/3 as the leading cell
  candidate with both W5 and W4, M0 cell-only / M1 plus linear portfolio terms /
  M2 plus the six polynomial terms, on fixed outcome-specific common samples.
  Retain 5/3/3 as a limited coarser comparator. If estimates move materially
  under necessary portfolio adjustment, simple cell-only identification needs
  qualification. Do not treat controlled polynomial balance as an independent
  validation. Broader FE search, dummy gain and employees can wait.


## 2026-10-21 E1-E4 report — authorized interpretation

Evidence: external CSMAR `outputs/platform_runs/sme_rf_e_design_checks/run_001/`,
24 original images and 27 CSV transcriptions; revision `sme_rf_v13_e_design_checks`.
User requested analysis after collection. All 24 image hashes rechecked with no
mismatch; 44 estimate rows checked against common outcome-specific sample counts.
These are rounded platform-report results, not new local microdata estimates.
Provenance follows the prior backend-report context, without fresh independent
run-specific confirmation. Source tables are E1-E4_estimates/intervals/variation,
common_composition, sample_selection, E1/E2_density_positive, balance_families,
balance_skipped, balance_detail_cell/final, settings and timing/count tables.

- Execution gate PASS, no blockers. All control_drop and derived_missing counts
  are zero. E1-E4 share each outcome's sample, omit 2024q3 and retain both zero
  sources. Stock has three waves (no 2024q2 question); the other outcomes four.
  Cost N=6,049 / 5,735 users, including 3,229 positive holders. Samples differ
  across outcomes, so cross-outcome contrasts are not common-sample tests.
- Cost beta / SE / raw p / within-specification Holm p:
  E1 -.25456 / .16942 / .1330 / 1.0000;
  E2 -.40794 / .14141 / .0039 / .0431;
  E3 -.25121 / .17299 / .1465 / 1.0000;
  E4 -.32071 / .14653 / .0286 / .3148.
  E2 cost is the only Holm-significant outcome in the four reported families.
  E2 ordinary 95% CI is [-.68510,-.13079]; E1 [-.58663,.07750];
  E4 [-.60791,-.03350]. These are not simultaneous confidence intervals.
  E2 GDP beta .53309, raw p .0112, Holm .1115. E1/E3 have no raw p<.05;
  E4 has only cost at raw p<.05. No other outcome passes Holm.
- Cost direction is consistent across E specifications, but magnitude and
  inference depend on conditioning. E2 increases absolute beta about 60% over
  E1 while reducing SE about 17%; this is not merely a threshold crossing from
  unchanged estimates. The reported Holm correction covers 11 outcomes within
  each specification, not the search across specifications. Do not choose E2
  as the main model solely for significance. No coefficient-difference test
  is available from these marginal summaries.
- Gain is measured per 10,000 yuan; cost is mapped expected percentage points.
  E1/E2/E3/E4 cost residual-gain SDs .1164/.1098/.1163/.1125 imply effects
  -.02963/-.04479/-.02922/-.03608 percentage points per residual SD. A 10,000-yuan
  contrast is much larger than typical conditional variation. The association
  concerns expected input costs, not observed costs or an established mechanism.
- E1 positive-cell median sizes range 8-34, with .29%-6.46% of observations in
  cells below five. E2 medians are 4-16, with .72%-17.95% below five. For cost,
  median 16 -> 7 and sparse share 1.80% -> 7.56%; stock 5.04% -> 14.59%, house
  6.46% -> 17.95%. Finer size bins trade sample support for tighter conditioning.
  E2 remains less sparse than historical D's 10/5/5 cells but does not eliminate
  sparse support. E3/E4 retain E1 cells and samples.
- Conditional gain variation remains positive for every outcome. SS shares:
  E1 .6052-.8175, E2 .4636-.7326, E3 .6038-.8158, E4 .4631-.7636. For cost,
  E1 .8035 -> E2 .7146 / E3 .8025 / E4 .7502. This rules out complete absorption
  of the shock, not weak support, tail influence or confounding. Zero cells
  have no direct within-cell gain variation; positive diagnostics are not
  additional positive-only outcome regressions.
- Cell-only balance rejects some linear portfolio balance: E1 six Holm flags
  in each scope, E2 five, D six/all and four/positive, C one in each scope.
  C has five waves, unlike D/E, so its lower flag count is not a same-sample
  design ranking. Final E1/E2/E3 have respectively 10/7/10 Holm flags per scope,
  concentrated in standardized log-size squared (ctrl_poly_00) and log-size x
  historical risk (ctrl_poly_01). Positive-scope maximum standardized slopes
  are .2124/.1357/.2121; full-scope .1789/.1136/.1786. These are trait changes
  in raw trait SDs per raw gain SD, not partial correlations or residual-SD
  effects. Different diagnostic layers test different target sets; their
  flag counts and maxima must not be treated as a common before/after metric.
- E3 adds city-level/industry-by-wave FE but barely changes E1 cost, conditional
  variation or nonlinear balance. These interactions do not address the
  detected portfolio nonlinearity; they also cannot rule out all common shocks.
- E4 directly controls all six polynomial terms. Its 143/154 attempted targets
  per scope are marked controlled_not_a_test, leaving only 11 employee-midpoint
  tests. Thus zero Holm flags is not proof of broad balance. Revenue's employee
  diagnostic has raw p .0391 (all) / .0425 (positive), Holm .4306/.4672 and small
  standardized slopes .0044/.0058. Employment groups are already FE, numeric
  employment is coarsely mapped, and survey timing is unverified. These provide
  limited independent evidence about exogeneity.
- Historical C and E1 use the same coarse design but five/four waves: cost
  -.43343 -> -.25456, CPI .41247 -> .12141, wage -.34009 -> -.01858. This supports
  wave sensitivity, without proving coefficient differences or a policy effect.
  E2's cost signal after omitting q3 means it is too strong to claim that all
  negative cost evidence is confined to q3; its identification remains qualified.
- Interpretation: a recurring negative cost association merits targeted follow-up,
  but neither broad optimism nor a robust causal wealth effect is established.
  The immediate design issue is nonlinear portfolio conditioning and influential
  exposures, rather than simply adding more group-by-wave FE. A future combined
  E2-plus-polynomial check would address the remaining gap (not run here).
  Pre-shock outcomes/traits, NAV-quality sensitivity and common-fund-shock
  inference remain useful independent checks. User clustering and flags-only
  unit-NAV returns retain their previously documented limitations.
- Recorded stage times total 1,460.39 seconds (24.34 minutes), including 968.29
  seconds aggregation (66.30%). Cell 8 is 223.04 seconds; components report 43.24
  for regression/variation and 168.45 for balance (nested, not additive to stages).
  Counts are 44 outcome fits, zero variation fallbacks, 242 balance projections.
  Timers may include inter-cell waits; no controlled speed comparison is claimed.


## 2026-10-19 D diagnostics supplement — report complete

Image 11 and D_density_all.csv, D_density_positive.csv, D_variation.csv added
to CSMAR outputs/platform_runs/sme_rf_cd_gain_only/run_001 (11 images, 15 CSVs).
All diagnostic counts match D composition. Previously missing tables now received.
Compared with v11 fine-cell full-wave reference, positive sparse-cell shares
rise for every outcome (D range 10.56%-44.94%); medians are 2-6. Stock sparse
share .3270 -> .4342; house .3355 -> .4494; cost .2122 -> .2530.
Residual gain SD decreases for every outcome, but stays positive. Cost .1098
-> .1053 (-4.1%); CPI .1198 -> .1133 (-5.4%); wage .1073 -> .1018 (-5.1%).
Cost conditional SS share increases .5814 -> .6576: retained fraction is not
absolute residual variation or total information. Cost attenuation cannot be
attributed simply to FE absorbing all gain variation. Fewer observations and
sparser cells still reduce support; coefficient differences not formally tested.
Main conclusion unchanged: no C/D Holm-significant outcome; wave sensitivity
and conditional associations, not a policy effect. No script changes.


## 2026-10-19 C/D robustness report

Evidence: CSMAR outputs/platform_runs/sme_rf_cd_gain_only/run_001 (10 images,
12 CSVs); local comparison reference is v11 include-zero continuous-control
specification, not its baseline. Displayed rounded values only.

- C holds observed sample sizes and zero composition fixed while coarsening
  cells to 5/3/3. Positive-holder cell median rises from 3-7 to 9-34.5;
  share in cells below 5 falls to .24%-4.31% (old 9.10%-33.55%). Conditional
  gain SS share .6544-.7824. Less restrictive FE retain more variation but
  do not demonstrate exogeneity; lower R2 with fewer FE is expected.
- CPI old beta .34874 (p .0787) -> C .41247 (p .0244, Holm .2687).
  Input cost -.56035 (p .0141) -> C -.43343 (p .0382, Holm .3820).
  Wage -.38688 -> C -.34009 (p .0851). No C outcome passes Holm.
- D omits 2024q3 with original fine cells: input cost -.20951, SE .16730,
  p .2105; CPI .11092 p .5357; wage -.16641 p .2966. Input-cost SE is
  smaller than old .22827 despite fewer observations, so lost significance
  is not explained solely by increased uncertainty. Coefficient attenuates
  about 62.6%; this is sensitivity, not a formal cross-model difference test.
  GDP .51659 p .0342, Holm .3765; no D outcome passes Holm.
- C and D differ in two dimensions: compare each to v11 separately. No direct
  C-D one-factor causal interpretation. Omission changes observation and
  exposure composition; does not identify policy effect or prove all signal
  originates in 2024q3. Report q3 gain window is Sep 1-17; policy timing
  relative to gain and response dates must be checked before a policy story.
- Zero-holder cells have no direct within-cell gain variation. Their retention
  helps shared nuisance estimation under model assumptions; full-sample
  noX shares .4225-.4657 mostly reflect structural zeros. Positive-only C
  noX shares .0004-.0054. These descriptive splits are not separate slopes.
- Evidence supports exploratory cost/wage negative and CPI positive patterns,
  not robust multiple-testing-adjusted causal conclusions. C cost effect per
  residual gain SD is -.43343*.1253 = -.05431 mapped percentage points.
  Historical mean is a historical proxy, not subjective expected return.
- Next interpretation needs D density/variation report; later targeted wave
  heterogeneity, pre-shock expectation/placebo and exposure-quality diagnostics
  can address remaining ambiguity. User-cluster SE alone does not resolve
  correlated common fund shocks; no new broad specification search authorized.


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
