# 脚本入口

| 脚本 | 用途与当前状态 |
| --- | --- |
| `analysis/04_sme_owner_formal.py` | 当前经营者正式报告；13 cells；新增暴露直方图待平台运行。见 [操作说明](../docs/platform/sme-owner-formal.md) |
| `analysis/01_sme_expectations_rf.py` | v19 共同样本识别审计；core/tail/wave 分别完整提交，三批历史结果均保留 |
| `diagnostics/03_employee_diagnostics.py` | 当前雇员第四轮诊断。见 [第四轮协议](../docs/platform/employee-round4-diagnostics.md) |
| `diagnostics/02_sme_expectations_diagnostics.py` | 旧经营者输入/样本诊断；不用于认证最新 01/04 样本一致 |
| `local/annotate_fund_nav_returns.py` | 当前完整 annotated 面板及精简上传文件构建 |
| `local/validate_fund_nav_annotated.py` | 当前基金面板校验 |
| `local/build_fund_total_return.py`、`local/build_fund_nav_screened.py` | 当前构建依赖的上游阶段，保留；旧单独交付不作为当前默认输入 |
| `local/audit_fund_manager_returns.py` | 基金公司公告外部核验 |
| `local/plot_owner_exposure_quantiles.py` | 从本地已核实汇总 JSON 重建 Notes 分位数图，无微观数据重建 |
| `local/read_report_ocr.ps1` | 对指定图片目录作 Windows OCR；输出不能替代原图校对 |

平台脚本遵守 [平台规则](../docs/platform/ant-platform-rules.md)，按 cell 标记依次复制，
完整运行和提交。普通本地 Python 不能替代平台真实数据执行。

本地结果路径遵循 [结果工作流](../docs/project/artifact-workflow.md)。从 Git 克隆后，
绘图等本地工具需要先从本地备份恢复对应运行的 `verified/` 输入；输出图本地保留。
OCR 用法：`powershell -File scripts/local/read_report_ocr.ps1 -ImageDirectory <图片目录>`。

本地语法检查使用 `python -m py_compile` 并显式传入修改的脚本。
合成数据检查位于 `tests/`，按修改范围运行对应脚本。
这些检查不提供真实样本数或估计证据。
