# Agroforestry × T6 discovery — `updated_lit`, synthesis-first (English) — 2026-10-02

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `probe_af_t6_lit_2026-10-02`, ruleset **v1.6.0**, synthesis-first rule (Pete 2026-10-01). SRCH rows carry the same run_id; candidates → `pipeline/acquisition_queue.csv` (status `pending`). 24 queued; ERA database HELD (dataset intake adapter pending; co-author COI noted).


**Scope:** `nbs_id=agroforestry` × T6 (NbS scorecard: effects on the T5 priorities, plus economics and adoption). This is the generic parent search (`suitability_family_id=""`), and each candidate is tagged with the FAM ids it covers. **Process:** `updated_lit` only, in English only. The multilingual and grey/MEL passes are run by sibling agents. **Ruleset:** v1.6.0. **Run id (proposed):** `probe_af_t6_lit_2026-10-02`. Everything is staging-only: nothing was registered, queued or ledger-stamped, and no PDFs were downloaded.
**Targeting rule (Pete 2026-10-01):** meta-analyses, SRs, systematic maps, EGMs and reviews come first; primary studies only where a target has no synthesis. In this run no primary study was needed or admitted. PADs are excluded.
**Starting seeds (from the T3 probe screen-outs):** Kuyah 2019, Niether 2020, Reed 2017, ERA, the SSA welfare SR-MA 2026 (T3 reserve), De Beenhouwer 2013, and the silvopasture/linear productivity review 2024. All 7 were included.
**Dedup:** every record was checked against `agroforestry_known_sources.json` (134 rows: 52 SRC + 82 queue, including the 20 T3 probe candidates) by DOI and normalised citation. No included candidate is known. Known items skipped included Castle 2021, De Stefano 2018 SOC MA, Pattanayak 2003, Giger 2015 WOCAT economics, Begum 2025 systematic map and Zhu 2019.

Deliverable: `agroforestry_T6_lit_candidates.json` (**25 candidates**: 24 lit + 1 tool/database).

---

## Channel
- **Search:** OpenAlex `/works`, using `https://api.openalex.org/works?filter=<filter>&per-page=200&mailto=p.steward%40cgiar.org&select=id,doi,display_name,publication_year,type,cited_by_count,primary_location,open_access`. Results were in default relevance order; the first page (≤200) was retrieved for each query.
- **Abstracts:** fetched from OpenAlex `abstract_inverted_index`. Where the publisher had elided the abstract, Semantic Scholar `/graph/v1/paper/DOI:` was used for 8 DOIs.
- **DOI checks:** Crossref `/works/<doi>` round-trip.
- **OA checks:** Unpaywall `?email=p.steward@cgiar.org`, then web search for OA recovery.
- **ERA:** web search. `era.ccafs.cgiar.org` refused the connection (ECONNREFUSED) on 2026-10-02.
- **Not re-run:** none of the T3 probe's Q1–Q18, T1 or T2 queries.

