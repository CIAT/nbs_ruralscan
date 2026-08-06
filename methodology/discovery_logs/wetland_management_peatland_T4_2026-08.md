# Discovery log — Wetland Management · peatland · T4

- Run `wetland_management_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.2 · nbs_id `wetland_management`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 1447 | 15 | 3 |
| updated_lit | 387 | 15 | 4 |
| grey | 16 | 16 | 3 |
| tool | 16 | 16 | 4 |

### Verbatim search terms

- **stock:** `title.search:(peatland OR paludiculture OR peat) AND (restoration OR rewetting OR suitability) ; sort=cited_by_count:desc`
- **updated_lit:** `title.search:(peatland OR paludiculture) AND (rewetting OR restoration OR mapping OR water table) , from_publication_date:2015-01-01 ; sort=cited_by_count:desc`
- **grey:** `WebSearch EN: 'peatland restoration rewetting suitability mapping guidance tropical Global Peatlands Initiative FAO IUCN'; 'paludiculture site suitability GIS MCDA rewetting peat water table'. Institutions: Ramsar, FAO, IUCN, UNEP-WCMC/Global Peatlands Initiative, DEFRA lowland-peat`
- **tool:** `WebSearch/GitHub: 'tropical peatland depth extent map Indonesia Congo Peru GitHub random forest'; 'wetland restoration site suitability GIS multi-criteria index GitHub'. Platforms: GEE community catalog, Global Surface Water, CIFOR Global Wetlands, PEATMAP/Peat-ML`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `page_lowland_tropical_peat_se_asia_2008` | stock | oa | ok | high | Restoration Ecology of Lowland Tropical Peatlands in Southeast Asia: Current Knowledge and Future Research Directions — Tropical LMIC (SE Asia) F3 anchor. Practice explicit (peatland restoration). Hyd |
| `page_canal_blocking_kalimantan_2013` | stock | oa | ok | high | Canal blocking strategies for hydrological restoration of degraded tropical peatlands in Central Kalimantan, Indonesia — Directly siting/hydrology: where and how to rewet drained tropical peat (draina |
| `page_artificial_drainage_peatlands_restoration_2004` | stock | oa | ok | med | Artificial drainage of peatlands: hydrological and hydrochemical process and wetland restoration — Foundational review of drainage state -> hydrological process -> restoration. Supplies the drainage-h |
| `page_indonesian_peat_physical_critical_groundwater_2019` | updated_lit | oa | ok | high | Exploration of the importance of physical properties of Indonesian peatlands to assess critical groundwater table — Tropical LMIC. Critical groundwater-table depth threshold tied to peat physical prop |
| `page_wt_driven_ghg_national_restoration_2023` | updated_lit | oa | ok | high | Water-table-driven greenhouse gas emission estimates guide peatland restoration at national scale — National-scale restoration prioritisation from water-table depth -> exactly the T4 siting logic (WTD |
| `page_wt_peat_carbon_se_asia_plantations_2015` | updated_lit | oa | ok | med | Modeling relationships between water table depth and peat soil carbon loss in Southeast Asian plantations — Tropical SE Asia. WTD as the governing variable; drainage state gradient. Restoration-releva |
| `page_nl_paludiculture_crop_suitability_model` | updated_lit | paywalled | ok | high | Modeling crop suitability for rewetting landscapes in the Netherlands across present and future climate scenarios — Explicit paludiculture SITE-SUITABILITY model: water balance, soil texture, pH, wate |
| `page_ramsar_rtr11_peatland_rewetting_guidelines_2021` | grey | oa | ok | high | Global guidelines for peatland rewetting and restoration (Ramsar Technical Report No. 11) — Anchor guidance. Water-table targets, hydrological-unit / minimum-viable-site-size rules, drainage-reversal  |
| `page_fao_peatland_mapping_monitoring_2020` | grey | oa | ok | med | FAO Peatland mapping and monitoring: recommendations and technical overview — Method for mapping peat presence/extent (the F3 gating layer) with tropical cases (Indonesia, DRC, Peru). Feeds the peat-s |
| `page_defra_lp2_paludiculture_report_2020` | grey | oa | ok | med | Defra LP2 Paludiculture report (lowland peat, England) — Paludiculture water-table / site-selection criteria and crop-water-table matrices. Temperate; useful for the rewet-and-farm suitability variabl |
| `tool_gee_amazon_peatland_extent` | tool | repo | ok | high | Amazonian Peatland Extent (awesome-gee-community-catalog) — GEE-hosted (server-side preferred) peat-presence siting layer, tropical LMIC (Amazonia/Peru). Random-forest derived. Dataset not MCDA code - |
| `tool_peat_ml_global_extent` | tool | oa | ok | high | Peat-ML: global peatland extent map created using machine learning (GMD 2022) — Global peat fractional-coverage siting layer + published code/model. Supplies the peat-presence gate everywhere incl. Co |
| `tool_global_peat_thickness_carbon_essd2024` | tool | oa | ok | high | Mapping thickness and carbon stock of global peatlands (ESSD preprint 2024) — Peat DEPTH/thickness layer = the F3 depth limiter directly. Global gridded dataset (server-side candidate). Dataset, not p |
| `tool_cifor_global_wetlands_v3` | tool | repo | ok | med | CIFOR Global Wetlands V3 — Global wetland/peat extent platform (siting/masking layer). Confirm peat-class separability before use; overlaps Peat-ML. Platform, no extractable thresholds. |

## Gaps / next iteration

Coverage skew: OpenAlex peatland core is GHG-flux/carbon-dominated (T6), not T4 siting; usable T4 signal is the water-table-depth threshold literature + drainage-state/canal-blocking siting studies, which were screened out of the flux mass. TROPICAL PEAT LMIC tie-break is only partly met: SE Asia (Indonesia/Kalimantan) is well covered, but CONGO Basin (Cuvette Centrale) and PERU/Amazonia peat have restoration/siting evidence that is thin and mostly extent-mapping (peat presence) rather than rewetting-suitability thresholds -> a targeted Congo/Peru grey + WOCAT/WB-project sweep is still needed. TOOL process found peat presence/depth SITING LAYERS (GEE Amazon peat, Peat-ML, global peat-thickness ESSD, CIFOR) but NO purpose-built paludiculture/peatland GIS-MCDA repository with hardcoded suitability weights/thresholds -> no file:line/commit_sha parameter extraction possible this round; the parameterised-suitability logic must come from the NL model + Ramsar/DEFRA guidance instead. Paludiculture (rewet-and-farm) evidence is overwhelmingly temperate fen (NL/DE/UK); tropical paludiculture crop-suitability thresholds are a genuine gap. No dedicated non-English (ES/FR/PT) grey beyond FAO/GPI multilingual portals surfaced; a Peru (Spanish) / Congo (French) national-guidance search is outstanding. Distinguishing peat vs non-peat wetland classes in the global extent layers (F3 vs F1/F2 routing) needs a BIND-level fitness check before any layer is bound.
