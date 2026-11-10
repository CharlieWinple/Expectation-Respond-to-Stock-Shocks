# Note Cache

## 2026-11-05 — 答题时长门槛的综合发现（后续Notes整合入口）

本条综合下列逐次记录；旧条目中的候选门槛、四波设定或逐波省略描述为当时状态。当前规则为经营者180秒、雇员100秒，均含下限、缺失保留；05四项宏观预期已接入q2补充表，股票仍后四波。

| 经营者门槛 | 0秒 | 120秒 | 180秒（主口径） | 240秒 |
|---|---:|---:|---:|---:|
| 控制完整BASE | 28,338 | 25,658 | 21,955 | 17,952 |
| 相对0秒BASE损失 | 0% | 9.46% | 22.52% | 36.65% |
| 物价系数（原始p） | .2569（.1687） | .2560（.1767） | .3902（.03652） | .3965（.03508） |
| 工资系数（原始p） | −.1773（.4601） | −.2024（.4092） | −.3910（.07106） | −.3141（.1745） |
| 原料成本系数（原始p） | −.3212（.2237） | −.4153（.1130） | −.5845（.004933） | −.4483（.05435） |
| BASE Cell平衡原始p<.05项数 | 1 | 3 | 4 | 4 |

- **比较对象及证据。** 系数均为逐题共同样本的Cell FE＋经营者控制，gain以万元计、用户聚类CR1；BASE为用户—波次记录而非独立人数，也不是各题最终回归N。证据：[0秒11052040](../project/results/sme_owner_formal_11052040.md)、[120秒11041730](../project/results/sme_owner_formal_11041730.md)、[180秒11032030](../project/results/sme_owner_formal_11032030.md)、[240秒11051650](../project/results/sme_owner_formal_11051650.md)。完整44行主规格比较位于0秒报告归档的verified/main_comparison.csv。
- **回归证据对门槛敏感。** 0/120秒的11项主规格均p>.10；物价系数在0/120秒约.256，在180/240秒约.39。0与180秒的物价SE同为.1866，显著性变化主要伴随点估计变化，并非单纯精度改善。原料成本0→180秒同时有绝对系数增大和SE下降，240秒证据又减弱，不能概括为“越严格越好”。未拒绝零不等于证明无效应，跨门槛显著与否不同也不等于系数差已显著。
- **平衡没有随严格程度整体改善。** 0秒BASE仅新一线城市在Cell下5%显著，但各结果样本仍有1—3项显著；性别编码0的Cell检验方差退化不算通过。显著项计数受样本、标准误及相关多项检验影响，不能凭计数选择门槛；标准化关联的尺度也随样本改变。
- **时长筛选会改变构成，不只是减少N。** [06诊断11051401](../project/results/sme_duration_11051401.md)中共同四波B的经营者/雇员中位时长300/145秒；雇员60秒已对v2明示路径剔除24.08%、其余v3工作路径剔除4.76%，180秒还改变年龄、学历及持仓构成。现有质量代理为全零，不能证明被删问卷无效。若响应异质，保留人群及估计对象可改变；额外选择偏误属于可能机制，尚未直接证实。
- **门槛和样本构建的影响尚未分离。** 各次运行在筛选后的样本内重建波内cell，系数变化同时包含样本组成和分组边界变化；未进行固定参考cell、短时长组响应或正式系数差检验。控制缺失也持续造成大幅损失。不得将0→180秒的变化直接解释为清除无效问卷带来的因果识别改善。
- **雇员100秒的依据与限制。** 原四波分箱下，为匹配经营者五波B在180秒剔除22.22%，雇员插值门槛约97秒；双方共同四波匹配则约94秒。用户取100秒，原四波估计剔除23.86%，不是精确等比例或等质量保证。05扩为五波后须用新报告核实实际损失，不能沿用该四波估计。
- **写入Notes时的口径。** 保留经营者180秒、雇员100秒为用户确定的规则，经营者0/120/240秒完整报告为敏感性结果；现有证据尚未验证任一阈值为问卷质量断点。不根据回归p值继续选择门槛。各报告来源及实际提交commit的未确认状态、平衡表单位标题冲突沿用原解读；本次只更新缓存，不修改LaTeX。

## 2026-11-05 — 经营者0秒参照结果

- [11052040](../project/results/sme_owner_formal_11052040.md)已归档18页及66回归等核实CSV。无时长筛选36,153条，cell34,380、控制完整BASE28,338/22,149人；比180秒BASE多6,383条（29.07%）。控制完整性仍损失17.57%，主要涉及学历；q4物价1,990→598。
- 主规格Cell FE+经营者控制：11项原始p>.10；物价+.2569（SE=.1866，p=.1687）、工资−.1773（.2400，.4601）、原料成本−.3212（.2639，.2237）。物价0/120秒约.256，180/240秒约.39；0与180秒物价SE相同，差异主要伴随点估计变化。不能推断短问卷必定无效或系数差已显著。
- BASE Raw/Wave/Cell显著数0/2/1；Cell新一线城市−.01898（p=.03133）。各结果Cell仍1–3项显著，物价、工资、原料成本样本均有三线城市关联。提高门槛未呈现整体平衡改善。
- 0秒保留为参照，180秒主口径不改；跨阈值样本与cell参考排名同时改变，非固定样本/固定分组系数差检验。报告平衡表实际标准化，首页单位标题不一致；来源及提交commit未确认。未修改LaTeX。

## 2026-11-05 — 05全面参照04并纳入q2补充表

- 用户明确要求雇员使用补充表并全面对齐04。05 v2接入同表、同submit_id合并、同编码与逐题冲突置缺失规则；GDP/房价/物价/利率扩为五波，股票仍四波，不回填q2原年度或方向题。先前“补充表仅经营者”的说法没有覆盖证据，不再沿用；新增q2雇员匹配与四题有效人数审计，平台结果尚未返回。
- 时长100秒保留；年龄取消雇员独有16—100岁限制，教育混合标签不再推定专科，按04留缺失；未知教育记录审计、不阻断整轮。后四波各自题目字典保留，不能用经营者v-code替换雇员题。
- 移除05独有逐波省略检验。两者相同全持仓、10×3×3分组框架、逐题共同样本三规格、同期特征平衡、用户聚类CR1及Funnel；身份、时长、可用结果与个人/企业控制存在必要差异。相同框架不代表两组cell边界相同。
- 五波扩展后，先前雇员四波100秒约23.86%的插值不能作为新五波的实际损失率。新结果、q2覆盖和控制缺失均以平台报告为准。未修改LaTeX。

## 2026-11-05 — 雇员正式口径确定100秒

