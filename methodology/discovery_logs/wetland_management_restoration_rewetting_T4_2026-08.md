# Discovery log — Wetland Management · restoration_rewetting · T4

- Run `wetland_management_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.2 · nbs_id `wetland_management`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 4 | 4 | 2 |
| updated_lit | 17 | 10 | 3 |
| grey | 10 | 8 | 2 |
| tool | 9 | 6 | 2 |

### Verbatim search terms

- **stock:** `title.search: wetland restoration site selection OR wetland restoration suitability OR wetland siting OR wetland restoration prioritization ; sort=cited_by_count:desc`
- **updated_lit:** `title.search: wetland restoration suitability OR wetland rewetting OR wetland restoration siting OR floodplain restoration hydrology ; from_publication_date:2015-01-01 ; sort=cited_by_count:desc`
- **grey:** `WebSearch EN: 'Ramsar/FAO/IWMI/Wetlands International inland wetland restoration rewetting siting hydrology' + 'floodplain reconnection wetland restoration site prioritization GIS water table degraded wetland mapping'`
- **tool:** `WebSearch/GitHub: 'wetland restoration suitability MCDA GIS Google Earth Engine Global Surface Water siting repository' + github.com/topics/wetlands`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `combined_hydro_landscape_2005` | stock | paywalled | ok | high | A combined hydrologic simulation and landscape design model to prioritize sites for wetlands restoration — Seminal (35c) siting model; hydrologic-simulation + landscape design to prioritize restoratio |
| `mcda_two_methods_wetland_2017` | stock | paywalled | ok | high | Comparing Two Multi-Criteria Methods for Prioritizing Wetland Restoration and Creation Sites Based on Ecological criteria — MCDA site-prioritization for wetland restoration/creation — directly maps T4 |
| `riparian_restoration_nutrient_hydro_2021` | updated_lit | paywalled | ok | med | Hydroclimatic variability and riparian wetland restoration control the hydrology and nutrient fluxes in a lowland catchment — Riparian/floodplain wetland restoration + hydrology (water table, connecti |
| `watershed_restoration_targets_hydro_2022` | updated_lit | paywalled | ok | med | Setting Targets for Wetland Restoration to Mitigate Climate Change Effects on Watershed Hydrology — Watershed-scale restoration targeting driven by hydrology — relevant to F1 system_constraint (former |
| `water_table_methane_wetland_2022` | updated_lit | paywalled | ok | med | Impact of Water Table on Methane Emission Dynamics in Terrestrial Wetlands and Implications on Strategies for restoration — Water-table depth = the F1 hydrology limiter; quantifies water-table thresho |
| `ramganga_floodplain_prioritization_2020` | grey | oa | ok | high | Integrating Hydrological Connectivity in a Process-Response Framework for Restoration and Monitoring Prioritisation of Floodplain Wetlands in the Ramganga Basin, India — TOP F1 candidate. LMIC (India) |
| `epa_principles_wetland_restoration` | grey | oa | ok | med | Principles of Wetland Restoration (US EPA) — Agency guidance: hydrology + surrounding land-use as primary site-selection criteria, restore original hydrologic regime. Non-quantitative but authoritativ |
| `gis_riparian_siting_russell_1997` | grey | paywalled | ok | med | The Role of GIS in Selecting Sites for Riparian Restoration Based on Hydrology and Land Use — Early/near-seminal GIS siting on hydrology+land-use (wetness index thresholds). Riparian restoration = F1- |
| `wetland_hydro_gee` | tool | repo | ok | med | Wetland-Hydro-GEE — mapping wetland hydrological dynamics (giswqs) — GEE tool: inundation dynamics + TWI (topographic wetness index) for wetlands. Provides F1 hydrology limiter method (TWI/inundation  |
| `sanjiang_restoration_suitability_gis` | tool | oa | ok | med | Exploring Spatial Relationship between Restoration Suitability and Rivers for Sustainable Wetland Utilization (Sanjiang Plain) — GIS wetland restoration suitability quantified vs stream order + buffer |

## Gaps / next iteration

1) OpenAlex title.search AND-semantics severely narrows real counts (stock=4, updated_lit=17); a full-text/abstract or inverted-index pass would recover more F1 siting studies missed by title-only. 2) Multilingual grey (ES/FR/PT) NOT run this cycle — EN saturated fast but LMIC Latin America (Pantanal/varzea floodplain restoration), Francophone W.Africa (inland valley bas-fonds), and Lusophone sources are unscreened; flag for next pass. 3) FAO/IWMI/Wetlands-International produced no F1-specific siting manual in EN search — most institutional grey is peatland (routed F3) or coastal (parked); inland-wetland rewetting siting guidance is thin. 4) Tool provenance not pinned — wetland_hydro_gee + sanjiang need commit-sha + file:line interrogation to confirm hardcoded TWI/water-table thresholds are a real restoration code branch (PICOS: mapping tool vs siting ruleset). 5) Strong overlap risk with F2 (permeability) and F3 (peat) — several 'wetland restoration' hits are peat/coastal; F1 corpus is smaller than expected and leans on floodplain-reconnection + riparian literature. 6) Most high-value siting/MCDA sources are paywalled (6 in acquisition_queue) — F1 extraction is blocked on Namita-J acquisition; only Ramganga (OA), EPA guidance, and Sanjiang (OA) are immediately extractable.
