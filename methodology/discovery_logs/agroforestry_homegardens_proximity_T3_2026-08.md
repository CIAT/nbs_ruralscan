# Discovery log — Agroforestry · homegardens_proximity · T3

- Run `discovery_crossfam_homegardens_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 185 | 18 | 2 |
| updated_lit | 110 | 22 | 5 |
| grey | 24 | 24 | 1 |
| tool | 3 | 3 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search:"homegarden agroforestry" sort=cited_by_count:desc per_page=15 (TOTAL=137); + title.search:"home garden agroforestry" (TOTAL=48); + title.search:"Cuban home gardens social-ecological resilience" for the seminal resilience item`
- **updated_lit:** `OpenAlex title.search:"homegarden agroforestry",from_publication_date:2015-01-01 sort=cited_by_count:desc (TOTAL=89); + title.search:"homegarden climate" (TOTAL=21)`
- **grey:** `WebSearch EN: "home garden agroforestry drought climate resilience WOCAT FAO TECA smallholder"; WebSearch ES: "huerto casero agroforesteria sequia resiliencia climatica (jardin tropical) OR quintal agroflorestal clima"; WebSearch: "WOCAT OR ICRAF home garden homestead agroforestry drought flood buffer climate adaptation case study tropical"`
- **tool:** `WebSearch: "github home garden agroforestry suitability model tree crop proximity settlement distance script"; GitHub API: repos/saraheb3/AgroforestrySuitability_GEE (commit af338e8, tree + gee_app blob grep home garden|settlement|weight|practice)`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `buchmann_cuban_homegardens_resilience_2009` | stock | paywalled | ok | high | Cuban Home Gardens and Their Role in Social-Ecological Resilience — Seminal (155 cit). Home garden = explicit unit; frames gardens as buffers to hurricanes, drought and food-supply shocks -> core T3 h |
| `fernandes_nair_chagga_homegardens_kilimanjaro_1984` | stock | paywalled | ok | med | The Chagga homegardens: a multistoried agroforestry cropping system on Mt. Kilimanjaro — Seminal (176 cit). Multistrata homegarden explicit; buffering value is microclimate/canopy-strata (heat, moistu |
| `quandt_climate_resilience_index_homegardens_2024` | updated_lit | oa | ok | high | Climate resilience index for assessing resilience in homegardens — Directly T3: constructs a resilience index specifically for homegardens against climate stress. Hybrid OA. Strong methodological tran |
| `mattsson_homegarden_climate_variability_southasia_2018` | updated_lit | oa | ok | high | Climate variability and adaptation of Homegardens in South Asia: case studies from Sri Lanka, Bangladesh and India — Directly T3, multi-country LMIC (Sri Lanka/Bangladesh/India). Homegarden adaptation |
| `ethiopian_rift_valley_homegarden_adaptation_2023` | updated_lit | oa | ok | high | Smallholder Farmers' Climate Change Adaptation Strategies in the Ethiopian Rift Valley: The Case of Home Gardens — Home garden = explicit adaptation unit; drought/rainfall-variability response in a dr |
| `microclimate_regulation_rural_homegarden_2019` | updated_lit | paywalled | ok | high | Microclimate regulation efficiency of the rural homegarden agroforestry system in the West ... — Directly T3: quantifies homegarden buffering of heat/microclimate (temperature/humidity moderation) ->  |
| `boloso_sore_homegarden_climate_adaptation_2025` | updated_lit | oa | ok | med | Contribution of homegarden agroforestry to adaptation strategy of climate change in Boloso Sore Woreda, Wolaita zone, South Ethiopia — Recent LMIC homegarden climate-adaptation case; likely perception |
| `fao_agroforestry_drylands_climate_resilience_scaling` | grey | oa | NO | low | Scaling Agroforestry as a Climate Resilience and Food Security Solution in Drylands of Kenya, Uganda, and Tanzania (FAO) — Institutional LMIC drylands context on agroforestry drought/erosion buffering |
| `saraheb3_agroforestry_suitability_gee_2025` | tool | repo | NO | low | AgroforestrySuitability_GEE Decision Support Tool (saraheb3) — PICOS FAIL: US-Midwest tool; practice enum {Alley Cropping, Riparian, Silvopasture, Windbreaks}, hardcoded ACweights=[5,5,3,2,5]; no home |

## Gaps / next iteration

Strongest evidence concentrates in updated_lit (5 OA/near-OA homegarden climate-adaptation studies) plus 2 seminal stock items. Key gaps: (1) GREY is thin for the specific practice - WebSearch surfaces only GENERIC agroforestry-for-drylands (FAO/CIFOR-ICRAF) where home-garden proximity is not the explicit unit; a direct WOCAT SLM-technologies DB query and a TECA query (not reachable via search snippets) are needed to find home-garden-specific documented technologies with hazard-response data. (2) No TOOL encodes homegarden climate-hazard response - the only agroforestry suitability tool found (saraheb3 GEE) is US-Midwest with no home-garden branch; homegardens_proximity has no computational hazard-response tool, so tool-derived T3 evidence is unavailable. (3) Geographic skew toward Ethiopia in recent literature; Indonesia/Kerala/Sri Lanka classic homegarden zones underrepresented in the T3-specific (as opposed to diversity/carbon) results - Mattsson 2018 partially fills South Asia. (4) Several high-value items paywalled (Cuban resilience, Chagga, microclimate regulation) - queued for CGIAR institutional retrieval before extraction. (5) Many high-cite homegarden papers are diversity/carbon-stock/structure studies off-scope for T3; T3 extraction should draw on the resilience/adaptation/microclimate subset, not the broader corpus.
