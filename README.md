# Same task, two tracks.

Each task is solved twice: 
* **Track A**: From first principles  
* **Track B**: With off-the-shelf libraries  

They are then displayed side by side, code and outputs.


## Workstreams

|                  | Status      | Notebook                |
|------------------|-------------|-------------------------|
| **Data Quality** | In progress | _link after publishing_ |
<!-- | Data Modeling | Planned | |
| Data Stack (many tracks) | Planned | |
| E2E workflow | Planned | | -->


## Repository layout

- `shared/`: Common utilities for convenient side-by-side comparison of Tracks (`views.py`, `cell_recorder.py`)
- `data-quality/`: Configuration, helpers, and cell records (`config.py`, `helpers.py`, `snippets`, `outputs`)


## Notebook

The accompanying notebook to this repo demonstrates the Data Quality workstream (WIP).
For stable and reproducible execution across all forks, it clones this repository at a pinned release tag.


## Definition of Done · Data Quality

_Target_: reference Data Quality syllabus completed (
[Coursera](https://www.coursera.org/specializations/data-quality-analyst-validation-debugging-and-monitoring), 
[DataKitchen](https://datakitchen.io/certifications/data-observability-and-data-quality-testing/)
), with each task solved twice: 
* Track A in pandas from first principles
* Track B with production tools (SQL · dbt)

_v1 ready when_: at least one task is complete in both tracks.
