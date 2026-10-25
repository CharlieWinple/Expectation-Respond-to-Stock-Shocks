# Note Cache

This file collects material for `Notes_Yanpeng.tex` before a note-editing pass.

## Workflow

- When the user asks to save a new finding or an important conclusion, summarize it under **Pending items**. Preserve its date, evidence or source, interpretation, and any uncertainty that matters. Do not add it to the LaTeX note yet.
- When the user asks to organize the note, use the pending items here as the content to organize and polish for `Notes_Yanpeng.tex`. Do not pull in other conclusions on your own.
- After the note has been updated and checked, remove the transferred items from this cache. Keep this file and its workflow so it can be reused. If an item was not transferred, leave it here and say why.
- Platform run facts still belong in `docs/project/run-log.md`, and reusable findings still belong in `docs/project/findings.md`, as required by `AGENTS.md`. This cache tracks what the user wants incorporated into the note.

## Pending items

### 2026-10-23 - v15 wave/control results and signed-balance qualification

- Source: local `outputs/output-10231150.pdf`, printed pp.60-71; verified
  tables in `docs/project/results/sme_rf_v15_wave_controls.md` and aggregate
  JSON archive under `outputs/platform_runs/sme_rf_wave_controls/run_001/`.
- Fixed 10/3/3 cells, common per-outcome M0/M1/M2 samples, W5/W4, 66 fits.
  W5 CPI beta .4480/.4548/.4444; W4 .3137/.3332/.3266. Cost W5
  -.4228/-.4345/-.4951; W4 -.1900/-.1812/-.3084. Positive CPI is relatively
  control-stable; cost is consistently negative but magnitude/inference depend
  more on wave selection and polynomial adjustment.
- Approximate Holm from rounded report p: only W5 M1 CPI crosses 5%
  (.049456); W5 M2 CPI/cost .059092/.068710. Do not choose M1 by this cutoff.
- Common-scale signed size-squared balance: 2024q3 -.1765; 2024q4 +.3315;
  2025q1 +.1120; 2025q2 +.2322, each CI excludes zero. This supports the
  concern that favorable pooled balance hides opposing within-wave dependence.
  Omitting q3 does not remove later-wave imbalance; polynomial inclusion is
  not an independent balance test. Next diagnostics should examine wave-specific
  adjustment and residual-gain influence without significance-based selection.
- Caveats: BASE/cell-only checks do not certify outcome samples or M1/M2;
  actual backend provenance remains unconfirmed; gain is NAV-price-based;
  common-fund dependence remains outside user clustering. Report p panels
  deduplicate some equal wave/p/note strings; no fabricated target-specific p.
  LaTeX note unchanged pending an explicit note-organization request.

### 2026-10-19 — C/D robustness results awaiting note integration

- Evidence: 10 images and 12 CSVs in external CSMAR outputs/platform_runs/sme_rf_cd_gain_only/run_001; see project findings for detailed values.
- Same-sample coarse cells substantially reduce sparse positive-holder groups. CPI beta .41247 (raw p .0244), cost -.43343 (.0382); neither passes Holm.
- Omitting 2024q3 with original fine cells attenuates cost to -.20951 (p .2105), CPI .11092 (.5357), wage -.16641 (.2966); GDP .51659 (.0342) also fails Holm.
- Compare each specification to archived v11 continuous-control results. These are exploratory associations and wave sensitivity, not a policy-effect design or proof of causal exogeneity. D diagnostics subsequently received: positive cells become sparser; residual gain SD remains positive and drops only about 4.1% for cost. Complete archive has 11 images and 15 CSVs.


### 2026-10-13 — 用户修订为只标记、不默认筛除（当前方案）

