# Water harvesting & conservation × T3/T6: grey MEL / impact-assessment pass (2026-10-05)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `water_synthesis_first_2026-10-05_grey`, ruleset **v1.6.0**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-05: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `water_synthesis_first_2026-10-05_grey`, ledger per `--ledger`.


- **Scope:** `nbs_id=water_harvesting_conservation`, generic parent (`suitability_family_id=""`), tables T3 + T6.
  - Process `grey` covers the MEL / ex-post evaluation channels.
  - A separate `stock` seed lists the 11 ERA economics primaries.
  - Ruleset v1.6.0. Run id `grey_mel_wh_t3t6_2026-10-05`.
- **Staging only.** Nothing was registered, queued or ledger-stamped, and no git commands were run. PDFs were read in `…/scratchpad/wh_grey/`.
- **Dedup:** checked against `wh_known_sources.json` (175 rows) by DOI and normalised title. None of the 20 grey includes is in the WH list. Two are already in SRC under agroforestry and are flagged **cross-NbS re-tag**: `ieg_ethiopia_slmp_ppar_2020` and `alemu_spia_ethiopia_2024`. Neither needs new acquisition.
- **Deliverable:** `wh_grey_mel_candidates.json` holds 31 rows: 20 `grey` and 11 ERA `stock`. The ERA rows were pre-specified by Pete, so they do not count against the grey include cap of 25.
- **Page refs** are **PDF page numbers**. WB PPAR/ICR printed page numbers differ: for example, PPAR 61065 printed page = PDF page − 18.

## Funnel (grey, all channels)
| stage | n |
|---|---|
| retrieved (API rows + web results) | ≈ 575 (WB WDS 23 queries ≈ 420 rows shown of ~2,800 hits · CGSpace 13 queries ≈ 195 rows shown · web 8 queries ≈ 75) |
| screened (full text or metadata) | 47 |
| included | **20** (+ 11 ERA stock seeds) |

---

## Channel 1: World Bank Documents & Reports API (ICR / IEG PPAR / ICRR)
Endpoint: `https://search.worldbank.org/api/v2/wds?format=json&qterm=<q>&docty_exact=<doctype>&rows=30&fl=docty,display_title,pdfurl,docdt,repnb,count`

Queries (verbatim `qterm | docty_exact`, total hits):

| # | query | doc type | total |
|---|---|---|---|
| W1 | `watershed management` | ICR | 212 |
| W2 | `watershed management` | PPAR | 61 |
| W3 | `watershed development` | ICRR | 149 |
| W4 | `soil and water conservation` | ICR | 503 ×2 (no count) |
| W5 | `soil and water conservation` | PPAR | 128 |
| W6 | `water harvesting` | ICR | 189 |
| W7 | `water harvesting` | PPAR | 503 ×2 (no count) |
| W8 | `water harvesting` | ICRR | 112 |
| W9 | `sustainable land management` | PPAR | 460 |
| W10 | `Sujala watershed` | ICR | 0 |
| W11 | `Neeranchal` | ICR | 0 |
| W12 | `Uttarakhand watershed` | ICR | 2 |
| W13 | `Himachal Pradesh mid-himalayan watershed` | ICR | 1 |
| W14 | `productive safety net public works` | ICR | 378 |
| W15 | `productive safety net` | PPAR | 90 |
| W16 | `national watershed management` | ICR | 162 |
| W17 | `land husbandry terracing` | ICR | 1 |
| W18 | `soil conservation terraces` | ICR | 3 |
| W19 | `community action plans natural resource management Niger` | ICR | 13 |

Notes on the table:
- Rows marked "503 ×2" returned HTTP 503 twice, so there is no count. W7 (`water harvesting` × PPAR) is effectively covered by W5 and W9.
- The Neeranchal (National Watershed Management Project) ICR is not yet indexed.

