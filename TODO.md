# TODO / Known issues

## Bugs

- **`NC_VARS` duplicate key** (`nbs/api/configs.ipynb`): `SMP_ID` appears twice — first mapped to `'id'`, then to `'smp_id'`. The second silently overrides the first. The `id` variable still exists in the CDL and the template; decide whether `SMP_ID` should map to `id` or `smp_id` and remove the duplicate.

- **Swapped lat/lon units and axis attributes** (`nbs/api/configs.ipynb`, `CONFIGS_CDL` around lines 377–398): `lon` is labelled `degrees_north`/`axis: Y`/`_CoordinateAxisType: Lat` and `lat` is labelled `degrees_east`/`axis: X`/`_CoordinateAxisType: Lon` — everything is inverted. Should follow CF conventions: lon → `degrees_east`, `axis: X`; lat → `degrees_north`, `axis: Y`.

- **"seal level" typo in CDL** (`nbs/files/cdl/maris.cdl`, 8 occurrences): `smp_depth` and `tot_depth` long-names read `"Sample/Total depth below seal level"` — should be `"sea level"`. Affects all four sample-type groups.

- **Wrong `standard_name` for `percentwt` in sediment group** (`nbs/files/cdl/maris.cdl`, line 374): uses `percentage_weight_of_biota_sample` — needs a sediment-appropriate name (or a custom token if no CF standard name exists).

- **Hardcoded dev paths in geotraces handler** (`nbs/handlers/geotraces.ipynb`, module-level lines 46–51): `fname_in` and `fname_out` are relative dev paths that break in distribution; `load_data` ignores its `fname` argument and always reads the hardcoded path. These module-level defaults must be removed or replaced with proper argument handling.

- **Duplicate function definitions in `utils`** (`nbs/api/utils.ipynb`): `download_files_in_folder` and `download_file` are each defined twice (lines 176/266 and 197/287 in the generated module). Remove the second copies.

- **TEPCO typo: `RemoveJapanaseCharCB`** (`nbs/handlers/tepco.ipynb`): class name misspells "Japanese". Rename to `RemoveJapaneseCB` or `RemoveJapaneseCharCB`.

## Handler fixes

- **TEPCO: `RemapVALUE_DL_DLV_CB` does three jobs** (`nbs/handlers/tepco.ipynb`): a single callback parses the value string, assigns the detection-limit flag, and optionally computes a DLV — three concerns in one. Split into `ParseValueTypeCB`, `AssignDetectionLimitCB`, and `ComputeDetectionLimitValueCB`.

- **TEPCO: magic unit ID in `ConvertToBqM3CB`** (`nbs/handlers/tepco.ipynb`): `UNIT = 1` is hardcoded with no explanation. Replace with a named constant (e.g. `UNIT_BQ_M3`) sourced from the LUT or `configs.py`.

- **GEOTRACES: module-level `phase` dict** (`nbs/handlers/geotraces.ipynb`, ~line 150): the `phase` mapping (e.g. `{'D': {...}}`) is defined as module-level data mixed with code. Move to `configs.py` or load from an Excel LUT alongside the other lookup tables.

- **OSPAR: missing docstrings** (`nbs/handlers/ospar.ipynb`): `NormalizeUncCB`, `RemapDetectionLimitCB`, and `ConvertLonLatCB` have no docstrings — intent must be inferred from code. Add one-line docstrings describing the transformation (e.g. "Convert DDMM.mmm to decimal degrees").

- **MARIS_LEGACY: `DropNAColumnsCB` conflates two NA semantics** (`nbs/handlers/maris_legacy.ipynb`): the callback mixes pandas `NaN` (missing data) with MARIS semantic NA (`id=0`, meaning "unknown/unclassified"). Split into `DropAllNaRowsCB` (pandas NaN) and `DropMarisUnknownCB(na_id=0)` (MARIS-specific).

## Cleanup / dead code

- **`CONFIGS_CDL` block in configs** (`nbs/api/configs.ipynb`): large dict already marked `# TO BE REMOVED` (generated module lines 289–648), plus commented-out `cdl_cfg`, `cdl_cfg()`, and `name2grp` references. Remove entirely once confirmed unused.

## Refactoring / improvements

- **Bundle LUTs inside the package** (`nbs/api/configs.ipynb`, `nbs/cli/`): move lookup tables and CDL into the package using `importlib.resources`; eliminate the `~/.marisco/` initialisation directory and the `maris_init` CLI command. This removes the network dependency at install time, makes `download_file`/`download_files_in_folder` redundant, and roughly halves `configs.py`.

