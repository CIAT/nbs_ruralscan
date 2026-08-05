# Discovery log — Water Harvesting & Conservation · terracing · T3

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 379 | 30 | 5 |
| updated_lit | 31 | 15 | 5 |
| grey | 18 | 18 | 4 |
| tool | 14 | 14 | 2 |

### Verbatim search terms

- **stock:** `OpenAlex title.search Q1: (terracing OR "stone bund") AND (runoff OR "water harvesting") sort=cited_by_count:desc | Q2: (terracing OR "bench terrace") AND (drought OR erosion)`
- **updated_lit:** `OpenAlex title.search: (terracing OR "stone bund") AND (drought OR "soil moisture" OR "water harvesting") filter from_publication_date:2015-01-01 sort=cited_by_count:desc`
- **grey:** `WebSearch EN: 'bench terrace stone bund fanya juu design siting slope soil water conservation manual drought FAO WOCAT drylands' ; ES/FR: 'terrazas banquetas conservacion suelo agua sequia manual diseno pendiente FAO / cordons pierreux Sahel captage eau ruissellement'`
- **tool:** `WebSearch: 'terracing suitability GIS model slope runoff GitHub soil water conservation site selection tool' ; 'GitHub soil water conservation suitability terrace bund runoff harvesting model script slope threshold reclassify'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `terraces_mitigate_2015_drought_ethiopia_2018` | updated_lit | paywalled | ok | high | Soil water management practices (terraces) helped to mitigate the 2015 drought in Ethiopia — Direct T3 drought-buffering: terraces quantifiably mitigated a named drought year, semi-arid Ethiopia (LMIC |
| `stone_bunds_trenches_runoff_semiarid_ethiopia_2015` | stock | oa | ok | high | Evolution of the effectiveness of stone bunds and trenches in reducing runoff and soil loss in the semi-arid Ethiopian highlands — Green OA. Stone-bund subpractice explicit; runoff + soil-loss (erosio |
| `terracing_water_erosion_metaanalysis_china_2017` | stock | paywalled | ok | high | Effects of terracing practices on water erosion control in China: A meta-analysis — Highest-tier synthesis (meta-analysis, 284 cites) of terracing erosion-hazard control magnitude. Paywalled -> acquis |
| `terrace_failure_connectivity_runoff_semiarid_2009` | stock | paywalled | ok | high | Application of connectivity theory to model the impact of terrace failure on runoff in semi-arid catchments — Hazard-TO-structure lens: terrace failure -> concentrated runoff/erosion cascade. Directly |
| `runoff_soilloss_rainfed_terraces_nepal_2003` | stock | paywalled | ok | med | Runoff and soil erosion on cultivated rainfed terraces in the Middle Hills of Nepal — Rainfed terrace runoff/erosion, Nepal Middle Hills (LMIC). Slope-limiter context. Paywalled -> queue. |
| `slow_forming_terraces_yield_erosion_rwanda_2012` | stock | oa | ok | med | Soil erosion, soil fertility and crop yield on slow-forming terraces in the highlands of Buberuka, Rwanda — Green OA, LMIC E.Africa highlands. Slow-forming (progressive stone/soil-bund) terraces; eros |
| `terrace_soilmoisture_metaanalysis_china_2019` | updated_lit | paywalled | ok | high | How can terracing impact on soil moisture variation in China? A meta-analysis — Meta-analysis quantifying terrace -> soil-moisture gain (drought/dry-spell buffering). High-tier synthesis. Paywalled -> |
| `terrace_construction_soilmoisture_loess_2021` | updated_lit | oa | ok | high | Effect of terrace construction on soil moisture in rain-fed farming area of Loess Plateau — Gold OA. Rain-fed terrace moisture-security in a semi-arid dryland; quantified profile-storage gain. |
| `soilmoisture_new_bench_terraces_ethiopia_2019` | updated_lit | oa | ok | med | Spatial Variability of Soil Moisture in Newly Implemented Agricultural Bench Terraces in the Ethiopian Plateau — Gold OA, LMIC. Bench-terrace moisture redistribution early post-construction; relevant  |
| `wocat_fanya_juu_terraces_1336` | grey | repo | ok | high | WOCAT SLM Technology #1336 - Fanya juu terraces — Diamond source class (WOCAT, LMIC-grounded). Fanya-juu subpractice explicit; documents drought/rainfall context, slope siting range, and maintenance/f |
| `ethiopia_moa_physical_swc_hillside_manual_2014` | grey | oa | ok | high | Ethiopia MoA - Technical Manual on Physical Soil & Water Conservation Measures on Hillside/Degraded Land — Government SWC manual, drylands/degraded-land focus. Hardcoded design-siting criteria (slope  |
| `fao_sti_fanya_juu_innovation` | grey | repo | ok | med | FAO STI Portal - Fanya juu terraces (semi-arid contour vs sub-humid graded design) — FAO grey. States the semi-arid = on-contour (hold rainfall) vs sub-humid = graded (discharge) rule = hazard-respons |
| `fao_manual_conservacion_suelos_ar758s` | grey | oa | ok | med | FAO - Manual para Practicas de Conservacion de Suelos (terrazas / banquetas) — Spanish-language FAO manual (multilingual coverage, LatAm dryland/hillside). Terrace design vs slope + runoff control. OA |
| `nrcs_cps_terrace_code_600` | tool | oa | ok | med | NRCS Conservation Practice Standard - Terrace (Code 600) — Design STANDARD functioning as a rule-tool: hardcoded siting/capacity criteria (channel grade, spacing, storm-capacity design) = terrace haza |
| `swat_terrace_parameterization_runoff_sediment` | tool | oa | ok | med | SWAT bench-terrace parameterization for runoff & sediment yield (model tool) — Represents the SWAT tool's terrace-effect coefficients (curve-number / USLE-P / slope-length adjustments) = quantified ha |

## Gaps / next iteration

SATURATION reached for stock/updated_lit/grey (FAO/WOCAT canon re-surfaced across EN/ES/FR sweeps). REMAINING GAPS: (1) TOOL process is genuinely thin for T3 - no open GitHub repo with hardcoded terrace suitability/hazard weights surfaced via WebSearch; the real tool evidence (SWAT curve-number/USLE-P/slope-length terrace coefficients) lives in papers, so a proper file:line + commit_sha interrogation of an actual SWC/terrace code repo is OUTSTANDING (recommend a direct GitHub API/code-search pass next). (2) Sahel stone-line / cordons-pierreux French grey lit under-sampled - only re-surfaced FAO canon; a targeted CILSS/AGRHYMET/ICRISAT-Sahel francophone sweep would strengthen dryland West-Africa coverage. (3) Flood/siltation hazard-TO-structure evidence is lighter than drought/erosion-buffering (only the terrace-failure connectivity paper) - a dedicated 'terrace overtopping / extreme-rainfall damage / siltation' query would balance the two T3 directions. (4) Geomorphology/land-abandonment terracing literature is high-volume noise on OpenAlex title.search - future runs should add NOT filters (abandonment, cosmogenic, stratigraphy, Pt/MoS2 catalysis) to cut screening load. No files written, no registers touched - JSON is the sole deliverable per hard rules.