**Included (12):**
- IEG PPARs: 61065 India cluster (IWDP Hills II + KWDP), 41122 China Loess II, 48733 Morocco Lakhdar, 82308 Tunisia NRM, 153559 Ethiopia SLMP (re-tag).
- ICRs: 5011 Karnataka II, 5940 Uttarakhand II, 4212 HP Mid-Himalayan, 4539 Rwanda LWH (+ IEG ICRR0021510), 3659 Ethiopia PSNP3, 2516 Yemen GSCP, 2294 Mauritania CBWM.

**Screened out:**
| item | reason |
|---|---|
| PPAR 35004 Yemen LWCP/Taiz/Sana'a | no_outcome (the terrace pilot has "no data on overall achievements", PDF p.20). Its only number is a component-pooled ERR of 15% |
| PPAR 62549 Ethiopia PSNP APL1 | practice (the drought effect of +30% caloric growth, PDF p.33, comes from transfers, not SWC public works) |
| ICR 3537 Kenya KAPSLMP | practice (bundled package; WH not disaggregated) |
| ICR 3503 Tunisia NRM2 | practice (income effect from IGAs/irrigation rehabilitation; SWC not disaggregated) |
| ICR 3074 Ethiopia SLMP-I | lineage (superseded by PPAR 153559, which re-audits it) |
| ICR 1205 Karnataka WDP-I | lineage (re-audited in PPAR 61065) |
| ICRR 0022303 / 0023194 / 0020963 | lineage (IEG validations of included ICRs; useful for COI cross-check, not separate sources) |
| PPAR 41122-adjacent and older 1990s PPARs (Kandi, Himalayan 1996) | recency/superseded (Kandi is summarised inside PPAR 61065, Table 6) |
| ICR 3918 Orissa tanks, ICRR14618 Karnataka tanks | not screened in full (tank rehabilitation = irrigation O&M; reserve) |

**Saturation:** reached for India / Ethiopia / MENA watershed ICR+PPAR. New queries returned already-seen projects by W14–W16.
- Not exhausted: Sahel (Niger CAP ICRs 956/2065/5331 are multi-sector, so not screened) and the Ethiopia SLMP-II ICR.

## Channel 2: CGSpace DSpace 7 API (ICRISAT / IWMI / IFPRI / SPIA)
Endpoint: `https://cgspace.cgiar.org/server/api/discover/search/objects?dsoType=ITEM&size=15&query=<q>`

| # | query (verbatim) | total |
|---|---|---|
| C1 | `Kothapally watershed AND (impact OR evaluation)` | 21 |
| C2 | `ICRISAT AND "watershed" AND ("impact assessment" OR "meta-analysis" OR evaluation)` | 989 |
| C3 | `"water harvesting" AND ("impact assessment" OR "impact evaluation" OR "ex-post")` | 876 |
| C4 | `"soil and water conservation" AND ("impact evaluation" OR "impact assessment") AND (yield OR income)` | 713 |
| C5 | `SPIA AND ("soil and water conservation" OR "water harvesting" OR watershed)` | 149 |
| C6 | `("zai" OR "half-moon" OR "demi-lune" OR "stone bunds") AND (impact OR adoption OR evaluation) AND (Burkina OR Niger OR Mali)` | 583 |
| C7 | `"Adarsha" watershed` | 14 |
| C8 | `("check dam" OR "farm pond" OR "percolation tank") AND (impact OR evaluation) AND (groundwater OR income)` | 617 |
| C9 | `"emergence and spreading of an improved traditional soil and water conservation"` | 30 |
| C10 | `"IWMI Working Paper 98"` | 13 |
| C11 | `"rainwater harvesting" AND Tigray AND ponds AND (impact OR evaluation)` | 73 |
| C12 | `"water harvesting" AND (failure OR siltation OR "dis-adoption" OR abandonment) AND (ponds OR "check dams" OR structures)` | 1571 |
| C13 | `("Jalyukt Shivar" OR "farm ponds") AND (impact OR evaluation)` | 305 |

