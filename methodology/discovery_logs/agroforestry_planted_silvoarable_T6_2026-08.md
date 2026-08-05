# Discovery log — Agroforestry · planted_silvoarable · T6

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 316 | 15 | 4 |
| updated_lit | 177 | 15 | 4 |
| grey | 16 | 12 | 3 |
| tool | 8 | 4 | 2 |

### Verbatim search terms

- **stock:** `title.search: ("alley cropping" OR silvoarable OR "tree intercropping" OR "hedgerow intercropping" OR parkland OR "trees on farms") AND (yield OR carbon OR adoption OR income OR profitability OR biodiversity) ; sort=cited_by_count:desc`
- **updated_lit:** `title.search: ("alley cropping" OR silvoarable OR "tree intercropping" OR "hedgerow intercropping" OR parkland OR "trees on farms") AND (yield OR carbon OR adoption OR cost OR income OR biodiversity) , from_publication_date:2015-01-01 ; sort=cited_by_count:desc`
- **grey:** `WebSearch q1='alley cropping parkland agroforestry field manual yield income adoption WOCAT FAO TECA ICRAF cost per hectare' ; q2='World Bank agroforestry trees on farms cost per hectare carbon adoption evidence report Sahel parkland'`
- **tool:** `WebSearch q='github agroforestry suitability MCDA alley cropping GEE model carbon yield tool repository' ; then: git clone --depth 1 https://github.com/saraheb3/AgroforestrySuitability_GEE.git ; grep -niE 'alley|weight|slope|income' gee_script/Agroforestry-Suitability-Map`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `bayard2006_haiti_alleycrop_econ` | stock | paywalled | ok | high | The economics of adoption and management of alley cropping in Haiti — LMIC (Haiti) adoption + management economics of alley cropping — core T6 adoption/dis-adoption + cost evidence |
| `luedeling2012_sahel_parkland_carbon` | stock | oa | ok | high | Carbon sequestration potential of parkland agroforestry in the Sahel — Parkland explicit; carbon accrual rate ~0.4 Mg C/ha/yr and system C stocks + carbon-payment feasibility -> T6 |
| `fahmi2016_sudan_parkland_yield_income` | stock | oa | ok | high | Impact of agroforestry parklands on crop yield and income generation: case study of rainfed farming in the semi-arid zone of Sudan — LMIC (Sudan) parkland yield + income generation |
| `mugendi1999_kenya_alleycrop_maize` | stock | paywalled | ok | high | Alley cropping of maize with calliandra and leucaena in the subhumid highlands of Kenya: Part 2. Soil-fertility changes and maize yield — Seminal LMIC (Kenya) alley-cropping maize  |
| `noldeke2021_indonesia_tof_adoption` | updated_lit | oa | ok | high | Simulating Agroforestry Adoption in Rural Indonesia: The Potential of Trees on Farms for Livelihoods and Environment — LMIC (Indonesia) trees-on-farms adoption dynamics + livelihoo |
| `leroux2020_senegal_parkland_millet_yield` | updated_lit | oa | ok | high | Using remote sensing to assess the effect of trees on millet yield in complex parklands of Central Senegal — LMIC (Senegal) parkland: EO-validated effect of trees on millet yield — |
| `kletty2023_temperate_silvoarable_biodiv` | updated_lit | oa | ok | med | Biodiversity in temperate silvoarable systems: A systematic review — Silvoarable explicit; systematic review of biodiversity outcomes — T6 biodiversity. OA. Temperate/Europe contex |
| `fleming2019_australia_tof_adoption` | updated_lit | oa | ok | med | Understanding the values behind farmer perceptions of trees on farms to increase adoption of agroforestry in Australia — Trees-on-farms adoption / dis-adoption behavioural drivers  |
| `cfa2024_alleycropping_training_manual` | grey | oa | ok | med | Training Manual for Applied Agroforestry Practices — Alley Cropping (2024 Edition), University of Missouri Center for Agroforestry — Alley cropping explicit; establishment cost + m |
| `fao_alley_farming_intro` | grey | oa | ok | med | Introduction to Alley Farming (FAO training unit, X5545E) — Alley farming/cropping explicit, LMIC (Africa) framing; yield + soil-fertility outcomes + establishment guidance. FAO gr |
| `icraf_sahel_parkland_carbon_brief` | grey | oa | ok | med | World Agroforestry (ICRAF): The carbon sequestration potential of farms in the African Sahel — Parkland/trees-on-farms carbon + income framing (grey companion to Luedeling 2012). L |
| `saraheb3_af_suitability_gee` | tool | repo | ok | med | AgroforestrySuitability_GEE (saraheb3) — GEE suitability + economic-viability decision tool — PICOS confirmed in CODE: alley cropping is an explicit practice branch, not just READM |
| `usda_alley_econ_tool` | tool | oa | ok | med | ALLEY: Agroforestry Land-use Economic Yield and Risk tool (USDA Forest Service GTR-SRS-235) — Alley-cropping economic model explicit (NPV, annualised returns, financial risk) -> T6 |

## Gaps / next iteration

Latin-American silvoarable/alley-cropping T6 evidence (CIPAV/Colombia, Central America) is thin in this pass — the OA hits skewed to Sahel parklands, temperate Europe, and US extension manuals; a targeted ES/PT WebSearch and OpenAlex Spanish/Portuguese title slice is the next iteration. WOCAT SLM database and FAO TECA did not surface via WebSearch and should be queried directly for LMIC establishment-cost and cost_per_ha figures. Cost-effectiveness in explicit cost_per_beneficiary / cost_per_tCO2e units remains weak (only indicative ranges from grey/ICRAF-Luedeling); the two tool candidates encode economics as US-budget design choices, so scoping-grade LMIC cost indicators still need dedicated grey (World Bank PAD/ICR) discovery.
