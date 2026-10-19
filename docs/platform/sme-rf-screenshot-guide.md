# SME RF: C/D Passive-Gain Sensitivity Run

Current revision: `sme_rf_v12_cd_gain_only`.
Run `scripts/analysis/01_sme_expectations_rf.py`, all **Cells 1–13** in order.
Defaults: `RUN_ID="cd_passive_gain_keepzero"`, `RUN_MODE="cd_only"`,
`OUTPUT_MODE="compact"`. No additional mode selection is needed.

Online cells use simulation only. Run the complete workflow successfully and
submit for administrator real-data execution. Estimates/sample sizes must come
from the returned platform report. No real-data v12 run has occurred yet.

## Questions and specifications

| Group | Question | Sample and waves | Portfolio cells |
| --- | --- | --- | --- |
| C | Does the association depend on fine conditioning cells? | Include both zero sources, all five configured waves | 5/3/3 |
| D | Does the association depend on 2024q3? | Include both zero sources, omit 2024q3 | Original 10/5/5 |

Both use passive gain per 10,000 yuan, the same city/gender/industry/employment
FE, age/college/firm-age/company controls, and continuous log portfolio size,
historical monthly SD and historical monthly mean controls. User-clustered
SE remain the default. Zero gain is 0; raw zero history stays not applicable,
with zero only in the continuous design columns and separate wave-specific
zero cells. NAV flags-only policy, timing and coverage rules are unchanged.

C and D each estimate all 11 outcomes: normally 22 main fits, no historical
baseline refits, no return regressions, no positive-only regressions, no balance
regressions, no crossed coarse-cell/four-wave specification. References remain
in local archives and are not embedded in platform code or report. Compare
results locally to the completed v11 include-zero continuous-control run.

## Comparability and sample rules

Prepare all five waves together once. On the same pre-outcome eligible cell
population, construct fine 10/5/5 and coarse 5/3/3 within-wave average-rank cells.
Fine assignments remain in `analysis_portfolio_cell`; coarse assignments live
in `coarse_portfolio_cell`. Source reading, survey preparation and user-level
aggregation are unchanged from v11.

For each outcome, retain the v11 complete-case eligibility and add the same
continuous controls. C uses these rows with coarse FE; D removes only the q3
rows from this sample. D never re-ranks or rebuilds cells after omission.
Unexpected missing coarse labels flag the C fit rather than silently deleting
rows. Current-sample selection reports basic N, continuous N, control losses,
C missing-cell count and D q3 losses, without fitting the five-wave fine model.

Actual wave lists/counts are printed per outcome: stock has four observed waves
in C and three in D if its original 2024q2 absence is preserved. This is a period
sensitivity check, not identification of a policy effect. A change in significance
alone does not establish a difference in coefficients.

Holm is applied within C and within D across their estimable outcomes; skipped
fits retain missing inference fields and an explicit note. It does not correct
selection across specifications. Ordinary 95% intervals are not simultaneous.

## Report cells

| Cell | Contents |
| --- | --- |
| 1–3 | Imports, settings, construction/estimation helpers |
| 4–7 | Shared source reading, survey, aggregation and both cell assignments |
| 8 | C and D fits only; current-sample summaries and residual-X diagnostics |
| 9 | Settings, integrity/addon checks, windows/messages and sample selection |
| 10 | C estimates, uncertainty, zero/positive counts and actual wave coverage |
| 11 | D estimates, uncertainty, zero/positive counts and actual wave coverage |
| 12 | Full/positive cell density, conditional gain variation, fit counts/timing |
| 13 | Optional preparation appendix and REPORT END |

Each report cell groups related tables. Tables retain all values, wrapping and
splitting wide panels, with at most 11 rows per block and target width 84.
`OUTPUT_MODE="full"` adds preparation tables in Cell 13; compact prints only a
short omitted-appendix status there. Both settings run the same C/D models.
Positive-density rows are descriptive and require no extra regressions.

Conditional-X diagnostics reuse the fitted projection; an aliased regressor can
trigger an explicitly counted auxiliary fit. Reported stage times exclude report
rendering but may include waiting between manually executed cells. Shared data
preparation is performed only once. No new aggregation speedup is claimed.

## Local verification

- `python tests/test_sme_rf.py`: 22-fit C/D execution, same-sample/coarse and
  fixed-cell/omission rules, zero handling, sample loss, blocked/missing inputs,
  clustered/HC1 parity, FWL diagnostics, per-group Holm and report ordering.
- `python tests/test_sme_diagnostics.py`: sample and zero-history checks.
- `python tests/test_addon_resolution.py`: addon resolution and merge checks.
- `python -m py_compile scripts/analysis/01_sme_expectations_rf.py`

02 is unchanged and is not a companion C/D execution script.
