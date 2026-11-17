# Data References

This repository does not contain the full original platform data. Platform data
must be read on the Ant platform with `ant_read_data`.

Included local references:

```text
schema/ant_tables_schema.json
  Machine-readable schema snapshot extracted from the old project.

panels/panel-schemas.md
  Expected columns for the two user-provided fund-level production panels.
```

Do not commit full platform extracts or large panel files. Record schemas and
platform table names instead.

## Local-only files

- `小微调研变量映射表.xlsx`: local reference workbook; existing schema paths retained, excluded from Git.
- `sme_survey_2024q2_addExpectation.csv`: local supplement.
- `panels/*_nav_annotated_v1.csv`: current compact panel copies.
- `archive/legacy_panels/`: old panels, formerly `panels/achived/`.

External CSMAR project: `D:/wyp_Files/xx.Files/data/CSMAR_fund_202608/20260823 exp stock/`.
Its `outputs/fund_nav_upload/` contains compact upload files;
`outputs/fund_nav_annotated/` retains wider audit panels. These are external
paths, distinct from this repository's result directories. Table/version
conventions remain in `panels/panel-schemas.md` and `docs/project/run-log.md`.

## Jobsurvey schema

- [机读 JSON](schema/jobsurvey_tables_schema.json) / [字段清单](schema/jobsurvey_tables_schema.md)：2026-11-11 用户提供表名及四张截图，问卷字段来自就业调研变量映射表。含 portrait、fund_trade、fund_invest、consumption 和四波 survey。
- 问卷 v 字段类型未提供，保留 null；截图所列字段类型已逐项记录。已补充 fund_invest 六个字段；fund_trade 不能替代持仓表。


## Jobsurvey 选定变量及选项字典

本地详表：`outputs/jobsurvey_mapping/jobsurvey_variable_options.xlsx`；同目录保存变量映射、选项分布、连续变量摘要、家庭消费收入比合并分布CSV。覆盖103个波次字段组合，其中102组已有完整观察选项；Q2 v53仅覆盖信息。总748行选项含性别及城市等级，列出全样本和非空分母。数值仅本地保存，不提交Git。可用 `scripts/local/build_jobsurvey_descriptives.py` 重建CSV和Notes矢量图。

## Jobsurvey基金窗口收益（2026-11-16本地生成）

外部CSMAR工程 `outputs/jobsurvey_fund_returns/`：upload下lag1/lag2两份CSV各96,314行，分别87,375/86,706条可计算；完整192,628行及筛查证据在同目录。版本jobsurvey_nav_price_annotated_v1，单位百分点，尚未上传平台。[方法与核验](../docs/methodology/jobsurvey-fund-returns.md)；[上传字段](schema/jobsurvey_fund_returns_schema.json)。SME旧文件未覆盖。
