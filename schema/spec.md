# Schema spec — field-level reference (v0.1)

> In-repo Markdown port of `NbS_Schema_Reference_v01_1.docx` (Pete Steward, 7 May 2026).
> Source archived at [`design/NbS_Schema_Reference_v01.docx`](design/NbS_Schema_Reference_v01.docx).
> Entity-relationship diagram: [`design/NbS_ERD_v01.html`](design/NbS_ERD_v01.html) (also published on the Pages site).
> Worked draft-0 examples (Agroforestry · Water Harvesting): CSV + JSON for every table — see [`README.md`](README.md).

This document defines the complete field-level schemas for the eight JSON/tabular structures that form the
analytical backbone of the Rural NbS Scan. They are the authoritative starting point for:

- **Pipeline implementation** — building the data pipeline and MCDA engine. Code always *reads* from these
  files rather than hardcoding values.
- **Literature team (Namita)** — populating the tables for each NbS via human-validated research.
- **Future expansion** — adding an NbS means appending rows, not changing the schema or the code.

All tables link via three foreign keys: `nbs_id` (from T0), `dataset_id` (from T1), `variable_id` (from T5).

## Table overview

| Table | Primary purpose | Owner | Per-NbS? | Location in repo |
|---|---|---|---|---|
| **T0** NbS Registry | Master record per NbS, economic archetype, evidence quality | Namita | yes (`nbs_id`) | `recipes/<nbs_id>/` |
| **T1** Data Registry | Dataset catalog, access routes, citations, limitations | Namita + Benson | no | schema root |
| **T2** Climate Risk Formulation | Risk variables, hazard/exposure formula, double-count guard | Namita (lit) | no | schema root |
| **T3** NbS × Hazard × Farming | Qualitative mitigation-potential matrix | Namita (lit) | yes (`nbs_id`) | `recipes/<nbs_id>/` |
| **T4** Suitability Mappings | Response functions, scenario flags, context overrides | Namita | yes (`nbs_id`) | `recipes/<nbs_id>/` |
| **T5** Opportunity Space Vars | TTL-facing priority layers | Namita + Benson | no | schema root |
| **T6** NbS Scorecard | Likert effects, economic profile per NbS | Namita (lit) + MFL | yes (`nbs_id`) | `recipes/<nbs_id>/` |
| **T7** Geographic Context | AEZ / farming-system / admin context definitions | Benson | no | schema root |

**Placement rule (draft-0):** tables that carry an `nbs_id` column (T0, T3, T4, T6) live under
`schema/recipes/<nbs_id>/`; cross-NbS tables (T1, T2, T5, T7) live at the schema root. Adding an NbS adds a
new recipe folder and appends rows to the root tables.

---

## T0 — NbS Registry

Master record — all other tables join on `nbs_id`. One row per NbS. **Create this first** for a new NbS
before populating any other table. `economic_archetype` maps to the CrossBoundary (2023) framework.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `nbs_id` | string | Required | Unique identifier (snake_case). Primary key for all joins. | `agroforestry` |
| `nbs_name` | string | Required | Canonical display name. | `Agroforestry` |
| `aliases` | string[] | Optional | Alternative names in use. | `['Tree intercropping','Parkland AF']` |
| `cluster` | enum | Required | `tree_based` \| `soil_water` \| `wetland` \| `pastoral` \| `landscape_scale`. | `tree_based` |
| `description_short` | string | Required | 1–2 sentence plain-language summary. | `Deliberate integration of trees…` |
| `description_technical` | string | Required | Technical description for methodology docs. | `Agroforestry encompasses…` |
| `farming_systems_applicable` | string[] | Required | FAO/IIASA farming-system IDs, or `all`. | `['mixed_rainfed','irrigated_paddy']` |
| `implementation_scale` | enum | Required | `plot` \| `farm` \| `landscape` \| `watershed`. | `farm` |
| `establishment_period_years` | object | Required | `{ min, max, typical }`. | `{ min: 2, max: 10, typical: 5 }` |
| `economic_archetype` | enum | Required | `high_capital` \| `long_horizon` \| `fragile_gains` \| `quick_returns`. | `long_horizon` |
| `upfront_cost_usd_ha` | object | Optional | `{ low, high, currency, source_note }`. | `{ low: 200, high: 800, … }` |
| `recurrent_cost_level` | enum | Required | `very_low` \| `low` \| `moderate` \| `high` \| `very_high`. | `moderate` |
| `time_to_benefit_years` | object | Required | `{ min, max }`. | `{ min: 5, max: 10 }` |
| `carbon_credit_eligible` | boolean | Required | Typically eligible for carbon finance. | `true` |
| `is_active` | boolean | Required | Included in the current pipeline. | `true` |
| `evidence_quality` | enum | Required | `strong` \| `moderate` \| `limited` \| `emerging`. | `strong` |
| `primary_references` | string[] | Required | Key supporting literature. | `['Mercer 2004','Jose 2009']` |
| `last_updated` | date | Required | ISO 8601. | `2026-05-07` |
| `updated_by` | string | Required | Last editor. | `namita.joshi` |

