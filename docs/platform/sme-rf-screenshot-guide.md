# SME RF: E1-E4 Four-Wave Design Diagnostics

Revision `sme_rf_v13_e_design_checks`; `RUN_ID="e_fourwave_gain_keepzero"`.
Run all Cells 1–16 with `RUN_MODE="e_design"`, `OUTPUT_MODE="compact"`.
Replace the full notebook blocks, including Cell 3 and Cell 7. Online execution
validates simulation only; real estimates require the approved backend report.
No new policy/response-date audit or policy-date sample split is implemented.
Existing eligibility/timing checks remain unchanged.

## Specifications

All E models exclude 2024q3 after fixed cell construction and use the same
outcome-specific complete-case sample. Both zero sources remain. The X is
passive_gain per 10,000 yuan. Other base FE, baseline traits and three portfolio
controls are retained unless explicitly replaced below.

| Model | Cells size/risk/mean | Change |
|---|---|---|
| E1 | 5/3/3 | Original other FE and linear portfolio controls |
| E2 | 10/3/3 | More detailed size matching |
| E3 | 5/3/3 | Replace city-level and industry FE with city-level x wave and industry x wave |
| E4 | 5/3/3 | Add three squares and three pairwise products of standardized portfolio controls |

Five waves are prepared once so C/D cell-only balance can use the exact reference
eligibility; their outcome regressions are not rerun. Normally 44 outcome fits.
The original fine cell eligibility remains required for comparability. All
three cell assignments use the same pre-outcome eligible population. Ranking
is within wave, so omission does not rerank retained waves. Missing derived
inputs skip the affected model with a note; no silent sample reduction.

E4 scaling is fixed on positive eligible four-wave records before outcome
selection. Center/scale the log portfolio yuan, history SD pp and history mean
pp; construct six second-order terms; zero-holder design values stay zero.
Raw zero-holder history stays missing. The basis is not re-scaled per outcome.
Historical mean is not a subjective expected return measure.

## Balance diagnostics

Cell-only references: C (five-wave coarse), D (four-wave fine), E1 and E2.
E3/E4 share E1 cell-only diagnostics. Targets are four baseline traits and
three portfolio controls. Final-model checks for E1-E4 mark included targets
as controlled_not_a_test; test remaining nonlinear portfolio terms and the
employee midpoint, where estimable. E4 controls all six polynomial targets.
Survey traits, especially employment, have unverified pre-shock measurement
and are supplementary associations, not evidence of pre-treatment balance.
Fully absorbed/constant targets are non-tests, never passes. Missing employee
values reduce its diagnostic sample only; N and dropped counts are reported.

Both all and positive scopes are checked; no positive-only outcome fit is run.
Cell-only projections use demeaning; final projections reuse a pseudoinverse
across targets with the same complete-case mask. User-cluster inference uses
normal p-values and 95% intervals; HC1 is supported. Standardized effect is
trait-on-gain slope times raw gain SD / raw trait SD in the diagnostic sample.
Holm spans all estimable Y-trait pairs per specification/layer/scope, separately
from the 11-outcome family of each E specification. It does not cover all model
search. Do not select a design merely because balance p-values exceed .05.

## Report order

| Cell | Content |
|---|---|
| 9 | Settings, integrity, existing shock calendar, common sample audit |
| 10 | E1/E2 estimates and common composition |
| 11 | E3/E4 estimates and polynomial scaling |
| 12 | E1/E2 density, all and positive (E3/E4 duplicate E1) |
| 13 | Conditional gain variation for all four models |
| 14 | Balance family summaries, skipped statuses, interpretation |
| 15 | Balance details and timing/counters |
| 16 | Optional preparation appendix and REPORT END |

Compact balance detail shows top three absolute standardized effects in each
family plus all Holm flags, with confidence intervals. Full shows all attempted
rows. Both modes compute the same models and diagnostics. More diagnostics
can increase elapsed time; no runtime guarantee. Separate main fits, balance
projections and component timers are reported. No microdata are exported.

## Local checks

`python -m py_compile scripts/analysis/01_sme_expectations_rf.py`
`python tests/test_sme_rf.py`
`python tests/test_sme_diagnostics.py`
`python tests/test_addon_resolution.py`

Synthetic checks cover actual Cell 7 assignment/merge, fixed E samples and
zero conventions, 44 main fits, blocked/missing inputs, robust covariance
parity against direct regressions, Holm families and ordered report output.
Local checks do not substitute for the platform environment or real-data run.
