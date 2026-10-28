# Identification

## 2026-10-28 v19 approved audit and run-volume policy

This section supersedes the active v18 grid. Passive gain units, source tables,
NAV flags-only choice, timing/history requirements, fixed cell assignments and
five-wave scaling are unchanged. No stock return-rate substitution or new IV.

A: broad eligible outcome sample, cell FE only. B: T2-complete outcome sample,
cell only. C: same sample, T2 personal/business controls. D: same sample, C plus
wave-specific linear and six standardized polynomial portfolio terms. E: same
sample, D plus wave-specific portfolio amount (10,000 yuan). B–E use identical
rows per outcome; not the intersection of all eleven outcomes. Invalid portfolio
design terms skip the outcome comparison explicitly rather than silently trim
one specification. No extra employee-size or prior-response requirement.
Current trait stability is still assumed, not validated pre-shock measurement.

Three complete-workflow batches avoid repeating all tests over W5/W4 and six
legacy specifications. `core` estimates 55 A–E plus 22 C/E positive-only plus
22 C/E current outcomes on the corresponding own-prior available positive subset
(maximum99 fits). Prior placebo is own prior outcome only (22 tests), with strict
previous scheduled response date before current shock; no backfill. All eleven
outcomes use their existing harmonized mapping, missing stock q2 stays missing.
Question equivalence still relies on the maintained mapping, not a new survey
validation. Report matching current outcomes so repeat-response selection is visible.

Core investor balance has 11 outcomes × 5 dated prior traits × 2 adjustments =110
rows. Both adjustments use the exact C/E common sample, restricted to positive
holders with that prior trait available. The adjustments are cell only and
portfolio-only W3, NOT all current trait controls; this avoids mechanically
absorbing the trait under test. The five are prior age, college, firm age,
registration and employment. Common positive BASE SD standardizes slopes/CIs.
Holm within five traits per outcome/adjustment. Not evidence for all missing
traits/respondents, unobservables or q2 where prior data are absent. The old
290-row broad-sample investor grid and180-row portfolio grid are not repeated.

`tail`: 22 C/E baseline anchors +88 tail refits +44 user refits =maximum154.
Capital cutoffs are positive pre-outcome BASE wave-specific 99.5/99 percentiles
of `portfolio_size_raw`; drop strictly above, keep boundary ties. Same cutoffs
across outcomes/models. This is predetermined source snapshot capital, not
realized gain. Residual deletion removes ceil(.005/.01 × positive N) observations
with largest squared gain residual in each original C/E fit, stable index tie
break. Both rules keep zero holders. Different cutoffs define different samples,
not automatically a superior causal estimand. `user_1` and `user_2` separately
remove all rows of each of the top two absolute cluster-score users, ranked once
in the original model. Score selection depends on Y and is diagnostic only.
All deletions genuinely refit FE, controls and user-cluster SE. Original cells
and scaling remain fixed. Report removed observations, disappeared cells and
baseline cells losing within-cell raw gain variation (including disappeared
cells), plus re-estimated residual concentration. No user IDs are output.

`wave`: 22 anchors +110 leave-one-wave-out fits +22 interaction fits =maximum154.
No separate default W4 grid: omitting q3 is one of five symmetric checks. Stock
q2 omission repeats baseline and is marked no-new-evidence. Interaction fit has
one gain slope per observed wave, original FE and shared trait coefficients;
E keeps wave-specific portfolio controls. Print all five wave rows including
missing/unidentified flags. Equality Wald uses user-cluster covariance over
estimable observed slopes, labels partial coverage and skips singular contrast
covariance. A common-fund correction remains unimplemented; five-wave clustering
is not substituted for user clustering.

Outcome Holm has fixed11 slots per model/scenario, filling unavailable tests with
p=1 for adjustment only (their printed estimates/p remain missing). Own-prior
checks and equality Wald tests similarly adjust eleven outcomes per C/E model.
Wave slopes adjust eleven per model/wave. None protects searching across models,
trimming rules or batches; report all predeclared scenarios. Check baseline
anchors match across batches before comparing results from backend PDFs.
Compact reporting retains all results/CI/skips but prints group decomposition
only for C/E anchors and does not repeat full size-bin grids after every refit.