---

## T1 — Data Registry

Dataset catalog — every dataset used anywhere in the analysis must have a record here. The pipeline looks up
datasets here rather than hardcoding URLs. `download_function_ref` points to a download/GEE-access script in
the repo.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `dataset_id` | string | Required | Unique identifier (snake_case). | `chelsa_precipitation_v21` |
| `dataset_name` | string | Required | Full descriptive name. | `CHELSA Precipitation v2.1` |
| `analytical_module` | enum | Required | `climate_hazard` \| `climate_impact` \| `structural_suitability` \| `adaptive_capacity` \| `exposure` \| `opportunity_space` \| `geographic_context`. | `climate_hazard` |
| `variable_name` | string | Required | Specific variable represented. | `mean_annual_precipitation` |
| `variable_unit` | string | Required | Unit of measurement. | `mm/year` |
| `hazard_type` | enum | Optional | If `analytical_module = climate_hazard`: `drought` \| `flood` \| `heat_stress` \| `fire` \| `wind_cyclone` \| `waterlogging` \| `frost` \| `multi`. | `drought` |
| `scenario_type` | enum | Required | `baseline` \| `future_ssp126` \| `future_ssp245` \| `future_ssp585` \| `multi_scenario`. | `baseline` |
| `time_period` | string | Optional | Reference period or horizon. | `1981–2010` |
| `spatial_resolution_m` | integer | Required | Native resolution (metres). | `1000` |
| `geographic_coverage` | string | Required | Geographic extent. | `Global` |
| `data_format` | enum | Required | `geotiff` \| `geotiff_cog` \| `geoparquet` \| `netcdf` \| `csv` \| `shapefile` \| `gee_asset`. | `geotiff_cog` |
| `access_type` | enum | Required | `direct_download` \| `gee_asset` \| `api` \| `proprietary_licensed`. | `direct_download` |
| `download_url` | string | Optional | Direct download URL or DOI. | `https://chelsa-climate.org/` |
| `gee_asset_id` | string | Optional | GEE asset path if `access_type = gee_asset`. | `ECMWF/ERA5_LAND/MONTHLY_AGGR` |
| `download_function_ref` | string | Optional | Path to a download/access script in the repo. | `scripts/data/download_chelsa.py` |
| `license` | string | Required | License (SPDX identifier preferred). | `CC-BY-4.0` |
| `citation` | string | Required | Full bibliographic citation. | `Karger et al. (2017). Sci. Data…` |
| `doi` | string | Optional | DOI. | `10.1038/sdata.2017.122` |
| `version` | string | Required | Dataset version used. | `v2.1` |
| `preprocessing_notes` | string | Optional | Resampling, masking, etc. | `Resample to 1km COG, clip to AOI` |
| `known_limitations` | string | Required | Key caveats for naive users. | `Coarse resolution, may miss local effects` |
| `do_not_use_for` | string | Required | Explicit guidance on inappropriate uses. | `Site-level engineering design` |
| `further_info_urls` | string[] | Optional | Publications, docs, codebase links. | `['https://doi.org/…']` |
| `nbs_ids_using` | string[] | Optional | Which NbS use this dataset (from T4/T2 joins). | `['agroforestry','water_harvesting_conservation']` |

