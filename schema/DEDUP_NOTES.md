# Shared-layer deduplication — decision log (June 2026)

The two draft-0 workbooks (Agroforestry, Water Harvesting & Conservation) were authored standalone. As a
result the **water-harvesting** workbook aliased shared framework entities with a `_wh` suffix instead of
reusing the existing ones. This collapsed those clones so the framework layer (T1/T2/T5/T7) is a single source
of truth, while keeping genuinely NbS-specific entries.

**Principle.** Tables without an `nbs_id` (T1 datasets, T2 risk variables, T5 priority layers, T7 contexts) are
the shared *framework* layer — one row per real-world concept, referenced by every recipe. Per-NbS tables
(T0/T3/T4/T6) were left untouched except for repointing references.

After the change: all foreign keys (including nested `context_overrides`, `baseline_dataset_id`,
`future_dataset_ids`) resolve; T2 weights sum to 1.0 per scenario; CSV mirrors JSON.

## Counts

| Table | Before | After | Removed |
|---|---|---|---|
| T1 Data Registry | 27 | 21 | 6 collapsed (2 renamed in place) |
| T2 Climate Risk | 14 | 11 | 3 collapsed |
| T5 Opportunity Space | 16 | 14 | 2 collapsed (2 renamed in place) |
| T7 Geographic Context | 21 | 15 | 6 collapsed (2 renamed in place) |

## Collapsed (clone → canonical; clone row removed, references repointed)

**T1 datasets** — identical products, aliased:

- `world_bank_poverty_pip_wh` → `world_bank_poverty_pip`
- `gaez_v4_aez33_wh` → `gaez_v4_aez33`
- `fao_farming_systems_wh` → `fao_farming_systems`
- `isric_soilgrids250_wh` → `isric_soilgrids250_v2`
- `spei_global_v26_wh` → `spei_global_v26`
- `worldpop_pop_density_wh` → `worldpop_population_density`

**T2 risk variables** — same metric/dataset:

- `drought_spei12_baseline_wh` → `drought_spei12_baseline`
- `drought_projected_ssp245_wh` → `drought_spei12_ssp245_2050`
- `agricultural_population_exposure` → `population_exposure_rural`

**T5 priority layers** — same concept (and same dataset after T1 collapse):

- `rural_poverty_headcount_wh` → `rural_poverty_headcount`
- `drought_hazard_wh` → `climate_drought_hazard`

**T7 contexts** — exact clones of an existing context (and unreferenced by any T4 override):

- `sub_humid_tropics_wh`, `highland_tropics_wh`, `humid_tropics_wh`, `mixed_rainfed_wh`,
  `agro_pastoral_millet_sorghum_wh`, `highland_mixed_wh` → their non-suffixed twins.

## Kept distinct (genuinely different — `_wh` alias stripped, not merged)

- T1 `srtm_dem_30m_wh` → **`srtm_dem_30m`**: 30 m DEM, deliberately finer than agroforestry's `srtm_dem_90m`
  (water harvesting needs finer terrain for drainage/runoff). Both retained.
- T1 `worldclim_v2_precip_wh` → **`worldclim_v2_precip`**: monthly precipitation layer, kept separate from the
  bioclim summary `worldclim_v2_bioclim` rather than asserting equivalence.
- T5 `soil_erosion_risk_wh` → **`soil_erosion_risk`**: related to but not the same as `soil_degradation_risk`
  (slope/DEM-based erosion vs SoilGrids degradation). *Candidate for a future merge — left distinct for now.*
- T5 `flood_risk_wh` → **`flood_risk`**: a new opportunity layer (agroforestry had no flood layer).
- T7 `dryland_south_asia_wh` → **`dryland_south_asia`**, `east_africa_semiarid_wh` → **`east_africa_semiarid`**:
  new regional contexts with no existing twin.

## Fixed (pre-existing data-quality issue in the source workbook)

- Water T4 mapping `wh_rainfall_global` referenced `chelsa_precip_ssp245_2050_wh` in `future_dataset_ids`, but
  that dataset was **never catalogued in T1** (a dangling foreign key). Repointed to the canonical future
  climate dataset `chelsa_bioclim_ssp245_2050`. *(This was missed by the earlier FK check, which validated only
  `dataset_id`; validation now also covers `baseline_dataset_id`, `future_dataset_ids` and
  `context_overrides`.)*

## ⚠ Needs methodology sign-off (Brayden — M2)

1. **Merged T2 baseline weights are provisional.** With the duplicates removed, the combined baseline risk set
   summed to 1.556. Weights were **renormalised proportionally** to sum to 1.0 so the invariant holds and
   validation passes — but proportional scaling simply preserves each workbook's internal emphasis and gives
   agroforestry-origin variables ~64% of total weight purely because it contributed more variables. The
   *correct* combined weighting is a methodology decision, not a mechanical one. Revisit before the pilot review.
2. **Two flood-hazard methods now coexist** in T2: `flood_exposure_baseline` (CHELSA precipitation-based,
   agroforestry origin) and `flood_hazard_runoff_depth` (SCS-CN runoff composite, water-harvesting origin).
   Left as distinct rows — decide whether the shared risk formulation should use one canonical flood method.
3. **`soil_erosion_risk` vs `soil_degradation_risk`** (T5) — confirm whether these stay distinct or merge.

## Reproducibility

Originals are recoverable from the archived workbooks in [`design/`](design/). The transformation was applied
by deterministic scripts; the run logs are retained with the working files.
