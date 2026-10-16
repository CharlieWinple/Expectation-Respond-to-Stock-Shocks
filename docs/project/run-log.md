# Run Log

## 2026-10-16 01 Addon Resolution Implemented — No New Platform Run

User authorized integrating duplicate/conflict handling and platform-compatible
summary diagnostics into 01, checking the changes, and removing temporary 03.
Revision is `sme_rf_audited_v9_addon_resolution`. Per-question cleaning and
resolution replace first-row selection; ambiguous or unknown nonempty answers
become missing only for that question. Missing keys are excluded from the
addon join. Raw addon conflicts no longer globally block all outcomes;
resolved key/value integrity is checked instead. Other source gates remain.

Output uses existing ant_print_all-backed helpers: policy and integrity status,
without IDs, answer values, small-group counts or before/after affected-group
samples. The raw-addon duplicate row and addon distinct-key total are omitted
to avoid revealing duplicate counts by subtraction; unmapped raw-answer
output is removed. Existing overall samples/estimates remain subject to
platform approval; no unverified minimum disclosure threshold is invented.

Validation: py_compile; synthetic tests for exact repeats, blank/valid merges,
conflicting valid answers, unknown answers, equivalent mapped labels, cleaned
key collisions, missing IDs, empty input, permutation invariance, idempotence,
input preservation and many-to-one merge with other outcomes retained.
All passed. 03 removed after these checks; 02 unchanged. Actual real-data
sample effects and estimates await complete simulation/approval/backend run.

## 2026-10-16 Received 01 R6 Screenshots — Estimates Blocked

Evidence provenance confirmed by user on 2026-10-16: all screenshots supplied
in this diagnostic exchange are real-data results from the administrator
backend workflow, not online simulation. Counts and the addon conflict in
this entry are therefore real-data evidence. Online cells still use simulation
only. The local CSV/platform count difference is real, but its cause and the
relationship between the two datasets remain unverified.
The earlier suggestion to inspect real data by appending an interactive cell
was incorrect. Include any follow-up diagnostics in the complete submission.

Six user-supplied screenshots show revision `sme_rf_audited_v8_nav_annotated`,
run `r6_passive_gain_w5_keepzero`, annotated-v1 shock/control tables,
10/5/5 within-wave average ranks, pooled zero cells within wave,
post-window timing and user-clustered SE. Exact executed commit and execution
time are unconfirmed; this is the evidence receipt date.

CORE 0 reports BLOCK with `conflicting_source_keys_2024q2_addon`.
All 11 CORE 4 rows report `blocked_integrity_gate`; no estimates were produced.
Current code checks raw macro-answer tuples by `submit_id` in
`sme_id3_2024q2_addExpectation` before deduplication and globally blocks all
regressions on a conflict. Conflict count, affected fields and overlap with
the analysis sample are not yet supplied. Raw differences need not imply
different cleaned/mapped responses.

Holding date parse audit: 7,826,840 rows, zero unparsed dates, PASS.
All five snapshot date audits PASS. Sequential funnel: 59,009 raw,
36,153 owners, 28,144 after answer-time filter, 28,139 unique user-wave,
28,139 post-window, 28,136 portfolio eligible, 28,012 return complete,
26,740 control complete, 21,078 after all listed controls and FE filters.

CORE 3/4 regression-ready observations / users:
stock 4,346/4,058; GDP 6,791/6,167; CPI 7,357/6,670;
house 5,504/5,108; rate 6,117/5,654; local environment 10,764/9,638;
revenue 17,519/14,217; market 17,029/13,827; price 8,166/7,410;
wage 8,899/8,024; input cost 8,533/7,726.
These are preparation counts, not successfully estimated samples.
Next evidence: Cell 4 `Duplicate Key Diagnostics Before Deduplication`,
especially the addon row; then diagnose conflicting answer fields and sample
overlap before selecting any resolution rule. No gate bypass or script edit.

Follow-up screenshot received: addon rows 14,876; unique submit IDs 14,874;
duplicate-key rows 4; duplicate keys 2; conflicting keys 1. Shock
122,359, control 1,266,578 and portrait 42,791 rows each have unique keys,
zero duplicate rows and zero conflicting keys. Prepared the optional
`scripts/diagnostics/03_sme_addon_conflicts.py` notebook follow-up to inspect
raw/cleaned/mapped duplicate answers and current sample overlap without
changing the blocker or selecting a resolution. Awaiting platform output.

User supplied `data/sme_survey_2024q2_addExpectation.csv` as the supplemental
questionnaire. Local read-only CSV inspection finds 4,604 rows and 4,604
distinct `seqno` values (no duplicate seqno), four macroeconomic answer
columns and eight focus columns; no `submit_id` column. This differs from
the platform addon audit (14,876 rows keyed by submit_id). The relation
between seqno and platform submit_id and the upload/join transformation
remain unverified. This file alone cannot identify the platform conflict;
do not assume that source CSV uniqueness guarantees platform key uniqueness.

## 2026-10-16 Agreed Configuration and Zero Handling — No Platform Run

