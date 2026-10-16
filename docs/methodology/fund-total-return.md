# Fund total-return reconstruction

**External validation update (2026-10-13): v1 is not ready for formal use.**
Manager reports reveal historical-split counterexamples and sign-dependent
selection under the current masks. The formula needs additive cumulative NAV
in the same share units; stable shares within the window alone are insufficient.
See [external validation](fund-return-external-validation.md). The build and
upload descriptions below document the existing candidate, not approval to use it.

Local build completed on 2026-10-13. No Ant platform run or user-level sample
estimate has used these panels yet. This document supersedes the two-patch
upload instructions for the current 01 and 02 scripts.

## Scope assessment before reconstruction

The control source contains 1,266,578 fund-wave-month rows and 24,485 fund
codes. Among positive-endpoint NAV rows without a legacy unresolved exclusion,
changing only the denominator from beginning cumulative NAV to beginning unit
NAV changes 392,381 rows, 157,214 distinct fund-months, and 7,592 fund codes
(31.0% of all source codes). A difference exceeding 0.0001 decimal return
(one basis point) affects 324,329 rows and 7,229 codes. This assessment compares
unrounded formulas so source four-decimal rounding is not counted as a method
change. It precedes the additional quality masks, and is not a count of final
usable changes or actual platform holdings.

This broad scope warrants complete replacement panels instead of another
sparse patch. Original source panels and both old delivery CSVs remain intact.

## New upload files

Directory relative to the CSMAR root:
`20260823 exp stock/outputs/fund_total_return/`.

| File / proposed uploaded table name | Rows | Usable rows |
| --- | ---: | ---: |
| `shock_panel_total_return_v1.csv` / `shock_panel_total_return_v1` | 122,359 | 105,395 |
| `ctrl_monthly_total_return_v1.csv` / `ctrl_monthly_total_return_v1` | 1,266,578 | 1,222,345 |

Every original key remains present. Unusable operational returns are missing,
never zero. The flags are `shock_usable` and `ctrl_usable`. Both files retain
the original return, a reconstructed candidate, `return_method`,
`quality_reason`, source endpoints, currency, and
`return_version=cash_total_return_v1`. A candidate is diagnostic and must not
be substituted for a missing operational return. A candidate may be missing
or nonfinite where source denominators are unavailable; operational values
are finite or missing only.

The control operational return is decimal. The shock file provides both
`shock_ret_rate` (decimal) and `shock_ret_rate_pp` (percentage points). The
existing platform column names are preserved. Only the two top-level CSVs
need uploading. `support/` holds comparisons, quality counts, changed shock
eligibility, income-unit metadata, hashes, source inventory, and validation.

## Return definition

For ordinary NAV-valued funds with stable share units and consistent
cumulative-NAV definitions:

```text
cash total return = (ending cumulative NAV - beginning cumulative NAV)
                    / beginning unit NAV
```

Writing cumulative NAV as unit NAV plus cumulative cash distributions shows
that the numerator equals the change in unit NAV plus distributions during
the window. The beginning unit NAV converts the beginning holding value into
fixed fund units. Therefore initial holding value times this return equals
the end value of those fixed units plus cash distributions/receivables minus
the initial holding value. Distributions are not reinvested in this ordinary
fund convention. The accumulated dividends from before the window are not
part of the investor's initial principal.

This is a conditional reconstruction from CSMAR fields, not an independently
verified corporate-action-adjusted total-return series. The available local
data do not include a complete dividend/share-split event table. Endpoint
consistency checks cannot detect every within-period event or vendor error.
The existing 80% shock daily coverage and 20% absolute shock bound are
retained, with valid positive unit and cumulative NAV required for counted
days. Recomputing the 20% bound can exclude formerly usable shocks.

Historical controls are fixed-weight portfolio monthly returns, followed by
their 12-month mean and sample standard deviation. Portfolio risk is NOT a
holding-weighted average of fund standard deviations. These monthly controls
are not a compounded 12-month buy-and-hold return.

## Money funds

The 51,845 usable monthly replacements from the old supplement are absorbed
without numeric changes. Its 822 unresolved rows stay missing. This preserves
the user-confirmed rule assigning cross-month bundled income to the recorded
month. It also preserves the prior within-month compounding reconstruction.
The existing 600 nonzero NAV-based money-fund monthly rows instead undergo
the same NAV-denominator reconstruction and quality screening as ordinary
NAV-valued funds.

Money-fund shocks without a positive NAV baseline are reconstructed as the
product of `(1 + disclosed_income / 10000)` for observations whose recorded
dates fall inside the shock window. No income amount recorded after the end
is added. This is a posted-income reconstruction with a daily-compounding
convention, not an exact natural-day accrual measure or fund-specific
settlement simulation. It is not the same cash-dividend strategy as ordinary
funds: money funds retain the accepted income-conversion convention.

