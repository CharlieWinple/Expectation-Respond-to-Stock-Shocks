# Project Status

## 2026-10-27 v18 report identified and archived

Sources: `outputs/output-10261200.pdf` (87 pages, printed 66-152) and
`outputs/output-10261200-2.pdf` (29 pages, printed 153-181). Every page footer
checked; complete REPORT BEGIN/END and Cells 9-16. PASS, no design/model skips;
198 regressions, 263 balance projections, 0 variation fallback. Completion
display: 2026-10-26 17:35:08. User calls these the latest results; administrator
real-data vs online-simulation provenance is not explicitly confirmed.

Verified against images: all 66 primary + 132 supplemental estimates, including
printed CI/Holm, 22 primary common-sample rows and 48 dated prior-expectation
checks. Numeric identities, expected row counts and family multiplicity also
checked. [Full record](results/sme_rf_v18_person_business.md) and adjacent JSON.
Local archive: `outputs/platform_runs/sme_rf_person_business/run_001/`, with
116 page images, word-position OCR, page text, metadata and verified aggregates.
Remaining influence/contribution and investor/portfolio-balance detail is
OCR-archived, not certified as a complete numerical dataset.

T0/T1/T2 are control-stable within their common samples: W5 CPI beta
.396781/.391928/.390245; cost -.582763/-.575824/-.584515. W4 T2 attenuates to
.195423/-.348084. Primary 5% outcome-Holm retains only W5 T0 cost (.048657);
T1/T2 cost are .059861/.054259. Do not select T0 by the cutoff. Supplemental
W5 W1-W3 CPI survive Holm, while W3 cost is not raw-significant. These are
different control/sample comparisons, not a unified causal conclusion.

Primary CPI/cost W5 N=7723/8895 versus broader 9016/10328. Missing basic traits,
especially education, drive most attrition. All 48 prior-check raw p>.18, with
only 259-578 observations; no detected association is not proof of exogeneity.
Reusable conclusions and note cache updated; LaTeX and platform scripts unchanged.


## 2026-10-25 v18 approved personal/business control comparison

User explicitly authorized basic age/education/gender controls and an extension
with city tier/firm age/registration/industry. Separately confirmed broad-industry
2024q2 v41 in place of historical v43; both scripts 01 and 02 now use
v41/v42/v28/v29/v29. Revision `sme_rf_v18_person_business_controls`, RUN_ID
`person_business_gain_keepzero`; replace Cells 1-16 in a fresh session.

Primary T0/T1/T2 use one T2-complete sample per outcome and wave set. T0 has
cell FE; T1 adds numeric age/college and gender categories; T2 adds city-tier
and industry categories, numeric firm age and company-registration indicator.
No employee, risk-rating, asset, consumption or mandatory prior-response input.
Sample audit reports initial eligibility, basic coverage, common coverage,
incremental attrition, positive/zero counts and overlapping per-field missingness.
Cells remain fixed. Existing 132 portfolio-model fits retain their broader
samples; 66 primary fits added (198 planned). Holm is separate per wave/model.
All 11 outcomes retained. Identification summaries cover both grids.

Existing v17 investor and v16 prior-expectation diagnostics remain supplementary:
they are not validation of the T0/T1/T2 complete-case samples. Current-wave
trait stability is an assumption, not verified pre-shock measurement. Gender
comes from the existing portrait merge. No platform run or real-data findings.
The v17 addition preceded explicit implementation authorization; this entry
records the subsequently approved main-control scope, not approval of every
earlier diagnostic design choice.

Local validation passed: py_compile of both platform scripts; synthetic T0/T1/T2
sample selection and independent OLS/user-cluster/HC1 parity; missing-column,
blank/nonfinite trait, zero-holder, nullable-category and gain-alias paths;
five-wave industry mapping/read-column checks; complete 198-fit compact/full
report execution; prior-expectation/investor diagnostic regressions and existing
portfolio-model parity. No real-data execution. Existing uncommitted work kept.


## 2026-10-25 v17 investor lottery diagnostics - awaiting platform run

User adopted the paper's aggregate conditional investor-balance interpretation:
jointly assess effect sizes and uncertainty, without requiring every p>0.05.
Revision `sme_rf_v17_investor_balance`; RUN_ID remains
`wave_identification_gain_keepzero`. Replace Cells 1-16 in a fresh session.
Adds up to 290 paired raw/cell diagnostic rows for five strictly dated prior
investor traits across W5/W4 BASE/all outcome samples and BASE wave detail.
Reports missing prior, slopes, standardized CIs, p and within-five-trait Holm.
Cell 13 places investor diagnostics before supplementary portfolio-bin checks.
Current survey traits are not assumed predetermined; repeated prior responses
are required. No additional source tables; no main-model/sample changes.
132 main fits, 180 portfolio checks and 48 prior-expectation checks retained.
No new platform execution or empirical results. See methodology for selection
and timing limitations and the distinction from the paper's Figure 1 slopes.
Local checks passed: py_compile, synthetic investor/prior diagnostic parity,
full regression/report checks (compact/full and blocked/missing-input paths),
and git diff --check. Existing uncommitted v16 work was preserved.


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
No new empirical results: local checks use synthetic data only. Local validation
passed: py_compile; full 132-fit compact/full execution; direct statsmodels
coefficient/cluster-SE parity; 180 cell-check rows including empty-stock-q2
statuses; 48 dated-prior checks; strict date and duplicate-prior exclusion;
FWL SS and contribution identities; gain-alias suppression; nullable-string
formula compatibility; renderer deduplication; addon and legacy diagnostics.