- 用户确认05雇员时长下限100秒，与04经营者180秒分别实施；均包含下限、保留缺失时长。05已修改，并在报告首页输出实际阈值，Funnel继续记录各步样本损失。平台100秒结果尚待返回。
- 上条等比例估算是规则选择参考，不是精确等比例保证：100秒雇员剔除约23.86%为分箱插值，经营者五波180秒剔除22.22%。同波比较或逐题完整案例的损失比例不同。旧条目中的“雇员尚未确定”描述由本条更新。
- 05沿用04全持仓、波内10×3×3 cell、逐题共同样本三规格与同期特征平衡框架；雇员四波五题、个人控制，另有逐波省略检验，不含分波持仓平衡或尾部删除。未修改LaTeX。

## 2026-11-05 — 经营者确定180秒；雇员等剔除比例门槛估算

- 用户决定经营者主口径180秒，04与运行说明已同步；120/240秒保留作敏感性结果。雇员尚未确定新阈值，05未改动。
- 依据[时长诊断11051401](../project/results/sme_duration_11051401.md)，以无时长筛选、完成基金/时点/历史覆盖及cell输入资格要求、尚未按控制变量或结果完整性筛选的B样本比较。经营者正式五波34,380条，180秒保留26,740条，剔除7,640/34,380=22.2222%。雇员四波10,308条，低于90秒1,924条、低于105秒2,727条；目标剔除约2,290.67条。在[90,105)秒803条内线性插值得96.8493秒，约97秒。
- 若为控制波次组成而双方均取共同四波，经营者180秒剔除5,263/25,367=20.7474%，对应雇员约94.0096秒。因此约95—100秒是当前分箱支持的近似范围；100秒在箱内均匀假设下预计剔除23.8585%，并非精确等比例。
- 证据：归档verified/hist_common4_B.csv及诊断阈值计数。15秒分箱不能给出97秒或100秒的精确剔除率，需平台逐秒/候选阈值计数核验；此处没有新增平台运行。分母为受访者—波次记录，不是独立人数。等剔除比例仅校准筛选强度，不证明无效问卷率相同，也不能排除身份路径、年龄或教育构成选择。未修改LaTeX。

## 2026-11-05 — 经营者240秒敏感性结果

- [11051650](../project/results/sme_owner_formal_11051650.md)报告确认240秒含下限、缺失保留。时长筛选36,153→22,913（剔除36.62%），cell输入21,825，控制完整17,952条/14,562人；较120秒BASE25,658少7,706条（30.03%），较180秒21,955少4,003条（18.23%）。
- 主规格为各结果共同样本的Cell FE加经营者控制，用户聚类CR1。物价+.3965（SE=.1882，原始p=.03508），与180秒+.3902（.1866，.03652）接近；120秒+.2560（.1895，.1767）。原料成本240秒−.4483（.2330，.05435），工资−.3141（.2313，.1745），均较180秒证据减弱。其余八项主规格p>.10。66行正式结果已保存。
- BASE Raw/Wave/Cell原始p<.05数量5/5/4，Cell仍有性别编码1/2、三线、新一线城市关联。物价样本的三线城市标准化关联+.0308，p=.02687。2024q4物价cell样本1,243→控制完整366，控制缺失仍突出。平衡表实际标准化，首页“原始单位”标题不一致，采用表内定义解释。
- 240秒只能提供门槛敏感性证据，不能据其物价显著判定质量或识别改善。样本构成与波内cell参考排名均随阈值变化，尚未进行固定参考cell或嵌套样本系数差检验。保留240秒为严格敏感性规格的建议未改变正式主口径，本地04仍120秒。后台/模拟来源及提交commit未独立确认，未修改LaTeX。

## 2026-11-05 — 时长诊断及路径选择

- 证据为[11051401](../project/results/sme_duration_11051401.md)，共同四波全持仓B，经营者/雇员中位时长300/145秒。经营者五波B在120秒保留31,298/34,380，损失8.96%；雇员60/120/180秒保留9,603/6,613/3,446，占10,308的93.16%/64.15%/33.43%。
- 雇员60秒也有路径选择，v2明示组1,109中剔除267（24.08%），其余v3工作组9,199中剔除438（4.76%）。180秒年龄37.23→40.06岁，已识别学历大学占比63.20%→51.75%。更长时间门槛不能简单解释为质量提高。
- 核心三题空白和路由异常全零，72项差异为zero_variance，不能表述为平衡通过。雇员<60秒的GDP/股价不确定率16.74%/22.13%，≥180秒37.12%/51.02%，仅描述，既不认证短问卷，也不否定不确定回答。
- 经营者120秒、雇员60秒仍是候选规则；建议保留无时长参照，并检查波次×路径答题负担。正式04/05阈值本次未调整，来源后台/模拟未独立确认。未修改LaTeX正文。
- **分布与口径。** B已满足身份、唯一性、提交时间、全持仓及收益/历史覆盖和cell输入要求，尚未要求控制与结果完整。共同四波经营者B为25,367条，时长P10/P25/P50/P75/P90为133/196/300/447/649秒；雇员B为10,308条，对应69/102/145/203/288秒。两类时长分布均已保存，[本地分布图](../../outputs/platform_runs/sme_duration/run_11051401/figures/duration_common4_B.png)及[核实分箱数据](../../outputs/platform_runs/sme_duration/run_11051401/verified/hist_common4_B.csv)可用于后续Notes。图按箱宽校正，仅展示0–900秒，CSV保留完整尾部。实际展示题量未知，不能仅凭题库长度或时长比例判定问卷无效。
- **筛选不等于单纯减小样本量。** 若剔除近似随机，主要代价是精度下降，并没有越严格越好的理由。若时长与年龄、学历、金融知识、答题路径或预期形成有关，门槛会改变保留人群及其权重。若不同人群对passive gain的反应存在异质性，估计对象可随门槛改变，即使组内识别成立。若答题时长同时受收益冲击及影响预期的未观测因素影响，条件化于时长还可能引入选择偏误；此为机制上的可能性，本轮没有证明该机制已经发生。已观察到的构成变化也不能直接等同于回归有偏，加入年龄学历控制未必能消除未观测选择。
- **240秒的含义。** 从共同四波经营者B的已核实分箱加总，低于240秒为8,988/25,367，即35.43%；低于180秒为5,263/25,367，即20.75%。240秒相对180秒再剔除3,725条，约占无门槛B的14.68个百分点。这是共同四波的门槛样本损失推算，不是经营者五波正式回归结果，也没有证实180–239秒问卷质量更差。
- **后续规格的建议，尚非用户确认的主口径。** 保留无时长筛选参照，与现有经营者120秒、候选雇员60秒并列比较；经营者240秒可作为严格敏感性规格，不能预设优于120秒。评价额外剔除者应依靠独立质量证据及人群构成变化，不能依据回归更显著、系数更稳定或答题更慢来选门槛。需同时权衡低质量回答减少、样本选择及精度损失。本次仅补充缓存，不调整正式脚本或LaTeX正文。

## 2026-11-04 经营者120秒：共同BASE增加3,703人次，三项预期信号减弱