- **用户明确选择：** 主收益列保留可计算的未筛查单位净值收益，疑似事件与证据不足只作标记，平台默认不筛除。旧筛查结果另存，供敏感性比较。
- **实现：** `nav_price_annotated_v1` 保留全部行；主收益有值的 shock 为 110,806 条，control 为 1,250,865 条，其中 6,381 / 103,872 条不满足旧筛查。无有效端点的记录仍缺失；货币基金政策不变。
- **标记解释：** 净值关系中断、日跳变、日度覆盖/缺口、窗口幅度、日期与成立时间、币种、旧补丁分别标注。无日度证据不能写成“确认有事件”；净值关系标记为空表示不能判断或不适用。`shock_usable/ctrl_usable` 此时指收益可计算，不等于质量通过。
- **研究限定：** 恢复数值并未校正分红、折算、外币汇率或过旧端点，可能包括非财富收益的净值跳变。平台开关 `APPLY_NAV_QUALITY_SCREEN=False`，可设 True 比较严格样本；原有用户层面 12 月要求不变。尚未运行平台。
- **依据：** [标记标准与交付说明](../methodology/fund-nav-annotated.md)。本条替代上一条“默认排除”作为当前使用方案，历史记录保留。

### 2026-10-13 — 用户确认并实施的临时口径：单位净值增长率＋事件筛查

- **历史筛查版口径（已由上条取代）：** 普通基金改用 `NAV_end/NAV_base-1`；累计净值仅辅助每日事件筛查。每个窗口以固定基准检验加法差额稳定或乘法比例稳定，至少一种关系须贯穿全窗口，并检查日度披露覆盖、缺口与大跳变。历史分红/折算不直接导致基金被整体排除；疑似事件窗口收益置缺失，不填零。货币基金保留原收益与披露月规则。
- **解释限制：** 这是净值价格收益率；在无事件条件下才可当作总收益率。自动筛查不等于逐条人工确认，可能漏掉微小事件或误排复杂净值构造，仍有分红频率、基金类型等选择问题。
- **实际交付：** `outputs/fund_nav_screened/` 下两张完整 CSV，版本 `nav_price_screened_v1`。可用 shock 104,425/122,359，可用月度 control 1,146,993/1,266,578。相对旧现金 v1 分别净减少 970、75,352 条。完整 12 个月基金窗口由 93,035 降为 76,458（-17.82%），不是用户样本损失比例；平台 12 月与覆盖门槛不变。
- **反例回归核验：** 159915 的 2024 年 12 个月全部保留，包括下跌月；159925 的 2024-01 合并月被排除；110007/110008 的 2025-01 分红月被排除；000001、110022 的 2024 年月份均保留。货币基金逐条保持不变。实际 01/02 聚合函数通过权重、均值/风险、收益单位和缺失覆盖检查。
- **后续状态：** 01/02 已同步新表名与版本检查，旧面板保留。尚未上传运行平台或获得用户层面的样本与估计，先用平台诊断检查损失及构成，再决定是否补充持仓权重较高的事件信息。
- **证据：** [临时口径说明及逐波数量](../methodology/fund-nav-screened.md)；本地交付目录的 `support/coverage_by_wave.csv`、`control_completeness_by_wave.csv`、`new_loss_reason_counts.csv`、`representative_funds.csv` 和 `validation.json`。本条只作为方法演进记录；现行口径以上条“只标记、不默认筛除”为准。

### 2026-10-12 — Fund control 月度收益中的零值

- **发现（用户核查）：** Fund control 月度收益数据中有大量记录为 0，涉及货币市场基金。这些零值源于 CSMAR 的收益率计算问题，不能解释为基金真实收益率恰好为 0，也不能解释为收益率数据不可得。
- **整理时保留的限定：** 目前未记录具体零值数量、涉及的字段或基金范围；不要据此推断修正后的收益率或样本影响。

### 2026-10-13 — 货币基金月度收益的计算与跨月归属

- **处理口径（用户确认）：** 货币基金已使用每份收益计算月度收益。因周末或法定节假日而合并披露、跨越月末的收益，全部归入披露所在的下个月，不在两个月之间拆分。
- **项目记录：** `docs/project/status.md` 中的 “Posted-Month Money Return Rule Prepared” 记录了这一归属规则及当前数据交付状态；整理正式笔记时应保留该规则的适用条件。