## Verbatim queries (OpenAlex `filter=` value) · total count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| Q1 | `title_and_abstract.search:(agroforestry OR silvopastoral OR silvopasture OR "alley cropping" OR "trees on farms" OR parkland OR "shade coffee" OR "cocoa agroforestry" OR homegarden) AND ("meta-analysis" OR "systematic review" OR "global synthesis") AND (yield OR productivity OR "soil organic carbon" OR biodiversity OR income OR erosion OR "ecosystem services")` | 495 | 200 |
| Q2 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "trees on farms" OR "tree-based farming" OR homegarden) AND (income OR poverty OR welfare OR livelihood OR "household wealth" OR "food security") AND ("meta-analysis" OR "systematic review" OR "evidence gap map" OR "systematic map")` | 252 | 200 |
| Q3 | `title_and_abstract.search:(agroforestry OR "tree planting" OR "trees on farms" OR silvopastoral OR "shea" OR "farmer managed natural regeneration") AND (gender OR women OR "intra-household") AND (review OR "systematic review" OR "meta-analysis" OR synthesis)` | 456 | 200 |
| Q4 | `title_and_abstract.search:(agroforestry OR "trees on farms" OR silvopastoral OR "farmer managed natural regeneration" OR "fertilizer trees") AND (adoption OR "dis-adoption" OR disadoption OR abandonment OR uptake) AND ("meta-analysis" OR "systematic review" OR review)` | 833 | 200 |
| Q5 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "trees on farms" OR "farmer managed natural regeneration" OR windbreak) AND ("cost-benefit" OR "benefit-cost" OR profitability OR "net present value" OR "establishment cost" OR "return on investment" OR "financial analysis" OR "economic analysis") AND (review OR "meta-analysis" OR "systematic review" OR synthesis)` | 217 | 200 |
| Q6 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "alley cropping" OR "vegetative buffer" OR hedgerow OR "contour hedgerow" OR windbreak) AND ("water quality" OR nitrate OR "nitrogen leaching" OR "nutrient loss" OR phosphorus OR "sediment yield") AND ("meta-analysis" OR "systematic review" OR review)` | 224 | 200 |
| Q7 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "trees on farms" OR parkland OR "tree cover") AND (infiltration OR "groundwater recharge" OR "soil moisture" OR "water use efficiency" OR "water productivity" OR evapotranspiration OR "water yield") AND ("meta-analysis" OR "systematic review" OR "global synthesis" OR review)` | 256 | 200 |
| Q8 | `title_and_abstract.search:(agroforestry OR "contour hedgerow" OR "hedgerow intercropping" OR "alley cropping" OR "vegetative barrier" OR "grass strip" OR silvopastoral) AND (erosion OR "soil loss" OR runoff) AND ("meta-analysis" OR "systematic review" OR review)` | 522 | 200 |
| Q9 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "trees on farms" OR "shade coffee" OR "cocoa agroforestry" OR homegarden) AND ("biomass carbon" OR "carbon stock" OR "carbon sequestration" OR "aboveground carbon") AND ("meta-analysis" OR "global synthesis" OR "systematic review" OR "global estimate")` | 123 | 123 |
| Q10 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "shade coffee" OR "cocoa agroforestry" OR homegarden OR "trees on farms" OR hedgerow) AND (biodiversity OR "species richness" OR pollinator OR "natural enemies" OR birds OR "pest control") AND ("meta-analysis" OR "systematic review" OR "global synthesis")` | 265 | 200 |
| Q11 | `title_and_abstract.search:("farmer managed natural regeneration" OR FMNR OR parkland OR "Faidherbia albida" OR "assisted natural regeneration" OR regreening) AND (yield OR income OR "food security" OR biomass OR "soil fertility" OR livelihood) AND (review OR "meta-analysis" OR synthesis OR "impact evaluation")` | 150 | 150 |
| Q12 | `title_and_abstract.search:(silvopastoral OR silvopasture OR "trees in pastures" OR "fodder trees" OR "intensive silvopastoral") AND ("meta-analysis" OR "systematic review" OR "global review" OR review) AND (milk OR "liveweight gain" OR productivity OR "animal performance" OR "methane" OR income OR "carbon")` | 273 | 200 |
| Q13 | `title_and_abstract.search:(homegarden OR "home garden" OR "homegardens" OR "multistrata") AND (nutrition OR "dietary diversity" OR income OR "food security" OR biodiversity OR carbon) AND (review OR "meta-analysis" OR "systematic review")` | 265 | 200 |
| Q14 | `title_and_abstract.search:(agroforestry OR "trees on farms" OR "tree tenure") AND (indigenous OR "Indigenous Peoples" OR "local communities" OR "customary tenure" OR "land tenure" OR "tree tenure") AND ("systematic review" OR review OR "meta-analysis")` | 543 | 200 |
| Q15 | `title_and_abstract.search:("fertilizer trees" OR "fertiliser trees" OR "improved fallow" OR "alley cropping" OR Gliricidia OR "Leucaena" OR "evergreen agriculture") AND ("meta-analysis" OR "systematic review" OR "quantitative synthesis" OR review) AND (yield OR maize OR "soil fertility" OR "nitrogen")` | 169 | 169 |
| Q16 | `title_and_abstract.search:(agroforestry OR "trees on farms" OR silvopastoral OR "fertilizer trees" OR "tree cover") AND ("yield stability" OR "yield variability" OR "production risk" OR "income diversification" OR "income stability")` | 322 | 200 |
| Q17 | `title_and_abstract.search:(trees OR forests OR agroforestry) AND ("dietary diversity" OR "diet quality" OR nutrition OR "child health") AND ("systematic review" OR "meta-analysis")` | 477 | 200 |
| Q18 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "trees on farms") AND ("cost-effectiveness" OR "cost per hectare" OR "cost per tonne" OR "abatement cost" OR "marginal abatement" OR "carbon price" OR "USD per tCO2")` | 109 | 109 |
| Q19 | `title_and_abstract.search:("Evidence for Resilient Agriculture" OR "ERA database" OR "ERAg") AND (agriculture OR agroforestry OR "climate-smart")` | 15 | 15 |
| Q20 | `title_and_abstract.search:(agroforestry OR "trees on farms" OR silvopastoral OR "fertilizer trees" OR "improved fallow") AND (disadoption OR "dis-adoption" OR "discontinued adoption" OR "abandonment of trees" OR "non-adoption" OR "adoption intensity") AND (review OR "meta-analysis" OR "systematic")` | 11 | 11 |
| Q21 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "tree-based") AND ("meta-analysis" OR "systematic review") AND (profitability OR "economic returns" OR "net returns" OR "gross margin" OR "financial performance" OR "benefit-cost")` | 35 | 35 |
| Q22 | `title_and_abstract.search:(agroforestry OR "tree-based" OR "trees on farms" OR silvopastoral) AND (gender OR women) AND ("systematic review" OR "meta-analysis" OR "evidence review" OR "systematic map")` | 61 | 61 |
| Q23 | `display_name.search:(agroforestry OR silvopastoral OR silvopasture OR "alley cropping" OR parkland OR homegarden OR "shade coffee" OR "cocoa agroforestry" OR "trees on farms") AND ("meta-analysis" OR "systematic review" OR "systematic map" OR "evidence gap map")` | 148 | 148 |
| T1 | `display_name.search:"maize yield response to woody and herbaceous legumes"` | 1 | 1 |
| T2 | `display_name.search:"Revisiting IPCC Tier 1 coefficients for soil organic and biomass carbon storage in agroforestry"` | 4 | 4 |
| T3 | `display_name.search:"Which agroforestry options give the greatest soil and above ground carbon benefits"` | 1 | 1 |
| T4 | `display_name.search:"Carbon sequestration and net emissions of CH4 and N2O under agroforestry"` | 1 | 1 |
| T5 | `display_name.search:"Land-based measures to mitigate climate change: potential and feasibility by country"` | 1 | 1 |
| T6 | `display_name.search:"Trees for life: The ecosystem service contribution of trees to food production and livelihoods"` | 1 | 1 |
| T7 | `display_name.search:"Effects of soil and water conservation techniques on crop yield, runoff and soil loss in Sub-Saharan Africa"` | 1 | 1 |
| T8 | `display_name.search:"role of knowledge, attitudes and perceptions in the uptake of agricultural and agroforestry innovations"` | 1 | 1 |
| T9 | `display_name.search:"Agroforestry: a refuge for tropical biodiversity"` | 2 | 2 |
| T10 | `display_name.search:"Effects of changing farming practices in African agriculture"` | 1 | 1 |
| T11 | `display_name.search:"Large climate mitigation potential from adding trees to agricultural lands"` | 1 | 1 |
| T12 | `display_name.search:"Global agroforestry adoption: A meta-analysis of econometric-based studies"` | 1 | 1 |