## 2026-10-23 v15 compact results received and verified

Local report `outputs/output-10231150.pdf` covers printed pages 60-71/71,
Cells 9-16 including report end. PASS; 66 fits, 15 tested balance rows,
five projections, zero fallbacks, no model/design issues. All 66 outcome
rows and 11 sample rows transcribed and consistency-checked; all 15 balance
coefficient/CI rows verified. Duplicate wave/p/note lines were collapsed in
the unique-rendered p panels; target-specific zeros are not silently assigned.
See run-log.md and results/sme_rf_v15_wave_controls.md for the full record.

CPI positive slopes are stable across controls; cost slopes are negative but
more wave/control-sensitive. Only W5 M1 CPI passes approximate within-family
5% Holm. Signed balance now supports opposite-wave cancellation, qualifying
the prior favorable pooled W5_C3 assessment. Wave-specific portfolio adjustment
and influence/variation diagnostics are recommendations, not implemented.
Run-specific online versus real-backend provenance remains unconfirmed.
No script or LaTeX edits; reusable conclusions added to findings and note cache.

## 2026-10-22 v15 Cell 8 formula dtype compatibility fix

User supplied a Cell 8 error at estimate_rf: TypeError, cannot interpret
string[python] as a data type. The new select_design_samples path preserves
pandas nullable-string FE labels, whereas legacy sample selectors normalized
them. Normalize active FE columns and user IDs with as_formula_object on a
private model-input frame at estimate_rf's formula boundary. No label, sample,
model, scaling or covariance change; no extra platform fits. Local newer
Patsy did not reproduce the exception, so a strict formula-boundary test
checks object dtype explicitly and compares nullable-string inputs against
object reference estimates for both wave sets, all three models and both
cluster-user/HC1 covariance options. Shared frames and missing semantics
are checked unchanged.

For an existing v15 notebook: replace and execute Cell 3, then rerun Cells
8–16. Cells 4–7 need not rerun if still present. This changes only a helper;
no new data reads are required. For a fresh submission use the full script.
Platform rerun remains pending; screenshot provenance is not confirmed.


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
Local checks passed: py_compile, synthetic 66-fit/15-check execution, direct
OLS/user-cluster covariance parity, common samples and wave/scaling invariance,
blocked/missing-input paths, compact/full rendering, and git diff --check.


## 2026-10-21 Wave-cell design results — initial analysis authorized

Analyzed verified Cells 9–13; visually verified nine targeted Cell 14 rows
(saved as balance_targeted_verified.csv). W5_C3 is the leading candidate,
with W5_C2 as a coarser comparator; neither is declared fully balanced. W4
shows larger portfolio associations even at C3. Retained-variance fractions
rise after q3 deletion but absolute residual SS falls. Pooled wave cancellation
remains possible; signed per-wave balance is the next diagnostic priority.
Recommend fixed C3, both wave sets, M0/M1/M2 estimation alongside that check;
no new code or platform execution. Full evidence/caveats in findings.md.
Missing tail pages 118–121 and actual fit counts remain pending; provenance
unconfirmed. This review does not certify the remaining OCR or report outcome
coefficients. Archive adds nine visually verified balance rows, not new data.


## 2026-10-21 Wave-cell report batch 5 — page 107 gap resolved

Received user-identified original page 107, archived unchanged as
29_batch5_page107.png under external CSMAR
outputs/platform_runs/sme_rf_wave_cell_diagnostics/run_001/. Transcribed
W4_C1 rows 67–78 into a 12-row CSV; row 78's second panel visually matched
original page 108 (PDF page 24). Verified target N+dropped against positive
composition, CI midpoints and rounded normal-p consistency. All 29 source
file hashes verified. W4_C1 panel coverage now complete, but only this
12-row supplement has certified numeric transcription from Cell 14; the
remaining PDF OCR is unverified. Still need full original pages 118–121
for W4_C3 tail, Cell 15 and report end. No substantive analysis.


## 2026-10-21 Wave-cell report batch 4 — PDF archived, coverage incomplete

Received PixPin 34-page image-only PDF; saved byte-identical original as
28_batch4_remaining_report.pdf in external CSMAR
outputs/platform_runs/sme_rf_wave_cell_diagnostics/run_001/. SHA256 verified;
34 embedded page images extracted losslessly, local OCR drafts and page index
saved. OCR has column/character errors and is NOT verified numerical data;
no new certified Cell 14 numeric CSV or substantive interpretation.

