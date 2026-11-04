# SME-owner formal regressions and contemporaneous balance

Revision: `sme_owner_formal_v1` (2026-10-31).
Script: `scripts/analysis/04_sme_owner_formal.py`.
Run title: `小微经营者 三规格回归、同期平衡与gain/holding直方图`.

Run all Cells 1–13 in a fresh platform workflow. Existing input tables are
unchanged; no new upload or intermediate write is required. Computation remains
in Cells 1–9. Four fixed final cells report: (10) samples and all regressions,
(11) distributions, (12) complete BASE balance, (13) outcome balance summaries,
employee-count supplement and essential integrity checks. Each marked block must
be a separate physical notebook cell. No manual continuation or repeated cell is
required after submission.
The earlier owner v19 and employee scripts remain unchanged.

## Exposure distributions and local figures

Cell 11 prints distribution statistics, eligibility counts and Histogram bins.
The four panels use the positive-holder complete-control BASE. Gain and initial
holdings are in RMB. The other scales are sign(gain)*log10(1+abs(gain)) and
log10(holdings). Each scale has 20 equal-width bins over all finite values,
or one bin for a constant. Bin edges are printed with 17 significant digits.
Bins include the lower edge, and the final bin includes both edges.

After checking the table against the returned report, save its columns
panel,bin,lower,upper,N,share in verified/histogram_bins.csv inside the run
directory. Retain all bins, including empty bins. Check each panel's total N
against finiteN in the eligibility table. From the repository root run
python scripts/local/plot_owner_histograms.py <path-to-verified-CSV>.
This creates two vector PDFs and two 300 dpi PNGs in the run's figures folder.
The November 2 screenshots remain historical evidence. The new printed-table
revision awaits platform execution.

## Population and measures

Only respondents explicitly coded as SME owners enter estimation. Existing
post-window timing, unique owner-wave, duration >=180 seconds (missing retained),
return coverage and NAV flags-only policies are retained. Gain is in RMB 10,000.
The 2024q2 macro supplement and broad industry v41 are retained. Stock expectations
start in q3. Zero recorded holdings and unmatched holdings treated as zero remain
separately counted, sharing a within-wave zero cell as in the existing design.

Owner controls: continuous age and firm age; binary college and company status;
gender, city tier and broad industry category indicators. They are not owner FE.
The unambiguous short college label already documented in employee mapping is
recognized. Other unmapped/mixed education labels remain missing and are reported
by wave; no new interpretation of ambiguous categories is imposed. This can change
sample sizes relative to v19. Existing owner company-status and firm-age mappings
are retained. Gender comes from the existing portrait table; no prior-wave match
is required and it is not claimed to be measured anew at each survey.

## Samples and regressions

For each of all eleven outcomes:

1. Wave-available: owner eligibility and complete gain/return coverage, outcome
   and wave; historical return coverage is not required here.
2. Cell-available: add complete twelve-month history and fixed 10/3/3 portfolio
   cell inputs (zero holdings exempt from history).
3. Owner-available/common: add complete owner controls.

Three main specifications use sample 3: Wave FE; Cell FE; Cell FE + owner controls.
The supplementary estimates use samples 1/2/3 respectively. Identical fits are
reused. Do not intersect all eleven outcome response samples. Cell ranks are fixed
before outcome and owner-control selection. Counts include singleton-cell rows;
these do not supply within-cell gain variation. Sample tables report N, unique
owners, history/control attrition, outcome-by-wave counts and control missingness
(nonadditive). There are 66 regression output rows, at most 55 distinct fits.

## Descriptive tables

BASE is sample 3 without requiring any specific outcome. Numeric tables report
N, missing N, mean, SD, P1/P10/P50/P90/P99. Gain and portfolio characteristics are
reported for all BASE and positive BASE; gain is also broken out by wave and
outcome common sample. Raw holdings amount remains missing for unmatched users,
while their gain is coded zero. Historical mean/risk are missing for zero holdings.
Each outcome has its own distribution on its common sample. Categorical owner
controls and the environment outcome have frequency/share tables. No trimming or
winsorization is applied for display or estimation.

## Balance

Current recorded characteristics, not previous-wave traits. BASE includes all eligible holdings, including recorded and imputed zeros.
Each outcome uses its main regression common sample. Targets are age, college, firm age,
company status, each gender/city/industry category indicator; employee count is
reported separately as a contemporaneous association (and excluded from the
balance overview counts). Unknown employee size is not imputed.

