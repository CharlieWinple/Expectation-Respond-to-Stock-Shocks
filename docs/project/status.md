# 项目当前状态

截至 2026-11-03。这里只维护当前进展；过去的逐次状态见
[历史状态](history/status-history.md)，运行证据见 [运行日志](run-log.md)。

## 经营者主线

- [11032030 核验记录](results/sme_owner_formal_11032030.md) 已收到。目标编码修正，全持仓 Cell 有 4 项显著，涉及性别和城市。旧 11031630 的平衡结果仅作异常记录。

- 当前平台脚本：`scripts/analysis/04_sme_owner_formal.py`，13 cells，
  `sme_owner_formal_v1` / `owner_formal_gain_current_traits`。
- 此前正式报告：[11021235](results/sme_owner_formal_11021235.md)，66 行正式回归完整。
  此前 [11020220](results/sme_owner_formal_11020220.md) 有截断，作为历史部分报告保留。
- Notes 已按完整报告更新；2026-11-03 接收 holding/gain 两张正持仓 BASE
  截图（四个面板，N=12153），挂接11021235并替换原分位数图。零持仓汇总为9802/21955。
  尾部材料仍暂存缓存，不能解释为尾部稳健。
- 04 分布图已收到；截图未显示运行时间，精确分箱和本地重绘图现见 11031630。
  [提交及输出规则](../platform/sme-owner-formal.md)。
- 待核对 2024q4 教育标签、贷款利率编码；城市等平衡关联、完整案例选择以及历史
  尾部/波次敏感性仍限制因果解释。后台真实数据/在线模拟来源以各次解读确认为准。

## 其他保留工作

- 01：`sme_rf_v19_common_sample_audit`，core/tail/wave 三批均已收到。
  [报告索引](results/README.md) 保留所有主批次和稳健性结论。
- 03：雇员诊断第四轮；前四轮报告及各轮协议保留，不混用不同轮次规格。
- 02：旧经营者输入诊断，不能据此宣称与最新 01/04 样本完全一致。
- 基金数据当前使用 `nav_price_annotated_v1`；质量标记及外部数据入口见
  [数据说明](../../data/README.md)。

## 工作区管理

2026-11-03 已按 [结果工作流](artifact-workflow.md) 整理目录、结果和 Git 边界。
具体变动及核验见 [整理记录](workspace-maintenance.md)。本次未执行平台估计，
未改变模型或待整理事项，未提交或推送已有研究修改。