User accepts 10/5/5 bins, retains existing full FE, and requests one shared
zero cell per wave rather than separate cells by zero source. Applied to 01/02.
Ranks are wave-specific and cell labels include wave (full wave-by-cell FE).
Zero-history eligibility is explicit; no fabricated coverage or 12-month
counts. Source flags and observed realized gains remain. 01 adds main vs
positive-only estimates with fixed positive cells and exact sample provenance.
Validation: both py_compile checks passed; synthetic cases passed for both
scripts (recorded/absent zeros pool within wave, different waves remain
separate, history stays missing, positive incomplete coverage still fails).
This supersedes the configuration and separate-zero-cell notes below.

## 2026-10-16 Zero-Holding Policy — Local Configuration Change Only

User confirms that recorded zero and absent snapshot holdings both represent
zero holdings, with invalid recorded amounts not expected. Select the existing
R6 preset in 01 and explicitly include absent-record zeros. Preserve source
flags and separate wave-specific zero cells. This supersedes the earlier
recommendation to exclude all absent holdings through R10. No new platform
execution or revised sample counts are available. Other settings unchanged.


## 2026-10-16 User Clarification — Structural Outcome Absence

The user confirms that 2024q2 did not contain exp_stock. Its zero exact
sample is therefore expected, not an input or mapping failure. This resolves
the earlier open question recorded below. Stock covers four waves; revenue
and price cover five. Cross-outcome comparisons should account for different
wave coverage and complete-case samples. No new platform run was performed.

## 2026-10-15 Screenshot Receipt — 02 Annotated-NAV Diagnostics (Batch Complete)

User reports platform execution completed. Two original Diagnostic Settings
screenshots have been archived, with matching source/copy SHA256 checksums,
under the CSMAR output root:
`outputs/platform_runs/sme_diagnostics_nav_annotated/run_001/`.
The manifest records each image, provenance, and transcribed settings. This is
the receipt date; the actual execution date and script revision are unconfirmed.

Observed settings: input gate PASS; `nav_price_annotated_v1`; NAV screening
False; five waves 2024q2–2025q2; passive_gain; usable scope; keep_zero False;
bins **10/5/5**; FE **analysis_portfolio_cell, city_level_from_yicai,
portrait_gender**; controls age, college, firm age and company; compact output;
key and conditional outcomes exp_stock/exp_rev/exp_price; cluster_user;
minimum answer time 180 seconds; return/control coverage 0.999999; 12-month
history enforced. Numeric employee control and employee-group FE are both False.

Actual bins and FE differ from repository defaults (5/3/3 plus industry and
employee-group FE). Interpret subsequent screenshots using the observed
configuration. Exact uploaded table names, full executed notebook provenance,
sample sizes and diagnostic results remain pending. Input gate PASS does not
establish economic validity of every retained fund return. No substantive
result is yet available for findings.md.

Screenshot 003 subsequently received: Source Read Summary. Survey reads are
2024q2 14,876 x 19; 2024q3 12,975 x 24; 2024q4 12,509 x 24;
2025q1 9,056 x 24; 2025q2 9,593 x 24. The 2024q2 addon is 14,876 x 5.
Shock is 122,359 x 15; control 1,266,578 x 13; portrait 42,791 x 2;
holding 1,288,708 x 7. Shock/control read dimensions match the compact upload
schema. These are script read-summary counts, not final analysis samples or
proof of key uniqueness. Exact table names remain unconfirmed. The archive
includes the original image and `source_read_summary.csv` transcription.

Screenshot 004: Shock Window Calendar. All five gates PASS:
2024q2 23,020 fund rows, 2024-06-01 to 2024-06-13;
2024q3 23,686, 2024-09-01 to 2024-09-17;
2024q4 24,391, 2024-12-01 to 2024-12-10;
2025q1 25,217, 2025-03-01 to 2025-03-17;
2025q2 26,045, 2025-06-01 to 2025-06-12.
The five row counts sum to 122,359, matching screenshot 003.
PASS confirms the script's nonmissing, common within-wave window-date checks;
it does not independently validate return quality or survey timing compliance.
Original image and `shock_window_calendar.csv` are retained in the same archive.

Screenshot 005: Fund NAV Flag Summary. Calculable denominators are 110,806
shock rows and 1,250,865 control rows. Prior-screen failures retained by the
current flags-only policy: 6,381 (5.76%) and 103,872 (8.30%), respectively.
For shock/control, individual flag counts are: NAV relation break 2,157/46,544;
large daily jump 5/348; insufficient daily evidence 3,440/52,014; large window
return 7/108; date or inception 1,885/2,737; currency 919/10,701; legacy issue
0/4. These match the earlier local calculable and retained-screen-failure
counts. Flags overlap; their sum is not a distinct anomaly count. These are
fund-row counts, not exposed user counts or holding-weighted shares. Original
image and `fund_nav_flag_summary.csv` (including derived percentages) are
archived. Exact executed notebook provenance remains unconfirmed.

Screenshot 006: Configured Variable Check reports `ok — all configured FE
and controls found`. This confirms column availability for the actual
configuration in screenshots 001–002; nonmissing coverage and final samples
are not established by this check. Original image and transcription are saved
in the same run archive and manifest.