---

## T2 — Climate Risk Formulation

Variables for hazard, exposure, sensitivity and adaptive capacity, plus the composite-index formula.
AR6-consistent: **Risk = Hazard × Exposure × Vulnerability**, where Vulnerability = f(Sensitivity, Adaptive
Capacity). Weights must sum to **1.0 per `scenario_type` group**. `double_count_risk` is the guard against a
variable appearing in both the risk index and the opportunity space — the pipeline checks it before
compositing.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `variable_id` | string | Required | Unique identifier for this risk variable. | `drought_spei12_baseline` |
| `dataset_id` | string | Required | FK → `T1.dataset_id`. | `spei_global_v26` |
| `risk_component` | enum | Required | `hazard` \| `exposure` \| `sensitivity` \| `adaptive_capacity`. | `hazard` |
| `hazard_type` | enum | Conditional | Required if `risk_component = hazard`. `drought` \| `flood` \| `heat_stress` \| `fire` \| `wind_cyclone` \| `waterlogging` \| `frost`. | `drought` |
| `variable_name` | string | Required | Descriptive name. | `SPEI-12 drought severity (baseline)` |
| `scenario_type` | enum | Required | `baseline` \| `future_ssp126` \| `future_ssp245` \| `future_ssp585`. | `baseline` |
| `use_in_simplified_mode` | boolean | Required | Include in simplified (climate-index-only) mode. | `true` |
| `use_in_advanced_mode` | boolean | Required | Include in advanced (hazard × exposure) mode. | `true` |
| `double_count_risk` | enum | Required | `risk_only` \| `opportunity_space_only` \| `shared` (shared → pipeline uses `risk_only` by default). | `risk_only` |
| `normalisation_method` | enum | Required | `min_max` \| `percentile_clip` \| `log_transform` \| `none`. | `percentile_clip` |
| `normalisation_params` | object | Optional | e.g. `{ p_low: 2, p_high: 98 }`. | `{ p_low: 2, p_high: 98 }` |
| `weight_default` | float | Required | Default weight in composite index (0–1; per-scenario weights sum to 1). | `0.35` |
| `weight_adjustable` | boolean | Required | Can TTL/analyst adjust this weight? | `true` |
| `directionality` | enum | Required | `positive_risk` \| `negative_risk` (e.g. adaptive capacity = `negative_risk`). | `positive_risk` |
| `justification` | string | Required | Brief rationale for inclusion and weight. | `SPEI-12 is standard drought metric…` |
| `references` | string[] | Required | Supporting references. | `['Vicente-Serrano et al. 2010']` |

---

## T3 — NbS × Hazard × Farming System

Qualitative matrix of NbS mitigation potential against each climate hazard, per farming-system context. One
row per NbS × hazard × farming_system. Use `all` in `farming_system` where the relationship holds universally.
Negative scores are allowed where an NbS *worsens* a hazard (e.g. dense planting raising fire risk).

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `record_id` | string | Required | Unique row identifier. | `agro_drought_mixed_rainfed` |
| `nbs_id` | string | Required | FK → `T0.nbs_id`. | `agroforestry` |
| `hazard_type` | enum | Required | `drought` \| `flood` \| `heat_stress` \| `fire` \| `wind_cyclone` \| `waterlogging` \| `frost`. | `drought` |
| `farming_system` | string | Required | Farming-system context, or `all`. | `mixed_rainfed` |
| `mitigation_potential` | enum | Required | 7-point: `very_negative` \| `negative` \| `none` \| `low` \| `moderate` \| `high` \| `very_high`. | `moderate` |
| `mitigation_mechanism` | string | Required | How the NbS mitigates the hazard (1–3 sentences). | `Tree canopy reduces evapotranspiration…` |
| `confidence` | enum | Required | `high` \| `medium` \| `low` \| `expert_opinion`. | `medium` |
| `timescale_of_effect` | enum | Required | `immediate` \| `short_term_1_3yr` \| `medium_term_3_7yr` \| `long_term_7yr_plus`. | `medium_term_3_7yr` |
| `landscape_scale_only` | boolean | Required | Effect only at landscape/catchment scale, not farm scale. | `false` |
| `caveats` | string | Optional | Conditions or exceptions. | `Effect reduced in very arid AEZs` |
| `justification` | string | Required | Rationale and key evidence summary. | `Meta-analysis of 47 studies shows…` |
| `references` | string[] | Required | Supporting references. | `['Mbow et al. 2014','Quandt et al. 2019']` |

