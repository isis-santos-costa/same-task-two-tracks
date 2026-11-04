# Same task, two tracks.

Each task is solved twice: 
* **Track A**: From first principles  
* **Track B**: With off-the-shelf libraries  

They are then shown side by side, code and outputs.

## Workstreams

|                  | Status      | Notebook                |
|------------------|-------------|-------------------------|
| **Data Quality** | In progress | _link after publishing_ |
<!-- | Data Modeling | Planned | |
| Data Stack (many tracks) | Planned | |
| E2E workflow | Planned | | -->

## Repository layout

- `shared/`: Resources common to every workstream, building the Tracks comparison structure (`views.py`, `cell_recorder.py`)
- `data-quality/`: Configuration, helpers, and cell records (`config.py`, `helpers.py`, `snippets`, `outputs`)

## Integration

The Kaggle notebook clones this repo at a pinned commit or tag, for a stable execution of forks.
