# QA backlog — recovered-source extraction (2026-10-08)

**For:** Namita (QA/QC). **From:** the orchestrator, after extracting the 71 sources recovered on 2026-10-07 (480 units from 66 sources; four lanes: water harvesting 219, agroforestry 107, forest restoration 124, wetland 30).

## What this is
Every unit passed the deterministic gates (verbatim quote on the cited page, every number in the quote, fixed context keys, bands, ontology id, family id). What the gates cannot judge is listed below: the lanes' own least-certain calls, plus a few cross-paper issues. 23 items. Each row: which unit (or source), what the doubt is. Decide keep · drop (with a reason code) · re-tag, in the dashboard QA tab or by marking the CSV.

## Items
| NbS | unit / source | question |
|---|---|---|
| water_harvesting_conservation | `ev_*_rock10_2` | Rockström 2010: tagged extreme drought with the cue taken from a table on the same page — confirm the author's wording applies to the result |
| water_harvesting_conservation | `ev_*_boil19_1 / _2 / ev_food_security_boil19_1` | Boillat 2019 Malawi 2015/16: tagged severe from the season description while results pages say 'below-average rainfall' (moderate) — pick one; also co-authored by P. Steward (tier capped medium) |
| water_harvesting_conservation | `ev_*_rock10_3` | Rockström: Syrian supplemental-irrigation yield gain >400 % — water may be groundwater, not harvested runoff (PICOS) |
| water_harvesting_conservation | `ev_*_pals23_1 / _2` | Palsaniya 2023 preprint, 11 farmers with ponds; dry-season unit is really irrigation |
| water_harvesting_conservation | `ev_*_mazv09_1` | Mazvimavi 2009: drought-year yield gain of conservation farming confounded with fertiliser |
| agroforestry | `ev_food_security_abasse23_1` | Abasse 2023: departments with dense FMNR had a cereal surplus in a drought year — co-occurrence across departments, confounded by population density |
| agroforestry | `ev_crop_yield_robusti17_2` | Robusti 2017: coffee plant deaths after frost recorded as crop_yield (no better variable); one young trial |
| agroforestry | `ev_livestock_productivity_saucedo23_3` | Saucedo 2023: '12 times more meat' uncited; same review elsewhere says 9–11 % — self-contradictory |
| agroforestry | `ev_crop_yield_bayala14_1` | Bayala 2014: cereal yield under parkland trees coded negative from a range spanning loss to gain by species |
| agroforestry | `ev_livestock_productivity_guaqueta25_1` | Guáqueta 2025: El Niño milk loss cited from a reference not checked; hazard left blank (sentence never names drought) |
| agroforestry | `cisneros_2024 forage-in-drought vs montagnini_2015 El Niño milk` | Likely the same Colombian farm and drought counted twice — consider lineage link |
| forest_restoration | `barajas_guzman_2013 drought asset unit` | Dry year named on p1, not in the quote |
| forest_restoration | `naidoo_2019 stunting → food_security` | Stunting recorded under food_security as a proxy |
| forest_restoration | `robertson_wunder_2005 'environmental protection' → biodiversity_outcome` | Proxy mapping — confirm |
| forest_restoration | `hochard_2019 / del_valle_2020 night-light economic activity → wind_cyclone_hazard` | No 'economic_activity' variable; recorded under the hazard variable |
| forest_restoration | `das_2011 / marois_mitsch_2015 mangrove benefit per ha` | Came out 'strong' because banded against COST bands — check band choice |
| forest_restoration | `bradshaw_2007 plantation–flood association; snilstveit_2019 deforestation result recorded as forest retained` | Direction/framing calls to confirm |
| forest_restoration | `kandel_2022 / hajjar_2021 / das_2011` | Thesis chapter, author manuscript, working-paper versions — page locators differ from the published versions |
| wetland_management | `ev_wet_flood_hazard_ramsar18_1` | Otter Creek flood-damage reduction measures existing wetlands/floodplains (tagged existing_wetland comparator); the only strong effect — would dominate the flood cell |
| wetland_management | `ev_wet_protected_area_status_qiu20_1` | Legal protection raises restoration priority — neither a T4 mask nor a soft factor; maybe a T5 descriptor |
| wetland_management | `ev_wet_built_up_areas_uuemaa18_1` | Distance to roads/farmsteads treated as a physical built_up_areas constraint — could be read as distance_to_road (wrong-table) |
| wetland_management | `medland_2020 groundwater + slope units` | Local quantile breaks; 11–86 m groundwater levels implausible as wetland water-table depths; slope % vs degrees |
| wetland_management | `wet_feasible_locations_lidar_suitability_2018 family` | Uuemaa covers in-stream impoundment wetlands (close to the parked 'constructed' family), filed under 'creation' — confirm |

## Also for a human
- `silvopastoral_drought_herbage_arid_india_2008`: cached file is a journal score list, not the paper — re-acquire by title.
- `icarda_oweis_wh_indigenous_2001`: scanned PDF, no text layer — OCR before any pass.
- `roose_2017_restauration_fr` (714-page IRD book): not extracted; needs a targeted chapter pass once title-verified.
- Unmapped effect variables (feed no cell until a crosswalk route or ontology decision exists): ecosystem_service (13), tree_canopy_cover (7), establishment_survival-as-effect (4), climate_shock (3), ndvi (3), adoption_rate, establishment_cost, recurrent_cost.
- Ontology gaps the lanes skipped rather than invent: historic wetland extent, wetland:catchment ratio, design water depth, GHG reduction after rewetting, landslide outcome, night-light economic activity, water productivity, cropping intensity, crop diversity, migration, methane intensity, EROI, adaptive capacity.

Technical record: `pipeline/staging/extract_recovered/lane_*_report.md` (local), `methodology/effect_evidence_followups.md`.
