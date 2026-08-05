# Discovery log — Agroforestry · shaded_perennial · T4

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 30 | 14 | 2 |
| updated_lit | 26 | 12 | 4 |
| grey | 20 | 10 | 4 |
| tool | 1 | 1 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: (coffee OR cocoa) AND climate AND suitability ; sort=cited_by_count:desc ; per_page=12`
- **updated_lit:** `OpenAlex title.search: (shade OR shaded) AND (cocoa OR cacao) AND (yield OR microclimate) , from_publication_date:2015-01-01 ; sort=cited_by_count:desc || complementary title search: coffee arabica shade meta-analysis optimal shade percent yield`
- **grey:** `WebSearch EN: 'shaded coffee cocoa agroforestry suitability optimal shade level recommendation WOCAT ICRAF CIFOR manual' || WebSearch ES: 'cafe con sombra cacao agroforestal zonificacion aptitud altitud requerimientos FAO CIPAV manual tecnico'`
- **tool:** `GitHub API repositories q= 'coffee suitability earth engine' (0), 'cocoa suitability random forest' (1), 'coffee land suitability GIS' (0), 'land suitability MCDA agriculture' (0), 'shade coffee model' (0)`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `gruter2022_global_coffee_suit` | stock | oa | ok | high | Expected global suitability of coffee, cashew and avocado due to climate change — PLoS ONE, 136 cites, gold OA. Global coffee (Coffea arabica) climate-suitability envelope current+ |
| `bunn2015_winner_loser_arabica` | stock | oa | ok | high | Winner or loser of climate change? A modeling study of current and future climatic suitability of Arabica coffee — Reg. Environ. Change, 89 cites, hybrid OA (Bunn et al). Seminal g |
| `koutouleas2022_shade_yield_meta` | updated_lit | oa | ok | high | Shade effects on yield across different Coffea arabica cultivars - how much is too much? A meta-analysis — Agron. Sustain. Dev. meta-analysis. OA PDF agritrop.cirad.fr/601173. THE  |
| `abdulai2018_cocoa_canopy_ghana` | updated_lit | oa | ok | high | On-farm cocoa yields increase with canopy cover of shade trees in two agro-ecological zones in Ghana — Climate and Development, 99 cites, hybrid OA. Shade-tree canopy-cover vs coco |
| `gateau2023_shade_drought_cocoa` | updated_lit | oa | ok | med | Combined effects of shade and drought on physiology, growth, and yield of mature cocoa trees — Sci. Total Environ., 32 cites, hybrid OA. Shade x drought interaction on mature cocoa |
| `ovalle2024_agroforestry_buffer_uganda` | updated_lit | oa | ok | high | The potential of agroforestry to buffer climate change impacts on suitability of coffee and banana in Uganda — Agroforestry Systems, hybrid OA. Models how shade/agroforestry shifts |
| `minambiente_rd_cafe_sombra_redd` | grey | oa | ok | high | Sistemas Agroforestales: Cafe Bajo Sombra en el marco de REDD+ (Guias Tecnicas) — Dominican Republic Ministry of Environment REDD+ technical guide, OA PDF. LMIC field manual for sh |
| `minambiente_rd_cacao_sombra_redd` | grey | oa | ok | high | Sistemas Agroforestales: Cacao Bajo Sombra en el marco de REDD+ (Guias Tecnicas) — DR Min. Environment REDD+ guide, OA PDF. Cacao-under-shade establishment envelope (altitude/temp/ |
| `cenicafe_agroforesteria_cafe` | grey | oa | ok | high | Agroforesteria y sistemas agroforestales con cafe (CENICAFE) — CENICAFE (Colombian National Coffee Research Center), OA PDF. Authority reference on coffee agroforestry incl. shade  |
| `zonificacion_arabica_guerrero_mx` | grey | oa | ok | med | Zonificacion agroecologica del Coffea arabica en el municipio Atoyac de Alvarez, Guerrero, Mexico — Investigaciones Geograficas (UNAM), OA (SciELO mirror). Agroecological-zoning me |
| `gh_fabiolexcastro_cocoa_col` | tool | repo | ok | low | fabiolexcastro/cocoa_Col - RandomForest/PCA cocoa suitability modelling (Colombia) — R repo, cocoa suitability via PCA + RandomForest over bioclim vars (bio_1:bio_29). clustering.R |

## Gaps / next iteration

All screened-in literature is OA (gold/hybrid/green), so no CGIAR-download hand-off is needed this iteration (acquisition_queue empty). Coverage skews to coffee (arabica) and Latin America/Ghana; thin on cocoa climatic-suitability envelopes and unsearched for Asian/robusta and shaded-tea systems (next iteration add 'shade tea' + robusta terms). Tool coverage is weak: no maintained GitHub shaded-perennial suitability tool with extractable hardcoded rules (cocoa_Col is data-driven; ShadeMotion is proprietary/closed and cannot be code-evidenced - flag for a docs-level acquire rule if its shade-geometry defaults are wanted). Confirm on-read that the two grey REDD+ guides and the Mexican zoning paper are framed for shaded (not full-sun) systems before tagging suitability_family_id.