**Included (7):**
- Joshi et al. 2005 CA-RR8 (meta-analysis)
- Abate et al. 2021 IFPRI DP2069
- Schmidt & Tadesse 2012 ESSP WP42
- Kaboré & Reij 2004 EPTD 114
- Arega et al. 2024 ILSSI note
- SPIA Ethiopia 2024 (re-tag)
- Verma & Shah 2019 WB note (hosted on CGSpace)

**Screened out:**
| item | reason |
|---|---|
| Kothapally farm-income paper (hdl 10568/58305, Agric. Syst. 2015) | peer-reviewed (sibling lane) |
| Kolar groundwater / BMP climate-resilience papers (EJRH 2020/21, Agric. Syst. 2021) | peer-reviewed (sibling lane) |
| SPIA Ethiopia 2020 (Kosmowski et al.) | lineage (earlier wave of SPIA 2024) |
| IWMI WP126 Barry et al. 2008 (Sahel RWH) | lineage (review of on-station trials; e.g. "20% loss in production behind stone" rows cites primaries) |
| IWMI 2025 MGNREGS decade at-a-glance | no_outcome (output inventory) |
| IWMI WP152 Evans et al. 2012 AgWater Solutions Ethiopia | practice (motor pumps / irrigation dominate) |
| Loulseged et al. 2011 AWM inventory | no_outcome (inventory slides) |
| Alaba RWH ponds MSc thesis 2006 (hdl 10568/688) | source_type (thesis; reserve) |
| ISPC 2015 evaluation of CGIAR IA on water management | relevance (meta-evaluation of research) |

**Saturation:** near-saturated for CGIAR ex-post watershed / SWC. C8 and C12 turned over into annual reports and workshop records. The IWMI-Tata Saurashtra recharge WPs (2002) are a reserve.

## Channel 3: 3ie
- Web query (verbatim): `3ie impact evaluation soil and water conservation water harvesting report` (domains 3ieimpact.org, developmentevidence.3ieimpact.org; 10 results).
- **Included: 0.**
  - IE 112 (Byiringo, Jones, Kondylis, *Rwanda irrigation*): screened out as practice. It evaluates LWH hillside irrigation, not WH structures. The headline is "Hillside irrigation increases smallholder yields and cash profits by 70%" (PDF p.5).
  - EGM 12 appendix D: pointer (included-studies list feeds the peer-reviewed sibling).
  - Abebe 2014 (Adama SWC) gapmaps record: pointer (thesis/journal; sibling).
- **Saturation:** reached. 3ie holds few WH-specific IEs, and those it holds are peer-reviewed.

## Channel 4: IFAD IOE
- Web query: `IFAD Independent Office of Evaluation soil and water conservation water harvesting impact evaluation Burkina Faso Niger` (10 results).
- **Included: 0.** `ioe.ifad.org` returns HTTP 403 and `ifad.org` returns 301 to a bot check.
- The snippet says the Burkina Faso Special Programme SWC/AGF had "a 25% increase in food crop yields on 20% to 30% of the land in 489 villages". That figure is **not read in a document** and must not be used.
- IFAD content is partly covered by the IFPRI IE of the IFAD-funded CBINReMP (Abate 2021).
- **Saturation: NOT reached** (tool-blocked).

## Channel 5: GEF IEO
- Web query: `GEF Independent Evaluation Office evaluation land degradation soil and water conservation water harvesting outcomes terraces report` (gefieo.org, thegef.org; 9 results).
- Fetched: the Water Security evaluation (GEF/E/C.64/01/Rev.02, 90 pp) and the Eritrea CPE 2015 (114 pp).
- **Included: 0.**
  - Water security evaluation: no WH outcome. The only hit is an IFAD WH design-tips citation (PDF p.71).
  - Eritrea CPE: outputs only. It cites a Ministry of Education report of "10 million km of hillside terraces and over 800,000 check dams" and says productivity "reportedly more than doubled" (PDF p.62), which is unverified and second-hand.
