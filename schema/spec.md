# Schema spec — field-level reference (v0.2)

> **v0.2 (June 2026)** — added `T3.risk_role` + `T3.asset_risk_weight` (the M2 / M2b two-risk split);
> added `T5.theme` + `T5.weight_default` (hotspot grouping & weighting); reconciled `T4.relationship_type`
> to one canonical membership-function set with a wireframe crosswalk; documented NbS-response layers as
> derived (T5 `theme=nbs_response` × T6) and the shared-layer dedup; **added the evidence & configuration layer**
> (Source / Evidence / Variable-Ontology / Subpractice-Family registers) making T3/T4/T6 values traceable, and
> keyed T4 to `suitability_family_id`. **Field trim (June 2026):** evidence-based tables (T2/T3/T4/T6) now carry
> `evidence_ids` (→ EV) instead of free-text `references`; canonical variable name + unit live only in the
> Variable Ontology (analytical tables reference `variable`); derived/duplicated fields removed
> (`T1.nbs_ids_using`, `T5.spatial_resolution_m`, `T5.category`, `T0.last_updated`/`updated_by`); minor merges
> (`T1.limitations`); added `T4.suitability_family_id` (the unit T4 keys to). v0.1 was the original 8-table design.
>
> **Structure frozen (`v0.2-structure-frozen`).** The column set here is machine-mirrored in
> [`structure/columns.json`](structure/columns.json) and enforced by `src/nbs_ruralscan/structure.py`. Change the
> structure only by editing this spec, regenerating the manifest, and raising an issue — never by reshaping data files.

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

---

## T1 — Data Registry

Dataset catalog — every dataset used anywhere in the analysis must have a record here. The pipeline looks up
datasets here rather than hardcoding URLs (`download_url` / `gee_asset_id` carry the access pointer). Which NbS
use a dataset is derived on demand from the T2/T4 joins, not stored.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `dataset_id` | string | Required | Unique identifier (snake_case). | `chelsa_precipitation_v21` |
| `dataset_name` | string | Required | Full descriptive name. | `CHELSA Precipitation v2.1` |
| `analytical_module` | enum | Required | `climate_hazard` \| `climate_impact` \| `structural_suitability` \| `adaptive_capacity` \| `exposure` \| `opportunity_space` \| `geographic_context`. | `climate_hazard` |
| `hazard_type` | enum | Optional | If `analytical_module = climate_hazard`: `drought` \| `flood` \| `heat_stress` \| `fire` \| `wind_cyclone` \| `waterlogging` \| `frost` \| `multi`. | `drought` |
| `scenario_type` | enum | Required | `baseline` \| `future_ssp126` \| `future_ssp245` \| `future_ssp585` \| `multi_scenario`. | `baseline` |
| `time_period` | string | Optional | Reference period or horizon. | `1981–2010` |
| `spatial_resolution_m` | integer | Required | Native resolution (metres). | `1000` |
| `geographic_coverage` | string | Required | Geographic extent. | `Global` |
| `data_format` | enum | Required | `geotiff` \| `geotiff_cog` \| `geoparquet` \| `netcdf` \| `csv` \| `shapefile` \| `gee_asset`. | `geotiff_cog` |
| `access_type` | enum | Required | `direct_download` \| `gee_asset` \| `api` \| `proprietary_licensed`. | `direct_download` |
| `download_url` | string | Optional | Direct download URL or DOI. | `https://chelsa-climate.org/` |
| `gee_asset_id` | string | Optional | GEE asset path if `access_type = gee_asset`. | `ECMWF/ERA5_LAND/MONTHLY_AGGR` |
| `license` | string | Required | License (SPDX identifier preferred). | `CC-BY-4.0` |
| `citation` | string | Required | Full bibliographic citation. | `Karger et al. (2017). Sci. Data…` |
| `doi` | string | Optional | DOI. | `10.1038/sdata.2017.122` |
| `version` | string | Required | Dataset version used. | `v2.1` |
| `preprocessing_notes` | string | Optional | Resampling, masking, etc. | `Resample to 1km COG, clip to AOI` |
| `limitations` | string | Required | Key caveats + inappropriate uses (merged). | `Coarse resolution; not for site-level design` |

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
| `variable` | string | Required | FK → Variable Ontology (canonical name + unit live there). | `spei12` |
| `scenario_type` | enum | Required | `baseline` \| `future_ssp126` \| `future_ssp245` \| `future_ssp585`. | `baseline` |
| `use_in_simplified_mode` | boolean | Required | Include in simplified (climate-index-only) mode. | `true` |
| `use_in_advanced_mode` | boolean | Required | Include in advanced (hazard × exposure) mode. | `true` |
| `double_count_risk` | enum | Required | `risk_only` \| `opportunity_space_only` \| `shared` (shared → pipeline uses `risk_only` by default). | `risk_only` |
| `normalisation_method` | enum | Required | `min_max` \| `percentile_clip` \| `log_transform` \| `none`. | `percentile_clip` |
| `normalisation_params` | object | Optional | e.g. `{ p_low: 2, p_high: 98 }`. | `{ p_low: 2, p_high: 98 }` |
| `weight_default` | float | Required | Default weight in composite index (0–1; per-scenario weights sum to 1). | `0.35` |
| `weight_adjustable` | boolean | Required | Can TTL/analyst adjust this weight? | `true` |
| `directionality` | enum | Required | `positive_risk` \| `negative_risk` (e.g. adaptive capacity = `negative_risk`). | `positive_risk` |
| `evidence_ids` | string[] | Required | FK list → EV (provenance: source · tier · page · quote). | `['ev_spei_vicente10']` |
| `justification` | string | Optional | One-line summary, generated from the evidence units. | `SPEI-12 is standard drought metric…` |

