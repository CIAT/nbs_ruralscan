# Discovery log — Water Harvesting & Conservation · terracing · T6

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 125 | 15 | 4 |
| updated_lit | 51 | 15 | 3 |
| grey | 16 | 16 | 5 |
| tool | 8 | 8 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: (terracing OR terraces OR "fanya juu") AND (yield OR adoption) ; sort=cited_by_count:desc ; per_page=15`
- **updated_lit:** `OpenAlex title.search: (terracing OR terraces OR "stone bund") AND (yield OR cost) , from_publication_date:2015-01-01 ; sort=cited_by_count:desc ; per_page=15`
- **grey:** `WebSearch EN: terracing "fanya juu" stone bund cost per hectare yield increase adoption WOCAT FAO soil water conservation | WebSearch ES/FR: terrazas conservación suelo agua costo rendimiento adopción / banquettes cordons pierreux Sahel coût rendement`
- **tool:** `WebSearch: bench terracing suitability GIS model runoff slope GitHub Google Earth Engine soil water conservation siting | github terrace suitability slope RUSLE runoff earth engine site selection MCDA repository ; + GitHub API repo/tree/raw inspection of RUSLE GEE repos`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `stone_terraces_adoption_ethiopia_2006` | stock | oa | ok | high | Determinants of adoption and continued use of stone terraces for soil and water conservation in an Ethiopian highland watershed — 474 cites, OA. Adoption + dis-adoption (continued use) determinants fo |
| `stone_terraces_tigray_yield_profit_1999` | stock | paywalled | ok | high | Effects of stone terraces on crop yields and farm profitability: results of on-farm research in Tigray, northern Ethiopia — Yield + farm profitability (cost-effectiveness proxy, not full CBA) for ston |
| `terraces_adoption_peruvian_andes_2005` | stock | oa | ok | high | Adoption of terraces in the Peruvian Andes — OA. Terrace adoption in Andes — non-African LMIC dryland-mountain context, useful for transferability. T6 adoption. |
| `slow_forming_terraces_adoption_2005` | stock | oa | ok | med | Spatial heterogeneity and adoption of soil conservation investments: integrated assessment of slow-forming terraces — OA. Adoption of slow-forming (fanya-juu-type) terraces with spatial heterogeneity  |
| `stone_bunds_crop_yield_gumara_2020` | updated_lit | oa | ok | high | Impacts of stone bunds on selected soil properties and crop yield in Gumara-Maksegnit watershed, Northern Ethiopia — OA, recent. Quantified crop-yield + soil-moisture/property gains from stone bunds ( |
| `stone_bund_terraces_yield_swethiopia_2021` | updated_lit | paywalled | ok | med | Spatial variation in soil properties and crop yield on stone bund terraces in southwest Ethiopia — Yield + soil-moisture variation across stone-bund terrace positions. Paywalled -> acquisition_queue.  |
| `swc_terraces_potato_yields_2019` | updated_lit | paywalled | ok | med | Estimated potential impacts of soil and water conservation terraces on potato yields under different climate scenarios — Terrace yield-impact estimates under climate scenarios (crop water availability |
| `swc_yield_ethiopia_review_synthesis_2022` | updated_lit | oa | ok | high | Soil and water conservation practice effects on soil physicochemical properties and crop yield in Ethiopia: review and synthesis — OA peer-reviewed synthesis aggregating terrace/bund yield + soil-mois |
| `wocat_slm_fanya_juu_1336` | grey | repo | ok | high | Fanya juu terraces — WOCAT SLM Technology #1336 — WOCAT structured DB entry: establishment + maintenance labour/inputs & cost per ha, yield-change and benefit fields, slope/soil-depth applicability. L |
| `fao_water_harvesting_manual_x5301e` | grey | repo | ok | med | FAO — Water harvesting / soil conservation manual (technical section, terraces & bunds) — FAO manual: terrace/bund design norms, spacing, labour-days per ha (e.g. ~90 days/ha at 15% slope), slope/soil |
| `ird_terrasses_antierosives_afrique_typologie` | grey | oa | ok | med | Les terrasses antiérosives en Afrique: typologie, efficacité (IRD/Horizon, FR) — French-language IRD review: typology + effectiveness (yield/water/erosion) of anti-erosion terraces across Africa, incl |
| `niger_sahel_ces_cordons_banquettes_cba` | grey | oa | ok | med | Bonnes pratiques de conservation des eaux et des sols — Sahel (cost-benefit of banquettes, half-moons, stone cordons) — FR grey report: cost + durability + benefit of Sahelian terracing/bunding (banqu |
| `nriveras_rusle_gee_pfactor` | tool | repo | NO | low | RUSLE (GEE Python-API) — support-practice P-factor block — PICOS-FAIL for terracing: P-factor is keyed to MODIS land-cover class (croplands=0.5) and slope (0.2-0.5), NOT to a terracing/stone-bund prac |

## Gaps / next iteration

Strong, well-evidenced T6 corpus on the OUTCOME side (yield, soil-moisture, erosion reduction) heavily concentrated in the Ethiopian highlands (stone bunds / fanya juu); Andes and Sahel add transferability but thinner. WEAK spots: (1) COST/cost-effectiveness quantification is scarce in peer-reviewed OA — the best per-ha establishment/maintenance cost figures sit in grey/database sources (WOCAT #1336, FAO manuals, Sahel FR reports), which carry a positive/self-reported bias needing the grey discount, esp. on benefit claims; the one solid peer-reviewed profitability source (Tigray 1999) is paywalled. (2) Cost-per-m3-stored / cost-per-tCO2e / cost-per-beneficiary indicators essentially absent — expect to leave those T6 economic_indicator_type slots unpopulated at scoping grade. (3) Dis-adoption / abandonment evidence limited to the 2006 continued-use study and Sahel banquette-durability notes. (4) TOOL process yielded nothing includable: no open repo hardcodes terracing as an explicit practice branch — RUSLE-GEE tools encode support-practice P-factor by land-cover/slope only, so terracing effectiveness is not a code criterion; a dedicated terracing-siting/effectiveness tool appears not to exist in OA repos. (5) Family-scope caution: several Sahel/FR sources mix in half-moons/zaï (different WH family) and some hits are species-specific orchard agronomy (avocado, coffee) — must be routed out of the terracing practice surface at extraction.