- **Saturation:** reached for WH-disaggregated GEF content.

## Channel 6: FAO / WFP evaluations
- Web query: `WFP food assistance for assets impact evaluation synthesis soil water conservation Niger Ethiopia evaluation report` (wfp.org, docs.wfp.org; 9 results).
- Second web query: `WFP "Food for Assets" impact evaluation 2002-2011 synthesis report "lessons for building livelihoods resilience" pdf` (9 results).
- **Included: 0.**
  - WFP-0000051011 was fetched. It is the *Sahel nutrition* synthesis, so it is screened out as relevance.
  - The 2014 FFA impact-evaluation series was not located as a PDF on a publisher domain. Uganda and Guatemala summaries are on ALNAP and wfp.org.
  - Niger "Resilience learning in the Sahel" IE (WFP/DIME; half-moons) exists only as a web page. **Human flag.**
- **Saturation: NOT reached.** The FFA series and the Niger half-moon IE still need a browser pass.

## Channel 7: NGO evaluations
Queries (verbatim):
- `sand dams evaluation report Kenya Excellent Development OR Africa Sand Dam Foundation impact groundwater income` (10 results)
- `Oxfam OR "Practical Action" OR "CARE" final evaluation rainwater harvesting water harvesting project evaluation report yield income Ethiopia OR Kenya OR Sudan` (9 results)
- `Kaboré Reij 2004 "emergence and spreading of an improved traditional soil and water conservation practice in Burkina Faso" IFPRI EPTD discussion paper 114` (9 results; used to locate the CGSpace copy)

**Included (1):** MCC Kenya sand-dam assessment (Graber Neufeld 2017).

**Screened out:**
| item | reason |
|---|---|
| Concern Worldwide sand-dam brief (fscluster.org) | unavailable (HTTP 403; **human download**). The snippet claims 30 dams, "83% accumulating volumes … lower than 1000 m³", and that 67% cannot supply one household. Not read, so not usable |
| ODI 2014 *A greener Burkina* (Lenhardt et al.) | lineage (re-reports Reij / Kaboré figures, e.g. "793 kg/ha … 611 kg/ha", PDF p.17) |
| Oxfam America Ethiopia water-for-productive-use | practice (small-scale irrigation policy) |
| Sand-dam peer-reviewed papers (Lasage, Ngugi) | known / sibling |
| *Investment trends and evaluation gaps in RWH in SSA drylands* (Agric. Water Manage. 2026, S0378377426001460) | peer-reviewed review. **Pass to sibling**: it is directly about RWH project-evaluation gaps |

**Saturation: NOT reached.** Oxfam, CRS, WV, Practical Action and IRHA portals were not queried directly.

## ERA economics primaries (stock seed)
- Source: `…/scratchpad/era_wh_econ_codes.csv` (pre-resolved from `ERAg::ERA_Bibliography`, 11 codes in `era_wh_codes.txt`).
- Crossref round-trip on 9 DOIs: all title ratio 1.0 (JS0241, DK0008, NN0385, AN0083, AN0121, NN0102, NN0259, NN0305, HK0259).
- No DOI for two codes:
  - **NJ0007** (Abubaker et al. 2014, Pak. J. Agric. Sci.): Crossref best hit is a different paper (ratio 0.58). Acquire by **title**.
  - **EO0122** (Said & Ameen 2016, Egypt. J. Agron.): exact-title candidate DOI 10.21608/agro.2016.600, **candidate, human-verify**. Its WH relevance is doubtful (sowing method), so a PICOS check is needed.
- The ERA dataset itself stays **PAUSED** (dataset adapter). It is used only as a seed list, and each primary is extracted from its own PDF.
- Several codes are conservation agriculture (DK0008, NN0305, HK0259) and map to `conservation_tillage_mulch`.
- NN0259 (Fox, Rockström & Barron 2005) is the key farm-pond economics paper.

