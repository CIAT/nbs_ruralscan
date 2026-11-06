# Runoff binding consumer trace

Read-only investigation; no git commands, register/recipe changes or scientific approvals. `consumer_trace.json` preserves exact inspected register values and local function probes. Source quantities below are readings of current EV fields, not fresh publication verification.

## Reach and regeneration

- `schema/T1_data_registry.csv:20`: mixed identity. Dataset ID/description say SCS runoff composite; name, asset, DOI and preprocessing identify HydroSHEDS/HydroBASINS context. Row calls polygons `grain_type=grid` and gives 90 m. Parent's official-catalogue check establishes polygon FeatureCollection based on 15 arc-second (~500 m equatorial) underlying data, not a 90 m runoff raster. GEE `ORDER` is classical hierarchy, not Strahler order.
- `schema/recipes/water_harvesting_conservation/T4_suitability_mappings.csv:12`: runoff-catchment runoff (`abs_min=75`, `opt_low=80`). Five cited EVs mix CN, depth in mm, and coefficient.
- Same file `:14`: stream order (`1,2,2,4`), three different EV IDs.
- Same file `:16`: drainage density (`opt_high=0.25`), three different EV IDs.
- Same file `:26`: terracing runoff (`opt_low=0.9`), one runoff-coefficient EV.
- `schema/T2_climate_risk.csv:10`: flood-hazard runoff-depth row also references same ID. This is outside T4 and must be recorded separately, not silently rewritten during T4 check.
- `schema/registers/VONT_variable_ontology.csv:14,15,25,37,39,40`: six candidate variables: drainage density, stream order, flood-hazard runoff depth, runoff potential, groundwater-recharge potential, flood risk. No BIND entries for any six.
- `src/nbs_ruralscan/recipe/t4_build.py:92`: `_first_dataset` takes first VONT candidate. `:279` builds defaults; `:327` writes them to T4. A recipe-only edit will not persist through regeneration. Reviewed matching-input holds exist at `:310`, but are specifically supported by reviewed profile adaptation metadata; no blanket scientific approval may be fabricated to invoke them.

## Actual resolution and execution limit

- `src/nbs_ruralscan/runtime/binding.py:101`: `resolve_binding` checks BIND status/context/rank only. No candidates -> `KeyError`; present catalogued dataset ID is accepted without T1 capabilities or native-unit verification.
- `src/nbs_ruralscan/recipe/developer_contract.py:171`: `_binding` catches missing BIND and uses recipe dataset. `:186` chooses GEE asset before download URL; `:198` reports `needs_upload=false` when ID exists. Probe returns HydroBASINS asset, no band, no documented input, no source unit, no reducer; canonical unit `index_or_native`. `:207` does explicitly warn access has not been fetched/validated.
- `scripts/release-t4-first-pass.py:167`: same recipe-retention fallback pattern, currently an agroforestry release tool; not proof this water-harvesting output was released.
- `src/nbs_ruralscan/data_loaders/__init__.py:1`: only package docstring; no acquisition implementation found. `runtime/schema_loader.py` and `runtime/outputs.py` are empty. No current `ee.Image`, `xee`, `open_dataset`, or `FeatureCollection` acquisition calls found in src.
- `src/nbs_ruralscan/runtime/numeric.py:12`: evaluates caller-supplied arrays, does not fetch or validate dataset units. These four legacy trapezoidal rows all raise `Unsupported numeric relationship` in direct probe (`:76`); supported evaluator branches are threshold and piecewise. Thus bad metadata propagates to handoff/defaults, but no actual HydroBASINS-as-runoff raster run was demonstrated.

## Six runoff evidence records (all reviewer_ok=false)

- dewinnaar07: CN qualitative increasing runoff-generation direction, no numeric cutoff.
- alabadi17: runoff depth mm, source criterion weight 0.368 and direction; weight is not depth.
- karimi19: runoff depth mm, >200 best class; stored opt_low 200.
- singh17: dimensionless runoff coefficient, corrected ordinal classes; no standalone abs/opt fields and explicit transfer hold.
- vema19: CN fuzzy INPUT classes, corrected record expressly forbids standalone suitability thresholds; high input class [75,80,100,100] is not independent suitability cutoff.
- krois14: runoff coefficient, >0.9 source optimal class; stored opt_low 0.9.

Existing 75/80 mapping is not defensible merely by replacing dataset. Its cited records have different quantities and two have corrections explicitly withdrawing standalone cutoffs. Preserve all evidence while reviewing mapping separately.

## Minimal remediation boundaries

1. Correct dataset identity/capability metadata only from verified provider documentation. Keep HydroBASINS as watershed polygons under an unambiguous identity; do not relabel it CN/runoff or use ORDER as Strahler.
2. Treat missing runoff input as unresolved. No supplied CN/depth/coefficient model, period, rainfall event or antecedent-moisture convention is established by this row. Do not choose a replacement model or invent a GEE runoff asset.
3. Any proposed hold must cover both recipe references and VONT regeneration defaults, plus developer fallback. A BIND-only requires-upload row leaves stale recipe IDs; recipe-only blanks repopulate from VONT. T2 is a separate affected consumer to notify/review.
4. Independently review runoff-catchment 75/80 and terracing 0.9 native-quantity compatibility. Preserve evidence and original source profiles; binding repair is not threshold approval.
5. Add generic representation/native-quantity checks only against declared metadata; no hardcoded dataset-specific scientific rules. Current structure/schema generation cannot establish native geospatial compatibility.