Screenshot 007: pooled Sample Size Sequential Funnel, 17 rows transcribed;
all adjacent remaining-count differences match reported drops. Starting
59,009 user-wave rows: SME owners 36,153 (-22,856); answer-time filter 28,144
(-8,009); unique user-wave 28,139 (-5); post-shock submission 28,139 (-0);
positive portfolio 15,827 (-12,312); passive gain nonmissing unchanged;
return completeness 15,703 (-124); control completeness 14,431 (-1,272);
cell inputs unchanged; age availability 14,426 (-5); college availability
12,210 (-2,216); firm age, company, and portfolio-cell FE unchanged; city
availability 12,153 (-57); gender availability unchanged. The final pooled
sequential count is 12,153, not yet an outcome-specific regression sample.
Drops depend on filter order and count rows rather than distinct users.
The zero post-shock timing drop applies only after the preceding filters.
Original image (including its page break) and
`sample_size_sequential_funnel.csv` are retained in the run archive.

Screenshot 008: Holding Provenance after Owner and Answer Filters:
no_holding_record 11,427; positive_no_usable 3; positive_usable 15,832;
record_zero 882. Total 28,144 matches the funnel after owner/answer filters,
before unique-user-wave and timing filters. Positive_usable exceeds the
subsequent 15,827 positive-portfolio count by five, consistent with the
intervening five duplicate user-wave row removals; this is an aggregate
reconciliation, without row-level identities. No holding record does not
establish zero holdings, and usable denotes calculable returns rather than
quality approval. Original image and `holding_provenance.csv` are archived.

Screenshot 009: Portfolio Cell Summary: rows_with_cell 14,431;
duplicate_user_wave_removed at this construction stage 0; n_cell 989;
n_singleton 63; min_cell_n 1; max_cell_n 119. The construction count matches
the funnel's control-complete/cell-input count. This partition is constructed
before trait and outcome complete-case selection; these are not final
outcome-specific cell/singleton counts. The zero duplicate removal at this
stage follows the earlier unique-user-wave filter and does not contradict
its five removed rows. Original image and `portfolio_cell_summary.csv` are
archived in run_001.

Screenshot 010: Outcome Regression Sample Size. Every outcome starts from
14,431 base rows. Transcribed (Y_nonmiss_n, Y_missing_drop, reg_ready_n,
reg_var_drop): exp_stock (3,171, 11,260, 2,520, 651);
exp_gdp (4,617, 9,814, 3,950, 667); exp_cpi (5,084, 9,347, 4,310, 774);
exp_house (3,703, 10,728, 3,014, 689); exp_rate (4,161, 10,270, 3,372, 789);
exp_env_local (7,229, 7,202, 6,053, 1,176);
exp_rev (11,959, 2,472, 10,155, 1,804);
exp_market (11,621, 2,810, 9,876, 1,745);
exp_price (5,476, 8,955, 4,658, 818);
exp_wage (5,936, 8,495, 5,074, 862);
exp_input_cost (5,659, 8,772, 4,830, 829).
Both arithmetic identities pass for all 11 rows. This preparation table must
still be reconciled with the forthcoming Exact Regression Samples table,
which applies numeric conversion and finite-value complete-case rules.
Counts are observations, not unique users or regression estimates. Original
image and `outcome_regression_sample_size.csv` are archived in run_001.

Screenshot 011: Exact Regression Samples. Observation / distinct-user counts:
exp_stock 2,520 / 2,342; exp_gdp 3,950 / 3,530; exp_cpi 4,310 / 3,844;
exp_house 3,014 / 2,793; exp_rate 3,372 / 3,091;
exp_env_local 6,053 / 5,323; exp_rev 10,155 / 8,158;
exp_market 9,876 / 7,938; exp_price 4,658 / 4,165;
exp_wage 5,074 / 4,491; exp_input_cost 4,830 / 4,308.
All 11 observation counts match screenshot 010's reg_ready_n. For every
outcome, duplicate_user_wave, record_zero, missing_holding, and
history_incomplete are zero, and positive equals the full outcome sample.
Users can recur across waves; distinct-user counts are outcome-specific and
must not be summed. These confirm this diagnostic run's complete-case counts,
not regression estimates or economic validity of retained flagged returns.
Original page-spanning screenshot and `exact_regression_samples.csv` are
archived in run_001.

Screenshot 012: Exact Samples by Wave, ordered 2024q2/2024q3/2024q4/2025q1/2025q2.
exp_stock n=0/1,053/95/652/720, X_sd=missing/.2493/.0339/.1972/.1932;
exp_rev n=3,104/2,621/967/1,631/1,832, X_sd=.1551/.2691/.1661/.2684/.1607;
exp_price n=1,442/1,373/165/776/902, X_sd=.1405/.2293/.0267/.1802/.1730.
Within each wave, users equal n. All three observation sums match screenshot
011. Distinct users across waves must not be obtained by summing wave users.
exp_stock has no 2024q2 final observations; the cause is not identified by
this table and should be checked against outcome mapping/availability and
complete-case filters. X_sd is raw passive_gain dispersion in 10,000-yuan
units, rounded in the screenshot, not conditional identifying variation.
Original image and `exact_samples_by_wave.csv` are archived in run_001.