(Q1–Q19 are topic and target sweeps. Q20–Q22 add adoption, economics and gender. Q23 is the title-only control. T1–T12 are title look-ups for seminal syntheses that the abstract queries could miss, because their titles lack the practice term. Example: Sileshi 2008 says "woody legumes", not "agroforestry".)

### Web searches (verbatim), for ERA and OA recovery
1. `Evidence for Resilient Agriculture ERA dataset agroforestry dataverse github ERAg version`
2. `"Agroforestry boosts soil health in the humid and sub-humid tropics" Muchane 2020 pdf`
3. `"Meta-analysis of maize yield response to woody and herbaceous legumes in sub-Saharan Africa" Sileshi pdf`
4. `"Carbon accumulation in agroforestry systems is affected by tree species diversity, age and regional climate" Ma 2020 pdf`
5. `"Carbon sequestration and net emissions of CH4 and N2O under agroforestry" Kim Kirschbaum Beedy pdf`
6. `"A global meta-analysis of the biodiversity and ecosystem service benefits of coffee and cacao agroforestry" De Beenhouwer pdf`
7. `"Effects of agroforestry on pest, disease and weed control: A meta-analysis" Pumariño pdf`
8. `"Effect of plant hedgerows on agricultural non-point source pollution: a meta-analysis" Zheng 2020 pdf`
9. `"Effect of plant hedgerows on agricultural non-point source pollution" researchgate OR pdf full text`
10. `"Agroforestry and smallholder farmers' welfare in sub-Saharan Africa" systematic review meta-analysis Jemaneh 2026`
11. `Jemaneh Thorn Dallimer "Agroforestry and smallholder" welfare sub-Saharan Africa eprints white rose OR leeds OR repository pdf`

