# Discovery log — Wetland Management · creation · T3

- Run `wetland_management_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.2 · nbs_id `wetland_management`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 1128 | 40 | 5 |
| updated_lit | 16 | 16 | 4 |
| grey | 15 | 15 | 4 |
| tool | 13 | 13 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search (sort cited_by_count desc): "constructed wetland" | "created wetland" | "wetland creation" | "farm wetland" | "peatland rewetting fire"`
- **updated_lit:** `OpenAlex title.search from_publication_date:2015-01-01: 'created restored wetland nitrogen phosphorus' / 'wetland flood storage' / 'peatland rewetting' -> 429 RATE-LIMIT (daily budget exhausted) -> WebSearch fallback: 'wetland creation agricultural landscape flood water storage siting 2020..2026'; 'created wetland catchment nutrient retention farm reservoir dry season water security'; 'tropical peatland rewetting fire risk reduction Indonesia Congo'`
- **grey:** `WebSearch: 'Ramsar OR Wetlands International OR FAO guidance wetland creation restoration flood water storage rural'; 'Global Peatlands Initiative peatland rewetting fire assessment guidance report'`
- **tool:** `WebSearch: 'wetland suitability mapping GIS MCDA AHP site selection GitHub Google Earth Engine'; 'Global Surface Water Explorer GIEMS wetland siting depression mapping tool github'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `created_restored_wetland_np_removal_2016` | stock | oa | ok | high | How effective are created or restored freshwater wetlands for nitrogen and phosphorus removal? — Practice explicit (created/restored freshwater wetlands). Directly quantifies nutrient (N/P) intercepti |
| `creating_riverine_wetlands_nutrient_pulsing_2005` | stock | paywalled | ok | med | Creating riverine wetlands: Ecological succession, nutrient retention, and pulsing effects — Wetland creation explicit; nutrient retention + hydrologic pulsing (flood attenuation) -> T3. Paywalled ->  |
| `wetland_creation_ag_landscapes_biodiv_2009` | stock | paywalled | ok | low | Wetland creation in agricultural landscapes: Biodiversity benefits on local and regional scales — Practice + rural-ag landscape explicit, but payload is biodiversity, not a T3 climate-hazard response  |
| `rewetting_peatland_fire_hazard_riau_2023` | stock | oa | ok | high | The Impact of Rewetting Peatland on Fire Hazard in Riau, Indonesia — F3 tropical-peat rewetting -> PEAT-FIRE risk reduction, exactly the T3 response. Indonesia (LMIC tropical-peat tie-break). Gold OA. |
| `fire_risk_groundwater_rewetting_peat_2020` | stock | oa | ok | high | Fire risk analysis based on groundwater level in rewetting peatland, Sungaitohor village — F3 peat: links groundwater-level target to fire risk (candidate threshold, e.g. water table depth) -> T3 peat |
| `ahlen_wetland_position_storage_flood_2022` | updated_lit | other | ok | high | Wetland position in the landscape: Impact on water storage and flood buffering — Landscape POSITION/siting -> water storage + flood buffering: direct T3 flood-attenuation/water-storage + the low-lying |
| `peatland_restoration_fire_cobenefits_indonesia_2022` | updated_lit | oa | ok | high | Peatland restoration as an affordable nature-based climate solution with fire reduction and conservation co-benefits in Indonesia — F3 peat rewetting/restoration with QUANTIFIED fire-risk reduction (6 |
| `tropical_peatland_restoration_reduces_fire_2026` | updated_lit | paywalled | ok | high | Tropical Peatland Restoration Reduces Fire Occurrence — Counterfactual evidence peat rewetting/restoration reduces fire occurrence -> T3 peat-fire. Recent (2026). AGU GRL likely paywalled -> acquisiti |
| `constructed_wetland_nutrient_watershed_scale_2024` | updated_lit | oa | ok | med | Implementing constructed wetlands for nutrient reduction at watershed scale: opportunity to link models and real-world execution — 'Constructed wetland' here is LANDSCAPE/watershed-siting sense (nutri |
| `ramsar_rtr11_peatland_rewetting_2021` | grey | oa | ok | high | Global guidelines for peatland rewetting and restoration (Ramsar Technical Report No. 11) — Authoritative F3 peat-rewetting practice guidance incl. water-table targets + fire prevention -> T3 peat-fir |
| `unep_gpi_global_peatlands_assessment_2022` | grey | oa | ok | med | Global Peatlands Assessment: The State of the World's Peatlands (UNEP/Global Peatlands Initiative) — Context + rewetting rationale + fire/emissions framing for F3. Broad assessment (context-heavy) ->  |
| `ramsar_wetland_restoration_principles` | grey | oa | ok | med | Principles and guidelines for wetland restoration (Ramsar) — General wetland creation/restoration principles incl. flood control, water supply, groundwater recharge -> T3 flood/water-storage framing ( |
| `water_conservation_zones_agri_catchments` | grey | oa | ok | med | Management and Area-wide Evaluation of Water Conservation Zones in Agricultural Catchments for Biomass Production, Water Quality and Food Security (IAEA/IWMI) — Farm/catchment water-conservation zones |

## Gaps / next iteration

STOCK/updated_lit skew: the freshwater-creation T3 evidence is dominated by TEMPERATE North-America/Europe (Mitsch lineage, tile-drained ag, Swedish landscapes) — LMIC non-peat F2 creation (e.g. African/S-Asian farm wetlands, valley-bottom dambos) is thin; the one LMIC-rainfed grey hit (IWMI water-conservation-zones) needs a targeted follow-up sweep. F3 tropical-peat is well covered for Indonesia (Riau/Kalimantan/Sumatra) but CONGO BASIN peat is a genuine hole (WebSearch returned no Congo-specific rewetting/fire source) — flag for a dedicated Congo/Cuvette-Centrale query next round. TOOL process is empty of true practice-thresholded sources: no GIS-MCDA tool hardcodes a wetland-creation siting branch; JRC-GSW/GIEMS/GLWD are DATA layers (route to BIND), so T3 'tool' evidence for this family is expected to stay nil — recommend closing the tool lane for wetland_creation__T3 rather than chasing it. OpenAlex daily budget was EXHAUSTED mid-run (HTTP 429) — updated_lit ran on WebSearch fallback only; a re-run after UTC reset would let updated_lit report real meta.count and pull recent DOIs/OA flags directly. ES/FR/PT title-search not executed for stock (budget) — Latin-American 'humedal construido/creado' and Francophone-Africa 'zone humide' literature under-sampled. Constructed-wetland/treatment-engineering pool (~14.7k) deliberately excluded per PICOS; if any WASH-adjacent nutrient-interception siting evidence is later wanted, it would need a separate scoped query.
