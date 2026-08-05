# Discovery log — Agroforestry · shaded_perennial · T6

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 154 | 15 | 5 |
| updated_lit | 15 | 15 | 6 |
| grey | 17 | 10 | 4 |
| tool | 15 | 6 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex REST: title.search:(shaded OR shade) AND (coffee OR cocoa OR cacao) AND (yield OR income OR carbon OR adoption OR biodiversity)  [sort=cited_by_count:desc]`
- **updated_lit:** `OpenAlex REST: title.search:(shade OR shaded) AND (coffee OR cocoa OR cacao) AND (adoption OR income OR livelihood OR profitability OR cost), from_publication_date:2015-01-01  [sort=cited_by_count:desc]`
- **grey:** `WebSearch #1: 'shaded coffee cocoa agroforestry adoption yield income carbon cost per hectare WOCAT FAO field manual'  |  WebSearch #2: 'WOCAT SLM technology shade-grown coffee cocoa agroforestry establishment cost benefit Latin America CIPAV'`
- **tool:** `GitHub API + gh CLI: repos q='shade coffee suitability' / 'cocoa agroforestry suitability mapping' / 'coffee cocoa agroforestry model yield' / 'coffee suitability google earth engine' / 'cocoa suitability climate mapping'; code q='shade coffee suitability language:Python'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `vaast2016_double_dividend` | stock | paywalled | ok | high | Shaded Coffee and Cocoa – Double Dividend for Biodiversity and Small-scale Farmers — Directly F5. Synthesises biodiversity + smallholder income co-benefits of shaded coffee/cocoa.  |
| `tscharntke2016_cacao_carbon_noyieldloss` | stock | oa | ok | high | Cacao Cultivation under Diverse Shade Tree Cover Allows High Carbon Storage and Sequestration without Yield Loss — gold OA. F5 cacao: carbon storage/sequestration + yield outcome j |
| `asare2018_cocoa_yield_canopy_ghana` | stock | paywalled | ok | high | On-farm cocoa yields increase with canopy cover of shade trees in two agro-ecological zones in Ghana — hybrid. Yield-vs-shade dose response, on-farm, LMIC Ghana, two AEZs — strong  |
| `bisseleua2013_cocoa_yield_netreturns_wafrica` | stock | oa | ok | high | Shade Tree Diversity, Cocoa Pest Damage, Yield Compensating Inputs and Farmers' Net Returns in West Africa — gold OA. Yield + net returns (economics) + input costs along shade grad |
| `philpott2005_biodiv_yield_certification` | stock | paywalled | ok | med | Biodiversity, yield, and shade coffee certification — Seminal shade-coffee certification/yield/biodiversity trade-off. Closed access -> acquisition_queue. Neotropical. |
| `asare2018_cocoa_income_climategradient` | updated_lit | oa | ok | high | Characterization of cocoa production, income diversification and shade tree management along a climate gradient — gold OA. Production + income diversification + shade management ac |
| `gyau2020_shadetree_adoption_cocoa_ghana` | updated_lit | oa | ok | high | The role of shade trees in influencing farmers' adoption of cocoa agroforestry systems: insight from semi-deciduous zone — bronze OA. ADOPTION driver study (observed reality), LMIC |
| `wartenberg2024_lowemission_profitable_cocoa_ghana` | updated_lit | paywalled | ok | high | Low-emissions and profitable cocoa through moderate-shade agroforestry: Insights from Ghana — hybrid. Profitability + emissions jointly (cost-effectiveness incl. cost_per_tCO2e ang |
| `shade_vs_intensification_2023_profitability` | updated_lit | paywalled | ok | high | Shade versus intensification: Trade-off or synergy for profitability in coffee agroforestry systems? — hybrid. Shade-vs-intensification profitability trade-off — direct income/cost |
| `adoption_coffee_shade_gobuseyo_2021` | updated_lit | oa | ok | med | Adoption of Coffee Shade Agroforestry Technology and Shade Tree Management in Gobu Seyo District, East Wollega — gold OA. Adoption + shade-tree management, LMIC Ethiopia. Adds E-Af |
| `timber_income_diversification_coffee_peru_2019` | updated_lit | oa | ok | med | Shade tree timber as a source of income diversification in agroforestry coffee plantations, Peru — diamond OA. Income diversification via shade-tree timber, LMIC Peru — Neotropical |
| `wb_fcpf_2022_cocoa_agroforestry_guide` | grey | oa | ok | high | Global Guide for the Implementation of Sustainable Cocoa Agroforestry (World Bank / FCPF) — World Bank project/implementation doc (in-remit authority). Practice-explicit shaded-coc |
| `wocat_tech513_shade_coffee_af` | grey | other | ok | high | WOCAT SLM Technology — shade-grown coffee / dynamic agroforestry (technologies_513) — Diamond source class (WOCAT SLM DB), LMIC-grounded. Carries structured establishment/maintenan |
| `swissco_2025_agroforestry_cocoa_brief` | grey | oa | ok | med | SWISSCO Issue Brief 2025/1 — Agroforestry in Cocoa — Industry-platform brief on cocoa agroforestry adoption/economics. Apply grey positive-bias discount (COI). OA PDF. |
| `nbsi_coffee_shading_brief` | grey | oa | ok | med | Exploring Agroforestry in Coffee Production for Climate Resilience (Nature-based Solutions Initiative) — NbS synthesis brief with quantified pooled outcomes (+$1,760/ha net income, |

## Gaps / next iteration

Adoption, income/profitability, carbon and yield are well covered, but concentrated in Ghana/West-African cocoa and Neotropical (Peru/Mexico/Ethiopia) coffee; Asian shaded systems (Indonesia, Vietnam, India) and shaded tea are thin-to-absent and should be targeted next iteration. Indicative scoping-grade unit costs (cost_per_ha establishment/maintenance, cost_per_beneficiary) come mainly from grey/WB/WOCAT sources that need positive-bias discounting and on-page cost-table confirmation, with no peer-reviewed cost_per_tCO2e primary yet secured. The tool process is empty for T6: no codebase hardcodes shaded-perennial outcome/cost parameters (tools sit in T4), so T6 cost-effectiveness must be built from literature + grey, not tools.
