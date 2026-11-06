# === CELL 1: Q2 diagnostic configuration and helpers ===
"""Standalone pre-selection survey audit, version q2_employee_sources_v2."""
import pandas as pd
from marvel.AntPrint import ant_print_all, ant_read_data

VERSION = "q2_employee_sources_v2"
SURVEY = "frlab_sample_project_202405290032751511010004_v2_sme_sp_smesurvey2024q2_202512"
ADDON = "sme_id3_2024q2_addExpectation"
KEY = "submit_id"
REFERENCE = {"gdp": 5, "house": 0, "cpi": 9, "rate": 2}
ORIGINAL = {"gdp": "v25", "house": "v26", "cpi": "v27", "rate": "v28"}
# Direction-only choices carry no quantitative midpoint.
DIRECTION = {"上升": 1, "上涨": 1, "增加": 1, "提高": 1, "上调": 1,
             "下降": -1, "下跌": -1, "降低": -1, "下调": -1,
             "不变": 0, "持平": 0, "保持不变": 0, "基本不变": 0, "没有明显变化": 0}
REASONS = ["empty", "valid", "uncertain", "unknown", "conflict", "multiple"]

PCT_DICT = {
    "基本不变": 0, "增长20_以上": 25, "增长20_以内": 10,
    "降低20_以上": -25, "降低20_以内": -10,
    "增长10_以上": 15, "增长10_以内": 5,
    "降低10_以上": -15, "降低10_以内": -5,
    "下降3_以上": -4.0, "下降3_以下": -4.0, "下降0_3": -1.5,
    "增长0_3": 1.5, "增长3_4": 3.5, "增长4_5": 4.5,
    "增长5_6": 5.5, "增长6_8": 7.0, "增长8_以上": 9.0,
    "下降0_1": -0.5, "下降1_2": -1.5, "下降2_3": -2.5,
    "下降3_5": -4.0, "下降5_以上": -6.0, "降低5_以上": -6.0,
    "增长0_1": 0.5, "增长1_2": 1.5, "增长2_3": 2.5,
    "增长3_以上": 4.0, "上涨3_5": 4.0,
    "上涨3_以内": 2.0, "上涨5_以上": 6.0, "上涨5_以内": 4.0,
    "降低3_以内": -2.0, "降低3_5": -4.0,
    "上升0_1": 0.5, "上升1_2": 1.5, "上升2_以上": 2.5,
    "上升0_3": 1.5, "上升3_5": 4.0,
    "上升5_8": 6.5, "上升8_以上": 9.0,
    "上升0_5": 2.5, "上升5_10": 7.5, "上升10_15": 12.5,
    "上升15_30": 22.5, "上升15_以上": 22.5, "上升30_以上": 35.0,
    "下降0_5": -2.5, "下降5_10": -7.5, "下降10_15": -12.5,
    "下降15_30": -22.5, "下降15_以上": -22.5, "下降30_以上": -35.0,
    "没有明显变化": 0, "0_1": 0.5, "1_2": 1.5,
    "2_3": 2.5, "3_4": 3.5, "4_5": 4.5, "5_以上": 6.0,
    "不清楚": None, "不确定": None, "不适用": None,
    "关心但拿不准": None, "不适用_去年尚未工作": None,
}

def clean_text(series):
    return (
        series.astype("string")
        .str.strip()
        .replace({
            "": pd.NA, "NAN": pd.NA, "NaN": pd.NA, "nan": pd.NA,
            "None": pd.NA, "NULL": pd.NA, "<NA>": pd.NA,
        })
    )


def question_keys(addon, topic):
    """One record per nonmissing addon key. All nonempty answers must agree."""
    answer = addon["macroeconomic_" + topic]
    focus = addon["focus_" + topic]
    value = answer.map(PCT_DICT)
    flags = pd.DataFrame({
        KEY: addon[KEY], "raw": answer.notna(), "recognized": value.notna(),
        "uncertain": answer.isin([k for k, v in PCT_DICT.items() if v is None]),
        "unknown": answer.notna() & ~answer.isin(PCT_DICT),
        "yes": focus.isin(["1", "1.0"]), "no": focus.isin(["0", "0.0"]),
        "other": focus.notna() & ~focus.isin(["0", "0.0", "1", "1.0"]),
    })
    result = flags.groupby(KEY).any()
    values = value.groupby(addon[KEY])
    result["conflict"] = values.nunique().gt(1)
    failures = result[["uncertain", "unknown", "conflict"]]
    result["reason"] = "valid"
    result.loc[~result.raw, "reason"] = "empty"
    for reason in failures:
        result.loc[failures[reason], "reason"] = reason
    result.loc[failures.sum(axis=1).gt(1), "reason"] = "multiple"
    result["value"] = values.first().where(result.reason.eq("valid"))
    result["focus"] = "missing"
    result.loc[result.yes, "focus"] = "selected"
    result.loc[result.no, "focus"] = "unselected"
    result.loc[result.other | (result.yes & result.no), "focus"] = "unresolved"
    return result.reset_index()


