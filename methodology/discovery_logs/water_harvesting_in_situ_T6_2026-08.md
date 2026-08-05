# Discovery log — Water Harvesting & Conservation · in_situ · T6

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 342 | 15 | 5 |
| updated_lit | 261 | 15 | 3 |
| grey | 26 | 26 | 4 |
| tool | 9 | 9 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search:(zai OR tassa OR "tied ridges" OR "contour bunds" OR "soil and water conservation") AND (yield OR adoption) ; sort=cited_by_count:desc; per_page=15`
- **updated_lit:** `OpenAlex title.search:("in situ rainwater harvesting" OR "soil moisture conservation" OR "planting pits" OR "conservation tillage") AND (yield OR cost OR adoption), from_publication_date:2015-01-01 ; sort=cited_by_count:desc; per_page=15`
- **grey:** `WebSearch EN: 'zai planting pits tassa cost per hectare yield Sahel FAO WOCAT technology cost water harvesting' ; 'contour bunds tied ridges cost effectiveness yield adoption ICRISAT IWMI in-situ water harvesting semi-arid' ; FR: 'cordons pierreux demi-lunes rendement cout adoption Sahel conservation eaux et sols FAO CILSS'`
- **tool:** `WebSearch/WebFetch: 'GitHub rainwater harvesting suitability model runoff GIS MCDA site selection python google earth engine' ; 'github rainwater harvesting suitability AHP weights slope curve number python reclassify' ; github.com/topics/rainwater-harvesting`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `wocat_qcat_zai_tassa_niger` | grey | oa | ok | high | Zai or tassa planting pits [Niger] - WOCAT SLM Technologies database entry — Diamond source (WOCAT SLM DB, LMIC-grounded). In-situ planting pits explicit. Structured T6 cost tables: establishment/main |
| `nyamadzawo_contour_ridges_zimbabwe_2013` | stock | paywalled | ok | high | Assessing crop yield benefits from in situ rainwater harvesting through contour ridges in semi-arid Zimbabwe — In-situ contour ridges explicit, semi-arid Zimbabwe (LMIC dryland). T6 yield-gain outcome |
| `swc_yield_runoff_soilloss_ssa_meta_2018` | stock | paywalled | ok | high | Effects of soil and water conservation techniques on crop yield, runoff and soil loss in Sub-Saharan Africa — Meta-analysis, SSA drylands. Quantified T6 yield/runoff/soil-loss effect sizes across SWC  |
| `kassie_csa_adoption_drylands_2016` | stock | paywalled | ok | high | Advancing climate-smart-agriculture in developing drylands: Joint analysis of the adoption of multiple on-farm SWC technologies — Dryland (E. Africa) joint adoption analysis of multiple SWC practices  |
| `swc_adoption_impact_switching_ethiopia_2013` | stock | paywalled | ok | high | The Adoption and Impact of Soil and Water Conservation Technology: An Endogenous Switching Regression Application — Ethiopia. Adoption + causal yield/welfare impact via switching regression - core T6  |
| `swc_adoption_burkina_faso_2004` | stock | paywalled | ok | high | Farm-level adoption of soil and water conservation techniques in northern Burkina Faso — Sahel (Burkina) in-situ SWC adoption determinants - T6 adoption. Seminal (2004, 217 cites), LMIC tie-break. Ag  |
| `tied_ridge_furrow_meta_asia_africa` | updated_lit | oa | ok | high | Influence of tied-ridge-furrow with inorganic fertilizer on grain yield across semiarid regions of Asia and Africa: A meta-analysis — OA (PMC). In-situ tied-ridge explicit, semi-arid Asia+Africa dryla |
| `conservation_tillage_maize_global_meta_2022` | updated_lit | paywalled | ok | med | Conservation tillage or plastic film mulching? A comprehensive global meta-analysis based on maize yield — Global meta-analysis, conservation tillage as in-situ moisture conservation. T6 yield/WUE. Mi |
| `conservation_tillage_semiarid_loess_wue_2020` | updated_lit | paywalled | ok | med | Conservation tillage increases yield and precipitation use efficiency of wheat on the semi-arid Loess Plateau — Semi-arid dryland (Loess Plateau, China - middle-income). In-situ conservation tillage T |
| `fao_zai_planting_pits` | grey | oa | ok | med | Zai planting pits - FAO Family Farming Knowledge Platform — FAO (authoritative grey). In-situ zai explicit. T6 yield uplift (60-90% millet/sorghum) + input/labour descriptors. Descriptive, thinner on  |
| `icrisat_contour_bunding_mali` | grey | oa | ok | med | Contour bunding preserves soils and boosts farmers' incomes by 20% in Mali (ICRISAT/ILRI) — ICRISAT Mali contour bunding: +20% net income, runoff -40%, 3x sorghum yield, 1750 ha adoption to 2013. T6 o |
| `cilss_cba_landrecovery_niger_fr` | grey | oa | ok | med | Analyse cout-benefice des amenagements de recuperation des terres (banquettes, demi-lunes, cordons pierreux) - CILSS/PARIIS (Niger) — FR grey (CILSS). In-situ/micro-catchment half-moons + stone lines. |
| `pylusat_gis_suitability_toolkit` | tool | oa | NO | low | PyLUSAT - open-source Python toolkit for GIS-based land-use suitability analysis (AHP) — SCREENED OUT. Generic NbS-agnostic AHP/suitability toolkit - hardcodes no in-situ WH practice rule (weights sup |

## Gaps / next iteration

TOOL PROCESS EMPTY (0 included): no code tool implements an in-situ FIELD moisture-conservation branch with hardcoded weights/thresholds. GitHub RWH repos are urban/rooftop stormwater (out of scope) or NbS-agnostic GIS-MCDA toolkits (PyLUSAT); published SCS-CN+AHP RWH-siting exists only as papers, not pinnable code. If a tool T6 slice is required, T6 (outcomes/cost) is structurally thin for tools - tool evidence is more natural for T4; recommend deferring tool-for-T6. COST-PER-M3/PER-STRUCTURE: only WOCAT + CILSS carry structured per-unit cost; peer-reviewed cost-effectiveness ($/tCO2e, $/beneficiary) for in-situ WH is sparse - a targeted WB PAD/ICR + IEG grey sweep would fill it. GEOGRAPHIC SKEW: stock/grey strong on Sahel (Burkina/Niger/Mali) + Ethiopian highlands; recent OpenAlex skews to China conservation-tillage (temperate, weaker LMIC-dryland fit) - India/MENA/E.Africa recent in-situ WH cost-outcome underrepresented, add IWMI/ICRISAT India query next. ADOPTION/DIS-ADOPTION well covered (stock). PAYWALL: 7 screened-in stock/updated_lit paywalled -> acquisition_queue (Namita-J, CGIAR institutional)."
