# Discovery log — Water Harvesting & Conservation · runoff_catchment · T6

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 98 | 40 | 5 |
| updated_lit | 794 | 60 | 5 |
| grey | 27 | 12 | 4 |
| tool | 18 | 10 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search (curl, sort=cited_by_count:desc): 'percolation tank recharge'; 'check dam groundwater recharge'; 'sand dam water'; 'farm pond irrigation yield'`
- **updated_lit:** `OpenAlex title.search + filter from_publication_date:2015-01-01, sort=cited_by_count:desc: 'check dam recharge'; 'farm pond'; 'water harvesting yield'; 'soil water conservation adoption'`
- **grey:** `WebSearch: 'WOCAT check dam percolation tank farm pond cost per structure groundwater recharge yield technology'; 'ICRISAT IWMI check dam farm pond percolation tank cost benefit groundwater recharge impact India report'; 'FAO water harvesting structures check dam cost per hectare ... récupération eau ruissellement' (EN+FR)`
- **tool:** `WebSearch: 'github water harvesting site selection GIS MCDA suitability check dam pond runoff model python earth engine repository'; 'github RWH runoff potential zone weighted overlay AHP tool code thresholds slope drainage stream order'; WebFetch github.com/topics/rainwater-harvesting`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| _(none)_ | | | | | |

## Gaps / next iteration

TOOL PROCESS EMPTY: no open-source macro-catchment siting tool with an inspectable code branch and hardcoded per-subpractice weights/thresholds found (RWH-MCDA is ArcGIS weighted-overlay in papers; GitHub topic only yields off-scope rooftop RainWise). Tool-derived T6 cost/threshold evidence not acquirable this pass. GREY primary figures uncached: the ICRISAT/WLE ₹/m3 impounded and returns-per-rupee (farm pond ₹1.80, recharge pit ₹1.78) and the 1-2.5 m GW-rise numbers are only in web summaries; primary ICRISAT/IWMI report must be located + cached before extraction. STRUCTURE SKEW: strong coverage of percolation tanks + check dams + sand dams (India/Ethiopia drylands); THIN on nala bunds, gully plugs, and explicit artificial-recharge/recharge-dam cost-per-m3 as standalone T6 units, and on Sahel/MENA + francophone/lusophone macro-catchment cost-effectiveness (grey EN-dominated despite FR query). COST-EFFECTIVENESS: cost-per-structure and cost-per-m3-stored mostly in grey (positive-bias discount needed); peer-reviewed cost-per-tCO2e / cost-per-beneficiary for these structures essentially absent. ADOPTION: structural-SWC adoption studies bundle terraces/bunds (in-situ family) with check dams -> must be split at extraction to keep only macro-catchment rows. MDPI 'Hydrologic and Cost-Benefit Analysis of Multiple Check Dams, Rajasthan' (mdpi.com/2073-4441/14/15/2378) surfaced but not yet screened into candidates -> follow-up.
