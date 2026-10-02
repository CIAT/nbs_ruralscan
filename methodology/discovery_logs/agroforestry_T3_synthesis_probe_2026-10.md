# Agroforestry × T3 discovery probe (synthesis-first) — 2026-10-02

> **Provenance.** Tracked copy of the probe agent's report (`pipeline/staging/discovery/agroforestry_T3_probe_report.md`, gitignored).
> One opus discovery agent, run `probe_af_t3_2026-10-02`, ruleset **v1.6.0**, synthesis-first rule (Pete 2026-10-01).
> SRCH rows: `agroforestry__T3__updated_lit__probe_af_t3_2026-10-02`, `agroforestry__T3__grey__probe_af_t3_2026-10-02` (see register for exact ids).
> Candidates → `pipeline/acquisition_queue.csv` (20 rows, status `pending`, tables `T3`). Ledger: `searched`/`screened` = `in_progress` (a probe, not the full search).



**Scope:** `nbs_id=agroforestry` × T3 (hazard-impact mitigation + `asset_vulnerability`). Generic parent search (`suitability_family_id=""`); every candidate is tagged with the FAM ids it covers. **Processes run:** `updated_lit`, `grey`. **Ruleset:** v1.6.0 (T3/T6 cell-synthesis; T3 = NbS → smaller hazard impact on livelihoods; asset_vulnerability = hazard → damage to the agroforestry asset). Staging-only: nothing was registered, queued or ledger-stamped.
**Targeting rule (Pete, 2026-10-01):** syntheses first, plus MEL/IA project grey literature. PADs excluded (ex-ante). Primary studies were admitted only where a hazard had no synthesis at all.
**Dedup:** checked against `agroforestry_known_sources.json` (114 rows: 52 SRC + 62 queue) by DOI and normalised title. **No included candidate is already known.** The known KCSAP item is the 2016 **PAD**; the ICR below is a separate ex-post document.

Deliverable: `agroforestry_T3_probe_candidates.json` (20 candidates).

---

## Process 1 — `updated_lit`

**Channel:** OpenAlex `/works` (`mailto=p.steward@cgiar.org`, `per-page=200`, default relevance sort, `select=id,doi,display_name,publication_year,type,cited_by_count,primary_location,open_access`). Base URL: `https://api.openalex.org/works?filter=<filter>&per-page=200&mailto=p.steward%40cgiar.org&select=...`. Semantic Scholar was tried and returned HTTP 429 (rate-limited, 0 results) for these 3 queries: `agroforestry drought yield meta-analysis` · `agroforestry extreme weather resilience systematic review` · `trees on farms buffer climate shocks household food security`. Crossref was used only for DOI round-trips.

