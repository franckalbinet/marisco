# Callback group dispatch — audit, diagnosis, and design

## Status

| Notebook | Status |
|---|---|
| `nbs/api/callbacks.ipynb` | ✅ done |
| `nbs/handlers/helcom.ipynb` | ✅ done |
| `nbs/handlers/ospar.ipynb` | ✅ done |
| `nbs/handlers/geotraces.ipynb` | 🔲 todo |
| `nbs/handlers/maris_legacy.ipynb` | 🔲 todo |

---

## Context

Every handler callback that operates on `tfm.dfs` must iterate over the groups
(`SEAWATER`, `BIOTA`, `SEDIMENT`, `SUSPENDED_MATTER`). There is no shared
abstraction for this in `Callback`, so every callback re-implements the loop.

---

## Audit — iteration patterns found across handlers

| Pattern | Where |
|---|---|
| `for grp, df in tfm.dfs.items():` | `SanitizeLonLatCB`, `EncodeTimeCB`, ospar `ParseTimeCB`, ospar `SanitizeValueCB` |
| `for k in tfm.dfs.keys():` | helcom `CastStationToStringCB`, ospar `DropNAColumnsCB`, ospar `RemapNuclideNameCB` |
| `for df in tfm.dfs.values():` | helcom `ParseTimeCB`, `AddDepthCB`, `AddSalinityCB`, `AddStationCB`, `RemapFiltCB` |
| `for _, df in tfm.dfs.items():` | helcom `AddSampleIDCB`, geotraces `AddSampleIDCB`, ospar `AddSampleIdCB` |
| `tfm.df[col] = ...` *(single df)* | all geotraces pre-split callbacks |
| `tfm.dfs['BIOTA']` *(direct key)* | ospar `EnhanceSpeciesCB`, `AddBodypartTempCB` |
| `if grp in tfm.dfs: tfm.dfs[grp]...` *(conditional single group)* | helcom `SplitSedimentValuesCB`, helcom `NormalizeUncCB` |

---

## Diagnosis

The `Callback` base class defines only `order = 0`. It provides no protocol
for *how* to visit groups. Consequences:

1. **Duplication** — the loop is written from scratch in every callback.
2. **Inconsistency** — four syntactic variants for the same semantic act.
3. **No shared missing-group policy** — some callbacks silently skip a missing
   group, others raise a `KeyError`, others add an explicit `if grp in tfm.dfs`
   guard. Behaviour depends on which variant the author happened to pick.
4. **Group scoping is ad-hoc** — `RemapCB` already has a `dest_grps` parameter
   for this purpose, but no other callback reuses that pattern.

The missing abstraction barrier is the question:

> **"Do I act on one group at a time, or do I need cross-group state?"**

For the vast majority of callbacks the answer is *one group at a time*. The
iteration is pure boilerplate and should not be visible in the subclass.

---

## Design — `PerGroupCB`

**Implemented in `nbs/api/callbacks.ipynb`.** Key decisions made during implementation:

- Template method is named `each_grp`: `process_group` was too verbose; `each` was too generic (hides the group aspect); `each_grp` is short, uses the `grp` abbreviation already established in the codebase, and is unambiguous
- Loop iterates over `self.grps or tfm.dfs` directly (dict iteration yields keys; no intermediate variable)
- Missing-group guard lives in `__call__`, not in subclasses

```python
class PerGroupCB(Callback):
    "Calls `each_grp` for each group in `tfm.dfs`; set `grps` to restrict to specific groups."
    grps: list = None  # None → all groups; explicit list restricts to those groups only

    def __call__(self, tfm):
        for grp in (self.grps or tfm.dfs):
            if grp in tfm.dfs: self.each_grp(grp, tfm.dfs[grp], tfm)

    def each_grp(self,
                 grp: str,          # Group key e.g. 'SEAWATER', 'BIOTA'
                 df: pd.DataFrame,  # DataFrame for this group
                 tfm,               # Parent Transformer
                 ): raise NotImplementedError
```

`__call__` owns: which groups to visit, the missing-group guard, and the loop.  
`each_grp` owns: the transformation logic for a single group.

The `grps` class variable is the scoping hook:
- `grps = None` → all groups (default)
- `grps = ['BIOTA']` → single group, class-level
- set in `__init__` for runtime-configurable scoping

Cross-group callbacks (`CompareDfsAndTfmCB`, `SplitSedimentValuesCB`) keep
their full `__call__` override — they legitimately need cross-group state.

### callbacks.ipynb — migrated ✅

| Callback | Note |
|---|---|
| `SanitizeLonLatCB` | migrated |
| `LowerStripNameCB` | migrated |
| `AddSampleTypeIdColumnCB` | migrated |
| `SelectColumnsCB` | migrated |
| `RenameColumnsCB` | migrated |
| `EncodeTimeCB` | migrated |
| `DecodeTimeCB` | migrated |
| `UniqueIndexCB` | migrated |
| `RemapCB` | **kept as `Callback`** — has own `dest_grps` scoping + loads LUT in `__call__` |
| `RemoveAllNAValuesCB` | **kept as `Callback`** — iterates over derived `cols_dict`, not directly over `tfm.dfs` |
| `CompareDfsAndTfmCB` | **kept as `Callback`** — cross-group by design |

### helcom.ipynb — migrated ✅