---

## T4 — Suitability Variable Mappings

The most complex table. Each row defines how a dataset variable maps to NbS suitability via a named
`relationship_type` (see the Relationship-type reference below).

- **Scenario candidate flag:** `is_scenario_candidate = true` **only** for variables a project investment could
  realistically change (road access, electrification, extension coverage). **Never** true for purely physical
  variables (slope, elevation, soil texture).
- **Context overrides:** the pipeline (1) checks `context_overrides` for a matching `context_type` + `context_id`
  from T7, then (2) falls back to the global `relationship_params` if no match.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `mapping_id` | string | Required | Unique row identifier. | `agro_slope_global` |
| `nbs_id` | string | Required | FK → `T0.nbs_id`. | `agroforestry` |
| `dataset_id` | string | Required | FK → `T1.dataset_id`. | `srtm_slope_30m` |
| `variable_name` | string | Required | Variable being assessed. | `Terrain slope` |
| `variable_unit` | string | Required | Unit. | `degrees` |
| `suitability_dimension` | enum | Required | `biophysical_constraint` \| `system_constraint` \| `operational_constraint`. | `biophysical_constraint` |
| `relationship_type` | enum | Required | `binary` \| `linear_decay` \| `trapezoidal_fuzzy` \| `gaussian_fuzzy` \| `ecocrop` \| `ranked_classes`. | `trapezoidal_fuzzy` |
| `relationship_params` | object | Required | Parameters for the relationship (structure depends on type). | `{ opt_low: 0, opt_high: 15, abs_max: 35 }` |
| `uncertainty_pct` | float | Optional | Symmetric ± buffer on limits (%). | `10` |
| `context_overrides` | object[] | Optional | `[{ context_type, context_id, relationship_params }]`. Global default if no match. | `[{ context_type:'aez', context_id:'humid_tropics', … }]` |
| `is_scenario_candidate` | boolean | Required | Can be toggled off in a what-if scenario (investment-influenceable only). | `false` |
| `scenario_label` | string | Conditional | Required if `is_scenario_candidate = true`. | `What if roads were accessible?` |
| `scenario_description` | string | Conditional | Required if `is_scenario_candidate = true`. | `Removes road-access constraint, showing…` |
| `has_future_projection` | boolean | Required | Changes under future climate scenarios (links to T2). | `true` |
| `baseline_dataset_id` | string | Conditional | Baseline `dataset_id` if `has_future_projection = true`. | `chelsa_precip_baseline` |
| `future_dataset_ids` | object | Conditional | `{ ssp126, ssp245, ssp585 }` → dataset_id. | `{ ssp245: 'chelsa_precip_ssp245_2050' }` |
| `weight_default` | float | Required | Default MCDA weight within the suitability index (0–1). | `0.15` |
| `weight_adjustable` | boolean | Required | Can the analyst adjust the weight? | `true` |
| `justification` | string | Required | Why this variable and this function shape. | `Slope >35° prevents machinery access…` |
| `references` | string[] | Required | Supporting references. | `['Nair 1993','Zomer et al. 2014']` |

### Relationship-type reference (`relationship_type` + `relationship_params`)

