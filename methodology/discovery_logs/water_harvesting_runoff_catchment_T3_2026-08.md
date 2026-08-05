# Discovery log — Water Harvesting & Conservation · runoff_catchment · T3

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 78 | 15 | 4 |
| updated_lit | 22 | 15 | 4 |
| grey | 14 | 14 | 5 |
| tool | 12 | 12 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: ("check dam" OR "farm pond" OR "percolation tank") AND (runoff OR recharge) ; sort=cited_by_count:desc; per_page=15`
- **updated_lit:** `OpenAlex title.search: ("sand dam" OR "gully plug" OR "nala bund" OR "recharge dam") AND (runoff OR drought OR recharge) ; from_publication_date:2015-01-01; sort=cited_by_count:desc; per_page=15`
- **grey:** `WebSearch #1: 'FAO WOCAT ICRISAT check dam farm pond percolation tank siting suitability drought recharge manual SWC drylands' ; WebSearch #2: 'sand dam manual site selection drainage line stream order suitability Africa Kenya RAIN Excellent development guidelines'`
- **tool:** `WebSearch: 'GitHub water harvesting site suitability GIS MCDA check dam farm pond runoff potential model Google Earth Engine' ; 'GitHub rainwater harvesting suitability tool RWH-SAT SCS-CN runoff drainage stream order recharge structure siting python' ; WebFetch github.com/AliSafari-IT/AquaFlow`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `percolation_tanks_mar_south_india_2014` | stock | paywalled | ok | high | Managed aquifer recharge in South India: What to expect from small percolation tanks — Percolation tank = ex-situ macro-catchment recharge structure, explicit. T3 drought/recharge-buffering lens (quan |
| `checkdam_recharge_sedimentation_ephemeral_2017` | stock | oa | ok | high | The Impact of a Check Dam on Groundwater Recharge and Sedimentation in an Ephemeral Stream — Check dam on ephemeral (drainage-line) stream - both T3 lenses in one: recharge/drought buffering AND sedim |
| `checkdam_runoff_sediment_semiarid_2014` | stock | paywalled | ok | med | Effect of check dams on runoff, sediment yield, and retention on small semiarid watershed — Semiarid check-dam runoff+sediment retention = soil-erosion hazard buffering + siltation. Borderline (leans  |
| `checkdams_runoff_sediment_loess_2019` | stock | paywalled | ok | med | Land-use changes and check dams reducing runoff and sediment yield on the Loess Plateau — Highest-cited (226). Check-dam runoff+sediment reduction = erosion-hazard/siltation. Risk: pure runoff/sedimen |
| `siltation_recharge_dams_remote_sensing_2020` | updated_lit | oa | ok | high | Mapping and accuracy assessment of siltation of recharge dams using remote sensing — Recharge dam (macro-catchment structure) siltation = hazard-TO-structure / failure-risk lens, directly T3. OA (Scie |
| `sand_dams_water_security_drought_resilience_2024` | updated_lit | oa | ok | high | Assessing sand dams for contributions to local water security and drought resilience — Sand dam = macro-catchment ex-situ storage on drainage line, explicit. T3 drought-resilience/water-security buffe |
| `conjunctive_sanddam_well_drought_2022` | updated_lit | oa | ok | high | Conjunctive Operation of Sand Dam and Groundwater Well for Reliable Water Supply during Drought — Sand dam drought-period reliability (supplemental supply / moisture security). T3 drought-buffering. O |
| `recharge_dam_performance_arid_satellite_2023` | updated_lit | paywalled | ok | med | Assessment of recharge dam performance in arid regions based on satellite data — Recharge-dam performance/siltation in arid regions - hazard-to-structure + recharge function. Paywalled -> queue. 0 cit |
| `sand_dam_manual_samsamwater` | grey | oa | ok | high | Sand Dam Manual (site selection: drainage line, stream order, riverbed width <25m, lithology) — Practitioner manual, explicit sand-dam siting on drainage lines (limiter = geomorphology). T3 relevance  |
| `sand_dam_manual_ethiopia` | grey | oa | ok | high | Manual on Sand Dams in Ethiopia — Ethiopia dryland sand-dam siting + drought-security manual. GREY positive-bias discount. LMIC context tie-break. Cache PDF + locators. |
| `kenya_practice_manual_small_dams_pans` | grey | oa | ok | med | Practice Manual for Small Dams, Pans and Other Water Conservation Structures in Kenya — Kenya govt (authority) manual - small dams/pans/check dams siting + drought-supply + failure/spillway. Multiple  |
| `fao_small_earth_dams_idp64` | grey | oa | ok | med | FAO Irrigation & Drainage Paper 64: Manual on small earth dams — FAO authority manual - small earth dam siting (catchment/runoff, siltation, spillway/failure). Overlaps water-storage-structure siting. |
| `sanddam_siting_guidelines_kenya_2020` | grey | repo | ok | high | Back to the drawing board: assessing siting guidelines for sand dams in Kenya — Critically assesses sand-dam siting criteria (AEZ, stream order influence on performance/failure) - directly the runoff- |

## Gaps / next iteration

TOOL PROCESS IS A GENUINE GAP: no open-source repo hardcodes macro-catchment WH-structure siting criteria (check dam/farm pond/percolation tank/sand dam) as a pinnable code branch. The field's operational logic lives in published GIS-MCDA/SCS-CN AHP weight matrices (stream order, drainage density, CN, slope, soil) embedded in papers, not in commit-sha/file:line-addressable code - so the 'tools are sources' extraction path has no target for this family. Recommend flagging to team: either (a) treat a representative AHP weight table as a tool-adjacent claim, or (b) accept no tool row and rely on stock/lit/grey. CONTENT GAPS: (1) hazard-TO-structure quantification is thin outside MENA recharge-dam siltation studies - little on extreme-flood damage/failure return-periods for farm ponds/check dams in Sahel/India. (2) Farm pond drought-buffering (supplemental irrigation) under-represented vs check/sand dams in the high-cite set; a targeted farm-pond+supplemental-irrigation query would help. (3) Spanish/French/Portuguese grey (Latin America olla/jaguey, Sahel Francophone) surfaced nothing for macro-catchment structures - may need AGROVOC-synonym title-only retry. (4) Grey manuals dominate - apply grey positive-bias discount to all benefit claims (drought/recharge overstated, failure/siltation under-reported).