def identity_groups(survey):
    nonowner = survey.v1.eq("我不是小微经营者").fillna(False)
    explicit = survey.v2.eq("作为小微经营户的雇员_帮助其收付款").fillna(False)
    working = survey.v3.eq("我在工作").fillna(False)
    return {
        "employee": nonowner & (explicit | working),
        "owner": survey.v1.eq("我是小微经营者_我自愿参与本次调查").fillna(False),
        "v2_only": nonowner & explicit & ~working,
        "v3_only": nonowner & ~explicit & working,
        "both": nonowner & explicit & working,
    }


def change_sign(label):
    if label in DIRECTION:
        return DIRECTION[label]
    if label.startswith(("上升", "上涨", "增长", "下降", "降低")) and label in PCT_DICT:
        value = PCT_DICT[label]
        if value is not None:
            return int(value > 0) - int(value < 0)
    return None


def emit(table, columns, rows):
    lines = [" ".join(map(str, row)) for row in rows]
    calls = []
    for start in range(0, max(1, len(lines)), 38):
        calls.append([f"{VERSION} {table} {start + 1}-{min(start+38,len(lines))}/{len(lines)} {columns}"]
                     + lines[start:start+38])
    calls.append([f"END {VERSION} {table} rows={len(rows)}"])
    if sum(len(line.encode("utf8")) + 10 for call in calls for line in call) > 42000:
        ant_print_all(pd.Series([f"BLOCK {table}: output budget"]), model_method="unique")
        return
    for call in calls:
        ant_print_all(pd.Series(call), model_method="unique")


# === CELL 2: Read raw survey and addon, preserve repeated submissions ===
survey_cols = [KEY, "v1", "v2", "v3", *ORIGINAL.values()]
addon_cols = [KEY] + [prefix + topic for topic in REFERENCE
                      for prefix in ["macroeconomic_", "focus_"]]
survey = ant_read_data(SURVEY, cols=survey_cols)[survey_cols].apply(clean_text)
addon = ant_read_data(ADDON, cols=addon_cols)[addon_cols].apply(clean_text)
groups = identity_groups(survey)
sizes = addon.groupby(KEY).size()
matched = survey[KEY].isin(sizes.index)
match_rows = []
for group, mask in groups.items():
    keys = survey.loc[mask, KEY]
    hits = int(matched[mask].sum())
    match_rows.append([group, len(keys), keys.isna().sum(), keys.nunique(), hits, len(keys)-hits])
employee_n = int(groups["employee"].sum())
employee_matched = int((groups["employee"] & matched).sum())

# === CELL 3: A - matching and duplicate key accounting ===
emit("A", "group rows null_key distinct_keys matched unmatched_incl_null", match_rows + [
    ["addon_counts", "rows", len(addon), "null_rows", addon[KEY].isna().sum(),
     "nonnull_rows", sizes.sum(), "distinct_keys", len(sizes), "repeated_keys", sizes.gt(1).sum(),
     "rows_on_repeated_keys", sizes[sizes.gt(1)].sum()]])

# === CELL 4: B - exclusive reasons among matched survey records ===
reason_rows = []
focus_rows = []
coding_rows = []
label_rows = []
reproduction = []
for topic, reference in REFERENCE.items():
    keys = question_keys(addon, topic)
    linked = survey[[KEY]].merge(keys, on=KEY, how="left", validate="many_to_one")
    # Only dictionary labels are releasable. Count survey records once per key/label.
    answer_col = "macroeconomic_" + topic
    labels = addon.loc[addon[KEY].notna() & addon[answer_col].isin(PCT_DICT),
                       [KEY, answer_col]].drop_duplicates()
    for group in ["employee", "owner"]:
        weights = survey.loc[groups[group], KEY].value_counts()
        totals = labels[KEY].map(weights).fillna(0).groupby(labels[answer_col]).sum()
        for label, count in totals[totals.gt(0)].items():
            label_rows.append(["known_label", group, topic, label, int(count)])
    for group, mask in groups.items():
        # Merge preserves left row order; masks are positional even for a non-default survey index.
        sample = linked.loc[mask.to_numpy(dtype=bool) & linked.reason.notna().to_numpy()]
        counts = sample.reason.value_counts().reindex(REASONS, fill_value=0)
        reason_rows.append([group, topic, len(sample), int(sample.raw.sum()), *counts.tolist()])
        coding_rows.append([group, topic, len(sample),
                            *[int(sample[c].sum()) for c in ["recognized", "uncertain", "unknown", "conflict"]]])
        if group in ["employee", "owner"]:
            for state in ["selected", "unselected", "missing", "unresolved"]:
                part = sample.loc[sample.focus.eq(state)]
                focus_rows.append([group, topic, state, len(part), int(part.raw.sum()), part.value.count()])
        if group == "employee":
            reproduction.append([topic, int(counts["valid"]), reference])
