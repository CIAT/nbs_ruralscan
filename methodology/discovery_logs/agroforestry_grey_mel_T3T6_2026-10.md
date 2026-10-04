# Agroforestry × T3/T6 — grey MEL / impact-assessment pass (2026-10-02)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `af_grey_mel_2026-10-02`, ruleset **v1.6.0**, synthesis-first rule (Pete 2026-10-01). SRCH rows carry the same run_id; candidates → `pipeline/acquisition_queue.csv` (status `pending`). 11 queued (grey ids renamed author_year at registration).


- **Scope:** `nbs_id=agroforestry`, generic parent search (`suitability_family_id=""`), tables T3 + T6, process **`grey`**, ruleset v1.6.0. Run id: `grey_mel_af_t3t6_2026-10-02`.
- **What this pass covered:** only the MEL / impact-assessment channels. It does not repeat the probe's WB ICR / PPAR channel. Peer-reviewed T6 and the multilingual pass belong to the sibling agents.
- **Staging only.** Nothing was registered, queued or ledger-stamped, and no git commands were run. PDFs were read from the scratchpad (`…/scratchpad/grey/`), not saved into the repo.
- **Dedup:** checked against `agroforestry_known_sources.json` (134 rows) by DOI and normalised title. None of the 11 included items is known.
- **Deliverable:** `agroforestry_grey_mel_candidates.json` (11 candidates).

## Funnel (all channels)
| stage | n |
|---|---|
| retrieved (API rows + web results + direct fetches) | ≈ 435 (CGSpace 245 rows shown of 9,069 hits · web 182 · direct 8) |
| screened (metadata or full text) | 44 |
| included | **11** (include cap of 25 not reached) |

---

## Channel 1 — CGSpace DSpace 7 API (CGIAR MELIA / SPIA / FTA / CCAFS)
Endpoint: `https://cgspace.cgiar.org/server/api/discover/search/objects?dsoType=ITEM&query=<q>&size=<n>`

| # | query (verbatim) | total | rows read |
|---|---|---|---|
| C1 | `"Regreening Africa" AND (endline OR "end line" OR evaluation OR "impact assessment")` | 42 | 30 |
| C2 | `"Regreening Africa" AND report` | 44 | 40 |
| C3 | `agroforestry AND ("impact assessment" OR "impact evaluation") AND (household OR farmers) AND (income OR yield OR "food security")` | 2406 | 25 |
| C4 | `dcterms.type:Report AND agroforestry AND ("impact evaluation" OR "impact assessment" OR endline OR "ex-post")` | 1198 | 25 |
| C5 | `SPIA AND (agroforestry OR trees OR "natural resource management")` | 546 | 20 |
| C6 | `"farmer managed natural regeneration" AND (evaluation OR impact OR endline)` | 286 | 25 |
| C7 | `"Trees for Food Security" AND (evaluation OR impact OR endline OR "final report")` | 43 | 15 |
| C8 | `silvopastoral AND ("impact evaluation" OR "impact assessment" OR "ex-post" OR evaluation) AND (income OR productivity OR adoption)` | 791 | 15 |
| C9 | `agroforestry AND (drought OR "climate shock") AND (household OR panel) AND (consumption OR "food security" OR income) AND (resilience)` | 3092 | 20 |
| C10 | `"FTA" AND "impact assessment" AND (agroforestry OR trees)` | 270 | 15 |
| C11 | `agroforestry AND "cost-benefit" AND (ex-post OR evaluation OR "returns")` | 941 | 15 |

**Included (6):**
- 05 SPS Caquetá DiD brief
- 06 Place et al. 2005 IFPRI RR142
- 08 SPIA Ethiopia 2024
- 09 Mutenje 2021 CCAFS
- 07 Coulibaly 2016 ICRAF WP223 (reached via web search; CIFOR-ICRAF domain)
- 01 Regreening endline (the CGSpace search found only the *baseline*, hdl 10568/113480; see the Regreening Africa section below)