Each target is regressed on gain with: intercept only; wave FE; cell FE. These
three fits use identical observations. No owner control enters these tests.
BASE and employee tables report the original coefficient, owner-clustered SE and
unadjusted p per RMB 10,000 higher gain. Age is in years, employee count in
persons, and indicator coefficients times 100 give percentage points. Outcome
summaries give test counts and sample ranges. The archived 11032030 report used
standardized estimates; the new reporting format awaits platform execution.
Current recording does not establish pre-shock stability for every trait; these
checks diagnose observable selection, not certify a causal lottery.

## Memory and inference

Fund-history expansion is processed within each wave in batches of 5,000 owners,
limited to surveyed owners. Raw source tables are released after aggregation.
Estimation retains a slim owner-wave frame, one outcome/sample at a time. Single
wave/cell FE is absorbed by demeaning, avoiding a dense cell dummy matrix. Only
owner controls enter a small SVD; no fitted model or N-by-N projection is retained.
Only aggregate results are buffered for final output. Four output cells contain
aligned tables with repeated titles and headers every 12 data rows, short
outcome/trait keys and four significant digits. Confidence
intervals are not repeated: use beta +/- 1.96 SE. Before any output all blocks are
checked against 36,000 UTF-8 payload bytes. Each reporting cell automatically
prints batches of at most 40 result lines plus one chunk header per call. The
cumulative cell budget is 44,000 bytes, including headers and a 512-byte reserve
per call, below the 50KB platform limit. This also avoids the observed 100-item
per-call truncation; batching does not require additional cells or manual reruns.
An unexpected over-limit block produces a short explicit preflight failure,
never truncation, false success or instructions to manually resume backend output.
Actual platform memory and
runtime remain to be measured; initial table reads still depend on source size.

User-cluster CR1 with full design rank degrees-of-freedom correction, normal
p-values and 95% CIs. Minimum regression N=30 and at least two users. Explicit
checks cover gain collinearity, residual variation, residual df and unexpected
category counts. Shared-fund error dependence is not addressed by user clustering.

## Local validation and evidence boundary

`python -m py_compile scripts/analysis/04_sme_owner_formal.py`
`python tests/test_sme_owner_formal.py`

Synthetic independent dense-OLS checks cover coefficients and CR1 SE/p values,
redundant category controls, absorbed/collinear gain, common-sample accounting,
current-trait three-column consistency and no output before the final cell.
A mocked complete source-to-report workflow checks all thirteen cells and chunked
versus whole-wave portfolio aggregation. These checks do not establish real-data
sample sizes, estimates, runtime or peak memory. The first PDF report was partial;
complete platform output with the batching fix remains pending.

## 2026-11-01 fixed compact report (supersedes paginated draft)

The 30-cell/manual-continuation draft is withdrawn. Cells 1–9 and the statistical
estimands remain unchanged. The compact report preserves all 66 formal regression
rows, sample accounting, distributions and full BASE balance. It replaces eleven
repeated full outcome-balance tables with descriptive summaries, removes redundant
CI columns and omits duplicate preparation descriptions. Essential calendar,
snapshot, duplicate/timing and fixed-cell audits remain.

Local full-workflow tests execute all 13 cells once. The output-size stress test
covers 80 levels for each categorical trait across all 12 balance scopes, verifies
four output blocks below 36KB, and checks explicit preflight failure for unexpected
oversized labels. Actual platform rendering overhead remains outside local mocks.
In a live session retaining completed aggregates, replace the old reporting tail
with Cells 10–13; otherwise submit the complete updated 13-cell script.

## 2026-11-02 automatic batches within the four report cells

Latest presentation revision: `2026-11-02 aligned tables`. Pipe-delimited rows
are replaced by aligned columns and repeated table headings, following script 01.
Expanded output is distributed by estimated byte size across the same four final
cells, preserving report order. A physical cell no longer corresponds to exactly
one subject area. Per-call batching and cumulative byte guards remain. Full local
tests, including the high-category-count stress case, pass; platform rendering
must still be verified. All 66 regression rows remain in the report.

The first PDF stopped blocks 1 and 4 at exactly 100 items despite their byte
budgets. Output revision `2026-11-02 batched40` splits each block into calls of
40 result lines plus a numbered chunk header, retaining the 13-cell workflow.
All blocks are preflighted before printing. Local tests simulate a 100-item
per-call cap and verify exact preservation of every report line, including all
66 regression rows and the final completion marker. Stress tests retain the
36KB payload and 44KB cumulative reserved cell budgets. Rendering overhead is
estimated; the next platform report must confirm complete output.
