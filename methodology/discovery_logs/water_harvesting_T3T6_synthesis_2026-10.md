# Water harvesting & conservation × T3 + T6 discovery: `updated_lit`, synthesis-first, English (2026-10-05)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `water_synthesis_first_2026-10-05_lit`, ruleset **v1.6.0**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-05: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `water_synthesis_first_2026-10-05_lit`, ledger per `--ledger`.


**Scope.** `nbs_id=water_harvesting_conservation`. Tables: T3 (hazard-impact mitigation: drought, flood/runoff, waterlogging, heat, plus asset vulnerability) and T6 (effects on T5 priorities, plus economics and adoption). This is the generic parent search (`suitability_family_id=""`); each candidate is tagged with the FAM ids it covers. **Process:** `updated_lit` only, in English. The multilingual and grey/MEL passes are run by sibling agents. **Ruleset:** v1.6.0. **Proposed run id:** `wh_t3t6_lit_2026-10-05`.

**Staging only.** Nothing was registered, queued or ledger-stamped. No PDFs were downloaded.

**Targeting (Pete 2026-10-01):** syntheses come first. Primary studies were admitted only where a hazard or target had no synthesis (1 primary admitted, Kato 2011). PADs were excluded.

**Dedup:** every record was checked against `wh_known_sources.json` (175 rows) by DOI and by a normalised-citation prefix. 9 retrieved records were already known and were dropped, among them Wolka 2018 SSA SWC review, Chen 2017 and Chen 2020 terracing MAs, Vohland 2009, Zhang 2022 CT-vs-mulch MA and Kosmowski 2018.

**Not repeated:** the archived 2026-08 WH T3/T6 SRCH rows (`_deferred/SRCH_T3_T6_deferred_2026-09.csv`, 32 rows, per family × stock/updated_lit/grey/tool). Those were **primary-oriented** title searches with no synthesis filter (e.g. `("check dam" OR "farm pond" OR "percolation tank") AND (runoff OR recharge)`). This run extends beyond them in three ways:
1. A synthesis-type block in every topic query.
2. Abstract-level (`title_and_abstract`) search.
3. Hazard-, target- and asset-vulnerability-specific blocks that the archive never ran: siltation/failure, flood peak, waterlogging, heat, yield variance, economics, adoption, gender, sand dams, spate and rooftop.

## Channel
- **Search:** OpenAlex `/works`, using `https://api.openalex.org/works?filter=<filter>&per-page=200&mailto=p.steward%40cgiar.org&select=id,doi,display_name,publication_year,type,cited_by_count,primary_location,open_access`. Results came in default relevance order, and the first page (≤200) was retrieved per query.
- **Rate limits:** HTTP 429 hit Q2, Q5, Q6, Q9 and Q21; all succeeded on retry.
- **Abstracts:** OpenAlex `abstract_inverted_index`. About 25 shortlisted records had elided abstracts; for those, screening fell back on title, venue and web-search snippets.
- **DOI checks:** Crossref `/works/<doi>` round-trip.
- **OA checks:** Unpaywall `?email=p.steward@cgiar.org`, then web search. The CGSpace DSpace REST API was used for the IWMI bitstreams.