Visible original report footers are 84–106 and 108–117; final PDF page is a
cropped continuation without footer. Page 107 is missing. W4_C1 detail rows
67–77 and row 78 panel 1 absent; W4_C3 tail incomplete. Request original
107 and complete 118–121 to recover missing panels and Cell 15/report end.
See batch4_coverage.txt for exact PDF/design spans. W5_C1/C2/C3 and W4_C2
panel coverage is present, not yet a certification of every numeric field.
Archive: 27 screenshots + one PDF; 22 verified result CSVs + page-index CSV.
Source provenance remains unconfirmed; addon-specific Cell 9 table not supplied.


## 2026-10-21 Wave-cell report batch 3 — Cell 13 archived

Received ten Cell 13 images; saved unchanged as originals 18–27 in external
CSMAR outputs/platform_runs/sme_rf_wave_cell_diagnostics/run_001/. Added
balance_families.csv (48 rows), header-only balance_skipped.csv and nine-row
balance_interpretation.csv. Archive totals: 27 hashed images, 22 CSV tables.
Paired horizontal panels by printed row ranges; rejoined wrapped family IDs.
Verified 48 unique families, expected 9/99 portfolio and 5/55 survey counts,
2016 attempted=tested instances, raw/Holm flag-count bounds and CI/effect
maximum ordering. All 27 hashes verified. Detail-based checks await Cell 14;
no Holm recalculation, substantive interpretation or script changes.

Cells 14–15 remain pending; addon-specific Cell 9 table still not supplied.
Run-specific simulation/real-data provenance remains unconfirmed. Empty skipped
table is recorded as displayed, not interpreted as zero target missingness.


## 2026-10-21 Wave-cell report batch 2 — Cell 12 archived

Received six Cell 12 images; archived originals 12–17 and six variation CSVs
in external CSMAR outputs/platform_runs/sme_rf_wave_cell_diagnostics/run_001/.
Archive totals: 17 SHA256-verified images and 19 CSV tables. All six designs
have 24 variation rows (144 total); N matches composition/density, residual
df equals N minus occupied cells, and SD/SS-share identities pass rounding-
interval checks. All printed notes are '-'. No substantive interpretation.

Cross-check found one prior transcription error: W5_C1 env_local/all cell
count was 128 in CSV; original image 06 shows 130. Corrected to 130 and logged
in archive README; original source images unchanged. Cells 13–15 remain
pending, along with the previously noted addon-specific Cell 9 table.
Run-specific simulation/real-data provenance remains unconfirmed.


## 2026-10-21 Wave-cell report batch 1 archived — analysis deferred

User supplied 11 images for Cells 9–11 and requested recognition/storage only.
Archived unchanged images with SHA256 manifest and 13 CSV tables in external
CSMAR outputs/platform_runs/sme_rf_wave_cell_diagnostics/run_001/.
Revision sme_rf_v14_wave_cell_diagnostics; wave_cell_design/compact. Settings
gate PASS, blockers none; design-issues table empty. Received 33 settings,
five shock-calendar rows, preparation message, 12 selection rows, 24 common
composition rows, three scaling rows and six complete density tables (144
all/positive rows). Image hashes, count identities and rounded density-share
reconciliation checked. No substantive interpretation or script edits.

Cells 12–15 remain pending. Cell 9 addon-specific integrity table not supplied;
global gate and shock-calendar gates are present. Actual fit counts not yet
received (settings say no outcome fits). Simulation/real-backend provenance
has not been explicitly confirmed for this run. See archive README for coverage.


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


## 2026-10-21 E1-E4 results reviewed

User authorized interpretation of the complete v13 report. E2 cost is the sole
within-specification Holm-significant outcome (.0431); negative cost slopes
persist across E1-E4 but significance and magnitude depend on specification.
Common samples verified. E2 improves some nonlinear balance at a density cost;
E3 barely changes E1; E4's zero Holm balance flags reflect a much smaller tested
target set after polynomial controls, not proof of exogeneity. See findings.md
and run-log.md for evidence, effect sizes and limitations. No script changes or
new runs. Further checks are recommendations, not implemented specifications.


## 2026-10-21 E design report — batch 2 archived, requested tables complete

Added 17 original report images and 15 CSV tables to external CSMAR
outputs/platform_runs/sme_rf_e_design_checks/run_001/. Total: 24 images with
SHA256 manifest, 27 CSVs. Received E1/E2 full/positive cell densities, E1-E4
conditional variation, 16 balance families, 8 controlled-target status rows,
52 cell-layer and 60 final-layer compact details, stage/component timing and
fit counters (44 main regressions, 0 variation fallbacks, 242 projections).
Cross-page detail panels paired by printed row numbers. Verified diagnostic
sample counts, attempted/tested/skipped identities, all family Holm-flag counts
and maximum effects against detail rows, and final diagnostic missing counts.
Displayed zero p-values are rounded, not exact zero. Compact rows are selected
and do not constitute all tested pairs; no Holm recalculation from rounded rows.
All requested compact report tables are now received. Optional preparation
appendix was not requested. Recognition/storage only; interpretation deferred.