时长合格28,144→32,951；控制完整BASE 21,955→25,658（20,200人）。CPI、工资、原料主规格系数+.2560、−.2024、−.4153，p=.1767/.4092/.1130。11项主规格均p>.10。BASE Cell仍有性别和新一线城市关联。两次估计不能单独鉴别短问卷质量。 [运行11041730及核对范围](../project/results/sme_owner_formal_11041730.md)。

## 2026-11-04 — Differences across waves (Owner controls)

Source: [October wave report](../project/results/sme_rf_v19_wave.md), Owner-controls specification C. Includes the eleven slope-equality tests and the comparison with omitting 2024q4.

```latex
\paragraph{Differences across waves.}
Estimate a separate passive-gain coefficient for each wave and test their equality. This assesses whether the association is stable across waves.

\begin{table}[H]
  \centering\small
  \setlength{\tabcolsep}{5pt}
  \caption{Equality of wave-specific gain slopes: owner controls.}
  \begin{tabular}{lr}
    \toprule
    Outcome & Wald p-value \\
    \midrule
    \texttt{exp\_stock} & 0.000002 \\
    \texttt{exp\_gdp} & 0.000422 \\
    \texttt{exp\_cpi} & $<0.000001$ \\
    \texttt{exp\_house} & $<0.000001$ \\
    \texttt{exp\_rate} & 0.000074 \\
    \texttt{exp\_env\_local} & 0.723476 \\
    \texttt{exp\_rev} & 0.595164 \\
    \texttt{exp\_market} & 0.571960 \\
    \texttt{exp\_price} & 0.171343 \\
    \texttt{exp\_wage} & 0.353597 \\
    \texttt{exp\_input\_cost} & $<0.000001$ \\
    \bottomrule
  \end{tabular}
\end{table}
\noindent Equal slopes are rejected for several outcomes. For example, 2024q4 coefficients are -47.907 (SE 4.515) for \texttt{exp\_cpi} and -37.527 (SE 6.033) for \texttt{exp\_input\_cost}, while omitting that wave barely changes the pooled estimates (0.390 to 0.390 and -0.585 to -0.578). A large wave-specific coefficient therefore need not drive the pooled result.
```

## 2026-11-03 — Owner sample sensitivity checks deferred from Notes

Positive-holder check: compare C/base with C/positive for each of the eleven outcomes in the [October core regressions](../project/results/sme_rf_v19_core.md). These estimates come from October. Complete-case selection: compare Available/Cell with Main/Cell for each outcome in the [November formal regressions](../project/results/sme_owner_formal_11021235.md). Each comparison holds its specification fixed. Overlapping missing-control counts and the q4 education-mapping caveat are retained below.

```latex
\paragraph{Sample comparisons.}
\begin{itemize}
\item \textbf{Missing controls.} Compare cell-only estimates before and after requiring nonmissing owner controls. Holding the specification fixed isolates sensitivity to the complete-case restriction.
\item \textbf{Zero-coded holdings.} Re-estimate owner controls among positive holders only. This checks sensitivity to including recorded-zero and unmatched-as-zero holdings; it does not validate treating unmatched holdings as zero.
\end{itemize}
\begin{itemize}
\item \textbf{Positive-holder check.} Owner-control estimates remain close to baseline: \texttt{exp\_cpi} 0.380 (SE 0.183; N=4,310), \texttt{exp\_wage} -0.388 (0.221; N=5,074), and \texttt{exp\_input\_cost} -0.576 (0.213; N=4,830). This addresses zero-exposure sensitivity, not missing holdings outside the platform.
\item \textbf{Complete-case selection.} Broad-to-common N falls from 9,016 to 7,723 for \texttt{exp\_cpi} and from 10,328 to 8,895 for \texttt{exp\_input\_cost}. Broad-sample cell-only estimates are 0.448 and -0.423, compared with 0.397 and -0.583 on the common sample. These differences reflect sample selection, not adding owner controls.
\item Requiring owner controls removes 4,785 observations (17.89\% of the cell base). College is missing for 4,624, city tier for 186 and age for 35; other controls are complete (counts overlap).
\item Selection is concentrated in 2024q4: \texttt{exp\_cpi} falls from 1,512 cell-eligible observations to 451 complete cases (70.17\% lost). The education audit for owner responses flags 4,946 missing or unmapped answers in that wave.
\end{itemize}
```

## 2026-11-02 — Owner tail analysis deferred from the current note

User requested moving tail analysis out of the active owner note. This is an
editorial deferral, not evidence that the estimates passed tail robustness.
Sources: [tail results](../project/results/sme_rf_v19_tail.md),
[core results](../project/results/sme_rf_v19_core.md). Preserve the original
mixed tail/wave block below for exact recovery; wave-omission rows remain active
in a separate table and must not be duplicated when restoring this material.
Capital/residual deletion coefficients, user-influence results, residual-SS
concentration and related concluding caveats are now cached. Ordinary raw-gain
and holding distributions remain in the note.

### Original refits and discussion (wave rows retained in the note)

```latex
\subsection{Actual deletion refits}
\noindent These are the October tail and wave results; the November run adds no deletion refits.
\begin{table}[H]
\centering\small
\setlength{\tabcolsep}{5pt}
\caption{Sensitivity of passive-gain coefficients: owner controls.}
\begin{tabular}{lrrrrr}
\toprule
\multicolumn{6}{l}{\textbf{Tail deletions}} \\[3pt]
Outcome & Baseline & \shortstack{Capital\\0.5\%} & \shortstack{Capital\\1\%} & \shortstack{Residual gain\\0.5\%} & \shortstack{Residual gain\\1\%} \\
\midrule
\texttt{exp\_cpi} & $0.390^{**}$ & $0.479$ & $0.620$ & $0.239$ & $-0.131$ \\
 & (0.187) & (0.400) & (0.489) & (0.535) & (0.687) \\[3pt]
\texttt{exp\_wage} & $-0.391^{*}$ & $-0.731^{**}$ & $-0.858^{*}$ & $-1.199^{**}$ & $-1.114$ \\
 & (0.217) & (0.346) & (0.443) & (0.545) & (0.684) \\[3pt]
\texttt{exp\_input\_cost} & $-0.585^{***}$ & $-0.234$ & $-0.803^{*}$ & $-0.260$ & $-0.142$ \\
 & (0.208) & (0.424) & (0.453) & (0.573) & (0.717) \\[3pt]
\midrule\multicolumn{6}{l}{\textbf{Wave omissions}} \\[3pt]
Outcome & \shortstack{Omit\\2024q2} & \shortstack{Omit\\2024q3} & \shortstack{Omit\\2024q4} & \shortstack{Omit\\2025q1} & \shortstack{Omit\\2025q2} \\
\midrule
\texttt{exp\_cpi} & $0.499^{*}$ & $0.195$ & $0.390^{**}$ & $0.434^{**}$ & $0.432^{**}$ \\
 & (0.272) & (0.186) & (0.186) & (0.195) & (0.205) \\[3pt]
\texttt{exp\_wage} & $-0.517$ & $-0.257$ & $-0.385^{*}$ & $-0.354$ & $-0.464^{*}$ \\
 & (0.319) & (0.193) & (0.216) & (0.234) & (0.239) \\[3pt]
\texttt{exp\_input\_cost} & $-0.786^{**}$ & $-0.348^{**}$ & $-0.578^{***}$ & $-0.638^{***}$ & $-0.592^{**}$ \\
 & (0.321) & (0.141) & (0.208) & (0.217) & (0.234) \\[3pt]
\bottomrule
\end{tabular}
\par\vspace{4pt}\begin{minipage}{\linewidth}\footnotesize User-clustered standard errors in parentheses. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$, using unadjusted two-sided p-values. Entries are passive-gain coefficients in RMB 10,000 units. Every column refits owner controls on the indicated sample.\end{minipage}
\end{table}
\noindent Capital tails use within-wave initial-amount cutoffs, retaining ties. Residual tails rank squared baseline residual gains, with deletion counts based on positive holders. Cells remain fixed; every scenario refits controls and clustered standard errors.
\begin{itemize}
\item \textbf{Tail sensitivity.} \texttt{exp\_cpi} changes sign after the 1\% residual deletion (-0.131, SE 0.687). \texttt{exp\_input\_cost} remains negative under all four tail deletions but loses precision; none has $p<0.05$. \texttt{exp\_wage} remains negative. Direction alone does not establish robustness.
\item \textbf{User influence.} Separately removing the two highest absolute-score users gives \texttt{exp\_cpi} 0.481 ($p=0.025$) and 0.329 ($p=0.074$). These are not cumulative deletions. Outcome-dependent rankings are diagnostics, not rules for selecting a preferred sample.
\item \textbf{Wave omissions.} The signs of \texttt{exp\_cpi}, \texttt{exp\_wage} and \texttt{exp\_input\_cost} survive every wave omission. Omitting 2024q3 lowers \texttt{exp\_cpi} from 0.390 to 0.195 ($p=0.293$). Omitting the unavailable q2 for \texttt{exp\_stock} adds no evidence.
\end{itemize}
```