Screenshot 013: Cell Information in Final Samples. Transcribed columns are
cells, singleton_cells, obs_cell_lt5, obs_no_X_variation, median_cell_n,
within_cell_X_sd, raw_X_sd:
exp_stock (574,144,824,144,3,.1486,.2219);
exp_gdp (782,194,1043,196,3,.1602,.2107);
exp_cpi (783,173,964,173,3,.1618,.2097);
exp_house (722,216,1004,216,3,.1438,.2066);
exp_rate (731,187,1034,189,3,.1560,.2155);
exp_env_local (843,157,915,159,4,.1435,.1861);
exp_rev (960,96,899,98,7,.1692,.2146);
exp_market (961,103,912,105,7,.1695,.2144);
exp_price (801,184,949,184,4,.1373,.1843);
exp_wage (809,167,915,167,4,.1470,.1883);
exp_input_cost (807,176,965,176,4,.1495,.1939).
All occupied-cell counts are at most the 989 constructed cells, and count
consistency checks against exact outcome sample sizes pass. Using screenshot
011 denominators, shares of observations in cells below five are 32.70% for
exp_stock, 8.85% for exp_rev and 20.37% for exp_price. These overlap with the
no-X-variation observations and must not be added. Within-cell dispersion
does not partial out the other FE and controls. Original image and
`cell_information_final_samples.csv` (with derived shares) are archived.

Screenshot 014: Conditional Shock Variation, columns n, raw_X_sd,
residual_X_sd, residual_SS_share, df_resid:
exp_stock (2520,.2219,.1482,.4463,1936);
exp_rev (10155,.2146,.1691,.6204,9185);
exp_price (4658,.1843,.1370,.5531,3847).
Sample counts match screenshot 011 and raw standard deviations match 013.
After the configured FE and controls, 44.63%/62.04%/55.31% of demeaned raw
X sum of squares remains for stock/revenue/price samples. These are
sum-of-squares shares, not standard-deviation shares. Nonzero residual
variation does not establish exogeneity, balance, or statistical power.
Results apply to this run's actual 10/5/5 cells, three FE and four controls.
Original image and `conditional_shock_variation.csv` are archived in run_001.

Screenshot 015: Conditional Balance. For traits age/college/firm_age/company/
employee_n, rows below give (n,beta,se,p,standardized effect):
exp_stock (2520,-1.2472,1.0900,.2526,-.0166);
(2520,-.0878,.0876,.3164,-.0283); (2520,.2106,.5466,.7001,.0079);
(2520,-.0256,.0261,.3265,-.0138); (1250,.1005,.3140,.7489,.0073).
exp_rev (10155,-.0445,.5384,.9341,-.0007);
(10155,-.0140,.0293,.6325,-.0049); (10155,.0189,.2094,.9280,.0008);
(10155,-.0314,.0183,.0854,-.0192); (4973,.1149,.1651,.4864,.0107).
exp_price (4658,-.0085,.9722,.9930,-.0001);
(4658,-.0862,.0581,.1382,-.0246); (4658,.1802,.4082,.6589,.0063);
(4658,-.0193,.0222,.3834,-.0097); (2288,-.4774,.3960,.2280,-.0372).
All notes say tested_trait_excluded_from_controls. No individual p-value is
below .05; the minimum is .0854 for company in the revenue sample. The
largest displayed absolute standardized effect is .0372. Employee tests use
smaller subsets (1250/4973/2288) and do not establish full-sample balance for
employee count. These exploratory unadjusted tests use user clustering per
the settings; no joint balance test is shown, and non-rejection does not
prove exogeneity or predetermined measurement. Original image and
`conditional_balance.csv` are archived in run_001. Collection remains open
for any additional screenshots or executed-notebook provenance.

User subsequently confirmed there are no more screenshots in this batch.
Collection closed on 2026-10-15 with 15 images; every manifest image is
present and its SHA256 matches. `README.txt` now consolidates the settings,
results, caveats and next checks. Remaining provenance gaps are the actual
execution date, uploaded table names and executed notebook code/revision.
Priorities are to explain the zero 2024q2 stock-outcome sample, match 01's
configuration to this diagnostic, and assess flagged-return holding exposure
and screening sensitivity before substantive interpretation.

## 2026-10-14 Local Upload Compacting and 02 Alignment — No Platform Run

The complete annotated panels remain the audit source. New same-name compact
CSV copies in `outputs/fund_nav_upload/` retain all 122,359 shock and 1,266,578
control rows, the columns used by 01/02, and seven quality flags. A streaming
row-by-row comparison confirmed identical selected values for every row.
Compact files are 10,785,594 and 95,262,813 bytes, respectively.
02 now defaults to R7 passive gain with user clustering, the post-window and
unique-user-wave rules, and within-wave portfolio ranks. It collects the key
tables at the end of Cell 10 for screenshots. No Ant run or new estimate has
been made. Local Python syntax check was unavailable because the configured
Python executable could not be found.
The dormant old-patch path in 01 and the superseded patch upload guide were
removed. Historical inputs and results remain described in the schema and
run log.

## 2026-10-13 Flags-Only Delivery — No Platform Run