## 2026-10-21 E design report — batch 1 recorded, analysis deferred

Archived 7 original images with hashes and 12 CSV tables in external CSMAR
outputs/platform_runs/sme_rf_e_design_checks/run_001/. Revision
sme_rf_v13_e_design_checks; e_fourwave_gain_keepzero; e_design/compact.
Settings gate PASS and blockers none. All 11 outcomes have control_drop=0
and derived_missing=0. Received E1-E4 estimates and intervals (44 rows total),
common sample composition, and polynomial scaling. Count sums and rounded
confidence intervals checked. Source is user-supplied report images under the
prior backend-report context; provenance not freshly independently confirmed.
Awaiting density, conditional variation, balance diagnostics, fit counts and
timing. User requested recognition/storage only; no result interpretation yet.


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


## 2026-10-19 C/D report received and recorded

Successful C/D run: PASS, 22 fits, all C sample counts preserved, D drops only
reported q3 observations. Main estimates and C diagnostics archived in
CSMAR outputs/platform_runs/sme_rf_cd_gain_only/run_001. Coarse cells improve
sample density; cost/CPI/wage associations are sensitive to omitting 2024q3.
Neither specification has Holm-significant outcomes. D density and conditional
variation are now received; the archive contains 11 images and 15 CSVs. See findings and run log. Earlier pending entries
below are historical.


## 2026-10-19 C/D Gain-Only Plan — Ready for Platform Verification

- 01 revision sme_rf_v12_cd_gain_only replaces the prior run loop with C/D only:
  C five-wave 5/3/3 cells; D omit 2024q3 with original 10/5/5 assignments.
- Both retain zero holders, gain units, FE, continuous controls and user SE.
  All five waves share unchanged v11 data preparation. Normally 22 main fits;
  no historical refits, embedded results, return or balance regressions.
- Cells 1–13; defaults cd_only + compact. Sample composition, actual wave
  coverage, cell density and conditional variation accompany each result group.
- Local syntax and synthetic sample/estimator/report checks passed; no platform
  estimates or timing for this revision yet.


## 2026-10-18 R6 v11 Complete Results — Reviewed

- All requested report output archived; user authorized analysis. Baseline
  sample/estimate/uncertainty fields match v9 at displayed precision for 11 Y.
- Continuous controls cause no sample or zero-holder loss. Input-cost negative
  association remains stable, but no reported outcome passes Holm adjustment.
- Code is operational under reported gates. Recorded aggregation time dominates;
  interpretation remains limited by sparse cells, selection, NAV and common shocks.
- Findings and run log updated; no script changes in this review.


## 2026-10-18 R6 v11 Report Collection — Complete, Analysis Deferred

- Remaining six images for Cells 12–13 received; same archive now holds
  15 SHA256-verified originals and 35 CSV tables, including all 55 balance tests.
- Requested Cells 9–13 complete. User requests saving only; no analysis yet.
  Real-data/simulation provenance remains unconfirmed for this specific run.


## 2026-10-18 R6 v11 Report Collection — Batch 1 Saved

- Nine original report images for Cells 9–11 archived with SHA256 verification;
  20 CSV transcriptions saved in CSMAR
  `outputs/platform_runs/sme_rf_continuous_controls/run_001/`.
- User requests recognition and saving only. Analysis deferred; Cells 12–13
  pending. Real-data/simulation provenance not yet explicit for this run.


## 2026-10-18 01 v11 Classified Report Cells — Ready for Verification

- Report naming replaces screenshot naming throughout 01. Cells 1–8 retain
  data preparation and cached computation; Cells 9–14 group related report tables
  into settings, main/zero results, extensions, diagnostics, balance and appendix.
- Run all Cells 1–14 in order. Next settings remain full_diagnostics + compact.
  Regression definitions and inference are unchanged; no new platform run.


## 2026-10-17 01 v10 Performance, Report and Continuous Controls — Ready for Verification

- Baseline statsmodels formulas/covariance retained; exact samples and duplicate
  fits cached, conditional-X diagnostics reuse fitted projections, and balance
  tests share FE projections within identical samples. Fit counters/timers added.
- `RUN_MODE`: main_results or full_diagnostics (default). `OUTPUT_MODE` controls
  preparation appendices independently. Cell 9 prints consecutive sections 01–06.
- Added separate log-size/history-risk/history-mean continuous extension for
  main and positive-only samples. Zero design exemptions preserve zero holders;
  baseline and extension-common samples are explicitly compared.
- Synthetic coefficient/cluster/HC1 parity, balanced/aliased designs, mode
  execution, zero retention, extension missingness and report tests pass.
  Next: R6 full_diagnostics + compact, all Cells 1–9; compare baseline with v9.
  No v10 real-data estimates or measured platform speedup yet. 02 unchanged.

