Platform regression screenshot workspace (local only; outputs/ is git-ignored).

Save screenshots in the folder matching the run ID shown by the platform.
The R6 folder contains 11 platform screenshots and 7 older placeholders.
R7-R9 folders are empty until their corresponding results are saved.
Keep one or two overlapping rows between consecutive screenshots of a long table.

ARCHIVE
-------

archive/pre_cell_fix_pooled_rank/
    Historical R1-R5 screenshots generated with pooled multi-wave ranks.
    These results are provisional and should not be mixed with corrected runs.
archive/pre_cell_fix_pooled_rank.zip
    Compressed backup of the same 69 PNG files.
archive/obsolete_run_plan_placeholders/
    Preserved empty placeholders from the superseded R6-R9 mapping.

ACTIVE RUN ORDER
----------------

R6: r6_passive_gain_w5_keepzero
    Purpose: five-wave passive-gain main run; 2026-09-21 platform screenshots
    already saved here. The settings screenshot crops RUN_ID/WAVES, and the
    result-table layout differs from the current repo script.
    RUN_ID = "r6_passive_gain_w5_keepzero"
    WAVES = all five waves
    CORE_X_CHOICE = "passive_gain"
    KEEP_ZERO_PORTFOLIO = True
    BINS = (5, 3, 3)

R7: r7_passive_gain_w5_positive
    Purpose: five-wave positive-portfolio comparison.
    RUN_ID = "r7_passive_gain_w5_positive"
    WAVES = all five waves
    CORE_X_CHOICE = "passive_gain"
    KEEP_ZERO_PORTFOLIO = False
    BINS = (5, 3, 3)

R8: r8_passive_gain_w4_drop2024q3_keepzero
    Purpose: four-wave passive-gain check excluding 2024q3.
    RUN_ID = "r8_passive_gain_w4_drop2024q3_keepzero"
    WAVES = ["2024q2", "2024q4", "2025q1", "2025q2"]
    CORE_X_CHOICE = "passive_gain"
    KEEP_ZERO_PORTFOLIO = True
    BINS = (5, 3, 3)

R9: r9_passive_return_w5_positive
    Purpose: five-wave passive-return comparison on the R7 sample rule.
    RUN_ID = "r9_passive_return_w5_positive"
    WAVES = all five waves
    CORE_X_CHOICE = "passive_return"
    KEEP_ZERO_PORTFOLIO = False
    BINS = (5, 3, 3)

COMMON REQUIRED SETTINGS
------------------------

CELL_RANK_SCOPE = "within_wave"
CELL_RANK_METHOD = "average"
ZERO_PORTFOLIO_CELL_MODE = "separate_recorded_and_imputed"
SHOCK_PORTFOLIO_SCOPE = "usable"
ENFORCE_CONTROL_COMPLETENESS = True
SE_TYPE = "HC1"

SCREENSHOTS
-----------

00_settings.png
00b_user_shock_summary.png
00c_holding_zero_provenance.png
00d_cell_construction_audit.png
01_sample_funnel.png
01b_outcome_nonmissing_by_wave.png
02_main_rf_1.png
02_main_rf_2.png
02_x_coef_comparison.png
03_outcome_sample.png
04_cell_density_1.png
04_cell_density_2.png
05_residual_x_variation_1.png
05_residual_x_variation_2.png
06_balance_tests_1.png
06_balance_tests_2.png
07_detailed_rf_1.png
07_detailed_rf_2.png

For every run, capture 00_settings.png and 00d_cell_construction_audit.png first.
Do not interpret the regression output if either screenshot shows the old pooled
ranking or zero portfolios entering positive-portfolio quantile bins.

Expected audit pattern:
- R7/R9: only status=positive; up to 5 size bins, 3 risk bins, and
  3 expected-return bins within each included wave.
- R6/R8: status=positive plus status=zero_recorded and status=zero_imputed.
  Each zero status has one cell per wave and zero quantile-bin counts.
- For a wave retained in both R6 and R8, its positive-portfolio cell assignment
  should not change merely because 2024q3 is omitted: compare the
  assignment_hash values exactly.
