# Discovery log — Wetland Management · peatland · T3

- Run `wetland_management_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.2 · nbs_id `wetland_management`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 2060 | 30 | 4 |
| updated_lit | 1278 | 27 | 6 |
| grey | 18 | 18 | 4 |
| tool | 16 | 16 | 2 |

### Verbatim search terms

- **stock:** `title.search:(peatland OR peat OR paludiculture OR mire OR bog OR fen) AND (restoration OR rewetting) [sort cited_by_count desc]; secondary title.search:(peatland OR paludiculture OR peat) AND (rewetting OR restoration) AND (fire OR flood OR water OR drought)`
- **updated_lit:** `title.search:(peatland OR paludiculture OR peat) AND (rewetting OR restoration),from_publication_date:2015-01-01 [sort cited_by_count desc]; secondary title.search:paludiculture [sort cited_by_count desc]`
- **grey:** `WebSearch EN: 'peatland rewetting restoration flood water storage fire risk reduction guidance Ramsar FAO Global Peatlands Initiative'; 'tropical peatland restoration rewetting Indonesia fire prevention water table siting guidelines Wetlands International IWMI'`
- **tool:** `WebSearch: 'GitHub peatland restoration prioritization suitability rewetting Google Earth Engine water table script'; 'GitHub wetland suitability GIS MCDA site selection model OR peatland depth mapping tool code repository'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `tuittila_tropical_seasia_restoration_2008` | stock | repo | ok | high | Restoration Ecology of Lowland Tropical Peatlands in Southeast Asia: Current Knowledge and Future Research Directions — Green OA. Tropical LMIC (SE Asia) peatland restoration foundations incl. hydrolo |
| `ritzema_canal_blocking_kalimantan_2013` | stock | repo | ok | high | Canal blocking strategies for hydrological restoration of degraded tropical peatlands in Central Kalimantan, Indonesia — Green OA. Direct T3 practice: rewetting via canal-blocking -> water-table recov |
| `holden_artificial_drainage_peatlands_2004` | stock | repo | ok | high | Artificial drainage of peatlands: hydrological and hydrochemical process and wetland restoration — Bronze OA (562 cites). Seminal on peat drainage->hydrology + restoration; underpins water-storage/flo |
| `jauhiainen_tropical_peat_hydro_restoration_2008` | stock | paywalled | ok | med | Carbon dioxide and methane fluxes in drained tropical peat before and after hydrological restoration — Closed access. Tropical hydrological restoration (water-table) evidence; primary framing is GHG ( |
| `dohong_tropical_restoration_techniques_review_2018` | updated_lit | paywalled | ok | high | A Review of Techniques for Effective Tropical Peatland Restoration — Closed access (129 cites). Comprehensive tropical-peat restoration technique review (rewetting, canal blocking, revegetation) - dir |
| `giesen_paludiculture_indonesia_progress_2020` | updated_lit | oa | ok | high | Progress of paludiculture projects in supporting peatland ecosystem restoration in Indonesia — Gold OA. LMIC paludiculture (farm-wet) linked to rewetting/restoration; dry-season water + fire-risk rele |
| `harrison_seasia_peat_strategies_2021` | updated_lit | paywalled | ok | high | Degradation of Southeast Asian tropical peatlands and integrated strategies for their better management and restoration — Closed access (J Applied Ecology, 108 cites). Integrated management/restoratio |
| `tan_paludiculture_tropical_review_2020` | updated_lit | paywalled | ok | high | Paludiculture as a sustainable land use alternative for tropical peatlands: A review — Closed access. Tropical paludiculture review — wet-farming siting/species + water-table maintenance. -> acquisiti |
| `budiman_lowdrainage_paludiculture_indonesia_2020` | updated_lit | repo | ok | med | Towards better use of Indonesian peatlands with paludiculture and low-drainage food crops — Hybrid OA. LMIC low-drainage/paludiculture + water-table management; dry-season water security angle. |
| `kiely_fire_smoke_health_peat_restoration_2019` | updated_lit | oa | ok | med | Fires, Smoke Exposure, and Public Health: An Integrative Framework to Maximize Health Benefits From Peatland Restoration — Gold OA. Peat-fire risk reduction via restoration + public-health co-benefit  |
| `vanderschaaf_typha_paludiculture_waterquality_2018` | stock | repo | ok | med | Typha latifolia paludiculture effectively improves water quality and reduces greenhouse gas emissions in rewetted peatlands — Bronze OA. Paludiculture + water-quality (nutrient/sediment buffering) in  |
| `unep_global_peatlands_assessment_2022` | grey | oa | ok | high | Global Peatlands Assessment: The State of the World's Peatlands (UNEP/Global Peatlands Initiative) — Hybrid OA / GPI flagship. Global authoritative context on drained-peat hazards (fire, flood, subsid |
| `ramsar_tr11_rewetting_restoration_guidelines_2021` | grey | oa | ok | high | Ramsar Technical Report 11: Global guidelines for peatland rewetting and restoration — OA PDF. Flagship guidance — explicit methodology for rewetting to reduce fire hazard + identify fire-prone areas, |
| `fao_peatland_restoration_monitoring_guidance` | grey | oa | ok | med | Practical guidance for peatland restoration monitoring (FAO) — OA PDF (FAO). Monitoring of groundwater level/soil moisture for peat restoration + disaster-risk (fire/flood) — supports T3 indicator sel |
| `wetlands_intl_mega_rice_canal_blocking` | grey | oa | ok | med | Wetlands International — Mega Rice Project (Block A) canal-blocking / rewetting & community fire brigades, Central Kalimantan — LMIC field-practice case: canal-blocking rewetting to stop drainage/oxid |

## Gaps / next iteration

1) TOOL process is the weakest: no purpose-built peatland-restoration-SITING or rewetting-prioritisation repo surfaced. Only generic wetland-mapping tools (wetlandmapR, wetland_id) with NO explicit F3 practice branch — flagged picos_ok=false. A dedicated tool sweep of GEE community scripts (Global Surface Water / GIEMS water-table, canal-block hydrology) + the BRG/BRGM Indonesia restoration-monitoring stack + code behind the national water-table-driven GHG prioritisation (BG 2023, W4381733917) is still owed. 2) Grey lit run EN-only; ES/FR/PT title searches not separately executed — acceptable for a SE-Asia/Congo peat family (EN + Indonesian dominant) but Congo-basin (French) tropical-peat grey lit (CongoPeat, potential) is under-sampled — a real geographic gap for the F3 LMIC tie-break. 3) T3 signal is partly entangled with T6 (GHG-mitigation) in the high-cite literature; many top sources frame rewetting as climate mitigation, so flood-attenuation / dry-season water-security / sediment-nutrient-buffering evidence is thinner and will need targeted extraction rather than more discovery. 4) 4 screened-in sources are paywalled -> acquisition_queue (Namita-J) before any extraction. 5) Sediment/nutrient buffering sub-function has only one direct candidate (Typha paludiculture) — under-covered; consider a targeted follow-up if T3 buffering rows come up short.