---

## T3 — NbS × Hazard × Farming System

Qualitative matrix of NbS mitigation potential against each climate hazard, per farming-system context. One
row per NbS × hazard × farming_system. Use `all` in `farming_system` where the relationship holds universally.
Negative scores are allowed where an NbS *worsens* a hazard (e.g. dense planting raising fire risk).

**This table carries the two-risk split.** `risk_role` tags each hazard×NbS row as something the NbS
*mitigates* (a livelihood **need** layer feeding M2) or something that *threatens the asset* but the NbS does
**not** mitigate (feeding the **M2b** project disaster-risk screen). The same hazard family can appear in both
roles for different NbS (e.g. flooding is a need driver for wetland creation but an asset threat to a parkland
plot). M2b reads the `asset_threat` rows and their `asset_risk_weight`; M2 reads the mitigation rows.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `record_id` | string | Required | Unique row identifier. | `agro_drought_mixed_rainfed` |
| `nbs_id` | string | Required | FK → `T0.nbs_id`. | `agroforestry` |
| `hazard_type` | enum | Required | `drought` \| `flood` \| `heat_stress` \| `fire` \| `wind_cyclone` \| `waterlogging` \| `frost`. | `drought` |
| `farming_system` | string | Required | Farming-system context, or `all`. | `mixed_rainfed` |
| `mitigation_potential` | enum | Required | 7-point: `very_negative` \| `negative` \| `none` \| `low` \| `moderate` \| `high` \| `very_high`. | `moderate` |
| `risk_role` | enum | Required | Which lens this row serves. `livelihood_mitigation` (NbS *mitigates* this hazard → M2 need layer) \| `asset_threat` (hazard *damages the NbS asset* but is not mitigated → M2b project-risk) \| `both`. | `livelihood_mitigation` |
| `asset_risk_weight` | float | Conditional | Required when `risk_role` includes `asset_threat`. Default weight (0–1) of this hazard in the M2b project disaster-risk rating for this NbS; per-NbS `asset_threat` weights sum to 1. Blank for pure `livelihood_mitigation` rows. | `0.40` |
| `mitigation_mechanism` | string | Required | How the NbS mitigates the hazard (1–3 sentences). | `Tree canopy reduces evapotranspiration…` |
| `confidence` | enum | Required | `high` \| `medium` \| `low` \| `expert_opinion`. | `medium` |
| `timescale_of_effect` | enum | Required | `immediate` \| `short_term_1_3yr` \| `medium_term_3_7yr` \| `long_term_7yr_plus`. | `medium_term_3_7yr` |
| `landscape_scale_only` | boolean | Required | Effect only at landscape/catchment scale, not farm scale. | `false` |
| `caveats` | string | Optional | Conditions or exceptions. | `Effect reduced in very arid AEZs` |
| `evidence_ids` | string[] | Required | FK list → EV (provenance). | `['ev_agro_drought_mbow14']` |
| `justification` | string | Optional | One-line summary, generated from the evidence units. | `Meta-analysis of 47 studies shows…` |

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
| `mapping_id` | string | Required | Unique row identifier. | `agro_f1_slope_global` |
| `nbs_id` | string | Required | FK → `T0.nbs_id`. | `agroforestry` |
| `suitability_family_id` | string | Required | FK → `FAM.suitability_family_id`. **The unit T4 is keyed to** — suitability is reasoned per family, not per whole NbS. Rolls up to `nbs_id` for display. | `agroforestry__planted_silvoarable` |
| `dataset_id` | string | Required | FK → `T1.dataset_id`. | `srtm_slope_30m` |
| `variable` | string | Required | FK → Variable Ontology (canonical name + unit live there). | `slope` |
| `suitability_dimension` | enum | Required | `biophysical_constraint` \| `system_constraint` \| `operational_constraint`. | `biophysical_constraint` |
| `relationship_type` | enum | Required | Canonical set: `trapezoidal` \| `gaussian` \| `linear_increasing` \| `linear_decreasing` \| `sigmoid` \| `inverted_sigmoid` \| `threshold` \| `ranked_classes` \| `piecewise`. See the reference + wireframe crosswalk below. | `trapezoidal` |
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
| `n_sources` · `corpus_n` | integer | Optional | Numerator (distinct sources with ≥1 evidence unit for this variable) and denominator (papers screened for the family). | `6` · `8` |
| `paper_support_pct` | float | Derived | Literature-prevalence selection signal = `100 · n_sources / corpus_n`. Rolls up to group via the Variable Ontology `group_id` (set-union). Not stored authoritatively — computed from `n_sources`/`corpus_n`. | `75.0` |
| `evidence_ids` | string[] | Required | FK list → EV (provenance behind the thresholds + shape). | `['ev_slope_nair93','ev_slope_zomer14']` |
| `justification` | string | Optional | One-line summary of why this variable and shape, generated from the evidence units. | `Slope >35° prevents machinery access…` |

