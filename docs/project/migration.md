# Migration Notes

The old project used dated version folders such as `scripts/20260827_v8/`.
This repository keeps the same research state but switches to git as the
version-control mechanism.

## What Was Kept

- Current v8 reduced-form script.
- Platform schema snapshot.
- Local copies of the two user-provided fund-level panel CSVs as schema/sample
  references.
- Project-level findings that remain valid.
- Ant platform constraints and data merge rules.

## What Was Not Copied

- Old temporary output images.
- Old `__pycache__` folders.
- Superseded script versions.
- Large literature PDFs.
- Claude-specific memory/session scaffolding.

## Mapping From Old To New

```text
../CLAUDE.md
  -> README.md
  -> docs/project/status.md
  -> docs/platform/ant-platform-rules.md

../TODO.md
  -> docs/project/status.md
  -> docs/project/run-log.md

../docs/KEY_NOTES.md
  -> docs/methodology/variable-definitions.md
  -> docs/project/findings.md

../scripts/20260827_v8/06_panel_and_reg_v4.py
  -> scripts/analysis/01_sme_expectations_rf.py

../data/addon/_schema.json
  -> data/schema/ant_tables_schema.json
```

## New Rule

Do not create a new dated folder for each iteration. Change the script in place
or create a clearly named new script, then commit the change with git.
