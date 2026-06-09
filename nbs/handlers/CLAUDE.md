# Handler pattern

A handler is a notebook (`nbs/handlers/*.ipynb`) that encodes one provider's dataset to MARIS NetCDF4. The generated module lives at `marisco/handlers/*.py`. Use `helcom` as the reference — it is the most complete example.

## Handler structure

```python
# 1. Constants
src_dir = '...'          # URL or path to raw provider data
fname_out = '...'        # default output NetCDF filename
zotero_key = 'XXXXXXXX' # 8-char Zotero record key for this dataset

# 2. Data loader — returns dict keyed by sample type group
def load_data(...) -> Dict[str, pd.DataFrame]: ...

# 3. Lookup table factories (one per enumerated field needing remapping)
lut_nuclides = lambda df: Remapper(...).generate_lookup_table(fixes={...})
lut_biota    = lambda: Remapper(...).generate_lookup_table(fixes={...})

# 4. Provider-specific callbacks (as many as needed)
# IMPORTANT: the class docstring is the processing log entry.
# run_cbs() appends cb.__doc__ to tfm.logs for every callback that has one.
# get_attrs() then serialises tfm.logs into the NetCDF global attribute
# `publisher_postprocess_logs`, so every post-processing step is permanently
# documented inside the output file. Write docstrings that are informative
# enough to stand alone as audit trail entries — what was done and why —
# but keep them to one or two sentences.
class RemapNuclideNameCB(Callback):
    "Remap provider nuclide names to MARIS standard nc_name identifiers via fuzzy-matched LUT; unresolved names are set to 0 (unknown)."
    ...
class ParseTimeCB(Callback):
    "Parse provider date/time columns (separate DATE and TIME fields, format DD/MM/YYYY) into a single datetime; rows with missing or unparseable dates are dropped."
    ...

# 5. Global attributes builder
def get_attrs(tfm, zotero_key, kw) -> dict:
    return GlobAttrsFeeder(tfm.dfs, cbs=[
        BboxCB(), DepthRangeCB(), TimeRangeCB(),
        ZoteroCB(zotero_key, cfg=cfg()),
        KeyValuePairCB('keywords', ', '.join(kw)),
        KeyValuePairCB('publisher_postprocess_logs', ', '.join(tfm.logs))
    ])()

# 6. encode() — the CLI entry point
def encode(fname_out, **kwargs):
    dfs = load_data(src_dir)
    tfm = Transformer(dfs, cbs=[...])
    tfm()
    NetCDFEncoder(
        tfm.dfs, dest_fname=fname_out,
        global_attrs=get_attrs(tfm, zotero_key, kw),
        verbose=kwargs.get('verbose', False)
    ).encode()
```

## MARIS column naming convention

Raw provider columns stay lowercase. Callbacks map them to UPPERCASE MARIS standard columns.

The canonical mapping between the UPPERCASE DataFrame column names used in handlers and the NetCDF4 variable names is `NC_VARS` in `nbs/api/configs.ipynb`. The NetCDF4 variable names themselves are defined in `nbs/files/cdl/maris.cdl`.

Key column mappings (UPPERCASE handler name → NetCDF name → description):

| Handler col   | NetCDF var  | Notes |
|---------------|-------------|-------|
| `TIME`        | `time`      | Integer seconds since 1970-01-01 |
| `LAT`         | `lat`       | Decimal degrees, −90 to 90 |
| `LON`         | `lon`       | Decimal degrees, −180 to 180 |
| `SMP_DEPTH`   | `smp_depth` | Metres below surface; −1 = not available |
| `TOT_DEPTH`   | `tot_depth` | Total water column depth (m) |
| `NUCLIDE`     | `nuclide`   | Integer ID from `dbo_nuclide.xlsx` |
| `VALUE`       | `value`     | Activity or MDA (float) |
| `UNC`         | `unc`       | 1σ uncertainty, same unit as VALUE |
| `DL`          | `dl`        | Detection-limit flag ID (see below) |
| `UNIT`        | `unit`      | Integer ID from `dbo_unit.xlsx` |
| `SPECIES`     | `species`   | Integer ID from `dbo_species.xlsx` (BIOTA) |
| `BIO_GROUP`   | `bio_group` | Integer ID from `dbo_biogroup.xlsx` (BIOTA) |
| `BODY_PART`   | `body_part` | Integer ID from `dbo_bodypar.xlsx` (BIOTA) |
| `SED_TYPE`    | `sed_type`  | Integer ID from `dbo_sedtype.xlsx` (SEDIMENT) |
| `TOP`         | `top`       | Top of sediment slice (cm) |
| `BOTTOM`      | `bottom`    | Bottom of sediment slice (cm) |
| `STATION`     | `station`   | String (VLEN); fill with `''` if missing |
| `SMP_ID`      | `smp_id`    | Provider sample code or generated integer |
| `FILT`        | `filtered`  | Integer: 1=filtered, 2=unfiltered |
| `SALINITY`    | `salinity`  | PSU |
| `TEMPERATURE` | `temperature` | °C |
| `LAB`         | `lab`       | Integer ID from `dbo_lab.xlsx` |
| `SAMP_MET`    | `samp_met`  | Integer ID from `dbo_sampmet.xlsx` |
| `PREP_MET`    | `prep_met`  | Integer ID from `dbo_prepmet.xlsx` |
| `COUNT_MET`   | `count_met` | Integer ID from `dbo_counmet.xlsx` |
| `AREA`        | `area`      | Integer ID from `dbo_area.xlsx` |

