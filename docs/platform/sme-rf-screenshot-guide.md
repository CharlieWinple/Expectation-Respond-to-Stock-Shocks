# SME RF v11: Run Modes and Classified Report

Use `scripts/analysis/01_sme_expectations_rf.py`, revision
`sme_rf_v11_classified_report_cells`. Copy **Cells 1 through 14** into the
platform notebook, in order. Restart from Cell 1 for each complete submission;
Cell 1 resets the output buffers and caches. Online cells use simulation only;
submit the complete successful workflow for administrator real-data execution.

## Next run

Keep `RUN_ID="r6_passive_gain_w5_keepzero"`, 10/5/5 bins and the current FE.
Use `RUN_MODE="full_diagnostics"` and `OUTPUT_MODE="compact"` (the defaults).
This first run checks v9 baseline parity and the new continuous-control extension.
Check N, beta, SE, p and Holm p against the archived v9 results. Local synthetic
parity has passed; actual platform timing and numerical parity are not yet known.

## Two independent settings

- `RUN_MODE="main_results"`: all 11 baseline outcomes, positive-only comparison,
  continuous-control extensions in both samples, common-sample baseline reruns
  when needed, sample/zero audits and cheap cell counts. No nested baseline
  specification fits, conditional-X diagnostic or balance regressions. These
  are explicitly labeled NOT_RUN. This is not a complete identification audit.
- `RUN_MODE="full_diagnostics"`: the above plus three baseline specifications,
  conditional-X diagnostics and all 55 individual baseline-sample balance tests.
  Balance remains trait + FE (not a new joint or positive-only balance test).
- `OUTPUT_MODE="compact"`: classified report only, with brief stage
  progress before it. `OUTPUT_MODE="full"` adds preparation audit tables as an
  appendix in Cell 14; it does not select the computation mode.

## Report cells

Capture the consecutive output between `REPORT BEGIN` and
`REPORT END`. Every table has a stable numbered short title;
long values wrap and wide tables split into panels repeating the first column.
Blocks contain at most 11 data rows, target width 84 characters. PDF pagination
is controlled by the platform; this does not guarantee a table occupies one page.

Cells 1–3 define imports, settings and helpers; Cells 4–7 prepare data;
Cell 8 computes the models. Subsequent cells only render stored summaries.
Each report cell covers one topic; tables retain numbered titles and wrap
without truncating values. Run all cells in order, including in compact mode.

| Cell | Contents |
| --- | --- |
| 9 | Settings, integrity, addon policy, computation timing/counts and shock windows |
| 10 | Main baseline estimates/intervals and zero inclusion/positive-only comparison |
| 11 | Specification stability, extension sample audit and continuous-control comparisons in both samples |
| 12 | Zero/history sources, cell density, conditional shock variation and sample construction |
| 13 | Balance summary, flags and all 55 individual tests, grouped by trait |
| 14 | Optional preparation audit appendix and REPORT END |

Each cell groups multiple related tables. Full diagnostic mode reports all
55 balance tests in Cell 13; main mode labels these as NOT_RUN. Compact output
omits the preparation appendix and prints a short status in Cell 14. Grouping
report cells does not add model fits.

`base` means the configured main sample: in R6 it includes zeros; in R7/R9 it
is already positive-only. Identical fits are reused, so base/positive labels in
an already-positive run do not cause duplicate regressions. Extension control
names and units are printed in 01. Columns: stock is index points, env_local
is a direction score, other outcomes are mapped percentage-point values.

## Continuous portfolio controls

Baseline is retained separately. Extension adds log positive portfolio yuan,
100 times historical monthly-return SD, and 100 times historical monthly-return
mean. Zero-holding rows have zero DESIGN entries for these three columns;
underlying history stays not applicable. Existing wave-specific zero cells
separate zeros from positives. Invalid positive inputs are not filled: the
extension drops those rows and compares with a baseline on exactly that sample.
Section 04 reports original and common-sample betas plus sample losses and
zero retention. Full extension and positive-only extension both have estimates,
SE, ordinary CI and Holm p-values.

Holm adjustment is across 11 outcomes separately for each labeled main/positive/
extended specification. It is not a correction for choosing among specifications.
Balance adjusts all tested baseline outcome/trait pairs together. No raw personal
answers or identifiers are printed by the new report.

## Performance and validation

Complete-case samples are cached after preparation is frozen. Regression results
are cached per outcome and exact sample/FE/control combination; only summaries
are retained. Full fitted matrices are released after each fit. Conditional X
variation normally comes from the main regression pseudoinverse (FWL), with a
legacy auxiliary-regression fallback if X is aliased. Balance traits sharing an
exact sample reuse one FE projection; missing employee counts get their own
projection. Cluster corrections retain the original full column count; HC1
retains the original full rank.

When extension inputs are complete and R6 has zeros, main mode typically fits
44 regressions; full mode fits 66 plus up to 22 balance projections, compared
with v9's 165 fits without extensions. Counts can increase for extension sample
loss or aliased-X fallbacks. Fit counts and stage/component seconds are printed;
no platform speedup factor is claimed before real execution.

Local checks: `python tests/test_sme_rf.py`,
`python tests/test_addon_resolution.py`, and `python -m py_compile`.
02 is unchanged and does not implement this extension or v11 reporting.
