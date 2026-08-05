# Discovery log — Water Harvesting & Conservation · micro_catchment · T4

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 402 | 15 | 5 |
| updated_lit | 417 | 15 | 5 |
| grey | 8 | 8 | 4 |
| tool | 9 | 9 | 2 |

### Verbatim search terms

- **stock:** `OpenAlex title.search:(micro-catchment OR microcatchment OR "semi-circular bund" OR "runoff farming") AND (suitability OR slope OR runoff OR catchment), sort=cited_by_count:desc, per_page=15`
- **updated_lit:** `OpenAlex title.search:("water harvesting" OR microcatchment OR "micro-catchment" OR runoff) AND (suitability OR "site selection" OR GIS OR "multi-criteria"), filter from_publication_date:2015-01-01, sort=cited_by_count:desc, per_page=15`
- **grey:** `WebSearch EN: 'micro-catchment water harvesting suitability slope soil ratio FAO WOCAT manual semi-circular bunds drylands'; ES/FR: 'captacion de agua microcuenca aptitud pendiente suelo manual / captage eau ruissellement demi-lune aptitude Sahel FAO'`
- **tool:** `WebSearch site:github.com 'rainwater harvesting suitability SCS-CN runoff Google Earth Engine QGIS model slope' and '...reclassify slope soil rainfall weighted overlay AHP script earth engine potential zones'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `boers_1986_mcwh_arid` | stock | paywalled | ok | high | Micro-Catchment-Water-Harvesting (MCWH) for arid zone development — Foundational MCWH design paper (Agric Water Mgmt, 88 cites). Explicit micro-catchment layout, catchment:cropped-area ratio, slope/so |
| `boers_1986_linreg_soilwater_design` | stock | paywalled | ok | high | A linear regression model combined with a soil water balance model to design micro-catchments for water harvesting — Micro-catchment sizing/design via runoff + soil-water-balance; directly informs run |
| `prinz_2004_microcatchment_swc` | stock | paywalled | ok | high | Impact of water harvesting techniques on soil and water conservation: a case study on a micro catchment — J Arid Environments (95 cites). Micro-catchment WH case study; slope/soil/runoff performance i |
| `evenari_1968_runoff_farming_layout` | stock | paywalled | ok | med | Runoff Farming in the Desert I. Experimental Layout — Seminal runoff-farming layout (50 cites, is_seminal). Catchment:cropped ratios and slope-length logic; historical anchor for micro-catchment sitin |
| `li_2005_field_microcatchment_loess` | stock | repo | ok | med | Soil quality responses to alfalfa watered with a field micro-catchment technique in the Loess Plateau of China — Green OA. Field micro-catchment technique in a Chinese dryland (Loess Plateau); soil/wa |
| `mahmoud_2016_mcda_gis_wh_recharge` | updated_lit | paywalled | ok | high | Multi-criteria analysis and GIS modeling for identifying prospective water harvesting and artificial recharge sites — J Cleaner Production (243 cites). GIS-MCDA WH siting with slope, soil, runoff, dra |
| `aladamat_2016_ahp_gis_azraq_jordan` | updated_lit | oa | ok | high | The Use of AHP within GIS in Selecting Potential Sites for Water Harvesting Sites in the Azraq Basin, Jordan — Diamond OA. AHP+GIS WH site selection, Jordan dryland (LMIC/MENA tie-break). Explicit cri |
| `maysan_2020_smce_wh_iraq` | updated_lit | oa | ok | high | Potential Water Harvesting Sites Identification Using Spatial Multi-Criteria Evaluation in Maysan Province, Iraq — Gold OA (ISPRS IJGI, 65 cites). SMCE WH siting, Iraq dryland. Slope/soil/LULC/runoff/ |
| `mcdm_2020_runoff_storage_zones` | updated_lit | oa | ok | high | GIS-based multi criteria decision making method to identify potential runoff storage zones within watershed — Gold OA (75 cites). MCDM for runoff-storage-zone siting; drainage geomorphology (stream or |
| `fuzzy_ahp_2017_wh_zones` | updated_lit | paywalled | ok | high | A GIS-Based Integrated Fuzzy Logic and Analytic Hierarchy Process Model for Assessing Water-Harvesting Zones — Fuzzy-membership + AHP WH-zone model (73 cites). Fuzzy criteria curves + weights for WH s |
| `fao_critchley_siegert_1991_wh_manual` | grey | oa | ok | high | Water Harvesting: A Manual for the Design and Construction of Water Harvesting Schemes (FAO, Critchley & Siegert) — Canonical FAO manual (gold grey). Micro-catchment ch. u3160e07.htm: catchment:croppe |
| `wocat_semicircular_bunds_slm` | grey | oa | ok | high | WOCAT SLM Technologies — semi-circular bunds / eyebrow terraces / micro-catchment WH — WOCAT SLM DB (diamond source class, LMIC-grounded). Per-technology entries give slope range, soil, rainfall, land |
| `fuberlin_iwrm_microcatchment` | grey | oa | ok | med | Microcatchment water harvesting — FU-Berlin IWRM (traditional to modern techniques) — Teaching/reference web page restating micro-catchment ratios/slope. Secondary (largely synthesises FAO manual); us |
| `fao_ai128s_latam_wh_manual_es` | grey | oa | ok | med | Manual de captacion y aprovechamiento del agua de lluvia — experiencias en America Latina (FAO, Spanish) — FAO LatAm rainwater-harvesting manual (Spanish). Micro-catchment (microcaptacion) sections wi |
| `gh_rodcgon_scsuh_qgis` | tool | repo | NO | low | ScsUh — QGIS Plugin: runoff hydrograph via SCS-CN + UH method — Pure SCS-CN runoff-generation tool. Runoff coefficient/CN is a T4 input layer, but micro-catchment SITING is not a code branch here. pic |
| `gh_alisafari_aquaflow` | tool | repo | NO | low | AquaFlow — SCS runoff estimation (Q=(P-Ia)^2/(P-Ia+S)) — Implements hardcoded SCS-CN Q formula. Runoff-only, no WH siting/suitability branch. picos_ok=false; interrogate for any hardcoded CN-lookup/so |

## Gaps / next iteration

TOOL is the weakest process: only pure SCS-CN runoff repos (ScsUh, AquaFlow) surfaced — the micro-catchment siting/suitability logic lives in ArcGIS/QGIS paper workflows, not in any OA repo with a committed reclassify/weighted-overlay/AHP branch. No commit-sha/file:line pinning done yet; both tool candidates are picos_ok=false pending code interrogation (they may still yield hardcoded CN/soil-group lookup tables as T4 runoff-input evidence, but not siting rules). GREY and TOOL retrieved counts are WebSearch surfacings, not true OpenAlex totals. Geographic skew: the GIS-MCDA lit clusters on MENA/India/Jordan/Iraq; Sahel semi-circular-bund/demi-lune quantitative siting thresholds are thin in the OpenAlex title-search and lean on FAO/WOCAT grey — a dedicated French Sahel (demi-lune, cordons pierreux, zai) grey/lit pass is advisable before F2 T4 synthesis. Drainage-geomorphology variables (stream order, drainage density, proximity-to-channel) are well covered by the MCDM/runoff-storage-zone papers; curvature/TWI is only implicitly covered and may need a targeted terrain-attribute search. All grey sources require .html/.pdf snapshots + section/anchor locators before any EV registration (none acquired in this discovery-only pass).