| `relationship_type` | Parameters required | When to use |
|---|---|---|
| `binary` | `{ threshold, above_is_suitable: bool }` | Hard pass/fail. e.g. protected area = exclude. |
| `linear_decay` | `{ suitable_max, unsuitable_min, direction: 'increasing'|'decreasing' }` | Suitability falls linearly between two boundaries. |
| `trapezoidal_fuzzy` | `{ abs_min, opt_low, opt_high, abs_max }` | Optimal plateau with declining shoulders. Most biophysical variables (slope, rainfall). Suitability = 1.0 within `[opt_low, opt_high]`, declining linearly to 0 at `abs_min`/`abs_max`. `uncertainty_pct` applies a symmetric ± buffer to all four limits. |
| `gaussian_fuzzy` | `{ mean, sigma }` | Bell-curve suitability around an optimum. Temperature optima. |
| `ecocrop` | `{ t_min, t_opt_low, t_opt_high, t_max }` (replicated per dimension) | Multi-dimensional EcoCrop-style with absolute and optimal limits. |
| `ranked_classes` | `{ class_map: { value: score } }` | Categorical input (soil type, land use) mapped to 0–1 scores. |

---

## T5 — Opportunity Space Variables

Layers characterising the opportunity space that TTLs weight and combine to identify hotspots. They describe
the *characteristics* of the geographic space within the biophysical opportunity space — **not** suitability
constraints. Climate risk enters here via `is_climate_risk_component = true`, but `double_count_risk` in T2
prevents double-counting.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `variable_id` | string | Required | Unique identifier. | `rural_poverty_headcount` |
| `variable_name` | string | Required | Display name. | `Rural poverty headcount ratio` |
| `category` | enum | Required | `socioeconomic` \| `biodiversity` \| `carbon` \| `agricultural_production` \| `infrastructure` \| `climate_risk` \| `governance` \| `gender`. | `socioeconomic` |
| `dataset_id` | string | Required | FK → `T1.dataset_id`. | `worldpop_poverty_2020` |
| `unit` | string | Required | Unit of measurement. | `% population below $2.15/day` |
| `directionality_of_concern` | enum | Required | `high_is_bad` \| `low_is_bad` \| `context_dependent` (sets dashboard colours). | `high_is_bad` |
| `ttl_priority_label` | string | Required | Short label in the weighting interface. | `Poverty` |
| `ttl_priority_description` | string | Required | 1–2 sentence explanation for the TTL. | `Areas with high poverty headcount…` |
| `is_climate_risk_component` | boolean | Required | Also used in T2 (pipeline uses T2 `double_count_risk` to avoid duplication). | `false` |
| `aggregation_method` | enum | Required | `mean` \| `sum` \| `max` \| `majority` \| `area_weighted_mean`. | `mean` |
| `normalisation_method` | enum | Required | `min_max` \| `percentile_clip` \| `log_transform` \| `none`. | `percentile_clip` |
| `spatial_resolution_m` | integer | Required | Native resolution of source. | `1000` |
| `has_future_projection` | boolean | Required | Future projection available. | `false` |
| `is_active` | boolean | Required | Include in current prototype. | `true` |
| `references` | string[] | Required | Data and literature references. | `['World Bank PovcalNet 2024']` |

---

## T6 — NbS Scorecard — Effects and Economic Profile

Per-NbS qualitative effect on each opportunity-space variable, plus economic indicators — the scorecard the
literature team completes. An economist can use `economic_value_range` to construct an indicative cost-benefit
narrative without a full CBA. `economic_archetype_note` is narrative linking to the CrossBoundary archetype,
not a model output.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `record_id` | string | Required | Unique row identifier. | `agro_rural_poverty` |
| `nbs_id` | string | Required | FK → `T0.nbs_id`. | `agroforestry` |
| `variable_id` | string | Required | FK → `T5.variable_id` **or** a hazard_type from T3. | `rural_poverty_headcount` |
| `variable_type` | enum | Required | `opportunity_space_variable` \| `climate_hazard_mitigation` \| `economic_indicator`. | `opportunity_space_variable` |
| `effect_direction` | enum | Required | Likert: `strong_negative` \| `moderate_negative` \| `slight_negative` \| `no_relationship` \| `slight_positive` \| `moderate_positive` \| `strong_positive`. | `moderate_positive` |
| `effect_confidence` | enum | Required | `high` \| `medium` \| `low` \| `expert_opinion`. | `medium` |
| `effect_mechanism` | string | Required | How/why the NbS affects this variable (1–3 sentences). | `Diversified income from timber and fruit…` |
| `conditionality` | string | Optional | Conditions under which the effect holds or reverses. | `Only where tenure security is established` |
| `timescale_of_effect` | enum | Required | `immediate` \| `short_term_1_3yr` \| `medium_term_3_7yr` \| `long_term_7yr_plus`. | `long_term_7yr_plus` |
| `economic_indicator_type` | enum | Conditional | Required if `variable_type = economic_indicator`. `establishment_cost` \| `recurrent_cost` \| `income_potential` \| `cost_reduction` \| `market_access` \| `carbon_revenue` \| `subsidy_dependency`. | `income_potential` |
| `economic_value_range` | object | Conditional | `{ low_usd_ha_yr, high_usd_ha_yr, source_note }`. | `{ low_usd_ha_yr: 50, high_usd_ha_yr: 300, … }` |
| `economic_archetype_note` | string | Optional | Free text linking to the CrossBoundary archetype. | `Long horizon: 5–10yr to income…` |
| `justification` | string | Required | Evidence summary. | `Mercer (2004) meta-analysis shows…` |
| `references` | string[] | Required | Supporting references. | `['Mercer 2004','ICRAF 2020']` |

