# Discovery log — Water Harvesting & Conservation · terracing · T4

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 106 | 27 | 4 |
| updated_lit | 33 | 21 | 3 |
| grey | 14 | 14 | 4 |
| tool | 8 | 8 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: (terracing OR "stone bund") AND (suitability OR runoff) ; sort=cited_by_count:desc ; also ran ("fanya juu" OR "stone bund" OR terracing) AND (semi-arid OR Ethiopia)`
- **updated_lit:** `OpenAlex title.search: (terracing OR "stone bund") AND (suitability OR GIS) , from_publication_date:2015-01-01 ; sort=cited_by_count:desc ; supplemented by WebSearch 'GIS MCDA water harvesting terracing suitability slope runoff SWAT'`
- **grey:** `WebSearch EN: 'terracing bench terrace stone bund suitability slope criteria GIS site selection FAO WOCAT manual drylands' ; WebSearch ES: 'cordones de piedra terrazas conservacion suelo agua aptitud pendiente FAO manual OR banquetas antierosivas'`
- **tool:** `WebSearch github.com: 'rainwater harvesting suitability slope runoff curve number weighted overlay AHP python earthengine' ; 'github GIS MCDA water harvesting terracing suitability model slope runoff SWAT reclassify weights'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `nyssen_2006_stonebunds_ethiopia_onsite` | stock | oa | ok | high | Interdisciplinary on-site evaluation of stone bunds to control soil erosion on cropland in Northern Ethiopia — Stone bund (F4 terracing/SWC) explicit; Tigray semi-arid drylands LMIC. Slope/soil condit |
| `gebreegziabher_2006_stone_terraces_adoption` | stock | oa | ok | med | Determinants of adoption and continued use of stone terraces for soil and water conservation in an Ethiopian highland watershed — Stone terraces explicit, Ethiopian highlands. Slope as biophysical det |
| `nyssen_2015_stonebunds_trenches_semiarid` | stock | oa | ok | high | Evolution of the effectiveness of stone bunds and trenches in reducing runoff and soil loss in the semi-arid Ethiopian highlands — Stone bunds + trenches explicit; semi-arid LMIC. Runoff-reduction vs  |
| `dahlke_2012_terrace_soils_yemen_suitability` | stock | paywalled | ok | high | Terrace soils in the Yemen Highlands: using physical, chemical and radiometric data to assess their suitability — Explicit terrace + soil SUITABILITY (depth, texture, WHC) in MENA dryland highland =>  |
| `beckers_2019_runoff_terraced_wadi_gis` | updated_lit | paywalled | ok | high | GIS-based hydrological modelling to assess runoff yields in ancient-agricultural terraced wadi fields (central Negev) — Terraced wadi water-harvesting fields; GIS runoff-yield siting in arid Negev dry |
| `rae_2025_rice_terrace_land_suitability_gis` | updated_lit | oa | ok | high | Modelling for a land suitability analysis of rice terraces on the upland area using the geographic information system — Explicit terrace land-SUITABILITY GIS model (slope, soil, land-cover eligibility |
| `konso_2025_rwh_mcda_ethiopia` | updated_lit | oa | ok | med | Multi-Criteria Analysis for Effective Rain Water Harvesting Site Identification in Konso Zone, Ethiopia — RWH MCDA siting, Konso drylands Ethiopia LMIC. Criteria: rainfall, land cover, curve number, T |
| `hami_qeshan_2023_runoff_structures_iraq` | updated_lit | oa | ok | med | Proposing Optimal Locations for Runoff Harvesting and Water Management Structures in the Hami Qeshan Watershed, Iraq — GIS-MCDA runoff-harvesting structure siting, MENA dryland LMIC; terracing among c |
| `fao_ad083e_watershed_terrace_manual` | grey | oa | ok | high | FAO Watershed Management Field Manual - terrace/hillside-ditch design & site conditions (AD083E ch VII-VIII) — Canonical grey: explicit terrace siting thresholds - slope 7-25deg hand / 7-20deg machine |
| `fao_ar758s_conservacion_suelos_es` | grey | oa | ok | med | FAO Manual para Practicas de Conservacion de Suelos (ES, Ecuador, ar758s) - terrazas y cordones de piedra — Spanish grey: stone-cordon (cordones de piedra) rule for extremely stony soils where machine |
| `sheng_bench_terrace_design_isco` | grey | oa | ok | med | Bench Terrace Design Made Simple - Ted C. Sheng (ISCO / Purdue NSERL) — Classic bench-terrace design ref: slope limits, spacing as function of slope/soil-depth. Seminal grey/technical. PDF cache-able. |
| `wocat_slm_terracing_stonebund_db` | grey | repo | ok | high | WOCAT SLM Global Database - bench terrace / stone bund / fanya juu technologies — Diamond LMIC-grounded SLM technology DB; per-technology slope range, soil, land-use eligibility qualifiers. LEAD - nee |
| `betwa_2017_rwh_mcda_india` | updated_lit | repo | ok | med | GIS-based multi-criteria approach for identification of rainwater harvesting zones in upper Betwa sub-basin, Madhya Pradesh, India — India semi-arid LMIC RWH-zone MCDA (slope, drainage density, land u |

## Gaps / next iteration

TOOL process is the main gap: no open repo with a terracing-specific code branch exposing hardcoded slope/soil/runoff reclassify tables (SWAT+SCS-CN+AHP/weighted-overlay recur as published methods, not pinnable commits; only GitHub hit is urban-tree stormwater, out of scope). A dedicated GitHub/GEE-script search is needed to find a repo where terracing is a real parameterised criterion, then pin commit sha + file:line. OpenAlex recent-title set is heavily polluted by archaeology/heritage/fluvial 'terrace' papers, so GIS-terrace-suitability siting lit is thinner than raw counts suggest and leans on WebSearch supplements. LMIC coverage strong for E.Africa (Ethiopia/Tigray stone bunds) and MENA (Yemen, Negev, Iraq) but light for Sahel/West-Africa terracing and South-Asia bench terraces beyond the Betwa India lead. WOCAT SLM records are a high-value LMIC-grounded lead needing specific technology-record URLs + snapshots before extraction. Adoption studies carry mixed T4/M2b content: extract slope/soil (T4) only, route tenure/labour/credit determinants to M2b operational_risk. No expert-opinion (Namita Task H) inputs sought this pass.
