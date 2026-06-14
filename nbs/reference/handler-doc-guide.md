# Handler documentation guide

## Who are we writing for?

Handler notebooks are **how-to guides** in the Diátaxis sense: goal-oriented directions aimed at
already-competent users — data providers who want to understand exactly what was done to their
data and why, not Python internals. The audience knows their own data well; they need to see
each curation decision explained and evidenced, not taught from scratch.

A how-to guide is "action and only action" — no digressions, no teaching. Each pipeline section
must be **problem-centred**: it names a real data-quality issue in the raw input, shows what was
done about it, and demonstrates the result. That recipe analogy from Diátaxis fits well: clear
objective, focused execution, output you can verify.

Each pipeline-step section is problem-centred: a short prose paragraph names the raw-data issue and what was done about it, followed by the callback and an example output. The prose carries the narrative — no `### Before / Why / Result` subheadings needed; those labels are redundant with well-written sentences.

Quarto callouts (`::: {.callout-important}`) flag known data-quality issues or requests to
the provider for future releases.

## Export directives: `#| export` vs `#| exports`

Use the right directive based on what the cell contains:

| Content | Directive | Reason |
|---|---|---|
| Callback classes | `#| export` | Hides source; the def signature + docstring are what providers see |
| Lookup tables, mappings, constants passed to callbacks | `#| exports` | The *values* are the content — providers must see the actual mapping |

`#| exports` shows raw Python source as a collapsible "Exported source" block, anchored to the
nearest preceding symbol heading. For constants defined immediately before a callback class, they
will appear under that class's heading — which is contextually appropriate since they are the
arguments passed to it. Add a short `# comment` to each constant explaining its purpose, so the
block is self-documenting when expanded.

```python
#| exports
# Metadata columns always kept as identifiers when reshaping wide → long
common_coi = ['yyyy-mm-ddThh:mm:ss.sss', ...]

# Regex patterns identifying radionuclide measurement columns
nuclides_pattern = ['^TRITI', ...]
```

The rendered page offers a **source** link (top-right of each symbol heading) for developers who
want the full class implementation.

## Structure of each pipeline-step section

```
## Step name                          ← H2 section, matches the pipeline concern

Markdown paragraph: name the raw-data issue and what the callback does about it.
The prose carries the narrative — no ### Before / Why / Result subheadings.

#| exports                            ← if a lookup table or mapping drives the step
NUCLIDE_LUT = { ... }                 ← source shown; the values ARE the content

#| export                             ← callback class; no show_doc() needed
class MyTransformCB(...):
    "One-line docstring: what it does."
    def __init__(self, param: type,   ← docments on every param
                 ...): store_attr()   ← fastcore is star-imported; no fc. prefix

# — Cell 1: run the cumulative pipeline up to this step
tfm = Transformer(df, cbs=[..., MyTransformCB(...)])
df_test = tfm()

# — Cell 2: minimal print + machine-checked assertions
print(f'...')           ← one line of visible evidence
test_eq(...)            ← fails loudly if the transformation breaks an invariant
test_eq(...)

::: {.callout-important}              ← optional: feedback to provider
## FEEDBACK TO DATA PROVIDER
Note that ...
:::
```

Usage cells carry **no directive** — they run during `nbdev_test` so live output is captured and
assertions double as regression tests. `show_doc()` is not used; nbdev renders callback docs
automatically from the class definition.

## Docments rules

Every `__init__` parameter needs an inline `# comment` immediately after the type annotation.
nbdev picks these up for the auto-generated API docs.

```python
def __init__(self,
             phase: dict,             # Phase code → {FILT, group} mapping
             var_name: str='NUCLIDE'  # Column containing nuclide names with embedded phase codes
             ):
```

## Class docstrings — dual purpose

Every callback docstring is:
1. The description shown under its heading in the rendered docs
2. Appended to `tfm.logs` at runtime → serialised into the NetCDF global attribute
   `publisher_postprocess_logs`

Write it as **one sentence** that stands alone as an audit-trail entry: what was done,
and if non-obvious, why.

```python
# Good — informative in both contexts
"Shift longitudes from [0, 360] convention to MARIS [-180, 180] by subtracting 180."

# Bad — too vague to serve as an audit trail entry
"Unshift longitudes."
```
