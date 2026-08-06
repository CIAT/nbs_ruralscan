# Discovery log — Riparian Buffers · planted · T3

- Run `riparian_buffer_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.1 · nbs_id `riparian_buffer`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 1379 | 15 | 4 |
| updated_lit | 81 | 18 | 5 |
| grey | 31 | 31 | 5 |
| tool | 12 | 12 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: "riparian buffer OR buffer strip OR filter strip OR vegetated buffer"; sort=cited_by_count:desc; per_page=15`
- **updated_lit:** `OpenAlex title.search: "riparian buffer OR buffer strip OR filter strip"; filter from_publication_date:2015-01-01; sort=cited_by_count:desc; per_page=18`
- **grey:** `WebSearch EN+ES+FR: "riparian buffer siting width guidance flood erosion sediment USDA NRCS conservation practice standard filter strip"; "WOCAT riparian buffer vegetated strip streambank stabilization SLM tropical erosion"; "franja ribereña vegetada control erosión sedimento inundación"; "bande riveraine tampon végétalisée cours d'eau érosion berge sédiment largeur"`
- **tool:** `WebSearch + GitHub API: "InVEST nutrient delivery ratio riparian buffer siting GIS MCDA"; "riparian buffer suitability siting GIS toolbox ArcGIS Python github stream buffer width slope reclassify"; natcap/invest + opengeos/WhiteboxTools-ArcGIS commit pins`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `rvb_wq_restoration_lowrance_1993` | stock | paywalled | ok | med | Riparian vegetated buffer strips in water-quality restoration and stream management — Seminal (950 cites) buffer function review; covers sediment/bank-erosion + stream management. Nutrient-heavy, henc |
| `buffer_width_guidelines_review_2004` | stock | paywalled | ok | high | Quantitative review of riparian buffer width guidelines from Canada and the United States — Synthesises buffer-width guidelines = the core limiter (width x function incl sediment/bank/thermal). Paywal |
| `multispecies_buffers_sediment_rainfall_2000` | stock | paywalled | ok | high | Multispecies Riparian Buffers Trap Sediment and Nutrients during Rainfall Simulations — Direct sediment-control (rainfall-simulation) evidence for planted multi-species buffer. Temperate (Iowa). Paywa |
| `sediment_nutrient_removal_multispecies_2003` | stock | paywalled | ok | high | Sediment and nutrient removal in an established multi-species riparian buffer — Established planted buffer sediment-removal performance metric. Paywalled -> queue. |
| `managing_buffer_strips_es_review_2020` | updated_lit | paywalled | ok | high | Managing riparian buffer strips to optimise ecosystem services: A review — Recent high-cite (342) synthesis spanning flood/erosion/sediment/thermal ES + management levers (width, veg type). Anchor upd |
| `effective_width_suspended_sediment_2020` | updated_lit | paywalled | ok | high | Assessment of the effective width of riparian buffer strips to reduce suspended sediment in an agricultural landscape — Effective-width limiter x suspended-sediment in agri landscape - directly T3 sed |
| `buffer_width_microclimate_logging_2019` | updated_lit | paywalled | ok | high | The effect of buffer strip width and selective logging on riparian forest microclimate — Buffer width x microclimate = thermal/drought-buffering hazard response (T3 shade/temperature). Paywalled -> qu |
| `veg_type_runoff_sediment_loss_2022` | updated_lit | oa | ok | high | Impacts of different vegetation in riparian buffer strips on runoff and sediment loss — OA. Grass-vs-woody vegetation parameter x runoff+sediment loss - directly informs the family's veg-type paramete |
| `nutrient_sediment_retention_length_vegtype_2024` | updated_lit | paywalled | ok | high | Nutrient and sediment retention by riparian vegetated buffer strips: impacts of buffer length, vegetation type, and ... — 2024 quantifies buffer length x veg type x sediment retention - limiter + para |
| `nrcs_cps_391_riparian_forest_buffer` | grey | oa | ok | high | USDA-NRCS Conservation Practice Standard - Riparian Forest Buffer (Code 391) — Authoritative practice standard for planted (woody/forested) riparian buffer: min horizontal width 35-50ft, enhancement u |
| `nrcs_390_393_filter_strip_grassed_buffer` | grey | oa | ok | high | USDA-NRCS Filter Strip (393) & Grassed Riparian Buffer (390) practice guidance — Grass/herbaceous filter-strip standard (grass side of the family): 20ft sediment / 30ft dissolved, widen by slope/soil/ |
| `wocat_6204_vegetative_riparian_buffers` | grey | oa | ok | high | WOCAT SLM Technology #6204 - Vegetative riparian buffers — Diamond source class (WOCAT SLM DB), LMIC-grounded practice entry: trees/bushes/grass strips for sediment+nutrient filtering and streambank s |
| `fao_franja_riberena_sti` | grey | oa | ok | med | FAO STI Portal - Franja Ribereña (riparian strip innovation) — Spanish-language FAO grey source; tropical/LMIC framing (sediment/runoff/flood control; establish 10m wide x ~1km each bank). LMIC + mult |
| `epa_riparian_buffer_width_2005` | grey | oa | ok | med | EPA - Riparian Buffer Width, Vegetative Cover, and Nitrogen Removal Effectiveness (2005) — Width x vegetative-cover synthesis. N-removal focus (water-quality) so med for T3-hazard, but width x veg-cov |
| `invest_ndr_natcap` | tool | repo | NO | low | InVEST Nutrient Delivery Ratio (NDR) model - natcap/invest — PICOS FAIL for this family: NDR computes effective_retention along generic downslope flow paths; 'riparian buffer' + retention_length (10-3 |
| `whiteboxtools_arcgis` | tool | repo | NO | low | WhiteboxTools-ArcGIS Python toolbox - opengeos — NbS-agnostic hydro/terrain/stream-network toolbox (buffer, slope, reclassify, stream-order primitives). No riparian-buffer siting criterion or hardcode |

## Gaps / next iteration

DISCOVERY + SCREENING ONLY - no extraction/files/registers/git performed; JSON is the sole deliverable. All searches ran ruleset v1.4.1. OpenAlex live via curl (no 429): stock title.search count=1379, updated_lit(2015+)=81 after tightening (first-pass 704 was polluted by riparian-plant SDM/flood-response ecology = single-species envelope, PICOS-excluded). KEY GAPS: (1) TOOL process yielded ZERO PICOS-passing candidates - InVEST NDR (retention along generic flow path, not a buffer-siting branch) and WhiteboxTools-ArcGIS (NbS-agnostic primitives) both fail the explicit-practice test; no dedicated planted-riparian-buffer siting tool with hardcoded width/slope criteria was found. A deeper GitHub sweep (riparian siting models, watershed BMP-placement optimisers e.g. SWAT-based) is warranted before declaring tool=searched-done. (2) LMIC/tropical evidence is thin vs temperate US/Canada/EU dominance - salvaged via WOCAT #6204 + FAO Franja Ribereña (ES) + a visible tropical vein in OpenAlex (Riparian buffers in tropical agriculture 2018 OA; oil-palm macroinvertebrate 2018 OA; Nigeria Ikpoba 2021 OA; humid-tropical-steeplands selection 1990) that should be pulled in a dedicated tropical sub-search next round. (3) FLOOD-attenuation/peak-flow evidence is under-represented in titles (corpus skews sediment + nutrient + thermal); targeted flood/peak-flow x buffer search recommended. (4) FR grey hits were Quebec regulatory (5m rule) - context only, not lead evidence; PT-language grey not yet searched. (5) 8 paywalled high-relevance items -> acquisition_queue for Namita-J (never PDFs in git; PDFs -> SharePoint library per acquisition lock). OA items (veg_type_runoff_2022, all grey PDFs, WOCAT, FAO) fetchable directly. Saturation on grey width/slope siting rules reached (NRCS 391/393/390 + EPA converge); NOT reached on tool or tropical dimensions.
