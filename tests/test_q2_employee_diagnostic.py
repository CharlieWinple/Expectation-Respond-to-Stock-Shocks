"""Exercise the actual notebook cells with synthetic tables and compare against 05."""
from pathlib import Path
import ast
import subprocess

import pandas as pd

from test_sme_employee_formal import environment


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/diagnostics/03_employee_diagnostics.py"


def test_q2_diagnostic():
    source = SCRIPT.read_text(encoding="utf8")
    # Compare the Q2 diagnostic against the five-wave formal revision it audited.
    historical = subprocess.check_output(
        ['git', 'show', '2a5007f:scripts/analysis/05_sme_employee_formal.py'],
        cwd=SCRIPT.parents[2], encoding='utf8')
    formal, _, _ = environment(historical)
    pairs = [
        ("empty", None), ("zero", "基本不变"), ("zero", None),
        ("same", "上涨5_以内"), ("same", "上涨3_5"),
        ("uncertain", "不清楚"), ("unknown", "private_text"),
        ("conflict", "基本不变"), ("conflict", "增长3_4"),
        ("mixed", "增长3_4"), ("mixed", "增长4_5"), ("mixed", "不适用"),
        ("mixed", "private_text"), (None, "增长3_4"),
    ]
    raw = pd.DataFrame(pairs, columns=["submit_id", "answer"])
    topics = ["gdp", "house", "cpi", "rate"]
    for i, topic in enumerate(topics):
        raw["macroeconomic_"+topic] = raw.answer.shift(i)
        raw["focus_"+topic] = ["0", "1", None, "1", "0", "X", "0"] * 2
    keys = raw.submit_id.drop_duplicates().tolist() + ["zero", "absent", "owner"]
    survey = pd.DataFrame({"submit_id": keys, "v1": "我不是小微经营者",
                           "v2": "作为小微经营户的雇员_帮助其收付款", "v3": "我在工作"})
    survey.loc[0, "v2"] = None
    survey.loc[1, "v3"] = None
    survey.loc[survey.index[-1], "v1"] = "我是小微经营者_我自愿参与本次调查"
    survey["v25"] = survey.submit_id.map({"zero": "基本不变", "same": "基本不变", "absent": "增长3_4",
                                              "mixed": "增长3_4", "unknown": "private_text"})
    survey["v26"] = None
    survey["v27"] = "增长3_4"
    survey["v28"] = "下降"
    survey.index += 10
    captured = []
    def read(table, cols):
        return (raw if "addExpectation" in table else survey)[cols]
    env = {"ant_read_data": read,
           "ant_print_all": lambda series, **kw: captured.append(list(series))}
    tree = ast.parse(source)
    assert not any(isinstance(n, ast.Name) and n.id == "getattr" for n in ast.walk(tree))
    tree.body = [n for n in tree.body if not (isinstance(n, ast.ImportFrom) and n.module == "marvel.AntPrint")]
    exec(compile(tree, str(SCRIPT), "exec"), env)
    assert env["PCT_DICT"] == formal["PCT_DICT"]
    ref = formal["resolve_2024q2_addon"](raw).set_index("submit_id")
    for topic in topics:
        current = env["question_keys"](env["addon"], topic).set_index("submit_id")
        expected = ref["macroeconomic_" + topic].map(formal["PCT_DICT"])
        pd.testing.assert_series_equal(current.value, expected, check_names=False, check_dtype=False)
    counts = env["match_rows"][0]
    assert counts[1] == sum(row[1] for row in env["match_rows"][2:])
    assert counts[2] == 1 and counts[5] == 2
    for group, topic, matched, nonempty, empty, *reasons in env["reason_rows"]:
        assert matched == nonempty + empty and nonempty == sum(reasons)
        if group in ["employee", "owner"]:
            parts = [r for r in env["focus_rows"] if r[:2] == [group, topic]]
            assert [sum(r[i] for r in parts) for i in [3, 4, 5]] == [matched, nonempty, reasons[0]]
    gdp = next(r for r in env["reason_rows"] if r[:2] == ["employee", "gdp"])
    assert gdp[4:] == [1, 3, 1, 1, 1, 1]
    assert all(len(call) <= 40 for call in captured)
    assert sum(call[0].startswith("END ") for call in captured) == 6
    assert "private_text" not in str(captured)
    for group, topic, mode, n, left, right, both, neither in env["source_rows"]:
        assert left + right + both + neither == n
        if mode == "raw":
            details = [r for r in env["overlap_rows"] if r[:2] == [group, topic]]
            assert details[0][-1] == both == sum(r[-1] for r in details[1:])
    gdp = [r for r in env["source_rows"] if r[:3] == ["employee", "gdp", "coded"]][0]
    assert gdp[4:7] == [2, 0, 3]
    assert ["employee", "gdp", "different_score", "different_or_multiple_labels", 1] in env["overlap_rows"]
    assert ["employee", "gdp", "same_label", "same_text", 2] in env["overlap_rows"]
    assert env["change_sign"]("0_1") is None and env["change_sign"]("下降0_1") == -1
    assert env["first_difference"] == "employee_rows"


if __name__ == '__main__':
    test_q2_diagnostic()