User chose to retain calculable ordinary NAV returns in primary columns,
with flags instead of default exclusions. Outputs: `fund_nav_annotated/`
`shock_panel_nav_annotated_v1.csv` (122,359 rows; 110,806 populated) and
`ctrl_monthly_nav_annotated_v1.csv` (1,266,578 rows; 1,250,865 populated).
`return_version=nav_price_annotated_v1`. New 01 revision
`sme_rf_audited_v8_nav_annotated`; both scripts default
`APPLY_NAV_QUALITY_SCREEN=False`, preserving the stricter policy as an option.
Primary values, screened alternatives and independent flags are separate.
Money policy is unchanged. No user-level results or platform run claimed.

## 2026-10-13 Local Screened NAV Build — No Platform Run

User approved unit-NAV price returns excluding suspected event windows.
Builder: `scripts/local/build_fund_nav_screened.py`; independent validator:
`scripts/local/validate_fund_nav_screened.py`. CSMAR source daily NAV files
for 2023–2025, static fund classification and retained v1 panels are inputs.
Outputs under `outputs/fund_nav_screened/`: `shock_panel_nav_screened_v1.csv`
(122,359 rows, 104,425 usable) and `ctrl_monthly_nav_screened_v1.csv`
(1,266,578 rows, 1,146,993 usable), version `nav_price_screened_v1`.
Ordinary prices use unit NAV, money rows are unchanged; daily NAV relations
are used for screening, not return magnitudes. All original keys preserved.

Complete 12-month fund-wave windows drop from 93,035 to 76,458. Required
coverage and month counts in platform scripts are unchanged. New main revision
is `sme_rf_audited_v7_nav_screened`; 01 and 02 table/version settings agree.
Syntax checks and independent validation pass, including real audited
distribution/split examples, actual aggregation functions and missing-month
coverage. See `docs/methodology/fund-nav-screened.md` for all rules, counts and
limitations. No platform execution, user-level attrition or estimates reported.

## 2026-10-13 Local Fund Reconstruction — No Platform Run

Source: CSMAR raw daily/monthly Stata data, static share metadata, original
shock/control CSVs and both 2026-10-12 delivery patches. Builder:
`scripts/local/build_fund_total_return.py`; validator:
`scripts/local/validate_fund_total_return.py`.

Prepared upload tables `shock_panel_total_return_v1` (122,359 fund-wave rows,
105,395 usable) and `ctrl_monthly_total_return_v1` (1,266,578 fund-wave-month
rows, 1,222,345 usable), under the CSMAR `outputs/fund_total_return/` directory.
The pre-build definition assessment found 7,592 affected fund codes and
392,381 control rows. Both old patches are integrated. The new shock panel
adds 4,449 money-income rows and excludes 2,047 formerly usable rows under
the expanded checks. These are local fund counts, not platform sample sizes.

Current main revision: `sme_rf_audited_v6_total_return`; old patch switch off.
01 and 02 share data tables and gain units. Syntax and independent validation
passed; support files include hashes, comparison tables and validation JSON.
Method details and limitations: `docs/methodology/fund-total-return.md`.
No coefficients, user-level coverage, or final sample sizes were produced.

## 2026-09-21 R6 Passive Gain, Five Waves, Keep Zero — Screenshots Reviewed 2026-10-12

Source: user-saved PNGs in `outputs/platform_screenshots/r6_passive_gain_w5_keepzero/`
and user confirmation on 2026-10-12. The platform task list identifies the
2026-09-21 15:04–15:46 run as the five-wave passive-gain keep-zero main
regression. Eleven of eighteen PNGs contain platform output; seven are still
placeholders. The visible `Active Regression Settings` screenshot starts below
`RUN_ID`, so the exact notebook run ID and wave list are not visible there.

- The settings show `CORE_X_CHOICE=passive_gain`, `GAIN_UNIT_YUAN=10,000`,
  `SHOCK_PORTFOLIO_SCOPE=usable`, `ENFORCE_CONTROL_COMPLETENESS=True`,
  `CELL_RANK_SCOPE=within_wave`, `CELL_RANK_METHOD=average`, 5/3/3 bins, and
  `KEEP_ZERO_PORTFOLIO=True`.
- The Cell 7 funnel explicitly uses `3_portfolio_ge0`; the analysis base has
  26,694 rows. Holding provenance reports 882 recorded-zero and 11,427
  imputed-zero rows in that base. The cell audit includes both zero statuses
  in each wave. These outputs agree with the user-confirmed keep-zero R6 label.
- The screenshots labeled `02_main_rf_1/2` show the older `Main RF Results`
  layout (`spec`, `Y`, `n_obs`, `beta`, `se`, `t`, `p`, `R2`, `note`). The current
  repository script instead emits `RF Coefficients and Fit - Estimates` and
  `RF Coefficients and Fit - P Values, R2, and Notes`. The notebook code or
  screenshot provenance therefore needs confirmation before attributing the
  exact code version to commit `f18e3c1`.
- Main specification `cell_other_fe_controls`: `exp_cpi` beta 0.46714,
  SE 0.19156, p 0.0147, n 7,343; `exp_input_cost` beta -0.45558,
  SE 0.20980, p 0.0299, n 8,514. These are nominal 5% results. Neither
  clears a Bonferroni threshold of 0.05/11 across the 11 outcomes.
- Outcome-specific cell counts range from 162 to 216; 42.3%–46.4% of
  observations lie in cells with no passive-gain variation. The residual
  shock-sum-of-squares share after FE/controls ranges from 0.6536 to 0.8010.
  The failed-traits balance table reports none at p<0.05.

