# recipes/riparian_buffer/ — T4 synthesis output

**Status: synthesised, NOT review-signed.** The two `T4_<family>.json` files are the machine
output of `synthesise_family` over the riparian T4 evidence sweep (49 EV units, ruleset
v1.5.0). They are the *candidate* T4 slice — `T4_suitability_mappings.csv`, the file the
dashboard and the pipeline read, is **deliberately not written yet**: two defects below have
to be ruled on first, and writing the table now would bake a wrong number into the recipe.

## What's here

| File | Contents |
|---|---|
| `T0_nbs_registry.{csv,json}` | T0 — NbS registry row |
| `T4_riparian_buffer__natural_restored.json` | 1 synthesised row (from 23 units) |
| `T4_riparian_buffer__planted.json` | 2 synthesised rows (from 26 units) |

T3/T6 are deferred (2026-09-17 scope cut) and are not populated for this NbS.

## How these were generated

```python
from nbs_ruralscan.recipe.family import synthesise_family, save_family
res = synthesise_family(units, tiers, family=<family>, corpus_n=<n>, group_map=VONT.group_id,
        canonical_units=VONT.canonical_unit, dataset_ids=VONT.candidate_dataset_ids,
        categories=SRC.source_category, floor_pct=20.0, allow_crop_scope=False)
```

`corpus_n` is the family's PRISMA screened-in count summed over the four discovery processes
in `SRCH` (`n_included`): **natural_restored 15**, **planted 12**. `tiers` are read from
`SRC.benchmark_tier` — all ten are Pete's **first-pass** tiers and are pending QA, so every
`paper_support_pct` below is provisional (tier weighting feeds the weighted median).

## Yield

| Family | units in | rows with params | variables that produced no params |
|---|---|---|---|
| natural_restored | 23 | 1 (`distance_to_waterbody`) | 10 |
| planted | 26 | 2 (`distance_to_waterbody`, `soil_drainage`) | 8 |

Most units encode a qualitative `direction` rather than a numeric threshold, so they carry no
shape params and synthesise to no row. Notably `slope` has the highest support in the planted
family (40%, 4 sources) and still yields **no threshold** — the sweep captured that slope
matters without capturing a value. That is a real coverage gap, not a synthesis failure.

## Open defects — rule on these before writing `T4_suitability_mappings.csv`

1. **Metres vs kilometres (blocking).** Every `distance_to_waterbody` EV unit carries
   `"unit": "m"` (values 5–210 m: statutory reserve widths, buffer extents). `VONT`'s
   canonical unit for the variable is **km**, and `synthesis._harmonise` only converts
   percent↔degrees — it passes every other value through unchanged while labelling the row
   with the canonical unit. The rows therefore read `abs_max: 30` **km** where the evidence
   says 30 **m**. `VONT.unit_conversions` already declares `{"m->km": "/1000"}`; the engine
   does not apply it. Fix in the engine (apply the declared conversion, or refuse on an
   unconvertible mismatch) — not by editing the numbers.
2. **Is this `distance_to_waterbody` or `riparian_buffer_width`?** The 13 units tagged
   `distance_to_waterbody` mostly describe the *buffer's own extent* (how far out from the
   channel the strip is planted/protected), not the site's distance to the nearest water
   body. `riparian_buffer_width` was added to `VONT` in this pass for that meaning.
   Re-tagging 13 units is a QA decision, so they are left as extracted.

Supporting flags: `distance_to_waterbody` carries `min_meaningful_resolution_m: 100`, which
30 m thresholds sit below — consistent with defect 2. `soil_drainage` synthesises
`abs_max: 1.0` on `ordinal_1_7` from a source whose own `1` is a depth-to-water-table class
in metres — same unit-provenance family of problem.

## New `VONT` entries raised by this sweep (all `pending_review`)

`riparian_buffer_width` · `riparian_vegetation_gap` · `regeneration_potential`. The third
collides with an existing alias on `rootstock_presence` ("regeneration potential"), which is
FMNR living-stump specific — reviewers to rule keep-distinct vs merge.