### Deferred residual concentration diagnostics

```latex
\paragraph{Concentration of identifying variation.}
Residual gains remove cell effects and owner controls from passive gains. Their sum of squares (SS) measures the variation used to estimate the gain coefficient. The shares below describe its concentration; the deletion refits above assess sensitivity to the observations providing it.

\begin{table}[H]
  \centering\small
  \setlength{\tabcolsep}{5pt}
  \caption{Concentration diagnostics from the October main analysis.}
  \begin{tabular}{p{0.23\linewidth}p{0.34\linewidth}p{0.35\linewidth}}
    \toprule
    Check & Result & Limitation \\
    \midrule
    Top 1\% residual SS share & \texttt{exp\_cpi} 85.31\%; \texttt{exp\_input\_cost} 85.83\%. & Most variation comes from a small set of positive holders. \\
    Largest observation share & \texttt{exp\_cpi} 19.45\%; \texttt{exp\_input\_cost} 21.04\%. & Observation and whole-user influence differ. \\
    q2+q3 residual SS share & \texttt{exp\_cpi} 78.03\%; \texttt{exp\_input\_cost} 75.07\%. & Variation shares are not independent wave effects. \\
    After 1\% residual deletion & \texttt{exp\_cpi} retains 10.87\%; \texttt{exp\_input\_cost} 10.76\% of baseline SS. & Information declines sharply after tail removal. \\
    \bottomrule
  \end{tabular}
\end{table}
\noindent For \texttt{exp\_cpi} and \texttt{exp\_input\_cost}, the top 1\% accounts for about 85\% of residual variation, and 2024q2--q3 contribute about three quarters. Removing the residual tail leaves only about 11\% of baseline SS. Tail deletion therefore removes much of the variation supporting the baseline estimates.
```

### Original conclusions for context (non-tail limitations remain active)

```latex
\subsection{Conclusions and limitations}
\begin{itemize}
\item \textbf{Working conclusion.} \texttt{exp\_cpi} is a positive exploratory signal but is tail-sensitive; \texttt{exp\_wage} and \texttt{exp\_input\_cost} retain negative directions across the reported deletions, with limited precision. No broad causal wealth effect is established.

\item \textbf{Identification and support.} Portfolio choice and business shocks may jointly affect gains and expectations. Current traits are not all verified pre-shock. Cells can leave continuous within-bin differences. Current balance leaves city/gender associations, education completeness strongly selects the sample, identifying variation is highly concentrated, and slopes differ across waves.

\item \textbf{Measurement and inference.} Interval coding and inapplicable answers affect samples. NAV-price returns may differ from total returns; unmatched holdings need not mean zero wealth. User clustering leaves common-fund dependence unresolved.
\end{itemize}
```


## 2026-10-31 雇员第四轮结果（待整理）

证据：[第四轮结果](../project/results/employee_round4.md)，output-10302355.pdf打印21–40。
- 教育修复通过、issues=0；BASE5168条/4330人。事前教育999条/761人。
- C1纯5/3/3 cell较C缩小每波金额关联29%–38%，但每波仍显著且q3方向相反，
  pooled不显著不能视为完整平衡。C1小cell仅21条，前1%剩余SS仍82.958%。
- 房价/利率在C、C1原始p均<.05；C1房价2.5471(p=.017391)，利率.24108(p=.011372)。
  删除残差前1%后分别.95181(p=.76047)、-.081628(p=.75552)，精度下降，不能说效应为零。
- 保留用户确认的pooled当期雇员和纯cell主线；前期预期不作否决门槛，身份转移不扩展。
  建议下一轮预设更细金额cell并在实际结果样本检查平衡；未实施新脚本。
  共同基金依赖未修正，严格事前个人特征只覆盖重复子样本，当前为条件关联证据。


## 2026-10-30 用户确认：pooled雇员与纯cell主线

- 当期逐波独立按非经营者且(v2明示雇员或v3工作)取样，合并使用；追踪较弱，
  主分析不要求上期受访或雇员。重复用户仍采用用户聚类。
- 用户选择不引入连续控制，比较3/3/3与5/3/3的特征平衡、稀疏度和剩余变异。
- 身份转移降级，不作为进入正式回归门槛；第四轮不再运行身份转移回归。
- 前期预期相关可能含gain序列相关，不能单独否决规格；可观测特征不显著亦不证明外生性。
- 依据：2026-10-30本轮用户确认。边界：当期雇员受访样本、共同基金依赖未修正，
  pooling不自动消除当期选择。第四轮代码已实现，尚无新平台证据；不转入LaTeX。


This file collects material for `Notes_Yanpeng.tex` before a note-editing pass.

## Workflow

