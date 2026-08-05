# Discovery log — Forest Restoration · active_planting · T3

- Run `forest_restoration_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** discovery + screening only. No extraction.
- **grey + tool = complete.** **stock + updated_lit = IN PROGRESS** — OpenAlex hit its daily budget (HTTP 429, resets midnight UTC); candidates below are provisional (WebSearch/canon fallback), to be finalised with real OpenAlex nets on rerun.

## grey + tool candidates (final)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `fao_global_guidelines_restoring_resilience_forests` | grey | oa | ok | high | FAO climate-change guidelines for forest managers / Global guidelines for restoring the resilience of forests — FAO. Plantation design/species selection adapted to drought; avoid clear-cut; residue ma |
| `fao_integrated_fire_management_voluntary_guidelines_2024` | grey | oa | ok | med | FAO Integrated Fire Management Voluntary Guidelines (2024) — FAO 2024. Landscape-level fire management incl. restoration/planting fire resilience - T3 fire hazard response. Confirm the exact 2024 IFM  |
| `climate_adapt_forest_restoration_after_climate_disasters_es` | grey | oa | ok | med | Restauracion forestal tras catastrofes relacionadas con el clima (Forest restoration after climate-related disasters) - EEA Climate-ADAPT — Multilingual (ES/EN). Restoration/replanting as response to  |
| `iufro_stanturf_climate_adaptive_restoration_reforestation_guidelines` | grey | paywalled | ok | high | Guidelines for Climate Adaptive Forest Restoration and Reforestation Projects (Stanturf, IUFRO) — IUFRO/Elsevier book. Climate-adaptive planting design against future drought/fire - high relevance but |
| `roam_iucn_wri_restoration_opportunities_assessment` | tool | oa | ok | low | A Guide to the Restoration Opportunities Assessment Methodology (ROAM) - IUCN/WRI — Methodology (not code) - restoration opportunity/prioritisation framework; climate-risk is one criterion but hazard- |
| `gh_langoodall_project_scotland_reforestation` | tool | repo | ok | med | langoodall/Project-Scotland-Reforestation (ML planting-suitability scenarios) — Practice explicit (reforestation planting scenarios). Suitability scenarios coded in scotland.py / Scotland.Rmd incl. cl |
| `gh_tnc_reforestationhub_cookpatton2020` | tool | repo | ok | low | thenatureconservancy/ReforestationHub (Cook-Patton et al. 2020 restoration opportunity, R) — US contiguous restoration-opportunity code (R). Mostly T4 opportunity/cost, limited direct T3 hazard params |

## stock + updated_lit candidates (PROVISIONAL — OpenAlex pending)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `large_seedling_survival_restorations_worldwide_2021` | stock | paywalled | ok | high | Climate and species stress resistance modulate the higher survival of large seedlings in forest restorations worldwide — Global active-restoration planting; seedling size x climate stress-resistance d |
| `road_to_recovery_asian_forest_restoration_2022` | stock | oa | ok | med | The road to recovery: a synthesis of outcomes from ecosystem restoration in tropical and sub-tropical Asian forests — OA synthesis of restoration (incl. active planting) outcomes; includes survival/mo |
| `allen_global_drought_heat_tree_mortality_2010` | stock | paywalled | NO | med | A global overview of drought and heat-induced tree mortality reveals emerging climate change risks for forests — Seminal (6500+ cites) drought/heat mortality mechanism = hazard-to-restoration context, |
| `mortality_thresholds_juvenile_trees_drought_heatwaves_2023` | updated_lit | oa | ok | high | Mortality thresholds of juvenile trees to drought and heatwaves: implications for forest regeneration across a landscape gradient — OA (Frontiers). Juvenile-tree drought+heat mortality thresholds acro |
| `tropical_seedling_drought_functional_trait_restoration_2026` | updated_lit | oa | ok | high | Tropical seedling performance under drought: a functional trait approach for species selection in restoration — OA (iForest). Drought performance of restoration seedlings; species = parameter (functio |
| `ecological_restoration_age_of_apocalypse_2023` | updated_lit | paywalled | ok | high | Ecological restoration in the age of apocalypse — GCB. Novel drought/heatwave levels cause complete restoration (incl. intensive outplanting) failure - key T3 hazard-to-establishment framing with quan |
| `seedling_field_performance_hot_dry_restoration_2025` | updated_lit | paywalled | ok | high | Seedling field performance on hot, dry forest restoration sites: influence of plant attributes — New Forests 2025. Planted-seedling field survival on hot/dry restoration sites vs plant attributes - di |
| `reforestation_failure_project_scale_mediterranean_dryland_2021` | updated_lit | paywalled | ok | high | Assessing reforestation failure at the project scale: the margin for technical improvement under harsh conditions - a case study in a Mediterranean Dryland — STOTEN 2021. Project-scale reforestation f |

### Verbatim search terms (as run / attempted)

- **stock:** `INTENDED OpenAlex boolean (title.search): (reforestation OR afforestation OR "tree planting") AND (drought OR fire OR survival OR mortality OR resilience) sort=cited_by_count:desc | RUN via WebSearch fallback: 'reforestation seedling drought survival mortality restoration planting tropical review' ; 'afforestation reforestation fire risk resilience planted forest climate hazard'`
- **updated_lit:** `WebSearch (OpenAlex fallback): 'active restoration planting drought mortality climate 2021..2026 review seedling establishment' [intended OpenAlex: same stock boolean + from_publication_date=2015-01-01, sort=publication_date]`
- **grey:** `WebSearch EN+ES: 'FAO reforestation restoration drought fire climate resilience planting guidelines report' ; 'WRI IUCN forest landscape restoration drought fire resilience planting technical guide ROAM' ; 'CIFOR-ICRAF World Bank reforestation restoration seedling survival drought fire climate resilience report LMIC' ; 'restauracion forestal reforestacion sequia incendios supervivencia plantacion resiliencia clima guia'`
- **tool:** `WebSearch + GitHub topics: 'restoration opportunity mapping suitability github reforestation potential model tree planting' ; 'github Afforestation Tracker Sahel tree planting suitability criteria drought aridity code' ; github.com/topics/reforestation`

## Gaps / next iteration

API OUTAGE: OpenAlex was budget-blocked (HTTP 429, resets midnight UTC) and Semantic Scholar 429 (no key) for the entire session, so stock/updated_lit retrieved counts are WebSearch-surfaced, NOT true corpus totals. ACTION: re-run the intended OpenAlex booleans (given verbatim in srch.search_terms) after reset to get real PRISMA counts and a proper high-cite ranking. TOOL gap: GitHub file contents + commit sha unreadable via WebFetch (SPA) - the two code tools are screened-in but hazard thresholds are UNVERIFIED; must pin commit+file:line and confirm a real code branch (not README) before any tool EV extraction. COVERAGE gaps: (1) flood/erosion-control and wind hazard responses are thin - searches surfaced mostly drought+fire; add targeted queries (restored cover x runoff/erosion, windthrow of young plantings). (2) Reforestation-vs-afforestation prior-land-cover flag + do-no-harm caveat for afforesting native non-forest ecosystems (savanna/grassland) surfaced only in prose (fire-risk of afforestation) - needs dedicated evidence. (3) LMIC-specific quantified survival/mortality under drought is mostly grey (CIFOR-ICRAF, positive-bias) - seek peer-reviewed LMIC field trials. (4) Multilingual FR/PT grey not yet run (only EN+ES done).

---

## stock + updated_lit — FINALISED (OpenAlex online, run `fr_stocklit_finish_2026-08`, 2026-08-05)

Supersedes the provisional section above (OpenAlex was budget-blocked at first pass).

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 244 | 30 | 5 |
| updated_lit | 156 | 30 | 4 |

**Verbatim terms:**
- **stock:** `title.search primary: (reforestation OR afforestation OR "tree planting" OR "restoration planting") AND (drought OR mortality OR survival); companion cover-hazard string also run: (reforestation OR afforestation OR "tree planting" OR "restoration planting") AND (fire OR flood OR erosion OR heat)`
- **updated_lit:** `title.search primary (from_publication_date:2015-01-01): (reforestation OR afforestation OR "restoration planting" OR "enrichment planting") AND (drought OR fire OR mortality OR survival); companion: (reforestation OR "tree planting" OR "restoration planting") AND ("seedling survival" OR "drought mortality" OR "climate")`

**Screened-in (stock/lit):**

| source_id | process | access | rel | title / note |
|---|---|---|---|---|
| `reforest_drylands_drought_filters_2020` | stock | repo | high | Reforesting drylands under novel climates with extreme drought filters: the importance of trait-based species selection — F3 active-planting drought hazard response in drylands; tr |
| `reforest_water_yield_drought_risk_2022` | stock | paywalled | high | Large-scale reforestation can increase water yield and reduce drought risk for water-insecure regions — Restored forest cover -> drought-risk reduction (hazard mitigation service); |
| `afforestation_arid_survival_taklimakan_2016` | stock | oa | med | Survival and growth of three afforestation species under high saline drip irrigation in the Taklimakan Desert, China — Afforestation survival under arid/drought + salinity stress;  |
| `reforestation_flood_wetspa_hornad_2006` | stock | paywalled | med | WetSpa Model Application for Assessing Reforestation Impacts on Floods in Margecany-Hornad Watershed, Slovakia — Flood-control hazard response by restored cover (spatial/hydrologic |
| `afforestation_erosion_sediment_catchments_2009` | stock | paywalled | med | Investigating the effects of afforestation on soil erosion and sediment mobilisation in two small catchments — Erosion/sediment control by restored cover (hazard mitigation). Pract |
| `enrichment_planting_seedling_survival_tradeoffs_2018` | updated_lit | paywalled | high | Tree Seedling Survival Depends on Canopy Age, Cover and Initial Composition: Trade-offs in Forest Restoration Enrichment — Direct F3 enrichment-planting survival under canopy/micro |
| `postfire_regeneration_failure_reforestation_boreal_2021` | updated_lit | oa | high | Mitigating post-fire regeneration failure in boreal landscapes with reforestation and variable retention harvesting — Active reforestation as fire-hazard recovery response (post-fi |
| `reforestation_drought_west_africa_2017` | updated_lit | paywalled | med | Future impacts of global warming and reforestation on drought patterns over West Africa — LMIC (West Africa) reforestation-drought interaction; climate-modelling of restoration eff |
| `forest_diversification_novel_planting_climate_2017` | updated_lit | oa | med | Climate change mitigation through adaptation: the effectiveness of forest diversification by novel tree planting regimes — Diversified/novel tree-planting as climate-resilience (dr |