## Lookup table remapping — the IMFA pattern

Provider nomenclature (nuclide names, species, sediment types, body parts, etc.) must be reconciled with MARIS IDs from the Excel LUTs in `nbs/files/lut/`. This is semi-automated via the **IMFA** pattern: **Inspect → Match → Fix → Apply**. Domain expertise is required at the Fix step — automated fuzzy matching alone is not reliable enough.

### Step 1 — Inspect

Examine the provider's own nomenclature. Typically this means loading a distinct-values DataFrame from the raw data:

```python
# e.g. all unique nuclide names across all sample-type DataFrames
get_unique_across_dfs(dfs, col_name='NUCLIDE', as_df=True)
```

Also inspect the target MARIS LUT to understand what names and IDs are available:

```python
pd.read_excel(nuc_lut_path())   # or species_lut_path(), sediments_lut_path(), …
```

### Step 2 — Match

Instantiate `Remapper` and run fuzzy matching (uses `jellyfish` under the hood) to find discrepancies between provider names and MARIS names:

```python
remapper = Remapper(
    provider_lut_df=df,              # provider's distinct nomenclature as DataFrame
    maris_lut_fn=nuc_lut_path,      # path function → MARIS LUT Excel file
    maris_col_id='nuclide_id',      # ID column in MARIS LUT
    maris_col_name='nc_name',       # name column in MARIS LUT
    provider_col_to_match='value',  # provider column to fuzzy-match against
    provider_col_key='value',       # provider column used as dict key
    fname_cache='nuclides_x.pkl'    # pickle cache stored in ~/.marisco/
)

remapper.generate_lookup_table(as_df=True)
remapper.select_match(match_score_threshold=1, verbose=True)
# prints all entries with a match score < 1 (i.e. imperfect matches)
```

These two calls are exploratory — mark the notebook cell `#| eval: false` so they don't run during `nbdev_export`.

### Step 3 — Fix

Create a `fixes_*` dict that explicitly resolves the imperfect matches identified above. This step requires domain knowledge: the correct MARIS name is not always obvious from the provider name (e.g. combined isotopes, synonyms, obsolete taxonomy).

```python
#| exports
fixes_nuclide_names = {
    'cs134137': 'cs134_137_tot',   # combined isotope → MARIS aggregate name
    'k-40':     'k40',             # formatting difference
    'bad_name': NA,                # unmappable → mark as not available
}
```

Re-run Match with `fixes` applied and confirm `select_match()` returns zero unresolved entries (or that remaining mismatches are acceptable after visual inspection):

```python
remapper.generate_lookup_table(as_df=True, fixes=fixes_nuclide_names)
fc.test_eq(len(remapper.select_match(match_score_threshold=1, verbose=True)), 0)
```

### Step 4 — Apply

Freeze the mapping into a `lut_*` factory lambda. Pass `overwrite=False` to use the cached pickle from Step 2/3 rather than recomputing, and `as_df=False` to return a plain dict for use in callbacks:

```python
#| exports
lut_nuclides = lambda df: Remapper(
    provider_lut_df=df,
    maris_lut_fn=nuc_lut_path,
    maris_col_id='nuclide_id',
    maris_col_name='nc_name',
    provider_col_to_match='value',
    provider_col_key='value',
    fname_cache='nuclides_x.pkl'
).generate_lookup_table(fixes=fixes_nuclide_names, as_df=False, overwrite=False)
```

This lambda is then passed to a `RemapCB` (or a provider-specific callback) in the `Transformer`:

```python
tfm = Transformer(dfs, cbs=[
    RemapNuclideNameCB(lut_nuclides, col_name='NUCLIDE'),
    RemapCB(fn_lut=lut_biota, col_remap='SPECIES', col_src='rubin', dest_grps='BIOTA'),
    ...
])
```

### When Remapper is overkill

For small, stable enumerations (e.g. a `filtered` flag with 3 values), skip `Remapper` and write a plain dict directly:

```python
lut_filtered = {'N': 2, 'n': 2, 'F': 1}
```

---

## Data curation rules

These rules are derived from the existing handlers and the MARIS data schema. Apply them consistently when writing a new handler.