- When the user asks to save a new finding or an important conclusion, summarize it under **Pending items**. Preserve its date, evidence or source, interpretation, and any uncertainty that matters. Do not add it to the LaTeX note yet.
- When the user asks to organize the note, use the pending items here as the content to organize and polish for `Notes_Yanpeng.tex`. Do not pull in other conclusions on your own.
- After the note has been updated and checked, remove the transferred items from this cache. Keep this file and its workflow so it can be reused. If an item was not transferred, leave it here and say why.
- Platform run facts still belong in `docs/project/run-log.md`, and reusable findings still belong in `docs/project/findings.md`, as required by `AGENTS.md`. This cache tracks what the user wants incorporated into the note.

## Pending items

### 2026-10-30 Owner controls main; Full controls deferred from the active note

User decision: Owner controls is the main specification; Full controls remains a supplementary robustness exercise, deferred from the active note pending further independent balance assessment. This is not a claim that no diagnostics exist: the core archive contains portfolio-adjusted prior-trait checks and Full-controls own-prior checks, but they do not establish a complete specification-ranking exercise.

Preserve all existing Full-controls estimates, uncertainty, tail/wave sensitivity and the f_w construction below. Comparator rows are retained only to preserve context. Source: verified v19 core/tail/wave Markdown under `docs/project/results/`; JSON is local under each `outputs/platform_runs/sme_rf_v19_<batch>/run_001/verified/`. No estimates were rerun or discarded. The active note now uses Owner-controls diagnostics; its conclusions must not inherit Full-controls numerical claims.

Deferred full regression: Y_iw = beta * passive_gain_iw + gamma_c(iw) + x_iw' delta + f_w(P_iw) + epsilon_iw.

<details>
<summary>Deferred methods and previous result discussion (LaTeX source, with comparison context)</summary>

