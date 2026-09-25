# recipes/riparian_buffer/ — T4 synthesis output

**Status: synthesised, NOT review-signed.** The two `T4_<family>.json` files are the machine
output of `synthesise_family` over the riparian T4 evidence sweep (49 EV units, ruleset
v1.5.0). They are the *candidate* T4 slice — `T4_suitability_mappings.csv`, the file the
dashboard and the pipeline read, is **not written yet**: the unit defect below is fixed, but
the variable-identity question is still open and it decides what the table should say.

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
| natural_restored | 23 | 1 (`distance_to_waterbody`, 0.05–0.21 km) | 10 |
| planted | 26 | 1 (`distance_to_waterbody`, ≤0.03 km) | 9 |

Most units encode a qualitative `direction` rather than a numeric threshold, so they carry no
shape params and synthesise to no row. Notably `slope` has the highest support in the planted
family (40%, 4 sources) and still yields **no threshold** — the sweep captured that slope
matters without capturing a value. That is a real coverage gap, not a synthesis failure.

## Open defects — rule on these before writing `T4_suitability_mappings.csv`

1. ~~**Metres vs kilometres.**~~ **FIXED in the engine.** `_harmonise` now folds unit
   spellings (`degrees_c`/`degC`, `mm_yr`/`mm/year`) to a common token, applies the
   conversion `VONT.unit_conversions` declares, and **refuses** a mismatch it has no rule
   for instead of emitting the raw number under the wrong label. The riparian rows now read
   0.05–0.21 km (= 50–210 m). A flat 1 dp rounding in `_weighted_median` was annihilating
   the converted values (30 m → 0.03 km → `0.0`), so rounding is now significant-figure
   aware below 1. Knock-on: `soil_drainage` no longer synthesises at all — its source's `1`
   is a depth-to-water-table class in metres against a canonical `ordinal_1_7`, so the row
   is refused rather than emitted (it was `abs_max: 1.0` before).
2. **Is this `distance_to_waterbody` or `riparian_buffer_width`?** The 13 units tagged
   `distance_to_waterbody` mostly describe the *buffer's own extent* (how far out from the
   channel the strip is planted/protected), not the site's distance to the nearest water
   body. `riparian_buffer_width` was added to `VONT` in this pass for that meaning.
   Re-tagging 13 units is a QA decision, so they are left as extracted.

Supporting flag for the open question: `distance_to_waterbody` carries
`min_meaningful_resolution_m: 100`, which 30 m thresholds sit below — a variable whose
thresholds are finer than its own stated meaningful resolution is usually the wrong
variable. Until that is ruled on, a km-scaled `distance_to_waterbody` row carrying
buffer-width evidence is technically correct and semantically doubtful, which is why the
recipe table stays unwritten.

## New `VONT` entries raised by this sweep (all `pending_review`)

`riparian_buffer_width` · `riparian_vegetation_gap` · `regeneration_potential`. The third
collides with an existing alias on `rootstock_presence` ("regeneration potential"), which is
FMNR living-stump specific — reviewers to rule keep-distinct vs merge.