## Verbatim queries (OpenAlex `filter=` value) · total count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| Q1 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "evidence gap map" OR "global synthesis" OR "quantitative synthesis") AND (yield OR productivity OR "crop production")` | 134 | 134 |
| Q2 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "global synthesis" OR review) AND (drought OR "dry spell" OR "yield stability" OR "yield variability" OR resilience OR "climate variability")` | 748 | 200 |
| Q3 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "evidence gap map" OR "global synthesis" OR "quantitative synthesis") AND (runoff OR "soil loss" OR erosion OR "sediment yield")` | 117 | 117 |
| Q4 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "global synthesis" OR review) AND ("soil moisture" OR infiltration OR "groundwater recharge" OR "water use efficiency" OR "water productivity")` | 470 | 200 |
| Q5 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "global synthesis" OR review) AND ("soil organic carbon" OR "carbon sequestration" OR "carbon stock")` | 133 | 133 |
| Q6 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "global synthesis" OR review) AND (income OR poverty OR welfare OR livelihood OR "food security" OR "household")` | 849 | 200 |
| Q7 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "global synthesis" OR review) AND (adoption OR disadoption OR "dis-adoption" OR uptake OR abandonment)` | 545 | 200 |
| Q8 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("cost-benefit" OR "benefit-cost" OR profitability OR "net present value" OR "internal rate of return" OR "labour requirement" OR "labor requirement" OR "establishment cost") AND (review OR "meta-analysis" OR "systematic review" OR synthesis)` | 97 | 97 |
| Q9 | `title_and_abstract.search:("check dam" OR "check dams" OR "farm pond" OR "small reservoir" OR "small dams" OR "sand dam" OR terraces OR bunds OR "water harvesting structure") AND (siltation OR sedimentation OR failure OR breach OR collapse OR "structural damage" OR "dam break") AND (review OR "meta-analysis" OR "systematic review")` | 361 | 200 |
| Q10 | `title_and_abstract.search:(terraces OR terracing OR "check dams" OR "water harvesting" OR "soil and water conservation" OR "small reservoirs") AND (flood OR "peak flow" OR "peak discharge" OR "flood mitigation") AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "global synthesis" OR review)` | 359 | 200 |
| Q11 | `title_and_abstract.search:("broad bed and furrow" OR "raised beds" OR "camber bed" OR ridges OR bunds OR "drainage furrows") AND (waterlogging OR "waterlogged" OR "excess water") AND (review OR "meta-analysis" OR "systematic review" OR vertisol)` | 67 | 67 |
| Q12 | `title_and_abstract.search:(mulch OR mulching OR "conservation tillage" OR "residue retention" OR "water harvesting") AND ("soil temperature" OR "heat stress" OR "high temperature") AND ("meta-analysis" OR "systematic review" OR "global synthesis")` | 37 | 37 |
| Q13 | `title_and_abstract.search:("rooftop rainwater harvesting" OR "roof water harvesting" OR "domestic rainwater harvesting" OR "rainwater tanks" OR cisterns) AND (review OR "systematic review" OR "meta-analysis") AND (rural OR household OR "water security" OR drought OR health OR cost)` | 228 | 200 |
| Q14 | `title_and_abstract.search:("spate irrigation" OR "floodwater harvesting" OR "flood-based farming" OR "flood based livelihood" OR "water spreading" OR jessour) AND (review OR synthesis OR "meta-analysis" OR yield OR income OR livelihood)` | 286 | 200 |
| Q15 | `title_and_abstract.search:("sand dam" OR "sand dams" OR "subsurface dam" OR "percolation tank" OR "percolation tanks" OR "managed aquifer recharge") AND (review OR "meta-analysis" OR "systematic review") AND (recharge OR "water availability" OR drought OR livelihood OR rural)` | 263 | 200 |
| Q16 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND (gender OR women OR "female-headed") AND (review OR "systematic review" OR "meta-analysis")` | 197 | 197 |
| Q17 | `title_and_abstract.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("impact evaluation" OR "randomized" OR "randomised" OR "quasi-experimental" OR "propensity score" OR "endogenous switching") AND (income OR welfare OR yield OR "food security") AND (Africa OR India OR Ethiopia OR Sahel OR Asia)` | 323 | 200 |
| Q18 | `title_and_abstract.search:(zai OR "planting pits" OR "half-moons" OR "demi-lunes" OR "semi-circular bunds" OR "stone lines" OR "cordons pierreux") AND (review OR "meta-analysis" OR synthesis OR "systematic")` | 446 | 200 |
| Q19 | `title_and_abstract.search:("mulch" OR "straw mulching" OR "residue mulch" OR "conservation tillage" OR "no-till") AND ("meta-analysis") AND (drylands OR "rainfed" OR "semi-arid" OR drought OR "soil moisture") AND (yield OR "water use efficiency")` | 110 | 110 |
| Q20 | `title_and_abstract.search:("tied ridges" OR "tied ridging" OR "ridge and furrow" OR "ridge-furrow" OR "contour ridges" OR "furrow diking") AND ("meta-analysis" OR review OR "systematic review")` | 169 | 169 |
| Q21 | `title_and_abstract.search:("farm ponds" OR "farm pond" OR "on-farm reservoirs" OR "supplemental irrigation" OR "small reservoirs") AND (review OR "meta-analysis" OR "systematic review") AND (yield OR income OR drought OR "dry spell" OR livelihood)` | 114 | 114 |
| Q22 | `display_name.search:("water harvesting" OR "rainwater harvesting" OR "runoff harvesting" OR "soil and water conservation" OR "soil water conservation" OR terracing OR "stone bunds" OR "contour bunds" OR "planting pits" OR "tied ridges" OR "check dams" OR "farm ponds" OR "micro-catchment" OR microcatchment) AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "evidence gap map" OR review)` | 515 | 200 |
| Q23 | `title_and_abstract.search:("sustainable land management" OR "soil and water conservation" OR "land restoration") AND ("evidence gap map" OR "systematic map" OR "evidence and gap map" OR "systematic review") AND (Africa OR "low- and middle-income" OR "developing countries" OR drylands)` | 45 | 45 |
| Q24 | `title_and_abstract.search:(terraces OR terracing OR "bench terraces") AND ("meta-analysis" OR "global synthesis" OR "systematic review") AND (yield OR "soil moisture" OR runoff OR "soil organic carbon" OR erosion)` | 38 | 38 |
| T1 | `display_name.search:"role of water harvesting to achieve sustainable agricultural intensification and resilience against water related shocks"` | 1 | 1 |
| T2 | `display_name.search:"Managing water in rainfed agriculture"` | 5 | 5 |
| T3 | `display_name.search:"Productivity limits and potentials of the principles of conservation agriculture"` | 1 | 1 |
| T4 | `display_name.search:"adaptive capacity of maize-based conservation agriculture systems to climate stress"` | 1 | 1 |
| T5 | `display_name.search:"Adoption of agricultural technology in the developing world: A meta-analysis"` | 2 | 2 |
| T6 | `display_name.search:"Mulching practices for reducing soil water erosion"` | 1 | 1 |
| T7 | `display_name.search:"potential for sand dams to increase the adaptive capacity of East African drylands"` | 1 | 1 |
| T8 | `title_and_abstract.search:("sand dam" OR "sand dams") AND (review OR "systematic" OR evidence OR synthesis)` | 46 | 46 |
| T9 | `title_and_abstract.search:(terraces OR terracing) AND ("soil organic carbon" OR "carbon sequestration") AND ("meta-analysis" OR "global")` | 85 | 85 |
| T10 | `title_and_abstract.search:("small reservoirs" OR "small dams" OR "farm ponds" OR "check dams") AND (sedimentation OR siltation OR "storage loss" OR "trap efficiency") AND (Africa OR India OR Ethiopia OR review OR "meta-analysis")` | 131 | 131 |
| T11 | `title_and_abstract.search:("water harvesting" OR "soil and water conservation" OR terraces OR bunds) AND ("extreme rainfall" OR "extreme events" OR "high-intensity rainfall" OR "heavy rainfall") AND (failure OR breach OR damage OR collapse OR effectiveness)` | 186 | 186 |
| T12 | `title_and_abstract.search:("soil and water conservation" OR "water harvesting" OR "sustainable land management") AND ("evidence gap map" OR "Campbell Systematic Reviews" OR 3ie OR "impact evaluation") AND (systematic OR review OR map)` | 9 | 9 |
| T13 | `title_and_abstract.search:("conservation agriculture" OR "no-till" OR mulching) AND ("drought" OR "dry years" OR "low rainfall" OR aridity OR "heat stress") AND ("meta-analysis" OR "meta-regression") AND (yield)` | 92 | 92 |
| T14 | `title_and_abstract.search:("soil and water conservation" OR "water harvesting" OR terraces OR "stone bunds") AND ("yield variability" OR "yield stability" OR "risk reduction" OR "downside risk" OR "production risk")` | 207 | 200 |
| T15 | `title_and_abstract.search:("rainwater harvesting" OR "water harvesting") AND ("cost-benefit" OR "benefit-cost" OR "net present value" OR "economic analysis") AND (Africa OR India OR Ethiopia OR Kenya OR Sahel OR "semi-arid") AND (review OR "meta-analysis" OR synthesis OR "multi-site" OR "across sites")` | 12 | 12 |
| T16 | `title_and_abstract.search:("broad bed and furrow" OR "broad-bed and furrow" OR "BBF") AND (Vertisol OR vertisols OR waterlogging)` | 86 | 86 |
| T17 | `title_and_abstract.search:(terraces OR terracing OR "check dams" OR "soil and water conservation measures") AND ("flood peak" OR "peak discharge" OR "peak flow" OR "flood attenuation" OR "flood regulation") AND (meta-analysis OR review OR catchment OR watershed)` | 203 | 200 |

