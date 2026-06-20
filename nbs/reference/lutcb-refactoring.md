# LutCB Refactoring: Architecture & Design Record

> Reference document for the planned refactoring of nomenclature reconciliation
> across all handlers. Captures the diagnosis, design decisions, and rationale
> from the design session. Use as the base when implementing.

---

## 1. The problem

Every handler that uses the new MIFA pattern currently exports a broken line:

```python
#| exports
lut_nuclides = Lut(fixed, key_col='value', val_col='nuclide_id')
```

This fails `nbdev-prepare` (both notebook test execution and module import) because
`fixed` is not in scope. The dependency chain is:

```
lut_nuclides  →  fixed  →  merged  →  dfs  (runtime data, #| eval: false)
```

`fixed = fix_lut(merged, ...)` has no `#| export` directive so it is absent from
the generated `.py` module. `merged` was computed in a `#| eval: false` cell so it
is also absent during notebook test execution.

The generated `marisco/handlers/helcom.py` therefore contains:

```python
fixes_nuclide_names = { ... }          # OK — exported, pure dict literal
lut_nuclides = Lut(fixed, ...)         # NameError: 'fixed' not defined
```

Importing the module fails. Running `nbdev-prepare` fails.

---

## 2. Root cause

The MIFA "Apply" step (`lut_nuclides = Lut(fixed, ...)`) is exported as a
**module-level eager computation**, but it depends on runtime data. The two
requirements are incompatible.

The old OSPAR / TEPCO handlers avoided this by making `lut_nuclides` a **lazy
lambda**:

```python
# OSPAR (old Remapper-based pattern) — lazy, fine
lut_nuclides = lambda df: Remapper(...).generate_lookup_table(...)

# GEOTRACES — lazy, fine (MARIS ref only, no provider data needed)
lut_nuclides = lambda: get_lut('NUCLIDE', reverse=False)
```

The new MIFA pattern broke laziness by switching to an eager `Lut` instance.

---

## 3. The architectural insight: callbacks are already recipes

Every `Callback` in the marisco system is a **recipe** in the Wickham/tidymodels
sense:

- Configured at construction time with no data
- Applied to data when `Transformer` runs (`tfm()`)
- Composed into a pipeline via `cbs=[...]`

```
Callback.__init__(config)   →  the recipe specification
Transformer(dfs, cbs=[...]) →  the composed recipe
tfm()                       →  bake() — apply recipe to data
encode()                    →  the top-level orchestrator
```

This means `lut_nuclides` as currently designed (an eager `Lut` instance resolved
at module load time) **breaks the recipe pattern**. Everything else in the system
is lazy; the LUT builder should be too.

`LutCB` (see §4) restores consistency: it is a sub-callback, configured upfront,
resolved lazily when `RemapCB` runs.

---

## 4. The solution: `LutCB`

### What it is

`LutCB` is a lazy callback that:

- **Closes over** its configuration at construction time (`lut_key`, `fixes`,
  `cache_fname`, `src_col`) — no data needed
- **Produces a `Lut`** when called with data (`dfs` or an explicit provider
  DataFrame)
- **Caches `merged`** to disk on first run; subsequent calls load from cache
- Is passed directly to `RemapCB` as the `lut` parameter

### Why the name

The existing vocabulary (`Lut`, `RemapCB`, `-CB` suffix) makes `LutCB` the
natural name. `RemapCB` takes a `lut` — that `lut` is now either an eager `Lut`
instance or a lazy `LutCB`. One new concept, zero new vocabulary.

### NC_DTYPES already has the column metadata

`NC_DTYPES` in `configs.ipynb` already stores `key` and `value` column names for
every MARIS LUT type:

```python
NC_DTYPES = {
    'NUCLIDE': {'fname': 'dbo_nuclide.xlsx', 'key': 'nc_name',  'value': 'nuclide_id'},
    'SPECIES': {'fname': 'dbo_species.xlsx',  'key': 'species',  'value': 'species_id'},
    'BODY_PART': {...},
    ...
}
```

`LutCB` takes the key string and resolves column names from `NC_DTYPES` internally.
The handler author states *what* they want (`'NUCLIDE'`), not *how* to look it up.
This reduces the param count from 6+ to 3 for the common case.

### Where it lives

`LutCB` belongs in `nbs/api/match.ipynb` — it composes the existing MIFA
primitives (`lut_from`, `fuzzy_merge`, `fix_lut`, `Lut`) into the full Apply step.

