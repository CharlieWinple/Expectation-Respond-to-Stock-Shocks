# Stock Return, Expectations, and Outcomes

研究事前基金持仓产生的被动收益冲击与居民、小微经营者预期及实际行为的关系。
目前以小微经营者预期为主线，另有雇员诊断。

当前进展与待办见 [项目状态](docs/project/status.md)。正式经营者报告 11021235
已完整接收；04 的正持仓分布截图已补充归档并更新 Notes，精确分箱表及新增完整报告尚未收到。
结果来源和因果解释限制以各次报告解读为准。

| 入口 | 内容 |
| --- | --- |
| [脚本目录](scripts/README.md) | 当前分析、诊断与本地工具 |
| [识别设计](docs/methodology/identification.md) | 设计、识别边界及历史规格 |
| [变量定义](docs/methodology/variable-definitions.md) | 变量、单位与样本规则 |
| [平台规则](docs/platform/ant-platform-rules.md) | 平台接口与执行约束 |
| [结果工作流](docs/project/artifact-workflow.md) | 接收、读取、核验、保存、归档与 Git 边界 |
| [结果索引](docs/project/results/README.md) | 各次报告解读及本地附件入口 |
| [运行日志](docs/project/run-log.md) | 按运行保存的证据与核验记录 |
| [研究发现](docs/project/findings.md) | 可复用结论及限制 |
| [Notes 源稿](docs/notes/Notes_Yanpeng.tex) / [待整理缓存](docs/notes/note-cache.md) | 正式笔记与待纳入内容 |
| [数据入口](data/README.md) | 本地数据、外部 CSMAR 工程及 schema |
| [本次整理记录](docs/project/workspace-maintenance.md) | 移动、保留、去重和检查范围 |

```text
scripts/                 平台分析、诊断、本地构建与核验工具
tests/                   本地合成数据检查
docs/methodology/        方法与变量定义
docs/platform/           平台接口、运行操作、历史截图设置
docs/project/            当前状态、运行日志、发现、结果工作流
docs/project/results/    报告解读（完整 JSON 结果仅本地保存）
docs/project/history/    历史 README 与状态记录
docs/notes/              Notes 源稿与缓存；PDF/插图本地保留
data/                   数据说明与 schema；数据文件本地保留
data/archive/           旧面板，本地归档
literature/              文献说明；原始 PDF 本地保留
outputs/platform_runs/   按主题/运行编号存放报告及附件，本地保留
outputs/note_build/      Notes 编译和视觉检查，本地保留
outputs/workspace_audit/ 整理前后清单、SHA256 和移动记录，本地保留
tmp/                    一次性工作文件，本地保留
```

使用 Git 提交和 `codex/<topic>` 分支管理代码，不建立日期版本文件夹。
Git 同步代码、Notes 源稿、说明与方法文档；数据、数值导出、报告、图片、
编译产物和临时归档由独立本地备份保管。Git 历史中的旧附件本次不重写。

早期 README 和详细历史状态分别保存在
[历史 README](docs/project/history/readme-history.md) 与
[历史状态](docs/project/history/status-history.md)，其中的“当前”“待运行”仅指当时。