### Relationship-type reference (`relationship_type` + `relationship_params`)

This is the **one canonical list** of membership/response functions. It supersedes the older
`binary`/`linear_decay`/`*_fuzzy` names and the diagram's "5-function" wording, and it is the set the
`docs/pipeline.html` P1 primitive and the TTL wireframe both map to (crosswalk in the last column).

| Canonical `relationship_type` | Parameters | When to use | TTL wireframe label · internal token |
|---|---|---|---|
| `trapezoidal` | `{ abs_min, opt_low, opt_high, abs_max }` | Optimal plateau with declining shoulders. Most biophysical variables (slope, rainfall). 1.0 within `[opt_low, opt_high]`, → 0 at `abs_min`/`abs_max`. `uncertainty_pct` applies a symmetric ± buffer to the limits. | "Trapezoidal (plateau)" · `trapezoid` |
| `gaussian` | `{ mean, sigma }` | Bell-curve suitability around an optimum (temperature optima). Subsumes the old "bell". | "Gaussian (optimal band)" · `gaussian` |
| `linear_increasing` | `{ unsuitable_min, suitable_max }` | More is better — rises linearly between the bounds. | "Linear — more is better" · `linup` |
| `linear_decreasing` | `{ suitable_max, unsuitable_min }` | Less is better — falls linearly (was `linear_decay`). | "Linear — less is better" · `lindown` |
| `sigmoid` | `{ midpoint, slope }` | Smooth monotonic **increase** (S-curve). | advanced — not in the TTL dropdown |
| `inverted_sigmoid` | `{ midpoint, slope }` | Smooth monotonic **decrease** (S-curve). | advanced — not in the TTL dropdown |
| `threshold` | `{ threshold, above_is_suitable: bool }` | Hard pass/fail (was `binary`); e.g. protected area = exclude. | "Threshold (hard cut)" · `threshold` |
| `ranked_classes` | `{ class_map: { value: score } }` | Categorical input (soil type, land use) → 0–1 scores. | categorical — separate control |
| `piecewise` | `{ points: [[x, y], …] }` | User-defined custom curve. | "Custom (piecewise)" · `custom` |