### Proposed implementation

```python
#| export
class LutCB:
    "Lazy MIFA Apply step: configured upfront, builds Lut from data on demand."
    def __init__(self,
                 lut_key:str,           # NC_DTYPES key ('NUCLIDE', 'SPECIES', ...)
                 fixes:dict={},         # Expert overrides (MIFA Fix step result)
                 cache_fname:str=None,  # Pickle filename under cache_path()
                 src_col:str='value',   # Provider column to match (lut_from convention)
                ):
        store_attr()
        cfg = NC_DTYPES[lut_key]
        self.maris_ref      = get_lut(lut_key, as_df=True)
        self.maris_name_col = cfg['key']    # e.g. 'nc_name' for NUCLIDE
        self.maris_id_col   = cfg['value']  # e.g. 'nuclide_id'

    def __call__(self,
                 src,                       # dfs dict (Case 2) or provider DataFrame (Case 1)
                 col:str=None,              # Column to extract when src is a dfs dict
                 overwrite_cache:bool=False,
                ) -> Lut:
        "Build Lut: infer or use provider LUT, fuzzy-match, apply fixes, cache merged."
        provider_lut = lut_from(src, col) if isinstance(src, dict) else src
        path = cache_path() / self.cache_fname if self.cache_fname else None
        if path and path.exists() and not overwrite_cache:
            merged = pd.read_pickle(path)
        else:
            merged = fuzzy_merge(provider_lut, self.maris_ref,
                                 left_on=self.src_col, right_on=self.maris_name_col)
            if path: merged.to_pickle(path)
        fixed = fix_lut(merged, self.fixes, self.maris_ref,
                        left_on=self.src_col, right_on=self.maris_name_col,
                        id_col=self.maris_id_col)
        return Lut(fixed, key_col=self.src_col, val_col=self.maris_id_col)
```

### Two provider cases

`LutCB.__call__` handles both MIFA usage patterns:

**Case 1 — provider supplies an explicit nomenclature table** (e.g. HELCOM
RUBIN_NAME.csv). Pass the DataFrame directly; set `src_col` at init to name the
matching column:

```python
lut_species = LutCB('SPECIES', fixes=fixes_species,
                     cache_fname='species_helcom.pkl', src_col='SCIENTIFIC NAME')
# call site:
lut = lut_species(provider_df)   # provider_df has 'SCIENTIFIC NAME' column
```

**Case 2 — infer unique values from the data** (e.g. nuclide names scattered
across all group DataFrames). Pass the full `dfs` dict and the column name:

```python
lut_nuclides = LutCB('NUCLIDE', fixes=fixes_nuclide_names, cache_fname='nuclides_helcom.pkl')
# call site:
lut = lut_nuclides(dfs, col='NUCLIDE')
```

---

## 5. Changes required in `RemapCB`

`RemapCB` currently resolves `lut` eagerly at `__init__`:

```python
self.lut = lut if isinstance(lut, dict) else dict(zip(lut.merged[lut.key_col], lut.merged[lut.val_col]))
```

It needs to accept a `LutCB` and resolve it lazily — using `tfm.dfs` (available
via the `tfm` argument already passed to `each_grp`) and reusing `self.col_src`
as the `col` argument:

```python
class RemapCB(PerGroupCB):
    def __init__(self,
                 lut: dict|Lut|LutCB,
                 col_remap: str,
                 col_src: str,
                 default_val: int=0,
                 grps: list[str]=None,
                ):
        store_attr()
        self._lut_dict = None  # deferred if LutCB

    def _resolve(self, tfm):
        if self._lut_dict is not None: return
        lut = self.lut(tfm.dfs, col=self.col_src) if isinstance(self.lut, LutCB) else self.lut
        self._lut_dict = lut if isinstance(lut, dict) else dict(zip(lut.merged[lut.key_col], lut.merged[lut.val_col]))

    def each_grp(self, grp, df, tfm):
        self._resolve(tfm)
        df[self.col_remap] = (df[self.col_src]
            .apply(lambda x: x.strip() if isinstance(x, str) else x)
            .map(self._lut_dict).fillna(self.default_val).astype(int))
```

Key point: `self.col_src` (already on `RemapCB`) is reused as `col` when calling
`LutCB`. No new parameter needed — the two concepts were always the same column.

---

## 6. The MIFA dual role in handler notebooks

The MIFA cells in a handler notebook serve two completely different purposes that
`nbdev` makes structurally explicit:

