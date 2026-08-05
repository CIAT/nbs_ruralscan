# Discovery log — Water Harvesting & Conservation · micro_catchment · T3

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 513 | 15 | 4 |
| updated_lit | 200 | 15 | 3 |
| grey | 18 | 18 | 4 |
| tool | 10 | 10 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: (microcatchment OR micro-catchment OR semi-circular OR runoff) AND (harvesting OR farming) | sort=cited_by_count:desc per_page=15`
- **updated_lit:** `OpenAlex title.search: (micro-catchment OR microcatchment OR runoff) AND (rainwater harvesting OR water harvesting OR crop), from_publication_date:2015-01-01 | sort=cited_by_count:desc per_page=15`
- **grey:** `WebSearch EN: 'micro-catchment water harvesting semi-circular bunds drought dry-spell mitigation FAO WOCAT drylands runoff catchment ratio'; 'ICRISAT IWMI micro-catchment rainwater harvesting supplemental irrigation drought resilience Sahel'; 'FAO water harvesting manual semi-circular bund microcatchment catchment cultivated area ratio slope drought Critchley Siegert'`
- **tool:** `WebSearch domain:github.com 'rainwater harvesting site selection SCS-CN curve number runoff python R repository code'; general 'GitHub water harvesting suitability model runoff GIS MCDA SCS-CN site selection tool'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `boers_1986_mcwh_arid` | stock | paywalled | ok | high | Micro-Catchment-Water-Harvesting (MCWH) for arid zone development — Seminal (is_seminal). Agricultural Water Management. Micro-catchment explicit; arid-zone drought/moisture-security framing = core T3 |
| `schiettecatte_2004_microcatchment_swc` | stock | paywalled | ok | high | Impact of water harvesting techniques on soil and water conservation: a case study on a micro catchment in southern (Tunisia/Syria) — Micro-catchment explicit + soil-erosion/siltation (hazard-to-struc |
| `qiwang_2007_microwh_ridge_furrow` | stock | paywalled | ok | med | Runoff Efficiency and the Technique of Micro-water Harvesting with Ridges and Furrows, for Potato Production in semi-arid China — Micro-catchment ridge-furrow runoff:crop ratio; runoff efficiency = th |
| `dewinnaar_2007_gis_runoff_thukela` | stock | paywalled | ok | med | A GIS-based approach for identifying potential runoff harvesting sites in the Thukela River basin, South Africa — Runoff-harvesting siting (T4-leaning) but encodes runoff-generation + slope/soil crite |
| `brazil_2018_wh_living_with_drought` | updated_lit | oa | ok | high | Harvesting Water for Living with Drought: Insights from the Brazilian Human Coexistence with Semi-Arid Conditions — OA (Sustainability). Directly T3: WH as drought-coexistence/livelihood buffer in LMI |
| `karimi_2019_runoff_map_rwh_zones` | updated_lit | paywalled | ok | med | Integrating runoff map of a spatially distributed model and thematic layers for identifying potential rainwater harvesting sites — Runoff-based RWH siting; runoff-generation as the donor-catchment dri |
| `semiarid_tropics_2022_rwh_zones` | updated_lit | oa | ok | med | Identifying potential zones for rainwater harvesting interventions for sustainable intensification in the semi-arid tropics — OA (PMC). Semi-arid tropics RWH zoning; drought/dry-spell intensification  |
| `fao_critchley_siegert_1991_wh_manual` | grey | oa | ok | high | Water Harvesting: A Manual for the Design and Construction of Water Harvesting Schemes for Plant Production (Critchley & Siegert, FAO AGL/MISC/17/91) — Canonical grey source, OA PDF. WebFetch-confirme |
| `wocat_slm_semicircular_bund` | grey | repo | ok | high | WOCAT SLM Technologies Database - semi-circular bund / demi-lune / microcatchment technologies — LMIC-grounded SLM tech DB (diamond source class). Per-technology QuickShare sheets carry C:CA ratios, s |
| `icraf_microcatchment_rwh_cgspace` | grey | oa | ok | med | Microcatchment Rainwater Harvesting (CGIAR/ICRAF, arid and semiarid zones) — OA CGSpace PDF. Micro-catchment RWH practice guide for arid/semi-arid; runoff-donor/cropped-basin design + drought framing. |
| `kothawadegs_runoff_cn_method` | tool | repo | NO | low | kothawadegs/Runoff_CN_method (SCS-CN runoff computation, Python) — SCREENED OUT. Hardcodes CN defaults for URBAN floods; no micro-catchment WH siting branch/criterion. WH subpractice not present in co |

## Gaps / next iteration

TOOL PROCESS EMPTY (0 included): no open-source repo encodes micro-catchment WH siting rules (C:CA ratio, short-slope, soil) as an explicit code branch. Available repos (kothawadegs/Runoff_CN_method, GeoscienceAustralia/flowtools, benjiyamin/pyflo) implement only the SCS-CN runoff sub-method with urban/generic defaults - fail PICOS. If a WH-siting tool is needed, look to GEE MCDA-AHP water-harvesting scripts (the T4 siting-paper query surfaced many AHP/fuzzy siting studies with hardcoded weights - candidates for the T4 tool sweep, not this T3 unit). MULTILINGUAL: Spanish/French/Portuguese grey searches (media luna / demi-lune / cordão de pedra) not separately executed - EN drylands corpus saturated for T3 but ES/FR Sahel + Latin-American semi-arid grey (INERA, Embrapa) likely adds region-specific drought-buffering evidence; run before closing grey. T3-vs-T4 BOUNDARY: several strong hits (De Winnaar, Karimi, the 2016 jclepro MCDA 243-cit) are siting/suitability-leaning (T4) - flagged picos_ok but should be co-tagged for the T4 sweep to read-once. HAZARD-TO-STRUCTURE side (siltation, extreme-flood damage, bund-failure/overtopping) is thin - only Schiettecatte + FAO manual overflow-provision touch it; a targeted search on 'water harvesting structure failure / siltation / overtopping' is recommended to populate the asset-risk half of T3.
