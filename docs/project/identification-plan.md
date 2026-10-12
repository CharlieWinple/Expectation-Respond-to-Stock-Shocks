# SME Expectations: Next Identification Decisions

Prepared 2026-10-12 after review of the R6 five-wave passive-gain keep-zero
screenshots. This is a decision plan, not a claim that the proposed checks have
already passed. Platform outputs remain the source of truth.

## What R6 Establishes

- The corrected within-wave cell audit is consistent with 5/3/3 bins and
  separate recorded-zero and imputed-zero cells.
- The base contains 26,694 observations, including 882 recorded-zero and
  11,427 unmatched-holding/imputed-zero observations. The latter are 42.8% of
  the base; they are not verified non-investors.
- In the fully controlled specification, CPI expectations rise by 0.46714
  mapped percentage points per 10,000 yuan of passive gain (SE 0.19156,
  p 0.0147), while input-cost expectations fall by 0.45558 points
  (SE 0.20980, p 0.0299). Neither p-value clears 0.05/11 for the 11
  outcomes. The one-standard-deviation shock associations are only about
  +0.066 and -0.061 mapped points, respectively.
- No tested trait appears in the screenshot's p<0.05 failed-balance table.
  This is a limited diagnostic, not proof that portfolio returns are random.
- The settings header is cropped and the screenshot result layout differs
  from the current repository script; the exact notebook code version remains
  unconfirmed.

## Gates Before a Causal Main Result

1. **Provenance and timing.** Recover the full platform settings, including
   run ID, waves, input tables, and code version. Tabulate survey submission
   dates relative to each fund-shock window. Exclude or separately report any
   respondent whose answer precedes the end of the shock used as exposure.
   Confirm the holding snapshot predates that window. The current 01 script
   reads `submit_date` but does not use it in the sample mask; the methodology
   note's claimed submission-date restriction therefore needs reconciliation.
2. **Observed portfolio.** Use R7's five-wave positive, matched-holding sample
   as the candidate causal benchmark. Verify usable shock and historical
   coverage in each outcome-specific sample. Retain R6 as the preexisting
   keep-zero analysis and report its imputed-zero share explicitly.
3. **Sample and cell parity.** For every outcome, report base, Y-observed, and
   regression-complete N, unique users, cell counts, small/constant-X cells,
   and shock residual variation. Positive-cell assignment hashes should match
   between R6 and R7. With cell FE alone, their X slopes should match when
   the positive observations are identical: zero cells contain no within-cell
   X variation. A mismatch calls for a construction or sample audit.
4. **Conditional comparability.** On R7's exact outcome samples, test balance
   of genuinely pre-shock owner and portfolio traits, both individually and
   jointly. Examine standardized differences and the full table, not only
   p<0.05 flags. Check whether fund exposure tracks the owner's industry or
   geography; use wave-by-industry and available wave-by-geography controls
   as prespecified robustness if sample support allows.
5. **Inference and sensitivity.** Replace HC1-only inference with user-clustered
   SE when users repeat across waves; investigate common fund-shock dependence
   with a fund-level design-based/randomization check where feasible. Report
   confidence intervals and all 11 outcomes with Holm or similar familywise
   adjustment. Sensitivity checks should include a fixed common sample across
   model columns, outcome mapping, answer-time rule, gain tails, and cell
   granularity chosen by density/balance rather than coefficient significance.

## Run Roles and Decision Rules

| Run | Role | What would change the assessment |
| --- | --- | --- |
| R6, five-wave gain, keep zero | Existing exploratory benchmark | If its nominal CPI/cost findings vanish when unmatched holdings are excluded, do not frame them as investor wealth-shock evidence. |
| R7, five-wave gain, positive only | Candidate primary reduced form | Promote only after timing, provenance, sample, balance, and inference gates pass; report nulls as well as positives. |
| R8, four-wave gain, keep zero | 2024q3 influence check | Compare with R6 on common outcome definitions and test a 2024q3 interaction; a significance change alone is not a coefficient-difference test. |
| R9, five-wave return, positive only | Alternative return/information exposure | Compare with R7 on the same respondent sample. Gain and return coefficients have different units and estimands; their contrast alone does not separate wealth from information. |

The pre-correction R1–R5 estimates used pooled cell ranks and should be shown
only as a documented construction problem, not as corroborating results.
Realized returns/gains are affected by trading; they are descriptive unless a
separate IV estimand and exclusion restriction are defended. For expectation
outcomes, passive returns may directly inform beliefs, so passive gain is not
automatically a valid instrument for realized gain.

## Immediate Platform Request

Save R7–R9 settings, cell audits, sample tables, X coefficient/SE/p-value
tables, cell-density and residual-variation tables, and balance outputs in their
corresponding folders. For R6, add the uncropped settings header and identify
the notebook script version. A separate timing cross-tab by wave is needed
before choosing a final causal sample.
