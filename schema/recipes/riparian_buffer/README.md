# recipes/riparian_buffer/ — T4 synthesis output

**Status: synthesised and written, NOT review-signed.** `T4_suitability_mappings.csv` — the
table the dashboard and the pipeline read — is generated from the riparian T4 evidence sweep
(49 EV units, ruleset v1.5.0) by `scripts/synthesise-recipe.py riparian_buffer`. Both defects
that blocked it are resolved (below). What still needs a human: the QA review of the 49 units,
Pete's ten first-pass `benchmark_tier` values, and dataset-fitness sign-off on the two
hydrography layers this pass added to `T1`.

## What's here

| File | Contents |
|---|---|
| `T0_nbs_registry.{csv,json}` | T0 — NbS registry row |
| `T4_suitability_mappings.{csv,json}` | the recipe table — 2 rows, one per family |
| `T4_riparian_buffer__natural_restored.json` | 1 synthesised row + selection table (from 23 units) |
| `T4_riparian_buffer__planted.json` | 1 synthesised row + selection table (from 26 units) |

T3/T6 are deferred (2026-09-17 scope cut) and are not populated for this NbS.

## How these were generated

```bash
python3 scripts/synthesise-recipe.py riparian_buffer   # then generate.py schema
```

Every input is read from the registers, never hand-passed — tiers from `SRC.benchmark_tier`,
grouping/units/datasets/conversions from `VONT`, grey-discount categories from
`SRC.source_category`. Re-run it after any QA decision and the table rebuilds.

`corpus_n` is the family's PRISMA screened-in count summed over the four discovery processes
in `SRCH` (`n_included`): **natural_restored 15**, **planted 12**. `tiers` are read from
`SRC.benchmark_tier` — all ten are Pete's **first-pass** tiers and are pending QA, so every
`paper_support_pct` below is provisional (tier weighting feeds the weighted median).

## Yield

| Family | units in | rows with params | thresholds | variables that produced no params |
|---|---|---|---|---|
| natural_restored | 23 | 1 (`distance_to_waterbody`) | 50–210 m | 10 |
| planted | 26 | 1 (`distance_to_waterbody`) | ≤30 m | 9 |

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
2. ~~**Is this `distance_to_waterbody` or `riparian_buffer_width`?**~~ **RULED 2026-09-25:
   they stay `distance_to_waterbody`, and its canonical unit changes km → m.** Three things
   decided it. `FAM` gives both families `spatial_product_type = zonal_linear` with a
   `dominant_limiting_factor` that begins "watercourse proximity" — the band *is* the
   product and proximity *is* the constraint, so these values are its threshold. All 13
   quotes measure outward from the watercourse, in metres. And `riparian_buffer_width`
   already has a separate, non-overlapping job: the width of the **existing** buffer as a
   restoration-priority indicator (zhao13's MBW) — the same paper supplies both, and the
   split is coherent. Re-tagging all 13 would have left the family with no gating variable
   at all, contradicting its own limiting factor. Blast radius of the unit change: nil —
   `distance_to_waterbody` appears in 13 EV units, all riparian, with no `BIND` row and no
   other recipe, and its `VONT` row was never ratified (`pending_review`, issue #103).

## The resolution caveat that survives the decision

`min_meaningful_resolution_m` moved 100 → 30 to match the evidence, but **the data does not
go that fine**. The binding is `merit_hydro_v1` (~90 m), so a 30 m band cannot be resolved
from the global stream network: the T4 threshold is scoping-grade, and a national hydrography
upload is preferable wherever one exists (recorded in the `BIND` `fitness_note` and in `T1`
`limitations`). This is the resolution-audit item for QA sign-off, not a reason to carry the
wrong unit.

## Added to the shared tables by this pass

| Table | Row | Why |
|---|---|---|
| `T1` | `merit_hydro_v1` | the stream network riparian distance is measured from (~90 m, GEE; **non-commercial licence clause — confirm before operational use**) |
| `T1` | `jrc_global_surface_water_v1_4` | 30 m water-surface complement for lakes and wide rivers |
| `BIND` | `distance_to_waterbody__global` (+ `…_water_bodies`) | global default binding, rank 1 / 2 |

Both `T1` rows need **dataset-fitness sign-off** — they were chosen to unblock the recipe's
required `dataset_id`, not ratified.

## New `VONT` entries raised by this sweep (all `pending_review`)

`riparian_buffer_width` · `riparian_vegetation_gap` · `regeneration_potential`. The third
collides with an existing alias on `rootstock_presence` ("regeneration potential"), which is
FMNR living-stump specific — reviewers to rule keep-distinct vs merge.
