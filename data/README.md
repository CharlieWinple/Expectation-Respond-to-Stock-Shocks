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
