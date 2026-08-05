# Discovery log — Water Harvesting & Conservation · runoff_catchment · T4

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 759 | 30 | 3 |
| updated_lit | 152 | 15 | 4 |
| grey | 21 | 21 | 3 |
| tool | 0 | 10 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: ("water harvesting" OR "check dam" OR "farm pond" OR "percolation tank" OR "recharge") AND ("site selection" OR suitability OR GIS) ; sort=cited_by_count:desc ; + companion run ("check dam" OR "farm pond" OR "nala bund" OR "gully plug") AND (site OR suitability OR morphometric OR watershed)`
- **updated_lit:** `OpenAlex title.search: ("water harvesting" OR "check dam" OR "farm pond" OR "percolation tank" OR "sand dam") AND ("site selection" OR suitability OR siting) ; filter from_publication_date:2015-01-01 ; sort=cited_by_count:desc`
- **grey:** `WebSearch: 'FAO OR WOCAT OR ICRISAT check dam farm pond percolation tank site selection suitability manual water harvesting structure' ; 'IWMI runoff water harvesting suitability mapping drainage line siting India Sahel GIS methodology' ; 'FAO Water Harvesting manual Critchley Siegert 1991 catchment ratio siting criteria macro-catchment'`
- **tool:** `GitHub API q=water+harvesting+suitability+AHP / check+dam+site+selection+GIS / runoff+harvesting+MCDA+earth+engine (sort=stars) ; WebSearch 'site:github.com rainwater harvesting suitability check dam AHP weights slope drainage reclassify earth engine' + 'github water harvesting suitability GEE javascript check dam farm pond runoff AHP'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `khan_maharjan_2005_checkdam_syi_morphometric` | stock | paywalled | ok | high | Check dam positioning by prioritization of micro-watersheds using SYI model and morphometric analysis - Remote sensing and GIS perspective — Seminal (383 cites) macro-catchment: prioritises micro-wate |
| `ammar_2016_mcda_wh_artificial_recharge_iran` | stock | paywalled | ok | high | Multi-criteria analysis and GIS modeling for identifying prospective water harvesting and artificial recharge sites — 243 cites; explicit WH + artificial-recharge structure siting via GIS-MCDA (slope, |
| `jaafari_2019_checkdam_geomorphometric_topohydro` | updated_lit | oa | ok | high | GIS-Based Site Selection for Check Dams in Watersheds: Considering Geomorphometric and Topo-Hydrological Factors — OA gold. Explicit check-dam siting on geomorphometric (stream order, drainage density |
| `aljabari_2016_ahp_gis_wh_azraq_jordan` | updated_lit | oa | ok | high | The Use of AHP within GIS in Selecting Potential Sites for Water Harvesting Sites in the Azraq Basin - Jordan — OA diamond; LMIC MENA drylands (tie-break). AHP weights over slope/runoff/soil/drainage  |
| `alwan_2020_smce_wh_maysan_iraq` | updated_lit | oa | ok | high | Potential Water Harvesting Sites Identification Using Spatial Multi-Criteria Evaluation in Maysan Province, Iraq — OA gold; LMIC dryland (tie-break). Spatial MCE with runoff/slope/soil/land-cover elig |
| `ryan_boakye_2020_sanddam_siting_kenya` | updated_lit | oa | ok | high | Back to the drawing board: assessing siting guidelines for sand dams in Kenya — OA hybrid; LMIC E-Africa dryland. Critically evaluates sand-dam siting guidelines (channel geomorphology, stream order,  |
| `mahmoud_2021_checkdam_suitability_topo_drainage_morocco` | updated_lit | paywalled | ok | high | GIS-based land suitability assessment for check dam site location, using topography and drainage information: a case study from Morocco — LMIC dryland (Morocco). Check-dam suitability driven explicitl |
| `singh_2019_fuzzy_wh_structure_rainfed` | updated_lit | paywalled | ok | high | Fuzzy inference system for site suitability evaluation of water harvesting structures in rainfed regions — Fuzzy membership site-suitability for WH structures in rainfed drylands - aligns with framewo |
| `critchley_siegert_1991_fao_wh_manual` | grey | oa | ok | high | Water Harvesting: A Manual for the Design and Construction of Water Harvesting Schemes for Plant Production (FAO AGL/MISC/17/91) — Seminal FAO manual; macro-catchment vs micro-catchment definitions, c |
| `wocat_slm_wh_technologies_db` | grey | repo | ok | med | WOCAT SLM Database - water harvesting technologies (check dams, ponds, recharge structures) — Diamond source class (WOCAT), LMIC-grounded practice DB. Per-technology qualitative siting/suitability con |
| `sivanappan_fao_wh_smc_small_watersheds` | grey | oa | ok | med | Technologies for water harvesting and soil moisture conservation in small watersheds for small-scale irrigation (R.K. Sivanappan, FAO) — FAO note; farm-pond/percolation-structure siting rules of thumb |
| `gmcda_gee_mcda_mar_webtool` | tool | paywalled | NO | med | A Web-Enabled Tool for Site Suitability Mapping for Managed Aquifer Recharge (MAR) using Google Earth Engine and MCDA (G-MCDA) — Hosted GEE+MCDA web tool for MAR/recharge-structure siting. NOT acquira |

## Gaps / next iteration

Strong OA + paywalled peer-reviewed yield for F3 runoff-catchment WH-structure siting (check dams, farm ponds, sand dams, percolation/artificial-recharge). Key GAPS: (1) TOOL process EMPTY - GitHub API total_count=0 across booleans; no open-source WH-suitability repo exists to pin commit/file:line hardcoded weights. Only a hosted GEE web tool (G-MCDA) with no public code. No extractable tool-parameter evidence for this family. (2) Sahel/W-Africa dryland under-represented - hits cluster in India, Iran/Iraq/Jordan (MENA), Kenya, Morocco; no Sahel-specific siting source surfaced (search more FR-language + AGRHYMET/ICRISAT-Sahel grey). (3) IWMI / ICRISAT discrete siting MANUAL not found as an acquirable doc despite being expected diamond grey - retry direct on iwmi.cgiar.org / oar.icrisat.org. (4) High-cite stock is dominated by groundwater-potential-zone hydrogeology (excluded on PICOS: no WH-structure siting) - real WH-structure stock corpus is thinner/more recent than raw counts suggest. (5) Need to separate 'percolation tank / artificial recharge' (recharge-focused, MAR-adjacent) from surface-storage farm ponds/check dams during extraction - both in-scope F3 but different limiter emphasis (storage/clay vs runoff generation). (6) FR/ES/PT grey not yet run (nala bund/tanka = India-English; Sahel needs 'seuil/digue filtrante/bouli/demi-lune de collecte').
