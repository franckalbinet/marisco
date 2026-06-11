# CLAUDE.md — marisco

## What this project is

**marisco** is a data curation tool developed at the IAEA Marine Environmental Laboratories (Monaco) for [MARIS](https://maris.iaea.org), the IAEA's open-access marine radioactivity repository.

**The problem it solves:** Marine radioactivity data comes from many providers — regional monitoring programmes (HELCOM, OSPAR), event-driven datasets (TEPCO data following Fukushima), individual research papers, and more. Each uses different file formats, nomenclature, units, and detection-limit conventions. MARIS ingests all of them into a single central database, but aligning them requires significant curation work.

**What marisco does:** It replaces a manual OpenRefine-based curation workflow with a reproducible Python pipeline. For each dataset, marisco:

1. Reads the raw provider data in whatever format it arrives
2. Aligns it to the MARIS data schema — standardising nomenclature, units, detection levels, and sample-type classification
3. Encodes the curated dataset as a self-contained **NetCDF4 file** that bundles measurements, variable metadata, lookup tables of used nomenclatures, and bibliographic global attributes in a single file
4. Can also export `.csv` files compatible with the existing OpenRefine → MARIS central-DB import pipeline

**How MARIS data is disseminated:** Via the web interface (https://maris.iaea.org), a data API, and as NetCDF files — marisco-generated NetCDF files feed all three channels.

## Critical rule — reading notebooks

**Never use `Read` on `.ipynb` files.** Use this tiered approach instead:

```bash
# 1. Locate a cell by symbol (Bash tool)
rg -n "sample_id" nbs/handlers/helcom.ipynb

# 2. View the relevant chunk by line range (Bash tool)
uv run python -c "from fastcore.tools import view; print(view('nbs/handlers/helcom.ipynb', (42, 65)))"

# 3. Broad survey — signatures only, no outputs (Bash tool)
uv run python -c "from toolslm.xml import folder2ctx; print(folder2ctx('nbs/api', sigs_only=True, out=False, file_re=r'.*\.ipynb', skip_folder_re=r'.*checkpoints.*'))"

# 4. Single notebook as clean XML (Bash tool)
uv run python -c "from toolslm.xml import nb2xml; print(nb2xml('nbs/foo.ipynb', out=False))"
```

Prefer scoped paths (`nbs/api`, `nbs/cli`) over full `nbs/` — handlers alone is 200KB, full tree is 387KB. Use full `nbs/` only when explicitly asked for a broad survey. See `nbs/CLAUDE.md` for full parameter reference.

## Critical rule — nbdev

**Never edit `.py` files in `marisco/`. They are auto-generated from notebooks.** All code lives in `nbs/`. After editing a notebook, run `nbdev_export` to regenerate modules.

Documentation follows the [`fastcore.docments`](https://fastcore.fast.ai/docments.html) convention: parameter documentation lives inline with the argument, not in a docstring body. nbdev picks these up automatically and renders them into the Quarto-based documentation site.

```python
def draw_n(n:int,        # Number of cards to draw
           replace:bool=True  # Draw with replacement?
          )->list:        # List of cards
    "Draw `n` cards."
```

Always use this style — inline `#` comments after type annotations — rather than numpy/Google-style docstrings.

## The four sample type groups

All measurements belong to one of four groups (also the NetCDF4 groups within each output file):

- `SEAWATER` — dissolved/filtered water samples (Bq/m³)
- `BIOTA` — marine organisms (Bq/kg wet or dry weight)
- `SEDIMENT` — bottom sediments (Bq/kg or Bq/m²)
- `SUSPENDED_MATTER` — suspended particles

## How the package works

Each data provider has a **handler** (`nbs/handlers/*.ipynb`). Every handler exposes an `encode(fname_out)` function that:

1. Loads raw provider data → `Dict[str, pd.DataFrame]` (one per sample type group)
2. Runs a `Transformer` with an ordered list of `Callback` objects that standardise the data
3. Feeds transformed data to `GlobAttrsFeeder` for NetCDF global attributes (bbox, time range, Zotero bibliographic metadata)
4. Writes output via `NetCDFEncoder`

## CLI tools

The CLI commands (`maris_init`, `maris_to_nc`, etc.) are defined in `nbs/cli/` and built with [`fastcore.script`](https://fastcore.fast.ai/script.html). The `@call_parse` decorator on a function generates the CLI entry point — arguments are inferred from the function signature. Entry points are declared in `settings.ini` under `console_scripts`.

## Setup

```bash
export ZOTERO_API_KEY=your_key_here
maris_init   # downloads template, lookup tables, creates ~/.marisco/
```

## Go deeper

- `nbs/handlers/CLAUDE.md` — handler pattern, column naming, how to add a new handler
- `nbs/api/CLAUDE.md` — core abstractions: Callback/Transformer, Remapper, configs, encoders
- `nbs/CLAUDE.md` — nbdev workflow, editing and building