```tex
\paragraph{Wave-specific portfolio controls: $f_w(P_{iw})$.}
\begin{itemize}
\item \textbf{Cells and continuous controls.} Cells and $q_{iw}$ use the same three underlying characteristics: initial amount, historical risk and mean return. Cells use within-wave bins; $q_{iw}$ retains continuous values after transformation. Thus $f_w$ adjusts residual within-cell differences, allowing nonlinear and wave-specific relationships. It supplements coarse grouping rather than merely seeking a balance-test pass.
\item \textbf{Construction.} For positive portfolios, define $A_{iw}$ as portfolio amount under the analysis scope and
\[
q_{iw}=\bigl(\log A_{iw},\;100\sigma_{iw},\;100\mu_{iw}\bigr)',
\qquad z_{k,iw}=\frac{q_{k,iw}-\bar q_k}{s_k}.
\]
The full-control adjustment is
\[
f_w(P_{iw})=a_w'q_{iw}
+\sum_{k=1}^{3}\sum_{\ell=k}^{3}b_{k\ell,w}z_{k,iw}z_{\ell,iw}
+d_w\frac{A_{iw}}{10{,}000}.
\]
There are three linear terms, three squares, three pairwise interactions and one amount-level term per wave. The linear terms use $q$; the polynomial terms use standardized $z$.
\item \textbf{Why amount levels also enter.} Gain equals amount times portfolio return. If $R_{iw}=\bar R_w+\Delta R_{iw}$, then its common-return component is $(A_{iw}/10{,}000)\bar R_w$. Amount interacted with wave can absorb this component; log amount alone cannot do so exactly. This can also remove substantial identifying variation.
\item \textbf{Implementation.} Each term is multiplied by a wave indicator and entered jointly in OLS. Means $\bar q_k$ and scales $s_k$ are fixed using the five-wave eligible positive-portfolio reference, before outcome-specific filtering. They and cell assignments are not recomputed after deletions. Zero-holder design terms are set to zero within separate zero cells; this does not assign a literal zero historical risk or return. For positive holders, invalid inputs remain missing.
\item \textbf{Independent balance evidence.} OLS residual gains are mechanically orthogonal to included control columns in the fitted sample. Testing those same columns again is not independent evidence of balance. Informative checks instead examine strictly pre-shock traits or expectations not directly absorbed by the adjustment, on the relevant diagnostic sample. Failure to detect such associations supports the conditional comparison but does not establish random assignment of passive gains.
\end{itemize}

\subsection{Main coefficients and interpretation}
\begin{table}[H]
\centering
\small
\setlength{\tabcolsep}{5pt}
\caption{Passive-gain coefficients across control specifications.}
\begin{tabular}{lrrr}
\toprule
Outcome & \shortstack{Cell\\only} & \shortstack{Owner\\controls} & \shortstack{Full\\controls} \\
\midrule
\multicolumn{4}{l}{\textbf{Macro and local expectations}} \\[2pt]
\quad \texttt{exp\_stock} {\footnotesize ($N=4,346$)} & $-50.597$ & $-57.643$ & $-49.971$ \\
 & (61.550) & (61.105) & (62.049) \\[3pt]
\quad \texttt{exp\_gdp} {\footnotesize ($N=7,132$)} & $0.241$ & $0.197$ & $0.095$ \\
 & (0.268) & (0.265) & (0.250) \\[3pt]
\quad \texttt{exp\_cpi} {\footnotesize ($N=7,723$)} & $0.397^{**}$ & $0.390^{**}$ & $0.490^{**}$ \\
 & (0.187) & (0.187) & (0.199) \\[3pt]
\quad \texttt{exp\_house} {\footnotesize ($N=5,573$)} & $-1.780$ & $-1.854$ & $-2.189$ \\
 & (2.285) & (2.238) & (2.486) \\[3pt]
\quad \texttt{exp\_rate} {\footnotesize ($N=6,204$)} & $0.135$ & $0.147$ & $0.189$ \\
 & (0.107) & (0.109) & (0.138) \\[3pt]
\quad \texttt{exp\_env\_local} {\footnotesize ($N=11,252$)} & $0.048$ & $0.043$ & $0.076$ \\
 & (0.074) & (0.074) & (0.077) \\[3pt]
\multicolumn{4}{l}{\textbf{Firm expectations}} \\[2pt]
\quad \texttt{exp\_rev} {\footnotesize ($N=18,252$)} & $0.059$ & $0.049$ & $0.136$ \\
 & (0.438) & (0.450) & (0.535) \\[3pt]
\quad \texttt{exp\_market} {\footnotesize ($N=17,750$)} & $-0.557$ & $-0.592$ & $-0.448$ \\
 & (0.522) & (0.531) & (0.620) \\[3pt]
\quad \texttt{exp\_price} {\footnotesize ($N=8,490$)} & $-0.404$ & $-0.374$ & $0.069$ \\
 & (0.292) & (0.289) & (0.314) \\[3pt]
\quad \texttt{exp\_wage} {\footnotesize ($N=9,291$)} & $-0.389^{*}$ & $-0.391^{*}$ & $-0.395^{**}$ \\
 & (0.219) & (0.217) & (0.185) \\[3pt]
\quad \texttt{exp\_input\_cost} {\footnotesize ($N=8,895$)} & $-0.583^{***}$ & $-0.585^{***}$ & $-0.310^{*}$ \\
 & (0.205) & (0.208) & (0.178) \\[3pt]
\bottomrule
\end{tabular}
\par\vspace{4pt}\begin{minipage}{\linewidth}\footnotesize Notes: User-clustered standard errors in parentheses. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-sided, unadjusted). Each entry is the passive-gain coefficient from a separate outcome regression; gain is in RMB 10,000. The complete-case sample is fixed across columns within each outcome. Owner controls add personal/business characteristics; full controls also add wave-specific portfolio terms and portfolio amounts.\end{minipage}
\end{table}
\begin{itemize}
\item \textbf{\texttt{exp\_cpi}.} Cell-only and owner-control estimates are close (0.397 and 0.390); the full-control estimate is 0.490 (SE 0.199, $p=0.014$). Thus RMB 10,000 more passive gain is associated with 0.49 percentage points higher coded \texttt{exp\_cpi}.

\item \textbf{\texttt{exp\_wage}.} Owner-control and full-control estimates are similar (-0.391 and -0.395; full controls $p=0.033$). The coefficient concerns expected growth in average full-time pay.

\item \textbf{\texttt{exp\_input\_cost}.} The coefficient attenuates from -0.585 with owner controls to -0.310 with full controls ($p=0.082$), a 47\% reduction in magnitude.

\item \textbf{Other outcomes.} The remaining eight full-control estimates provide no clear overall response; imprecision does not imply zero effects.

\item \textbf{Sample selection.} Broad-to-common N falls from 9,016 to 7,723 for \texttt{exp\_cpi} and from 10,328 to 8,895 for \texttt{exp\_input\_cost}. Complete-case comparisons hold N fixed. Full-control positive-holder estimates are close to baseline: 0.481 for \texttt{exp\_cpi} and -0.295 for \texttt{exp\_input\_cost}.
\end{itemize}

\subsection{Actual deletion refits}
\begin{table}[H]
\centering
\small
\setlength{\tabcolsep}{5pt}
\caption{Sensitivity of passive-gain coefficients: full controls.}
\begin{tabular}{lrrrrr}
\toprule
\multicolumn{6}{l}{\textbf{Tail deletions}} \\[3pt]
Outcome & Baseline & \shortstack{Capital\\0.5\%} & \shortstack{Capital\\1\%} & \shortstack{Residual gain\\0.5\%} & \shortstack{Residual gain\\1\%} \\
\midrule
\texttt{exp\_cpi} & $0.490^{**}$ & $0.541$ & $0.714$ & $0.749$ & $0.721$ \\
 & (0.199) & (0.466) & (0.555) & (0.644) & (0.788) \\[3pt]
\texttt{exp\_wage} & $-0.395^{**}$ & $-0.413$ & $-0.251$ & $-0.966$ & $-1.089^{*}$ \\
 & (0.185) & (0.405) & (0.539) & (0.649) & (0.659) \\[3pt]
\texttt{exp\_input\_cost} & $-0.310^{*}$ & $0.021$ & $-0.241$ & $0.816$ & $0.690$ \\
 & (0.178) & (0.459) & (0.587) & (0.675) & (0.761) \\[3pt]
\midrule\multicolumn{6}{l}{\textbf{Wave omissions}} \\[3pt]
Outcome & \shortstack{Omit\\2024q2} & \shortstack{Omit\\2024q3} & \shortstack{Omit\\2024q4} & \shortstack{Omit\\2025q1} & \shortstack{Omit\\2025q2} \\
\midrule
\texttt{exp\_cpi} & $0.754^{**}$ & $0.375^{*}$ & $0.486^{**}$ & $0.484^{**}$ & $0.462^{**}$ \\
 & (0.323) & (0.213) & (0.199) & (0.201) & (0.208) \\[3pt]
\texttt{exp\_wage} & $-0.531$ & $-0.308^{*}$ & $-0.386^{**}$ & $-0.366^{*}$ & $-0.436^{**}$ \\
 & (0.324) & (0.170) & (0.184) & (0.197) & (0.196) \\[3pt]
\texttt{exp\_input\_cost} & $-0.380$ & $-0.263^{*}$ & $-0.302^{*}$ & $-0.356^{**}$ & $-0.276$ \\
 & (0.337) & (0.156) & (0.178) & (0.179) & (0.193) \\[3pt]
\bottomrule
\end{tabular}
\par\vspace{4pt}\begin{minipage}{\linewidth}\footnotesize Notes: User-clustered standard errors in parentheses. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-sided, unadjusted). Each entry is the passive-gain coefficient from a separate outcome regression; gain is in RMB 10,000. Columns identify the sample deletion; all regressions use full controls.\end{minipage}
\end{table}
\noindent\small Capital tails use within-wave initial-amount cutoffs, retaining boundary ties. Residual tails rank squared baseline residual gains; deletion counts use positive holders. Each scenario refits controls and fixed effects while keeping cell assignments and scaling fixed.\normalsize

\begin{itemize}
\item \textbf{Tail sensitivity.} Full-control \texttt{exp\_cpi} remains positive (0.541--0.749), but SE rises to 0.466--0.788 and all $p>0.19$. Owner-control \texttt{exp\_cpi} changes sign after the 1\% residual deletion (-0.131, SE 0.687). Full-control \texttt{exp\_input\_cost} estimates change sign across tail rules; \texttt{exp\_wage} estimates remain negative with owner or full controls.

\item \textbf{User influence.} Separately deleting the two highest absolute-score users gives full-control \texttt{exp\_cpi} 0.631 ($p=0.002$) and 0.410 ($p=0.033$). Scores depend on the outcome: these are diagnostics, not sample-selection rules. Both deletions retain positive \texttt{exp\_cpi} and negative \texttt{exp\_input\_cost}.

\item \textbf{Wave omissions.} The coefficient signs for \texttt{exp\_cpi}, \texttt{exp\_wage} and \texttt{exp\_input\_cost} survive every omission with owner or full controls. Removing 2024q3 lowers full-control \texttt{exp\_cpi} to 0.375 ($p=0.078$) and owner-control \texttt{exp\_cpi} to 0.195. \texttt{exp\_stock} has no q2 observations, so its q2 omission adds no evidence.
\end{itemize}

\subsection{Balance, concentration and wave heterogeneity}
\begin{table}[H]
\centering
\small
\setlength{\tabcolsep}{4pt}
\caption{Identification diagnostics and their limits.}
\begin{tabular}{p{0.23\linewidth}p{0.34\linewidth}p{0.35\linewidth}}
\toprule
Check & Result & Interpretation / limitation \\
\midrule
Prior investor traits & 4 of 110 tests have p<0.05. & Selected repeat respondents; no q2 prior coverage. \\
Own prior expectations & 22 checks; N=161--1,702. \texttt{exp\_house}: $p=0.008$ with owner controls; $p=0.604$ with full controls. & Earlier answer is a placebo outcome, not a same-target forecast revision. \\
Top 1\% residual SS share & Full-control \texttt{exp\_cpi} 81.92\%; \texttt{exp\_input\_cost} 82.90\%. & A small set of positive-holder observations supplies most variation. \\
Largest observation SS share & Full-control \texttt{exp\_cpi} 21.65\%; \texttt{exp\_input\_cost} 23.69\%. & Observation influence need not equal whole-user influence. \\
q2+q3 residual SS share & Full-control \texttt{exp\_cpi} 81.88\%; \texttt{exp\_input\_cost} 79.18\%. & Contribution shares are not wave-specific causal slopes. \\
After 1\% residual deletion & Remaining SS: \texttt{exp\_cpi} 9.67\%; \texttt{exp\_input\_cost} 9.32\% of baseline. & Lower concentration comes with a large information loss. \\
\bottomrule
\end{tabular}
\end{table}
\noindent Balance checks use strictly pre-shock age, college, firm age, registration and employment, with cell or portfolio adjustment. Four tests have $p<0.05$: age in the \texttt{exp\_rev}/\texttt{exp\_market} samples and firm age in the \texttt{exp\_market} sample. Prior expectations use the previous scheduled response, dated before the current shock; no backfill. Limited historical coverage prevents a general balance claim.

\begin{table}[H]
\centering
\small
\setlength{\tabcolsep}{4pt}
\caption{Equality of wave-specific gain slopes: unadjusted Wald p-values.}
\begin{tabular}{lrr}
\toprule
Outcome & Owner controls & Full controls \\
\midrule
\texttt{exp\_stock} & 0.000002 & 0.117086 \\
\texttt{exp\_gdp} & 0.000422 & 0.155219 \\
\texttt{exp\_cpi} & $<0.000001$ & $<0.000001$ \\
\texttt{exp\_house} & $<0.000001$ & 0.000007 \\
\texttt{exp\_rate} & 0.000074 & 0.001825 \\
\texttt{exp\_env\_local} & 0.723476 & 0.398896 \\
\texttt{exp\_rev} & 0.595164 & 0.750254 \\
\texttt{exp\_market} & 0.571960 & 0.232250 \\
\texttt{exp\_price} & 0.171343 & 0.143267 \\
\texttt{exp\_wage} & 0.353597 & 0.003018 \\
\texttt{exp\_input\_cost} & $<0.000001$ & 0.005469 \\
\bottomrule
\end{tabular}
\end{table}
\noindent The equality tests indicate wave heterogeneity. In 2024q4, full-control \texttt{exp\_cpi} is -47.768 (SE 6.365) and \texttt{exp\_input\_cost} -41.771 (SE 11.197). Yet omitting q4 barely changes pooled estimates (0.490 to 0.486; -0.310 to -0.302). These interaction slopes need support and influence checks before economic interpretation.

\subsection{Conclusions and limitations}
\begin{itemize}
\item \textbf{Working conclusion.} \texttt{exp\_cpi} is a positive exploratory signal; \texttt{exp\_wage} estimates show a consistent negative direction. \texttt{exp\_input\_cost} estimates are more control- and tail-sensitive. The evidence remains conditional association, not a general causal wealth effect.
\item \textbf{Identification.} Portfolio selection and business shocks may jointly affect gains and expectations. Current traits are not all verified pre-shock. Historical balance checks cover selected repeat respondents.
\item \textbf{Support.} Tail deletion removes about nine tenths of identifying variation for \texttt{exp\_cpi} and \texttt{exp\_input\_cost}. A large N therefore does not establish broad support. Wave heterogeneity further limits a common-effect interpretation.
\item \textbf{Measurement and inference.} Interval coding and inapplicable answers affect outcomes and coverage. NAV-price changes may differ from total returns. Unmatched holdings need not imply zero wealth, and user clustering leaves common-fund dependence unresolved.
\item \textbf{Next checks.} Audit answer mappings and q4 residual support; consider strictly pre-shock business-scale/profitability balance. Operating-cost and employment expectations are possible extensions after coding checks.
\end{itemize}

\noindent\small Sources: verified core, tail and wave outputs (10281700, 10291050, 10291330); definitions follow \textit{小微调研变量映射表.xlsx}. All 22 repeated baseline estimates match. Tables report rounded estimates; no new regressions were run.\normalsize



```
</details>


