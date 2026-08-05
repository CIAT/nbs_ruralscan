# Discovery log — Agroforestry · shaded_perennial · T3

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 39 | 12 | 4 |
| updated_lit | 27 | 14 | 5 |
| grey | 8 | 8 | 4 |
| tool | 8 | 6 | 2 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: (shaded OR shade) AND (coffee OR cocoa OR cacao) AND (drought OR climate OR resilience OR temperature) | sort=cited_by_count:desc`
- **updated_lit:** `OpenAlex title.search: (shade OR shaded) AND (coffee OR cocoa OR cacao) AND (drought OR heat OR microclimate OR buffer OR adaptation), from_publication_date:2015-01-01 | sort=cited_by_count:desc ;; PLUS WebSearch for 2025 systematic review/meta-analysis`
- **grey:** `WebSearch: 'shaded coffee cocoa agroforestry shade trees drought climate resilience field manual WOCAT FAO CIPAV' ;; 'WOCAT SLM technology shade coffee cocoa agroforestry drought erosion; TECA FAO shade-grown cocoa climate adaptation manual'`
- **tool:** `GitHub repo search: 'coffee+agroforestry', 'coffee+suitability+model', 'cocoa+climate+suitability', 'shade+tree+microclimate+coffee' | sort=stars ;; code search blocked (auth required)`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `lin2022_shaded_coffee_review` | stock | oa | ok | high | Shaded-Coffee: A Nature-Based Strategy for Coffee Production Under Climate Change? A Review — Anchor benchmark review. Explicitly frames shade trees over coffee as an NbS buffering |
| `abdulai2018_cocoa_shade_gradient_ghana` | stock | oa | ok | high | Characterization of cocoa production, income diversification and shade tree management along a climate gradient in Ghana — LMIC (Ghana) climate-gradient study of shade-tree managem |
| `gateau2023_shade_drought_cocoa` | stock | oa | ok | high | Combined effects of shade and drought on physiology, growth, and yield of mature cocoa trees — Direct shade x drought interaction on mature cocoa (hazard-response core). Important  |
| `rodriguez2019_low_shade_arabica_brazil` | stock | oa | ok | high | Low levels of shade and climate change adaptation of Arabica coffee in southeastern Brazil — LMIC (Brazil) shade-level x heat/climate adaptation for Arabica. Quantifies optimal sha |
| `niether2018_throughfall_microclimate_cocoa` | updated_lit | oa | ok | high | Shade trees and tree pruning alter throughfall and microclimate in cocoa (Theobroma cacao L.) production systems — Mechanism paper: shade->throughfall/microclimate (temperature, hu |
| `metaanalysis2025_coffee_agroforestry_climate_risk` | updated_lit | oa | ok | high | Mitigating climate risks in coffee production through agroforestry: global evidence from a systematic review and meta-analysis — 68-study meta-analysis. Quantified hazard-response: |
| `gomes2021_microclimate_estimation_coffee_af` | updated_lit | oa | ok | high | Microclimate estimation under different coffee-based agroforestry systems using full-sun weather data and shade tree attributes — Links shade-tree attributes to microclimate buffer |
| `ampim2024_shade_species_microclimate_cocoa_ghana` | updated_lit | oa | ok | med | Impact of common shade tree species on microclimate and cocoa growth in agroforestry systems in Ghana — LMIC (Ghana) practice-level shade->microclimate->growth. Shade-species named |
| `gomes2020_microclimate_soil_water_loss_coffee_af` | updated_lit | paywalled | ok | high | Microclimate and soil and water loss in shaded and unshaded agroforestry coffee systems — Shade vs full-sun effect on erosion/soil-water loss (erosion hazard-response). Paywalled - |
| `wb_fcpf_cocoa_agroforestry_guide` | grey | oa | ok | high | Global Guide for the Implementation of Sustainable Cocoa Agroforestry — World Bank / FCPF project doc (diamond source class). Practice-level shade-cocoa agroforestry for climate re |
| `wocat_tech_513_cocoa_agroforestry` | grey | other | ok | med | WOCAT SLM Technology 513 — cocoa agroforestry — WOCAT SLM DB (LMIC-grounded diamond class). Documents cocoa agroforestry climate-change benefits (shade working conditions, reduced  |
| `fao_teca_shade_grown_coffee` | grey | other | ok | med | FAO TECA — Shade-grown coffee agroforestry system — FAO practice DB entry on shade-grown coffee (multi-storey shade trees + coffee). Practice explicit. Web => snapshot + section lo |
| `nbsi_coffee_shading_brief` | grey | other | ok | low | Exploring Agroforestry in Coffee Production for Climate Resilience (Nature-based Solutions Initiative) — NBSI brief; secondary/summary. Low standalone evidence weight (points to pr |
| `vanoijen_caf2014` | tool | repo | ok | high | CAF2014 — process-based model for coffee agroforestry systems — Fortran process model; shade is a real code branch. model/shade.f90 L21: SA = CA * SHADEPROJ (shade area = crown are |
| `vezy_dynacof` | tool | repo | ok | med | DynACof — Dynamic Agroforestry Coffee Crop Model — R process model; shade->microclimate/energy/water-stress coupling in R/2-energy_model.R, 2-soil_model.R, 2-tree_model.R, 0-Consta |

## Gaps / next iteration

Strong OA coverage of the shade->microclimate->drought/heat buffering mechanism with good LMIC representation (Ghana, Brazil, Colombia, Ethiopia) and a fresh 68-study meta-analysis giving quantitative T3 effect priors. Key missing pieces: (1) the counter-evidence lane — shade can INCREASE pest/pathogen and, under extreme drought, water competition can raise cocoa mortality — needs deliberate inclusion so T3 response curves are not one-sided; (2) wind/flood hazard-response for shaded perennials is thin (evidence is almost all drought/heat/erosion); (3) no purpose-built shade suitability/MCDA GIS tool was found — only process models (CAF2014, DynACof), and GitHub code search was auth-blocked. Next iteration: run authenticated GitHub code search for hardcoded shade thresholds, and target Asia (Vietnam/Indonesia robusta) grey lit to balance the Latin-America/Africa skew.