### 2026-10-13 — 普通基金收益率指标的分母修正

- **方法调整（用户确认）：** 原指标用累计净值的变化率计算基金收益率，其分母为期初累计净值，包含历史分红；将这一收益率直接乘以按单位净值计价的持仓，不能正确得到持仓收益。重构后的指标保留累计净值的变化作为分子，将分母改为期初单位净值。
- **适用条件：** 现有 `docs/methodology/variable-definitions.md` 将该口径用于普通基金，并注明须满足基金份额单位稳定；货币基金另按每份收益计算。

### 2026-10-13 — 基金公司外部核验：分母修正的适用范围与折算反例

- **结论修正：** 上一条分母修正仅适用于累计净值确为“同单位净值 + 累计现金分红”的序列。仅当期份额稳定不够，历史折算也可能使累计净值处于不同的份额单位；不能概括为“累计净值作分母一定错误”。`cash_total_return_v1` 尚未通过通用口径外部核验，应先修正再用于正式估计。
- **无分红对照：** 110022 易方达消费行业 2024 年，原公式端点和新公式均为 4.2961%，官方 4.30%。000001 华夏成长历史有分红但 2024 年无分红，原公式 1.2261%，新公式 5.2497%，官方 5.25%，支持加法累计净值样本的修正。
- **期内分红：** 易方达稳健收益 A/B（110007/110008）2025 Q1，官方 2025-01-14 除息、每份分红 0.030/0.038 元。新公式 0.2696565%/0.3440045%，与公告分红和端点净值直接计算的现金持有收益一致。红利再投资重算为 0.2783117%/0.3567202%，官方 0.29%/0.37%；仍差 1.1688/1.3280 bp，超过单纯报告显示舍入容差，残差原因未查明，不能写成已完全复现官方。公告称“2024 年度分红”，但实际除息在 2025 年，事件应计入 2025 Q1。A/B 不算两个独立基金样本。
- **历史折算反例：** 159915 易方达创业板 ETF 于 2011-11-30 按 1.14558776 折算，累计净值近似为单位净值乘该系数。2024 年官方 13.98%，原公式 13.9818%，新公式却为 16.0172%。这不是当期分红或当期折算，直接反证简单分母替换的普适性。
- **期内合并反例：** 159925 南方沪深300 ETF 于 2024-01-26 按 0.503545799 合并。2024 Q1 官方 2.97%，原公式 2.9697%，新候选 2.6036%；按合并后份额 × 期末净值 / 期初净值还原为 2.9699301%，与官方一致。
- **已交付数据中的具体问题：** 159915 在 2024 年的 6 个正收益月被保留，6 个负收益月因“累计分红下降”规则被剔除；24Q4、25Q1、25Q2 的错误放大 shock 仍可用。这会造成涨跌方向相关的缺失。159925 则被净值单位筛查排除，未作为可用收益进入面板，但原收益可被官方事件解释，存在误删。修正需要基金层面的净值口径及事件识别，不能按当月涨跌筛选。
- **口径与限制：** 上述“原公式”是累计净值端点增长率；实际 CSMAR 四位小数月收益率复合值另见比较表。新公式年度/季度值为诊断候选，不冒充实际交付的可用聚合收益。核验共 5 只基金、6 个份额代码，不是随机抽样或全库影响评估；未运行平台回归，未外部核验货币基金。现金分红与官方业绩再投资口径须分开。
- **证据：** [详细核验报告](../methodology/fund-return-external-validation.md) 列出基金公司原始公告链接、PDF 物理页码、算法和局限。本地证据位于 `D:/wyp_Files/xx.Files/data/CSMAR_fund_202608/20260823 exp stock/outputs/fund_return_external_audit/`，含官方 PDF、页面图、`comparison.csv`、CSMAR 原始切片与实际 v1 面板切片。整理正式 note 时应将本条对上一条的限定一并写入。