- Q1–Q24 are topic, hazard and target sweeps; Q22 is the title-only control.
- T1–T7 are title look-ups for seminal syntheses whose titles may lack the synthesis term.
- T8–T17 are hazard and asset-vulnerability extensions: sand dams, terrace SOC, reservoir siltation, extreme-rainfall failure, EGM/3ie, CA × drought/heat, yield variance, WH economics, BBF/waterlogging and flood peak.

### Web searches (verbatim), for OA recovery
1. `"The role of water harvesting to achieve sustainable agricultural intensification and resilience against water related shocks" Dile pdf`
2. `"Managing water in rainfed agriculture—The need for a paradigm shift" Rockström pdf`
3. `"Soil and water conservation technologies: a buffer against production risk" Kato Ringler pdf`
4. `"Balancing watershed and local scale impacts of rain water harvesting in India" Glendenning pdf`
5. `"Effects of farming terraces on hydrological and geomorphological processes. A review" Arnáez pdf`
6. `Adimassu "Impacts of Soil and Water Conservation Practices on Crop Yield, Run-off, Soil Loss and Nutrient Loss in Ethiopia" pdf cgspace OR iwmi`
7. `Bouma "Assessing the returns to water harvesting: A meta-analysis" pdf`
8. `Stavi "Water runoff harvesting systems for restoration of degraded rangelands: A review of challenges and opportunities" pdf`
9. `"Economic and environmental rehabilitation through soil and water conservation, the case of Tigray" pdf`
10. `"Spatiotemporal effects of soil and water conservation measures on soil organic carbon" meta-analysis China pdf`
11. `Lucas-Borja "Check dams worldwide: Objectives, functions, effectiveness and undesired effects" pdf`
12. `Bouma Hegde Lasage "returns to water harvesting" research.vu.nl OR pure pdf`
13. `"Assessing the returns to water harvesting" Bouma 2016 pdf free full text`
14. `Glendenning van Ogtrop Mishra Vervoort rain water harvesting India review ses.library.usyd.edu.au OR pdf`
15. `Arnáez Lana-Renault Lasanta "farming terraces" review 2015 digital.csic.es OR unirioja pdf`
16. `IFPRI discussion paper 871 Kato Ringler Yesuf Bryan soil water conservation production risk Nile Basin pdf ebrary.ifpri.org`
17. `Haile Gebremeskel 2017 "soil and water conservation" Tigray "Journal of Arid Environments" economic environmental rehabilitation researchgate OR repository`

