# nbdev workflow

All code lives in notebooks under `nbs/`. Python modules in `marisco/` are auto-generated — never edit them directly.

## toolslm / fastcore.tools parameter reference

Key parameters for notebook access tools (rule and examples in root `CLAUDE.md`):

- `folder2ctx`: `sigs_only=True` (function signatures only), `out=False` (skip outputs), `file_re` (filter by filename pattern), `max_size`/`max_total` (size limits), `recursive=True`
- `nb2xml`: `out=False` (skip outputs), `ids=True` (include cell ids), `nums=False` (line numbers)
- `rg`: use directly via Bash (`rg -n "pattern" file`) — `fastcore.tools.rg` conflicts with Claude Code's shell wrapper
- `view`: `view_range=(start, end)` for line slicing, `nums=True` for line numbers

## Edit → export cycle

After **every** notebook edit, run both commands — export first, then test the specific notebook:

```bash
uv run nbdev-export
uv run nbdev-test --path nbs/path/to/notebook.ipynb
```

Run the full test suite only when touching core abstractions (e.g. `callbacks.ipynb`) that other notebooks depend on:

```bash
uv run nbdev-test
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

## Design checklist

Apply these when adding a new callback, handler, or core API function. Full principles and rationale: `nbs/reference/sicp-design-memento.md`.

### Design
- [ ] What abstraction level am I at? What are my primitives here?
- [ ] Can I name the *what* without specifying the *how*?
- [ ] Is there an abstraction barrier I should define first?
- [ ] Would wishful thinking produce a cleaner interface than bottom-up building?
- [ ] Am I solving the general problem or a special case? Should I solve the general one?

### Composition & state
- [ ] Is this function pure? If not, is the impurity isolated and explicit?
- [ ] Could this be expressed as a composition of existing higher-order functions?
- [ ] Am I introducing mutable state? Can I make it local and bounded?
- [ ] Is there a lazy/streaming version that decouples production from consumption?
- [ ] If I describe this as data, can it be inspected, tested, or replayed?

## Coding style

Follows the [fastai style guide](https://docs.fast.ai/dev/style.html) and [abbreviation guide](https://docs.fast.ai/dev/abbr.html).

### Naming

- **Huffman coding**: frequently used / generic concepts get shorter names; rare or specific ones get longer names.
- CamelCase for classes, `under_score` for everything else.
- Assume domain knowledge — use standard terminology (`kl_divergence`, not `kullback_leibler_divergence`).

**Common abbreviations (use these, don't spell them out):**

| Abbrev | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| `f` | function (short scope) | | `fn` | function (module scope) |
| `x` | input / tensor | | `o` | object |
| `i` | index | | `k`, `v` | key, value |
| `s` | string or plural suffix | | `n_` | count prefix |
| `is_` | boolean predicate | | `to_` | conversion prefix |
| `2` | conversion infix (`name2idx`) | | `tfm` | transform |
| `cfg` | configuration | | `col` | column |
| `idx` | index | | `ds` | dataset |
| `sz` | size | | `n` | number of elements |
| `bs` | batch size | | `pred` | prediction |
| `tok` | token | | `lm` | language model |

### Layout

- Max line width: 160 characters.
- One line = one complete idea; put `if` body on the same line when it fits: `if cond: return x`.
- Ternary over multi-line if/else: `x = a if cond else b`.
- Group related assignments: `self.a,self.b = a,b`.
- No blank lines between related one-liners.
- No automatic linters or formatters.
- Comments explain *why*, not *what*.
