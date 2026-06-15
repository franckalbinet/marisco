# Simplify Package Initialisation

## Problem

After `pip install marisco` users must run `maris_init`, which downloads Excel LUT files from GitHub and the NetCDF template, then writes a `configs.toml` under `~/.marisco/`. The rest of the package reads that file through a chain of helpers (`cfg()` → `lut_path()` → `*_lut_path()`).

This complexity exists for one reason: LUTs and the NetCDF template are not bundled in the installed package. Everything else follows from that single decision.

**Confirmed constraint:** MARIS staff will not need to test modified LUTs without a package release. Any LUT update → bump version → redeploy. This removes the only justification for the `~/.marisco/` indirection.

---

## What disappears

| Item | Location |
|---|---|
| `maris_init` CLI command | `nbs/cli/init.ipynb` (delete or gut the file) |
| `~/.marisco/` directory | runtime artefact |
| `configs.toml` | runtime artefact |
| `cfg()`, `base_path()`, `lut_path()`, `cache_path()` | `nbs/api/configs.ipynb` |
| All `*_lut_path()` helpers (14 functions) | `nbs/api/configs.ipynb` |
| `CONFIGS` dict (gh/dirs/paths/names sections) | `nbs/api/configs.ipynb` |
| `CONFIGS_CDL` dict (already marked TO BE REMOVED) | `nbs/api/configs.ipynb` |
| `download_file`, `download_files_in_folder` | `nbs/api/utils.ipynb` (also fixes the duplicate-definition bug in TODO.md) |

---

## What changes

### 1. Bundle LUT files and NetCDF template as package data

LUTs already live in `nbs/files/lut/` and the template in `nbs/api/files/nc/`. They need to be declared in `settings.ini` so they ship with the installed package:

```ini
# settings.ini
package_data = marisco=files/lut/*.xlsx files/nc/*.nc
```

Exact syntax depends on nbdev version — check `nbdev_export` docs for `package_data`.

### 2. Replace path helpers with `importlib.resources`

```python
from importlib.resources import files

def lut_path():
    return files('marisco') / 'files/lut'

def nc_tpl_path():
    return files('marisco') / 'files/nc/maris-template.nc'
```

All `*_lut_path()` helpers become inline calls to `lut_path() / fname` — most can be deleted; callers pass the path directly.

### 3. Shrink `CONFIGS` to just Zotero constants

```python
ZOTERO_LIB_ID = '2432820'
# ZOTERO_API_KEY → env var only; no TOML fallback
```

### 4. Cache directory for WoRMS species lookups

The only runtime-writable artefact. Replace `~/.marisco/cache/` with:

```python
from pathlib import Path
def cache_path() -> Path:
    return Path.home() / '.cache' / 'marisco'
```

Or use `platformdirs.user_cache_dir('marisco')` if `platformdirs` is already a dependency.

---

## What stays unchanged

- All `NC_VARS`, `CSV_VARS`, `NC_GROUPS`, `NC_DTYPES`, `CSV_DTYPES` constants — pure data, no change
- `get_lut()` — still loads an Excel file into a dict; caller passes the path
- `Enums` class — unchanged
- `sanitize()`, `NETCDF_TO_PYTHON_TYPE` — unchanged
- `get_time_units()` — update to use `nc_tpl_path()` from `importlib.resources`
- `nc_tpl_name()` — simplify or remove (name is a constant: `'maris-template.nc'`)
- `ZOTERO_LIB_ID` — promoted from nested dict to top-level constant

---

## Implementation order

1. **Verify files are in repo**: confirm LUTs are at `nbs/files/lut/` and template at `nbs/api/files/nc/`. Check that `settings.ini` or `MANIFEST.in` would include them.
2. **Add package data declaration** in `settings.ini`.
3. **Add `lut_path()` and `nc_tpl_path()`** using `importlib.resources` in `configs.ipynb`.
4. **Remove all `*_lut_path()` helpers** — update callers to use `lut_path() / fname` directly or via `NC_DTYPES[key]['fname']`.
5. **Remove `cfg()`, `base_path()`, `CONFIGS`** — fix all call sites.
6. **Simplify `cache_path()`** — remove `cfg()` dependency.
7. **Remove `CONFIGS_CDL`** and its commented-out dead code.
8. **Gut `nbs/cli/init.ipynb`** — remove `maris_init` from `console_scripts` in `settings.ini`.
9. **Remove `download_file` / `download_files_in_folder`** from `utils.ipynb`.
10. **Update `get_time_units()` and `nc_tpl_name()`** to use new path helper.
11. **Run `nbdev-export` + full test suite**.
12. **Update `README` / `index.ipynb`** — remove `maris_init` from setup instructions; new setup is just `export ZOTERO_API_KEY=...`.

---

## Expected outcome

- `configs.py` shrinks from ~650 lines to ~100.
- Setup: `pip install marisco` + `export ZOTERO_API_KEY=...`. No network calls, no mutable state outside cache.
- Removes the duplicate `download_file`/`download_files_in_folder` bug (TODO.md).
- `CONFIGS_CDL` dead code removed (TODO.md).
- `maris_init` removed (TODO.md).
