# TODO

_Last updated: 2026-11-26 · Release: v0.2.0 · Track A effort so far: 128h_

## Status
`CellSpec` fully applied: all cells running on the new standard.

## Latest
1.a refactor(notebook): applied `CellSpec` to every cell
1.b refactor(notebook): broke out `raw_data` from overloaded cells

## Next (in order)

1. **refactor: promote task prompts from comment to display**
   - First step: review all the task prompts commented out for full readability.
   - Done when: all tasks display a prompt first thing after their titles, before Raw Data display.

2. **chore(git): add `commit-msg` global hook (Conventional Commits, 50/72)**
   - First step: save `commit-msg` to `username/username/cfg/hooks/` and run `git config --global core.hooksPath <full-path-to-hooks>`.
   - Done when: `git commit --allow-empty -m "bad"` is rejected, and a valid message passes.

3. **feat(dq): add Uniqueness check**
   - First step: write `get_uniqueness_report(df, key_cols)` and one test table.
   - Done when: the cell records a snippet and output, and the table row shows both pills.

## Parked
- Move `get_prog_acr` and `identity.py` helpers to `id_convention.py`.
- `reconcile_tables`: duplicate target keys, `key_col` parameter, dtype note.
- Snippets-full; Track B.
- `build_reconciliation_report`: format numbers

## Before recording or publishing
- `DEV.max_rows = 0`, `DEV.chart_dpi = 150`.
- `USE_MAIN_BRANCH = False` with the release tag in the secret.
- Update `CHANGELOG.md`, tag, publish.
