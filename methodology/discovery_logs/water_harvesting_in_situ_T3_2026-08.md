# Discovery log — Water Harvesting & Conservation · in_situ · T3

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 281 | 36 | 5 |
| updated_lit | 187 | 24 | 4 |
| grey | 22 | 16 | 4 |
| tool | 18 | 18 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search (3 queries): (1) 'zai OR tassa OR "planting pits" OR "micro-basins"'; (2) '"tied ridging" OR "contour bunds" OR "contour ridging"'; (3) '"in-situ rainwater harvesting" OR "soil moisture conservation"'. sort=cited_by_count:desc, per_page=12.`
- **updated_lit:** `OpenAlex title.search + filter from_publication_date:2015-01-01 (2 queries): (1) 'zai OR tassa OR "planting pits"'; (2) '"tied ridging" OR "contour bunds" OR "micro-basins"'. sort=cited_by_count:desc, per_page=12.`
- **grey:** `WebSearch EN: 'FAO WOCAT in-situ rainwater harvesting soil water conservation zai tied ridges drought resilience technology manual drylands'. WebSearch FR/ES: 'zaï cordons pierreux conservation eaux et sols Sahel FAO manuel technique sécheresse OR "conservación de agua y suelo" captación in situ zonas áridas manual'.`
- **tool:** `WebSearch (allowed_domains github.com): 'rainwater harvesting OR soil water conservation suitability model repository python google earth engine slope soil'. WebSearch: 'GitHub rainwater harvesting suitability site selection GIS MCDA model runoff SCS curve number script'. GitHub API: q=rainwater+harvesting+suitability+GIS+MCDA sort=stars; q=soil+water+conservation+runoff+earth+engine.`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `wh_insitu_rwh_landscape_africa_2009` | stock | paywalled | ok | high | A review of in situ rainwater harvesting (RWH) practices modifying landscape functions in African drylands — Seminal in-situ RWH review, African drylands. Core T3: how in-situ WH buffers drought/dry-s |
| `wh_insitu_arid_suitability_method_2014` | stock | paywalled | ok | high | The potential of in situ rainwater harvesting in arid regions: developing a methodology to identify suitable areas — Explicit in-situ WH + suitability-siting methodology; T3 (aridity/rainfall-deficit  |
| `wh_insitu_tied_ridge_mulch_barley_2010` | stock | oa | ok | high | Effects of tied ridges and mulch on barley rainwater use efficiency and production in a semi-arid area — Tied ridging (in-situ) x rainwater-use-efficiency under dry conditions = T3 moisture-security/d |
| `wh_insitu_zai_west_africa_1999` | stock | oa | ok | high | Zai Practice: A West African Traditional Rehabilitation System for Semiarid Degraded Lands — Seminal zai (in-situ planting-pit) source, Sahel semi-arid. T3: drought/degraded-land moisture concentratio |
| `wh_insitu_climate_adapt_maize_2015` | stock | oa | ok | high | Evaluation of In Situ Rainwater Harvesting as an Adaptation Strategy to Climate Change for Maize Production — Explicit in-situ WH framed as climate-change adaptation = direct T3 (hazard buffering). Hy |
| `wh_insitu_contour_bund_mali_2020` | updated_lit | oa | ok | high | Contour bunding technology - evidence and experience in the semiarid region of southern Mali — Recent LMIC Sahel; contour bunds (in-situ, gentle-slope inter-stream placement). T3: runoff/moisture mana |
| `wh_insitu_tied_ridge_cotton_climate_2020` | updated_lit | oa | ok | high | Tied Ridges and Better Cotton Breeds for Climate Change Adaptation — Tied ridges explicitly for climate-change adaptation = T3 hazard buffering. Gold OA. Screen at extraction to keep tied-ridge (pract |
| `wh_insitu_zai_kenya_sorghum_2021` | updated_lit | oa | ok | high | Zai pits for heightened sorghum production in drier parts of Upper Eastern Kenya — Recent E-Africa dryland; zai pits (in-situ) in drier zones = T3 dry-spell/moisture security. Gold OA, LMIC tie-break. |
| `wh_insitu_tied_ridge_furrow_erosion_2021` | updated_lit | oa | ok | med | Runoff and nutrient losses in alfalfa production with tied-ridge-furrow rainwater harvesting — Tied-ridge-furrow: in-situ ridging with a furrow micro-store (borderline in-situ/micro). T3 hazard-side:  |
| `wocat_slm_insitu_wh_db` | grey | oa | ok | high | WOCAT SLM Technologies Database - in-situ RWH / zai / tied-ridge / contour-bund entries — Diamond grey. Per-technology quantitative specs (slope, rainfall band, land use) + degradation/hazard-addresse |
| `fao_water_harvesting_runoff_farming_manual` | grey | oa | ok | med | FAO - Water harvesting in agriculture (runoff farming) + FAO Soil & Water Conservation module — FAO manual: tied ridges effective <1000mm rainfall on <7% slopes (quantitative T3/T4 boundary). Contains |
| `niger_gdte_cordon_pierreux_fiche_2022` | grey | oa | ok | med | Recueil de fiches techniques - Techniques mecaniques de CES/DRS (cordon pierreux, zai) — French Sahel govt/programme SWC manual. Quantitative: cordons pierreux 400-1100mm, slope 0.2-3%, limon-sandy/cr |
| `embrapa_captacion_insitu_arid_es` | grey | oa | ok | med | Metodos de captacion de agua de lluvia in situ para cultivos en zonas aridas (Embrapa) — Spanish-language in-situ micro-catchment/moisture-conservation manual, arid zones (LatAm dryland context). T3 m |
| `rwh_gis_mcda_scs_cn_suitability` | tool | oa | NO | low | Integrating GIS-Based MCDA and SCS-CN for Identifying Potential Rainwater Harvesting Zones (semi-arid) — OFF-SCOPE risk: SCS-CN RWH-zone siting targets external-catchment runoff generation (macro/micr |

## Gaps / next iteration

TOOL process is the weak axis: no GitHub repo confirmed to encode an in-situ (LOW-runoff) moisture-conservation suitability branch with hardcoded slope/soil/rainfall thresholds. Web/API hits are (a) GIS-MCDA+SCS-CN RWH-siting papers that target EXTERNAL-catchment runoff generation (belongs to macro/micro-catchment families, off-scope for F1 in-situ) and (b) generic FAO-56 soil-water-balance code (soilwater org) with no WH-practice branch (PICOS fail, like spatMCDA.R). Recommend a dedicated deeper GitHub interrogation (commit-pinned file:line) before registering any tool EV; likely the tool corpus for in-situ WH is genuinely thin. Second gap: hazard-TO-structure T3 content (siltation of pits/bunds, extreme-flood/gully damage, structure failure/breach risk on steeper or high-intensity-rain sites) is under-represented - only partially covered by the tied-ridge-furrow erosion paper and contour-ridge rill-erosion titles (W2050525355, W2001516273, W2011353633 seen in stock listing but not yet screened-in); a targeted follow-up query on 'contour ridge/bund failure OR breach OR overtopping OR siltation' would fill it. Third: WOCAT records need per-technology snapshotting (locator = technology ID) to become extractable. Multilingual grey (FR Sahel, ES LatAm) is well-covered and should be extracted with native+EN quote pairs.
