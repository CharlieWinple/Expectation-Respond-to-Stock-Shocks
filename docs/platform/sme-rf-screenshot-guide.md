# SME passive gain: wave choice and nonlinear controls

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


## Collect the report

- Cell 9: settings, integrity, actual counts and skips.
- Cell 10: 11 common-sample rows, positive/zero counts and q3 deletions.
- Cells 11–12: W5/W4 M0–M2 beta, SE and raw p; collect all panels.
- Cell 13: all 15 signed balance checks, CIs and notes.
- Cell 15: timing and fit counts: normally 66 outcome fits, 5 projections,
  zero variation fallbacks. Inspect skips when counts differ.

Cells 14 and 16 are optional full-mode supplements. Use a fresh session and
replace all Cells 1–16; no old diagnostic grid runs alongside this submission.
Record whether the report comes from simulation or backend execution.