### Verbatim queries (OpenAlex `filter=` value) · count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| Q1 | `title_and_abstract.search:(agroforestry OR silvopastoral OR silvopasture OR "trees on farms" OR windbreak OR shelterbelt) AND (drought OR "heat stress" OR "extreme weather" OR "climate shock" OR "climate resilience" OR flood OR cyclone OR wildfire) AND ("meta-analysis" OR "systematic review" OR "evidence map" OR "review")` | 657 | 200 |
| Q2 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "trees on farms" OR "tree-based" OR windbreak OR shelterbelt OR "shade tree") AND ("meta-analysis" OR "systematic review" OR "global synthesis") AND (yield OR microclimate OR temperature OR drought OR "water use" OR resilience)` | 341 | 200 |
| Q3 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "trees on farms" OR "farmer managed natural regeneration") AND ("food security" OR income OR livelihood OR welfare) AND (shock OR drought OR "climate variability" OR "extreme events" OR resilience) AND ("systematic review" OR "meta-analysis" OR "evidence gap map" OR review)` | 633 | 200 |
| Q4 | `title_and_abstract.search:(windbreak OR shelterbelt OR "tree windbreak" OR "live fence") AND (crop yield OR "wind damage" OR "wind erosion" OR storm OR cyclone OR hurricane) AND (review OR "meta-analysis" OR synthesis)` | 148 | 148 |
| Q5 | `title_and_abstract.search:(agroforestry OR "shade tree" OR "trees on farms" OR silvopastoral) AND ("tree mortality" OR windthrow OR "hurricane damage" OR "cyclone damage" OR "drought mortality" OR "fire damage")` | 74 | 74 |
| Q6 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "trees on farms" OR "riparian buffer" OR hedgerow) AND (flood OR runoff OR "peak flow" OR infiltration OR waterlogging) AND ("meta-analysis" OR "systematic review" OR review)` | 397 | 200 |
| Q7 | `title_and_abstract.search:(agroforestry OR "shade trees" OR "coffee agroforestry" OR "cocoa agroforestry" OR silvopastoral) AND ("heat stress" OR "extreme temperature" OR "canopy temperature" OR "microclimate buffering" OR "thermal comfort") AND ("meta-analysis" OR "systematic review" OR review)` | 54 | 54 |
| Q8 | `title_and_abstract.search:(silvopasture OR silvopastoral OR agroforestry OR "fuel break" OR "green firebreak") AND (wildfire OR "fire risk" OR "fuel load" OR "fire behaviour" OR "fire behavior") AND (review OR "meta-analysis" OR synthesis)` | 61 | 61 |
| Q9 | `title_and_abstract.search:(agroforestry OR "shade trees" OR windbreak OR shelterbelt) AND (frost OR "frost damage" OR "cold damage" OR "freezing")` | 217 | 200 |
| Q10 | `title_and_abstract.search:("nature-based solutions" OR "ecosystem-based adaptation") AND (agriculture OR agroforestry OR farm) AND (effectiveness OR "evidence map" OR "systematic review" OR "meta-analysis")` | 423 | 200 |
| Q11 | `title_and_abstract.search:(agroforestry OR "shade coffee" OR "agroecological" OR "trees on farms" OR "diversified farms") AND (hurricane OR cyclone OR typhoon OR "tropical storm" OR "extreme wind")` | 154 | 154 |
| Q12 | `title_and_abstract.search:(agroforestry OR "trees on farms" OR "tree cover" OR "farmer managed natural regeneration" OR parkland) AND (drought OR "rainfall shock" OR "dry spell") AND ("yield stability" OR "yield variability" OR "food security" OR consumption OR "crop failure" OR "household welfare" OR "income stability")` | 434 | 200 |
| Q13 | `title_and_abstract.search:(agroforestry OR "shade trees" OR silvopastoral) AND (frost) AND (coffee OR pasture OR crop)` | 59 | 59 |
| Q14 | `title_and_abstract.search:(agroforestry OR silvopastoral OR "trees on farms" OR windbreak OR "tree-based") AND ("climate change adaptation" OR "adaptation effectiveness" OR "climate resilience") AND ("systematic review" OR "meta-analysis" OR "evidence gap map" OR "scoping review")` | 67 | 67 |
| Q15 | `title_and_abstract.search:(agroforestry OR silvopastoral OR silvopasture OR "trees on farms") AND (wildfire OR "fire risk" OR "forest fire") AND (Mediterranean OR review OR "fire prevention")` | 136 | 136 |
| Q16 | `title_and_abstract.search:(biodrainage OR "bio-drainage") AND (trees OR plantation OR agroforestry) AND (waterlogging OR "water table" OR salinity)` | 42 | 42 |
| Q17 | `title_and_abstract.search:(agroforestry OR "trees on farms" OR "smallholder farmers") AND ("climate risk" OR "climate variability") AND (trees) AND (adaptation OR "risk management" OR "safety net")` | 113 | 113 |
| Q18 | `display_name.search:(agroforestry OR silvopastoral OR "shade trees" OR "trees on farms" OR windbreak OR shelterbelt) AND (drought OR heat OR "extreme weather" OR "climate extremes" OR flood OR cyclone OR hurricane OR fire OR frost) AND ("meta-analysis" OR "systematic review" OR review OR synthesis)` | 3 | 3 |
| T1 | `display_name.search:"effectiveness of nature-based solutions for climate change adaptation"` | 1 | 1 |
| T2 | `display_name.search:"ecosystem-based approaches for adaptation"` | 15 | 15 |

**Language note:** the queries were English-only. The AGROVOC ES/FR/PT synonym expansion in the protocol was **not** run in this probe, which is a recall gap. Add it before the full search.

### PRISMA-lite funnel
- **Retrieved:** 2,327 records over 20 queries. **1,813 were unique** (DOI or title).
- **Title screen:** all 1,813. The title-level filter kept syntheses (meta/systematic/review/synthesis/map/global) that mention agroforestry terms, plus every record from the hazard-specific queries Q5, Q9, Q11, Q13, Q15 and Q16. Known sources (flagged) were dropped.
- **Abstract / full-text screen:** **60** shortlisted records (cap reached).
- **Included:** **16**. That is 13 syntheses (2 meta-analyses, 5 systematic reviews or maps, 6 reviews) plus 3 primary studies admitted under the sole-evidence exception (frost, and wind_cyclone for both livelihood and asset rows).

### Screened out at abstract or full-text level (one-word reason)
| record | reason |
|---|---|
| Lasco et al. 2014 WIREs CC (10.1002/wcc.301) | overlap (same team as the included COSUST review) |
| Doswald et al. 2014 Clim & Dev EbA review | superseded (by Chausson 2020) |
| Miller et al. 2019 Campbell EGM (10.1002/cl2.1066) | lineage (parent of known castle_sr_2021, which has no hazard effect sizes) |
| Castle et al. 2022 HIC systematic map (10.1186/s13750-022-00260-4) | HIC-only, no hazard focus |
| Kuyah et al. 2019 SSA MA (10.1007/s13593-019-0589-8) | outcome (yield/soil/water, not hazard), so T6 |
| De Beenhouwer 2013 coffee/cacao MA | outcome (biodiversity), so T6 |
| Niether 2020 cocoa MA (10.1088/1748-9326/abb053) | outcome (multi-dimensional, not hazard), so T6 candidate |
| Ivezić 2021 European AF yields MA | outcome (yield) + HIC |
| Effects of AF on maize yield, global MA 2023 | outcome (yield, no stress stratum) |
| Mediterranean AF productivity MA 2023 (10.1007/s13593-023-00927-3) | outcome (yield) + HIC |
| Silvopasture/paddock-tree/linear AF productivity quantitative review 2024 (10.1016/j.agsy.2024.104240) | outcome (productivity), so T6 |
| Windbreaks in the US, SR of producer-reported benefits 2020 | HIC + perception |
| Tree windbreaks and shelter benefits to pasture 1998 / Kort 1988 / Cleugh 1998 / Brandle 2004 | known or HIC (Cleugh, Brandle, Kort are already in the corpus) |
| Silvopastoral systems as a strategy for drought resilience, short review 2025 (Silva Balcanica) | credibility (short, low-tier venue) |
| Agroforestry and Climate Extremes … Critical Review 2026 (BPI book chapter) | credibility (low-quality publisher) |
| Many "A Review" items in IJECC/JEAI/AJRAF 2019–2026 (≈25) | credibility (predatory or low-tier venues, narrative) |
| Abebaw 2025 SR AF mitigation/adaptation (10.1002/cli2.70018) | relevance (mitigation-led, no hazard outcomes in abstract); **reserve** |
| Evidence on AF practices for CC adaptation in Africa, SR 2026 (10.1007/s44274-026-00849-3) | unverified (abstract not checked within cap); **reserve, high priority** |
| Agroforestry and smallholder welfare in SSA, SR+MA 2026 (10.1016/j.agsy.2026.104670) | outcome (welfare, not shock-conditional); **T6 reserve** |
| Global analysis of rice-tree integration benefits/risks 2022 (FCR) | outcome (yield) |
| Reed et al. 2017 Trees for life SR (Forest Policy & Econ) | outcome (ES and food, not hazard), so T6 |
| Hedgerow multiple-benefits evidence review 2025 (People & Nature) | HIC + relevance |
| Biodrainage India review 2020 (JANS) / Agric Water Mgmt 2020 perspectives | overlap (Singh & Lal 2018 kept; these are fallbacks) |
| Holt-Giménez 2002 Hurricane Mitch | primary (Philpott 2008 kept as the single cyclone primary for livelihoods) |
| Post-cyclone agroforest food system, Pacific 2022 (10.1007/s10113-022-01916-0) | primary; **reserve** for wind_cyclone |
| Lin 2007 coffee microclimate / Sida-type Faidherbia buffering primaries | known or primary |
| Damianidis-adjacent Spanish fuel-break grazing primaries (2011, 2012) | primary (review kept) |
| Ecosystem-based adaptation for smallholders, definitions 2015 (AGEE) | relevance (conceptual) |
| Climate change adaptation through agroforestry: opportunities and gaps (COSUST 2022, S1877343522000963) | surfaced late via web search, unverified; **reserve, high priority** |

### Saturation (updated_lit)
- The title-only control query Q18 (`display_name.search`) returned only **3** records, all already seen.
- In the later queries (Q13–Q17), over 80% of the top-35 records were either already seen or known.
- **Judgement:** saturated for English-language syntheses on drought, heat, wind and fire. **Not saturated** for (a) the AGROVOC ES/FR/PT synonyms, (b) frost and waterlogging (only primaries and grey biodrainage literature exist) and (c) cyclone (only primaries).

### Draft `SRCH` row — updated_lit
```
nbs_id=agroforestry | suitability_family_id="" | table=T3 | process=updated_lit
search_terms = <verbatim filters Q1–Q18, T1, T2 in the table above> (OpenAlex title_and_abstract.search / display_name.search); Semantic Scholar 3 queries (HTTP 429, 0 results)
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = synthesis (meta-analysis / SR / systematic map / EGM / review in a reputable venue) reporting an agroforestry (any family) effect on a T3 hazard's impact on yield, income, food security or livestock, or hazard damage to agroforestry trees; primaries only when a hazard has no synthesis; exclude PADs, predatory venues, pure physiology, urban trees, species-only envelopes, known sources
limits = retrieve<=200/query; screen<=60 (abstract/full-text); include<=20 overall; English only (multilingual not run)
n_retrieved=2327 (1813 unique) | n_screened=60 | n_included=16
search_date=2026-10-02 | run_id=probe_af_t3_2026-10-02 | searched_by=discovery-agent (probe) | ruleset_version=v1.6.0
note = probe, not a full search; do NOT stamp ledger searched=done from this
```

---

## Process 2 — `grey`

**Channels:** (a) web search (US engine), (b) the **World Bank Documents & Reports API** `https://search.worldbank.org/api/v2/wds`, (c) the **CGSpace DSpace 7 API** `https://cgspace.cgiar.org/server/api/discover/search/objects`.

