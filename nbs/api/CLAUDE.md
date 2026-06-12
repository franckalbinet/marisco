# Core API abstractions

## Callback / Transformer (`callbacks.py`)

`Transformer` holds `dfs: Dict[str, pd.DataFrame]` (one key per sample type group) and applies an ordered list of `Callback` objects in place.

```python
tfm = Transformer(dfs={'SEAWATER': df, ...}, cbs=[CallbackA(), CallbackB()])
tfm()  # runs all callbacks; mutates tfm.dfs in place
```

Each callback implements `__call__(self, tfm: Transformer)`. Use the `order` attribute to control sequencing. After `tfm()`, `tfm.logs` contains processing notes appended by callbacks.

**Built-in callbacks:**

| Callback | Purpose |
|---|---|
| `SanitizeLonLatCB` | Remove rows with (0,0) or out-of-range coordinates |
| `RemapCB(fn_lut, col_remap, col_src, dest_grps)` | Generic LUT remapping, optionally scoped to specific groups |
| `LowerStripNameCB(col_src, col_dst)` | Normalise a column to lowercase stripped strings |
| `ParseTimeCB` | Parse TIME column from ISO8601 string to datetime |
| `EncodeTimeCB` / `DecodeTimeCB` | Convert datetime ↔ seconds-since-epoch |
| `SelectColumnsCB` | Keep only specified columns |
| `RenameColumnsCB` | Rename columns to MARIS standard names |
| `RemoveAllNAValuesCB` | Drop rows where all values are NA |
| `CompareDfsAndTfmCB` | Log rows removed or added during transformation |
| `UniqueIndexCB` | Assign a unique index per group |

## Configurations (`configs.py`)

Central registry of MARIS data standards and path helpers.

Key exports:
- `NC_GROUPS` — sample type group names → NetCDF4 group names
- `NC_VARS` — MARIS variable names → NetCDF variable names
- `NC_DTYPES` — all enumeration type definitions (NUCLIDE, UNIT, SPECIES, etc.)
- `cfg()` — reads `~/.marisco/configs.toml`
- `get_lut(src_dir, fname, key, value)` — load a LUT Excel file → `{key: value}` dict
- `*_lut_path()` — path helpers per LUT (e.g. `nuc_lut_path()`, `species_lut_path()`)
- `cache_path()`, `base_path()` — helpers for `~/.marisco/`

## Metadata (`metadata.py`)

`GlobAttrsFeeder` produces NetCDF4 global attributes (ISO 19115-compatible) via its own callback pattern:

```python
GlobAttrsFeeder(dfs, cbs=[
    BboxCB(),                           # geographical bounding box
    DepthRangeCB(),                     # min/max depth
    TimeRangeCB(),                      # time_coverage_start/end
    ZoteroCB(zotero_key, cfg=cfg()),    # title, summary, creators from Zotero
    KeyValuePairCB('keywords', '...'),  # arbitrary key-value pairs
])()
```

Every MARIS dataset has a Zotero record. `zotero_key` is the 8-character alphanumeric key. Requires `ZOTERO_API_KEY` env var.

## Encoding (`encoders.py`)

```python
NetCDFEncoder(
    dfs=tfm.dfs,          # dict of DataFrames, one per sample type group
    dest_fname='out.nc',
    global_attrs={...},   # from GlobAttrsFeeder
    verbose=False
).encode()
```

Uses `~/.marisco/maris-template.nc` as the structural template. The template is generated from `nbs/api/files/cdl/maris.cdl` via `ncgen` — see `nbs/CLAUDE.md`.

## Decoding (`decoders.py`, `netcdf2csv.py`)

`decode()` reads a MARIS NetCDF4 file and writes CSV files in the MARIS standard format (one file per sample type group present). This legacy CSV format is still required by the MARIS Master Database ingestion pipeline.
