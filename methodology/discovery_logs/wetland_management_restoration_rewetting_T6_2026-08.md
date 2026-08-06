# Discovery log — Wetland Management · restoration_rewetting · T6

- Run `wetland_management_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.2 · nbs_id `wetland_management`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 3164 | 15 | 3 |
| updated_lit | 1580 | 16 | 3 |
| grey | 16 | 16 | 3 |
| tool | 6 | 6 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search:"wetland restoration" ; sort=cited_by_count:desc ; per_page=15 (curl). Boolean pilot title.search:(wetland restoration OR wetland rewetting OR floodplain restoration OR wetland reconnection) also run (count=18, mostly coastal/estuarine -> parked).`
- **updated_lit:** `OpenAlex title.search:"wetland restoration",from_publication_date:2015-01-01 ; sort=cited_by_count:desc ; per_page=15 (curl). + targeted WebSearch for LMIC floodplain-reconnection prioritisation (OpenAlex rewetting/paludiculture/peatland query returned HTTP-402 daily-budget-exceeded; that query is F3 peat-scope, excluded here).`
- **grey:** `WebSearch EN: "wetland restoration rewetting cost per hectare carbon water quality Ramsar FAO IUCN Wetlands International guidance" ; "floodplain wetland restoration reconnection developing countries site selection prioritization hydrology water table IWMI FAO manual". (ES/FR/PT title variants not separately run due to OpenAlex budget cap; EN grey saturated on cost/target figures.)`
- **tool:** `WebSearch: "wetland suitability siting GIS MCDA GitHub OR Google Earth Engine drainage rewetting floodplain restoration tool" ; GitHub topic:wetlands ; inspected github.com/NASA-DEVELOP/WET (GEE wetland-extent, TWI + Sentinel-1/L8).`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `jenkins_2010_mav_ecosystem_service_value` | stock | oa | ok | high | Valuing ecosystem services from wetlands restoration in the Mississippi Alluvial Valley — T6 cost + ES value ($/ha C sequestration, N mitigation, waterfowl) for freshwater floodplain restoration. Stro |
| `meli_2014_restoration_enhances_wetland_biodiversity_es` | stock | oa | ok | high | Restoration Enhances Wetland Biodiversity and Ecosystem Service Supply, but Results Are Context-Dependent — Meta-analysis of restoration outcomes -> T6 biodiversity/habitat + ES supply, with context-d |
| `erwin_2009_wetland_restoration_climate_change` | stock | paywalled | ok | med | Wetlands and global climate change: the role of wetland restoration in a changing world — Seminal (1303 cites) restoration-in-climate-context review; T6 carbon/regulation framing. Paywalled -> queue. |
| `cost_effectiveness_wetland_restoration_2020` | updated_lit | oa | ok | high | Climate change mitigation potential of wetlands and the cost-effectiveness of their restoration — Directly T6: carbon mitigation potential + cost-effectiveness ($/tCO2e) of wetland restoration. 198 ci |
| `cheng_2020_us_nitrate_removal_wetland_restoration` | updated_lit | paywalled | ok | high | Maximizing US nitrate removal through wetland protection and restoration — T6 water quality (N removal) + spatial prioritisation/siting of restoration. 255 cites. Nature paywall -> acquisition_queue. |
| `ramganga_2020_floodplain_wetland_restoration_prioritisation` | updated_lit | oa | ok | high | Integrating Hydrological Connectivity in a Process-Response Framework for Restoration and Monitoring Prioritisation of Floodplain Wetlands in the Ramganga Basin, India — LMIC (India) floodplain-wetlan |
| `balancing_2022_floodplain_reconnection_wetland_restoration` | updated_lit | paywalled | ok | med | Balancing multiple stakeholder objectives for floodplain reconnection and wetland restoration — Floodplain reconnection (F1) multi-objective trade-offs -> T6 outcomes + operational conditionality. Pay |
| `ramsar_global_wetland_outlook` | grey | other | ok | high | Ramsar Global Wetland Outlook (restoration cost band + targets) — T6 cost band $1,000->70,000/ha/yr restoration; authoritative Ramsar. Grey positive-bias/cost-range caveat applies. Snapshot needed at  |
| `fao_wetland_characterisation_ag_development` | grey | oa | ok | med | Wetland characterization and classification for sustainable agricultural development (FAO) — FAO framing of ag-wetlands + hydrology classes -> system/operational-constraint context + LMIC. Web source: |
| `european_wetland_restoration_costs_es` | grey | repo | ok | med | Restoration is an investment: comparing restoration costs and ecosystem services in selected European wetlands — T6 cost/ha + ES comparison across 100 restoration projects. Temperate (transferability  |

## Gaps / next iteration

1) OpenAlex daily budget exhausted after stock+lit queries (HTTP-402); the failed rewetting/paludiculture/peatland query is F3 peat-scope and excluded here anyway, so F1 coverage is intact — but a follow-up OpenAlex pass tomorrow for non-coastal freshwater/inland marsh restoration cost figures would deepen T6. 2) ES/FR/PT grey-lit variants were NOT run separately (budget); EN grey saturated on cost bands/targets but LMIC-language sources (Latin America floodplain, Congo-basin swamp, francophone West Africa) remain under-searched. 3) TOOL process is thin: no restoration-SITING tool with hardcoded siting/rewetting logic exists in the wild — WET is extent-mapping (PICOS-fail as practice tool), G-MCDA is NbS-agnostic. F1 'former/degraded wetland extent' limiter is better served by platforms (JRC Global Surface Water occurrence, GIEMS inundation) as BIND datasets, not as evidenced 'tools'. 4) Coastal/tidal restoration dominates the high-cite literature (parked) — inland/freshwater F1 signal is diluted; targeted title.search excluding coastal terms recommended next pass. 5) Cost figures gathered are temperate/US/EU-heavy; LMIC per-ha restoration cost evidence is a genuine gap for the D591 pilot context."}