### Verbatim queries · results
**Web search (verbatim strings):**
1. `Kenya Climate Smart Agriculture Project P154784 Implementation Completion and Results Report`: 9 results (ICR00006593 found, plus the IEG ICRR and ISRs)
2. `agroforestry drought resilience impact evaluation report smallholders World Bank IEG`: 9
3. `3ie evidence gap map agroforestry climate adaptation resilience`: 9
4. `Mapping evidence on agroforestry's role in biodiversity and climate change mitigation and adaptation in low- and middle-income countries systematic map 2025`: 9
5. `Regional Integrated Silvopastoral Ecosystem Management Project Implementation Completion Report Nicaragua Colombia Costa Rica`: 9 (RISEMP ICR0000875 and Colombia CMSCR ICR00005139)
6. `Regreening Africa evaluation report agroforestry resilience drought households endline`: 9
7. `Green Climate Fund IEU evidence gap map adaptation agroforestry ecosystem-based`: 9
8. `World Bank study silvopastoral systems Colombia climate variability milk productivity losses resilience 2009-2019`: 9
9. `CGSpace agroforestry impact assessment resilience drought shock household panel evaluation ICRAF`: 9
10. `Implementation Completion Report sustainable land management agroforestry flood drought resilience Ethiopia SLMP ICR`: 9
11. `Regreening Africa Consolidated Endline Report 2023 pdf`: 9
12. `"Regreening Africa" endline survey report drought food security tree cover households 2023 worldagroforestry.org`: 9
(OA-recovery web searches are listed separately below.)