### Closed box — production (exported cells)

```python
#| exports
fixes_nuclide_names = {          # the persisted human expertise
    'cs134137': 'cs134_137_tot',
    'k-40': 'k40',
    ...
}

#| exports
lut_nuclides = LutCB('NUCLIDE', fixes=fixes_nuclide_names, cache_fname='nuclides_helcom.pkl')
```

These two cells are the entire production artifact. `lut_nuclides` is a lazy
callback ready to be passed to `RemapCB`. `fixes_nuclide_names` is the durable
record of every expert decision.

### Open box — maintenance interface (`#| eval: false` cells)

```python
#| eval: false
# Step 1 — Match (slow, needs data, human reviews output)
provider_lut = lut_from(dfs, 'NUCLIDE')
maris_ref = get_lut('NUCLIDE', as_df=True)
merged = fuzzy_merge(provider_lut, maris_ref, left_on='value', right_on='nc_name')
merged.query('score > 0')    # Step 2 — Inspect: review borderline matches

# Step 3 — Fix: update fixes_nuclide_names above, then verify:
fixed = fix_lut(merged, fixes_nuclide_names, maris_ref,
                left_on='value', right_on='nc_name', id_col='nuclide_id')
fixed[fixed['score'] > 0]    # should be empty

# Step 4 — Apply: verify the LutCB produces correct results
lut = lut_nuclides(dfs, col='NUCLIDE')
```

The `#| eval: false` boundary is the **maintenance hatch** — cells you open when
data changes and new/unexpected nomenclature appears. Run them interactively,
inspect borderline matches, update `fixes_nuclide_names`, and on the next
`encode()` call `LutCB` regenerates the cache from the updated fixes.

### The cache mechanism

- **Normal production run**: `LutCB` loads `merged` from the pickle cache — fast,
  no fuzzy matching, no data needed
- **Data changes / new nomenclature**: Run MIFA cells interactively, update
  `fixes_nuclide_names`, call `lut_nuclides(dfs, col='NUCLIDE', overwrite_cache=True)`
  to regenerate
- **Cache does not exist yet**: `LutCB.__call__` computes `merged` via `fuzzy_merge`
  and saves it; subsequent calls are fast

---

## 7. What stays the same in handler notebooks

- `fixes_xxx_names` dicts — still exported, still the primary artifact of the MIFA
  Fix step
- MIFA `#| eval: false` cells — still present, still the human-in-the-loop
  interface
- `encode()` function — largely unchanged; `lut_nuclides(dfs, col='NUCLIDE')` is
  called once before constructing `Transformer`, or `RemapCB` resolves it
  transparently if `RemapCB` is extended (see §5)

---

## 8. Files to change

| File | Change |
|---|---|
| `nbs/api/match.ipynb` | Add `LutCB` class (export) |
| `nbs/api/callbacks.ipynb` | Extend `RemapCB` to accept and lazily resolve `LutCB` |
| `nbs/handlers/helcom.ipynb` | Replace exported `lut_nuclides = Lut(fixed, ...)` with `LutCB(...)` |
| `nbs/handlers/ospar.ipynb` | Migrate from `Remapper` lambda to `LutCB` |
| `nbs/handlers/geotraces.ipynb` | Migrate (simple case: `LutCB` with no fixes needed) |
| `nbs/handlers/tepco.ipynb` | Migrate |
| `nbs/handlers/maris_legacy.ipynb` | Migrate |

---

## 9. Design principles applied

**SICP λ3 — Closure as object**: `LutCB.__init__` captures the configuration as
its defining environment. `__call__` is the single operation exposed. The class
*is* a closure over `fixes`, `maris_ref`, `cache_fname`.

**SICP λ4 — Wishful thinking**: The exported cell reads as a declaration —
"nuclide lookup is MIFA over NUCLIDE with these fixes and this cache" — before
any data exists. Implementation details are hidden.

**fastai/Howard — abstract when the pattern recurs**: `LutCB` is justified because
the same pattern appears in every handler. One class, learned once, used
everywhere.

**fastai/Howard — name the data, not the machinery**: `lut_nuclides` is the
meaningful name in the handler notebook. `LutCB` is the class. The name on the
instance carries the semantic weight.

**nbdev structural discipline**: `#| eval: false` is not just a performance
annotation — it is the architectural boundary between the production pipeline
(exported) and the maintenance interface (interactive only).