> `ecocrop` is **not** a base type — it is a multi-dimensional composite (`{ t_min, t_opt_low, t_opt_high, t_max }`
> replicated per dimension) built from `trapezoidal`/`threshold` limits. Document it as a composite where used.
>
> **Surfacing.** The TTL wireframe exposes the continuous subset (trapezoidal · gaussian · linear↑/↓ · threshold ·
> piecewise). `sigmoid`/`inverted_sigmoid` and `ranked_classes` are available to the engine and to technical users
> but are not in the default TTL dropdown. The wireframe keeps its short internal tokens (`trapezoid`, `linup`,
> `lindown`, `custom`); they map to the canonical names per the table above.

---

## T5 — Opportunity Space Variables

Layers characterising the opportunity space that TTLs weight and combine to identify hotspots. They describe
the *characteristics* of the geographic space within the biophysical opportunity space — **not** suitability
constraints. Climate risk enters here via `is_climate_risk_component = true`, but `double_count_risk` in T2
prevents double-counting.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `variable_id` | string | Required | Unique identifier. | `rural_poverty_headcount` |
| `variable` | string | Required | FK → Variable Ontology (canonical name, unit, and `group_id` for theme roll-up live there). | `rural_poverty_headcount` |
| `theme` | enum | Required | Hotspot pillar for grouping + theme-level weighting in M4. `climate_hazard` \| `nbs_response` \| `people_production` \| `infrastructure`. | `people_production` |
| `dataset_id` | string | Required | FK → `T1.dataset_id`. | `worldpop_poverty_2020` |
| `directionality_of_concern` | enum | Required | `high_is_bad` \| `low_is_bad` \| `context_dependent` (sets dashboard colours). | `high_is_bad` |
| `ttl_priority_label` | string | Required | Short label in the weighting interface. | `Poverty` |
| `ttl_priority_description` | string | Required | 1–2 sentence explanation for the TTL. | `Areas with high poverty headcount…` |
| `is_climate_risk_component` | boolean | Required | Also used in T2 (pipeline uses T2 `double_count_risk` to avoid duplication). | `false` |
| `aggregation_method` | enum | Required | `mean` \| `sum` \| `max` \| `majority` \| `area_weighted_mean`. | `mean` |
| `normalisation_method` | enum | Required | `min_max` \| `percentile_clip` \| `log_transform` \| `none`. | `percentile_clip` |
| `weight_default` | float | Required | Default weight of this variable **within its theme** for the hotspot MCDA (0–1; weights within a theme normalise to 1). TTL-adjustable at M4. | `0.25` |
| `has_future_projection` | boolean | Required | Future projection available. | `false` |
| `is_active` | boolean | Required | Include in current prototype. | `true` |
| `evidence_ids` | string[] | Optional | FK list → EV where a literature claim backs inclusion (context layers may be data-only). | `['ev_poverty_wb24']` |

### Theme weights and NbS-response layers

