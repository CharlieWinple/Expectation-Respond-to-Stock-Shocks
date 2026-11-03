# 经营者正式报告 11032030

2026-11-03 接收。PDF 共 19 页，印刷页 40–58/58 连续，页脚完成时间 18:04:59，版本 explicit balance targets v2。STATUS=COMPLETED、blocking issues=none，四块 203/114/133/146 行，末页出现 REPORT COMPLETE。后台真实数据或模拟来源未独立确认。[报告原件](../../../outputs/platform_runs/sme_owner_formal/run_11032030/source/output-11032030.pdf)；[哈希与来源](../../../outputs/platform_runs/sme_owner_formal/run_11032030/verified/metadata.json)。

**目标编码已修正。** 印刷页 52 的 T1–T4 分别为年龄、大学学历、企业年龄和公司注册；T5–T7 为性别，T8–T13 为城市，T14–T16 为行业，T17 为单列的雇员数。11031630 的行业类别错配已消失。全持仓 BASE 21,955 条、17,508 位经营者。16 个主要目标中 Raw/Wave 各 16 项有效，Cell 15 项有效。三个规格分别有 3/3/4 项原始 p<.05。Cell 显著项为性别编码 1、2 及三线、新一线城市。11 个结果样本的 Cell 检验均有至少一项显著。

| BASE Cell 目标 | 标准化系数 | 聚类标准误 | 原始 p |
| --- | ---: | ---: | ---: |
| 性别编码 1 | +.01466 | .007288 | .04432 |
| 性别编码 2 | −.01467 | .007294 | .04432 |
| 三线城市 | +.01729 | .008282 | .03685 |
| 新一线城市 | −.02714 | .008434 | .00129 |

报告按各检验样本的 SD(gain)/SD(trait) 标准化系数。新一线的 −.02714 表示收益相差一个样本标准差时，该指示变量条件预测值相差 −.02714 个自身标准差。城市和性别分类指标彼此相关，p 值未经多重比较调整。性别编码 0 在 BASE 只有 23 条，Cell 行标记聚类方差退化，p 缺失。旧正持仓报告与本轮均显示城市和性别关联，但两者的标准化尺度不同。不能据此量化主回归偏误或认证外生性。

逐结果样本 Cell 的显著项数按 Y1–Y11 顺序为 1、3、1、1、1、1、4、4、2、1、1，最大绝对标准化系数介于 .02329 与 .04688。控制变量完整性及各预期的非缺失条件决定每列样本。雇员数另有 36 个检验，均 p>.05；BASE 非缺失 N=21,838，Cell 系数 .003734，SE .01009，p=.7113。[BASE 全表](../../../outputs/platform_runs/sme_owner_formal/run_11032030/verified/base_balance.csv) · [结果样本汇总](../../../outputs/platform_runs/sme_owner_formal/run_11032030/verified/balance_summary.csv) · [雇员数](../../../outputs/platform_runs/sme_owner_formal/run_11032030/verified/employee_balance.csv)。

**正式回归与分布。** 印刷页 43–45 的 66 行回归延续前次正式结果，逐结果使用相同的共同样本。Owner 规格中，每万元被动收益对应 CPI 预期 +.3902 个百分点（p=.03652），原材料价格预期 −.5845（p=.004933），工资预期 −.3910（p=.07106）。其余八项 Owner 结果均 p>.10。Cell 可用样本 26,740 到 Owner 完整样本 21,955；4,785 条剔除中有 4,624 条涉及学历缺失。五波窗口和持仓快照审计均 PASS。[正式回归表](../../../outputs/platform_runs/sme_owner_formal/run_11032030/verified/formal_regressions.csv)。

印刷页 48–52 的 80 个分箱频数与 11031630 逐箱一致，每面板加总为正持仓 BASE 的 12,153 条。绘图 CSV 沿用核实频数、报告端点和等宽规则；两组 BASE 的区别是这里仅对正持仓画图。[频数表](../../../outputs/platform_runs/sme_owner_formal/run_11032030/verified/histogram_bins.csv) · [收益图](../../../outputs/platform_runs/sme_owner_formal/run_11032030/figures/owner_gain_histogram.pdf) · [持仓图](../../../outputs/platform_runs/sme_owner_formal/run_11032030/figures/owner_holding_histogram.pdf)。

本次保存原页和未经全文纠错的 OCR。新增 BASE、结果汇总及雇员表按原图转录，核对可估计 BASE 和雇员行的双侧 p 与系数/标准误的一致性。平台只公布了逐结果平衡的汇总，不能从中恢复每项特征的逐结果系数。
