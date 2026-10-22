# SME wave-by-cell design diagnostic report

Revision `sme_rf_v14_wave_cell_diagnostics`; `RUN_ID="wave_cell_gain_keepzero"`.
Run **Cells 1–16**, `RUN_MODE="wave_cell_design"`, `OUTPUT_MODE="compact"`.
Replace all blocks in a fresh notebook session, especially Cells 2, 3, 7 and
8–16. Input tables and NAV/zero/history/timing policies are unchanged. Online
simulation verifies execution only; real findings require the backend report.

## Six designs

| Group | Waves | Size/risk/history-mean bins |
|---|---|---|
| W5_C1 | all five | 3/3/3 |
| W5_C2 | all five | 5/3/3 |
| W5_C3 | all five | 10/3/3 |
| W4_C1 | omit 2024q3 | 3/3/3 |
| W4_C2 | omit 2024q3 | 5/3/3 |
| W4_C3 | omit 2024q3 | 10/3/3 |

Only cell FE condition the diagnostic slopes. There are **0 outcome fits**;
no M0–M3, E1–E4 or historical outcome regressions run. Balance fits are batched
by complete-case target mask and use user-clustered SE by default.

## Samples and transformations

Cells are built once within wave on the same eligible pre-outcome population.
Three linear portfolio design columns and six standardized squares/products
use positive five-wave eligible records as a fixed scaling reference. W4 only
deletes q3; it neither reranks nor rescales. Zero design values remain zero
while raw history remains not applicable.

BASE uses base eligibility, cell-input eligibility, finite gain/linear portfolio
targets and nonmissing IDs/waves. The 11 outcome samples additionally require
finite Y, without using its magnitude. Optional survey controls and other FE
are NOT required for membership. N may exceed v13; this is intentional.
Survey missingness is target-specific and reported. Stock has four/three actual
waves because q2 has no question; other outcomes can have five/four.
Missing/nonfinite candidate designs are skipped explicitly without shrinking
the common sample. Integrity/configuration blockers skip all diagnostics.

## Report collection

| Cell | Tables |
|---|---|
| 9 | Settings, source integrity/messages, affected design issues |
| 10 | Common selection/composition; fixed polynomial scaling |
| 11 | All/positive density for BASE and 11 Y samples, six designs |
| 12 | Cell-demeaned gain SD, raw SD, retained SS share, residual df, notes |
| 13 | Balance coverage, effect/CI maxima, skipped status, interpretation |
| 14 | Target effects, CI, raw p and supplementary Holm p |
| 15 | Timings and fit counts (outcome regression must be 0) |
| 16 | Optional preparation appendix; legacy complete-case reference labeled |

Collect all panels of Cells 9–15, including row numbers in Cell 14. Report
rendering is excluded from compute timing; component time is nested in stages.
Cell 16 legacy complete-case tables do not define current diagnostic samples.

## Balance interpretation and compact selection

Targets: three linear portfolio features, six polynomial terms, four basic
survey traits and employee midpoint. Portfolio provenance is pre-window;
survey timing is unverified. No target enters as a control. Constant/absorbed
targets, too-small samples and no residual shock variation are non-tests.

Standardized effect = trait slope on gain x raw SD(gain) / raw SD(trait), on the
diagnostic sample. It is not a partial correlation or a residual-SD effect.
Intervals are pointwise 95%. Six decimals are displayed; zero p-values may
still be rounded. No automatic pass or design selection from p-values.

Families separate design, all/positive scope, portfolio/survey provenance and
BASE/outcome samples (48 families). Holm is supplementary within each family,
not across model search. Family maxima/counts use all tested rows.

Compact shows each tested target's largest absolute effect and, if different,
widest CI across outcome samples; BASE is separate. No tested target is hidden
for nonsignificance. Compact detail is selected, not every pair or every flag.
Skipped counts appear in Cell 13. Full mode shows every target/outcome row.
Do not recalculate Holm from selected/rounded rows. Evaluate effect sizes,
uncertainty, density and conditional variation before choosing cells or waves.
