# SME-owner formal regressions and contemporaneous balance

Revision: `sme_owner_formal_v1` (2026-10-31).
Script: `scripts/analysis/04_sme_owner_formal.py`.
Run title: `小微经营者 正式三规格回归与同期特征平衡`.

Run all Cells 1–10 in a fresh platform workflow. Existing input tables are
unchanged; no new upload or intermediate write is required. All tables appear
in Cell 10, bounded by REPORT BEGIN/END. Do not append cells to an old session.
The earlier owner v19 and employee scripts remain unchanged.

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

Current recorded characteristics, not previous-wave traits. Positive holders
only, in BASE and each outcome's common sample. Targets are age, college, firm age,
company status, each gender/city/industry category indicator; employee count is
reported separately as a contemporaneous association (and excluded from the
balance overview counts). Unknown employee size is not imputed.

Each target is regressed on gain with: intercept only; wave FE; cell FE. These
three fits use identical observations. No owner control enters these tests.
Standardized coefficients and CIs use SD(gain)/SD(target) from that test sample,
fixed across the three adjustments; scales may differ across outcomes. This is
not a partial correlation. All category indicators are shown, including dependent
complementary tests. Constant/absorbed targets and insufficient samples are marked,
not called balanced. The overview reports counts, max absolute standardized
association and sample ranges; the appendix retains every target and adjustment,
not only significant tests. BASE also reports raw coefficients/SEs. No Holm output.
Current recording does not establish pre-shock stability for every trait; these
checks diagnose observable selection, not certify a causal lottery.

## Memory and inference

Fund-history expansion is processed within each wave in batches of 5,000 owners,
limited to surveyed owners. Raw source tables are released after aggregation.
Estimation retains a slim owner-wave frame, one outcome/sample at a time. Single
wave/cell FE is absorbed by demeaning, avoiding a dense cell dummy matrix. Only
owner controls enter a small SVD; no fitted model or N-by-N projection is retained.
Only aggregate results are buffered for final output. Actual platform memory and
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
A mocked complete source-to-report workflow checks all ten cells and chunked
versus whole-wave portfolio aggregation. These checks do not establish real-data
sample sizes, estimates, runtime or peak memory. Backend PDF results are pending.