Interpretation: this is a user-confirmed keep-zero R6 result, but the cropped
run header and older result-table layout prevent exact code-version
attribution. The 11,427 imputed-zero observations (42.8% of the base) remain
a substantive sample-definition concern. Treat coefficients as provisional
until the R7 positive-portfolio comparison and notebook provenance are checked.

Updated run plan confirmed by the user from the platform task list:
R7 is five-wave `passive_gain`, positive only (2026-09-21 15:51–16:37);
R8 is four-wave `passive_gain`, keep zero, excluding 2024q3
(2026-09-22 08:56–09:26); R9 is five-wave `passive_return`, positive only
(2026-09-22 10:19–11:07). The platform task screenshot confirms run labels
and timing, but the R7–R9 result tables have not yet been saved locally.

## 2026-09-10 User-Supplied Post-Diagnostic Main RF Run

Source: four platform screenshots supplied in conversation on 2026-09-10.
Script: `scripts/analysis/01_sme_expectations_rf.py`

Active settings:
- `CORE_X_CHOICE = passive_return`; `CORE_X_VAR = X100_R_passive`
- `SHOCK_PORTFOLIO_SCOPE = usable`
- `KEEP_ZERO_PORTFOLIO = False`
- `ENFORCE_CONTROL_COMPLETENESS = True`
- Portfolio-cell bins: 5 size x 3 risk x 3 expected-return
- SE type: HC1
- Fixed effects: `analysis_portfolio_cell`, `city_level_from_yicai`,
  `portrait_gender`, `survey_industry`, `aer_bal_employee_group`
- Controls: `aer_bal_age`, `aer_bal_college`, `aer_bal_firm_age`,
  `aer_bal_company`

Sequential funnel from screenshots:
- Raw rows: 59,009
- SME owners: 36,153; dropped 22,856
- After answer-time screen: 28,144; dropped 8,009
- Positive usable portfolio: 15,807; dropped 12,337
- `X100_R_passive` nonmissing: 15,807; dropped 0
- Return-complete diagnostic: 15,336; dropped 471
- Control-complete diagnostic: 14,385; dropped 951
- Cell inputs: 14,385; dropped 0
- Age nonmissing: 14,379; dropped 6
- College nonmissing: 12,169; dropped 2,210
- Firm age/company nonmissing: 12,169; dropped 0 each
- Portfolio cell/city/gender nonmissing: city drops 57; gender drops 0
- Industry nonmissing: 11,597; dropped 515
- Employee-group nonmissing: 11,597; dropped 0

Outcome-specific samples and reduced-form results:

| Y | Y nonmissing in base | Final n | beta | se | p |
|---|---:|---:|---:|---:|---:|
| exp_stock | 3,162 | 2,510 | -0.14748 | 0.28798 | 0.6086 |
| exp_gdp | 4,603 | 3,726 | -0.06199 | 0.05086 | 0.2229 |
| exp_cpi | 5,065 | 4,064 | 0.01840 | 0.03683 | 0.6174 |
| exp_house | 3,697 | 2,962 | 0.15003 | 0.21272 | 0.4806 |
| exp_rate | 4,149 | 3,300 | 0.00296 | 0.02321 | 0.8983 |
| exp_env_local | 7,207 | 5,740 | 0.00196 | 0.00903 | 0.8284 |
| exp_rev | 11,915 | 9,687 | 0.05330 | 0.07951 | 0.5026 |
| exp_market | 11,580 | 9,415 | 0.07113 | 0.07894 | 0.3675 |
| exp_price | 5,463 | 4,451 | 0.03615 | 0.03967 | 0.3622 |
| exp_wage | 5,925 | 4,827 | 0.02935 | 0.02495 | 0.2394 |
| exp_input_cost | 5,639 | 4,595 | -0.03431 | 0.03554 | 0.3343 |

Interpretation:
- No coefficient is significant at the 5 percent or 10 percent level.
- The post-diagnostic main specification should be treated as the current
  preferred reduced-form benchmark, and its evidence is mostly null.
- The earlier marginal positive `exp_price` result does not survive the added
  industry and grouped employment-size fixed effects plus enforced historical
  control completeness.
- Next diagnostics should focus on exact outcome-specific cell sparsity,
  residual shock variation after fixed effects, wave-specific/leave-one-wave-out
  estimates, answer-time cutoff robustness, and a separately labeled passive-gain
  robustness for zero-portfolio respondents.

## 2026-09-08 User-Supplied Positive-Portfolio Run

Source: four platform screenshots supplied in conversation on 2026-09-08.
Execution date, commit and Active Regression Settings were not supplied.
Intended specification was all waves, passive return, usable scope, positive
portfolio, 10/5/5 cells, city/gender FE and four basic controls. However, the
actual funnel includes employee count, so this is not confirmed as that baseline.
Do not attribute differences from the earlier keep-zero run to zero holdings alone.

Portfolio cells: 15,332 user-wave rows, 2 duplicates removed for cell construction,
937 occupied cells, 102 singleton cells, size range 1-126. These precede outcome
and complete-case filtering and are not outcome-specific occupied-cell counts.

