# Discovery log — Agroforestry · linear_boundary · T6

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 326 | 24 | 5 |
| updated_lit | 30 | 22 | 5 |
| grey | 34 | 18 | 4 |
| tool | 8 | 6 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: (windbreak OR shelterbelt) AND (yield OR carbon OR biodiversity)  [188 hits] ;  (hedgerow OR "living fence" OR "contour hedgerow") AND (yield OR carbon OR income)  [138 hits]  — sort=cited_by_count:desc, per_page=12`
- **updated_lit:** `OpenAlex title.search filter+publication_year:2015-2026: (hedgerow OR "living fence" OR shelterbelt) AND (adoption OR smallholder OR tropical)  [10 hits] ;  (windbreak OR shelterbelt) AND (yield OR income OR cost)  [20 hits]  — sort=cited_by_count:desc`
- **grey:** `WebSearch (EN+ES): 'windbreak shelterbelt living fence cost per hectare establishment yield benefit smallholder WOCAT FAO field manual' ; 'CIPAV living fence cerca viva costo beneficio ganadería América Latina cortina rompevientos rendimiento' ; 'WOCAT SLM technology contour hedgerow vegetative barrier establishment cost benefit yield database' ; 'World Bank ICRAF windbreak shelterbelt Great Green Wall Sahel cost per hectare carbon farmer income project'`
- **tool:** `GitHub REST + gh search repos: 'windbreak+shelterbelt+suitability' [0], 'riparian+buffer+siting+GIS' [0], 'hedgerow placement optimization' [0], 'windbreak', 'shelterbelt suitability', 'agroforestry suitability GEE', 'riparian buffer siting'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `zhang_2019_threenorth_shelterbelt_carbon` | stock | paywalled | ok | high | Assessment on forest carbon sequestration in the Three-North Shelterbelt Program region, China — Shelterbelt (linear) carbon-sequestration outcome at program scale, China (large re |
| `zheng_2015_shelterbelt_cropyield_ne_china` | stock | paywalled | ok | high | Assessment of the effects of shelterbelts on crop yields at the regional scale in Northeast China — Regional-scale shelterbelt yield-effect quantification, China. 102 cites. Core T |
| `albrecht_2020_flowerstrips_hedgerows_metaanalysis` | stock | oa | ok | high | The effectiveness of flower strips and hedgerows on pest control, pollination services and crop yield: a quantitative synthesis — 636-cite Ecology Letters meta-analysis; hedgerow e |
| `harvey_2013_livefences_windbreaks_biodiversity_tropical` | stock | paywalled | ok | high | Live Fences, Isolated Trees, and Windbreaks: Tools for Conserving Biodiversity in Fragmented Tropical Landscapes — Seminal tropical (LMIC) biodiversity-outcome evidence for live fe |
| `kim_2017_shelterbelt_soc_saskatchewan` | stock | oa | ok | med | Soil organic carbon sequestration by shelterbelt agroforestry systems in Saskatchewan — Shelterbelt SOC-sequestration rates; bronze OA (CJSS PDF). T6 carbon indicator. HIC (Canada) |
| `chan_2020_livingfences_livestock_cambodia` | updated_lit | paywalled | ok | high | Living fences for improved smallholder livestock systems in Cambodia — LMIC (Cambodia) smallholder living-fence livestock/fodder outcomes + adoption context. Forests Trees & Liveli |
| `abera_2021_vetiver_hedgerow_adoption_ethiopia` | updated_lit | oa | ok | high | Farmers' Adoption of Vetiver Grass Hedgerows for Soil and Water Conservation, Haru District, Western Ethiopia — LMIC (Ethiopia) contour vegetative-hedgerow adoption/dis-adoption de |
| `jonczak_2022_shelterbelt_costs_benefits_adoption` | updated_lit | oa | ok | high | Costs, Benefits and Obstacles to the Adoption and Retention of Shelterbelts: Regional Perception and Mind Map Analysis — Directly on shelterbelt cost/benefit + adoption & retention |
| `osorio_2018_windbreak_cropyield_gis_kansas_nebraska` | updated_lit | oa | ok | med | A GIS approach to estimate windbreak crop yield effects in Kansas–Nebraska — Spatialised windbreak yield-effect estimates (bushels/ha) — bridges T6 outcome to placement. Hybrid OA  |
| `battambang_2019_livingfence_adoption_dataset` | updated_lit | repo | ok | med | Farmer adoption of living fences, Battambang, Cambodia (dataset) — LMIC living-fence farmer-adoption micro-dataset (Harvard Dataverse, green OA). Observed-reality adoption evidence |
| `wocat_670_contour_hedgerows_alfalfa_afghanistan` | grey | oa | ok | high | WOCAT SLM Technology #670 — Contour hedgerows of alfalfa in annual cropland (Afghanistan) — Diamond grey source: WOCAT structured establishment/maintenance cost fields + fodder-yie |
| `villanueva_2018_cercas_vivas_revision_tropical` | grey | oa | ok | med | Cercas vivas en sistemas de producción tropicales: una revisión mundial de los usos y percepciones — Spanish global review of tropical living-fence uses/perceptions (income, forage |
| `cipav_lrrd_bursera_livingfence_establishment` | grey | oa | ok | med | Establecimiento de postes de Chacah (Bursera simaruba) como cerco vivo (CIPAV/LRRD) — CIPAV/LRRD LMIC (Latin America) living-fence establishment practice + cost/survival. OA web →  |
| `wb_ieg_fao_great_green_wall` | grey | oa | NO | med | Scaling the Great Green Wall? (World Bank IEG) + FAO GGW status report — WB project-evidence lens on GGW (carbon 250 MtCO2e target, 10M jobs, farmer fodder income ~US$0.35/bundle). |
| `saraheb3_agroforestry_suitability_gee` | tool | repo | ok | low | saraheb3/AgroforestrySuitability_GEE — Field-Buffer + Riparian-Buffer siting scripts (GEE) — Riparian/field-buffer placement is a real code branch (not just README) — practice expl |

## Gaps / next iteration

Quantitative T6 outcome + cost-effectiveness evidence is heavily HIC/temperate (Canada/US/China shelterbelts, European hedgerows); LMIC-grounded numbers are thin and mostly grey (WOCAT, CIPAV) or adoption-only, with scarce indicative $/ha, $/beneficiary, or $/tCO2e figures for tropical living fences/contour hedgerows — cost-effectiveness is the weakest cell. No GitHub tool encodes T6 outcome/cost parameters (tools here are T4 placement/suitability only), so the tool process is effectively empty for T6. Next iteration: targeted CGIAR/ICRAF and CATIE grey-lit sweep for African/SE-Asian windbreak and Latin American live-fence cost-benefit studies (ES/FR/PT title queries) plus 3ie/WOCAT cost fields, to raise LMIC coverage before extraction.
