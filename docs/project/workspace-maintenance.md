# 工作区整理记录：2026-11-03

范围为本仓库；外部 CSMAR 数据工程未移动或修改。本次是文件与文档维护，
没有平台运行、新估计、模型变更、Notes 内容转移或 Git 提交/推送。
整理前已有未提交的研究修改，均保留；不把这些修改当成本次维护成果。

## 工作流与入口

先制定 [结果工作流](artifact-workflow.md)，再执行现有文件整理。
README、当前状态、脚本说明改为导航和当前任务入口，避免历史“待运行”误导。
历史 README 和完整历史状态移到 `docs/project/history/`，原有结论不删除，
只更新迁移后的文件路径。运行日志保留完整；不把旧诊断自动视为已失效。

## 文件变动

| 原位置 | 新位置 / 处理 |
| --- | --- |
| 根 README 中逐次运行历史 | `docs/project/history/readme-history.md`；根 README 重写为导航 |
| `docs/project/status.md` 的完整历史 | `docs/project/history/status-history.md`；状态页只维护当前进展 |
| `outputs/output-*.pdf`，12 份 | 对应 `outputs/platform_runs/<topic>/<run>/source/`，原文件名保留 |
| `outputs/owner_formal_11020220/`、`owner_formal_11021235/` | `outputs/platform_runs/sme_owner_formal/run_<报告编号>/` |
| `docs/project/results/*.json`，11 份，含未跟踪的新报告 JSON | 对应运行的 `verified/`；不再同步 Git |
| 结果解读 Markdown | 保留在 `docs/project/results/`，作为有来源与限制的说明文档；新增运行索引 |
| `data/panels/achived/` | `data/archive/legacy_panels/`，旧面板保留，修正目录拼写 |
| `outputs/platform_screenshots/README.txt` | `docs/platform/legacy-screenshot-layout.txt`，标明历史设置 |
| `tmp/pdfs/read_report_ocr.ps1` | `scripts/local/read_report_ocr.ps1`，改为图片目录参数，不再硬编码某批运行 |
| `tmp/pdfs/batch4_footers.png` | `outputs/archive/legacy_review/`，保留人工检查证据 |
| `tmp/notes_check/` | `outputs/note_build/review_1102/`，保留检查记录和一次性脚本 |
| Notes 旁的 aux/log/out/synctex | `outputs/note_build/legacy_aux/` |
| Notes PDF、分位数图、变量映射 xlsx、文献 PDF | 保留本地原位置，解除跟踪或忽略，避免破坏 LaTeX 与 schema 引用 |

既有报告目录的图像/OCR 平铺布局保留；本次统一运行入口及 source/verified，
后续新运行使用完整的 source/pages/ocr/verified/figures/scratch 分层。
历史轮次、失败/截断结果、上游基金构建脚本都保留，避免丢失诊断或构建依赖。

## 去重与证据保留

整理前逐文件登记 1,689 个文件的路径、大小与 SHA256。移动操作另有清单。
全局发现 8 组完全相同的文件；空文本提取、各轮辅助脚本、旧数值副本等保留其
运行上下文，不为节约少量空间而打断历史核验流程。

只删除两份可替代副本，共 16,949,240 字节（约 16.2 MiB）：

- `outputs/platform_screenshots/archive/pre_cell_fix_pooled_rank.zip`：逐项核对
  ZIP 的全部 69 个成员，均与仍保留的解压原图逐字节一致。
- `outputs/note_build/review_1102/Notes_Yanpeng.pdf`：与仍保留的
  `docs/notes/Notes_Yanpeng.pdf` 完全一致。

未删除原始报告、原始数据、不同规格结果或有人工检查价值的截图。
部分报告 11020220 由完整报告 11021235 补齐，但两份来源证据都保留。
没有重新开展 OCR 或重新验证经济结论；旧报告的真实性/识别限制仍然有效。

## Git 与检查

- `.gitignore` 覆盖本地输出、tmp、归档、数据、数值导出、图像、PDF、压缩包和
  编译缓存；schema JSON、代码、Notes 源稿/缓存和说明文档可正常纳入版本控制。
- 16 个原已跟踪的附件条目仅从索引移除，本地文件或迁移后副本仍在。
  Git 显示的删除是停止版本控制，不是删除本地研究证据。
- 已更新正文链接、JSON 来源路径、绘图输入路径及受移动影响的历史识别脚本。
  历史识别脚本仅做路径修复和语法检查，不重跑以免覆盖已人工核实的结果。
- 验证包括本地 Markdown 链接、Python/PowerShell 语法、分位数图实际重建、
  原始 PDF/数据哈希、Notes 与既有研究脚本保留、Git 忽略与空白检查。

本地审计目录为 `outputs/workspace_audit/2026-11-03/`：
`before.json`、`after.json`、`initial-git-status.txt`、`moves.json`、
`duplicates.json`、`deleted-duplicates.json`、`verification.json` 和
`preservation.json`。这些审计附件不提交 Git。

旧 Git 提交中仍存在过去提交过的附件；本次不重写历史。新的提交将反映停止跟踪，
只有推送该提交后 GitHub 当前版本才会体现。数据、原始报告、核实数字和 Notes
插图应从独立本地备份恢复，单独克隆代码仓库不能恢复完整研究档案。