## WOCAT (PAUSED, pointers only, NOT included)
- No new WOCAT search was run. WH WOCAT technologies (1219 zaï, 1587, 1100, 959, 1652, 968, 1614, 2895, 5860, 750 …) are already in SRC/queue.
- Hold everything until the WOCAT QT adapter exists. WOCAT QT §6.3 is the T3 asset-threat seed.

---

## Draft SRCH rows
```
nbs_id=water_harvesting_conservation | suitability_family_id="" | table=T3 | process=grey
search_terms = WB WDS API W1–W19 (verbatim table above; qterm|docty_exact ICR/PPAR/ICRR); CGSpace DSpace7 API C1–C13 (verbatim above); web: 3ie (`3ie impact evaluation soil and water conservation water harvesting report`), IFAD IOE (`IFAD Independent Office of Evaluation soil and water conservation water harvesting impact evaluation Burkina Faso Niger`), GEF IEO (`GEF Independent Evaluation Office evaluation land degradation soil and water conservation water harvesting outcomes terraces report`), WFP ×2, NGO ×3 (verbatim above); direct fetches GEF/E/C.64/01/Rev.02, GEF Eritrea CPE 2015, WFP-0000051011, ioe.ifad.org BF SWC/AGF (403), fscluster CWW sand-dam brief (403)
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = ex-post ICR / IEG PPAR / impact evaluation / endline / institutional synthesis reporting an OBSERVED WH/SWC outcome under a T3 hazard (drought-conditional livelihood outcome) or structure performance/failure/siltation (asset_vulnerability); exclude PADs, ex-ante CBA, bundled packages without WH/SWC attribution, transfer-driven effects (PSNP transfers), lineage duplicates, peer-reviewed (sibling lanes), WOCAT (PAUSE), datasets (PAUSE)
limits = WDS rows=30/query; CGSpace size=15/query; web ~9–10/query; screen<=80; include<=25 (shared with T6)
n_retrieved≈575 | n_screened=47 | n_included=8 (ieg_2011_india_watershed_cluster_ppar, ieg_2007_china_loess2_ppar, ieg_2009_morocco_lakhdar_ppar, ieg_2013_tunisia_nrm_ppar, kabore_reij_2004_ifpri_eptd114_zai, arega_2024_ifpri_ilssi_psnp_public_works, verma_shah_2019_wb_drought_proofing_recharge, neufeld_2017_mcc_sand_dam_assessment)
search_date=2026-10-05 | run_id=grey_mel_wh_t3t6_2026-10-05 | searched_by=discovery-agent (grey MEL) | ruleset_version=v1.6.0
note = drought-conditional WH evidence in grey MEL is qualitative only (Tunisia PPAR: drought "limited soil conservation benefits"; China Loess cisterns "mitigating" drought; zaï low-rainfall-year yields). asset_vulnerability is the grey channel's real yield (MCC sand dams, Morocco gabions, India earthen-dam siltation [secondary]). IFAD/WFP/NGO channels not exhausted → do NOT stamp searched=done
```
```
nbs_id=water_harvesting_conservation | suitability_family_id="" | table=T6 | process=grey
search_terms = (same strings as T3 row — single pass, both tables)
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = as T3 row but outcome = T5 priority (production_gap, rural_poverty, water_stress, soil_erosion_risk, carbon, gender) or economics with a per-unit denominator (cost/ha treated, cost/structure, labour h/ha, BCR/IRR of a WH programme) or observed adoption/dis-adoption
limits = as T3 row
n_retrieved≈575 | n_screened=47 | n_included=20
search_date=2026-10-05 | run_id=grey_mel_wh_t3t6_2026-10-05 | searched_by=discovery-agent (grey MEL) | ruleset_version=v1.6.0
note = 2 includes are cross-NbS re-tags of SRC rows (ieg_ethiopia_slmp_ppar_2020, alemu_spia_ethiopia_2024); ICRs are Bank self-evaluations → COI discount, cross-check with ICRRs; do NOT stamp searched=done (IFAD/WFP/NGO not exhausted)
```
```
nbs_id=water_harvesting_conservation | suitability_family_id="" | table=T6 | process=stock
search_terms = ERA economics meta-dataset seed: ERAg::ERA_Bibliography filtered to ERACODE in (AN0083,AN0121,DK0008,EO0122,HK0259,JS0241,NJ0007,NN0102,NN0259,NN0305,NN0385) — R: suppressMessages(library(ERAg)); b<-as.data.frame(ERAg::ERA_Bibliography); b[b$ERACODE %in% c(...),c("ERACODE","DOI","TITLE","AUTHOR","YEAR")]
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = ERA rows tagged water harvesting / SWC practices with economic outcomes; dataset used as discovery seed only (dataset adapter PAUSED); primaries extracted from their own PDFs; DOI must round-trip (Crossref)
limits = pre-specified code list (11)
n_retrieved=11 | n_screened=11 | n_included=11 (9 DOI-verified; NJ0007 title-only; EO0122 candidate DOI, PICOS check)
search_date=2026-10-05 | run_id=grey_mel_wh_t3t6_2026-10-05 | searched_by=discovery-agent (grey MEL) | ruleset_version=v1.6.0
note = ERA codes resolved upstream to era_wh_econ_codes.csv; T3 stock seed not applicable (economics only)
```