### 2026-10-30 — 雇员第三轮主回归与敏感性结果

- **证据：** `outputs/platform_runs/employee_round3/run_001/source/output-10292215.pdf`打印21–41，21页全部视觉审查；30辅助与
  126敏感性核心估计已保存并做p/CI/Holm核对。完成显示2026-10-29 21:56:57，
  issues=3。后台/模拟来源未独立确认。[完整结果](../project/results/employee_round3.md)。
- **更正教育结论：** 前两波实际混合标签含“高中”，q4起改为
  `大学专科_高职高专_技师学院`。上一轮识别将前两波文字泛化到了后续波次，修复
  因而不完整。第三轮gate阻断后三波；pre_college仅560条，排除混合类别394条，
  不能当成全四波平衡证据。需逐波补齐，混合类别继续保留假设/排除对照。
- **主结果：** BASE5168条/4330人，五预期N不变。全部10个C/F原始基线均无5%Holm
  显著；F-GDP=-.81421，原始p=.016391、Holm=.081953。九情景保持负号，尾部删除
  后SE增大；不是证明效应为零，也不足以定为因果发现。
- **选择与事前平衡：** C事前CPI经删尾部/删用户/逐波省略仍关联；F缓解但不精确。
  F身份选择九情景点估计均正，省略2025q2重点Holm=.037392；不能宣告选择风险消失。
  辅助单目标Holm与重点两目标Holm范围不同，必须标明，不能误当原始估计变化。
- **报告边界：** 90个当期情景仅5项通过各自Holm，不能跨情景挑显著结果。
  本轮不提供共同基金/市场暴露推断修正。下一步应优先教育修复和身份/可观察性设计，
  而非继续增加规格。此次不修改LaTeX或平台脚本。

### 2026-10-29 — 雇员第二轮诊断及正式识别前的剩余问题

- **证据：** `outputs/platform_runs/employee_round2/run_001/source/output-10292033.pdf`打印18–28，11页全部视觉审查，
  28辅助检验、25变异诊断及核对记录见[第二轮结果](../project/results/employee_round2.md)
  与相邻JSON。后台/模拟来源尚未独立确认；运行issues=0不等于识别通过。
- **口径落地：** v2明示雇员与v3工作互斥无冲突，后四波全部预期字典匹配。
  合格BASE5168条用户—波次、4330人，股票有效3162条，其余3545–3665条。
  当前正式操作口径不变，v9全职/兼职信息不能独立核实小微单位规模。
- **实现缺陷：** 教育实际`大学专科_高中_高职高专_技师学院`与脚本标签不符，
  该类被误记缺失；旧pre_college C/F不能用作平衡证据，须明确混合类别的归类假设、
  修复并新增未知标签审计。不能把全部教育缺失都归因于该问题。