## PRISMA-lite funnel
- **Retrieved:** 4,717 records over 41 OpenAlex queries. **3,570 were unique** after deduplicating on DOI or normalised title.
- **Known:** 9 matched `wh_known_sources.json` and were dropped.
- **Title screen:** 1,092 records had a synthesis-type title (meta / systematic / review / synthesis / map / global / overview / lessons). These were narrowed to about 230 by a WH-practice term and by removing urban, stormwater, atmospheric-water, plastic-film, clinical and Quaternary-geology noise. Q13, Q14 and Q18 were very noisy: "cistern", "water spreading" and "pit" pull medical and materials papers.
- **Abstract screen:** 62 records (the shortlist is `scratch short.txt`; the abstract cap was set at 62, slightly above the 50–60 norm, to cover rooftop and spate).
- **Included:** **30** (cap 30). By type:
  - 11 meta-analyses or meta-regressions
  - 4 systematic reviews
  - 12 structured reviews
  - 2 IWMI synthesis reports (DOI-registered)
  - 1 primary (Kato 2011)
- **DOI checks:** 30/30 passed the Crossref round-trip; there were no DOI failures.

## Included (30)
| candidate_id | type | tables | families | tier | OA |
|---|---|---|---|---|---|
| dile_2013 | review | T3|T6 | in_situ, micro_catchment, runoff_catchment | high | rg_flag_for_human |
| rockstrom_2010 | review | T3|T6 | in_situ, micro_catchment, runoff_catchment | high | rg_flag_for_human |
| biazin_2012 | review | T3|T6 | in_situ, micro_catchment, runoff_catchment | medium | oa_repository |
| zougmore_2014 | review | T3|T6 | in_situ, micro_catchment, terracing | high | oa_direct |
| steward_2018 | meta_regression | T3|T6 | in_situ | high | oa_direct |
| corbeels_2020 | meta_analysis | T3|T6 | in_situ | high | oa_repository |
| fan_2023 | meta_analysis | T3|T6 | in_situ | medium | oa_direct |
| kato_2011 | primary_econometric | T3 | in_situ, terracing | medium | rg_flag_for_human |
| makmensah_2021 | meta_analysis | T3|T6 | in_situ | medium | oa_direct |
| tefera_2024 | meta_analysis | T3|T6 | in_situ, micro_catchment | medium | oa_direct |
| nguru_2026 | systematic_review | T3 | in_situ, micro_catchment, terracing | medium | oa_direct |
| silva_2026 | systematic_review | T3|T6 | runoff_catchment, rooftop | medium | oa_direct |
| glendenning_2012 | review | T6 | runoff_catchment | high | rg_flag_for_human |
| ritchie_2021 | review | T3|T6 | runoff_catchment | medium | oa_direct |
| saruchera_2019 | review | T3|T6 | runoff_catchment | medium | oa_repository |
| venot_2012 | review | T6 | runoff_catchment | medium | oa_repository |
| arnaez_2015 | review | T3|T6 | terracing | medium | rg_flag_for_human |
| lucasborja_2021 | review | T3|T6 | runoff_catchment | high | oa_repository |
| frankl_2021 | review | T3|T6 | runoff_catchment, terracing | high | oa_direct |
| wei_2016 | review | T3|T6 | terracing | high | oa_repository |
| adimassu_2016 | review | T6 | in_situ, terracing | high | rg_flag_for_human |
| bouma_2016 | meta_analysis | T6 | in_situ, micro_catchment, runoff_catchment | high | rg_flag_for_human |
| zhang_2026 | meta_analysis | T6 | in_situ, terracing | medium | oa_repository |
| ruzzante_2021 | meta_analysis | T6 | in_situ, micro_catchment, runoff_catchment, terracing | high | oa_direct |
| malan_2024 | systematic_review | T6 | in_situ, terracing | medium | oa_direct |
| gonzalezsanchez_2019 | meta_analysis | T6 | in_situ | medium | oa_repository |
| moges_2011 | review | T6 | runoff_catchment, rooftop | medium | oa_repository |
| stavi_2020 | review | T6 | micro_catchment, runoff_catchment | medium | rg_flag_for_human |
| mekonnen_2014 | review | T6 | runoff_catchment, terracing | medium | oa_repository |
| gebremeskel_2018 | review | T6 | in_situ, terracing, runoff_catchment | medium | paywalled_verified |