## 2026-10-17 01 R6 v9 Results — Complete and Reviewed

- Four real-data PDF screenshots archived unchanged, with SHA256 manifest
  and CSV transcriptions in CSMAR
  `outputs/platform_runs/sme_rf_addon_resolution/run_001/`.
- Received CORE 0, active settings, CORE 3 and CORE 4. Revision v9, R6;
  CORE 0 reports PASS with no blockers. Transcription consistency checks pass.
- Follow-up addon-specific CORE 1 received and archived as image 005 with
  six-row transcription; resolved_keys_and_values reports PASS.
- Second batch of eight CORE/AUX screenshots received and transcribed;
  archive now has 13 verified original images and 13 table CSVs. All
  requested tables are received; user confirms screenshot collection complete.
- Initial interpretation recorded in findings.md: no Holm-significant main
  outcome; input-cost negative association persists in positive-only sample.
  Zero inclusion has limited coefficient/precision impact. Remaining priorities
  are positive-only diagnostics, NAV/tail robustness, wave sensitivity and
  inference under common fund shocks. No analysis script changed in this review.

## 2026-10-16 01 Addon Resolution — Awaiting Platform Verification

- 01 revision `sme_rf_audited_v9_addon_resolution` resolves addon duplicates
  question by question; conflicting or unknown answers become question-level
  missing values. Missing IDs do not join; no arbitrary first-row selection.
- The raw-addon global conflict blocker is replaced by a resolved-key/value
  integrity check. All other source integrity gates remain active.
- Diagnostics use platform output helpers and policy/integrity status only;
  addon duplicate counts, resolved key totals and raw unmapped answers are
  not displayed. Existing overall sample and regression tables remain.
- Local syntax and synthetic resolution/merge checks pass. Temporary 03 is
  removed. Run the complete 01 in simulation, then submit for backend approval;
  only administrator real-data PDF results establish samples and estimates.
- 02 is unchanged and does not yet share the new addon-resolution policy.

## 2026-10-16 Agreed 01/02 Configuration — Ready for Platform Verification

- Both scripts now use 10/5/5 within-wave bins and retain portfolio-cell,
  city, gender, industry and employment-group FE plus four controls.
- Both zero sources enter one shared zero cell per wave, with source flags
  retained. Zero gains are 0; return/risk/expected return are not applicable.
  Explicit zero exemptions replace fabricated 12-month history/coverage.
  Observed realized gains and history diagnostics are preserved.
- 01 adds a fixed-positive-cell main-vs-positive-only comparison and exact
  zero-source/history applicability counts. 02 reports history applicability.
- Both scripts pass py_compile and synthetic checks for pooled wave-specific
  zeros, history exemptions and rejection of insufficient positive coverage.
  No new platform estimates or sample counts yet.

## 2026-10-16 Zero-Holding Convention Confirmed — Not Yet Run

- User confirms that a zero holding record or no holding record in the
  relevant snapshot both mean zero fund holdings; invalid recorded amounts
  are not expected under the source convention.
- 01 now selects R6, including both zero sources, with separate source flags
  and wave-specific cells. Positive holdings without usable fund returns
  remain subject to coverage requirements and are not recoded as zero.
- Other configuration is unchanged by this edit. This does not apply the
  proposed 10/5/5 and city/gender-only configuration alignment yet.


## 2026-10-15 Platform Diagnostic Screenshot Batch Complete

- User confirms this batch is complete: 15 original 02 diagnostic screenshots,
  all checked against manifest SHA256 values. Originals and transcriptions are under CSMAR
  `outputs/platform_runs/sme_diagnostics_nav_annotated/run_001/`.
- Observed input gate PASS, annotated NAV version, flags-only policy,
  passive_gain, positive portfolios and user clustering. Actual bins are
  10/5/5; FE include portfolio cell, city and gender only. These differ from
  repository defaults. Exact samples are stock 2,520 / 2,342 users, revenue
  10,155 / 8,158, and price 4,658 / 4,165. Stock has no 2024q2 observations;
  the user confirmed on 2026-10-16 that this outcome was absent in that wave
  by design. Conditional X variation is nonzero and
  no displayed individual balance p-value is below .05.
- Execution date, exact script revision and uploaded table names remain
  unconfirmed. Use the run log and manifest for the received evidence.

## 2026-10-13 Flags-Only NAV Returns — Current User Choice

- User explicitly requested calculable returns in primary columns and no
  default event-screen exclusions. Current inputs are under
  `outputs/fund_nav_annotated/`, version `nav_price_annotated_v1`.
- All original rows retained; primary returns populated for 110,806 shock
  and 1,250,865 control records. Respectively 6,381 and 103,872 carry values
  despite failing the former screen. Missing valid endpoints remain missing;
  money policy unchanged. Calculability is separate from quality approval.
- 01/02 default `APPLY_NAV_QUALITY_SCREEN=False`; True restores stricter
  quality selection. Revision `sme_rf_audited_v8_nav_annotated`. No platform run.
