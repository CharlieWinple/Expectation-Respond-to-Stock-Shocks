# Stock Return, Expectations, and Outcomes

## 2026-10-29 v19 wave results received

`output-10291330.pdf`:40 pages, PASS;154 fits,108 estimable wave slopes and22
equality tests saved. All22 anchors match core/tail.
[Full record](docs/project/results/sme_rf_v19_wave.md).
All three batches received and archived; platform scripts unchanged.

## 2026-10-29 v19 tail results received

`output-10291050.pdf`:34 pages, PASS;154 outcome fits and132 deletion coverage
rows saved. All22 C/E anchors match core. [Full record](docs/project/results/sme_rf_v19_tail.md).
Core and tail received; wave remains pending. Platform scripts unchanged.

## 2026-10-29 v19 core results received

`output-10281700.pdf`: 32 pages, printed 67–98, PASS; all 99 outcome regressions,
11 sample rows and 22 own-prior checks saved and numerically checked.
[Run record and full tables](docs/project/results/sme_rf_v19_core.md).
Core complete; tail/wave outputs still pending. Scripts unchanged in this archive update.

## 2026-10-28 v19 common-sample identification audit — awaiting platform runs

Revision `sme_rf_v19_common_sample_audit`. Replace **Cells 1–16** of
`scripts/analysis/01_sme_expectations_rf.py` in a fresh platform session.
No new input tables. All batches retain all eleven outcomes and fixed 10/3/3 cells.
Set `RUN_BATCH` in Cell 2; default is `"core"`. Submit each batch as its own complete
workflow (not an extra cell against a previous backend run).

| Batch | Purpose | Maximum outcome fits |
| --- | --- | ---: |
| `core` | A–E common-sample comparison, positive-holder comparison, own-prior placebo and matched current outcome, investor balance | 99 |
| `tail` | C/E anchors; 0.5%/1% capital and residual-exposure deletion; two separate top-user deletions | 154 |
| `wave` | C/E anchors; omit each wave; interaction slopes and equality Wald tests | 154 |

Core additionally has 110 investor-trait checks and 22 own-prior checks, using
batched projections where masks match. Counts are upper bounds, not measured
runtime promises; unavailable samples are explicitly skipped. Reports suppress
legacy grids and repeated group decompositions, not selected outcome estimates.
Run in order core → tail → wave. Titles: `v19-core 全预期共同样本与事前平衡`;
`v19-tail 全预期尾部与逐用户删除`; `v19-wave 全预期波次稳健性`.
See [method and exact scopes](docs/methodology/identification.md).
No new empirical findings; local validation uses synthetic data only.


## 2026-10-27 v18 platform report received and saved

Two supplied PDFs cover printed pp.66-181 continuously, including the complete
Cells 9-16 report. PASS; 198 regressions. Verified and saved all 66 primary and
132 supplemental estimates, 22 primary sample rows and 48 preperiod checks.
See [results and verification scope](docs/project/results/sme_rf_v18_person_business.md)
and [structured data](docs/project/results/sme_rf_v18_person_business.json).
Full-page OCR/images are retained locally; remaining diagnostic detail is not
yet a fully verified numerical database. Report-specific backend/simulation
provenance remains unconfirmed. No analysis script changes in this review.

## 2026-10-25 v18 personal/business controls - awaiting platform run

Current revision: `sme_rf_v18_person_business_controls`; RUN_ID
`person_business_gain_keepzero`. Replace Cells 1-16 in a fresh session.
Primary T0/T1/T2 compare cell only, plus age/college/gender, and additionally
city tier/firm age/company registration/broad industry. All three use the same
T2-complete sample within each outcome and W5/W4. All 11 outcomes remain active:
66 primary fits plus the 132 existing supplemental portfolio-control fits.
Cell 10 reports control-related attrition, Cell 11 leads with the primary
results, and Cell 12 includes their identifying-variation diagnostics.
No mandatory previous-wave responses, employee control or new asset tables.
User confirmed 2024q2 broad industry v41 (replaces v43 in scripts 01 and 02).
The older entries below describe earlier revisions, not the current model grid.
No new platform estimates are available.

## 2026-10-25 v17 investor balance diagnostics - awaiting platform run

Current revision: `sme_rf_v17_investor_balance`, same RUN_ID and input tables.
Replace Cells 1-16 in a fresh session. Main v16 regressions remain unchanged.
Cell 13 now leads with raw versus cell-adjusted associations between current
passive gain and five dated previous-wave investor traits, with missingness,
signed effects, CIs and supplemental p/Holm. These are aggregate conditional
checks, not per-cell tests or an all-p>0.05 pass requirement. No new estimates
are available until platform execution. See status and identification docs.

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


## 2026-10-23 v15 compact report received and analyzed