Sequential funnel: raw 59,009; owners 36,153; answer filter 28,144;
positive portfolio 15,807; X nonmissing 15,807; return complete 15,336;
history complete 14,385; cell inputs 14,385; age 14,379; college 12,169;
firm age/company 12,169; employee count 5,678; city/gender 5,646.
Employee count drops 6,491 (53.34% of preceding observations). Historical
completeness in this diagnostic funnel is not enforced in the actual base mask.

| Y | Y nonmissing in base | Final n | beta | se | p |
|---|---:|---:|---:|---:|---:|
| exp_stock | 3457 | 1357 | -0.44545 | 0.52503 | 0.3962 |
| exp_gdp | 4978 | 2144 | -0.06474 | 0.08940 | 0.4690 |
| exp_cpi | 5437 | 2272 | 0.00887 | 0.06649 | 0.8939 |
| exp_house | 3998 | 1619 | -0.11143 | 0.38659 | 0.7732 |
| exp_rate | 4476 | 1800 | 0.02812 | 0.03906 | 0.4715 |
| exp_env_local | 7686 | 3046 | -0.02292 | 0.01632 | 0.1603 |
| exp_rev | 12740 | 5297 | -0.07703 | 0.12741 | 0.5454 |
| exp_market | 12394 | 5142 | 0.02197 | 0.12783 | 0.8636 |
| exp_price | 5855 | 2445 | 0.06046 | 0.07510 | 0.4208 |
| exp_wage | 6340 | 2693 | -0.00214 | 0.04760 | 0.9641 |
| exp_input_cost | 6044 | 2518 | -0.03514 | 0.06568 | 0.5922 |

Base n is 15,336 for every outcome. exp_stock has no 2024q2 question;
its base-to-outcome loss cannot all be labeled respondent nonresponse.
All supplied p-values exceed .10. Approximate normal 95% intervals:
exp_stock [-1.4745, 0.5836], exp_price [-0.0867, 0.2077]. These do not
establish precise zero effects. The earlier exp_price estimate 0.09457 is
inside the latest interval; significance changes alone are not a difference test.

Follow-up: 02 adds employee complete-case attrition and cell sparsity on fixed
cells, keeps four controls by default, and switches default keep-zero to False.
No new platform run performed by Codex; local synthetic and syntax checks only.

Use this file to record platform runs after git commits.

## 2026-09-01 Migration

- Migrated the old v8 script into `scripts/analysis/01_sme_expectations_rf.py`.
- No platform run has been performed in this new git-based project yet.

## 2026-09-01 First Platform Run, Interrupted In Cell 8

Date: 2026-09-01
Commit before follow-up fix: `6d10887`
Script: `scripts/analysis/01_sme_expectations_rf.py`
Platform environment: Ant platform notebook

Inputs:
- `SHOCK_TABLE = shock_panel_v2`
- `PORT_CONTROL_TABLE = ctrl_monthly_panel`

Cell 4 source-read diagnostics:
- Surveys: 2024q2 14,876 rows/16 cols; 2024q3 12,975/21;
  2024q4 12,509/21; 2025q1 9,056/21; 2025q2 9,593/21.
- 2024q2 addon: 14,876 rows/5 cols.
- Shock panel: 122,359 rows/4 cols.
- Control panel: 1,266,578 rows/4 cols.
- Holding panel: 1,288,708 rows/6 cols.

Cell 5 survey construction:
- Rows/users/sme owners/answer observations/answer time below 180 seconds:
  2024q2 14,876/14,876/9,354/14,876/6,857;
  2024q3 12,975/12,975/7,502/12,975/5,028;
  2024q4 12,509/12,509/8,007/12,509/5,190;
  2025q1 9,056/9,056/5,324/9,056/4,126;
  2025q2 9,593/9,583/5,966/9,593/4,299.
- 2024q2 addon merge diagnostics: survey keys 14,874; addon keys 14,874;
  key overlap 14,874; `exp_gdp`, `exp_house`, `exp_cpi`, and `exp_rate`
  nonmissing counts all 0. The keys merged, but the expected macro columns did
  not produce numeric nonmissing values.

Cell 6 user-level shock/control summary:
- Rows/users/mean portfolio/return coverage/control coverage/min control
  coverage/control months/return nonmissing/risk nonmissing:
  2024q2 24,163/24,163/28,962.74/0.9996/0.9942/0.9852/11.37/22,890/22,905;
  2024q3 23,168/23,168/29,946.61/0.9996/0.9954/0.9867/11.35/21,904/21,933;
  2024q4 21,913/21,913/32,034.86/0.9996/0.9938/0.9851/11.45/20,896/20,925;
  2025q1 22,253/22,253/31,587.94/0.9997/0.9951/0.9877/11.09/20,557/20,583;
  2025q2 20,997/20,997/33,902.31/0.9995/0.9958/0.9904/11.41/19,957/19,986.

Base sample sequential funnel:
- Final sample after `R_nonmissing`: 2024q2 4,115; 2024q3 3,628;
  2024q4 3,219; 2025q1 2,299; 2025q2 2,552.
- The largest drops are the SME-owner filter, answer-time filter, and positive
  portfolio filter.

Portfolio-cell diagnostics:
- Rows with cell: 15,809.
- Duplicate user-wave rows removed: 2.
- Number of cells: 223.
- Singleton cells: 4.
- Cell size range: 1 to 243.

