# Changelog

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