## PRISMA-lite funnel
- **Retrieved:** 3,637 records over 35 OpenAlex queries (23 topic + 12 title look-ups). **2,442 were unique** after deduplicating on DOI or normalised title.
- **Title screen:** all 2,442 were screened. Records were kept if they were a synthesis (meta / systematic / review / synthesis / map / global / evidence / quantitative), mentioned an agroforestry term, and were not known. Clinical, urban and forestry-only noise was removed; Q3 and Q17 were especially noisy.
- **Abstract screen:** **60** records, which is the cap. The shortlist is in `scratch/t6/short.txt`; abstracts came from OpenAlex, or from Semantic Scholar where elided.
- **Included:** **25**. By type:
  - 17 meta-analyses
  - 4 systematic reviews
  - 1 systematic map
  - 2 reviews (counted as structured syntheses)
  - 1 database (ERA)
- **Primaries admitted:** 0.
- **DOI checks:** all 25 DOIs passed the Crossref round-trip.

## Screened out at abstract level (one-word reason)
| record | reason |
|---|---|
| Torralba 2016 European AF MA (10.1016/j.agee.2016.06.002) | HIC |
| Mupepele 2021 European AF biodiversity MA (10.1186/s12862-021-01911-9) | HIC |
| Choden 2025 temperate silvoarable SR+MA (10.1016/j.agee.2025.109963) | HIC (**reserve**: family-isolating F1 temperate) |
| Thiesmeier 2023 economic performance scoping review (10.1016/j.forpol.2023.102939) | HIC (**reserve**: the only economics synthesis, EU/N America) |
| Huang 2022 rubber AF economic outcomes SR (10.1007/s10457-022-00734-x) | crop_specific (**reserve**: F5 rubber economics) |
| Feliciano 2018 AF carbon options by region (10.1016/j.agee.2017.11.032) | overlap (Cardinael 2018 / Ma 2020 / Shi 2018 kept); **reserve** |
| Pan 2024 SOC arid MA (CATENA) · Chatterjee 2018 continuum SOC · 2026 C–N–P MA (ecolind) | overlap (carbon saturated) |
| Chapman 2020 trees-on-ag-lands mitigation potential (10.1111/gcb.15121) | method (a mapping estimate, not an effect synthesis; close to known Sprenkle-Hyppolite 2024) |
| Santos 2019 Brazilian Atlantic Forest MA · Bohada-Murillo 2019 birds · Cervantes-López 2024 herpetofauna | overlap (biodiversity covered by De Beenhouwer + Nguyen + Pumariño); **reserve** |
| Bhagwat 2008 TREE "refuge for tropical biodiversity" | superseded (narrative; later MAs kept) |
| Baier 2023 maize-yield global MA (10.3389/fsufs.2023.1167686) | overlap (Kuyah/Sileshi kept); **reserve** |
| Koutouleas 2022 coffee shade yield MA | crop_specific (F5 coffee; **reserve**) |
| Hernández-Salmerón 2022 tree cover vs grass biomass MA · Ripamonti 2025 forage SR · de Oliveira 2023 SPS cattle SR | overlap (Baker 2025 kept); **reserve** for planted_silvopasture |
| Wolka 2018 SSA SWC MA (10.1016/j.agwat.2018.05.016) | practice (cross-slope barriers; vegetative barriers not tree-specific) |
| Pan 2025 vegetated buffer strips MA · Pavlidis 2017 water-pollution review | practice (buffer strips = riparian NbS, not in-field agroforestry) / narrative |
| Bayala 2011 CA cereal yield W Africa | practice (conservation agriculture, not AF) |
| Tranchina 2024 adoption-barrier SLR · Mercer 2004 · Meijer 2014 · Bhandari 2025 · Kerkoff 2026 SPS adoption SR | overlap (Stubblefield 2026 + Sánchez 2026 kept); **reserve** |
| Gonçalves 2021 indigenous agroforestry SR (MDPI) | credibility (descriptive; **reserve** as the only IPLC synthesis) |
| Razafindratsima 2021 forests/trees & poverty dynamics · Cheng 2019 forest–poverty systematic map · Foli 2014 | practice (forest-dominated; agroforestry not disaggregated); Razafindratsima = **reserve** |
| Köthke 2022 "evidence base is patchy" evidence review | relevance (a meta-review of evidence gaps, no effects); useful as a gap check |
| Takal 2026 Africa adaptation SR (10.1007/s44274-026-00849-3) | T3 (adaptation; already the T3 reserve) |
| Low-tier venue reviews (IJECC, JEAI, AJAF, EAJFA, IJCMAS, "A Review on…" Ethiopia ≈30) | credibility (predatory or low-tier venue, narrative) |
| Roe 2021 companions; Mayr 2025 PES scoping review | relevance (finance instrument, not an NbS effect); **reserve** for M6 |
| Evidence/gap-map protocols (Campbell cl2.173, CSA SR protocol 2016) | protocol |

