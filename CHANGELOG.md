# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-18

### Added


- `helpers` : Add versioning to orchestrating functions (`get_data_profiling`, `get_dq_tests_result`).
- `helpers` : Add **Data Imputation (⚠ use with caution)** functions.
- `helpers` : Add **Missing Data** analysis and synthesis functions.
- `helpers` : Add **Data Reconciliation** functions.
- `config`  : Add **Data Quality Tests** standards.
- `config`  : Add **Data Profiling** standards.
- `config`  : Add `@dataclass` `DevClass` called as `DEV.<feature_flag>`.
- `config`  : Add `VERSION_NOTES` as a tracker of orchestrating functions.
- `config`  : Add `INPUT_FILES`.
- overall   : Add `.github/pull_request_template.md` and `CHANGELOG.md`.
- overall   : Add `README.md`.

### Changed

- `helpers` : Improve `get_cell_meta` with a `show_title` flag.
- `config`  : Standardize `DQ_TESTS_CLASSES` (NULL, UNIQUE, RANGE, DOMAIN, FORMAT).
- `views`   : Display in the ToC tools by Track (A: pandas, B: SQL, dbt).

## [0.1.0] - 2026-11-03

### Added

- Add initial dual-track notebook architecture (Track A: First Principles in pandas; Track B: Production in SQL/dbt).
- Add shared theme configuration (`cfg/config.py`) and HTML table/chart styling helpers.

[Unreleased]: https://github.com/isis-santos-costa/same-task-two-tracks/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/isis-santos-costa/same-task-two-tracks/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/isis-santos-costa/same-task-two-tracks/releases/tag/v0.1.0