## Screened out at abstract level (one-word reason; **R** = reserve)
| record | reason |
|---|---|
| Pittelkow 2015 FCR "When does no-till yield more" (10.1016/j.fcr.2015.07.020) · Pittelkow 2015 Nature (10.1038/nature13809) | overlap: CA aridity is covered by Steward 2018/Corbeels 2020, and these are HIC-heavy **R** |
| Rusinamhodzi 2011 CA maize MA (10.1007/s13593-011-0040-2) · Bayala 2012 W Africa CA synthesis (10.1016/j.jaridenv.2011.10.011) | overlap: CA saturated **R** |
| Qin 2015 mulching MA (10.1038/srep16210) · ridge-furrow maize MA 2020 (10.1016/j.agwat.2020.106144) · ridge-tillage global MA 2026 (10.1016/j.agwat.2026.110332) | practice: plastic-film confound, China **R** |
| Kubiku 2022 Zimbabwe sorghum RWH MA (10.1016/j.heliyon.2022.e09164) | overlap: covered by Tefera 2024 **R** |
| Prosdocimi 2016 mulching erosion review (10.1016/j.earscirev.2016.08.006) | superseded by Fan 2023 MA **R** |
| Deng 2021 terracing pros/cons (10.1016/j.iswcr.2021.03.002) · Chapagain 2017 terrace agronomy | overlap with Wei 2016 **R** |
| Tarolli 2014 terraced landscapes hazard (10.1016/j.ancene.2014.03.002) | HIC (Europe abandonment); asset-vulnerability **R** |
| Abbasi 2019 check dams examples (10.1016/j.scitotenv.2019.04.249) | overlap with Lucas-Borja 2021 **R** |
| Maetens 2012 ESR Europe/Mediterranean plot runoff | HIC **R** |
| Castelli 2022 sand dams STOTEN (10.1016/j.scitotenv.2022.156126) · Ryan 2016 sand dams drought (10.1007/s10113-016-0938-y) | overlap with Ritchie 2021; Ryan = primary drought evidence **R** |
| Owusu 2022 small reservoirs W Africa review (10.3390/w14091440) | overlap with Saruchera 2019 **R** |
| Okello 2024 NbS ASALs SR (10.1016/j.nbsj.2024.100172) | practice: multi-NbS, not isolated **R** |
| Wolka 2026 PSWC adoption SR Ethiopia (10.1007/s43621-026-04391-3) · SLM adoption SR SSA 2026 (10.3389/fsufs.2026.1829066) · Zondo 2024 CSWM adoption SLR | overlap with Ruzzante 2021; Wolka = only dis-adoption/WTP synthesis **R** |
| Jiru 2022 Ethiopia SWC soil props (10.1186/s13717-022-00364-2) | overlap with Adimassu **R** (SOC alternative) |
| Chen 2020 STOTEN red-soil SWCM MA · Rajbanshi 2022 conservation practices MA · Loess Plateau erosion SR 2020 · SWC erosion-plots MA China 2026 | overlap: China-only erosion, Wei/Fan kept **R** |
| Chen 2020 "Does terracing enhance SOC" (10.1016/j.scitotenv.2020.137751) | overlap with Zhang 2026 **R** |
| Basche 2019 infiltration MA (10.1371/journal.pone.0215702) | HIC: no-till/cover crops **R** |
| Lepcha 2024 rooftop RWH review (10.1016/j.gsd.2024.101305) · Moges/rooftop microbial reviews (npj 2019, AQUA 2006) | credibility (narrative, India) **R**; microbial = health outcome, not a T5 target |
| Pavelic 2012 floodwater harvesting Thailand (10.1016/j.jhydrol.2012.08.007) | method: modelling, single country. Only spate/flood-storage item **R** |
| Fox 2005 WH supplemental-irrigation risk/economics Burkina/Kenya (10.1016/j.agsy.2004.04.002) | primary: economics covered by Bouma/Venot/Moges **R** |
| Sinore 2024 Ethiopia adaptation MA Heliyon (10.1016/j.heliyon.2024.e26103) · Asefa 2025 Ethiopia CSLM SR | relevance: adaptation-strategy prevalence, not WH effect sizes |
| Diop 2022 SWC Africa state of play (10.3390/su142013425) | credibility: narrative overview **R** |
| Ageing water storage infrastructure (UNU 2021) · reservoir sedimentation India budget | practice: large dams |
| Rooftop/urban RWH sizing, economics and building SLRs (RCR 2020, AQUA 2016, Utilities Policy 2022, Malaysia/UiTM) | practice: urban/building |
| MAR reviews (contaminants, MENA, Brazil, Gulf) | practice: engineered MAR, not WH NbS |
| Plastic-mulch MAs (STOTEN 2018, etc.) | practice: plastic film, not an NbS |
| Low-tier narrative reviews (IJCMAS, IJIRSET, AJAR, "A Review on…" Ethiopia/Kenya ≈20) | credibility: predatory/low-tier venue |
| Campbell protocol cl2.129 · peer-review records (PeerJ) · SSRN/EGU duplicates | protocol / duplicate |