| Callback | Note |
|---|---|
| `ParseTimeCB` | migrated |
| `SanitizeValueCB` | migrated — `dfs_dropped` side-channel removed (see TODO below) |
| `RemapUnitCB` | migrated — per-group if/elif in `each_grp` |
| `RemapDetectionLimitCB` | migrated |
| `RemapSedimentCB` | migrated — `grps` set from `sed_grp_name` in `__init__` |
| `RemapFiltCB` | migrated |
| `AddSampleIDCB` | migrated |
| `AddDepthCB` | migrated |
| `AddSalinityCB` | migrated |
| `AddStationCB` | migrated |
| `AddTemperatureCB` | migrated |
| `RemapSedSliceTopBottomCB` | migrated — `grps = ['SEDIMENT']` |
| `LookupDryWetPercentWeightCB` | migrated |
| `RemapNuclideNameCB` | migrated — `__call__` builds LUT, `each_grp` applies it |
| `ParseCoordinates` | migrated + **renamed `ParseCoordinatesCB`** |
| `SplitSedimentValuesCB` | **kept as `Callback`** — creates new groups by splitting |
| `NormalizeUncCB` | **kept as `Callback`** — iterates `self.coi` (list of tuples), not `tfm.dfs` |

---

## Example rewrites

### 1. Key not needed — `AddDepthCB` (helcom)

Before:
```python
class AddDepthCB(Callback):
    "Ensure depth values are floats and add 'SMP_DEPTH' and 'TOT_DEPTH' columns."
    def __call__(self, tfm: Transformer):
        for df in tfm.dfs.values():
            if 'sdepth' in df.columns:
                df['SMP_DEPTH'] = df['sdepth'].astype(float)
            if 'tdepth' in df.columns:
                df['TOT_DEPTH'] = df['tdepth'].astype(float)
```

After:
```python
class AddDepthCB(PerGroupCB):
    "Ensure depth values are floats and add 'SMP_DEPTH' and 'TOT_DEPTH' columns."
    def each_grp(self, grp, df, tfm):
        if 'sdepth' in df.columns: df['SMP_DEPTH'] = df['sdepth'].astype(float)
        if 'tdepth' in df.columns: df['TOT_DEPTH'] = df['tdepth'].astype(float)
```

---

### 2. Key used as config lookup — `ParseTimeCB` (ospar)

Before:
```python
class ParseTimeCB(Callback):
    def __init__(self, col_src, col_dst, format): fc.store_attr()
    def __call__(self, tfm):
        for grp, df in tfm.dfs.items():
            src_col = self.col_src.get(grp)
            df[self.col_dst] = pd.to_datetime(df[src_col], format=self.format, errors='coerce')
```

After:
```python
class ParseTimeCB(PerGroupCB):
    def __init__(self, col_src, col_dst, format): fc.store_attr()
    def each_grp(self, grp, df, tfm):
        df[self.col_dst] = pd.to_datetime(df[self.col_src.get(grp)], format=self.format, errors='coerce')
```

---

### 3. Scoped to a single group — `EnhanceSpeciesCB` (ospar)

Before:
```python
class EnhanceSpeciesCB(Callback):
    def __call__(self, tfm):
        df = tfm.dfs['BIOTA']
        df['SPECIES'] = df.apply(
            lambda row: row['enhanced_species'] if row['SPECIES'] in [-1, 0]
                        and pd.notnull(row['enhanced_species']) else row['SPECIES'], axis=1)
```

After:
```python
class EnhanceSpeciesCB(PerGroupCB):
    grps = ['BIOTA']
    def each_grp(self, grp, df, tfm):
        df['SPECIES'] = df.apply(
            lambda row: row['enhanced_species'] if row['SPECIES'] in [-1, 0]
                        and pd.notnull(row['enhanced_species']) else row['SPECIES'], axis=1)
```

The group guard (`if 'BIOTA' in tfm.dfs`) moves from ad-hoc call-site logic
into the base class. A typo in the group name previously silenced the error;
now the base class handles it uniformly for all subclasses.

---

## TODO — redesign `dfs_dropped` tracking

`SanitizeValueCB` used to populate `tfm.dfs_dropped` (a side-channel dict of removed rows)
alongside the sanitizing logic. These are two concerns in one place:

1. Sanitizing — drop NaN rows, standardize to `VALUE` column → belongs in `SanitizeValueCB`
2. Tracking removals — before/after row diff → `CompareDfsAndTfmCB` already does this properly

During the `PerGroupCB` migration, the `dfs_dropped` mechanism was removed from
`SanitizeValueCB`. A proper removal-tracking design should be revisited separately,
likely by ensuring `CompareDfsAndTfmCB` is composed after `SanitizeValueCB` in every
handler pipeline that needs it.

---

## TODO — revisit data-dependent LUT lambdas

`lut_nuclides` takes `df` (unique values from runtime data) unlike all other zero-arg LUT lambdas.
This creates a redundancy with the exploration workflow and leaks data-gathering into the callback.
Needs further design thought to align with the broader LUT closure pattern.

---

## What does NOT change

Callbacks that require cross-group state or a fundamentally different dispatch
strategy keep their full `__call__`:

- `CompareDfsAndTfmCB` — computes diffs *between* original and transformed dfs
- `SplitSedimentValuesCB` — creates new groups by splitting one group
- `GroupBySampleTypeCB` (geotraces) — *produces* `tfm.dfs` from `tfm.df`
- `RemapNuclideNameCB` (helcom/ospar) — calls `get_unique_across_dfs` first

These are not special cases to be worked around — they are legitimately
cross-group operations and belong at the `Callback` level, not `PerGroupCB`.