emit("B", "group topic matched raw_nonempty " + " ".join(REASONS), reason_rows)

# === CELL 5: C - focus and availability by topic ===
emit("C", "group topic focus matched raw_nonempty valid", focus_rows)

# === CELL 6: D - overlapping coding flags and comparison with 11061530 ===
checks = [["employee_rows", employee_n, 3555], ["matched_employee_rows", employee_matched, 3555]] + reproduction
first_difference = next((name for name, actual, expected in checks if actual != expected), "none")
comparison = [["reference", name, actual, expected, "MATCH" if actual == expected else "DIFF"]
              for name, actual, expected in checks]
emit("D", "group topic matched recognized uncertain unknown conflicting_numeric; reference field actual expected status",
     coding_rows + label_rows + comparison + [["first_observable_difference", first_difference]])

# === CELL 7: E - original versus addon coverage, prior to any regression filters ===
source_rows = []
overlap_rows = []
option_rows = []
for topic, column in ORIGINAL.items():
    answers = addon["macroeconomic_" + topic]
    addon_keys = question_keys(addon, topic)
    # Preserve all distinct labels for raw agreement; duplicate addon rows never multiply survey rows.
    label_sets = answers.dropna().groupby(addon[KEY]).agg(frozenset)
    addon_keys["labels"] = addon_keys[KEY].map(label_sets)
    paired = survey[[KEY, column]].merge(addon_keys, how="left", on=KEY, validate="many_to_one")
    for group in ["employee", "owner"]:
        frame = paired.loc[groups[group].to_numpy(dtype=bool)]
        original = frame[column]
        numeric = original.map(PCT_DICT)
        orig_ok = numeric.notna()
        if topic == "rate":
            orig_ok = original.dropna().map(change_sign).reindex(original.index).notna()
        addon_ok = frame.value.notna()
        for mode, left, right in [
            ("raw", original.notna(), frame.raw.eq(True)),
            ("coded", orig_ok, addon_ok),
        ]:
            source_rows.append([group, topic, mode, len(frame), (left & ~right).sum(),
                                (~left & right).sum(), (left & right).sum(), (~left & ~right).sum()])
        # Report only constrained option labels, never arbitrary respondent text.
        safe = original.isin(PCT_DICT) | original.isin(DIRECTION) | original.str.fullmatch(
            r"(?:上升|下降|增长|降低|上涨|下跌)?[0-9]{1,2}(?:_[0-9]{1,2})?(?:_以[上下内])?", na=False)
        categories = original.where(safe, "OTHER_UNREVIEWED").fillna("EMPTY")
        categories = categories.where(original.notna(), "EMPTY")
        for label, count in categories.value_counts().items():
            status = "empty" if label == "EMPTY" else "unreviewed"
            if label in PCT_DICT:
                status = "numeric" if PCT_DICT[label] is not None else "uncertain"
            if topic == "rate" and label in PCT_DICT and PCT_DICT[label] is not None and change_sign(label) is None:
                status = "rate_unit_unverified"
            if topic == "rate" and label in DIRECTION and label not in PCT_DICT:
                status = "direction_only"
            option_rows.append([group, topic, label, status, count])

        # Count every raw overlap, explicitly mark ambiguous or uncodable answers.
        comparisons = {}
        overlaps = frame.loc[original.notna() & frame.raw.eq(True), [column, "labels", "reason", "value"]]
        for left_label, labels, reason, addon_value in overlaps.itertuples(index=False, name=None):
            left_value = PCT_DICT.get(left_label)
            same_text = len(labels) == 1 and left_label in labels
            if reason != "valid":
                outcome = "addon_unresolved"
            elif topic == "rate":
                # Only explicit change labels establish a direction (bare rate levels do not).
                sign = change_sign(left_label)
                signs = {change_sign(label) for label in labels}
                if sign is None or None in signs or len(signs) != 1:
                    outcome = "rate_not_direction_comparable"
                else:
                    outcome = "same_direction" if sign in signs else "different_direction"
            elif left_value is None:
                outcome = "original_unresolved"
            elif same_text:
                outcome = "same_label"
            elif left_value == addon_value:
                outcome = "same_score_other_label"
            else:
                outcome = "different_score"
            key = (outcome, "same_text" if same_text else "different_or_multiple_labels")
            comparisons[key] = comparisons.get(key, 0) + 1
        overlap_rows.append([group, topic, "raw_overlap", "total", sum(comparisons.values())])
        overlap_rows.extend([group, topic, status, text_match, n]
                            for (status, text_match), n in sorted(comparisons.items()))
emit("E", "group topic mode N original_only addon_only both neither", source_rows)

# === CELL 8: F - paired answers and original option frequencies ===
emit("F", "paired: group topic comparison text_match N; option: group topic label status N",
     [["paired", *row] for row in overlap_rows] + [["option", *row] for row in option_rows])
