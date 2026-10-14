# Wetland management × T3 (hazard side) discovery: `updated_lit`, synthesis-first, English (2026-10-14)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `wet_t3t6_2026-10-14_lit_t3`, ruleset **v1.6.10**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-14: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `wet_t3t6_2026-10-14_lit_t3`, ledger per `--ledger`.


> Staging-only report. Run `wet_t3_lit_2026-10-14`, ruleset **v1.6.10**, process `updated_lit`, language English. Nothing was registered, queued, ledger-stamped or downloaded; no git command was run. Candidates: `pipeline/staging/discovery/wet_t3_lit_2026-10-14.json`.

**Scope.** `nbs_id=wetland_management`, table **T3 only** (hazard-impact mitigation for rural livelihoods, plus asset vulnerability of the works themselves). Hazards covered: flood · drought · fire (peat) · waterlogging/salinity · heat · coastal storm surge; asset side: sedimentation/clogging · breach/structure failure · subsidence · restoration failure. Generic parent search (`suitability_family_id=""`); every candidate is tagged with the FAM ids it speaks to (`wetland_management__restoration_rewetting` · `__creation` · `__peatland` · `__constructed` · `__coastal`).

**Why this round exists.** Wetland's current tables came out of a T4-era (siting/suitability) discovery; the progress ledger honestly records T3 and T6 as never searched. Two gaps shaped every query:
1. **Tropical / LMIC evidence** — the 70 known sources are overwhelmingly temperate and high-income. Every hazard block was run again with tropical/LMIC qualifiers (Q9, T15, T18, T19, T23, T24), and three dedicated tropical lanes were added (tropical-island NFM, Indonesian peat fire, SE-Asian peat subsidence).
2. **Measured rather than modelled flood outcomes** — our flood rows rest on hydraulic models. T16, T12 and T10 were written specifically to surface measured/observed/gauged/econometric flood outcomes, and every included candidate carries an `evidence_basis` field (`measured` · `mixed`).

