# Discovery log — Agroforestry · linear_boundary · T3

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 715 | 12 | 3 |
| updated_lit | 98 | 11 | 4 |
| grey | 16 | 16 | 4 |
| tool | 2 | 2 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: (windbreak OR shelterbelt OR hedgerow OR shelterbelts OR windbreaks) AND (drought OR wind OR erosion OR microclimate OR crop) ; sort=cited_by_count:desc`
- **updated_lit:** `OpenAlex title.search: (shelterbelt OR windbreak OR hedgerow) AND (Sahel OR semiarid OR Africa OR tropical OR erosion) , from_publication_date:2010-01-01 ; sort=cited_by_count:desc  [broad agroforestry x climate slice (windbreak OR shelterbelt OR hedgerow OR agroforestry) AND (drought OR wind OR flood OR erosion OR resilience OR climate), 2015+ = 1612 but mostly whole-NbS, not F4]`
- **grey:** `WebSearch #1: shelterbelt windbreak field manual wind erosion drought crop protection FAO WOCAT guidelines | WebSearch #2: living fence contour hedgerow living barrier erosion control manual CIPAV ICRAF Latin America Sahel windbreak climate resilience`
- **tool:** `WebSearch: github windbreak shelterbelt suitability GIS model wind erosion RWEQ WEPS site placement tool | github riparian buffer placement suitability GEE agroforestry hedgerow siting model script ; GitHub API: repos/saraheb3/AgroforestrySuitability_GEE tree + gee_script/Field-Buffer-Areas, Riparian-Buffer-Areas`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `brandle_windbreak_crop_benefits_1988` | stock | paywalled | ok | high | Benefits of windbreaks to field and forage crops — Seminal (312 cites) F4 hazard-response: quantifies wind-shelter effects on crop microclimate/yield (wind reduction to ~15-20H, ET |
| `cleugh_windbreak_airflow_microclimate_1998` | stock | paywalled | ok | high | Effects of windbreaks on airflow, microclimates and crop yields — Seminal review (267 cites) linking barrier porosity/height to sheltered-zone wind, temperature and moisture respon |
| `cornelis_optimal_windbreak_wind_erosion_2004` | stock | paywalled | ok | high | Optimal windbreak design for wind-erosion control — J Arid Environments (257 cites): windbreak geometry vs wind-erosion/threshold friction velocity in arid land. Directly F4 x wind |
| `windbreak_wind_speed_soil_protection_2017` | updated_lit | oa | ok | high | Effect of windbreaks on wind speed reduction and soil protection against wind erosion — Gold OA (62 cites). Measured wind-speed-reduction profiles and soil-loss protection behind w |
| `windbreak_vineyard_ET_reduction_ZA_2020` | updated_lit | oa | ok | high | Windbreaks as part of climate-smart landscapes reduce evapotranspiration in vineyards, Western Cape Province, South Africa — Gold OA, LMIC-grounded (South Africa). F4 x drought/wat |
| `hedgerow_erosion_loess_plateau_2019` | updated_lit | paywalled | ok | high | Erosion control of hedgerows under soils affected by disturbed soil accumulation in the slopes of loess plateau, China — Catena (China, LMIC). Contour-hedgerow response to water er |
| `windbreak_efficiency_wind_erosion_pm_2020` | updated_lit | paywalled | ok | med | Windbreak efficiency in controlling wind erosion and particulate matter concentrations from farmlands — AGEE (67 cites). Windbreak efficiency vs wind erosion + PM flux from farmlan |
| `fao_shelterbelt_soil_conservation` | grey | other | ok | med | Soil conservation through multi-purpose wind breaks/shelter belts (FAO Family Farming Knowledge) — FAO authority entry: shelterbelts reduce sandstorms, wind erosion, drought, frost |
| `nrcs_windbreak_shelterbelt_cps380` | grey | oa | ok | med | NRCS Conservation Practice Standard 380 - Windbreak/Shelterbelt Establishment (2021) — Authoritative design standard: hardcoded protection distance ~10H leeward/2H windward, porosi |
| `unccd_natural_windbreaks_toolbox` | grey | other | ok | med | Natural Windbreaks (UNCCD Land & Life SDS toolbox) — UNCCD sand-and-dust-storm toolbox: windbreaks as drought/wind-erosion/sandstorm buffer. Drylands/LMIC framing. Prose response c |
| `fao_sti_shelterbelts_sandy_areas` | grey | other | ok | med | Shelterbelts for farmland in sandy areas (FAO STI Portal innovation) — FAO STI: shelterbelts for sandy/drought-prone farmland - LMIC-relevant deployment context and hazard-bufferin |
| `saraheb3_agroforestry_suitability_gee` | tool | repo | ok | med | AgroforestrySuitability_GEE - Field-Buffer-Areas & Riparian-Buffer-Areas scripts — Explicit F4 branches: Field-Buffer-Areas comment 'field buffer zones for windbreaks' (L1), inward |

## Gaps / next iteration

Strong global coverage of windbreak/shelterbelt x wind-erosion and microclimate response, but the corpus skews HIC/temperate + wind-tunnel physics; genuinely LMIC-grounded F4 hazard-response is thin (Western Cape ET, loess-plateau/China hedgerows, arid-land design) and Sahel/Latin America living-fence + contour-hedgerow field evidence surfaced only as prose grey lit - WOCAT SLM DB and CIPAV/ICRAF entries were referenced but not directly retrieved and should be queried by name next iteration. Flood/riparian-buffer climate-hazard response (vs pollutant filtering) and living-fence drought/heat buffering for livestock are under-covered. The one tool encodes placement geometry, not hazard-response coefficients, so T3 tool evidence is effectively absent; a WEPS/RWEQ windbreak-submodel repo would fill the mechanistic-tool gap.