Cell 8 interruption:
- Error line: `results = pd.DataFrame([run_rf(df, y_name) for y_name in Y_VARS])`.
- Error message: `TypeError: Cannot interpret 'string[python]' as a data type`.
- Follow-up change: convert formula categorical variables (`wave` and
  `analysis_portfolio_cell`) from pandas nullable string dtype to ordinary
  object dtype inside `run_rf`; add a CELL 8 dtype diagnostic table before the
  regressions.

## 2026-09-01 Platform Run, Completed Through Main RF Results

Date: 2026-09-01
Script: `scripts/analysis/01_sme_expectations_rf.py`
Platform environment: Ant platform notebook

Inputs:
- `SHOCK_TABLE = shock_panel_v2`
- `PORT_CONTROL_TABLE = ctrl_monthly_panel`

Cell 4 source-read diagnostics:
- Surveys: 2024q2 14,876 rows/16 cols; 2024q3 12,975/21;
  2024q4 12,509/21; 2025q1 9,056/21; 2025q2 9,593/21.
- 2024q2 addon: 14,876 rows/5 cols.
- Shock panel: 122,359 rows/4 cols.
- Control panel: 1,266,578 rows/4 cols.
- Holding panel: 1,288,708 rows/6 cols.

Cell 5 survey construction:
- Rows/users/sme owners/answer observations/answer time below 180 seconds:
  2024q2 14,876/14,876/9,354/14,876/4,399;
  2024q3 12,975/12,975/7,502/12,975/2,729;
  2024q4 12,509/12,509/8,007/12,509/3,030;
  2025q1 9,056/9,056/5,324/9,056/2,455;
  2025q2 9,593/9,583/5,966/9,593/2,512.
- 2024q2 addon merge diagnostics: survey keys 14,874; addon keys 14,874;
  key overlap 14,874; nonmissing mapped outcomes: `exp_gdp` 2,977,
  `exp_cpi` 3,227, `exp_house` 485, `exp_rate` 705.

Cell 6 user-level shock/control summary:
- Rows/users/mean portfolio/return coverage/control coverage/min control
  coverage/control months/return nonmissing/risk nonmissing:
  2024q2 24,163/24,163/28,962.74/0.9996/0.9942/0.9852/11.37/22,890/22,905;
  2024q3 23,168/23,168/29,946.61/0.9996/0.9954/0.9867/11.35/21,904/21,933;
  2024q4 21,913/21,913/32,034.86/0.9996/0.9938/0.9851/11.45/20,896/20,925;
  2025q1 22,253/22,253/31,587.94/0.9997/0.9951/0.9877/11.09/20,557/20,583;
  2025q2 20,997/20,997/33,902.31/0.9995/0.9958/0.9904/11.41/19,957/19,986.

Cell 8 regression summary:
- `exp_stock`: n 3,290, beta -0.18940, se 0.22447, t -0.844, p 0.3988, R2 0.1641.
- `exp_gdp`: n 5,017, beta -0.03236, se 0.03929, t -0.824, p 0.4102, R2 0.0465.
- `exp_cpi`: n 5,419, beta -0.00738, se 0.02776, t -0.266, p 0.7903, R2 0.0732.
- `exp_house`: n 3,795, beta 0.18588, se 0.17653, t 1.053, p 0.2923, R2 0.0677.
- `exp_rate`: n 4,226, beta 0.01105, se 0.01767, t 0.626, p 0.5316, R2 0.4021.
- `exp_env_local`: n 7,429, beta 0.00006, se 0.00657, t 0.009, p 0.9930, R2 0.0456.
- `exp_rev`: n 12,858, beta -0.00015, se 0.05757, t -0.003, p 0.9979, R2 0.0217.
- `exp_market`: n 12,478, beta 0.00996, se 0.05821, t 0.171, p 0.8641, R2 0.0197.
- `exp_price`: n 5,714, beta 0.05436, se 0.03134, t 1.735, p 0.0828, R2 0.0462.
- `exp_wage`: n 6,169, beta 0.02803, se 0.02243, t 1.250, p 0.2114, R2 0.0446.
- `exp_input_cost`: n 5,923, beta -0.00924, se 0.02750, t -0.336, p 0.7368, R2 0.0582.

Interpretation:
- No outcome is significant at the 5 percent level. `exp_price` is marginal at
  the 10 percent level and positive.
- The active specification estimates precise nulls for many business outcomes,
  but the credibility of a pure null should be checked against sample attrition,
  answer-time filtering, outcome mapping, and shock variation after portfolio
  cell fixed effects.

Follow-up changes:
- Cell 8 now prints `Detailed RF Coefficients` for the passive-return regressor
  and four trait controls before the final `Main RF Results` table.
- Cell 8 now prints `RF Fixed Effect Diagnostics` with wave and portfolio-cell
  FE inclusion/counts.

## Template

```text
Date:
Commit:
Script:
Platform environment:

Inputs:
- SHOCK_TABLE =
- PORT_CONTROL_TABLE =

Cell 4 source-read diagnostics:

Cell 5 sample funnel:

Cell 5b distribution checks:

Cell 6 regression summary:

Interpretation:

Follow-up changes:
```
