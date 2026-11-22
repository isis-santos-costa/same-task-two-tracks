# TODO

_Last updated: 2026-11-22 · Release: v0.2.0 · Track A effort so far: 112h_

## Status
`CellSpec` shipped; the first cell runs on the new standard.

## Next (in order)

1. **refactor: apply `CellSpec` to every cell**
   - First step: restart the kernel, run setup, check the first converted cell.
   - Done when: all cells use `CellSpec`, a fresh Run All passes, and `len(COMPARISON) == 15`.

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

## Before recording or publishing
- `DEV.max_rows = 0`, `DEV.chart_dpi = 150`.
- `USE_MAIN_BRANCH = False` with the release tag in the secret.
- Update `CHANGELOG.md`, tag, publish.