## DOI round-trip and OA
- **DOI round-trip:** **25/25 passed** (Crossref title equals OpenAlex title; `doi_crossref_match=true`). Citations were rebuilt from Crossref author, year, title, container and volume.
- **Haverhals 2016 (CIFOR):** the Crossref record has given and family names swapped, so its citation was corrected by hand from those fields.
- **Baker:** Crossref issue year is 2025, while the T3 probe used 2024 (online-first). The id `baker_2025` follows Crossref.
- **DOIs blanked:** none.
- **OA breakdown (25):**
  - **oa_direct 17** (Unpaywall OA, publisher): Kuyah, Niether, Reed (AM), ERA Sci Data, Félix, Cardinael, Shi, Nguyen, Basche, Kiptot, Haverhals, Stubblefield, Sánchez, Roe, Baker, Muthuri, Sharma.
  - **oa_repository 2**: Muchane 2020, an accepted manuscript on CentAUR Reading (`centaur.reading.ac.uk/89345/7/Main%20text.pdf`; the AM title differs slightly, so confirm). Pumariño 2015, the SLU publications record (confirm a full-text file is attached).
  - **rg_flag_for_human 6**: Sileshi 2008 (RG author-profile PDF + academia.edu seen), Ma 2020, Kim 2016, De Beenhouwer 2013 (RG; a Scribd copy is not acceptable provenance), Zheng 2020, Jemaneh 2026 (also: ask the authors for the AM).
  - **paywalled_verified 0.** ResearchGate cannot be verified by a tool, so nothing is labelled paywalled.
- **ERA:** has no DOI of its own. Use:
  - the Sci Data descriptor DOI `10.1038/s41597-024-03805-z` (Rosenstock et al. 2024, ERA v1.0.1), and
  - the Harvard Dataverse dataset `doi:10.7910/DVN/C3YBNN` ("Evidence for Resilient Agriculture Dataset v1.0.1"), and
  - ERAg R package `github.com/EiA2030/ERAg`. The search snippet gives v1.4.1 (2024-11-29) and CGSpace lists v1.0.3.0, so **confirm the version and pin a commit**.