## DOI round-trip and OA
- **DOI round-trip:** 30/30 matched (normalised Crossref title = OpenAlex title). Citations were rebuilt from Crossref fields.
  - The Dile 2013 Crossref record has no container title, so the container was patched from SEI and web-search metadata (AEE 181:69–79).
  - The Crossref issued year differs from the print year for Adimassu (2016 online / 2017 print), Stavi (2020), Mekonnen (2014) and Zhang (2026). Candidate ids follow Crossref.
  - The `haile_2017` placeholder was renamed **gebremeskel_2018**: per Crossref, the first author is Gebremeskel, G.
- **OA breakdown:**
  - **oa_direct 11:** Zougmoré, Steward, Fan, Mak-Mensah, Tefera, Nguru, Silva, Ritchie, Frankl, Ruzzante, Malan.
  - **oa_repository 10:** Biazin (WUR), Corbeels (Göttingen), Saruchera and Venot (CGSpace bitstreams), Lucas-Borja (HAL), Wei (accepted manuscript at ScienceDirect), Gonzalez-Sanchez (Córdoba Helvia), Moges and Mekonnen (WUR), and Zhang (SSRN **preprint** — not the version of record).
  - **rg_flag_for_human 8:** Dile, Rockström (CGIAR MEL "View/Open" not tool-verified), Kato (earlier IFPRI DP 871 version is free but is a different item), Glendenning, Arnáez, Adimassu (ICRISAT OAR copy is restricted to ICRISAT users), Bouma and Stavi.
  - **paywalled_verified 1:** Gebremeskel 2018. Unpaywall is closed and web search found no copy; RG cannot be tool-verified.
