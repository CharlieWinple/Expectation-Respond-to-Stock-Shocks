# SME diagnostics (02)

Run `scripts/diagnostics/02_sme_expectations_diagnostics.py` as a standalone
Ant notebook, copying cells 1-10 in order. It does not require running 01 and
does not fit outcome regressions. All source tables are read on the platform.

Cell 2 defaults match the user's second screenshot run: all five waves,
passive return, usable scope, keep-zero enabled, 10/5/5 bins, portfolio-cell,
city and gender FE, and the four basic controls. Industry and employee count
are audited even when excluded from the regression. Set Cell 2 to the exact
regression configuration of interest before running.

Cells 1-7 deliberately mirror 01's preparation for copy/paste deployment;
keep their preparation functions synchronized when changing either script.
Only the three settings above (keep-zero, scope, FE list) differ by default.
Current historical-completeness and zero-imputation behavior is preserved,
not silently corrected. The inherited sequential funnel is not an exact
regression sample count. Cell 9 reconstructs `run_rf` complete cases, including
numeric conversion and finite-value checks, for each outcome.

- Cell 8: corrected employer industry fields, employee conversion failures,
  and holding provenance before zero filling.
- Cell 9: exact samples, unique users, duplicate user-wave observations,
  incomplete history, distributions, optional-variable availability, and
  cell-level identifying variation for all outcomes.
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