**WB Documents API** (verbatim `qterm` × `docty_exact`; `rows=30`):
| qterm | docty_exact | total |
|---|---|---|
| `agroforestry drought resilience` | Implementation Completion and Results Report | 0 |
| `agroforestry drought resilience` | Project Performance Assessment Report | 1 |
| `silvopastoral` | Implementation Completion and Results Report | 1 |
| `silvopastoral` | Project Performance Assessment Report | 0 |
| `agroforestry climate resilience` | Implementation Completion and Results Report | 3 |
| `agroforestry climate resilience` | Project Performance Assessment Report | 1 |
| `trees on farms resilience` | Implementation Completion and Results Report | 11 |
| `trees on farms resilience` | Project Performance Assessment Report | 0 |
| `Ethiopia Sustainable Land Management project performance assessment` | (none) | 5 shown |

**CGSpace API** (verbatim `query`, `dsoType=ITEM`, `size=40`):
| query | total |
|---|---|
| `agroforestry AND (drought OR flood OR cyclone OR "extreme weather") AND (resilience) AND (evaluation OR "impact assessment" OR endline OR MELIA)` | 3,225 |
| `agroforestry AND resilience AND "systematic review"` | 587 |
| `silvopastoral AND (drought OR "heat stress") AND resilience` | 458 |
| `"Regreening Africa" endline` | 3 |

