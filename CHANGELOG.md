# Changelog

<!-- do not remove -->

## 1.9.2

### New Features

- [FRAM STRAIT] Extend fram strait handler data coverage to 2002-2025 ([#56](https://github.com/franckalbinet/marisco/issues/56))


## 1.9.1

### New Features

- Improve doc layout and make docstrings consistent ([#55](https://github.com/franckalbinet/marisco/issues/55))


## 1.9.0

### Breaking Changes

- Rebuild CLI tools on the unified handler interface ([#52](https://github.com/franckalbinet/marisco/issues/52))
- Unify handler interface (encode signature, status, docstring) ([#51](https://github.com/franckalbinet/marisco/issues/51))

### New Features

- Update README Quick start and Documentation sections ([#53](https://github.com/franckalbinet/marisco/issues/53))


## 1.8.1

### New Features

- Remove redundant `grps` declarations on single-group PerGroupCB handlers, and document that it's optional ([#50](https://github.com/franckalbinet/marisco/issues/50))

### Bugs Squashed

- Testing multiple labels ([#49](https://github.com/franckalbinet/marisco/issues/49))


## 1.8.0

### New Features

- `fram_strait2025` handler: add detection limit (MDC) to the ingestion pipeline
- Add `data/` folder with example MARIS inputs (NetCDF + CSV) pending a proper INIS file-sharing mechanism
- Add how-to guide for opening and reading marisco-generated NetCDF4 files
- Show first rows of the MARIS CSV ready for MARIS DB import; clarify callout boxes to data provider and make LAB id assignment more explicit

### Bugs Squashed

- Fix U-238 conversion (ppb → atoms/kg) in the `jois` handler
- Revert HELCOM handler to running with all data instead of sub-sampled

## [1.7.0] - 2026-07-27

### Added
- `fram_strait2025` handler: ingests the FS2025 I-129 seawater record from Zenodo into MARIS-standard NetCDF4

## [1.6.1] - 2026-07-15

### Fixed
- `AddSampleIDCB`: whole-number float provider IDs (e.g. `289.0`) are cast to `Int64` before stringification, so `SMP_ID_PROVIDER` reads `"289"` instead of `"289.0"`

## [1.6.0] - 2026-07-02

  ### Changed
  - Refactored `netcdf2csv` module into a simpler, cleaner `nc2csv` module
  - Removed obsolete modules and fixed downstream implications across handlers

## [1.5.0] - 2026-06-29

### Added
- `jois` handler: ingests four years (2021–2024) of JOIS seawater radionuclide measurements (I-129, U-236, U-238, U-236/U-238) from the Beaufort Sea (CCGS Louis St. Laurent expeditions)
  - `load_data`: fetches ZIP archives from Zenodo, normalises column names, applies scale factors, and concatenates all years into a single `SEAWATER` DataFrame
  - `norm_cols` / `extract_scales` / `apply_scales`: scale-factor helpers handling inconsistent `( x 10^N)` suffixes across years
  - `RenameNucColsCB`: aligns `U238_ppb` and `U236_U238` column names to `{Nuclide}_{Unit}` pattern before melting
  - `RenameColsCB`: maps provider CTD columns to MARIS standard names (`LAT`, `LON`, `SMP_DEPTH`, `TEMP`, `SAL`, etc.)
  - `ParseDateTimeCB`: combines separate `Date` and `Time` columns into a single `TIME` column
  - `MeltJOISCB`: reshapes wide nuclide columns to long format with `NUCLIDE`, `UNIT`, `VALUE`, `UNC`
  - `ConvertU238CB`: converts U-238 from ppb to atoms/kg using Avogadro's number and U-238 molar mass
  - `encode`: full pipeline entry point writing standardised data to NetCDF4

## [1.4.3] - 2026-06-26

### Added
- `DataLoader`: loads the MARIS global dump CSV, filters by `ref_id`, and returns one DataFrame per sample type (`BIOTA`, `SEAWATER`, `SEDIMENT`, `SUSPENDED_MATTER`)
- `CastStationToStringCB`: coerces the `STATION` column to VLEN string and fills missing values with empty string
- `DropNAColumnsCB`: removes columns that are entirely `NaN` or all-zero (MARIS "Not Available" sentinel)
- `AddSampleIDCB`: casts `SMP_ID` to `int` and `SMP_ID_PROVIDER` to variable-length string

### Changed
- `maris_legacy` handler fully migrated to the current callback API (`RenameColumnsCB`, `RemapCB`, `PerGroupCB`, `SanitizeLonLatCB`, `ParseTimeCB`, `EncodeTimeCB`)
- Handler notebook restructured as a step-by-step documentation guide (column selection → type casting → NA dropping → DL remapping → time encoding → coordinate sanitization → NetCDF encoding)
- MARIS Legacy handler status updated to ✅ Active in README

## [1.4.2] - 2026-06-24

### Fixed
- `BboxCB`: correct Shapely `bounds` unpacking order (`lon_min, lat_min, lon_max, lat_max`); previously `lat_min`/`lon_max` were swapped, producing wrong bounding-box attributes in generated NetCDF files (reported by @tabascojijii in PR #42)

## [1.4.1] - 2026-06-24

### Changed
- Improved "Write a new handler" how-to: getting-started guidance and column naming conventions
- Fixed missing/mistyped nbdev directives
- Removed leftover code and stale documentation
- General README and how-to refinements

## [1.4.0] - 2026-06-23

  ### Added
  - `fuzzy_merge`: brute-force Levenshtein (or custom) matching between provider and MARIS reference
  DataFrames
  - `fix_lut`: apply expert overrides on top of fuzzy matches, with a stderr warning for unknown
  targets
  - `lut_from` / `uniq_across_dfs`: build source LUTs from unique column values across group
  DataFrames
  - `make_lut` / `make_lut_from`: lazy factory functions that defer the full match-and-fix pipeline
  until runtime; integrate directly with `RemapCB`

  ### Changed
  - HELCOM handler fully refactored to the new matching API (`make_lut`, `make_lut_from`, `RemapCB`)
  - OSPAR, TEPCO, and MARIS Legacy handlers temporarily muted (`#| eval: false`) pending migration
  to the new API

  ### Removed
  - `Remapper` class: replaced by the `fuzzy_merge` / `fix_lut` / `make_lut` / `make_lut_from`
  workflow

## [1.3.0] - 2026-06-18

### Changed
- `NetCDFEncoder` methods renamed for consistency and brevity: `copy_global_attributes` → `copy_global_attrs`, `copy_dimensions` → `copy_dims`, `process_groups` → `process_grps`, `process_group` → `process_grp`, `copy_variables` → `copy_vars`, `copy_variable` → `copy_var`, `copy_variable_attributes` → `copy_var_attrs`, `_get_variable_type` → `var_type`, `_create_netcdf_variable` → `create_var`, `_populate_variable_data` → `fill_var`, `sanitize_if_enum_and_nan` → `fillna_enum`
- `retrieve_all_cols(dtypes=NC_DTYPES)` replaced by `all_cols` read-only property
- All `NetCDFEncoder` methods now carry docstrings and inline parameter docs (fastcore.docments style)
- Module docstring updated to reflect its role: handler-curated DataFrames → MARIS NetCDF

### Removed
- `_create_and_copy_variable` internal helper (logic inlined into `copy_var`)

## [1.2.1] - 2026-06-18

### Changed
- `Callback`: added explicit `__init__` so subclasses inherit cleanly without needing `super()`
- `PerGroupCB`: added `__init__(grps=None)` with inline parameter docs; `each_grp` promoted to a `@patch` method with a docstring so it appears in generated API docs
- `RenameColumnsCB`: now performs column selection *and* renaming in one pass — only columns listed in `renaming_rules` survive (replaces the separate `SelectColumnsCB` step)
- `callbacks` module: expanded test coverage and reorganised documentation sections (Foundation, Cleaning & validation, Value mapping, Schema alignment, Comparison & audit, Time)

### Removed
- `SelectColumnsCB`: folded into `RenameColumnsCB`; `maris_legacy` handler updated accordingly

## [1.2.0] - 2026-06-17

### Added
- `INISClient`: lightweight client to fetch bibliographic metadata from the IAEA INIS InvenioRDM API
- `InisCB`: callback that populates `id`, `title`, `summary`, `creator_name`, `references` (DOI), and `metadata_link` (URL) global attributes from an INIS record
- `fetch_inis` / `find_curl`: helpers to retrieve INIS records via curl

### Changed
- `ZoteroClient` (formerly `ZoteroItem`): refactored to use `@property` accessors (`title`, `summary`, `creator_name`) defined in the class body rather than separate `@patch` cells
- `ZoteroCB`: updated to use the new `ZoteroClient` API

### Contributors
- Takahito Tsujii — initial INIS integration (PR)

## [1.1.0] - 2026-06-16

Initial public release with `bundle-luts` refactoring, standalone LUT file, and direct install without `maris_init`.