**Screened out:**
| item | reason |
|---|---|
| T4FS Rwanda impact assessment (OICS3757) | placeholder (MELIA record "On-going", no results) |
| Malawi improved fruit trees impact (OICS3758) | placeholder (planned QE, no results) |
| Heifer Olancho silvopastoral brief 2026 | modelled (typology/scenario) |
| Simutowe 2023 CSA meta-analysis | practice (agroforestry not disaggregated) |
| FTA WP14 synthesis of 5 impact studies + Challenge 2/4 reports | relevance (research-attribution meta-evaluation, no farm outcomes) |
| Evaluation of FTA CRP 2014 | relevance (programme governance) |
| CIAT-AICCRA sustainable agriculture IE 2025 | practice (not agroforestry) |
| Africa RISING country impact reports | practice (bundled sustainable intensification) |
| CCAFS Nyando endline synthesis | practice (bundled) |
| FMNR soil health Niger 2025 (10568/180323) | primary (soil only; T4/T6 lit lane) |
| Regreening Africa baseline 2020 | superseded (by endline) |

**Saturation: near-saturated for CGIAR outcome studies.** Top-25 lists turned over into annual reports and plans of work by C7 to C10. ERA (Evidence for Resilient Agriculture) remains the obvious unworked CGIAR source. It is a database with no acquisition rule, so it is **PAUSE** and treated as a pointer.

## Channel 2 — Regreening Africa site (live 404) → Internet Archive
- `https://regreeningafrica.org/reports-and-publications/` returns **HTTP 404** live.
- The Wayback availability API gave snapshot `20260422042137`. That snapshot lists the endline and its French version.
- Both PDFs were fetched with `web.archive.org/web/2026id_/<orig>`. See the Regreening Africa section below.

**Also listed and screened:**
| item | reason |
|---|---|
| RegreeningAfrica-Final-Report_29Aug-ONLINE.pdf (68 pp) | duplicate (narrative companion of the endline) |
| ELD Ghana / Rwanda / Senegal reports | modelled (ex-ante CBA) |
| 2022 country reports | superseded (by endline) |

## Channel 3 — 3ie (EGMs, systematic reviews, impact evaluations)
Web queries (verbatim, 9 results each):
- W3: `3ie impact evaluation agroforestry trees on farms farmer managed natural regeneration report` (domains 3ieimpact.org, developmentevidence.3ieimpact.org)
- W4: `3ie evidence gap map land use forestry agroforestry systematic review payment environmental services` (domain 3ieimpact.org)
- W5: `3ie "Impact Evaluation Report" agroforestry OR "tree planting" OR "trees" Uganda OR Malawi OR Kenya OR Ethiopia`

Direct fetches: the EGM 29 page and the CCB programme page.

**Included: 0.** EGMs carry no effect sizes, so they are pointers only:
- 3ie **EGM 29** (2024), *Land-use change and forestry programmes in LMICs: EGM update*, DOI 10.23846/EGM029 (Crossref ✓). Report PDF is behind a JS download button.
- 3ie **CCB EGM** (2024/2025; 1,512 IEs + 93 SRs) and its online appendix H list of included records. This is the best route to agroforestry IEs.
- 3ie **SR 44** PES (Snilstveit et al.). Screened out: practice (PES, not agroforestry).
- Miller et al. 2019 / Castle 2021 Campbell agroforestry EGM/SR: known or lineage.

The 3ie-registered Vi Agroforestry IE (Hughes et al., World Dev) is peer-reviewed, so it belongs to the sibling agent.

**Saturation:** reached for the 3ie channel. Its value is the EGM appendices, which feed the peer-reviewed sibling.

## Channel 4 — IFAD (IOE + impact assessments)
- W6: `IFAD Independent Office of Evaluation project performance evaluation agroforestry farmer managed natural regeneration results` (ifad.org; 9)
- W7: `IFAD impact assessment report agroforestry trees resilience ASAP` (ifad.org; 9)

**Included: 0.**
- **ifad.org and ioe.ifad.org return a bot-check page or HTTP 403** to curl and WebFetch, and there is no Wayback copy.
- CHARMP2 Philippines IA (Hossain et al. 2022, 55 pp, fetched from the IA-2021 asset path). Screened out: bundled. Agroforestry appears only as training/benefit receipt (+203% agroforestry trainings, +94% reforestation/agroforestry benefits). Outcomes such as +32% gross income are package-level.
- Mexico DECOFOS IA. **Human flag:** the snippet claims NDVI is positive where the project focused on agroforestry. The document could not be fetched.
- IOE Burkina Faso Special Programme SWC/AGF (phases 1–2). **Human flag:** 403.
- *Strengthening agroforestry in rural investments: lessons from IFAD operations*. **Human flag:** bot-check.

**Saturation: NOT reached.** The channel is blocked by the tool, not exhausted.

