# Discovery log — Agroforestry · silvopastoral · T3

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 84 | 15 | 4 |
| updated_lit | 59 | 20 | 5 |
| grey | 16 | 16 | 4 |
| tool | 20 | 10 | 1 |

### Verbatim search terms

- **stock:** `title.search:(silvopastoral OR silvopasture OR silvopastoril OR sylvopastoral) AND (drought OR heat OR resilience OR climate) | sort=cited_by_count:desc`
- **updated_lit:** `title.search:(silvopastoral OR silvopasture OR silvopastoril) AND (drought OR heat OR flood OR erosion OR wind OR microclimate OR shade OR resilience),from_publication_date:2015-01-01 | sort=cited_by_count:desc`
- **grey:** `EN: 'silvopastoral systems climate resilience drought heat livestock field manual WOCAT FAO CIPAV Latin America' | ES: 'sistemas silvopastoriles resiliencia climatica sequia ganado manual CIPAV FAO guia tecnica'`
- **tool:** `WebSearch: 'silvopasture GitHub suitability model GIS MCDA grazing shade tree livestock tool' + GitHub API repo search: q=silvopasture / silvopastoral / agroforestry+suitability+grazing / silvopasture+model (sort=stars)`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `charra2020_eucalyptus_brazil` | stock | oa | ok | high | Silvopastoral system with Eucalyptus as a strategy for mitigating the effects of climate change on Brazilian pastures — Diamond OA, Brazil (LMIC). Practice explicit (silvopastoral) |
| `murgueitio2014_iss_adaptation` | stock | oa | ok | high | Contribution of intensive silvopastoral systems to animal performance and to adaptation and mitigation of climate change — Gold OA, Colombia (LMIC, CIPAV lineage). Intensive silvop |
| `iss_dryland_drought_2016` | stock | repo | ok | high | Silvopastoral Systems: Best Agroecological Practice for Resilient Production Systems Under Dryland and Drought — Green OA (Springer chapter). Direct T3 title: drought/dryland resil |
| `guevara2008_soilmoisture_nz` | stock | paywalled | ok | med | Soil moisture and water use by pastures and silvopastures in a sub-humid temperate climate in New Zealand — Temperate (non-LMIC) but quantifies silvopasture vs pasture soil-moistur |
| `bosi2015_microclimate_soilmoisture_brazil` | updated_lit | oa | ok | high | Microclimate and soil moisture in a silvopastoral system in southeastern Brazil — Diamond OA, Brazil (LMIC). Practice explicit. Core T3 mechanism: tree cover moderates microclimate |
| `kumar2020_soilhealth_semiarid` | updated_lit | repo | ok | high | Silvopastoral system for resilience of key soil health indicators in semi-arid environment — Green OA, semi-arid (likely India, LMIC). Practice explicit. T3: resilience of soil ind |
| `cardinael2020_forest2silvo_drought_ET` | updated_lit | repo | ok | high | Influence of forest-to-silvopasture conversion and drought on components of evapotranspiration — Green OA. Practice explicit (silvopasture conversion). T3: explicit drought x ET pa |
| `argentina2024_forage_drought` | updated_lit | paywalled | ok | high | Response of forage production to drought in silvopastoral systems in Argentina — Argentina (LMIC), 2024, recent. Direct T3: forage response to drought under silvopastoral canopy =  |
| `caatinga2022_thermalcomfort_arrangements` | updated_lit | paywalled | ok | high | Microclimate and animal thermal comfort indexes in different silvopastoral system arrangements in Caatinga — Caatinga, Brazil semi-arid (LMIC). Practice explicit. T3: heat/thermal- |
| `chara2019_fao_cipav_latam` | grey | oa | ok | high | Silvopastoral Systems and their Contribution to Improved Resource Use and Sustainable Development Goals: Evidence from Latin America (FAO/CIPAV/Agri-Benchmark) — OA PDF. High autho |
| `cipav_zapata_ssp_manual` | grey | oa | ok | med | Sistemas silvopastoriles: aspectos teoricos y practicos (Zapata Cadavid, CIPAV) — ES-language CIPAV field manual, OA PDF, LMIC (Colombia). Practice explicit. Practitioner threshold |
| `catie_ssp_chapter6` | grey | oa | ok | med | Sistemas silvopastoriles: una herramienta para... (CATIE, Capitulo 6) — CATIE repository OA PDF (Costa Rica, LMIC), ES. Practice explicit. T3-relevant drought/dry-season & microcli |
| `fao_sti_ssp_drought_fodder` | grey | oa | ok | med | Introduction of silvopastoral systems for cattle raising to sustainably provide fodder in drought periods (FAO STI Portal) — FAO web brief on Colombia/Costa Rica/Nicaragua project: |
| `hortibonn_silvopastoral_livestock_tool` | tool | repo | ok | low | hortibonn/Silvopastoral_Livestock (R decision-analysis Monte-Carlo model) — Practice explicit in code (App.R, Mindrum_Complete_DA_Model_3.R, Input_table_Rev3_AM.csv). BUT it is a f |

## Gaps / next iteration

Flood, wind, and erosion hazard-response evidence for F3 is nearly absent — the corpus is dominated by heat/thermal-comfort and drought/dry-season forage + microclimate/soil-moisture buffering (a livestock-welfare rather than land-hazard framing). LMIC coverage is strong but LatAm-skewed (Brazil/Colombia/Argentina/Costa Rica); Sub-Saharan Africa and South/Southeast Asia dryland silvopasture are thin (one semi-arid soil-health paper), so next iteration should query the WOCAT SLM technologies DB directly and add AGROVOC ES/FR/PT title terms for African rangeland-tree systems. No spatial hazard-response tool exists for F3 — treat the tool process as closed/N-A for T3 rather than re-run.