- See `docs/methodology/fund-nav-annotated.md` for thresholds and interpretation.

## 2026-10-14 Compact Upload and Diagnostic Output — No Platform Run

- Generated same-name compact upload panels in `outputs/fund_nav_upload/`:
  shock 15 columns / 10.8 MB, control 13 columns / 95.3 MB. Every row and
  selected value matches the full annotated delivery. The full files remain
  available for fund-event audit.
- 02 now defaults to 01's R7 passive-gain specification and user-clustered
  covariance, applies the post-window and unique-user-wave rules, ranks
  portfolio cells within wave, reads the seven quality flags, and groups key tables in the
  final compact screenshot section. The older standalone validators were
  retired; the dormant old-patch branch was removed from 01. The builder's
  upstream stages and external-audit script remain.
- Python is not currently executable in the local shell. Platform execution
  and syntax checking of the edited script remain outstanding.

## 2026-10-13 Screened Unit-NAV Price Returns Prepared

- User approved temporary unit-NAV returns with automatic event screening.
  New `outputs/fund_nav_screened/` panels use `nav_price_screened_v1`;
  ordinary returns are NAV_end/NAV_base-1 with whole-window daily additive
  or multiplicative NAV-relation screening and daily coverage checks.
  All money-fund rows retain prior values/flags. Old panels are preserved.
- Usable shock: 104,425 / 122,359 (970 fewer than cash v1). Usable control:
  1,146,993 / 1,266,578 (75,352 fewer). Complete 12-month fund-wave windows:
  76,458 versus 93,035 previously. These are local counts, not user samples.
- External-audit regression cases pass: 159915 retains all 12 months of 2024;
  159925's January 2024 merger and 110007/110008's January 2025 dividends
  are excluded. Actual 01/02 aggregation and missing-coverage tests pass.
- Both platform scripts point to the proposed new upload names; revision
  `sme_rf_audited_v7_nav_screened`. No upload/platform run or estimates yet.
  See `docs/methodology/fund-nav-screened.md` for formulas and selection limits.

## 2026-10-13 External Return Audit — v1 Not Ready for Estimation

- Manager reports confirm the denominator correction for additive cumulative
  NAV examples, but refute its universal use: 159915 has a historical split
  factor in cumulative NAV, and 159925 merged shares during 2024 Q1.
- The current v1 masks retain inflated positive returns for 159915 while
  removing its negative returns. Do not upload/use v1 for formal estimation
  pending a fund-level NAV-convention and corporate-action correction.
- Cash-dividend returns for 110007/110008 reproduce event-based cash gains;
  reinvested reconstructions still differ from reported quarterly performance
  by 1.17/1.33 bp, so that reconciliation remains open.
- See `docs/methodology/fund-return-external-validation.md` and the requested
  note-cache entry. This is a local audit, not a platform run. Existing panels
  and platform scripts have not been rebuilt by this audit.

## 2026-10-13 Integrated Total-Return Panels Prepared

- The denominator-only scope assessment affects 7,592 fund codes and 392,381
  control rows; 7,229 codes have changes above one basis point. Complete new
  panels replace the sparse-patch upload workflow.
- `outputs/fund_total_return/` under the CSMAR data root contains
  `shock_panel_total_return_v1.csv` (122,359 rows; 105,395 usable) and
  `ctrl_monthly_total_return_v1.csv` (1,266,578 rows; 1,222,345 usable).
  Original files are preserved. Ordinary NAV returns use cumulative-NAV
  change divided by initial unit NAV, conditional on stable share units;
  money controls retain the accepted old supplement values and posted-month
  convention. Money shocks add 4,449 usable fund-wave observations.
- Additional quality rules remove 2,047 originally usable shocks. These are
  conservative source-review exclusions, not proof of zero or erroneous
  economic returns. Non-CNY operational returns are missing pending FX data.
- 01 revision `sme_rf_audited_v6_total_return` and 02 read the same new tables,
  check the return version, and use gains in 10,000 yuan. Old patch application
  is disabled. Local syntax, algebra, patch-integration and actual aggregation
  checks passed. No platform run or user-level sample comparison has occurred.
- See `docs/methodology/fund-total-return.md` for scope, exact rules, remaining
  share-event/income-unit limitations, and upload instructions. Earlier
  two-file patch statuses below are retained as historical records.

## 2026-10-12 Posted-Month Money Return Rule Prepared

- Rebuilt the two delivery CSVs with full income assigned to the CSMAR
  `TradingDate` month when a disclosure bridges calendar month-end. The
  supplement now has 51,845 usable fund-wave-month returns: 43,974 without
  a true month-end split and 7,871 using the posted-month rule. It retains
  the old even-allocation candidate for comparison and adds bridge-in/out
  counts, normalized income, source-event IDs, and the posted-month return.
