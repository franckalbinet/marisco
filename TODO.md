# TODO / Known issues

## Bugs

- **`NC_VARS` duplicate key** (`nbs/api/configs.ipynb`): `SMP_ID` appears twice — first mapped to `'id'`, then to `'smp_id'`. The second silently overrides the first. The `id` variable still exists in the CDL and the template; decide whether `SMP_ID` should map to `id` or `smp_id` and remove the duplicate.

## Handler fixes

- **helcom** (`nbs/handlers/helcom.ipynb`): uses `SALINITY` and `TEMPERATURE` as DataFrame column names, but `NC_VARS` defines `SAL` and `TEMP`. These callbacks need to be updated to use the correct names.