## Channel 5 — GEF IEO
- W11: `GEF Independent Evaluation Office evaluation agroforestry land degradation drylands sustainable forest management outcomes report` (gefieo.org, thegef.org; 9)
- Direct fetches: the VfM-2016 page, the SCCE-drylands page and the drylands blog.

**Included: 0.**
- **SCCE Drylands (2023), vol 1 (84 pp, fetched).** Screened out: lineage. Its agroforestry and drought findings come from the IEG Ethiopia SLMP PPAR, which is already queued:
  - "gross primary production grew by 14 percent on average in project areas affected by severe droughts and by 3 percent in other project areas" (printed p.32)
  - "Agroforestry and area closures to limit free grazing led to a 5 percent increase in vegetation cover" (citing IEG 2020a)
  - ~~Note for the PPAR extraction: … it lives in the PPAR.~~ **CORRECTED 2026-10-04 by the lane-D extraction pass:** the sentence above was read in the **SCCE Drylands document**, not in the PPAR. A full-text search of the cached PPAR (110 pp) returns **zero** hits for "gross primary production" or "GPP". Do NOT attribute this number to the PPAR; it is unusable until the SCCE Drylands evaluation is acquired and cached in its own right.
- **VfM 2016 land degradation (GEF/ME/C.51/Inf.02, 56 pp).** Screened out: practice (1 agroforestry mention, no disaggregation).

**Saturation:** reached for agroforestry-disaggregated GEF IEO content.

## Channel 6 — FAO OED
- W12: `FAO Office of Evaluation final evaluation agroforestry "Action Against Desertification" OR "Forest and Farm Facility" results` (fao.org; 8)

**Included: 0.**
- AAD final evaluation (cc0151en, 116 pp). Screened out: practice + no_outcome. It covers enrichment planting and forest restoration, and its M&E "did not capture survival rates". Its only number is carbon (+2.2–9.3% vs baseline), which is not agroforestry-specific.
- Forest and Farm Facility. Screened out: relevance (producer organisations).

**Saturation:** partial (two queries only). FAO OED's search UI was not exercised.

## Channel 7 — World Vision FMNR (Talensi, Humbo, Senegal, Niger)
Queries (verbatim):
- W8: `World Vision Talensi FMNR project final evaluation report Ghana` (9)
- W9: `Humbo assisted natural regeneration project evaluation World Vision Ethiopia report income carbon` (9)
- W10: `FMNR evaluation report Senegal World Vision "Beysatol" endline` (10)

**Included (2):** 03 Talensi Phase-3 impact brief; 04 WV *Evidence of impact: FMNR* (2019).

**Screened out:**
| item | reason |
|---|---|
| Talensi SROI report (Weston & Hong; wvi.org returned HTML) | lineage (basis of the known Weston et al. 2015) |
| Humbo ANR (CDM; Oxford Economics GPG case study / BioCarbon Fund) | practice (communal hillside forest restoration, so forest_restoration rather than on-farm agroforestry) |
| Beysatol / BLST Senegal | unavailable (only a 2009 baseline is referenced; the endline is not online) |
| WV FMNR EGM 2024 research brief | egm (pointer) |
| Niger | the WV/USAID Niger evaluations were not found online |

**Saturation:** reached for publicly posted WV documents. The rest needs WV MEL contacts.

## Channel 8 — USAID / GIZ / DFID / Sida / CRS
Queries (verbatim):
- W13: `USAID final performance evaluation FMNR Niger REGIS-ER natural regeneration results report pdf` (9)
- W14: `DEval OR GIZ impact evaluation agroforestry OR "soil rehabilitation" ProSoil Benin Burkina Ethiopia Kenya rigorous evaluation report` (8)
- W15: `USAID impact evaluation agroforestry shade coffee cocoa OR "trees on farms" Haiti OR Guatemala OR Uganda evaluation report dec.usaid.gov` (9)
- W16: `Larwanou Abdoulaye Reij 2006 "Etude de la régénération naturelle assistée dans la région de Zinder" USAID IRG pdf` (10)
- W17: `Sida decentralised evaluation Vi Agroforestry programme evaluation report Kenya Uganda Tanzania outcomes` (9)
- W18: `Agroforestry Food Security Programme Malawi AFSP evaluation report Irish Aid maize yield impact` (9)

**Included (2):** 02 CRS Regreening cost-efficiency (found via W1); 07 Coulibaly 2016 (AFSP-linked, via W18).

