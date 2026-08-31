# Agent Instructions

Read this file before editing the repository.

## Project Posture

This is the git-based continuation of the old stock-expectations project. Do
not create new dated version folders such as `20260901_v9/`. Use git commits,
branches, and clear filenames instead.

## Before Editing

1. Read `README.md`.
2. Read `docs/project/status.md`.
3. For method changes, read `docs/methodology/identification.md` and
   `docs/methodology/variable-definitions.md`.
4. For platform scripts, read `docs/platform/ant-platform-rules.md`.

## Platform Script Rules

- Use `ant_read_data`, `ant_write_data`, `ant_print_all`, and `ant_plot`.
- Do not use ordinary `print()` in platform scripts.
- Do not use local file readers for platform data.
- Keep platform scripts split with `# === CELL N: ... ===` markers.
- Use `cols=` on table reads and `validate=` on merges.
- Run local syntax checks with `python -m py_compile` when possible.

## Data Rules

- Do not commit full platform extracts.
- Keep schema and table-name information in `data/` and `docs/project/run-log.md`.
- Treat platform output as the source of truth for sample sizes and estimates.

## Result Documentation

After every platform run:

1. Add the run information to `docs/project/run-log.md`.
2. Move reusable conclusions to `docs/project/findings.md`.
3. Commit script changes and result notes together when they belong to the same
   run.