## Human flags
1. **IFAD (403 / bot check).** Download the IOE Burkina Faso SWC/AGF phases 1–2 evaluation in a browser. Its "+25% yields on 20–30% of land" snippet is unverified.
2. **WFP.** Get these in a browser:
   - the 2014 FFA impact-evaluation series synthesis (and the Ethiopia/Niger country IEs)
   - the Niger *Resilience Learning in the Sahel* IE (half-moons)
   - the MERET evaluations
3. **Concern Worldwide sand-dam brief** (`fscluster.org/sites/default/files/2025-04/CWW sand dam brief v2.pdf`) returns 403. Download it manually. Its snippet figures (83% < 1000 m³; 67% cannot supply one household) are **unread**.
4. **MCC sand-dam report.**
   - It is hosted on cyrho.com (author host) and marked draft. Get the MCC-published final.
   - Sand dams have **no FAM subpractice id**. Ratify one (nearest are `check_dams` / `macrocatchment_wh`).
5. **Joshi et al. 2005 CA-RR8.** The body text layer is font-ciphered (garbled). OCR it before extraction. Only the summary page (PDF p.6) is readable.
6. **Primaries to chase from lineage:**
   - Kurian, Dietz & Murali 2003 (EPW). This is the source of "31% of earthen dams silted up within five years", cited in PPAR 61065, PDF p.72.
   - ISRO KWDP Phase I/II impact reports.
   - The DIME LWH terracing IE (Rwanda).
   - The PSNP 2011 Public Works Impact Assessment and the 2014 IE.
   - NABCONS 2017 Jalyukt Shivar assessment.
   - The full ILSSI PSNP-PW assessment.
7. **Arithmetic error** in ICR5940: sediment yield 71.6 → 69.3 t/ha/yr is labelled "(17 % reduction)", but that change is 3.2%. Extractors must not encode 17%.
8. **Ethiopia SLMP PPAR p.66.** The 20%/5% yield dip next to SWC structures is a **CBA assumption**, not an observed value. It is a tempting T3 asset_sensitivity number; do not use it.
9. **Cross-NbS re-tags.** `ieg_ethiopia_slmp_ppar_2020` and `alemu_spia_ethiopia_2024` need `water_harvesting_conservation` added and a WH extraction pass. There is no re-acquisition.
10. **China** was LMIC at evaluation (2007) and is UMIC now. Set `transfer_class` from the study-period income group.