Verified 66 outcome fits and 15 signed balance checks from the supplied report.
CPI slopes are positive and control-stable; cost slopes are negative with more
wave/control sensitivity. Signed balance supports opposite-wave cancellation,
so favorable pooled W5 balance is not a quasi-randomness certificate.
See [result tables](docs/project/results/sme_rf_v15_wave_controls.md),
[findings](docs/project/findings.md), and [status](docs/project/status.md).
The older awaiting-run entries below are historical. No new script changes
were made; further wave-specific diagnostics remain recommendations.

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


This repository is the git-based continuation of the earlier Claude-built
project in `../`. It keeps the usable research design, data conventions, and
current SME regression script, but replaces the old `YYYYMMDD_vN/` folder
workflow with ordinary git commits.

## Current Research Question

How do stock-market return shocks generated by predetermined mutual-fund
holdings affect:

1. household and SME expectations about the stock market, macro conditions, and
   own prospects;
2. real outcomes such as household consumption and SME business performance.

The active branch of the project is the SME-owner expectations analysis.
Household/job-survey work is planned but not yet active.

## Identification

The project follows Andersen, Johannesen, and Sheridan (2024). For each user,
passive return is constructed by fixing the beginning-of-period mutual-fund
portfolio and applying fund returns over a common window. Conditional on
portfolio characteristics, this passive return is treated as quasi-lottery
variation.

The active v18 run estimates expectations on passive gain with fixed 10/3/3
wave-by-portfolio cells. T0 is cell only; T1 adds age, college and gender;
T2 adds city tier, firm age, company registration and broad industry. They share
T2-complete cases within each outcome/wave set. Both zero sources remain in
pooled wave-specific zero cells. W4 removes 2024q3 without reranking.

Supplemental M0/M1/M2/W1/W2/W3 preserve the portfolio-control comparison and
its broader sample without survey-trait restrictions. Compare T0/T1/T2 to
each other; T0 vs M0 can additionally reflect sample selection. Existing
balance and prior-expectation checks refer to supplemental samples, not proof
of balance in the new primary samples. User clustering does not resolve
dependence arising from shared fund holdings.

## Repository Layout

```text
docs/
  project/                  project status, migration notes, reusable findings
  methodology/              identification, variable definitions, sample rules
  platform/                 Ant platform rules and script workflow
data/
  schema/                   machine-readable platform schema snapshot
  panels/                   local schema/sample copies of user-provided panels
scripts/
  analysis/                 active analysis scripts for platform execution
  diagnostics/              active SME sample and input diagnostics
```

## Active Script

The current active platform script is:

```text
scripts/analysis/01_sme_expectations_rf.py
```

Before running it on the Ant platform, select `RUN_ID` in Cell 2 and verify
these table names:

```python
SHOCK_TABLE = "shock_panel_nav_annotated_v1"
PORT_CONTROL_TABLE = "ctrl_monthly_nav_annotated_v1"
APPLY_NAV_QUALITY_SCREEN = False
```

Upload the two compact CSVs from the CSMAR
`outputs/fund_nav_upload/` directory, confirming actual uploaded table names
against the platform sidebar. Ordinary funds use unit-NAV price returns with
daily suspected-event flags; flags do not exclude calculable ordinary returns
by default. Money-fund rows retain the prior policy. The wider files in
`outputs/fund_nav_annotated/` are retained locally for audit; both upload files
have the same row keys and the same names expected by 01 and 02.
Do not apply the old patches again. Previous cash-total-return v1 failed
external validation and is superseded. Both platform scripts expect
`return_version=nav_price_annotated_v1`. See
`docs/methodology/fund-nav-annotated.md` for definitions, quality rules,
counts, limitations, and reproducibility. Then paste
cells 1 through 16 into the platform notebook in order. See
`outputs/platform_screenshots/README.txt` for the R6–R9 settings and screenshot
folders.

## Sample Diagnostics

Run `scripts/diagnostics/02_sme_expectations_diagnostics.py` independently on
the platform. See `docs/platform/sme-diagnostics.md` for settings, outputs,
and the optional conditional-balance checks. Its current defaults use the
post-diagnostic candidate specification, with positive portfolios, usable scope,
coarser cells, city/gender/industry/employment-size FE, and four basic controls.

## Git Workflow

Use git commits instead of dated version folders:

```text
main
  stable documented state

feature/<short-topic>
  one analysis change, diagnostic, or robustness exercise
```

Recommended commit rhythm:

```text
1. edit scripts or docs
2. run local syntax checks where possible
3. commit before platform execution
4. paste platform outputs into docs/project/run-log.md or a dedicated result note
5. commit the result interpretation
```

Platform mid-table names should still carry explicit versions because the
platform does not support overwriting mid-tables.

## Current Next Step

The v18 Cells 9-16 report has been received and archived. Review the verified
personal/business-control results and their sample attrition before choosing
any further analysis. Remaining balance, influence and group-contribution
detail has page OCR but requires numeric verification before precise citation.
No additional platform run or model change has been selected.