## Flagged for a human
1. **ERA needs a dataset acquire adapter.** It is a CSV/R tabular evidence base, not a PDF or web page. Under the acquisition lock this is a **PAUSE**: define the adapter, the locator (row/observation id plus commit/version) and a QA rule before registering it.
   - **COI:** Pete Steward and Namita Joshi are listed co-authors on the Sci Data descriptor. Note this on the independence axis.
   - ERA is a pool of primary observations, so the T6 engine would need to re-aggregate them rather than read a pooled effect.
2. **Adoption syntheses are routing-sensitive.** Stubblefield 2026 and Sánchez 2026 report adoption *determinants*: labour, extension, knowledge. Under the 2026-06-23 lock these are soft enabling-environment evidence, which means `use_role=operational_risk` (M2b-B / M6), **not** T6 effect rows. They are tagged `adoption`, `method_type=adoption_study`. Sánchez is the only synthesis covering **dis-adoption**.
3. **PICOS and practice pooling.** Some syntheses mix agroforestry with other practices; extract only the agroforestry rows:
   - Basche 2019 pools agroforestry with perennial grasses and forestry, so treat it as an XW proxy.
   - Sileshi 2008 includes herbaceous green manures.
   - Félix 2018 includes ramial-wood amendments.
   - Reed 2017 and Haverhals 2016 include forest and landscape trees.
   - Zheng 2020 includes grass hedgerows.
4. **Unverified numbers in search snippets.** Some engine summaries attached figures to Muchane (erosion −50%, SOC +21%), Zheng (N −69%, P −67%) and Kim (7.2 t C/ha/yr). **None of these were read from the PDF.** They are not stored in the candidate JSON except where they came from the OpenAlex abstract: Ma +46.1 Mg C/ha, Nguyen +28.4%, Basche +59.2%, Niether −25% cocoa yield, Muthuri per-system C stocks.
5. **`crop_specific`:** Niether 2020 (cocoa) and De Beenhouwer 2013 (coffee/cacao) are re-includable only for F5 `shaded_perennial_crop` via `allow_crop_scope`.

## What was found, per T6 target
| T6 target | synthesis-grade evidence now | effect sizes? | gap |
|---|---|---|---|
| `production_gap` (yield) | Kuyah 2019, Sileshi 2008, Félix 2018, Baker 2025, Niether 2020, Pumariño 2015 (pest-loss proxy), Reed 2017, ERA | yes (MA lnRR / t ha⁻¹) | **yield *stability*: no synthesis** (only a Research Square preprint, "horticultural AF stability MA 2025", and a 2026 yield-variability MA not agroforestry-specific); reserve |
| `rural_poverty` (income/wealth) | Jemaneh 2026 SR-MA, Muthuri 2023, Reed 2017, Niether 2020 (economic performance), ERA (economic outcomes), Sharma 2022 | partial (Jemaneh, Niether) | LMIC per-family income magnitudes thin |
| `soil_erosion_risk` | Kuyah 2019, Muchane 2020, Zheng 2020 (+ known Zhu 2019) | yes | none at synthesis grade for windbreak wind erosion in LMIC |
| `carbon_sequestration_potential` | Cardinael 2018 (IPCC Tier-1 by system), Ma 2020, Shi 2018 (by family), Kim 2016 (net GHG), Muthuri 2023, Félix 2018, Roe 2021 | yes, strong | **saturated** |
| `biodiversity_priority` | Nguyen 2026 (silvopasture), De Beenhouwer 2013 (F5), Pumariño 2015 (natural enemies), Sharma 2022 | yes | parkland/FMNR and F1 biodiversity in LMIC thin (reserve Santos 2019, Bohada-Murillo 2019) |
| `water_quality_risk` | Zheng 2020 (hedgerows, China) (+ known Zhu 2019) | yes | thin; UMIC-only, so `transfer_class` caution for LIC |
| `water_stress` (infiltration / water use) | Kuyah 2019 (water regulation), Basche 2019 (proxy) | yes (proxy) | **no agroforestry-specific water-use or groundwater synthesis**. The known Ilstedt-type primaries and Bargués Tobella are in the queue only. Water-competition (tree water use reducing crop water) is not synthesised. |
| `agricultural_dependency` | Reed 2017, Muthuri 2023 (diversification / safety net), ordinal | no | **effectively uncovered** |
| `gender_inequity` | Kiptot & Franzel 2011, Haverhals 2016 (SR), Sharma 2022 | no (ordinal) | no quantitative gendered-outcome synthesis |
| `iplc_lands` | none included | — | **uncovered** (reserve Gonçalves 2021, descriptive MDPI) |
| economics (cost, BCR, cost/tCO2e) | Roe 2021 (cost-effective ≤ USD100/tCO2e by country), Niether 2020, Jemaneh 2026 (+ known Giger 2015 WOCAT BCR) | partial | **no LMIC synthesis of establishment/recurrent cost or BCR**; only HIC Thiesmeier 2023 and crop-specific Huang 2022 (reserves). The grey/WOCAT/ICR channels must fill this. |
| adoption / dis-adoption | Stubblefield 2026 (MA), Sánchez 2026 (systematic map, incl. dis-adoption) (+ known Pattanayak 2003) | vote-count | adoption *rates* (as opposed to determinants) not synthesised |