- **Promote repeated handler callbacks to `callbacks.py`**: across the 5 existing handlers, several callbacks are either identical or trivially parameterisable. Factorising them shrinks every handler and makes the vocabulary available to new ones. Two phases:

  *Phase 1 — near-identical, move as-is:*
  - `RemapNuclideNameCB` (helcom/ospar have identical implementations) → move to `callbacks.py`, accept `fn_lut` + `col_name`
  - `AddSampleIdCB` (helcom/ospar/tepco all do `range(1, len(df)+1)` + `SMP_ID_PROVIDER`) → one callback parameterised on the source column name
  - `SelectColsOfInterestCB` (geotraces/tepco identical `__init__`, differ only in regex vs substring) → one callback with optional `use_regex` flag
  - `NormalizeUncCB` (helcom/ospar identical structure, same `fn_convert_unc` injection) → move to `callbacks.py` unchanged
  - `CastStationToStringCB` (helcom/ospar/maris_legacy identical) → move as-is

  *Phase 2 — same pattern, needs interface design:*
  - `ParseTimeCB` (ospar/tepco/geotraces/maris_legacy are all `pd.to_datetime(col, format, errors='coerce')` with minor variation) → generic `ParseTimeCB(col_src, col_dst, format, dest_grps)`; helcom's bespoke fallback logic stays in its handler
  - `WideToLongCB` (geotraces/tepco both `pd.melt`; geotraces adds regex column selection + dropna) → parameterisable with defaults
  - `ExtractUnitCB` / `ExtractFromPatternCB` (geotraces has 3 and tepco has 3 near-identical regex-extract callbacks; geotraces uses `[unit]` brackets, tepco uses `(unit)` parens) → one `ExtractFromPatternCB(pattern, dst_col)` replaces all 6

- **Replace raw group-name string literals with `NC_GROUPS`** (`nbs/handlers/helcom.ipynb`, `nbs/handlers/ospar.ipynb`): handlers contain 110+ (HELCOM) and 74+ (OSPAR) occurrences of bare string literals `'SEAWATER'`, `'BIOTA'`, `'SEDIMENT'`, `'SUSPENDED_MATTER'`. `NC_GROUPS` already exists in `configs.py` and is imported in `callbacks.ipynb` — handlers should use it to avoid typos and ease future renaming.

- **Introduce `GroupDispatchCB` base class** (`nbs/api/callbacks.ipynb`): 10+ callbacks in HELCOM and OSPAR repeat the same `for grp in tfm.dfs.keys(): if grp == 'SEAWATER': ... elif grp == 'BIOTA': ...` pattern. A `GroupDispatchCB(group_ops: Dict[str, Callable])` base in `callbacks.py` would replace all of them with a declarative dict of per-group operations.

- **Validate** in handlers that dataframe columns (uppercase) are all in the NC_VARS keys in nbs/api/configs.ipynb

## Features

- **INIS metadata source as Zotero alternative**: add support for fetching dataset bibliographic metadata from the IAEA INIS database (https://www.iaea.org/resources/databases/inis) as an alternative to Zotero.

- **TEPCO handler overhaul** (`nbs/handlers/tepco.ipynb`): TEPCO now exposes data via the RAMDAS API (https://radioactivity.nra.go.jp/en). Rewrite the handler to consume the API directly rather than parsing inconsistent flat files.

- **New handler: Casacuberta group / TITANICA** (`nbs/handlers/`): Nuria Casacuberta's group (ETH Zurich / Univ. Barcelona), world leaders in using long-lived radionuclides to trace ocean processes, are systematically publishing their datasets to the TITANICA Zenodo community (https://zenodo.org/communities/titanica). A dedicated handler (or family of handlers) is needed to ingest these datasets into MARIS. New datasets appear periodically so the process should support incremental updates.

- **New handler: ARPANSA / Ocean Decade proof of concept** (`nbs/handlers/`): collaborative initiative with ARPANSA (Australia) under the UN Ocean Decade programme to automate data transfer to MARIS and use MARIS as the front end for a national/regional marine radioactivity information system. This is a proof of concept that could serve as a template for other national bodies.

## Documentation

- **Handler-writing guide** (`nbs/handlers/`): no documented vocabulary of available callbacks and their contracts. A concise guide (or extended `CLAUDE.md`) is needed both for contributors and to enable AI-assisted handler authoring.

- **Embed SICP design principles into CLAUDE.md files**: `nbs/reference/sicp-design-memento.md` captures the design principles this codebase should follow. Progressively extract the most relevant principles as concrete, codebase-grounded rules into the appropriate `CLAUDE.md` files:
  - `nbs/api/CLAUDE.md` — abstraction level rules for callbacks (λ1, λ2: when to promote a callback; λ4: don't reach through the Transformer interface)
  - `nbs/handlers/CLAUDE.md` — handler composition rules (λ5: callback list as declarative pipeline; λ2: three-instances-before-abstracting rule; λ8: group names as data not strings)
  - Do this incrementally as each refactoring above is completed, grounding each rule in a concrete before/after example from the codebase.