**Screened out:**
| item | reason |
|---|---|
| USAID DEC | unavailable (no DEC results returned; REGIS-ER evaluation not located) |
| Larwanou et al. 2006 IRG/USAID Zinder study | unavailable (no OA copy; FR, so passed to the multilingual sibling; flag RG for a human) |
| GIZ ProSoil MAP/TAPE country reports (CIFOR-ICRAF 9350–9352) | practice (agroecology index, agroforestry not disaggregated) |
| Sida DE 2023:1 | wrong document (education sector) |
| Vi Agroforestry ALIVE end evaluation | unavailable (no report found; outcomes only on the Vi website) |
| AFSP external evaluation (Centre for Independent Evaluations 2011) | unavailable (not online) |
| ACIAR FST-2015-039 final report | not screened (cap/time; **reserve**, ACIAR final reports are OA) |
| ICRAF refugee agroforestry evaluative report | non-publisher host (Scribd) |

**Saturation: NOT reached.** USAID DEC is unavailable and GIZ/DFID evaluation portals were not queried directly.

## Channel 9 — IPCC / IPBES beyond AR6 WGII Ch5
Located via Crossref DOI round-trip plus direct ipcc.ch downloads.

**Included (2):**
- 10 SRCCL Ch6 (10.1017/9781009157988.008 ✓; 122 pp)
- 11 AR6 WGIII Ch7 (10.1017/9781009157926.009 ✓; 114 pp)

**Reserve:**
- SRCCL Ch5 *Food security* (10.1017/9781009157988.007 ✓). Not screened for agroforestry depth.
- IPBES Land Degradation & Restoration Assessment 2018 (10.5281/zenodo.3237392, DataCite ✓). The Zenodo files API did not return JSON, so the text was not checked.

**Saturation:** reached for IPCC. IPBES has not been checked.

## WOCAT (PAUSED; pointers only, NOT included)
- W19: `qcat.wocat.net technology agroforestry drought resilience smallholder "impacts" FMNR OR silvopastoral OR "shade trees"` (9)
- W20: `site:qcat.wocat.net agroforestry technologies drought` (9)

Pointers:
- Multistorey agroforestry, Ethiopia: `qcat.wocat.net/en/wocat/technologies/view/permalink/6621/`
- technologies_513
- technologies_1331
- UNCCD Prosopis cineraria agroforestry, India (unccd_226)
- The agroforestry SLM-group filter, which lists about 161 pages of technologies

Known WOCAT 507 (FMNR, Kenya) and 1358 (ANR) are already in SRC. Hold everything until the WOCAT adapter exists.

---

## Regreening Africa Consolidated Endline Report: FOUND
- **Citation (printed p.2):** Woldeyohanes T., Kegode H., Hughes K., Outtara I., Vågen T.-G., Winowiecki L.A., Kleinsmann J., Prabhu R., Bourne M. 2023. *Regreening Africa Consolidated Endline Survey Report*. World Agroforestry, Nairobi. 60 pp, A4 landscape, InDesign export, **text layer OK**.
- **Publisher URL:** `https://regreeningafrica.org/wp-content/uploads/2023/08/Endline-Report_21_08_23_Online.pdf`
  - It now returns **404**, which is why the probe failed.
  - The verified copy is at `http://web.archive.org/web/2026id_/https://regreeningafrica.org/wp-content/uploads/2023/08/Endline-Report_21_08_23_Online.pdf` (19.3 MB).
  - A French version is at `/2023/12/Endline-Report_French_2023.pdf`.
  - Nothing is on CGSpace.
  - **Action:** a human should mirror the file to SharePoint and set `library_path`. The publisher domain is dead, so `url` should cite the original path plus the archive copy.

**What it actually reports (verbatim, printed page numbers; PDF page = printed + 1):**
- **Design (p.4):**
  - "A total of 9,835 households were intervened at baseline. Of these, 7,683 were reinterviewed at endline."
  - "The original plan was to assess programme impact by comparing households targeting earlier on in the programme with those targeted in its last year. However … led to the abandonment of this strategy."
  - What remains is a before–after comparison plus first-difference associations.
- **Adoption (p.5):**
  - "household engagement in regreening practice rose from 55% to 88%"
  - "Tree density also increased from an average of 43 trees per hectare at baseline to 120 trees per hectare at endline"
  - "189,562 Hectares of land were regreened … representing 47% of the target"
  - "152,251 households … representing 65% of the direct scaling target"
- **SOC (p.5, p.37):** "The mean SOC increased by only 0.31 gC kg-1 overall, which represents a relative increase of 3 percent."
- **Erosion:**
  - p.38: "We do not observe large changes in soil erosion across the project overall, except in Kenya."
  - p.39: "We found no statistically significant association between the numbers of trees upscaled on the main field and changes in predicted erosion prevalence."
