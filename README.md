# KPI Automation

This repository implements a lightweight automation system for generating
industrial KPIs based on parameters stored in an Excel workbook. The
architecture is modular and supports resuming after failures, deduplicating
requests, and logging every step of the process.

## Getting started

1. **Create a virtual environment** (if you haven't already):

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1       # Windows PowerShell
    # or source .venv/bin/activate        # macOS / Linux
    ```

2. **Install dependencies**:

    ```bash
    pip install -U pip
    pip install -r requirements.txt      # or use ``pip install .``
    ```

    The project currently depends on:
    - lmstudio (for LLM calls)
    - loguru (logging)
    - openpyxl (Excel I/O)
    - pyperclip (used elsewhere in project)

3. **Put your workbook** in `data/` and update `config.EXCEL_PATH` if
   necessary. The workbook must have a header row with at least the
   columns `Key Parameters` and `KPIs`.

4. **Run the script**:
    ```bash
    python main.py
    ```
    The script will process every sheet, fill in the `KPIs` column, and
    persist progress. Log output is written to `logs/app.log` (see
    `config.py` for settings).

## Architecture

- `utils/excel_manager.py` – wraps `openpyxl` to read/write cells, identify
  the relevant columns, and save the workbook incrementally.
- `utils/llm_prompt.py` – constructs the prompt that is sent to the LLM.
- `utils/llm_manager.py` – interfaces with the LMStudio model. The
  raw response is converted to a string and then parsed with `json.loads()`
  so that non‑serializable objects (e.g. `PredictionResult`) still yield
  valid JSON results.
- `utils/cache_manager.py` – a persistent file-backed cache that stores every
  normalized input seen across runs. Because the cache is loaded on startup
  and written after each new result, the script will never call the LLM for
  a previously processed parameter set.
- `main.py` – orchestrates the flow: iterates rows, handles null values,
  checks the cache, calls the LLM when necessary, writes results back to the
  sheet, and logs every action.

## Resuming and deduplication

- The script never re‑processes rows where the `KPIs` column already contains
  a value. That means you can rerun after a crash and only new rows will be
  computed.
- Before calling the LLM the script normalizes the JSON string from the
  `Key Parameters` cell (sorted keys) and looks it up in a persistent cache
  (`data/cache.json`). Previously seen inputs are returned immediately.

## Logging

Logs are produced by `loguru` and can be written to file and/or console as
configured in `config.py`. Each row processed is recorded with sheet name and
row index; errors are logged but do not halt the whole run.
