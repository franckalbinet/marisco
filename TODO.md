# TODO / Known issues

## Bugs

- **`NC_VARS` duplicate key** (`nbs/api/configs.ipynb`): `SMP_ID` appears twice — first mapped to `'id'`, then to `'smp_id'`. The second silently overrides the first. The `id` variable still exists in the CDL and the template; decide whether `SMP_ID` should map to `id` or `smp_id` and remove the duplicate.

- **Swapped lat/lon units and axis attributes** (`nbs/api/configs.ipynb`, `CONFIGS_CDL` around lines 377–398): `lon` is labelled `degrees_north`/`axis: Y`/`_CoordinateAxisType: Lat` and `lat` is labelled `degrees_east`/`axis: X`/`_CoordinateAxisType: Lon` — everything is inverted. Should follow CF conventions: lon → `degrees_east`, `axis: X`; lat → `degrees_north`, `axis: Y`.

- **"seal level" typo in CDL** (`nbs/files/cdl/maris.cdl`, 8 occurrences): `smp_depth` and `tot_depth` long-names read `"Sample/Total depth below seal level"` — should be `"sea level"`. Affects all four sample-type groups.

- **Wrong `standard_name` for `percentwt` in sediment group** (`nbs/files/cdl/maris.cdl`, line 374): uses `percentage_weight_of_biota_sample` — needs a sediment-appropriate name (or a custom token if no CF standard name exists).

- **Hardcoded dev paths in geotraces handler** (`nbs/handlers/geotraces.ipynb`, module-level lines 46–51): `fname_in` and `fname_out` are relative dev paths that break in distribution; `load_data` ignores its `fname` argument and always reads the hardcoded path. These module-level defaults must be removed or replaced with proper argument handling.

- **Duplicate function definitions in `utils`** (`nbs/api/utils.ipynb`): `download_files_in_folder` and `download_file` are each defined twice (lines 176/266 and 197/287 in the generated module). Remove the second copies.

## Handler fixes

- **helcom** (`nbs/handlers/helcom.ipynb`): uses `SALINITY` and `TEMPERATURE` as DataFrame column names, but `NC_VARS` defines `SAL` and `TEMP`. These callbacks need to be updated to use the correct names.

## Cleanup / dead code

- **`CONFIGS_CDL` block in configs** (`nbs/api/configs.ipynb`): large dict already marked `# TO BE REMOVED` (generated module lines 289–648), plus commented-out `cdl_cfg`, `cdl_cfg()`, and `name2grp` references. Remove entirely once confirmed unused.

## Refactoring / improvements

- **Bundle LUTs inside the package** (`nbs/api/configs.ipynb`, `nbs/cli/`): move lookup tables and CDL into the package using `importlib.resources`; eliminate the `~/.marisco/` initialisation directory and the `maris_init` CLI command. This removes the network dependency at install time, makes `download_file`/`download_files_in_folder` redundant, and roughly halves `configs.py`.

- **Promote repeated handler callbacks to `callbacks.py`**: across the 5 existing handlers, several callbacks are either identical or trivially parameterisable. Factorising them shrinks every handler and makes the vocabulary available to new ones. Two phases:

  *Phase 1 — near-identical, move as-is:*
  - `RemapNuclideNameCB` (helcom/ospar have identical implementations) → move to `callbacks.py`, accept `fn_lut` + `col_name`
  - `AddSampleIdCB` (helcom/ospar/tepco all do `range(1, len(df)+1)` + `SMP_ID_PROVIDER`) → one callback parameterised on the source column name
  - `SelectColsOfInterestCB` (geotraces/tepco identical `__init__`, differ only in regex vs substring) → one callback with optional `use_regex` flag

  *Phase 2 — same pattern, needs interface design:*
  - `ParseTimeCB` (ospar/tepco/geotraces/maris_legacy are all `pd.to_datetime(col, format, errors='coerce')` with minor variation) → generic `ParseTimeCB(col_src, col_dst, format, dest_grps)`; helcom's bespoke fallback logic stays in its handler
  - `WideToLongCB` (geotraces/tepco both `pd.melt`; geotraces adds regex column selection + dropna) → parameterisable with defaults
  - `NormalizeUncCB` (helcom/ospar both inject `fn_convert_unc`, identical structure) → move to `callbacks.py` unchanged
  - `ExtractUnitCB` (geotraces uses `[unit]` brackets, tepco uses `(unit)` parens) → one callback with configurable regex

## Features

- **INIS metadata source as Zotero alternative**: add support for fetching dataset bibliographic metadata from the IAEA INIS database (https://www.iaea.org/resources/databases/inis) as an alternative to Zotero.

- **TEPCO handler overhaul** (`nbs/handlers/tepco.ipynb`): TEPCO now exposes data via the RAMDAS API (https://radioactivity.nra.go.jp/en). Rewrite the handler to consume the API directly rather than parsing inconsistent flat files.

- **New handler: Casacuberta group / TITANICA** (`nbs/handlers/`): Nuria Casacuberta's group (ETH Zurich / Univ. Barcelona), world leaders in using long-lived radionuclides to trace ocean processes, are systematically publishing their datasets to the TITANICA Zenodo community (https://zenodo.org/communities/titanica). A dedicated handler (or family of handlers) is needed to ingest these datasets into MARIS. New datasets appear periodically so the process should support incremental updates.

- **New handler: ARPANSA / Ocean Decade proof of concept** (`nbs/handlers/`): collaborative initiative with ARPANSA (Australia) under the UN Ocean Decade programme to automate data transfer to MARIS and use MARIS as the front end for a national/regional marine radioactivity information system. This is a proof of concept that could serve as a template for other national bodies.

## Documentation

- **Handler-writing guide** (`nbs/handlers/`): no documented vocabulary of available callbacks and their contracts. A concise guide (or extended `CLAUDE.md`) is needed both for contributors and to enable AI-assisted handler authoring.