- **Income (p.6):**
  - "The sale of tree-related products increased from 8% to 20%"
  - "the overall average income per household from tree products did not change, remaining at USD 82 purchasing power parity (PPP)"
- **Food security (p.44):**
  - "The FIES score showed no substantial change over the project period. The overall score dropped from 4.9 to 4.8 out of the 8 possible points"
  - MDD-W cut-off rose "from 16 to 21, a 31 percent increase compared to the baseline"
  - p.45 (FIES association): significant only in Ghana, and "contrary to our expectation … positive and statistically significant in the case of Kenya and Niger"
- **Drought:**
  - The word appears only in context passages (p.9: SDG 15.3; p.38: erosion after prolonged droughts).
  - **There is no drought-conditional outcome.** The snippet figure "40% fewer food-insecure months during drought" **does not appear in this document.** Treat it as fabricated or mis-attributed.
- **Gender (p.26):** "women's involvement in decision-making and labour contribution declined in Ethiopia" (mixed across countries).
- **Routing:**
  - T6: food security is null or modest, erosion is null, SOC rises slightly, adoption is strong.
  - **T3: nothing.**
  - Because the findings are null or modest, this programme self-evaluation shows little positive spin.

## Draft SRCH rows (grey)
```
nbs_id=agroforestry | suitability_family_id="" | table=T3 | process=grey
search_terms = CGSpace DSpace7 API C1–C11 (verbatim above); Regreening Africa resources page via Wayback snapshot 20260422042137; web W1–W20 (verbatim above; W1 `"Regreening Africa" "endline" report pdf`, W2 `regreeningafrica.org endline survey consolidated report 2023`); direct fetches 3ie EGM29 / CCB pages, GEF IEO VfM-2016 / SCCE-drylands / blog, IFAD DECOFOS + IOE BF (403)
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = ex-post MEL / impact assessment / endline / programme evaluation / institutional synthesis (CGIAR MELIA·SPIA, GEF IEO, IFAD IOE/IA, 3ie, FAO OED, WV, CRS, IPCC/IPBES) reporting an OBSERVED agroforestry outcome under a T3 hazard (livelihood impact or asset damage); exclude PADs, placeholders, ex-ante CBA/scenario models, bundled packages without agroforestry disaggregation, lineage duplicates of known sources, WOCAT (PAUSE)
limits = CGSpace size 15–40/query; web ~9–10 results/query; screen<=80; include<=25 (shared with T6)
n_retrieved≈435 | n_screened=44 | n_included=2 (af_grey_mel_04 [drought, weak], af_grey_mel_10)
search_date=2026-10-02 | run_id=grey_mel_af_t3t6_2026-10-02 | searched_by=discovery-agent (grey MEL) | ruleset_version=v1.6.0
note = grey MEL channels yield almost no hazard-conditional agroforestry evidence; [CORRECTED 2026-10-04: the GPP +14% drought number is NOT in the IEG PPAR — it was read in the SCCE Drylands evaluation, which is not acquired; claim unusable]; IFAD + USAID channels tool-blocked → not saturated
```
```
nbs_id=agroforestry | suitability_family_id="" | table=T6 | process=grey
search_terms = (same strings as T3 row — single pass, both tables)
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = as T3 row but outcome = T5 priority (yield/production_gap, poverty/food security, erosion, carbon, biodiversity, water, gender) or economics with a per-unit denominator or observed adoption/dis-adoption
limits = as T3 row
n_retrieved≈435 | n_screened=44 | n_included=11
search_date=2026-10-02 | run_id=grey_mel_af_t3t6_2026-10-02 | searched_by=discovery-agent (grey MEL) | ruleset_version=v1.6.0
note = complements probe grey row (WB ICR channel); do NOT stamp searched=done — IFAD/USAID/FAO-OED not exhausted
```

## Human flags
1. **Regreening endline:** mirror the Wayback copy to SharePoint (the publisher link is dead).
2. **IFAD (bot-blocked):**
   - Download in a browser: DECOFOS Mexico IA (`ifad.org/documents/d/new-ifad.org/mx_decofos_ia-report-pdf`), IOE Burkina Faso SWC/AGF evaluation, and *Strengthening agroforestry in rural investments* (IFAD).
   - DECOFOS may hold agroforestry-disaggregated NDVI results.
