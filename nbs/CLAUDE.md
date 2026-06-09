# nbdev workflow

All code lives in notebooks under `nbs/`. Python modules in `marisco/` are auto-generated — never edit them directly.

## Edit → export cycle

```bash
# After editing any notebook:
nbdev-export      # regenerates marisco/*.py and marisco/**/*.py
nbdev-test        # runs notebook tests
```

## Regenerating the NetCDF template

`nbs/api/files/nc/maris-template.nc` is generated from the CDL definition:

```bash
# Requires netCDF-C utilities (ncgen)
ncgen -4 -o nbs/api/files/nc/maris-template.nc nbs/api/files/cdl/maris.cdl
cp nbs/api/files/nc/maris-template.nc ~/.marisco/
```

## Documentation sidebar

`nbs/sidebar.yml` controls the Quarto documentation site navigation. It is **not** auto-generated — edit it manually when adding new notebooks.

## Key notebook locations

```
nbs/index.ipynb                      ← package overview and getting started
nbs/api/callbacks.ipynb              ← Callback, Transformer, built-in callbacks
nbs/api/configs.ipynb                ← NC_VARS, NC_GROUPS, NC_DTYPES, LUT helpers
nbs/api/metadata.ipynb               ← GlobAttrsFeeder, ZoteroCB, BboxCB
nbs/api/encoders.ipynb               ← NetCDFEncoder
nbs/api/decoders.ipynb               ← NetCDFDecoder
nbs/api/utils.ipynb                  ← Remapper, ddmm_to_dd, ExtractNetcdfContents
nbs/api/files/cdl/maris.cdl         ← NetCDF4 template definition (CDL)
nbs/api/files/nc/maris-template.nc  ← NetCDF4 template (committed binary)
nbs/handlers/helcom.ipynb            ← reference handler (most complete)
nbs/cli/init.ipynb                   ← maris_init
nbs/cli/to_nc.ipynb                  ← maris_to_nc
nbs/cli/db_to_nc.ipynb               ← maris_db_to_nc
nbs/cli/nc_to_csv.ipynb              ← maris_nc_to_csv
```
