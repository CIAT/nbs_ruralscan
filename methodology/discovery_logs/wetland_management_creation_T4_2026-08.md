# Discovery log — Wetland Management · creation · T4

- Run `wetland_management_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.2 · nbs_id `wetland_management`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 63 | 15 | 3 |
| updated_lit | 5 | 5 | 1 |
| grey | 18 | 12 | 4 |
| tool | 2 | 2 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: ("wetland creation" OR "created wetland" OR "wetland reconstruction" OR "farm wetland") AND (suitability OR siting OR hydrology OR restoration); sort=cited_by_count:desc; per_page=15`
- **updated_lit:** `OpenAlex title.search: ("wetland creation" OR "created wetland" OR "farm wetland") AND (siting OR suitability OR GIS OR location); filter from_publication_date:2015-01-01; sort=cited_by_count:desc`
- **grey:** `WebSearch EN: 'wetland creation site selection suitability GIS hydrology depression terrain farm wetland siting guidance'; 'Ramsar OR IWMI OR "Wetlands International" wetland creation reconstruction siting suitability landscape water storage guidance'; 'FAO OR "Global Peatlands Initiative" wetland creation restoration siting hydrology peat depth mapping guidance'`
- **tool:** `WebSearch/GitHub: 'github wetland suitability GIS MCDA "Global Surface Water" depression topographic wetness index site selection python'; GitHub API repos uva-hydroinformatics/wetland_id, NASA-DEVELOP/WET`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `oa_lidardem_wetland_creation_suitability_2018` | stock | oa | ok | high | Identifying Feasible Locations for Wetland Creation or Restoration in Catchments by Suitability Modelling Using LiDAR DEM — MDPI Water, gold OA. Core T4: LiDAR-DEM depression/low-lying terrain + TWI + |
| `oa_mcda_catchment_wetland_suitability_2017` | stock | oa | ok | high | A multi-criteria, ecosystem-service value method used to assess catchment suitability for potential wetland restoration — Ecological Indicators, gold OA. GIS-MCDA catchment suitability for wetland sit |
| `oa_semiarid_created_wetland_water_quality_2007` | stock | other | ok | med | Creating wetlands for the improvement of water quality and landscape restoration in semi-arid zones degraded by agriculture — Explicit wetland CREATION on degraded agricultural land (semi-arid, nutrie |
| `oa_instream_wetland_creation_suitability_2025` | updated_lit | oa | ok | med | Finding suitable locations for in-stream wetland creation/restoration: comparing suitability analysis with macro... — EGU 2025 - abstract only (egusphere conference), no full paper yet. Recent creatio |
| `grey_sepa_constructed_farm_wetland_manual` | grey | oa | ok | high | Constructed Farm Wetlands (CFW) - Design Manual for Scotland (SEPA) — Explicit farm-wetland siting guidance: gently sloping land, hydrology, soils, drainage, archaeology screens. Landscape-siting (nut |
| `grey_mn_bwsr_wetland_restoration_guide` | grey | oa | ok | med | Wetland Restoration Guide - Engineering (Minnesota BWSR) — Site-suitability by geology/soils/topography/hydrology/drainage-history/land-ownership; low-lying depression/floodplain preference. Restorati |
| `grey_ramsar_tr11_peatland_rewetting` | grey | oa | ok | med | Global guidelines for peatland rewetting and restoration (Ramsar Technical Report 11) — F3 peat: hydrological-unit completeness (peat domes/sub-domes) + water-table as siting/feasibility gate; peat pr |
| `grey_fao_peatland_mitigation_guidance` | grey | oa | ok | med | Peatlands - guidance for climate change mitigation through conservation, rehabilitation and sustainable use (FAO) — Peat depth (5m polar to >15m tropical), mapping/boundary delineation, drainage state |

## Gaps / next iteration

Recent peer-reviewed CREATION-scoped siting literature is thin (updated_lit real meta.count=5); the large 'constructed wetland' corpus (count=44) is dominated by WASH/treatment-engineering, excluded per PICOS. Strongest T4-siting signal is grey (SEPA farm-wetland manual, MN BWSR) + two gold-OA GIS-MCDA papers - but both peer-reviewed hits are temperate (US/EU); LMIC/tropical creation-siting evidence for F2 is a gap. F3 tropical-peat (SE Asia/Congo) is covered only by rewetting/restoration guidance (Ramsar TR11, FAO), not de-novo creation - and peat-depth/hydrology-unit thresholds there are qualitative. ES/FR/PT title-only grey searches were not separately executed (flag for follow-up). No code-branch tool is genuinely 'wetland creation'; wetland_id/WET map extent from terrain indices (relevant as F2 depression/TWI + F1 former-wetland engines, PICOS-marginal). Global Surface Water & GIEMS/inundation datasets are BIND candidates (inundation-regime / water-availability layers) but were not surfaced as extractable sources this pass.
