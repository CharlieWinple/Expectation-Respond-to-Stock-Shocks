# 03 · 2024Q2 雇员预期补充表诊断

目标是解释 11061530 的 3,555 条雇员问卷记录为什么全部匹配，但 GDP、房价、物价、利率各只有 5、0、9、2 条可编码。脚本版本为 `q2_employee_coverage_v1`。在新平台 notebook 中，依次将 03 的六个 CELL 各粘贴为一个单元并全部执行。只读 Q2 主问卷和 id3 补充表，无时长筛选、持仓筛选、控制或回归。不写中间表。提交整套流程；在线模拟用于验运行，后台报告才用于真实样本判断。

## 核验顺序

1. A 表先核对 employee 的 rows 和 matched。rows 计问卷记录，同编号重复的问卷行各计一次；distinct_keys 只计非空不同编号。缺编号计入 unmatched。v2_only、v3_only、both 应加总为 employee。owner 是明确经营者。addon_counts 单独描述原始补充表，repeated_keys 为出现超过一次的非空编号数。
2. B 表以已匹配问卷记录为分母。每个编号、每题先独立合并全部原始行，再把结果关联回问卷。核对 matched = empty + raw_nonempty，且 raw_nonempty = valid + uncertain + unknown + conflict + multiple。uncertain 涵盖字典内的不确定、不适用等非数值选项；unknown 为字典外非空标签；conflict 表示出现多个不同有效数值。重复同值、空白加一个有效值可保留。两种以上失败原因并存归 multiple。
3. C 表只对雇员总体和经营者报告。按每个编号的非空关注标记汇总，1/0 表示选中/未选，全部为空归 missing，有其他标记或同时出现 0 和 1 归 unresolved。各状态的 matched、raw_nonempty、valid 加总应与 B 表对应。只有原问卷说明或投放记录可以确认跳题规则。
4. D 表各标志可重叠，每项统计有该标志的匹配问卷记录数。recognized 表示至少有一个数值选项，包括有效零；最终有效数见 B 表。known_label 行是正式字典所列选项的问卷记录频数，同一编号同一标签只算一次。未知文本仅报告总数。reference 行依次对照雇员总数、匹配数及四个题目的有效数。若出现 DIFF，first_observable_difference 指出旧报告可比指标中最先不一致的一项；旧报告没有中间原因计数。每张表需有 END 标记，无 BLOCK，核对分页行数后再登记。

若有效答案主要损失在原字段全空，先查问卷适用人群和跳题说明；若集中于编码或重复记录，核对原始选项含义和补充表生成过程，再决定是否调整 05。本地补充 CSV 有 4,604 个唯一 seqno，历史平台审计有 14,876 行，seqno 与 submit_id 的关系未验证。本轮只用正式 id3 的 submit_id。

## 历史版本与验收

第 4 轮脚本可用 `git show 0c3e5ece98ba97448eb3c18a497610031ad8f4b9:scripts/diagnostics/03_employee_diagnostics.py` 复现。历史测试从该 Git 对象读取源代码，需有该提交的本地历史。

本地运行 `python -m py_compile scripts/diagnostics/03_employee_diagnostics.py`，再分别运行 `python tests/test_q2_employee_diagnostic.py`、`python tests/test_employee_round2.py` 和 `python tests/test_sme_employee_formal.py`。收到报告后登记来源、版本、四表覆盖和各题结论；首轮截图见[结果解读](../project/results/employee_q2_addon_run_001.md)，执行环境待确认。