**Family coverage:**
- **Well covered:** alley_cropping, tree_intercropping, shaded_perennial_crop (crop_specific), planted_silvopasture, homegardens (Sharma; Shi), parkland_retention / fmnr (Félix, Kuyah).
- **Thin:** windbreaks_shelterbelts (Baker, Shi, Cardinael; mostly HIC/UMIC), contour_vegetative_buffers (Zheng, Muchane), planted_boundary_cropland.
- **None isolated:** agrosilvopasture, anr_on_farm.

## Saturation
- **Q23 (title-only control):** 148 records, of which **35 were new unique records**. Of those 35, only 3 were relevant new syntheses: Ma 2020, Stubblefield 2026 and Kerkoff 2026. The rest were dataset or figshare twins, burn-medicine "Parkland formula" noise, or low-tier venues.
- **Later topic queries (Q12–Q22):** over 75% of the top-30 relevant titles had already been seen. The T1–T12 look-ups found 4 seminal MAs that the abstract queries had missed: Sileshi, Cardinael, Kim and Roe. All 12 were also checked for known status.
- **Judgement:**
  - **Saturated:** carbon, yield, biodiversity and erosion (English synthesis literature).
  - **Not saturated, or structurally empty in the peer-reviewed synthesis literature:** economics (LMIC cost/BCR), agricultural_dependency, iplc_lands, gender (quantitative), water use/groundwater, yield stability. These need the grey/MEL/WOCAT channels and the multilingual pass (for example ES/PT silvopastoral economics, FR Sahel RNA welfare). Primary studies admitted under the sole-evidence exception are also an option.

## Draft `SRCH` row — updated_lit
```
nbs_id=agroforestry | suitability_family_id="" | table=T6 | process=updated_lit
search_terms = <verbatim OpenAlex filters Q1–Q23, T1–T12 in the table above> (title_and_abstract.search / display_name.search); OA-recovery + ERA web searches 1–11 above
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = synthesis (meta-analysis / SR / systematic map / EGM / structured review in a reputable venue) or harmonised effect-size database reporting an agroforestry (any family) effect on a T5 priority outcome (yield, income/welfare, erosion, carbon, biodiversity, water quality, water use, gender, IPLC) or economics (cost, BCR, cost/tCO2e) or adoption/dis-adoption; LMIC-relevant preferred (HIC-only kept as reserve); primaries only when a target has no synthesis (none needed); exclude PADs, predatory/low-tier venues, protocols, forest-only syntheses, riparian buffer strips (other NbS), non-agroforestry practices, known sources
limits = retrieve<=200/query; screen<=80 (60 used, abstract level); include<=25; English only (multilingual + grey/MEL run by sibling agents)
n_retrieved=3637 (2442 unique) | n_screened=60 | n_included=25
search_date=2026-10-02 | run_id=probe_af_t6_lit_2026-10-02 | searched_by=discovery-agent | ruleset_version=v1.6.0
note = synthesis-first discovery pass; do NOT stamp ledger searched=done until multilingual + grey/MEL rows exist
```

## Artefacts (scratch, not in repo)
Raw OpenAlex dumps (`Q*.json`, `T*.json`), `seen.json`, `abstracts.json` and `xref.json` (Crossref + Unpaywall) are in the session scratchpad `t6/`.
