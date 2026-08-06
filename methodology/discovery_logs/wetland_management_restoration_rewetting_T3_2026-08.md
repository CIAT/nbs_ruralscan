# Discovery log — Wetland Management · restoration_rewetting · T3

- Run `wetland_management_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.2 · nbs_id `wetland_management`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 666 | 42 | 5 |
| updated_lit | 54 | 40 | 6 |
| grey | 32 | 32 | 5 |
| tool | 8 | 8 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search runs (sort=cited_by_count:desc): (1) "wetland restoration flood" [count 50]; (2) "wetland restoration water storage" [count 1]; (3) "wetland rewetting" [count 47]; (4) "floodplain restoration" [count 568]`
- **updated_lit:** `OpenAlex title.search, filter from_publication_date:2015-01-01, sort=cited_by_count:desc: (1) "wetland restoration flood" [19]; (2) "wetland restoration drought" [3]; (3) "floodplain restoration flood" [24]; (4) "wetland restoration nutrient retention" [0]; (5) "wetland restoration prioritization" [8]`
- **grey:** `WebSearch EN: 'wetland restoration rewetting flood attenuation water storage guidance Ramsar IWMI FAO drought'; ES: 'restauración humedales rewetting regulación inundaciones sequía almacenamiento agua guía técnica'; FR/PT: 'restauration zones humides réhumidification régulation crues sécheresse; restauração zonas húmidas reidratação inundações seca'`
- **tool:** `GitHub API: 'wetland restoration suitability GIS' [0]; 'wetland MCDA OR wetland siting OR floodplain restoration model' [4]; 'global surface water wetland mapping' [0]. WebSearch: 'wetland restoration site suitability GIS multi-criteria toolbox open source github flood water storage'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `upper_mississippi_flood_reduction_1995` | stock | paywalled | ok | high | Flood Reduction through Wetland Restoration: The Upper Mississippi River Basin as a Case History — Seminal (178c, is_seminal) quantified flood-attenuation-via-restoration case; direct T3 flood-respons |
| `synoptic_prioritize_flood_attenuation_2000` | stock | paywalled | ok | high | A synoptic assessment for prioritizing wetland restoration efforts to optimize flood attenuation — Siting + flood-attenuation objective = T3 response feeding M1/M4 targeting. Closed -> queue. |
| `flood_pulse_advantage_river_floodplain_1991` | stock | paywalled | ok | med | The flood pulse advantage and the restoration of river-floodplain systems — Foundational floodplain-reconnection concept (355c, seminal); conceptual basis for reconnection-driven attenuation, less qua |
| `restoration_strategies_lowland_floodplains_europe_2002` | stock | repo | ok | med | Restoration strategies for river floodplains along large lowland rivers in Europe — Green OA. Floodplain reconnection strategy; hydrological/flood context, temperate. Accepted per temperate-baseline t |
| `wetland_restoration_flood_pulsing_disturbance_1999` | stock | paywalled | ok | med | Wetland Restoration, Flood Pulsing, and Disturbance Dynamics — High-cite (283c) but flood-pulse ecology more than siting/response magnitude; borderline, kept as context. |
| `spatial_targeting_floodplain_equity_2020` | updated_lit | paywalled | ok | high | Spatial targeting of floodplain restoration to equitably mitigate flood risk — Siting + flood-risk mitigation + equity distribution (ties to M4/equity_inclusion). Closed -> queue. |
| `floodplain_restoration_flood_risk_lower_missouri_2015` | updated_lit | paywalled | ok | high | The Role of Floodplain Restoration in Mitigating Flood Risk, Lower Missouri River, USA — Quantified flood-risk-reduction from floodplain restoration. Closed -> queue. |
| `wetland_restoration_prioritizing_reduce_drought_2018` | updated_lit | paywalled | ok | high | Wetland restoration prioritizing, a tool to reduce negative effects of drought — Rare DROUGHT/dry-season water-security lens + prioritization/siting; key for that T3 sub-response. Closed -> queue. |
| `comparing_mcda_prioritize_wetland_sites_2017` | updated_lit | paywalled | ok | high | Comparing Two Multi-Criteria Methods for Prioritizing Wetland Restoration and Creation Sites — MCDA siting method (AHP-type) directly informs our MCDA engine + variable weighting. Closed -> queue. |
| `floodplain_stage0_flood_attenuation_2022` | updated_lit | paywalled | ok | high | Impact of floodplain and Stage 0 stream restoration on flood attenuation and floodplain expansion — Hybrid OA. Measured flood-attenuation + reconnection response. Verify OA copy; if not free -> queue. |
| `sediment_nutrient_trapping_mississippi_floodplain_2015` | updated_lit | paywalled | ok | med | Sediment and nutrient trapping as a result of a temporary Mississippi River floodplain restoration — Covers the sediment/nutrient-buffering T3 sub-response (title-search for 'nutrient retention' retur |
| `framework_prioritize_restoration_from_cropland_2023` | updated_lit | paywalled | ok | med | A methodological framework for prioritizing wetland restoration from cropland: a case study — Rural/agricultural-land restoration targeting (China) = rural-scan relevant; siting method. Closed. Spare  |
| `iwmi_wetlands_hydrological_resilience_blog` | grey | oa | ok | med | Why wetlands must be central to building hydrological resilience - beyond protection (IWMI) — IWMI institutional framing: redefine restoration around hydrological function (soil-moisture, recharge, ET |
| `ramsar_bn10_restoration_climate_resilience` | grey | other | ok | high | Ramsar Briefing Note 10 - Wetland restoration for climate change resilience — Ramsar technical briefing, general wetland (not peat-only), flood/drought/hydrology framing. WebFetch got HTTP 403 (bot bl |
| `agua_mx_guia_restauracion_humedales` | grey | oa | ok | med | Guía metodológica para el desarrollo de iniciativas de restauración de humedales (agua.org.mx, Mexico) — LMIC (Mexico) practical restoration methodology: hydrological assessment, water sources, active |
| `andex_high_andes_wetland_rehydration_lowcost` | grey | oa | ok | high | Restauración de humedales altoandinos mediante rehidratación del paisaje: enfoque de bajo costo basado en satélites (ANDEX-RHP) — LMIC (Andes) low-cost landscape re-wetting/rehydration + satellite sit |
| `wetland_solutions_extreme_flood_drought_efficiency_2023` | grey | paywalled | ok | high | Wetland-based solutions against extreme flood and severe drought: efficiency evaluation of risk mitigation — Peer-reviewed (Climate Risk Management) surfaced via grey search - reclassify to lit on reg |

## Gaps / next iteration

DROUGHT / dry-season water-security response is thin: only 3 OpenAlex title hits ('wetland restoration drought'), essentially one usable source (W2781712938) — most restoration T3 evidence is flood-attenuation-heavy. Consider a soil-moisture/baseflow/groundwater-recharge query angle next sweep. SEDIMENT/NUTRIENT buffering had 0 title hits ('nutrient retention') — evidence is embedded inside floodplain-restoration papers (W1793877710), so a dedicated 'sediment/nutrient trapping wetland' query is warranted. LMIC coverage is weak in the peer-reviewed layer (dominated by US Mississippi/Missouri + European Danube temperate cases); tropical/agricultural-landscape restoration siting is under-represented — grey (agua.org.mx Mexico, ANDEX Andes) partly compensates but needs a targeted LMIC OpenAlex pass (Africa/SE-Asia floodplain wetlands). TOOL layer is empty: no registerable open-source code tool (top MCDA-siting repo is README-only; live tools are ArcGIS/GEE-dataset, not code-inspectable) — flag for Benson: JRC Global Surface Water + USACE WMTT/EMRRP are dataset/method leads to evaluate, not evidence sources. PEAT-FIRE and coastal/tidal responses deliberately parked (F3 / coastal parked); if F1 later absorbs any peat rewetting, re-run with Ramsar rtr11 + Global Peatlands Initiative.