### PRISMA-lite funnel
- **Retrieved:** 108 web results, 22 WB-API documents (17 unique) and 123 CGSpace items (top 40 per query plus 3), so about 250 in total.
- **Screened (title/metadata, then full-text grep where the PDF downloaded):** 24.
- **Included:** **4** (KCSAP ICR · Colombia CMSCR ICR · IEG Ethiopia SLMP PPAR · IPCC AR6 WGII Ch5).

### Screened out (one-word reason)
| item | reason |
|---|---|
| RISEMP ICR0000875 (2008), silvopastoral CR/CO/NI | relevance (fodder banks and fire-use reduction are management metrics, not hazard outcomes) |
| Togo Integrated Disaster & Land Management ICR4297 | practice (0 agroforestry mentions) |
| Mexico Coastal Watersheds ICR4848 | relevance (agroforestry restoration costs only, no hazard outcome) |
| Mozambique FIP ICR5977 / Rwanda LAFREC ICR5783 / Ghana SLWM ICR5558 | relevance (forest/landscape; not screened beyond title, so **reserve**) |
| DEval/GCF-IEU adaptation EGM 2020 (Doswald et al.) | practice (agroforestry named once, not disaggregated) |
| ADB SDWP-115 *Investing in Agroforestry* (2025, 10.22617/WPS250549-2, Crossref-verified) | credibility (advocacy, qualitative, country profiles); **reserve** |
| IEG ICR Review of KCSAP | duplicate (companion to the ICR; recorded in the ICR row) |
| Ethiopia SLMP ICR4449 / ICR3074 | duplicate (the PPAR is independent and covers both phases) |
| CCAFS "10 best bet innovations for adaptation" | relevance (practice catalogue, no outcomes) |
| CGSpace: Akponikpè 2025 SR protocol (sorghum/millet) | protocol (no results yet, not agroforestry-specific) |
| CGSpace: Nguru et al. 2026 Sahel land- and water-management SR (10.3390/su18020787) | practice (SWC structures, not agroforestry) |
| CGSpace: CGIAR SR protocol on drought/heat research 2024 | protocol |
| ERA (Evidence for Resilient Agriculture) database | scope (yield and productivity effect sizes, not hazard-conditional), so **T6 high-priority** |
| Regreening Africa Consolidated Endline Report (Aug 2023) | **unverifiable**: the cited PDF URL returns an HTML/404 page and nothing is on CGSpace, so it was not included (see "flagged for a human") |

### Saturation (grey)
**Not saturated.** Only the WB-ICR channel was worked to the point of diminishing returns, and its yield is low: the API surfaces few agroforestry-specific ICRs. MELIA channels need their own pass: CGIAR (FTA/CIFOR-ICRAF impact assessments, ERA), GEF IEO, IFAD IOE, 3ie repository, FAO OED and WOCAT. Note that WOCAT is a PAUSE until its adapter is built.

