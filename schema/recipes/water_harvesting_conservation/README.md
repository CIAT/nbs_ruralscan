# recipes/water_harvesting_conservation/ — draft-0 example

**Status: draft 0 — worked example, not yet review-signed.** Populated schema tables for Water Harvesting &
Conservation (`nbs_id = water_harvesting_conservation`, cluster `soil_water`). Demonstrates the schema spec
([`../../spec.md`](../../spec.md)) and is the second worked recipe alongside agroforestry.

## What's here (per-NbS tables — carry `nbs_id`)

| File | Table | Rows |
|---|---|---|
| `T0_nbs_registry.{csv,json}` | T0 — NbS Registry | 1 |
| `T3_nbs_hazard_farming.{csv,json}` | T3 — NbS × Hazard × Farming | 8 |
| `T4_suitability_mappings.{csv,json}` | T4 — Suitability Mappings | 9 |
| `T6_nbs_scorecard.{csv,json}` | T6 — NbS Scorecard | 7 |

The cross-NbS tables this recipe joins to — `T1_data_registry`, `T2_climate_risk`, `T5_opportunity_space`,
`T7_geographic_context` — live at the [schema root](../../) and merge rows from every recipe. The water-harvesting
T4 introduces hydrological variables (drainage density, Strahler stream order, hydrologic soil group, land-cover
eligibility) on top of the shared biophysical datasets.

## Provenance

Generated from `RuralNbS_WaterHarvesting_Tables_T0-T7.xlsx` (archived at [`../../design/`](../../design/)).
This recipe also corresponds to Benson's existing water-harvesting methodology recipe
([`methodology/recipes/water_harvesting.md`](../../../methodology/recipes/water_harvesting.md)), the source of
several framework primitives (fuzzy membership functions, hybrid AHP + CRITIC + Entropy weighting).

Both formats describe the same content: **JSON is the machine-readable source of truth; CSV is the
human-editing view.** Fix the JSON, then regenerate the CSV.

## Naming note (for reconciliation)

The workbook sets `nbs_id = water_harvesting_conservation`, so this recipe folder matches that ID. The
methodology file is `methodology/recipes/water_harvesting.md` and `CLAUDE.md` cites `water_harvesting` as the
NbS-ID example. **These should be reconciled to a single canonical `nbs_id`** before the schema stabilises —
raise an issue rather than silently editing.

## Shared-layer deduplication (June 2026)

This workbook was authored standalone and aliased shared framework entities (datasets, risk variables,
priority layers, geographic contexts) with a `_wh` suffix. Those clones have been collapsed into the canonical
shared rows at the [schema root](../../) so the framework layer is one source of truth — e.g. this recipe's
T6 now references `rural_poverty_headcount` and `climate_drought_hazard`, not the `_wh` aliases. Genuinely
water-specific entries (e.g. `srtm_dem_30m`, `runoff_potential_index`, `groundwater_recharge_potential`,
`agricultural_water_deficit`, `flood_risk`, `dryland_south_asia`) were retained. Full log:
[`../../DEDUP_NOTES.md`](../../DEDUP_NOTES.md). Three items await Brayden's M2 sign-off (T2 weight reconciliation,
flood-hazard method, erosion-vs-degradation).

## Validation status (draft-0)

- All foreign keys validated against the merged root tables — including nested `context_overrides`,
  `baseline_dataset_id` and `future_dataset_ids` — no broken links.
- A pre-existing dangling reference (`chelsa_precip_ssp245_2050_wh`, never catalogued in T1) was repointed to
  `chelsa_bioclim_ssp245_2050`.
- All required fields populated; optional fields blank rather than omitted.

> Draft-0 content still needs literature-team review before the pilot review milestone.