- **Direct-PDF caveat:** the direct PDF links for PeerJ and OUP returned 403 to scripted fetches (bot-block), so `oa_url` = DOI landing and they should be acquired in a browser. The old iwmi.cgiar.org PDF links now redirect to a CGSpace search, and have been replaced with CGSpace bitstream URLs.

## Human flags
1. **COI, internal authorship.** `steward_2018` (Pete is first author) is the only heat-hazard synthesis. Record it on the independence axis.
2. **Grey-sibling overlap.** `saruchera_2019` and `venot_2012` are IWMI reports with DOIs, so the grey/MEL agent may also surface them. Dedup at queue merge.
3. **Preprint vs version of record.** `zhang_2026`: only the SSRN preprint is free. Extraction must cite the cached version; for the VoR, use institutional access.
4. **Claim-scope risk.**
   - Conservation agriculture items (`steward_2018`, `corbeels_2020`, `gonzalezsanchez_2019`) speak to `conservation_tillage_mulch` only and must not set in-situ WH rows for bunds or pits.
   - Ruzzante adoption drivers route to `use_role=operational_risk`, not T6.
5. **Transfer.** Fan 2023, Arnáez 2015, Wei 2016 and Lucas-Borja 2021 are global or HIC/China-heavy, so their LMIC transfer class needs care.
6. **Null/negative evidence retained:**
   - Glendenning 2012: watershed-scale downstream losses and thin field evidence.
   - Malan 2024: paucity of causal socioeconomic evidence.
   - Corbeels 2020: limited CA yield gains.
   - Adimassu 2016: yield losses on bund area.
7. **ResearchGate.** RG-flagged rows need a human RG check before they go to institutional access.

## Coverage (synthesis-grade evidence after this run)
| axis | covered by | gap |
|---|---|---|
| T3 drought / dry spell | 19 (Dile, Rockström, Biazin, Zougmoré, Tefera, Bouma, Corbeels, Steward; Kato = yield variance) | yield **stability**: no synthesis; only the Kato primary |
| T3 flood / runoff attenuation | 7 (Fan, Arnáez, Lucas-Borja, Wei, Frankl, Tefera, Mekonnen) | **flood-peak / downstream flood attenuation**: no synthesis. Runoff-coefficient reductions only (plot/field) |
| T3 waterlogging | **0** | none. T16 (BBF/Vertisol) returned only primaries; flag for grey/ILRI-ICRISAT Vertisol pass |
| T3 heat | 1 (Steward 2018, CA only) | no synthesis for bunds, pits or ponds × heat |
| Asset vulnerability | Lucas-Borja (check dam filling/failure), Frankl (failure rates), Ritchie (sand-dam failure), Saruchera (reservoir sedimentation/maintenance), Arnáez + Wei (terrace collapse), Moges (pond seepage/siltation) | bund breaching in extreme rainfall: no synthesis (T11 returned primaries only); Tarolli 2014 is reserve (HIC) |
| T6 production_gap | 19 | adequate |
| T6 water_stress (moisture, infiltration, recharge) | 14 (Glendenning = recharge) | groundwater recharge quantification for percolation tanks is review-level only |
| T6 soil_erosion_risk | 12 | adequate (China/HIC-heavy MAs; Adimassu and Tefera are LMIC) |
| T6 water_quality_risk (sediment) | 5 (Mekonnen, Lucas-Borja, Fan, Ritchie, Adimassu) | thin |
| T6 carbon | 4 (Zhang China, Gonzalez-Sanchez CA, Wei, Zougmoré) | no LMIC synthesis of SOC under bunds or terraces |
| T6 rural_poverty / income | 11 (Malan = paucity; Bouma; Venot; Dile) | causal evidence thin (Malan) |
| Economics (cost/ha, BCR, labour) | Bouma, Venot, Moges, Adimassu (BCR), Zougmoré | labour-days synthesis: none; adoption/dis-adoption via Ruzzante (+ Wolka 2026 reserve) |
| Gender | **0** | Q16 returned no WH-specific gender synthesis; leave to the grey/MEL sibling |
| Families | in_situ 18 · runoff_catchment 16 · terracing 12 · micro_catchment 9 · rooftop 2 · **spate 0** | spate: no peer-reviewed synthesis (Pavelic 2012 is reserve; spate guidelines are already known grey). Rooftop: only Silva 2026 + Moges (household) |