**Targeting (Pete's standing rule).** Syntheses first: meta-analyses, systematic reviews, systematic maps, evidence gap maps and quantitative syntheses. Primaries were admitted **only** where a hazard has no synthesis, and each one says so in its `tier_rationale` ("PRIMARY admitted: …"). 14 of the 37 included are primaries, all for hazards where the synthesis literature is empty: measured flood-peak response to rewetting, measured flood damages, tropical peat fire, peat subsidence, and the canal-blocking works themselves.

**Out of scope by family.** Mangrove-only syntheses (Menéndez-type mangrove flood-protection work, mangrove tsunami reviews, mangrove hydrodynamic modelling SRs) were screened OUT: FAM puts mangroves under `forest_restoration__mangrove_coastal`, not `wetland_management__coastal`. Where an included coastal item mixes marsh and mangrove (`rowland_2026`, `narayan_2016`, `silliman_2019`), the note says to keep the marsh component here and route mangrove claims to forest restoration. Constructed-wetland water-treatment performance literature (pollutant/pathogen/nutrient removal) was filtered out as a T6 water-quality question, not T3; only its **clogging/failure** strand was kept.

## Channel
- **Search:** OpenAlex `/works`, `https://api.openalex.org/works?filter=<filter>&per-page=200&select=id,doi,display_name,publication_year,type,cited_by_count,primary_location,open_access,authorships,abstract_inverted_index&mailto=p.steward%40cgiar.org`. Default relevance order; first page (≤200) retrieved per query.
- **Rate limits:** retry-with-backoff on HTTP 429/503 was wired into the fetcher; no query failed after retry.
- **DOI checks:** Crossref `/works/<doi>` round-trip; citations rebuilt from the authoritative Crossref record (authors, container, volume, pages, issued year).
- **OA checks:** Unpaywall by DOI (`?email=p.steward@cgiar.org`), then web search per closed source (the required second step).
- **Dedup:** against `pipeline/staging/discovery/wetland_known_sources.json` (70 rows) by DOI and by normalised title/citation prefix.

## Verbatim queries (OpenAlex `filter=` value) · total count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| Q1 | `title_and_abstract.search:("wetland restoration" OR "wetland rewetting" OR "wetland creation" OR "floodplain restoration" OR "floodplain reconnection" OR "wetland conservation" OR "restored wetlands") AND (flood OR "flood risk" OR "flood peak" OR "peak discharge" OR "flood attenuation" OR "flood mitigation") AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "evidence gap map" OR "global synthesis" OR "quantitative synthesis" OR review)` | 155 | 155 |
| Q2 | `title_and_abstract.search:("wetland restoration" OR "wetland rewetting" OR "wetland creation" OR "floodplain restoration" OR "restored wetlands" OR "wetland management") AND (drought OR "dry season" OR "water scarcity" OR "low flow" OR baseflow OR "groundwater recharge" OR "water storage") AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "global synthesis" OR review)` | 66 | 66 |
| Q3 | `title_and_abstract.search:(peatland OR peat OR "peat swamp") AND (rewetting OR restoration OR "canal blocking" OR "drainage blocking") AND (fire OR fires OR "burned area" OR haze OR "fire risk") AND (review OR "meta-analysis" OR "systematic review" OR synthesis)` | 93 | 93 |
| Q4 | `title_and_abstract.search:("salt marsh" OR "saltmarsh" OR "tidal marsh" OR "coastal wetland" OR "coastal marsh") AND ("storm surge" OR "wave attenuation" OR "wave height" OR "coastal protection" OR "flood protection" OR "shoreline protection") AND ("meta-analysis" OR "systematic review" OR "global synthesis" OR review OR synthesis)` | 176 | 176 |
| Q5 | `title_and_abstract.search:(wetland OR wetlands OR peatland OR floodplain) AND ("disaster risk reduction" OR "ecosystem-based adaptation" OR "nature-based solutions" OR "natural flood management") AND ("systematic review" OR "systematic map" OR "evidence gap map" OR "meta-analysis" OR "evidence synthesis")` | 90 | 90 |
| Q6 | `title_and_abstract.search:("constructed wetland" OR "treatment wetland" OR "restored wetland" OR "wetland creation") AND (sedimentation OR siltation OR clogging OR "sediment accumulation" OR failure OR breach OR "embankment failure" OR "bund failure" OR subsidence) AND (review OR "meta-analysis" OR "systematic review" OR synthesis)` | 185 | 185 |
| Q7 | `title_and_abstract.search:(peatland OR peat) AND (subsidence OR "land subsidence" OR "peat subsidence" OR "surface motion") AND (drainage OR rewetting OR restoration OR plantation) AND (review OR "meta-analysis" OR synthesis OR "systematic review")` | 54 | 54 |
| Q8 | `title_and_abstract.search:(wetland OR wetlands OR "wetland restoration" OR peatland) AND (heat OR "heat stress" OR cooling OR "land surface temperature" OR microclimate OR "heat wave" OR "heatwave") AND ("meta-analysis" OR "systematic review" OR review OR synthesis)` | 419 | 200 |
| Q9 | `title_and_abstract.search:("wetland restoration" OR "wetland creation" OR "restored wetlands" OR "floodplain restoration" OR "wetland conservation" OR rewetting) AND (flood OR "flood risk" OR "flood attenuation" OR drought OR "water scarcity") AND (tropical OR Africa OR Asia OR "Latin America" OR "developing countries" OR "low-income" OR "middle-income" OR "Global South")` | 189 | 189 |
| Q10 | `title_and_abstract.search:(wetland OR wetlands OR floodplain OR peatland) AND ("flood" OR "flood peak" OR "flood wave" OR "flood storage") AND ("observed" OR "measured" OR "empirical" OR "monitoring" OR "gauged" OR "field data") AND (review OR synthesis OR "meta-analysis" OR "systematic review")` | 658 | 200 |
| Q11 | `title_and_abstract.search:("natural flood management" OR "runoff attenuation features" OR "working with natural processes" OR "leaky barriers" OR "online ponds" OR "offline storage") AND (evidence OR review OR "systematic review" OR effectiveness OR synthesis)` | 304 | 200 |
| Q12 | `title_and_abstract.search:(wetland OR wetlands OR peatland OR "floodplain") AND (livelihood OR livelihoods OR "food security" OR poverty OR "rural households" OR fisheries) AND (flood OR drought OR "climate shock" OR "climate variability" OR resilience) AND (review OR "systematic review" OR "meta-analysis" OR synthesis)` | 481 | 200 |
| Q13 | `title_and_abstract.search:(paludiculture OR "wet agriculture" OR "wet farming" OR "rewetted peat") AND (review OR "systematic review" OR synthesis OR "meta-analysis" OR potential OR yield)` | 279 | 200 |
| Q14 | `title_and_abstract.search:("peat fire" OR "peatland fire" OR "peat fires" OR "peatland fires") AND ("water table" OR rewetting OR "groundwater level" OR restoration OR canal) AND (review OR synthesis OR "meta-analysis" OR "systematic review" OR risk)` | 97 | 97 |
| Q15 | `title_and_abstract.search:("mangrove" OR "salt marsh" OR "coastal wetland") AND ("storm surge" OR "wave attenuation" OR "coastal flooding" OR "cyclone" OR "typhoon" OR "hurricane") AND ("meta-analysis" OR "systematic review" OR "global analysis" OR "evidence") AND (damage OR "damage reduction" OR "avoided damage" OR protection OR mortality)` | 139 | 139 |
| Q16 | `title_and_abstract.search:(wetland OR wetlands OR "wetland restoration") AND (waterlogging OR salinization OR salinisation OR "soil salinity" OR "water table rise" OR drainage) AND (agriculture OR cropland OR farmland OR "agricultural land") AND (review OR "meta-analysis" OR "systematic review" OR synthesis)` | 493 | 200 |
| Q17 | `title_and_abstract.search:("wetland restoration" OR "ecological restoration" OR "restoration project") AND (wetland OR wetlands) AND (failure OR "failed" OR "unsuccessful" OR "restoration success" OR "recovery rate") AND ("meta-analysis" OR "systematic review" OR "global" OR synthesis)` | 74 | 74 |
| Q18 | `title_and_abstract.search:(wetland OR wetlands OR peatland OR floodplain OR "riparian wetland") AND ("ecosystem services" OR "flood regulation" OR "water regulation") AND ("systematic map" OR "evidence gap map" OR "evidence and gap map" OR "systematic review")` | 103 | 103 |
| T1 | `title_and_abstract.search:(wetland OR wetlands OR floodplain OR peatland) AND ("flood" OR "flood peak" OR "flow regulation" OR "hydrological cycle" OR "water regime") AND ("169 studies" OR "the role of wetlands" OR "how wetlands affect" OR "flow regulation services" OR "do wetlands")` | 154 | 154 |
| T2 | `display_name.search:"The role of wetlands in the hydrological cycle"` | 1 | 1 |
| T3 | `display_name.search:"How Wetlands Affect Floods"` | 1 | 1 |
| T4 | `display_name.search:"The flow regulation services of wetlands"` | 1 | 1 |
| T5 | `display_name.search:"Wetlands as large-scale nature-based solutions"` | 3 | 3 |
| T6 | `display_name.search:"A restatement of the natural science evidence concerning catchment-based natural flood management"` | 3 | 3 |
| T7 | `display_name.search:"The effectiveness, costs and coastal protection benefits of natural and nature-based defences"` | 1 | 1 |
| T8 | `display_name.search:"Widespread subsidence and carbon emissions across Southeast Asian peatlands"` | 1 | 1 |
| T9 | `display_name.search:"Subsidence and carbon loss in drained tropical peatlands"` | 1 | 1 |
| T10 | `display_name.search:"Amplification of wildfire area burnt by hydrological drought in the humid tropics"` | 1 | 1 |
| T11 | `display_name.search:"Coastal wetlands reduce property damage during tropical cyclones"` | 1 | 1 |
| T12 | `title_and_abstract.search:(wetland OR wetlands OR floodplain) AND ("flood damage" OR "avoided damage" OR "property damage" OR "damage reduction" OR "insurance claims") AND (empirical OR observed OR econometric OR "panel data" OR "meta-analysis" OR review)` | 153 | 153 |
| T13 | `title_and_abstract.search:("peatland restoration" OR "peat rewetting" OR "canal blocking" OR "peatland rewetting") AND ("water table" OR hydrology OR "groundwater level") AND (effectiveness OR "meta-analysis" OR "systematic review" OR "global" OR synthesis)` | 123 | 123 |
| T14 | `title_and_abstract.search:(wetland OR wetlands OR "wetland restoration") AND (drought OR "drying" OR "water deficit" OR "low rainfall") AND ("drought refuge" OR "dry season grazing" OR "dry-season" OR "dambo" OR "fadama" OR "vlei" OR "bas-fond" OR "inland valley" OR "seasonal wetland")` | 2604 | 200 |
| T15 | `title_and_abstract.search:(dambo OR dambos OR fadama OR "bas-fond" OR "inland valley swamp" OR "vlei" OR "wetland agriculture") AND (livelihood OR "food security" OR drought OR "dry season" OR yield OR cultivation) AND (review OR synthesis OR "systematic review" OR assessment)` | 106 | 106 |
| T16 | `title_and_abstract.search:("natural flood management" OR "wetland restoration" OR "floodplain restoration" OR "wetland creation") AND ("flood peak" OR "peak flow" OR "peak discharge" OR "flood hydrograph") AND (measured OR observed OR monitored OR "catchment experiment" OR "paired catchment" OR "before-after")` | 57 | 57 |
| T17 | `title_and_abstract.search:("restored wetland" OR "restored wetlands" OR "wetland restoration" OR "constructed wetland" OR "created wetland" OR levee OR dike OR dyke OR bund OR embankment) AND (breach OR "breaching" OR overtopping OR erosion OR "structural failure" OR "dam failure" OR "berm") AND (wetland OR marsh OR peat OR floodplain)` | 1975 | 200 |
| T18 | `title_and_abstract.search:("peat" OR "peatland") AND ("subsidence") AND (tropical OR Indonesia OR Malaysia OR "Southeast Asia" OR plantation OR smallholder) AND (rate OR rates OR measured OR monitoring)` | 164 | 164 |
| T19 | `title_and_abstract.search:(wetland OR wetlands OR dambo OR floodplain OR "swamp") AND ("dry season" OR drought OR "dry-season grazing" OR "drought refuge" OR "coping strategy" OR "safety net") AND (livestock OR grazing OR pastoral OR cattle OR "dry season cropping" OR "recession agriculture" OR "flood recession") AND (Africa OR Asia OR tropical OR Sahel OR Ethiopia OR Zambia OR Tanzania OR Nigeria)` | 322 | 200 |
| T20 | `title_and_abstract.search:("wetland restoration" OR "rewetting" OR "peatland rewetting" OR "wetland creation" OR "floodplain reconnection") AND (waterlogging OR "waterlogged" OR "rising water table" OR "adjacent farmland" OR "neighbouring land" OR "land loss" OR "crop damage" OR "trade-off" OR conflict) AND (agriculture OR farmland OR farmers OR cropland)` | 124 | 124 |
| T21 | `title_and_abstract.search:("peat dam" OR "canal blocking" OR "canal block" OR "tabat" OR "check dam" OR "bund" OR "berm" OR "dike" OR "dyke") AND (peatland OR wetland OR marsh OR "peat") AND (failure OR breach OR washout OR overtopping OR damage OR maintenance OR durability OR collapse)` | 520 | 200 |
| T22 | `title_and_abstract.search:(wetland OR wetlands OR "wetland restoration" OR floodplain) AND ("flood" OR "flooding") AND ("crop loss" OR "crop damage" OR "agricultural damage" OR "yield loss" OR "harvest loss" OR "farm household") AND (review OR "meta-analysis" OR "systematic review" OR empirical OR observed)` | 35 | 35 |
| T23 | `title_and_abstract.search:("wetland" OR "wetlands" OR "peatland") AND ("ecosystem-based adaptation" OR "community-based adaptation" OR "climate adaptation") AND (Africa OR Asia OR "Latin America" OR tropical OR "low-income" OR "developing") AND ("systematic review" OR "meta-analysis" OR "evidence" OR "effectiveness")` | 73 | 73 |
| T24 | `title_and_abstract.search:("natural flood management" OR "wetland" OR "floodplain restoration") AND ("tropical" OR "Global South" OR "low- and middle-income" OR "developing countries") AND (flood OR "flood risk") AND (review OR "systematic review" OR evidence OR effectiveness)` | 278 | 200 |
| T25 | `title_and_abstract.search:("wetland" OR "marsh" OR "mangrove" OR "coastal wetland") AND ("salinity intrusion" OR "saltwater intrusion" OR "salinisation" OR "salinization") AND (agriculture OR rice OR cropland OR livelihood) AND (review OR "systematic review" OR "meta-analysis" OR evidence)` | 477 | 200 |
- **Q1–Q18** are the hazard and asset-vulnerability sweeps with a synthesis-type block (flood, drought/water storage, peat fire, coastal storm, DRR/EbA/NFM, clogging-failure-breach-subsidence, subsidence, heat, tropical/LMIC, measured-flood, NFM, livelihoods, paludiculture, peat fire × water table, coastal damage, waterlogging/salinisation, restoration failure, EGM/systematic map).
- **T1–T11** are title look-ups for seminal syntheses whose titles carry no synthesis term (Bullock & Acreman, Acreman & Holden, Kadykalo & Findlay, Thorslund, Dadson restatement, Narayan, Hoyt, Hooijer, Taufik, Sun & Carson).
- **T12–T25** are the gap-driven extensions: measured flood damages, peat rewetting hydrology, LMIC seasonal-wetland agriculture (dambo/fadama/bas-fond/inland valley), measured flood-peak catchment experiments, levee/bund/dike breach, tropical subsidence rates, dry-season grazing and drought refuge in Africa/Asia, rewetting-versus-farmland trade-offs, peat-dam/canal-block failure, flood crop damage, EbA in LMICs, tropical NFM, and salinity intrusion.
- Q8 (heat), Q10, Q11, Q12, Q13, Q16, T14, T17, T19, T21, T24 and T25 exceeded 200 hits; the first relevance-ordered page was retrieved and the overflow is recorded as a known recall limit.

## PRISMA-lite funnel
- **Retrieved:** 4,824 records over **43** OpenAlex queries (11,234 total hits before the 200/query page cap). **4,137 unique** after deduplicating on the OpenAlex work id.
- **Known-source dedup:** **5 dropped** as already in `wetland_known_sources.json` —
  - Dohong et al. 2018, *A Review of Techniques for Effective Tropical Peatland Restoration* (10.1007/s13157-018-1017-6) — matched twice, via Q3 and T13
  - Mishra/Harrison et al. 2021, *Degradation of Southeast Asian tropical peatlands and integrated strategies* (10.1111/1365-2664.13905)
  - Tan et al. 2021, *Paludiculture as a sustainable land use alternative for tropical peatlands: A review* (10.1016/j.scitotenv.2020.142111)
  - Brouwer et al. 2026, *Modeling crop suitability for rewetting landscapes in the Netherlands* (10.1016/j.agwat.2026.110190)
  - All matched on DOI; no title-only matches were needed.
- **Practice screen (step 1–2, frame + source type):** 2,020 of the unique records carried a wetland/peat/marsh/floodplain/mire/bog/fen/paludiculture/rewetting term in the title. The remainder were sea-level-rise ecology, hydrology methods, remote-sensing method papers and off-topic noise.
- **Synthesis-type title screen:** **323** of those 2,020 had a synthesis-type title. Removing the constructed-wetland water-treatment chemistry strand (pollutant/pathogen/nutrient/metal/microplastic removal, substrate, microbial, wastewater) left **265**, all of which were read at title+venue level, alongside the full per-query lists for the 12 gap-driven extensions (~250 further records).
- **Abstract / record screen (step 3–4, relevance + six-axis credibility):** **57** records.
- **Included:** **37** (cap 40). 23 syntheses (12 reviews, 5 systematic reviews, 3 meta-analyses, 1 systematic review+meta-analysis, 1 systematic map, 1 quantitative review, 1 evidence restatement, 1 global synthesis — some overlap in labelling) and **14 primaries**, each admitted against a named synthesis gap.
- **DOI round-trip:** 36/36 DOI-bearing candidates passed the Crossref check (resolved title matches the citation); citations were rebuilt from Crossref. 1 candidate (`downard_2011`) is DOI-less and must pass `verify_metadata.py verify-titles` before extraction.

## Included (37)
| candidate_id | year | type | hazards | families | basis | tier | income | OA |
|---|---|---|---|---|---|---|---|---|
| bullock_2003 | 2003 | review | flood,drought | rewet,creation,peat | measured | high | high,upper_middle,lower_middle,low | oa_direct |
| acreman_2013 | 2013 | review | flood | rewet,peat,coastal | measured | high | high,upper_middle,lower_middle,low | oa_repository |
| kadykalo_2016 | 2016 | systematic_review | flood,drought | rewet,creation | measured | high | high,upper_middle,lower_middle,low | rg_flag_for_human |
| thorslund_2017 | 2017 | review | flood,drought | rewet,creation,constructed | mixed | high | high,upper_middle,lower_middle,low | oa_direct |
| dadson_2017 | 2017 | evidence_restatement | flood | rewet,creation,peat | measured | high | high | oa_direct |
| zhu_2024 | 2024 | quantitative_review | flood | rewet,creation,peat | mixed | medium | high,upper_middle | oa_direct |
| connelly_2023 | 2023 | systematic_map | flood | rewet,creation,peat | mixed | medium | high | oa_direct |
| bagheri_2025 | 2025 | systematic_review | flood | rewet,creation,peat | mixed | medium | high,upper_middle | oa_direct |
| earl_2023 | 2023 | review | flood | rewet,creation | mixed | medium | upper_middle,lower_middle,low | oa_direct |
| knox_2022 | 2022 | review | flood | rewet | measured | medium | high,upper_middle | rg_flag_for_human |
| shuttleworth_2018 | 2019 | primary_catchment_experiment | flood | peat,rewet | measured | medium | high | oa_direct |
| gatis_2023 | 2023 | primary_catchment_experiment | flood,drought | peat,rewet | measured | medium | high | oa_direct |
| gourevitch_2026 | 2026 | primary_econometric | flood | rewet,creation | measured | high | high | paywalled_verified |
| sun_2020 | 2020 | primary_econometric | storm_surge,flood | coastal,rewet | measured | high | high | oa_repository |
| zhang_2026 | 2026 | primary_geospatial | flood | rewet,creation | mixed | high | high,upper_middle,lower_middle,low | paywalled_verified |
| rowland_2026 | 2026 | primary_observational | storm_surge,flood | coastal | measured | medium | high | oa_direct |
| shepard_2011 | 2011 | systematic_review_meta_analysis | storm_surge,flood | coastal | measured | high | high,upper_middle,lower_middle,low | oa_direct |
| narayan_2016 | 2016 | meta_analysis | storm_surge,flood | coastal | measured | high | high,upper_middle,lower_middle,low | oa_direct |
| leonardi_2017 | 2018 | review | storm_surge,sedimentation | coastal | measured | high | high,upper_middle | oa_repository |
| cahoon_2006 | 2006 | review | storm_surge,sedimentation,subsidence | coastal | measured | medium | high | rg_flag_for_human |
| silliman_2019 | 2019 | meta_analysis | storm_surge | coastal | measured | high | high,upper_middle,lower_middle | oa_repository |
| liu_2024 | 2024 | meta_analysis | storm_surge | coastal | measured | high | high,upper_middle,lower_middle,low | oa_direct |
| bring_2022 | 2022 | systematic_review | drought | rewet,creation,peat | measured | high | high | oa_direct |
| stachowicz_2022 | 2022 | primary_basin_assessment | drought | peat,rewet | mixed | medium | high,upper_middle | rg_flag_for_human |
| fynn_2015 | 2015 | review | drought | rewet | measured | high | low,lower_middle | rg_flag_for_human |
| mandishona_2022 | 2022 | review | drought,flood | rewet,creation | mixed | medium | low,lower_middle,upper_middle | rg_flag_for_human |
| verhoeven_2009 | 2009 | review | waterlogging,salinity | rewet,creation | measured | high | high,upper_middle,lower_middle,low | oa_direct |
| taufik_2017 | 2017 | primary_observational | fire,drought | peat | measured | high | lower_middle | oa_repository |
| taufik_2023 | 2023 | primary_modelled_observational | fire | peat | mixed | medium | lower_middle | oa_direct |
| alexandra_2026 | 2026 | review | fire | peat | mixed | low | lower_middle | oa_direct |
| ma_2022 | 2022 | global_synthesis | subsidence | peat | measured | high | high,upper_middle,lower_middle | oa_direct |
| hooijer_2012 | 2012 | primary_measured | subsidence | peat | measured | high | lower_middle | oa_direct |
| hooijer_2024 | 2024 | primary_measured | subsidence,fire | peat,rewet | measured | high | lower_middle | oa_direct |
| ritzema_2013 | 2014 | primary_measured | subsidence,flood | peat,rewet | measured | medium | lower_middle | oa_repository |
| fang_2022 | 2022 | review | sedimentation | constructed | measured | medium | high,upper_middle | paywalled_verified |
| maxwell_2026 | 2026 | systematic_review | flood | rewet,creation | mixed | medium | high,upper_middle,lower_middle,low | oa_direct |
| downard_2011 | 2011 | systematic_review | drought | rewet,creation | measured | low | high | oa_repository |

*`year` is the Crossref `issued` year, which differs from the print/online year for `leonardi_2017` (Crossref 2018), `ritzema_2013` (Crossref 2014) and `shuttleworth_2018` (Crossref 2019). The `candidate_id` follows the commonly cited year; resolve at SRC registration.*

## Screened out at abstract level (one-word reason; **R** = reserve)
| record | reason |
|---|---|
| *Nature-Based Engineering: A Review on Reducing Coastal Flood Risk With Mangroves* (2021); *Hydrodynamic Modelling of Mangrove-Mediated Coastal Flood Protection: A Systematic Review and Bibliometric Analysis* (2026); *Two Decades of Lessons: Systematic Review of Mangroves' Role in Tsunami Disaster Mitigation* (2026); *Can mangroves keep pace with contemporary sea level rise?* (2015) — DOIs deliberately not transcribed here, they were not re-read at record level | family: mangrove = `forest_restoration__mangrove_coastal`, not wetland_management. Hand to the forest-restoration lane |
| Hoyt et al. 2020, *Widespread subsidence and carbon emissions across Southeast Asian peatlands* (10.1038/s41561-020-0575-4) | overlap: subsidence covered by Ma 2022 (global) + Hooijer 2012/2024 (measured, tropical) **R** |
| Vuik et al. 2019, *Salt marshes for flood risk reduction: long-term effectiveness and life-cycle costs* (10.1016/j.ocecoaman.2019.01.010) | overlap with Narayan 2016 on marsh attenuation + cost; HIC (NL) **R** — the best next coastal economics item |
| Watson et al. 2016, *Quantifying flood mitigation services: Otter Creek wetlands* (10.1016/j.ecolecon.2016.05.015) | overlap: measured flood damages covered by Gourevitch 2026; single HIC catchment **R** |
| Garcia et al. 2021, *Record-breaking wildfires in the world's largest continuous tropical wetland* (10.1016/j.jenvman.2021.112870) | relevance: Pantanal fire **management** framing rather than an intervention-to-hazard effect **R** — the only non-peat tropical wetland fire item |
| *Drainage Depth, Peat Subsidence, and GHG Emissions in Tropical Peatland Agriculture: A Systematic Review and Meta-Analysis* (10.5281/zenodo.22500234, also on OSF) | credibility: unrefereed Zenodo/OSF preprint, two unaffiliated authors, no venue — provenance cannot be established from the record **R, human check** |
| Connelly et al. 2020 NFM systematic-map **protocol** (10.1186/s13750-020-00192-x); Bring et al. 2020 groundwater-storage systematic-review **protocol** (10.1186/s13750-020-00209-5) | protocol, not the review — the completed 2023 map and 2022 review are included instead |
| *Effects of farming on…*, *Wetlands Ecology and Management* ES-valuation items; *Evaluating ecosystem services for agricultural wetlands: a systematic review and meta-analysis* (10.1007/s11273-022-09883-3) | table: T6 (ES value), not a T3 hazard row **R for the T6 lane** |
| *The Economic Value of Wetland Conservation and Creation: A Meta-Analysis* (SSRN 2008); *The Values of Natural and Constructed Wetlands: A Meta-Analysis* (SSRN 2009); Danube floodplain ES meta-analysis (10.1016/j.scitotenv.2021.148509) | table: T6 economics **R for the T6 lane** |
| Constructed-wetland performance reviews (contaminant/pathogen/nutrient/metal/PFAS removal, substrates, clogging-chemistry, cold/tropical climate performance, ~40 records) | table: water-treatment performance is a T6 water-quality question; only the clogging/failure strand (Fang 2022) is a T3 asset row |
| Urban wetland cooling, urban stormwater and urban-wetland-value reviews (*Urban Wetlands: A Review on Ecological and Cultural Values*, urban thermal-stress items, ~15 records) | practice: urban, not a rural landscape NbS |
| Wetland GHG / methane / carbon-flux reviews and meta-analyses (~35 records, incl. *Carbon stock recovery and GHG shifts following wetland restoration: a global meta-analysis* 2025) | table: T6 carbon **R for the T6 lane** |
| Peat-degradation **driver** reviews (*A review of the drivers of tropical peatland degradation in South-East Asia*; Ethiopia/Nigeria/Ghana wetland-degradation reviews, ~20 records) | relevance: describes degradation, not an intervention-to-hazard effect |
| Remote-sensing / mapping / InSAR method reviews (~30 records) | relevance: method papers, no hazard effect claim |
| Wetland biodiversity, bird, fish, fisheries and vegetation-recovery syntheses (incl. *A global systematic review of the effects of hydromorphological floodplain restoration on biodiversity* 2026) | table: T6 biodiversity **R for the T6 lane** |
| Low-tier narrative "A Review on…" wetland items in predatory or ungraded venues (~45 records across Q1, Q10, Q12, Q16, Q18) | credibility: venue axis |
| Figshare "Additional file N of…" rows, peer-review reports, EGU abstracts, SSRN/Zenodo duplicates of included works (~25 records) | duplicate / not a source |

## DOI round-trip and OA
- **DOI round-trip:** 36/36 passed. Crossref resolved titles matched the OpenAlex titles for every candidate; citations (authors, container, volume, pages, year) were rebuilt from Crossref, not from search snippets. No DOI was emitted that was not read from the record itself. `downard_2011` carries **no DOI** and is acquired by TITLE; it needs `title_verified=true` before any extraction.
- **OA breakdown (Unpaywall by DOI, then web search per closed record):**
  - **`oa_direct` 21** — Bullock, Thorslund, Dadson, Zhu, Connelly, Bagheri-Gavkosh, Earl, Shuttleworth, Gatis, Rowland, Shepard, Narayan, Liu, Bring, Verhoeven, Taufik 2023, Alexandra, Ma, Hooijer 2012, Hooijer 2024, Maxwell.
  - **`oa_repository` 7** — Acreman 2013 (NERC Open Research Archive accepted manuscript, `nora.nerc.ac.uk/502685/1/N502685PP.pdf`), Sun 2020, Leonardi 2017, Silliman 2019, Taufik 2017 (WUR), Ritzema 2013 (WUR), Downard 2011 (Utah State Digital Commons).
  - **`rg_flag_for_human` 6** — Kadykalo 2016, Knox 2022, Cahoon 2006 (a USGS Publications Warehouse entry surfaced but could not be tool-resolved to a PDF), Stachowicz 2022, Fynn 2015, Mandishona 2022. ResearchGate cannot be tool-verified, so **no claim is made that no copy exists**; a human checks RG / the author or institutional copy before any institutional request.
  - **`paywalled_verified` 3** — Gourevitch 2026 (Nature Water), Zhang 2026 (Nature Sustainability), Fang 2022 (J. Cleaner Production). Unpaywall closed and web search found only landing pages; the Zenodo records attached to both Nature papers hold **code and data only**, not the article.
- **Duplicate-record caveat:** OpenAlex carries two records for the Gourevitch wetland–flood-loss paper ("…in the US", Nature Water 2023, bronze; "…in the USA", Nature Water 2026, closed). Only the 2026 record round-tripped through Crossref; resolve which is the version of record at acquisition.

## Human flags
1. **ResearchGate.** The 6 `rg_flag_for_human` rows need a human RG/author-site check before they go to institutional access. Three of them (Fynn, Mandishona, Stachowicz) are the LMIC and water-storage items we most want.
2. **Mangrove vs marsh.** `rowland_2026`, `narayan_2016` and `silliman_2019` mix tidal marsh with mangrove. Extraction must keep the marsh component under `wetland_management__coastal` and route mangrove-specific claims to `forest_restoration__mangrove_coastal` (PICOS: the practice must be evidenced per claim).
3. **Beneficiary routing.** `gourevitch_2026` and `sun_2020` measure **property/insurance** damages, i.e. `beneficiary=society` — avoided-damage value must be kept out of the poverty priority (ruleset v1.6.7).
4. **LLM-assisted screening.** `maxwell_2026` used a large language model for its literature screen with manual validation. Record this on the methodological-transparency axis; its outcome indicators are biodiversity-weighted, so hazard claims from it need care.
5. **Null and negative evidence retained (do not drop at QA):**
   - Bullock & Acreman 2003 and Acreman & Holden 2013: **headwater/upland wetlands can GENERATE flood flow** — a direct maladaptation signal against a blanket positive flood row.
   - Dadson 2017: measured flood-peak benefit is demonstrated at small scale and **unproven at catchment scale and in large events**.
   - Gatis 2023: storage and attenuation improve, **but not immediately** after restoration.
   - Taufik 2023: extreme-fire frequency and extent fell after rewetting, **but mean event duration rose**.
   - Verhoeven & Setter 2009: re-wetting imposes **waterlogging and salinity costs on adjacent cultivated land**.
   - Liu 2024: a large share of salt-marsh plantings **fail**.
6. **Severity cueing.** Several flood items distinguish ordinary from extreme events (Dadson explicitly). `context.hazard_severity` must be taken from the author's own words (`severity_cue` verbatim), never inferred.
7. **Scope to confirm.** `rowland_2026` has an all-Australian author team; the study region is not stated in the abstract. Confirm at extraction before assigning an income group.

## Coverage after this run (T3 hazard axes)
| axis | included candidates | state |
|---|---|---|
| Flood — synthesis | Bullock 2003, Acreman 2013, Kadykalo 2016, Thorslund 2017, Dadson 2017, Zhu 2024, Connelly 2023, Bagheri 2025, Earl 2023, Knox 2022, Mandishona 2022, Maxwell 2026 (12) | good, but temperate/UK-weighted; Earl 2023 is the single tropical flood synthesis |
| Flood — **measured** | Shuttleworth 2018, Gatis 2023, Gourevitch 2026, Zhang 2026, Sun 2020, Rowland 2026, Knox 2022, Bullock 2003, Kadykalo 2016 (9) | the model-reliance gap is now partly closed, but **every measured flood-peak study is HIC (UK) and every measured damage study is HIC (US/AU)** |
| Drought / water storage | Bring 2022 (SR), Kadykalo 2016, Bullock 2003, Stachowicz 2022, Fynn 2015, Mandishona 2022, Gatis 2023, Taufik 2017, Downard 2011 (9) | thin; Bring 2022 is explicitly temperate/boreal. Fynn 2015 is the only LMIC rural-livelihood drought mechanism (dry-season grazing) |
| Fire (peat) | Taufik 2017, Taufik 2023, Alexandra 2026, Hooijer 2024 (4) + 2 already known (Salmayenti 2026, Dohong 2018) | adequate and genuinely tropical/LMIC; no meta-analysis exists |
| Coastal storm surge | Shepard 2011, Narayan 2016, Silliman 2019, Sun 2020, Rowland 2026, Leonardi 2017, Cahoon 2006, Liu 2024 (8) | strong on the service, HIC-weighted on the damage side; only Rowland 2026 measures **agricultural** rather than property loss |
| Waterlogging / salinity | Verhoeven 2009 (1) | **near-empty.** No synthesis of what re-wetting does to adjacent farmland |
| Heat | **0** | **empty.** Q8 returned only urban cooling, wetland evapotranspiration methods and GHG work |
| Asset vulnerability — subsidence | Ma 2022, Hooijer 2012, Hooijer 2024, Cahoon 2006 (4) | good, and tropical/measured |
| Asset vulnerability — sedimentation / clogging | Fang 2022 (constructed), Leonardi 2017 (marsh), Cahoon 2006 (3) | thin for restored freshwater wetlands |
| Asset vulnerability — breach / structure failure | Ritzema 2013 (canal-block dams) (1) | **thin.** T21 returned mostly tidal-marsh restoration ecology, not engineering failure |
| Asset vulnerability — restoration failure | Liu 2024 (marsh planting), Maxwell 2026 (floodplain) (2) | adequate for coastal and floodplain; nothing for peatland or created wetlands |
| Families | rewetting 24 · peatland 17 · creation 15 · coastal 9 · constructed 2 | `__constructed` is barely covered on the T3 axis (by design — its literature is T6 water quality) |

## Saturation and what could not be found
- **Saturated:** flood (the same ~12 syntheses recur across Q1, Q5, Q10, Q11, Q18, T1, T16, T24 — Acreman & Holden and Bullock & Acreman appear in five queries each) and coastal storm surge (Shepard and Narayan recur in four). Late queries returned only already-seen items or mangrove material.
- **Not saturated, because the literature is effectively empty:**
  - **Heat.** No synthesis, and no primary, on wetland restoration and rural heat exposure or crop heat stress. Everything returned was urban heat-island cooling. Leave to the grey lane or accept an empty cell.
  - **Waterlogging of adjacent farmland after re-wetting.** T20 (124 hits) surfaced GHG and paludiculture papers, policy critiques and single-site European cases, no synthesis. This is the most important missing **maladaptation** axis for wetland T3 and should be a targeted grey/MEL question.
  - **Breach and structural failure of restored wetland works.** T21 (520 hits) is dominated by tidal-marsh restoration ecology; the only engineering items found were a Dutch peat-dyke geotechnical failure study (*The horizontal failure mechanism of the Wilnis peat dyke*, Géotechnique 2005, 10.1680/geot.2005.55.4.319 — HIC and very narrow, held as a reserve) and Ritzema 2013. No synthesis exists.
  - **Measured flood evidence from tropical or LMIC catchments.** Earl 2023 reviews the tropical-island NFM literature and itself reports the gap; T16 and T10 returned no tropical paired-catchment or gauged study. **Our flood rows will remain HIC-measured plus model-based unless the grey/MEL lane (IWMI, Wetlands International, Ramsar, basin authorities) fills this.**
  - **Drought in LMIC rural livelihoods.** T15 and T19 surfaced seasonal-wetland agriculture (dambo, fadama, bas-fond, inland valley) as a large but largely **descriptive, single-site and often low-tier** literature, with Fynn 2015 the one usable review. A targeted grey/CGSpace pass is the realistic route.
- **Also not run here (by design):** the multilingual lane (ES/FR/PT — Spanish and Portuguese wetland-agriculture and Pantanal/Amazon floodplain literature is likely substantial), the grey/MEL lane, the tool lane, and Lens.org. AGRIS remains a manual browser run.

## Draft SRCH row
```
search_id: wetland_management__T3__updated_lit____2026-10-14
nbs_id: wetland_management | suitability_family_id: "" | table: T3 | category: updated_lit
search_terms: OpenAlex /works filter= (verbatim, see the query table in this report): Q1-Q18 (title_and_abstract.search wetland practice block AND synthesis block AND hazard/asset block), T1-T11 (display_name.search title look-ups for seminal syntheses), T12-T25 (gap-driven extensions: measured flood damages, peat rewetting hydrology, LMIC seasonal-wetland agriculture, measured flood-peak catchment experiments, levee/bund/dike breach, tropical subsidence, dry-season grazing, rewetting-farmland trade-offs, peat-dam failure, flood crop damage, EbA in LMICs, tropical NFM, salinity intrusion); per-page=200, relevance order
screening_steps: frame|source_type|relevance|credibility_six_axis|saturation_stop
inclusion_criteria: wetland practice explicit in the record (FAM wetland_management__*; mangrove-only = forest_restoration, excluded); synthesis-first (MA/SR/systematic map/EGM/review), primaries admitted only where a hazard has no synthesis and the admission is stated per row; T3 = hazard->livelihood-outcome buffering (flood, drought, fire, waterlogging/salinity, heat, coastal storm surge) + asset vulnerability (sedimentation/clogging, breach/structure failure, subsidence, restoration failure); constructed-wetland water-treatment performance excluded (T6); known (70) excluded; HIC-only retained but flagged for transfer_class
limits: retrieve<=200/query; screen<=60 abstracts; include<=40
n_retrieved: 4824 (4137 unique) | n_screened: 57 | n_included: 37
search_date: 2026-10-14 | run_id: wet_t3_lit_2026-10-14 | searched_by: Pete/Claude | ruleset_version: v1.6.10
discovery_log_ref: wetland_management_T3_synthesis_2026-10.md
note: First T3 search for wetland_management (ledger correctly recorded T3 as never searched). Gaps left open: heat 0, waterlogging/farmland trade-off 1, breach/structure failure 1, measured flood from tropical/LMIC catchments 0. Multilingual, grey/MEL and tool lanes not run.
```
