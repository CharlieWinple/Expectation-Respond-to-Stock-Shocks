# SME diagnostics (02)

Run `scripts/diagnostics/02_sme_expectations_diagnostics.py` as a standalone
Ant notebook, copying cells 1-10 in order. It does not require running 01 and
does not fit outcome regressions. All source tables are read on the platform.

Cell 2 defaults (updated 2026-09-08) use the intended baseline: all five waves,
passive return, usable scope, keep-zero disabled, 10/5/5 bins, portfolio-cell,
city and gender FE, and the four basic controls. Industry and employee count
are audited even when excluded from the regression. Set Cell 2 to the exact
regression configuration of interest before running.
`DIAG_OUTPUT_MODE="compact"` is the default so the platform output stays
readable. Switch it to `"full"` only when drilling into a specific sample-loss
or mapping issue. In compact mode, detailed distribution tables are limited to
`DIAG_KEY_Y` and inherited preparation output is filtered to the main funnel,
portfolio-cell summary, and outcome sample table.

Cells 1-7 deliberately mirror 01's preparation for copy/paste deployment;
keep their preparation functions synchronized when changing either script.
Scope and FE list differ from 01 by default.
Current historical-completeness and zero-imputation behavior is preserved,
not silently corrected. The inherited sequential funnel is not an exact
regression sample count. Cell 9 reconstructs `run_rf` complete cases, including
numeric conversion and finite-value checks, for each outcome.

- Cell 8: corrected employer industry fields, employee conversion failures,
  configured-variable checks, and holding provenance before zero filling.
  Missing configured FE/control variables are reported rather than raised,
  because the platform does not allow `raise`.
- Cell 9: exact samples, unique users, duplicate user-wave observations,
  incomplete history, selected distributions, and cell-level identifying
  variation. Full mode also prints by-wave exact samples and optional-variable
  availability for all outcomes.
  Additional employee complete-case tables compare counts by outcome/wave
  with and without the employee nonmissing requirement and report cell-size
  quantiles, singleton counts, and observation shares in small or constant-X
  cells. The same partition is used throughout; no extra outcome fits or fund
  aggregation are needed. The configured final sample still governs Cell 10.
  To reproduce the latest screenshot's employee-inclusive sample in Cell 10,
  add aer_bal_employee_n to REG_CONTROL_NAMES in Cell 2. Confirm the actual
  platform settings; the screenshot bundle did not include Active Settings.
- Cell 10: residual shock variation and conditional balance for exp_stock,
  exp_rev and exp_price. Set RUN_CONDITIONAL_DIAGNOSTICS=False in Cell 8 to
  skip these more expensive fits. DIAG_BALANCE_Y and DIAG_BALANCE_VARS limit
  the work. Each balance regression excludes the tested trait from controls;
  missing optional traits produce a smaller, explicitly reported sample.

Record-zero means a recorded aggregate amount of zero, not independently
verified economic nonparticipation. Missing holding records are reported
separately even when the regression fills them as zero. Current tied-rank
splitting is retained so diagnostics describe the actual regression.

Balance is exploratory. Verify timing of firm characteristics before calling
them predetermined; p-values use the configured covariance (HC1 by default).
No joint balance test or clustered inference is implemented here. No platform
results have been generated locally. Record actual platform outputs in the
run log after execution.

Employer industry mapping confirmed by the user: 2024q2 v43, 2024q3 v42,
2024q4 v28, 2025q1 v29, 2025q2 v29. This replaces v5 in both scripts.