### Detection limit encoding

The `DL` column must always hold an integer ID from `dbo_detectlimit.xlsx`:

| MARIS DL ID | Meaning | When to use |
|-------------|---------|-------------|
| 1 (`=`)     | Measured value | Provider reports an actual activity; `VALUE` is the measurement |
| 2 (`<`)     | Below detection limit | Provider reports an MDA or detection limit; `VALUE` holds that limit value |
| 3 (`ND`)    | Not detected, no limit given | No activity and no MDA reported |
| 4 (`DE`)    | Derived (aggregated) | `VALUE` is an aggregate (mean, sum, etc.) of multiple samples |

Typical mapping logic (adapt to provider encoding):

```python
# HELCOM pattern: explicit '<' column
lut_dl = {'<': 2}  # default → 1

# OSPAR pattern: value_type column
# value_type == '<' → DL=2; value_type == '=' → DL=1; NaN → DL=1

# TEPCO pattern: "ND" string in VALUE
# "ND" + no limit given → VALUE=NaN, DLV=NaN, DL=3
# "ND" + limit available → VALUE=limit, DLV=limit, DL=2
# numeric VALUE → DL=1
```

### Unit assignment and conversion

The `UNIT` column holds an integer ID from `dbo_unit.xlsx`. Key IDs used across handlers:

| MARIS unit ID | Unit | Used for |
|---------------|------|----------|
| 1             | Bq/m³ | SEAWATER standard |
| 3             | Bq/L  | SEAWATER (some providers; convert to Bq/m³ by ×1000) |
| 4             | Bq/kg dry wt | BIOTA dry-weight basis |
| 5             | Bq/kg wet wt | BIOTA wet-weight basis (preferred when both available) |

**Seawater unit rule:** MARIS stores seawater in Bq/m³. If the provider reports Bq/L, multiply `VALUE`, `UNC`, and any detection-limit value by 1000 and assign `UNIT = 1`.

**Biota wet/dry rule:**
- If only wet-weight measurements reported → `UNIT = 5`
- If only dry-weight measurements reported → `UNIT = 4`
- If both reported for the same sample+nuclide → prefer wet weight (`UNIT = 5`); also compute and store `PERCENTWT = DRYWT / WETWT * 100`

**Uncertainty rule:** Uncertainties must be 1σ absolute values in the same unit as `VALUE`. If the provider reports relative uncertainty (%), convert: `UNC_abs = VALUE * UNC_pct / 100`.

**SEDIMENT split:** Some providers (e.g., HELCOM) report sediment activity in both Bq/kg and Bq/m². Split these into two separate rows with the appropriate `UNIT` ID.

### Date/time handling

All handlers encode time as **integer seconds since 1970-01-01 00:00:00 UTC** for NetCDF storage (via `EncodeTimeCB`).

Parsing rules:
- Parse to `pd.Timestamp` first (use `errors='coerce'` to produce `NaT` on failure).
- Drop rows where `TIME` is `NaT` after parsing.
- If only a year is provided, use `{year}-01-01`.
- If year + month are provided, use `{year}-{month}-01`.
- If day or month = 0 in the source, the row is invalid — drop it.
- Remove any non-numeric/non-date tokens before parsing (e.g., Japanese character `約` in TEPCO).
- Different source files within one provider may use different date formats — handle each separately.

### Coordinate handling

- Store as decimal degrees: `LAT` ∈ [−90, 90], `LON` ∈ [−180, 180].
- If the provider uses degrees + decimal minutes (DDMM.mmm), convert via `ddmm_to_dd`.
- If the provider uses DMS, convert to decimal degrees.
- If longitudes are in [0, 360], shift to [−180, 180] by subtracting 360 for values > 180.
- Drop rows where `LAT == 0` and `LON == 0` (sentinel for unknown position).
- Drop rows with coordinates outside valid range.
- Replace comma decimal separators with periods before parsing.

### Depth handling

- `SMP_DEPTH`: depth (m) below water surface at which sample was taken. Use `−1` as sentinel for "not available" (not `NaN`, which the CDL may not allow for mandatory fields). Surface samples = 0.
- `TOT_DEPTH`: total water column depth (m). `NaN` if not reported.
- `TOP` / `BOTTOM`: sediment core slice boundaries in cm relative to the water-sediment interface.
- Cast all depth fields to `float`.

### Nuclide name remapping patterns

Common fixes needed across providers (domain knowledge):