- **识别限制：** C事前CPI beta=1.513、Holm=.0034179；F=.86463、CI跨零但精度低。
  F当期雇员身份beta=.18623、p=.042521，仅是既往雇员且当前非经营者受访者中的
  条件关联，不是就业因果效应，也不检查失访/转为经营者。
- **集中度：** F合并前1%观测贡献69.842%的剩余冲击平方和；q4单条贡献57.721%。
  这是解释变量变异贡献，不等于结果系数贡献。应做预定尾部、单用户和逐波敏感性。
- **下一步：** 可准备探索性主回归与上述诊断，不能宣称外生性已经验证。
  本次仅保存结果/结论，不修改LaTeX或平台代码。

### 2026-10-29 — 用户确认的小微雇员研究口径

- **研究对象与操作性定义（用户明确确认）：** 当前关注小微雇员。在 SME 问卷的非小微经营者分支中，将 `v2` 选择“作为小微经营户的雇员_帮助其收付款”或 `v3` 选择“我在工作”的受访者认作雇员。两条路径取并集（OR），不要求同时满足；不额外以工资题或预期题非空作为身份条件。
- **抽样背景（用户说明）：** SME 问卷面向使用收款码且达到一定流水条件的用户，入样本身不意味着是雇主或雇员。不能将全部非经营者直接认作雇员。
- **依据：** 本次用户口径确认；`outputs/platform_runs/employee_round1/run_001/source/output-10291620.pdf` 打印页16、18、20、22、25中的 v2/v3 实际选项。第一轮报告各波 v2 明示雇员数与 v3 工作人数之和等于工资题非空数，支持两条答题路径的推断，但边际数量不证明逐行互斥。详见 [第一轮审查](../project/results/employee_round1.md)。
- **解释边界：** 这是用户选定、后续采用的研究口径。v3“我在工作”本身没有完整区分受雇、自雇或其他就业形式，亦不单独验证所在单位是否属于小微；因此不将该操作性分类表述为对每个受访者雇佣关系与单位规模的独立核实。v9 可作后续描述和一致性检查，不自动增加为该口径的准入条件。
- **执行状态：** 本次仅存入 note cache，尚未修改平台脚本或 LaTeX。后续按此定义重算样本与诊断；原第一轮“非经营者候选”数量不能直接当成新口径的雇员数量。




### 2026-10-27 - v18 personal/business controls and sample-selection distinction

- Evidence: supplied two PDFs, printed pp.66-181; 198 verified outcome rows,
  22 primary sample rows, 48 prior-expectation rows in
  `docs/project/results/sme_rf_v18_person_business.md` and local JSON in `outputs/platform_runs/sme_rf_person_business/run_001/verified/`.
  Backend vs simulation provenance remains unconfirmed.
- Common-sample W5 T0/T1/T2 CPI .396781/.391928/.390245 and cost
  -.582763/-.575824/-.584515: selected personal/business controls have small
  incremental effects. W4 T2 attenuates to .195423/-.348084.
- Primary 5% Holm retains only W5 T0 cost (.048657), while T1/T2 cost are
  .059861/.054259; CPI W5 raw p around .034-.039 but Holm .339-.395. Do not
  choose T0 by significance or call controlled estimates causally established.
- CPI W5 N 9016 -> 7772 basic -> 7723 common; cost 10328 -> 8949 -> 8895.
  Missing education drives most losses. Broader M0 vs T0 differences reflect
  sample selection; T0/T1/T2 differences hold sample fixed.
- Supplemental CPI W5 W1-W3 survive outcome Holm; W3 cost is attenuated and
  raw-insignificant. Distinguish flexible portfolio adjustment from personal
  trait adjustment and their different samples.
- All 48 prior-check raw p>.18, Holm=1, on only 259-578 observations. Limited
  prior coverage is not an exogeneity certificate. Other balance/influence
  numbers remain OCR candidates pending item-level verification. No LaTeX edit.

### 2026-10-23 - v15 wave/control results and signed-balance qualification

- Source: local `outputs/platform_runs/sme_rf_wave_controls/run_001/source/output-10231150.pdf`, printed pp.60-71; verified
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

## 2026-11-06 雇员正式回归 11061530

雇员100秒，BASE 8,329 条；五项共同样本主规格均 p>.10。房价补充 Cell 的正关联随完整案例筛选减弱。2024Q2 补充表虽全匹配，共同样本仅有 GDP 1 条、物价 3 条。 BASE及五题 Cell 平衡均为0/10项显著；教育缺失和补充表有效覆盖限制外推。[报告与核验范围](../project/results/sme_employee_formal_11061530.md)。

## 2026-11-06 2024Q2 雇员补充表覆盖诊断

3,555 条雇员记录全部匹配。GDP、房价、物价、利率原字段非空数与最终有效数逐题相等，分别为 5、0、9、2；字典外标签、不确定和冲突造成的损失均为零。 此为平台补充表覆盖诊断；问卷投放和生成原因尚未确认。雇员回归主要覆盖后四波。[截图核验记录](../project/results/employee_q2_addon_run_001.md)。

## 2026-11-06 2024Q2 雇员预期双来源核验

雇员原表 GDP、房价、CPI、利率分别有 2,162、773、2,354、594 条现行可编码答案。补表独有可编码数为 0、0、2、1。GDP 五对中四对分值不同，CPI 七对均有分值差异，利率一对方向不同。 原表前三题为全年预期，利率为变化题。数据在回归前筛选阶段统计；此前 05 仅用补表，尚未按原表重估。[证据](../project/results/employee_q2_addon_run_002.md)。

## 2026-11-06 雇员预期正式口径：采用 2024Q3–2025Q2 四波

雇员五项预期的正式分析统一采用 2024Q3、2024Q4、2025Q1、2025Q2，排除 2024Q2。此选择基于各波题目所测预期的可比性。GDP、全国房价和 CPI 在 2024Q2 问的是 2024 日历年的增速，后四波问的是从答卷时点起未来 12 个月的增速。贷款利率在 2024Q2 问年内如何变化，后四波问未来 12 个月后、5 年期以上贷款的年化利率水平。股票方面，2024Q2 没有与后四波上证指数点位预期对应的题目。[逐波问卷映射](../../data/小微调研变量映射表.xlsx)

2024Q2 原问卷中确有可用的雇员答案。即使能从原表取数，预测期限和利率度量仍有上述差异。此前 11061530 按含 Q2 的旧口径运行；新四波口径的估计须以重新运行的结果为准。[原表与补表核验](../project/results/employee_q2_addon_run_002.md)；[旧口径回归记录](../project/results/sme_employee_formal_11061530.md)。

## 2026-11-10 雇员四波基准接收

[11101440](../project/results/sme_employee_formal_11101440.md)确认为四波100秒v3基准。BASE6,674，五项共同样本主规格均p>.10。房价宽样本Cell为2.905（p=.03621），完整样本Cell为.5763（p=.7007），加控制为.6055（p=.6852）。 与旧报告主系数在显示精度下一致，Q2旧口径本来仅贡献1条GDP与3条CPI。
