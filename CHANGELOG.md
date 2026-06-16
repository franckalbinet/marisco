# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.0] - 2026-06-16

### Breaking changes
- Removed `maris_init` CLI command and `~/.marisco/` setup directory — lookup tables and the NetCDF template are now bundled inside the package via `importlib.resources`; only `export ZOTERO_API_KEY=...` is required after `pip install`
- Removed `cfg()` function (previously read `~/.marisco/configs.toml`)
- Removed `base_path()` path helper
- Removed all per-LUT path helpers (`nuc_lut_path()`, `species_lut_path()`, etc.) — replaced by `lut_fname(key)` using `NC_DTYPES` keys (e.g. `lut_fname('NUCLIDE')`)
- `ZoteroCB` no longer accepts a `cfg` parameter — Zotero library ID (`ZOTERO_LIB_ID`) and API key (`ZOTERO_API_KEY` env var) are resolved internally
- Cache directory moved from `~/.marisco/cache/` to `~/.cache/marisco/`

### Refactoring
- Merged `NC_VARS` and `CSV_VARS` into a single source-of-truth dict `NC_CSV`; both are still exported as derived views
- Removed dead `nbs/api/inout.ipynb` (`write_toml`, `flatten_dict`, `read_toml` — no callers)
- Completed post-refactoring verification across all notebooks: callbacks, metadata, encoders, decoders, all handlers, all CLI notebooks, and reference docs

### Documentation
- Updated `nbs/api/CLAUDE.md`, `nbs/handlers/CLAUDE.md`, and `nbs/reference/guide.ipynb` to reflect new setup and API

---

## [1.0.11] - 2026-06-12

### Refactoring
- Completed `PerGroupCB` migration across all handlers (helcom, ospar, geotraces, maris_legacy); TEPCO is excluded — a new structured data source is now available and the handler will be redeveloped
- Extracted shared `ParseTimeCB` (ISO8601 string → datetime) to `callbacks.py`; removed duplicate definitions from geotraces and maris_legacy handlers

### Documentation
- Added "Writing a new handler" section to the data guide: handler anatomy, IMFA nomenclature pattern, curation rules reference table, and verification checklist

---

## [1.0.10] - 2026-06-01

### Maintenance
- Migrated to nbdev3

---

## [1.0.9] - 2025-10-06

### New Features
- HELCOM handler: added station name in output
- TEPCO handler: added variable-length string variable type (e.g. station name), unit conversion, and export-to-CSV renaming
- Added `SMP_ID_PROVIDER` field to trace back original data provider sample IDs
- Added `station` field across all groups in CDL

### Bugs Squashed
- Fixed HELCOM detection limit assignment logic
- Fixed TEPCO value, unit, detection limit, and uncertainty remapping from column names

---

## [1.0.0] - 2025-02-18

### New Features
- New CLI command `maris_nc_to_csv`: converts NetCDF files to CSV ready for MARIS DB import
- New CLI command `maris_db_to_nc`: converts MARIS DB exports to NetCDF
- New CLI command `maris_to_nc`: encodes raw handler output to NetCDF
- Added capability to encode string variables in NetCDF output

---