```python
# Combined isotopes — provider reports sum, MARIS has aggregate entry
'cs134137'   → 'cs134_137_tot'
'cm243244'   → 'cm243_244_tot'
'pu239240'   → 'pu239_240_tot'
'pu238240'   → 'pu238_240_tot'
'239,240pu'  → 'pu239_240_tot'

# Formatting normalization
'k-40'       → 'k40'
'99tc'       → 'tc99'
'238pu'      → 'pu238'
'226ra'      → 'ra226'
'ra-226'     → 'ra226'
'137cs'      → 'cs137'
'3h'         → 'h3'

# OCR/data-entry errors in HELCOM (all mapped to cs137)
'cs143','cs145','cs142','cs141','cs144','cs140','cs146','cs139','cs138' → 'cs137'
```

If a name cannot be resolved to any MARIS nuclide, set it to `NA` (unknown, ID 0). Never silently drop it — the row may still carry valid data for other nuclides.

### Species remapping patterns

Common fixes:

```python
# Obsolete taxonomy → current accepted name
'STIZOSTEDION LUCIOPERCA' → 'Sander luciopercas'
'LAMINARIA SACCHARINA'   → 'Saccharina latissima'
'CARDIUM EDULE'          → 'Cerastoderma edule'
'PSETTA MAXIMA'          → 'Scophthalmus maximus'

# Mixed or unresolvable taxa → NA
'RHODYMENIA PSEUDOPALAMATA & PALMARIA PALMATA' → NA
'Mixture of green, red and brown algae'         → NA
'Flatfish'                                       → NA

# Generic group fallback (OSPAR pattern): when species = NA but biological group
# is known, use the group name as a coarse species mapping
'fish' / 'Fish' / 'FISH' → 'Pisces'
```

`BIO_GROUP` is always derived from `SPECIES` via the `biogroup_id` column in `dbo_species.xlsx` — do not assign it independently.

### Body part remapping

Body part names often need normalisation (case, trailing spaces) before matching:

```python
'WHOLE FISH WITHOUT HEAD AND ENTRAILS' → 'Whole animal eviscerated without head'
'WHOLE FISH WITHOUT ENTRAILS'          → 'Whole animal eviscerated'
'SKIN/EPIDERMIS'                       → 'Skin'
'ENTRAILS'                             → 'Viscera'
'whole seaweed'                        → 'Whole plant'
'flesh fish'                           → 'Flesh with bones'
```

For OSPAR, the body part description depends on the biological group, so concatenate `body_part + biological_group` before lookup.

### Sediment type remapping

Most sediment type names map cleanly. Flag entries that are missing or outside the Udden-Wentworth scale as `NA`. HELCOM has two legacy sediment IDs (56 and 73) that are not in the current MARIS LUT — map them to a sentinel value (e.g., −99) and document the decision in the callback docstring.

### Row dropping criteria

Drop a row when:
- `TIME` cannot be parsed (NaT after `errors='coerce'`), or day/month = 0.
- `LAT` and `LON` are both 0 (unknown position sentinel).
- Coordinates are outside valid ranges.
- The row carries all-NaN measurements across all nuclides (wide-format sources).

Track drops via `CompareDfsAndTfmCB` — it logs row counts before and after each callback and writes the summary to `publisher_postprocess_logs`.

Do **not** drop rows just because a remapped field (species, sediment type, etc.) could not be resolved — use `NA`/0 instead and keep the measurement.

### Sample ID (`SMP_ID`)

- If the provider supplies a stable sample identifier, store it verbatim as `SMP_ID` and also keep it in a provider-specific column (e.g., `SMP_ID_PROVIDER`).
- If no identifier exists, generate a sequential integer ID (e.g., `range(len(df))`).
- `SMP_ID` is cast to string for VLEN NetCDF storage.

### Wide-to-long reshaping

Some providers (GEOTRACES) deliver data in wide format, with one column per nuclide. Steps:
1. Parse nuclide name, unit, and filter status from column headers (e.g., via regex `\[(.*?)\]`).
2. Drop columns that are all-NaN before reshaping.
3. Melt to long format, then apply IMFA remapping on the nuclide name column.

### Filtered field

`FILT` encodes filter status as an integer: `1` = filtered (dissolved), `2` = unfiltered (total). For GEOTRACES: column suffix `_D` → 1, `_T` → 2, suspended fractions → 1. For a simple Y/N flag: `{'Y': 1, 'N': 2}`.

### Negative activity values

GEOTRACES contains a small number of negative activity values (radiometric artifact). Do **not** drop them silently — flag the issue in the callback docstring and consider reporting upstream to the data provider.

---

## Existing handlers

| Handler | Provider | Sample types |
|---|---|---|
| `helcom` | HELCOM MORS (Baltic Sea monitoring) | SEAWATER, BIOTA, SEDIMENT |
| `ospar` | ODIMS OSPAR (NE Atlantic) | BIOTA |
| `geotraces` | BODC GEOTRACES IDP2021 | SEAWATER |
| `tepco` | Fukushima monitoring (TEPCO/NRA) | SEAWATER, BIOTA, SEDIMENT |
| `maris_legacy` | MARIS Master Database legacy format | all types |