- The anomaly file has 23,529 rows: 7,871 usable bridge rows with
  `exclude=0`, 15,652 control exclusions, and six shock exclusions. A further
  140 bridge-affected rows have other money-data problems and remain
  excluded. The active platform script is `sme_rf_audited_v5`, which checks
  that every default-use bridge is backed by a usable supplement. Local key,
  syntax, and Cell 4 checks passed; no platform run has used this revision.

## 2026-10-12 Fund Anomaly Classes Reviewed (superseded delivery)

- The delivered `other_ctrl_shock_anomalies.csv` now has three diagnostic
  classes while retaining its 28,368 keys and `exclude=1` platform behavior.
  There are 12,710 cross-month money-fund disclosure rows (5,263 distinct
  fund-months) whose omitted dates all coincide with weekends or the State
  Council's 2023-2025 holiday schedule, 14,907 inception-period missing
  rows, and 751 other anomalies including the six shock rows.
- Calendar-consistent bundled disclosure does not establish an exact
  natural-month return. The 12,710 estimates stay out of the main analysis;
  seek original manager notices for exact month splits, then test how
  alternative boundary allocations affect actual holdings' 12-month
  expected-return and risk bins. No platform run has used these classes.
- A source audit of fund 000010 revealed that the earlier 4,485-row count
  flagged only the month before a cross-month disclosure. The following
  month also uses the unverified income split. The rebuilt delivery flags
  both months; the earlier 47,360 usable count is superseded by 39,135.

## 2026-10-12 Two-File Fund Quality Delivery Prepared (superseded counts)

- `outputs/fund_quality_delivery/` under the CSMAR data root contains two
  top-level CSV files. The money-market supplement lists 52,667 originally
  zero-return control rows; 39,135 have a reconstructed monthly return that
  does not require cross-month income allocation. The remaining 13,532 are
  flagged unresolved, including 12,710 with a separate cross-month estimate
  that is not applied by default.
- The anomaly file has 28,362 control exclusions (14,830 non-money-fund and
  13,532 unresolved money-fund rows) plus six shock exclusions. The two files
  reconcile exactly with all 67,497 original control patch keys and six shock
  keys. The platform script revision `sme_rf_audited_v4` reads both files in
  Cell 4. No platform run of this revision has occurred.

## 2026-10-12 Money-Fund Control Return Audit

- Cross-checking `fund_static.csv` and the CSMAR manual shows that 52,667 of
  the 67,497 v1 control exclusions are money-market fund rows (926 fund codes).
  Their cumulative NAV and `ReturnAccumulativeNAV` are zero, but the manual
  defines money-market return from realized income per fund share. The zero
  NAV-based rate is not evidence of zero economic return.
- Daily income is present for every one of these fund-month rows: 50,267 use
  `AchieveReturn`, 600 use `MillionAchieveReturn`, and 1,800 use
  `HundredAchieveReturn`. The disclosure count matches the monthly
  `TradingDays` in all 52,667 rows. The field-specific denominators and
  settlement schedules must be checked before constructing replacement
  monthly returns. See the local `outputs/money_fund_diagnostic/` export.
- The v1 patch remains a conservative missing-return mask pending this
  reconstruction. Its 52,667 money-fund control rows are recoverable
  candidates, not confirmed unusable fund months. No platform run has been
  made using a reconstructed money-market series.

## 2026-10-12 Fund Quality Patch Prepared

- A local CSMAR audit found six usable shock fund-wave rows with a baseline NAV
  more than 30 days old and 67,497 control fund-wave-month rows whose reported
  monthly return lacks a positive previous or current cumulative NAV.
- `fund_quality_exclusions_v1.csv` combines these exclusions. The analysis
  script revision `sme_rf_audited_v3` reads the uploaded patch in Cell 4 and
  applies it before user-level aggregation. No platform run using this patch
  has been completed; platform sample sizes and estimates remain unconfirmed.
  The patch workflow is retired; its data schema remains in
  `data/panels/panel-schemas.md` and its results in the run log.

## 2026-10-12 Recorded-Zero Sensitivity Added

- Added R10 (`passive_gain`, five waves, positive plus recorded-zero holdings)
  to separate verified zero fund balances from unmatched holding records.
  R7 remains the candidate investor-only benchmark, and R6 is the historical
  full keep-zero sensitivity. All three require fresh platform runs under
  audited revision `sme_rf_audited_v2` before comparing estimates.

## 2026-10-12 Audited R7 Script Awaiting Platform Run

- `01_sme_expectations_rf.py` revision `sme_rf_audited_v1` now defaults to R7.
  It checks shock-window and holding-snapshot dates, excludes pre-window and
  duplicate user-wave survey records, blocks estimates on source conflicts,
  uses a common sample across model columns and user-clustered uncertainty,
  and reports Holm-adjusted p-values.
- Compact `CORE` and `AUX` tables are designed for platform screenshots. Local
  syntax and synthetic checks passed. No audited platform estimates exist yet;
  older R6 screenshots remain provisional and should not be pooled with the
  new script's output. See `docs/platform/sme-rf-screenshot-guide.md`.

