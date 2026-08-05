# Discovery log — Agroforestry · planted_silvoarable · T4

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 397 | 12 | 3 |
| updated_lit | 104 | 12 | 3 |
| grey | 24 | 10 | 2 |
| tool | 6 | 3 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: ("alley cropping" OR "silvoarable" OR "hedgerow intercropping" OR "tree intercropping" OR parkland) AND (suitability OR climate OR rainfall OR soil OR slope) ; sort=cited_by_count:desc`
- **updated_lit:** `OpenAlex title.search: ("alley cropping" OR silvoarable OR "trees on farms" OR "trees outside forests" OR parkland OR "hedgerow intercropping") AND (suitability OR mapping OR GIS OR "land suitability" OR potential OR zonation) ; from_publication_date:2015-01-01 ; sort=cited_by_count:desc  +  WebSearch: 'ICRAF FAO agroforestry suitability mapping trees on farms parkland rainfall soil requirements technical guideline'`
- **grey:** `WebSearch EN: 'WOCAT alley cropping silvoarable parkland agroforestry land suitability biophysical requirements manual' ; 'ICRAF FAO agroforestry suitability mapping trees on farms parkland rainfall soil requirements technical guideline' ; 'Faidherbia albida parkland rainfall range mm agroecological zone Sahel establishment FAO WOCAT technology'`
- **tool:** `WebSearch: 'GitHub agroforestry land suitability GEE Earth Engine MCDA model alley cropping trees on farms' ; then GitHub API inspection of saraheb3/AgroforestrySuitability_GEE @ commit af338e8251c6bde4fa46caccf4e92124f80d7623 (tree + raw gee_script/Agroforestry-Suitability-Map)`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `bayala2014_parklands_climate_sahel` | stock | oa | ok | high | Parklands for buffering climate risk and sustaining agricultural production in the Sahel of West Africa — Bayala et al. 2014, Curr Opin Environ Sustain, 232 cites, hybrid OA. Pract |
| `bayala2015_parkland_processes_sahel` | stock | paywalled | ok | high | Advances in knowledge of processes in soil-tree-crop interactions in parkland systems in the West African Sahel: A review — Bayala et al. 2015, Agric Ecosyst Environ, 124 cites. Pr |
| `bayala2014_trees_preferential_flow_parkland` | stock | paywalled | ok | med | The effect of trees on preferential flow and soil infiltrability in an agroforestry parkland — Ilstedt/Bayala et al. 2014, Water Resour Res, 295 cites. Parkland soil-infiltration p |
| `nikiema2019_parkland_profiles_burkina_climatic_zones` | updated_lit | oa | ok | high | Agroforestry parkland profiles in three climatic zones of Burkina Faso — Diamond OA, LMIC-grounded. Parkland composition/structure across Sahelian-Sudanian-Sudano-Guinean climatic  |
| `reppin2021_trees_on_farms_indonesia_potential` | updated_lit | oa | ok | med | Simulating Agroforestry Adoption in Rural Indonesia: The Potential of Trees on Farms for Livelihoods — Gold OA, LMIC. Trees-on-farms potential/adoption simulation -> system_constra |
| `india_fao_agroforestry_suitability_mapping_2017` | updated_lit | paywalled | ok | high | FAO guidelines and geospatial application for agroforestry suitability mapping: case study of Ranchi, Jharkhand, India — Agrofor Syst 2017. FAO-land-suitability method applied to a |
| `fao_x3940e_parklands_ssa` | grey | oa | ok | high | Agroforestry parklands in sub-Saharan Africa (FAO Conservation Guide 34) — FAO authority guide, LMIC. Practice-level parkland definitions, distribution across agroecological/rainfa |
| `usda_nac_an12ac01_alley_cropping` | grey | oa | ok | med | Alley Cropping #1 (USDA National Agroforestry Center Agroforestry Notes AN-12) — USDA-NAC practice note, explicit alley-cropping siting/design guidance. Authoritative but temperate |
| `castle_agroforestry_suitability_gee_midwest` | tool | repo | ok | high | AgroforestrySuitability_GEE — geospatial MCDA agroforestry suitability decision-support tool (Castle, Miller, Wardropper; US Midwest) — PICOS confirmed in code: L79 'var practice = |

## Gaps / next iteration

No LMIC-grounded WOCAT SLM Technologies entry surfaced for silvoarable/alley cropping via web index — a direct WOCAT portal query is the top next-iteration action, since WOCAT is the diamond LMIC-context class for biophysical establishment requirements. Coverage is Sahel-parkland heavy (West Africa) plus temperate US; under-represented are Latin America (CIPAV, ES-language) and South/Southeast Asia silvoarable/hedgerow-intercropping quantitative envelopes. Much of the strongest quantitative material is Faidherbia-specific (species lane, deliberately excluded from the practice-level T4 surface) — a practice-vs-species boundary to hold at extraction.