## 2026-10-25 Approved primary personal/business controls (v18)

The primary comparison now follows the user's selected two control layers:

| Model | Fixed effects | Numeric controls |
| --- | --- | --- |
| T0 | Fixed wave-by-portfolio cell (10/3/3) | None |
| T1 | T0 plus gender category | Age, college indicator |
| T2 | T1 plus city tier and broad industry categories | T1 plus firm age, company registration indicator |

T0/T1/T2 share the T2 complete-case sample for each of 11 outcomes within each
W5/W4 set (66 planned estimates). Basic-only availability is reported as sample
coverage, not estimated as a differently sized T1 column. Missing/nonfinite
numeric traits and missing categorical traits are excluded explicitly for all
three columns; missing columns yield empty/skipped primary fits. Unavailable
traits do not filter the 132 supplemental M0/M1/M2/W1/W2/W3 portfolio fits.
T0 vs supplemental M0 therefore diagnoses sample changes, not added controls.
The new grid does not additionally impose portfolio polynomial controls.

Current-wave survey records supply age, education and business characteristics;
gender retains the existing portrait source. No prior survey response is required.
Using them as controls assumes relevant stability over the shock window; this
does not establish that mutable registration, location or industry was measured
before the shock. Employee size, risk rating and newly discussed financial or
behavioral tables are outside this change. Existing coarse firm-age conversion
and education binary are preserved, not silently redefined.

User confirmed broad-industry codes v41/v42/v28/v29/v29 for 2024q2--2025q2.
This supersedes historical 2024q2 v43 (specific service industry) in 01 and 02.
No broad-industry value is imputed from a detailed-service answer.

Inference remains OLS on passive gain (10,000 yuan), user-cluster SEs, signed
95% normal CIs and outcome Holm separately within each wave/model. Report all
specifications; do not select controls using p-values. The existing diagnostic
tables are not reinterpreted as validation of primary complete-case samples.
No automatic all-p>0.05 gate, no switch to the paper's IV estimator, and no new
empirical findings before platform execution.

## 2026-10-25 Investor balance interpretation adopted (v17; pending platform run)

Following Andersen, Johannesen and Sheridan (2024), pp.443-444, Figure 1 and
footnote 9, the primary balance question is whether passive gains remain
associated with predetermined investor characteristics conditional on portfolio
cells. Evaluate signed economic magnitudes and confidence intervals together;
do not require every p-value to exceed 0.05 or treat nonsignificance as proof of
random assignment. These are pooled conditional associations, not separate
tests within each cell. Portfolio-input checks remain supplementary diagnostics
of coarse bins. Statistical significance alone does not establish a material
identification failure, and wide intervals are inconclusive rather than passes.

v17 adds paired raw/cell-only regressions of prior investor traits on current
passive gain, on identical target-specific positive-holder subsets. This slope
orientation differs from the paper's plots (gain on the vertical axis); these
tables implement a related balance diagnostic, not a reproduction of Figure 1.
The five targets are previous-wave age, college, firm age, registration and
employment midpoint. The prior scheduled wave must have a unique owner answer,
pass duration eligibility and strictly precede the current shock start. No
backfill, current-trait substitution or imputation is permitted. This stricter
timing choice restricts evidence to repeat respondents, not the whole sample.
The original paper's deposits/risky share/spending targets are not recreated
from unavailable fields. Our firm traits are project-specific extensions.

Report W5/W4 for BASE and all 11 outcome samples, plus BASE by wave: up to
290 rows (including explicit missing/skipped rows). Both sides of each raw/cell
comparison have the same target-specific sample and five-wave BASE SD reference.
Report N, missing prior, raw slope, signed standardized slope, 95% CI, raw p and
Holm within five traits per sample/scope/adjustment. This correction is not over
all 290 comparisons. No automatic cell/model selection or balance pass gate.
Targets absorbed by the design and unavailable/underpowered checks are not passes.

Main outcome specifications, all 11 outcomes, existing prior-expectation checks,
and fixed cell assignments remain as in v16. Adding demographics to the main
models is a separate specification change, not implemented by this diagnostic
update. The analysis still regresses expectations on passive gain; the paper
instruments actual gain with passive gain. No new causal claim or platform result.

