# Discovery log — Water Harvesting & Conservation · micro_catchment · T6

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 30 | 15 | 4 |
| updated_lit | 20 | 20 | 5 |
| grey | 13 | 13 | 5 |
| tool | 10 | 10 | 1 |

### Verbatim search terms

- **stock:** `title.search:("micro-catchment" OR microcatchment OR "semi-circular bund" OR "runoff farming") AND (yield OR cost OR adoption OR "soil moisture") | sort=cited_by_count:desc`
- **updated_lit:** `title.search:("water harvesting" OR "runoff harvesting" OR "runoff farming") AND ("micro-catchment" OR microcatchment OR bund OR "catchment ratio" OR ridge),from_publication_date:2015-01-01 | sort=cited_by_count:desc`
- **grey:** `WebSearch EN: 'WOCAT SLM technology semi-circular bunds demi-lune establishment cost USD per hectare maintenance benefit-cost drylands'; 'FAO WOCAT micro-catchment semi-circular bund runoff water harvesting yield cost per hectare drylands'; 'ICRISAT IWMI micro-catchment semi-circular bunds runoff farming yield adoption cost Sahel India semi-arid manual'`
- **tool:** `WebSearch (github.com only): 'github.com rainwater harvesting site selection python SCS-CN runoff suitability AHP repository code'; general: 'github water harvesting suitability model runoff catchment ratio GIS MCDA siting tool RWH'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `turkey_ridgefurrow_redpepper_2021` | stock | paywalled | ok | high | The effect of mulched ridge and furrow micro catchment water harvesting on red pepper yield and quality features in Bafra Plain of Northern Turkey — Micro-catchment WH explicit; T6 yield + quality out |
| `ethiopia_eshewa_microcatchment_adoption_2020` | stock | paywalled | ok | high | Farmers' Perceptions and Adoption of Micro Catchments for Improved Establishment of Agroforestry Trees in East Shewa Zone, Ethiopia — Micro-catchment WH explicit; T6 adoption + dis-adoption drivers, E |
| `jojoba_runoff_microcatchment_yield_1978` | stock | paywalled | ok | med | Growth and Yield of Jojoba Plants in Native Stands Using Runoff-Collecting Microcatchments — Seminal runoff-collecting microcatchment yield evidence (19 cites). claim_scope likely crop_specific (jojob |
| `runoff_farming_desert_v_rangespecies_1971` | stock | paywalled | ok | med | Runoff Farming in the Desert V. Persistence and Yields of Annual Range Species — Seminal 'runoff farming' desert series; T6 yield/persistence of range species under micro-catchment runoff. species/cro |
| `egypt_matrouh_ridgefurrow_fababean_2015` | updated_lit | oa | ok | high | Impact of ridge-furrow water harvesting system on faba bean (Vicia faba L.) production under rainfed conditions in Matrouh, Egypt — OA, 26 cites. Ridge-furrow micro-catchment WH, rainfed; T6 crop prod |
| `mali_infield_contourbund_wh_2017` | updated_lit | oa | ok | high | In-field water harvesting using contour bund with earth to cope with changing climate in semi-arid smallholder farming areas in Mali — OA. In-field contour-bund micro-catchment WH, Sahel smallholder ( |
| `kenya_nyando_microcatchment_rwh_trees_2015` | updated_lit | repo | ok | high | Effects of micro-catchment rain water-harvesting on survival and growth of multipurpose trees and shrubs in Nyando District, Western Kenya — OA (figshare). Micro-catchment RWH explicit; T6 survival/gr |
| `pearl_millet_tied_ridges_yield_2019` | updated_lit | oa | ok | med | Effects of Integrated Nutrient Management and Water Harvesting Technique (Tied Ridges) on Grain and Stover Yields of Pearl Millet — OA. Tied-ridges micro-catchment WH; T6 grain + stover yield. Pearl m |
| `ibiza_ground_runoff_harvesting_2023` | updated_lit | oa | ok | med | Ground-Runoff Harvesting to Increase Water Availability in Isolated Households on Hilly Mediterranean Islands: A Case Study in a Micro-Catchment of Ibiza (Spain) — OA (Water/MDPI). Micro-catchment gro |
| `wocat_niger_semicircular_bunds_1614` | grey | oa | ok | high | WOCAT SLM Technology: Semi-Circular Bunds for crops and forest/rangelands in Niger (QCAT technologies_1614) — Semi-circular bunds explicit (core family vocab). T6 yield (millet +180 kg/ha, straw +400  |
| `wocat_contour_trench_bund_1480` | grey | oa | ok | med | WOCAT SLM Technology: Contour Trench cum Bund (QCAT technologies_1480), Sourakhak watershed Afghanistan — Contour trench + bund micro-catchment; T6 establishment cost ~1450 USD/ha (1380 labour + 70 to |
| `icrisat_modified_contour_bunding_alfisols_1989` | grey | oa | ok | high | A Modified Contour Bunding System for Alfisols of the Semi-Arid Tropics (ICRISAT, Agric Water Management 1989) — OA PDF (ICRISAT OAR). Contour-bunding micro-catchment; T6 yield/runoff outcome, India S |
| `india_sat_swc_adoption_productivity_risk_2020` | grey | oa | ok | med | Does Adoption of Soil and Water Conservation Practice Enhance Productivity and Reduce Risk Exposure? Empirical Evidence from Semi-Arid Tropics (SAT), India — OA (Sustainability). Adoption + productivi |
| `fao_sivanappan_wh_smallwatersheds_manual` | grey | oa | ok | med | FAO: Technologies for water harvesting and soil moisture conservation in small watersheds for small-scale irrigation (R.K. Sivanappan) — FAO manual (diamond source). Micro-catchment / small-watershed  |
| `runoff_cn_method_github_generic` | tool | repo | NO | low | kothawadegs/Runoff_CN_method - SCS-Curve Number runoff computation (GitHub) — PICOS FAIL: generic NbS-agnostic SCS-CN runoff calculator; no micro-catchment/semi-circular-bund practice branch, no catch |

## Gaps / next iteration

Strong on yield/adoption; THIN on hard cost (cost per structure / per m3 stored) and cost-effectiveness ratios - only WOCAT structured entries (Niger #1614; contour-trench #1480 ~1450 USD/ha) and secondary web mentions (~7000 USD/ha semi-circular bunds; ~20 USD/ha India contour bunds) surfaced, none yet from a primary corpus-cacheable source. No groundwater-recharge or area-irrigated cost-effectiveness datum specific to the micro-catchment family. TOOL is a genuine gap: no interrogable code repo hardcodes a micro-catchment/semi-circular-bund WH practice branch or catchment-ratio threshold (RWH GIS-MCDA logic lives only in journal AHP figures/tables, not published code) - recommend evidencing catchment-ratio/slope siting rules from the GIS-MCDA journal set into T4 rather than as a tool. Core-family (semi-circular bund / demi-lune) peer-reviewed T6 yield-with-cost is scarcer than broader ridge-furrow/tied-ridge in-field variants, which dominate recent OpenAlex hits - flag family-fit screening at extraction so tied-ridge/ridge-furrow rows are not silently counted as micro-catchment. Grey-lit benefit claims (WOCAT/FAO 3-4x yield) need the positive-bias/COI discount in synthesis. LMIC context coverage good (Niger, Mali, India SAT, Kenya, Egypt, Jordan) but MENA/S-Asia over-represented and Sahel semi-circular-bund cost primary data is light.