## Saturation
Saturation was reached for in-situ, terracing and runoff-catchment on drought, erosion and yield. Late queries (Q19–Q24, T13–T17) returned already-seen syntheses or China/HIC duplicates; for example, Wei 2016 and Arnáez 2015 recur in 5 queries each. Saturation was not reached for waterlogging, heat, flood-peak, gender and spate, because the peer-reviewed synthesis literature is effectively empty for them; the remaining leads are grey (sibling pass) or primary. The cap of 30 binds, and the reserve list above holds about 25 next-best items.

## Draft SRCH rows (one per table)
```
search_id: water_harvesting_conservation__T3__updated_lit____2026-10-05
nbs_id: water_harvesting_conservation | suitability_family_id: "" | table: T3 | category: updated_lit
search_terms: OpenAlex /works filter= (verbatim, see wh_T3T6_lit_report.md table): Q1–Q24 (title_and_abstract.search WH practice block AND synthesis block AND hazard/target block; Q22 display_name.search control) + T1–T17 title look-ups/hazard extensions; per-page=200, relevance order
screening_steps: frame|source_type|relevance|credibility_six_axis|saturation_stop
inclusion_criteria: WH sub-practice explicit (FAM water_harvesting__*); synthesis-first (MA/SR/map/EGM/review), primaries only where a hazard has no synthesis; T3 = hazard→outcome buffering (drought/dry spell, runoff/flood, waterlogging, heat) + asset vulnerability (structure failure/siltation); PADs excluded; known (175) excluded; HIC-only = reserve
limits: retrieve<=200/query; screen<=62 abstracts; include<=30 across T3+T6
n_retrieved: 4717 (3570 unique) | n_screened: 62 | n_included: 18   # rows with T3 in tables
search_date: 2026-10-05 | run_id: wh_t3t6_lit_2026-10-05 | searched_by: Pete/Claude | ruleset_version: v1.6.0
discovery_log_ref: water_harvesting_conservation_T3T6_synthesis_2026-10.md
note: Extends archived 2026-08 primary-oriented SRCH rows (not repeated). Gaps: waterlogging 0, heat 1 (CA, COI), flood-peak 0 synthesis. 429s retried.

search_id: water_harvesting_conservation__T6__updated_lit____2026-10-05
nbs_id: water_harvesting_conservation | suitability_family_id: "" | table: T6 | category: updated_lit
search_terms: (same verbatim query set as T3 row; shared run)
screening_steps: frame|source_type|relevance|credibility_six_axis|saturation_stop
inclusion_criteria: WH sub-practice explicit; synthesis-first; T6 = effects on T5 priorities (production_gap, water_stress, soil_erosion_risk, rural_poverty, carbon_sequestration_potential, water_quality_risk) + economics (cost/ha, BCR, labour) + adoption (→ operational_risk); PADs excluded; known excluded
limits: retrieve<=200/query; screen<=62 abstracts; include<=30 across T3+T6
n_retrieved: 4717 (3570 unique) | n_screened: 62 | n_included: 28   # rows with T6 in tables
search_date: 2026-10-05 | run_id: wh_t3t6_lit_2026-10-05 | searched_by: Pete/Claude | ruleset_version: v1.6.0
discovery_log_ref: water_harvesting_conservation_T3T6_synthesis_2026-10.md
note: 30 unique candidates total (16 T3|T6, 12 T6-only, 2 T3-only). Gender 0, spate 0, labour-days 0. 2 IWMI reports may duplicate grey sibling.
```
