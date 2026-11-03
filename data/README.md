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