An observation spanning up to 14 calendar days supports disclosure coverage.
A later observation can establish coverage of trailing nontrading days but
its amount never enters the earlier shock. The number of such days is
`money_future_evidence_days`. The inferred trading calendar is used to flag
missing income on market trading days. Long gaps, incomplete calendars,
multiple income fields, all-zero income with zero yield, and positive income
with zero yield remain unusable. No income is inferred from seven-day yield.

The common 10,000-yuan normalization is inherited from the prior audited
income convention. The original share metadata now supply `ParValue` in
`support/money_income_units.csv`: most per-100-share fields have 100-yuan
par and all per-million-share fields have 0.01-yuan par. Codes 016002, 159001,
159002 have field/par combinations needing separate vendor/manager checks.
Their prior normalization is retained, not silently changed by factors of
100. No claim of independent fund-specific unit or settlement verification
is made. The two output files expose the reconstructed money method.

## Integrated quality treatment

All 15,652 legacy control exclusions and six legacy shock exclusions remain
excluded. The 7,871 old `exclude=0` bridge annotations are usable replacements,
not exclusions. The original 51,845 usable money replacements match the new
operational control values exactly to exported precision.

Additional masks are conservative screening rules, not proof that the
underlying fund return is erroneous. Reasons can overlap:

| Rule | Treatment |
| --- | --- |
| Non-CNY currency | Exclude from the RMB-compatible operational series until FX conversion is available; retain the local-currency candidate. |
| Nonpositive/missing unit or cumulative NAV | Exclude NAV-based return. Money-income route is handled separately. |
| Cumulative NAV below unit NAV by more than 0.001 | Exclude as inconsistent units/definitions. |
| Change in cumulative NAV minus unit NAV below -0.001 | Exclude as an unexplained decreasing distribution offset or share event. |
| Increase in that offset above 20% of initial unit NAV | Quarantine pending distribution/share-event verification; a real large dividend is possible. |
| Absolute reconstructed monthly return above 50% | Quarantine, not winsorize. |
| Class inception on/after window start | Exclude NAV return; a fixed pre-window holding cannot be verified. |
| Shock baseline over 7 days before last common pre-window trading day; endpoint over 3 days before last common window trading day | Exclude. Missing dates also fail. |
| Monthly endpoints over 7 calendar days before corresponding month-end | Exclude pending freshness review. |
| Previous monthly NAV references disagree with actual previous source month by more than 0.001 | Exclude pending source review. |

Class inception uses the earliest recorded class date when metadata retain
multiple historical records; both inception dates remain in the local build.
This does not resolve every transformation history. Thresholds are explicit
in the builder and should only be relaxed with source evidence.

## Results and interpretation

The new panels have 105,395 usable shocks versus 102,993 originally. They add
4,449 income-based money-fund shocks across 915 codes and remove 2,047 formerly
usable shocks under the expanded rules. Among removed shocks, 917 are
non-CNY; NAV-unit and decreasing-offset issues overlap and must not be summed.

Among finite old/new return pairs, changes above one basis point affect
357,197 control rows across 7,944 codes and 24,821 shock rows across 6,157
codes. This comparison includes income replacement and original rounding;
it differs intentionally from the pre-build denominator-only assessment.
New money shocks with missing old returns are not counted as finite-pair
changes. Counts are fund-level, not user samples or regression effects.

## Reproduction and checks

Run locally from the repository:

```powershell
python scripts/local/build_fund_total_return.py
```

The historical standalone validator has been retired. Its recorded results
remain in the run log; current output is validated by
`scripts/local/validate_fund_nav_annotated.py`.

The builder reads raw monthly/daily Stata files and saved legacy patch inputs.
It does not depend on prior chat scratch files. `--root` can point to another
CSMAR root with the same layout. It regenerates the stable output filenames.
Input/output hashes and source-file inventory are saved. Large CSVs are not
committed to the research git repository.

Local validation passed for source-key preservation, missing/finite rules,
RMB scope, cash-wealth identities, old patch integration, 12-month history
windows, cross-wave consistency, and exclusion of post-window income amounts.
Actual aggregation functions extracted from both platform scripts were tested
on a mixed ordinary/money portfolio, including missing-month coverage and
gain units. Both scripts now use 10,000 yuan for passive/realized gains.

## Platform use

Upload the two CSVs and confirm the actual platform table names. Both 01 and
02 default to their filenames without extensions. The main script revision
is `sme_rf_audited_v6_total_return`, with `APPLY_FUND_QUALITY_PATCH=False`.
Do not apply either old patch again. Version columns are checked at reading;
01 blocks estimates on a mismatch or an attempted legacy patch, while 02
disables fund indicators on a mismatch.

Run the diagnostics and main analysis afresh. Report holding coverage,
new/removed users, risk/expected-return cell transitions, balance and
coefficients before drawing conclusions. Platform execution and actual
holding valuation (NAV versus market price) remain to be confirmed.
