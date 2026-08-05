# Discovery log — Agroforestry · planted_silvoarable · T3

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 42 | 12 | 4 |
| updated_lit | 30 | 15 | 4 |
| grey | 18 | 18 | 3 |
| tool | 10 | 10 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: (alley cropping OR silvoarable OR hedgerow intercropping OR parkland) AND (drought OR erosion OR microclimate OR resilience) ; sort=cited_by_count:desc`
- **updated_lit:** `OpenAlex title.search: (alley cropping OR silvoarable OR tree intercropping OR parkland) AND (drought OR heat OR flood OR windbreak OR erosion OR resilience) , from_publication_date:2015-01-01 ; sort=cited_by_count:desc`
- **grey:** `WebSearch #1: 'WOCAT SLM technology alley cropping OR parkland agroforestry erosion drought wind erosion control sub-Saharan' ; WebSearch #2: 'alley cropping parkland trees on farms drought resilience field manual WOCAT FAO agroforestry climate hazard buffering'`
- **tool:** `WebSearch: 'ICRAF agroforestry suitability GEE Google Earth Engine github tree cover cropland MCDA site selection' + GitHub API inspection of saraheb3/AgroforestrySuitability_GEE`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `lal_alley_erosion_hilly_philippines_1995` | stock | paywalled | ok | high | Alley cropping for managing soil erosion of hilly lands in the Philippines — Alley cropping explicit; hilly-land water-erosion control (hazard response) in a LMIC. Seminal erosion- |
| `kang_econ_erosion_alley_notill_nigeria_1990` | stock | paywalled | ok | high | Economic analysis of soil erosion effects in alley cropping, no-till and bush fallow systems in South Western Nigeria — IITA/Nigeria (LMIC), alley cropping vs no-till/fallow; soil- |
| `antecedent_soilmoist_runoff_erosion_alley_2007` | stock | paywalled | ok | high | Effects of antecedent soil moisture on runoff and soil erosion in alley cropping systems — Highest-cited true hit (125). Runoff + soil-erosion response of alley cropping (rainfall/ |
| `vandermeer_coffee_alley_erosion_indonesia_2003` | stock | oa | ok | high | Erosion Control on a Steep Sloped Coffee Field in Indonesia with Alley Cropping, Intercropped Vegetables, and No-Tillage — OA gold, Indonesia (LMIC), steep-slope erosion control vi |
| `alley_oilpalm_microclimate_moderation_2019` | updated_lit | paywalled | ok | high | Alley-cropping system increases vegetation heterogeneity and moderates extreme microclimates in oil palm plantations — Indonesia (LMIC), alley cropping explicit; moderation of extr |
| `walnut_alley_drought_shade_winterpea_2021` | updated_lit | paywalled | ok | high | Interactions between drought and shade on the productivity of winter pea grown in a 25-year-old walnut-based alley cropping system — Temperate (France) walnut alley cropping; droug |
| `alley_barley_drought_yield_benefit_2025` | updated_lit | oa | ok | high | High and dry: Barley (Hordeum vulgare) yield benefits from tree presence in a temperate alley cropping system during a drought year — OA hybrid, recent (2025). Direct drought-year  |
| `treelines_grassland_drought_alley_2023` | updated_lit | oa | ok | med | Tree lines do not reduce grassland productivity and herbage quality in alley cropping under drought — OA hybrid. Alley cropping tree-line drought response; alley in grassland leans |
| `wocat_slm_alley_parkland_erosion_ssa` | grey | oa | ok | high | WOCAT SLM Technologies database — alley cropping / parkland / ANR erosion & drought case studies — LMIC-grounded SLM technology entries documenting water/wind-erosion + drought ben |
| `fao_parklands_ssa_x3940e` | grey | oa | ok | high | Agroforestry parklands in sub-Saharan Africa (FAO) — FAO authority monograph on parkland (scattered trees on cropland = F1 sub-vocab) in SSA; drought/microclimate buffering and soi |
| `fao_agroforestry_adaptation_module` | grey | oa | ok | med | FAO agroforestry adaptation option / SFM toolbox agroforestry module — Authority framing of agroforestry (incl. alley cropping/silvoarable) as climate-adaptation option buffering d |
| `saraheb3_agroforestrysuitability_gee_af338e8` | tool | repo | ok | med | AgroforestrySuitability_GEE — field-buffer (windbreak) + riparian-buffer hazard-response branches — Windbreak (wind-hazard) and riparian-buffer (flood/erosion) are explicit code br |

## Gaps / next iteration

Recent (2015-2026) F1 hazard-response evidence is dominated by temperate/EU alley-cropping studies (walnut, barley, oil-palm); genuinely recent LMIC drought/heat-buffering peer-reviewed work on trees-on-cropland is thin, with the strongest LMIC signal in older classics (Philippines/Nigeria/Cote d'Ivoire/Indonesia erosion + microclimate) and in grey WOCAT/FAO parkland material. OpenAlex title-search is heavily polluted by the urban 'alley' homonym (green alleys, flash-flood alley), so a full-text or concept-filtered query is advisable next iteration to recover missed LMIC studies. Tool coverage for T3 is weak - agroforestry GEE tools are almost all T4 suitability; only windbreak/riparian-buffer branches encode hazard response, and those are US-context, so parkland/Sahel windbreak or FMNR-adjacent wind-erosion tooling remains a gap.