### Draft `SRCH` row — grey
```
nbs_id=agroforestry | suitability_family_id="" | table=T3 | process=grey
search_terms = <12 verbatim web strings above> ; WB WDS API qterm×docty_exact (8 combos + 1 targeted) ; CGSpace DSpace API (4 queries above)
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = ex-post project evidence (ICR / IEG PPAR or ICRR / impact evaluation / MELIA endline) or institutional assessment (IPCC) reporting agroforestry outcomes under a T3 hazard, or hazard damage to agroforestry assets; exclude PADs (ex-ante), ISRs (in-progress), advocacy briefs without outcome data, documents with no agroforestry disaggregation
limits = web ≤ ~10 results/query; WB API rows=30; CGSpace size=40; screen<=60; include<=20 overall (shared with updated_lit)
n_retrieved≈250 | n_screened=24 | n_included=4
search_date=2026-10-02 | run_id=probe_af_t3_2026-10-02 | searched_by=discovery-agent (probe) | ruleset_version=v1.6.0
note = probe; channels not exhausted (see saturation)
```

---

## DOI round-trip (Crossref) and OA recovery
- **All 17 DOIs emitted passed** the Crossref title round-trip (`doi_crossref_match=true`, with the Crossref title stored). The 3 grey documents with no DOI are anchored on the title and report number, read from the downloaded PDF cover or the WB API record.
- **No candidate failed the round-trip.** Lasco WIREs, Doswald, Miller EGM and ADB WPS were also verified but screened out.
- **IPCC Ch5:** Crossref has no author list. The authors in the citation (Bezner Kerr, Hasegawa, Lasco et al.) must be confirmed from the chapter PDF.
- **OA breakdown (20):**
  - **oa_direct 12**: publisher OA or WB/IPCC download.
  - **oa_repository 4**: Damianidis (Cranfield CERES) · Zhu (HAL hal-02490364) · Philpott (author lab PDF, utexas) · Ntawuruhunga (CGSpace item; confirm the bitstream exists).
  - **rg_flag_for_human 4**: Deniz 2023 · Singh & Lal 2018 · Caramori 1996 · McGuigan 2024. For each, Unpaywall was closed and a web search found only the publisher page plus RG/Semantic Scholar stubs.
  - **paywalled_verified: 0.**
- **OA-recovery web searches (verbatim):**
  - `"Climate-smart agroforestry systems and practices: A systematic review of what works, what doesn't work, and why" pdf`
  - `"A multi-scale assessment of hurricane impacts on agricultural landscapes based on land use and topographic features" Philpott pdf`
  - `"Reductions in water, soil and nutrient losses and pesticide pollution in agroforestry practices" Zhu pdf`
  - `"Predictors of tree damage and survival in agroforests after major cyclone disturbance in Fiji" pdf`
  - `"A systematic review of the effects of silvopastoral system on thermal environment and dairy cows" pdf`
  - `"Review and Case Studies on Biodrainage: An Alternative Drainage System to Manage Waterlogging and Salinity" pdf`
  - `Caramori 1996 "Coffee shade with Mimosa scabrella" frost protection southern Brazil pdf`

## Flagged for a human
- **ResearchGate check first:** Deniz 2023 · Singh & Lal 2018 · Caramori 1996 · McGuigan 2024. Ntawuruhunga 2023 also needs a check if the CGSpace item has no PDF.
- **Regreening Africa Consolidated Endline Report (CIFOR-ICRAF/World Vision/CRS, Aug 2023):**
  - **Status:** a strong MELIA candidate, but the PDF could not be retrieved or verified. Locate it via CIFOR-ICRAF.
  - **Do not trust the hazard numbers in the search snippets.** The search engine's summary attached "40% fewer food-insecure months during drought" figures to it, and these were not traced to any document.
- **Chausson 2020:** the publisher PDF was bot-blocked. Confirm that the agroforestry/silvopastoral slice exists and which hazards it covers before extraction.

---

## What the probe found
- **Drought now has synthesis-grade and project-grade evidence:**
  - Dobhal 2024 (multi-hazard review with quantified ranges), Chausson 2020 (directional NbS effectiveness) and Lasco 2014.
  - **The Colombia CMSCR ICR, the most useful find.** It gives a quantified drought livelihood effect for silvopasture: 0.4–5.5% milk-productivity loss versus up to 19% on extensive farms. It also gives an explicit **asset_vulnerability** signal: newly planted intensive SPS area fell 45% in the 2019 drought.
  - The IEG Ethiopia PPAR adds independent LIC evidence, but it is ordinal and bundled with SLM.