---

## T7 — Geographic Context

AEZ, farming-system, administrative and hydrological context definitions used to resolve context-specific
overrides in T4. Primarily populated by Benson. Provides the controlled vocabulary the pipeline looks up by
`context_type` + `value_in_dataset` when reading raster/vector data.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `context_id` | string | Required | Unique identifier. | `humid_tropics` |
| `context_type` | enum | Required | `aez` \| `farming_system` \| `admin_country` \| `admin_region` \| `hydrobasin`. | `aez` |
| `context_name` | string | Required | Human-readable name. | `Humid tropics` |
| `parent_context_id` | string | Optional | For hierarchical contexts (sub-AEZ within AEZ). | `tropics` |
| `dataset_id` | string | Required | FK → `T1.dataset_id` for the boundary/classification dataset. | `gaez_v4_aez33` |
| `geometry_field` | string | Required | Field in the dataset holding the geometry or raster value. | `aez_code` |
| `value_in_dataset` | string | Required | Value/code identifying this context in the dataset. | `120` |
| `description` | string | Required | Brief description for documentation. | `Humid tropical zone, >1200mm rainfall…` |
| `is_active` | boolean | Required | Currently used for overrides. | `true` |

---

## Implementation notes

**File formats.** Tables are implemented as JSON arrays of objects (one object per row) for machine
consumption, with a parallel CSV view for human editing. For large tables (T1, T4), JSONL (one object per
line) is an option for streaming.

**Foreign-key validation (fail loudly).** On load, validate: every `dataset_id` in T2/T3/T4/T5/T7 exists in
T1; every `nbs_id` in T0/T3/T4/T6 exists in T0; every `variable_id` in T6 exists in T5 (or is a T3 hazard_type
for `climate_hazard_mitigation` rows). A missing target raises an explicit error — never a silent gap.

**Climate mode switch.** A top-level `climate_mode = 'simplified' | 'advanced'`. Simplified filters T2 rows by
`use_in_simplified_mode = true` and uses only the composite climate index as a single variable; advanced uses
all `use_in_advanced_mode = true` rows and computes hazard × exposure × vulnerability explicitly.

**Scenario / what-if logic.** For each T4 row with `is_scenario_candidate = true`, expose a UI toggle. Toggling
off sets that variable's suitability to 1.0 (constraint removed); the pipeline recomputes the composite
suitability surface and reports the change in opportunity-space extent and density.

**Context-override resolution.** For each pixel: (1) identify AEZ and farming system via T7; (2) for each T4
row, check `context_overrides` for a matching `context_type` + `context_id`; (3) use the override
`relationship_params` if found, else the global params.

**Pilot scope.** Populate T0–T7 for one NbS at a time. The pipeline reads dynamically from the files; adding a
new NbS later requires only adding rows, not code changes.

---

*Ported from `NbS_Schema_Reference_v01_1.docx` — v0.1 Draft, Peter Steward (Team Lead), 7 May 2026.
For queries: P.Steward@cgiar.org*
