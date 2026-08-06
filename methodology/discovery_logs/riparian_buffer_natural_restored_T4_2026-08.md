# Discovery log — Riparian Buffers · natural_restored · T4

- Run `riparian_buffer_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.1 · nbs_id `riparian_buffer`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 1040 | 30 | 4 |
| updated_lit | 8588 | 15 | 3 |
| grey | 24 | 24 | 5 |
| tool | 12 | 12 | 3 |

### Verbatim search terms

- **stock:** `OpenAlex title.search:"riparian buffer restoration" (from 1990, sort cited_by_count) ; title.search:"riparian restoration prioritization OR siting OR suitability"`
- **updated_lit:** `OpenAlex title.search:"riparian revegetation OR regeneration OR reforestation", from_publication_date:2015-01-01, sort cited_by_count`
- **grey:** `WebSearch EN: "riparian buffer restoration siting suitability GIS multi-criteria stream network width guidance" ; "riparian forest buffer natural regeneration degraded streambank restoration guidance FAO tropical" ; ES/PT: "restauración vegetación ribereña regeneración natural franja ripária mata ciliar restauração degradada guía"`
- **tool:** `WebSearch + GitHub: "riparian buffer siting GIS tool github stream network suitability model buffer width algorithm" ; github.com/search q=riparian+buffer+suitability OR siting`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `spatial_mcda_riparian_priorities_2013` | stock | paywalled | ok | high | A spatial multi-criteria planning scheme for evaluating riparian buffer restoration priorities — Direct T4: GIS-MCDA prioritization of WHERE to restore riparian buffers (stream network, land use, slop |
| `critical_source_areas_buffer_planning_2009` | stock | paywalled | ok | high | Assessing Critical Source Areas in Watersheds for Conservation Buffer Planning and Riparian Restoration — T4 siting via critical-source-area targeting (adjacent runoff-generating land use = system_con |
| `latam_riparian_forest_buffers_2019` | stock | paywalled | ok | med | Riparian-forest buffers: Bridging the gap between top-down and bottom-up restoration approaches in Latin America — LMIC tie-break (Latin America). F2 restoration approaches + enabling context; some T4 |
| `global_review_riparian_veg_restoration_2015` | stock | paywalled | ok | med | Restoration of riparian vegetation: a global review of implementation and evaluation approaches in the international literature — F2 natural/restored review; passive vs active regen, site condition de |
| `neotropical_riparian_biodiversity_thresholds_2020` | updated_lit | paywalled | ok | med | Thresholds of freshwater biodiversity in response to riparian vegetation loss in the Neotropical region — LMIC (Neotropics). Riparian-condition/width loss thresholds -> regen-potential & minimum-condi |
| `brazil_landuse_loworder_streams_2018` | updated_lit | paywalled | ok | med | Effects of land use and land cover on water quality of low-order streams in Southeastern Brazil: watershed versus riparian zone — LMIC (Brazil). Riparian-zone vs watershed land use (cropland/pasture = |
| `managing_riparian_buffer_strips_es_review_2020` | updated_lit | paywalled | ok | med | Managing riparian buffer strips to optimise ecosystem services: a review — Review linking buffer siting/width/condition to ES outcomes; context + candidate width/placement rules. Paywall -> acquisitio |
| `usda_nrcs_riparian_forest_buffer_cps_391` | grey | oa | ok | high | USDA-NRCS Conservation Practice Standard 391 - Riparian Forest Buffer — Authority grey: design/width criteria, min widths, streamside zone specs -> directly extractable T4 buffer-width & placement rul |
| `epa_riparian_buffer_width_2005` | grey | oa | ok | med | Riparian Buffer Width, Vegetative Cover, and Nitrogen Removal Effectiveness (EPA) — Synthesis of buffer-width vs function; width thresholds (10/30/100 m feasibility bands). OA PDF. |
| `fao_sfm_riparian_forest_buffer_tool` | grey | oa | ok | med | FAO SFM Toolbox - Riparian forest buffer (practice standard) — FAO authority practice standard; placement/condition guidance incl. degraded-streambank restoration. Needs snapshot at extraction. OA web |
| `tropics_riparian_restoration_systematic_map_2025` | grey | oa | ok | med | Restoring riparian habitats for benefits to biodiversity and human livelihoods: a systematic map protocol for riparian restoration approaches in the tropics — LMIC/tropical focus; F2 restoration-appro |
| `conabio_manual_restauracion_riberas_mx` | grey | oa | ok | med | Restauracion ecologica de riberas: Manual para la recuperacion de la vegetacion (CONABIO, Mexico) — Spanish/LMIC manual; passive restoration, advanced/natural regeneration nuclei, site-condition selec |
| `qgis_dynamic_riparian_buffer_brazil` | tool | repo | ok | high | qgis-dynamic-riparian-buffer (gsgeocardoso) - Brazilian Forest Code APP width tool — LMIC tool. Hardcoded APP buffer-width classes by measured river width (<=10m->30m; 10-50->50; 50-200->100; 200-600- |
| `ripzet_sfei_functional_width` | tool | other | ok | med | RipZET - Riparian Zone Estimator Tool (SFEI/ASC) — GIS decision-support tool estimating functional riparian width from slope, vegetation, land use, and drainage-network position -> direct T4 siting/wi |
| `auto_riparian_buffers_springinnovate` | tool | repo | ok | low | auto-riparian-buffers (springinnovate) - DEM-only riparian buffer builder — Builds riparian buffers from a DEM only; hardcoded width/threshold params not confirmed from repo view (2 commits). Needs so |

## Gaps / next iteration

CORPUS SKEW: Stock riparian-restoration literature is temperate/US-dominated (Southwest cottonwood-Tamarix flow-regime cluster is off-scope for T4 siting; it is species/flow-ecology, not buffer placement). LMIC/tropical field siting evidence is thin - best hits (Neotropics, Brazil, LatAm, Mexico CONABIO, PMC tropics protocol) are mostly land-use/condition or approach-typology, not quantified spatial siting rules. F2-SPECIFIC GAP: 'existing riparian condition / regeneration potential + hydro-connectivity' as a mappable T4 limiter is under-evidenced - most sources treat width/placement (shared with F1 planted) rather than regen-potential scoring; expect to lean on condition/degradation proxies (canopy loss, vegetation-loss thresholds) rather than a purpose-built regen-potential layer. TOOL LAYER: strong on regulatory buffer-WIDTH rules (Brazilian Forest Code QGIS tool - LMIC, commit-pinned) and functional-width (RipZET), but NO tool found that scores riparian-restoration SUITABILITY or regen-potential; InVEST has no riparian-buffer-siting model (NDR is nutrient retention, excluded per PICOS). ACCESS: 7 of the strongest peer-reviewed candidates are paywalled -> acquisition_queue (Namita-J); OA coverage is carried mainly by grey (NRCS-391, EPA, FAO, CONABIO). ACQUIRE-NEXT PRIORITY: spatial_mcda_riparian_priorities_2013 (only true GIS-MCDA siting reference found). WOCAT returned no riparian-specific SLM technology - a genuine diamond-source gap for this family.