- **Heat_stress:** good evidence.
  - Patil 2025 is a coffee meta-analysis with pooled effect sizes (F5, crop-specific).
  - Hao 2026 is a shelterbelt meta-analysis (−4% summer air temperature).
  - Deniz 2023 covers silvopasture and cow thermal comfort.
  - Dobhal 2024 reports 2–4 °C shade cooling.
- **Wind_cyclone:**
  - Windbreak crop protection has a meta-analysis (Hao 2026, wind −35.8%, yield +16.6%), but from China only (UMIC).
  - For **cyclone/hurricane damage** there are **only primaries**: Philpott 2008 (livelihoods) and McGuigan 2024 (assets).
- **Flood:** proxy-grade only. Zhu 2019 gives mean runoff reduction of 58%, which should be read through XW `proximity=proxy` (0.7 haircut). Chausson and Dobhal add direction. No synthesis measures flood *impact* on livelihoods under agroforestry.
- **Fire:** HIC only (Damianidis 2021, Mediterranean, plus the known Batcheler 2024, US). Expect `transfer_class` = HIC and `no_applicable_evidence` for LMIC rows.
- **Frost:** one primary (Caramori 1996, coffee, Brazil), plus a qualitative mention in Dobhal 2024. Effectively a single source.
- **Waterlogging:** one review (Singh & Lal 2018, biodrainage). It applies only to irrigated systems with shallow water tables, which is a narrow transfer.
- **Asset_vulnerability:** Watts 2022 (systematic review), van Noordwijk 2021, the Colombia ICR (drought, establishment phase) and McGuigan 2024 (cyclone). Still no synthesis for fire or flood damage to agroforestry assets. Under v1.6.0, `asset_risk_weight` therefore stays on the equal-weight fallback, because not all 7 hazards will have a row.
- **KCSAP ICR: yes, it exists.** It is Report **ICR00006593**, dated 31 May 2024, and an IEG ICR Review also exists. **It does not give agroforestry hazard evidence:**
  - Agroforestry was a minor bundled practice (395 acres of county sub-projects, plus fruit-tree seed).
  - The PDO "resilience indicator" is simply *adoption of ≥1 TIMP* (593,521 beneficiaries).
  - The only shock-conditional result is a 48.2% productivity gain against non-beneficiary counties during the 2020–22 drought. It covers 5 value chains (sorghum, millet, cassava, dairy, aquaculture) and none of them is agroforestry.
  - The ICR itself (Lesson 6) says resilience was not measured beyond productivity and adoption.
  - Treat it as a documented gap or null for agroforestry. It is a low-tier signal for bundled CSA in Kenya.

## Scale-up estimate
- **Full agroforestry T3 (generic + per family, all 4 processes, AGROVOC multilingual):** expect about **25–40 sources** in total. That is the 20 here plus roughly 5–10 from the multilingual and family-targeted queries (ES/PT silvopastoral heat and drought literature from Brazil and Colombia; FR Sahel parkland and FMNR drought literature), roughly 3–6 MELIA/IA reports (Regreening Africa, FTA/CIFOR-ICRAF impact assessments, GEF IEO, IFAD IOE), and 2–4 WOCAT entries once the adapter exists. Synthesis-grade evidence will remain thin for frost, waterlogging, cyclone damage and LMIC fire.
- **T6 add-on:** the same corpora plus the T6-specific syntheses screened out here (Kuyah 2019, Niether 2020, De Beenhouwer 2013, the welfare SR-MA 2026, Reed 2017, the silvopasture productivity review 2024, ERA). Expect **+20–35 sources**, so roughly **45–75** for T3+T6 combined, before applying the ≈20-per-table cap.
- **Saturation:** `updated_lit` saturated for English syntheses on the main hazards, with diminishing returns since Q13. `grey` did **not** saturate; the MELIA and evaluation channels were only sampled.

## Artefacts (scratch, not in repo)
Raw query dumps, Crossref and Unpaywall JSON and downloaded ICR texts are in the session scratchpad (`oa/`, `wds/`, `cg/`, `xref.json`, `*_icr.txt`). None were written to `.cache/corpus/`; acquisition goes through the normal pipeline.