3. **SPS Caquetá brief:** the text layer has no numbers. Find the underlying Alliance working paper or dataset with the DiD coefficients.
4. **Unattributed claim:** "farmers practicing agroforestry in Kenya experienced 25% greater food security than conventional farmers during a prolonged drought" came from a search-engine summary that pointed to worldagroforestry.org news, "Surviving drought through agroforestry". **Not traced to a document**, so it is the same risk as the Regreening snippet. The likely primary is Thorlakson & Neufeldt 2012 (peer-reviewed; sibling agent). Verify before any use.
5. **Lineage:** GEF SCCE drylands repeats IEG 2020a/b (the Ethiopia SLMP PPAR). When extracting the PPAR, capture the 14% GPP severe-drought figure from the primary.
6. **Check ResearchGate / WV MEL for:**
   - Larwanou et al. 2006 (IRG/USAID Zinder, FR)
   - the Beysatol (Senegal) endline
   - the WV East Africa FMNR endlines that the WV 2019 brief synthesises
   - the AFSP Malawi CIE evaluation 2011
7. **Family mapping:** Place 2005 "improved fallows" (rotational planted fertilizer trees) has no exact FAM id. It is tagged `tree_intercropping|alley_cropping`, which needs ratifying.
8. **IPCC author lists** (SRCCL Ch6: Smith, Nkem, Calvin…; AR6 WGIII Ch7: Nabuurs, Mrabet, Abu Hatab…) should be confirmed from the chapter front matter.

## What the grey MEL pass added

**T3 (by hazard):**
- **drought:** nothing new and agroforestry-specific. The WV 2019 brief only cites literature. SRCCL Ch6 gives IPCC-confidence ordinal ratings for agroforestry on desertification and adaptation. The best number is GEF SCCE → IEG PPAR, which is lineage.
- **heat, flood, wind/cyclone, fire, frost, waterlogging:** **zero** MEL evidence.
- **asset_vulnerability:** **zero.** No MEL report measured tree survival under a hazard. FAO AAD explicitly did not monitor survival.
- **Implication for v1.6.0:** project grey literature will not fill the T3 hazard gaps. Hazard-conditional evidence has to come from the literature or synthesis lane.

**T6 (by target):**
- **economics:** first per-unit costs from ex-post spend (CRS: FMNR USD 58/ha and USD 66/household in Ghana; planted agroforestry USD 1,387/ha and USD 201/household in Rwanda), plus IPCC ≤USD100/tCO2 economic potential.
- **adoption:**
  - Regreening Africa: engagement 55→88%, density 43→120 trees/ha
  - SPIA Ethiopia national panel: afforestation 10.1→13.6%, avocado on farms 12.5→16.5%
  - CCAFS CSV FMNR shares
  - IFPRI RR142 adoption and dis-adoption
- **rural_poverty / food security:** Regreening is null on FIES and modest on MDD-W. Talensi improved on hungry months (68.2→41%, before–after, bundled). Coulibaly 2016 (ESR, Malawi) and WV East Africa (+15 pp reported income) are positive.
- **production_gap:** IFPRI RR142 maize-yield gains (median +122 to 167%); Coulibaly (Malawi); SPS Caquetá (directional only).
- **soil_erosion_risk:** Regreening is null. SRCCL Ch6 is ordinal.
- **carbon:** Regreening SOC +3%; SRCCL 0.1–5.7 GtCO2e/yr; AR6 WGIII Ch7 potential.
- **gender:** Regreening (mixed, declining in Ethiopia); WV 2019 (qualitative).

**Grey positive-bias note:** the two largest and most independent sources (Regreening endline, SPIA) are the least positive. The implementer briefs (WV, Talensi) are the most positive. This supports applying the COI discount in synthesis.

## Saturation summary
| channel | saturated? |
|---|---|
| CGSpace (CGIAR MELIA/SPIA/CCAFS) | ~yes (ERA database = PAUSE pointer) |
| Regreening Africa site | yes (via Wayback) |
| 3ie | yes (EGMs = pointers to peer-reviewed lane) |
| IFAD IOE/IA | **no** (bot-blocked; 3 human downloads) |
| GEF IEO | yes for agroforestry-disaggregated content |
| FAO OED | partial (2 queries) |
| World Vision FMNR | yes for public docs; rest needs WV MEL |
| USAID / GIZ / DFID / Sida | **no** (DEC unavailable; portals not queried directly) |
| IPCC / IPBES | IPCC yes; IPBES unchecked |
