# Audited SME Regression: Platform Run and Screenshots

Use `scripts/analysis/01_sme_expectations_rf.py`, revision
`sme_rf_audited_v1`. Copy the marked cells into the Ant notebook in order.
Cell 2 defaults to `r7_passive_gain_w5_positive`, the candidate primary run.
For R6, R8, or R9, change only `RUN_ID` first. Do not combine these outputs
with the older R6 screenshots: the timing, sample, uncertainty, and output
rules changed.

## Screenshot Priority

All table headings begin with `RUN_ID`, so retain the heading in each image.
One run should have the following screenshots, in this order:

| Priority | Table | What it establishes |
| --- | --- | --- |
| 1 | `CORE 0 Run Integrity Gate` | Code revision, run ID, timing, SE, PASS/BLOCK. No estimate is valid when BLOCK. |
| 2 | `CORE 4 Main Effects - One Row per Outcome` | All 11 main estimates, confidence intervals and Holm p-values. |
| 3 | `CORE 3 Outcome Regression Sample Size` | Exact complete-case N and unique users by outcome. |
| 4 | `CORE 5 Specification Stability - Same Outcome Sample` | Coefficient stability with common N. |
| 5 | `CORE 2 Survey Timing and Duplicate Audit` | Submission timing and duplicate survey rows. |
| 6 | `CORE 2 Holding Match and Zero Portfolio Provenance` | Observed vs imputed zero holdings. Essential for R6/R8. |
| 7 | `CORE 1 Shock Window Calendar`, `CORE 1 Holding Date Parse Audit`, and `CORE 1 Holding Snapshot Date Audit` | Exposure and holding chronology. |

If a core table is wider than one image, capture it in overlapping segments
with the first column and title visible in each segment. The detailed input
and coefficient tables are hidden by default. `OUTPUT_MODE="full"` restores
them for a targeted audit.

## Auxiliary Screenshots

Capture `AUX 1 Cell Density and Within-Cell Shock Variation`, `AUX 2
Conditional Shock Variation After FE and Controls`, `AUX 3 Balance Test
Summary`, and `AUX 4 Balance Flags (Holm p<0.05)` for R7. For R6/R8, also
capture `AUX 0 Sample Size Sequential Funnel`. The balance flag table shows
only adjusted flags; an empty flag table does not prove random assignment.

Record run date, code commit, table names, `RUN_ID`, and whether all cells
finished in `docs/project/run-log.md`. Transfer only checked conclusions to
`docs/project/findings.md` after reviewing the platform output. The script
does not write full platform extracts.