## 2026-10-25 v16 identification checks implemented - awaiting platform run

Revision `sme_rf_v16_identification_checks`; RUN_ID
`wave_identification_gain_keepzero`; replace Cells 1-16 in a fresh session.
All ELEVEN outcomes remain active: W5/W4 x M0/M1/M2/W1/W2/W3 = 132 planned
main fits. User explicitly requested retaining the full outcome scope.
M0-M2 retain v15 definitions. W1 uses wave-specific linear portfolio controls;
W2 adds wave-specific six polynomial terms; W3 adds wave-specific portfolio
amount in 10,000 yuan. No new data tables or factor-return construction.

Cells and five-wave polynomial scaling remain fixed; common samples within
outcome/wave set across all six models. Invalid added inputs skip all six
models for that sample, not silently trim it. Omitted-wave all-zero interaction
columns are excluded from estimation/covariance column counts. Outcome Holm
uses eleven outcomes separately per wave/model; it does not adjust model selection.

Diagnostics: 180 planned signed cell-only checks (BASE + all 11 actual outcome
samples, five waves, three targets). Stock q2 is empty, with explicit skip notes.
Common five-wave positive BASE standardization. Independent prior-expectation
checks remain focused on current CPI/cost: 48 planned rows across both wave
sets, six models and two previous-wave targets. Previous scheduled wave only,
unique owner response passing duration, answer strictly before current shock
start; no backfill or contemporaneous traits. Missing prior answers never
filter main fits. Positive repeat-response subsets and their missing counts
are reported; Holm covers all tested prior-check rows. These are diagnostic
associations, not proof of exogeneity or an event-study design.

Every main fit reports residual gain SS/SD, retained SS, top-1-percent-positive
observation SS share, maximum observation SS share and maximum absolute user
score. Scores are first-order influence measures, not exact leave-one-out
changes. Group SS shares sum to one and coefficient contributions sum to beta;
contributions are not separately estimated wave causal effects. Fixed five-wave
size ranks are used. Compact groups show M0/W3 wave contributions for all Y and
size contributions for CPI/cost; full mode shows all groups/models. No IDs or
individual outcomes are released. Common-fund inference remains unresolved;
fund type/industry/beta and pre-business trajectories are unavailable in current
mapped inputs and are explicitly reported as such, not inferred or imputed.

Report rows now have stable keys repeated in every panel, including unique
continuation keys, preventing `unique` from deleting repeated p-value rows.
No new empirical results: local checks use synthetic data only.


## 2026-10-22 Fixed C3 wave/control run implemented — awaiting platform execution

Revision `sme_rf_v15_wave_controls`; RUN_ID `wave_controls_gain_keepzero`;
RUN_MODE `wave_controls`, OUTPUT_MODE `compact`; replace Cells 1–16.
W5 (all five) / W4 (omit 2024q3) x M0/M1/M2 x 11 outcomes = 66 planned
outcome fits. Fixed 10/3/3 cells: M0 cell FE only; M1 adds three linear
portfolio features; M2 adds six standardized squares/products. Both zero
sources remain. Per-outcome samples are identical across models; invalid
cell/polynomial inputs skip the affected wave/outcome triplet without silent
drops. Optional survey controls and other FE do not filter samples.
Five-wave preparation, ranks and polynomial scaling are reused unchanged.

Only 15 targeted balance checks run: positive BASE x five waves x log size,
size squared and size/history-mean interaction. Cell demeaning batches the
three targets per wave (normally five projections). Signed effects and CIs
use a common five-wave positive BASE SD(gain)/SD(target) reference. This
screens cancellation; it does not certify all covariates or outcome samples.
No automatic wave/control selection by outcome significance. Main estimates
use the existing statsmodels OLS/user-cluster covariance; no auxiliary
variation fits in this mode. Gain aliasing suppresses the affected estimate.

Compact output: settings/gates, 11-row sample comparison, W5/W4 M0–M2
beta/SE/raw-p tables, 15 signed balance rows, timing and actual fit counts.
Outcome CIs/Holm (within each wave/model's outcome family) and preparation
appendix require full mode. No full density/balance grid, gain-sign dummies,
employee sample or additional FE search. Runtime and real coefficients
remain pending; local synthetic verification is not platform evidence.


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