## 2026-10-12 R6–R9 Run Plan Corrected

- The user confirmed the 2026-09-21 R6 screenshots are the five-wave
  `passive_gain` keep-zero main run. Cell audit shows corrected within-wave
  ranks and separate recorded/imputed zero cells. The settings header is
  cropped and the result-table layout differs from the repository script, so
  the precise notebook code version remains unconfirmed.
- The intended sequence is R6 five-wave gain/keep-zero, R7 five-wave
  gain/positive-only, R8 four-wave gain/keep-zero excluding 2024q3, and R9
  five-wave return/positive-only. Cell 2 now selects these settings from
  `RUN_ID`; screenshot folders and their README match this sequence.
- Next: verify R7–R9 platform outputs and compare R7 with R6 to assess the
  influence of the 11,427 imputed-zero R6 observations. See the run log for
  provisional R6 estimates and caveats. The decision gates and reporting roles
  are in `docs/project/identification-plan.md`.

## 2026-09-10 Post-Diagnostic Regression Candidate

- Recorded the 2026.09.10 compact 02 diagnostic conclusions in
  `docs/notes/Notes_Yanpeng.tex`.
- Added lightweight balance diagnostics to `01_sme_expectations_rf.py` so the
  main platform run now reports outcome-specific cell density, within-cell shock
  variation, residual shock variation after FE/controls, and lottery balance
  checks that regress the shock on predetermined traits plus fixed effects.
- 01 now defaults to the post-diagnostic candidate specification: positive
  portfolios, usable passive return, 5/3/3 portfolio cells, full return and
  historical-control completeness, city/gender/industry/employment-size FE,
  and four basic controls.
- Employee-size interval answers are now mapped instead of being coerced
  directly to numeric. The main specification uses grouped employment-size FE;
  numeric midpoint employee count is retained for diagnostics and robustness.

## 2026-09-09 Diagnostic Output Trim

- 02 now defaults to compact output. It keeps the main preparation funnel,
  portfolio-cell summary, outcome sample counts, key-Y distributions,
  configured-variable checks, employee attrition, and selected conditional
  balance tables while hiding bulk by-wave and optional-variable tables unless
  `DIAG_OUTPUT_MODE="full"`.
- Platform rules now explicitly avoid `raise`; diagnostics report missing
  configured FE/control variables through platform output instead of stopping
  with an exception.

## 2026-09-08 Screenshot Review

- Latest supplied run still filters on employee count, unlike the suggested
  four-control baseline. Active settings/commit were not supplied.
- 02 now defaults to the intended positive-portfolio four-control baseline
  and additionally audits employee selection and final-sample cell sparsity
  on fixed cells. See the run log for supplied results and their limitations.

## 2026-09-05 Diagnostic Script Update

- Corrected employer industry mapping in 01 to v43/v42/v28/v29/v29 across
  the five waves, as confirmed by the user; v5 was the wrong branch field.
- Added standalone `scripts/diagnostics/02_sme_expectations_diagnostics.py`.
  Defaults match the user's second screenshot configuration. It audits fields,
  holding provenance, exact regression samples, distributions and conditional
  balance. Usage: `docs/platform/sme-diagnostics.md`.
- Local syntax and synthetic mapping/sample-parity checks passed. Awaiting
  platform execution of the new diagnostic script; no new estimates asserted.
- The older migration status below is historical and predates completed runs
  recorded in the run log.

Last migrated: 2026-09-01.

## Active State

The project is ready for the first v2 platform run. The latest usable script
from the old project has been migrated to:

```text
scripts/analysis/01_sme_expectations_rf.py
```

The old project's v8 status was "generated / waiting for platform run". That
remains the current status here.

## Immediate To Do

1. Fill `SHOCK_TABLE` in Cell 2 with the platform table name for the fund-level
   shock panel.
2. Fill `PORT_CONTROL_TABLE` in Cell 2 with the platform table name for the
   fund-level 12-month control panel.
3. Run Cells 1-6 in order on the Ant platform.
4. Record Cell 4/5/5b/6 outputs in `docs/project/run-log.md`.
5. Interpret coefficients and update `docs/project/findings.md`.

## Waiting For Confirmation

- Exact platform table names for `SHOCK_TABLE` and `PORT_CONTROL_TABLE`.
- Whether `extro_info` consistently contains `answerSeconds=` across all five
  SME survey waves.
- Whether the current holding month map matches the user-provided shock windows
  in the production panels.

## Known Small Inconsistencies In The Old Project

- The old `TODO.md` referred to `05_panel_and_reg_v4.py`, while the actual latest
  script is `06_panel_and_reg_v4.py`.
- The old root directory is not a git repository.
- Old documentation sometimes says 2024q2 addon should not be used for employer
  macro outcomes; the latest v8 design deliberately uses the addon for
  2024q2 `exp_gdp`, `exp_house`, `exp_cpi`, and `exp_rate`, while still leaving
  2024q2 `exp_stock` missing.