**Theme weights.** Variable weights normalise within a theme; the *theme-level* defaults that set how much each
pillar drives the hotspot index live in a small `theme_weights` lookup at the schema root (pilot defaults:
`climate_hazard` 0.30 · `nbs_response` 0.25 · `people_production` 0.30 · `infrastructure` 0.15). All TTL-adjustable
at M4. (A row carrying `weight_default` × its theme weight gives the variable's contribution before user reweighting.)

**NbS-response layers (`theme = nbs_response`).** These are the only T5 variables whose magnitude is
**NbS-specific** — e.g. erosion-reduction potential, water-yield benefit, carbon sequestration, biodiversity
co-benefit. They are **derived, not stored as fixed rasters**: the shared T5 row defines the underlying
need/biophysical layer + direction + `dataset_id`; the per-NbS strength comes from the matching **T6** scorecard
effect, joined on `variable_id` + `nbs_id` (`effect_direction` / `effect_mechanism`). So no extra table is needed —
the T5↔T6 link already carries the NbS-specific modulation. Pure context layers (poverty, market access) have no
T6 row and are identical across NbS.

---

## T6 — NbS Scorecard — Effects and Economic Profile

Per-NbS qualitative effect on each opportunity-space variable, plus economic indicators — the scorecard the
literature team completes. An economist can use `economic_value_range` to construct an indicative cost-benefit
narrative without a full CBA. `economic_archetype_id` points to the CrossBoundary archetype lookup (the
narrative lives there), not a model output.

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
| `economic_archetype_id` | string | Optional | FK → CrossBoundary archetype lookup (narrative lives there, not inline). | `agroforestry_long_horizon` |
| `evidence_ids` | string[] | Required | FK list → EV (provenance behind the effect + economic range). | `['ev_agro_income_mercer04']` |
| `justification` | string | Optional | One-line evidence summary, generated from the evidence units. | `Mercer (2004) meta-analysis shows…` |

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

## Evidence & configuration layer (upstream of T0–T7)

Added v0.2. These tables feed the evidence-based analytical tables (**T3, T4, T6**) and are produced by the T4
generation method ([`../methodology/T4_generation_method.md`](../methodology/T4_generation_method.md)). They make
every analytical value traceable: **T4 row → `evidence_id`s → source (tier, page, quote)**. Source tier is stored
once on the Source Register and reached by `source_id` join — never copied onto evidence rows.

### SRC — Source Register

One row per publication/report/tool (formalises the stocktake `NbS_peer_reviewed_benchmarked.csv`).

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `source_id` | string | Required | Unique id. | `nath_2021` |
| `citation` · `doi` | string | Required | Bibliographic. | `Nath et al. (2021)…` |
| `benchmark_tier` | enum | Required | `high` \| `medium` \| `low` (C/I/D rubric). **The only place tier is stored.** | `medium` |
| `study_country` · `region` · `coords` | string | Optional | Where the study was done. | `India / E. Himalaya` |
| `aez` · `farming_system` | string | Optional | Study context (→ T7 vocab). | `humid_tropics` |
| `method_type` | enum | Optional | `ahp` \| `critic` \| `entropy` \| `fao_landeval` \| `ecocrop` \| `empirical` \| `expert`. | `ahp` |
| `spatial_scale` · `analysis_resolution_m` | string/int | Optional | Scale + grid used. | `1000` |
| `nbs_ids` | string[] | Optional | NbS the source addresses. | `['agroforestry']` |

### EV — Evidence Register

One row per **atomic claim**. The structured replacement for free-text justifications.

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `evidence_id` | string | Required | Unique id. | `ev_slope_nath21` |
| `source_id` | string | Required | FK → SRC. (tier via join.) | `nath_2021` |
| `nbs_id` · `suitability_family_id` | string | Required | What it pertains to. | `agroforestry` · `agroforestry__planted_silvoarable` |
| `variable` | string | Required | FK → Variable Ontology (canonical). | `slope` |
| `relationship` | object | Optional | Extracted thresholds/shape. | `{opt_low:0,opt_high:10,abs_max:44,unit:"deg"}` |
| `context` | object | Optional | AEZ/farming system the claim applies to. | `{aez:"humid_tropics"}` |
| `use_role` | enum | Required | Which table it feeds. `structural_suitability`(T4) \| `climate_risk`(T2) \| `priority_need`(T5) \| `nbs_effect`(T6) \| `dataset`(T1). | `structural_suitability` |
| `evidence_type` | enum | Required | `literature_relationship` \| `ml_importance` \| `scoping_candidate` \| `expert`. Only literature/expert carry shape params. | `literature_relationship` |
| `claim_basis` | enum | Required | `primary_measured` \| `modelled` \| `cited_secondary` \| `expert_assertion` \| `table` \| `figure_read`. Claim strength within source. | `table` |
| `claim_scope` | enum | Required | `practice_technology` \| `species_specific` \| `crop_specific`. Species/crop claims must not set practice rows. | `practice_technology` |
| `taxon` | string | Conditional | Required when `claim_scope ≠ practice_technology`. | `Morus alba` |
| `lineage_of` | string | Optional | `evidence_id`/`source_id` this claim is *echoing* (citation cascade) → dedupe to origin. | `harrison_2016` |
| `extraction_confidence` | enum | Required | Transcription fidelity. | `high` |
| `quote` · `page` | string/int | Required | Verbatim + page (provenance). | `"…slope 0 to 5…", p.11` |
| `reviewer_ok` | boolean | Optional | Human-validated. | `false` |

### VONT — Variable Ontology

Canonical variables: harmonisation + data-catalog link + resolution validity.

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `canonical_variable_id` | string | Required | Unique id. | `slope` |
| `label` | string | Required | Display name. | `Terrain slope` |
| `aliases` | string[] | Optional | Known surface names (may be empty). | `['terrain slope','gradient','slope %']` |
| `canonical_unit` | string | Required | Canonical unit. | `degrees` |
| `unit_conversions` | object | Optional | Conversions to canonical unit (may be empty). | `{pct→deg:"atan"}` |
| `group_id` | string | Required | → Variable-Group vocab (Topographic, …). | `topographic` |
| `candidate_dataset_ids` | string[] | Required | → T1 datasets that can supply it. | `['srtm_dem_30m','srtm_dem_90m']` |
| `min_meaningful_resolution_m` | integer | Required | Coarsest grid at which the variable stays valid. | `90` |
| `resolution_sensitivity` | enum | Required | `low` \| `medium` \| `high` (derivatives = high). | `high` |
| `derive_then_aggregate` | boolean | Required | Compute native then summarise to grid (slope, TWI…). | `true` |

### FAM — Subpractice / Suitability-Family registry

NbS decomposition; the unit T4 is keyed to.

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `subpractice_id` · `nbs_id` | string | Required | Variant + parent NbS. | `alley_cropping` · `agroforestry` |
| `name` · `definition` | string | Required | + scope boundaries. | `Alley cropping` |
| `suitability_family_id` | string | Required | The family it belongs to (T4 keys to this). | `agroforestry__planted_silvoarable` |
| `dominant_limiting_factor` | string | Required | Why it's grouped here. | `biophysical envelope + management` |
| `spatial_product_type` | enum | Required | `area_suitability` \| `applicability_zone` \| `zonal_linear` \| `qualitative_only`. | `area_suitability` |
| `grouping_rationale` · `references` | string/[] | Required | Documented + cited (auditable lumping). | `…` |

**T4 change:** rows key to `suitability_family_id` (subpractices roll up to NbS for display). T4 `references`/
`justification` now cite `evidence_id`s.

---

## Implementation notes

**File formats.** Tables are implemented as JSON arrays of objects (one object per row) for machine
consumption, with a parallel CSV view for human editing. For large tables (T1, T4), JSONL (one object per
line) is an option for streaming.

**Foreign-key validation (fail loudly).** On load, validate: every `dataset_id` in T2/T3/T4/T5/T7 exists in
T1; every `nbs_id` in T0/T3/T4/T6 exists in T0; every `variable_id` in T6 exists in T5 (or is a T3 hazard_type
for `climate_hazard_mitigation` rows). Evidence layer: every `variable` in T2/T4/T5 (and EV) exists in **VONT**;
every `evidence_id` in T2/T3/T4/T5/T6 exists in **EV**; every `source_id` in EV exists in **SRC**; every
`suitability_family_id` in T4 (and EV) exists in **FAM**. A missing target raises an explicit error — never a
silent gap.

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