## What the grey MEL pass added

**T3 (by hazard)**
- **drought:** qualitative only.
  - Tunisia PPAR: drought "limited soil conservation benefits", the only negative-conditionality statement.
  - China Loess: cisterns "successfully mitigating adverse effects of frequent periods of drought".
  - Kaboré & Reij: zaï sorghum 300–400 kg/ha in a low-rainfall year vs 0 without.
  - Verma & Shah: drought-proofing framing, but secondary.
  - No document gives a drought-year vs normal-year effect size.
- **flood, heat, wind, fire, frost, waterlogging:** zero.
- **asset_vulnerability:** this is the grey lane's real contribution.
  - MCC sand dams (n = 87 random + 8): erosion 72%, leakage 33%, broken <5%, siltation −10–25% storage, 3 of 14 pump wells working in the dry season.
  - Morocco gabion check dams filled and "nearly lost their original function" without maintenance.
  - India PPAR (secondary): 31% of earthen dams silted within 5 years, 20% worked under 1 year.
  - ILSSI PSNP note: maintenance handed over without support.

**T6 (by target)**
- **production_gap:** KWDP +24–26% rainfed yields vs control (IEG-audited); Uttarakhand DiD +20.8% rainfed; HP +21–29%; Rwanda harvest value +36–60% vs control; PSNP SWC +9.1%; Schmidt +15.2% value of production for early adopters only. The **nulls** are Abate 2021 (no crop-yield effect) and the Ethiopia SLMP MoA IA (yields fell in both treated and control).
- **rural_poverty:** KWDP income +53–54% vs control; Karnataka II +18% vs +11% control; CBINReMP +17.8% (high-participation only); PSNP-PW SWC participation did not raise food security (ILSSI).
- **soil_erosion_risk:** PSNP −12 t/ha soil loss (12 micro-watersheds); China Loess 25 Mt/yr sediment captured; Uttarakhand sediment (arithmetic flagged).
- **water_stress:** KWDP water-table rises (no control); Karnataka II soil moisture +30.5% vs IWMP sites; Uttarakhand water scarcity 73 → 48%.
- **economics (per-unit):** watershed treatment US$261/ha (IWDP Hills II) and US$217/ha (KWDP) vs the Indian norm of Rs 6,000 → 12,000/ha; zaï labour ~300 man-hours/ha; maize-on-terrace NPV USD 285/ha with BCR 1.38 (Rwanda); India watershed meta-analysis BCR 2.14 and IRR 22%; ERRs of 15–22% across ICRs (programme-level, no unit denominator). The ERA stock seeds add 11 plot-level economics primaries (Fox et al. 2005 farm ponds is the key one).
- **adoption:** Uttarakhand 93.7% vs 65.8% control; SPIA Ethiopia SWC on 78.5% of households nationally; Schmidt farmer rankings.

**Grey positive-bias note:** the independent sources (IEG PPARs, IFPRI IEs, SPIA, MCC audit) are the most sceptical. They report nulls, high unit costs and structure decay. The Bank ICRs are the most positive, so apply the COI discount and cross-check against the ICRRs.

## Saturation summary
| channel | saturated? |
|---|---|
| WB ICR / IEG PPAR / ICRR | yes for India / Ethiopia / MENA watershed; Sahel CAP partial |
| CGSpace (ICRISAT / IWMI / IFPRI / SPIA) | ~yes |
| 3ie | yes (pointers to sibling) |
| IFAD IOE | **no** (403) |
| GEF IEO | yes (no WH-disaggregated outcomes) |
| FAO / WFP | **no** (FFA series and Niger half-moon IE not acquired) |
| NGO (MCC / Concern / Oxfam / CRS / WV / Practical Action / IRHA) | **no** (portals not queried directly; Concern brief 403) |
| ERA stock seed | complete for the supplied 11 codes |
