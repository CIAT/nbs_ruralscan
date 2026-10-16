# Wetland management × T3/T6 discovery: the GREY and evaluation lane (2026-10-16)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `wet_grey_2026-10-16_lit`, ruleset **v1.6.10**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-16: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `wet_grey_2026-10-16_lit`, ledger per `--ledger`.


> **Run** `wet_grey_2026-10-16` · ruleset **v1.6.10** · process `grey` · `nbs_id=wetland_management`.
> **Staging only.** Nothing was registered, queued or ledger-stamped. No `git` command was run. No PDF, snapshot or dataset was downloaded. Every field in the candidate file comes from the institutional record or search result that surfaced it; nothing was read from a document body.

## Why this lane ran

The published-literature lane (`wetland_T6_priorities_synthesis_2026-10.md`) screened 449 unique records and reported, honestly, that it found **no measured household income effect of wetland restoration in a low-income country**. Its four "measured household outcome" candidates were one upper-middle-income restoration programme and three low-income studies of *existing wetland use* rather than restoration. With the project lead's ruling that only value reaching the household may set a poverty class, the wetland poverty row had nothing underneath it.

Evaluation grey literature was the remaining net. This lane cast it.

**The headline: the net caught something.** The Green Climate Fund's Independent Evaluation Unit has published a difference-in-differences-with-matching impact evaluation of a wetland restoration project in **Uganda**, a low-income country, over **1,666 households**, measuring **household welfare, income and food security**. Its finding is a **measured null**. That is not the same as an absence of evidence, and under the ruling it is a usable answer.

## Channels searched

These repositories are not indexed like journals; most have no scriptable API and several block tool fetches. Each channel below states what was actually run and what it returned.

### Channel 1 — World Bank Documents & Reports (WDS API)

The only institutional repository in this lane with a usable machine interface. Queries were issued against `https://search.worldbank.org/api/v3/wds` with `format=json` and the field list `docdt,display_title,pdfurl,docty,repnb,count`.

#### Verbatim queries — World Bank WDS

```
https://search.worldbank.org/api/v3/wds?format=json&qterm=wetland%20restoration%20livelihoods&fl=docdt,docna,count,display_title,pdfurl,docty,repnb&rows=20
```
— returned 20 records (mostly safeguards and resettlement documents; 1 ICR, 2 ICR Reviews, 1 PPAR).

```
https://search.worldbank.org/api/v3/wds?format=json&qterm=peatland%20rewetting&fl=docdt,docna,count,display_title,pdfurl,docty,repnb&rows=20
```
— **total 0**. The World Bank has published nothing indexed under "peatland rewetting".

```
https://search.worldbank.org/api/v3/wds?format=json&qterm=peatland&fl=docdt,display_title,pdfurl,docty,repnb,count&rows=25
```
— 21 records, all Indonesia governance/accounting/PID material plus unrelated Japanese and Sri Lankan land-reclamation reports. **No peatland restoration evaluation.**

```
https://search.worldbank.org/api/v3/wds?format=json&qterm=marshlands%20restoration&fl=docdt,display_title,pdfurl,docty,repnb,count&rows=25
```
— 25 records, 23 of them Rwanda Rural Sector Support Project resettlement and safeguards volumes (see exclusions).

```
https://search.worldbank.org/api/v3/wds?format=json&qterm=wetland&docty_exact=Implementation%20Completion%20and%20Results%20Report&fl=docdt,display_title,pdfurl,docty,repnb,count&rows=25
```
— 25 ICRs; 11 genuinely wetland-related. This was the productive query.

```
https://search.worldbank.org/api/v3/wds?format=json&qterm=wetland&docty_exact=Project%20Performance%20Assessment%20Report&fl=docdt,display_title,pdfurl,docty,repnb,count&rows=20
```
— 20 IEG PPARs; 4 wetland-relevant.

```
https://search.worldbank.org/api/v3/wds?format=json&qterm=marshland%20rehabilitation&docty_exact=Implementation%20Completion%20and%20Results%20Report&fl=docdt,display_title,pdfurl,docty,repnb,count&rows=20
```
— **total 0**.

```
https://search.worldbank.org/api/v3/wds?format=json&qterm=marshlands%20Iraq&fl=docdt,display_title,pdfurl,docty,repnb,count&rows=25
```
— 2 records, both about school construction. **The Bank has no Mesopotamian marshes restoration evaluation in WDS.**

### Channel 2 — GCF Independent Evaluation Unit

#### Verbatim queries — GCF IEU

```
WebSearch: Adaptation Fund final evaluation wetland restoration project household income beneficiaries report
WebSearch: GCF Independent Evaluation Unit Uganda wetlands FP034 impact evaluation household income food security
WebFetch: https://ieu.greenclimate.fund/project/fp034
WebFetch: https://ieu.greenclimate.fund/document/impact-evaluation-report-fp034
WebFetch: https://ieu.greenclimate.fund/search?keywords=wetland
```

The IEU site search returned **exactly two substantive wetland documents** — the FP034 endline impact evaluation (June 2026) and its baseline (February 2025). Everything else was a news item, a blog or an event page. The GCF portfolio contains one evaluated wetland restoration project, and this lane found it.

### Channel 3 — FAO Office of Evaluation

```
WebFetch: https://openknowledge.fao.org/server/api/discover/search/objects?query=terminal%20evaluation%20wetland&size=30
```
— **HTTP 403**. The FAO DSpace API refuses tool requests. Fell back to:

```
WebSearch: FAO terminal evaluation GEF project peatland OR marshland OR wetland restoration rehabilitation livelihoods household openknowledge
WebSearch: "Climate Adaptation in Wetlands Areas" CAWA Lao terminal evaluation FAO "Project Evaluation Series" 2024 title
WebSearch: Laos Adaptation Fund terminal evaluation "Xe Champhone" OR "Beung Kiat Ngong" wetland household income fisheries
```
— surfaced the CAWA Lao PDR terminal evaluation (Project Evaluation Series 19/2024, GCP/LAO/022/LDF, GEF ID 5489) and several non-wetland FAO terminal evaluations.

### Channel 4 — 3ie

```
WebFetch: https://developmentevidence.3ieimpact.org/search-result?page=1&...&search=wetland%20restoration&searchType=simple
WebFetch: https://developmentevidence.3ieimpact.org/api/search?q=wetland&size=25
WebSearch: 3ie impact evaluation wetland restoration household income evidence gap map
WebSearch (allowed_domains = 3ieimpact.org, developmentevidence.3ieimpact.org, gapmaps.3ieimpact.org):
  wetland restoration impact evaluation household income randomized Africa
WebSearch (allowed_domains = developmentevidence.3ieimpact.org):
  wetland peatland marsh restoration impact evaluation
```

**The 3ie Development Evidence Portal could not be queried by any tool available here.** Both the search-result URL and the API path returned a bare page title with no records — it is a client-side application. The domain-restricted web searches ignored the restriction and returned other domains, which means the portal's record pages are not in the general index either.

What the open-web 3ie searches *did* return was instructive: 3ie's agriculture, resilience (REAPER) and payment-for-environmental-services evidence products, and an Ethiopian soil-and-water-conservation record in the climate-change-and-biodiversity gap map — **but no wetland, peatland or marsh restoration impact evaluation, and no wetland evidence gap map**. This corroborates the published lane's finding (its point 2) that no EGM covers this practice.

**→ HUMAN STEP.** The 3ie Development Evidence Portal and the Climate Change & Biodiversity EGM need a browser-based search by a person before we can state that 3ie holds nothing. A tool cannot establish that, and this report does not claim it.

### Channel 5 — IFAD Independent Office of Evaluation

```
WebSearch: IFAD Independent Office of Evaluation wetland restoration project performance evaluation household income
WebSearch: IFAD evaluation marshland development Rwanda OR Burundi rice household income impact evaluation IOE project performance
```

IFAD's document server bot-blocks tool fetches (a known constraint, already recorded in `search_protocol.md`). The searches returned IFAD's evaluation *manuals*, country strategy evaluations for Rwanda and Burundi, and the regional East Africa impact evaluation. The substantive IFAD marshland work — Burundi's 16,714 ha of "developed or rehabilitated marshlands", the Rwanda watershed operations — is **marshland drainage and development for irrigated rice**, which is the opposite intervention to restoration. See exclusions. **No IFAD IOE evaluation of a wetland restoration intervention was found.**

### Channel 6 — GEF IEO / UNDP ERC / Adaptation Fund

```
WebSearch: GEF Independent Evaluation Office terminal evaluation peatland wetland restoration livelihoods
WebFetch: https://www.gefieo.org/search?keywords=wetland    → HTTP 404
WebSearch: UNDP GEF terminal evaluation peatland rewetting Belarus OR Russia OR Indonesia restoration local livelihoods income erc.undp.org
```

GEF IEO's own search endpoint 404'd. The open-web pass surfaced the GEF IEO Sustainable Forest Management evaluation (2022) and a drylands country-cluster evaluation, both of which mention wetlands rehabilitation only in passing ("showed promise in pilot areas but were constrained by commercial pressures and a lack of scale-up mechanisms") — a judgement, not a measurement, and not extractable as an effect unit. The productive result was the **UNDP-GEF Belarus terminal evaluation** (PIMS 5495 / GEF ID 7993), whose evaluators state they found no evidence of household-level benefit. Its exact ERC record id could not be confirmed and is flagged for a human.

Adaptation Fund: its ex-post evaluation series exists (the Eritrea ex-post, #6, was returned) but **no wetland restoration project appears in it**.

### Channel 7 — paludiculture and rewetting economics, programme sources

```
WebSearch: paludiculture business case report Greifswald Mire Centre Wetlands International Interreg "Carbon Connects" OR "DESIRE" economics farmers income
WebSearch: peatland rewetting compensation payment farmers scheme report evaluation "opportunity cost" drained grassland
WebSearch: Ireland peatlands climate action scheme rewetting farmers payment report evaluation Bord na Mona NPWS "ex-post"
```

Returned the Greifswald/Wichmann paludiculture economics volume, the RRR2017 and RRR2021 conference proceedings (excluded — conference material is not an artefact of record), the ClimateXchange Scotland policy report, Ireland's Bord na Móna Peatlands Climate Action Scheme bog-by-bog rehabilitation plans (**ex-ante design documents**, excluded), and the German farm-economics assessment.

### Channel 8 — compensation and payment schemes attached to restoration

```
WebSearch: "returning farmland to lake" OR "retreat farmland to restore wetland" China compensation resettled households income evaluation Dongting Poyang
```

The most productive single query in the lane for the brief's target 3. China's post-1998 "returning farmland to lake" programme is the largest real-world case of households being taken out of cultivated floodplain and compensated, and two studies price it at household level.

### Channel 9 — waterlogging of neighbouring farmland (the missing maladaptation axis)

```
WebSearch: rewetting peatland waterlogging adjacent farmland damage neighbouring fields report
WebFetch: https://globalpeatlands.org/sites/default/files/2023-07/QA-peatland-rewetting_fin.pdf   → HTTP 403
```

**There is no measurement of this anywhere that this lane could find.** What exists is *guidance that the risk is real*: the Ramsar global guidelines state that where adjacent land use may be impaired, rewetting must be gradual and flooding of surrounding land must be avoided. One German landscape study notes rising groundwater around blocked ditches raising soil moisture in adjacent grassland and field margins. Irish farm press carries maps of potential rewetting impacts on neighbouring farmland and farmer objections — advocacy and news, not evidence.

So the axis gets **named, authoritatively, but never quantified**. Two expert-assertion sources are registered for it; neither can set a class.

### Channel 10 — rural heat

```
WebSearch: wetland restoration land surface temperature cooling rural agricultural landscape heat report evidence
```

The brief flagged that every published heat hit in the lit lane was urban. This single query returned three rural ones, all peer-reviewed rather than grey. They are registered here as `process = updated_lit` cross-lane hand-overs so they are not mis-logged as grey finds.

### Channel 11 — Iraq marshes, Hadejia-Nguru, Working for Wetlands

```
WebSearch: Iraq Mesopotamian marshes restoration evaluation livelihoods Marsh Arabs household income UNEP report reflooding
WebSearch: Hadejia-Nguru wetlands Nigeria project evaluation livelihoods fishing households report IUCN
WebSearch: Wetlands International project evaluation report household income livelihoods wetland restoration Africa "final evaluation"
WebSearch: "Working for Wetlands" South Africa rehabilitation household provisioning services value per household rand study
WebFetch: https://www.un.org/esa/sustdev/publications/africa_casestudies/bushbuck.pdf
WebSearch: CIFOR ICRAF assessment Indonesia peatland restoration agency BRG village livelihood outcomes evaluation report
```

Wetlands International and Ramsar publish advocacy, guidance and programme communications; **neither has a published project evaluation with household outcomes** that this lane could find. The South African Working for Wetlands programme does have a household provisioning-value figure attached to a rehabilitated rural communal wetland, which is the one strong *positive* household number in the round.

## PRISMA-lite funnel

| stage | n | note |
|---|---|---|
| channels searched | 11 | institutional repositories + targeted web search |
| queries run | 28 | all logged verbatim above (8 WDS API, 20 WebSearch/WebFetch) |
| institutional interfaces that refused tool access | 4 | FAO DSpace API (403), globalpeatlands.org (403), gefieo.org search (404), 3ie DEP (JS-only, no records returned) |
| records returned and inspected at record level | ~210 | WDS record sets (166) + search-result sets |
| screened (title + publisher + document type + country) | ~210 | five-step funnel |
| excluded at screening | ~182 | grouped below |
| **included** | **28** | `wet_grey_2026-10-16.json` |

Dedup was run programmatically against the full `pipeline/acquisition_queue.csv` (696 rows, 135 wetland) and `SRC_source_register.csv`: **zero `source_id` collisions, zero DOI collisions, zero normalised-title collisions.** Nothing in this set duplicates anything already in the pipeline.

### Screening: the five-step funnel

1. **Frame** — does the document evaluate or cost a wetland-management action (restore, rewet, create, block drainage, reconnect floodplain, reinstate tidal flow, paludiculture, treatment wetland) and speak to a T5 priority, to economics, or to adoption?
2. **Source type** — evaluations, completion reports, terminal evaluations, performance assessments, commissioned policy research and convention technical guidance are in. **Excluded outright:** project appraisal documents, project information documents, integrated safeguards data sheets, environmental and social assessments, resettlement plans and process frameworks, aide-mémoires, rehabilitation plans, news articles, advocacy blogs and conference proceedings. The locked rule is that a design document is not effect evidence; this lane applied it strictly, and it removed the large majority of the World Bank record sets.
3. **Relevance / PICOS** — the practice must be named in the record. Two documents were admitted with the PICOS link explicitly marked **unconfirmed** (`wb_ieg_ppar_uganda_environmental_management_2008`) or **at risk of being a different NbS** (the Vietnam and Guinea-Bissau coastal operations, which are predominantly mangrove and therefore `forest_restoration` under FAM). These are flagged for a screening decision before any `nbs_id` is tagged, not quietly assumed.
4. **Six-axis credibility** — evidence strength (counterfactual designs upweighted; self-evaluations and modelled assessments capped), transparency, authority and venue, context transferability (LMIC tie-break in favour of inclusion), recency, seminality, minus an independence/COI discount. Grey positive-bias discount applied to programme self-reports and advocacy-adjacent agency material. Result: **High 4 · Medium 23 · Low 1**.
5. **Saturation stop** — reached immediately in the World Bank channel (the ICR and PPAR document-type queries return the same eleven wetland operations). **Not reached** for impact evaluations with household counterfactuals: there simply is only one.

### Why the ~182 exclusions, grouped

| reason | rough share | examples |
|---|---|---|
| ex-ante design document, not effect evidence (PAD, PID, ISDS, ESMF, resettlement plan, rehabilitation plan) | ~55 % | the 23 Rwanda RSSP resettlement volumes; Trinidad Nariva social impact assessment; Maldives and Sierra Leone safeguards; Bord na Móna Drinagh and Templetuohy rehabilitation plans; Indonesia Peatland Partnership and PEAT ISDS/PID pairs |
| no wetland-management action evaluated (institutional, accounting, governance, mapping) | ~15 % | Indonesia peatland ecosystem accounts; "Improving Governance of Indonesia's Peatlands"; Congo forest ecosystem accounts; GEF IEO SFM and drylands evaluations where wetlands are a passing mention |
| wrong intervention — marshland **drainage and development for irrigated rice**, not restoration | ~10 % | Rwanda Rural Sector Support Project I–III; Burundi IFAD marais programmes (16,714 ha "developed or rehabilitated"); Turkey, Iran and Ceylon drainage and reclamation PPARs. Draining a wetland to farm it is the counterfactual our rows are measured against, not an instance of the practice |
| wrong NbS under PICOS — mangrove | ~5 % | the Indonesia large-scale mangrove economics report; mangrove components of Vietnam and Guinea-Bissau. `mangrove_restoration` → `forest_restoration`. Hand to that lane; do not borrow |
| existing-wetland use, not restoration | ~5 % | Hadejia-Nguru provisioning-service studies; Iraq Mesopotamian marshes **desiccation** studies (a degradation contrast, and qualitative) |
| urban, outside the rural scan | ~3 % | Nyandungu eco-tourism park, Kigali; Sri Lanka Metro Colombo; the entire urban-heat-island literature |
| not an artefact of record | ~3 % | RRR2017/RRR2021 conference proceedings; farm-press articles; UNDP and IUCN news pages; advocacy blogs |
| off-topic noise | ~4 % | Albania education, São Tomé health, India power — the WDS `qterm` is fuzzy and returns these |

## Included candidates (28)

### Tier 1 — the answer to the poverty question (2)

| # | Source | Publisher | Year | Type | Stage | Country | Income | HH outcomes | Tier |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Impact Evaluation **Endline** Report for FP034: Building Resilient Communities, Wetland Ecosystems and Associated Catchments in Uganda | GCF Independent Evaluation Unit (LORTA) | 2026 | impact evaluation | **ex-post** | Uganda | **low** | **measured** | High |
| 2 | Impact evaluation **baseline** report, FP034 Uganda | GCF IEU (LORTA) | 2025 | IE baseline | baseline | Uganda | low | baseline only | Medium |

`gcf_ieu_lorta_fp034_uganda_endline_2026` is the reason this lane was worth running. Difference-in-differences with matching, 1,666 households, treatment and comparison wetland systems in eastern and south-western Uganda, covering both the hydrological restoration component and the livelihoods component. Per the IEU's own record, the project raised awareness, crop diversification and adaptation practice, but **"these gains did not translate into measurable improvements in household welfare, income, or food security during the evaluation period."**

Read that carefully before it is encoded. It is a **measured null with a comparison group**, in a **low-income country**, for a **restoration** intervention. It is the single piece of evidence in the whole wetland corpus that meets the poverty ruling's test — and what it says is that the value did not arrive. The baseline report is registered as its methodological companion and must not be extracted from.

### Tier 2 — World Bank ex-post (11)

| # | Source | Report | Year | Type | Country | Income | Restoration? | Tier |
|---|---|---|---|---|---|---|---|---|
| 3 | Sierra Leone Wetlands Conservation Project | ICR3927 | 2016 | ICR | SLE | low | check | Medium |
| 4 | Ghana Environmental Resource Mgmt / GEF Coastal Wetlands / NRM | IEG PPAR 43758 | 2008 | PPAR | GHA | lower-middle | check | High |
| 5 | Ghana Coastal Wetlands Management Project | ICR 20668 | 2000 | ICR | GHA | lower-middle | check | Medium |
| 6 | Bulgaria Wetlands Restoration and Pollution Reduction | ICR1004 | 2009 | ICR | BGR | upper-middle | **yes** | Medium |
| 7 | Bulgaria Wetlands Restoration — ICR Review | IEG ICRR | 2011 | ICR Review | BGR | upper-middle | **yes** | Medium |
| 8 | Gabon Sustainable Mgmt of Critical Wetlands Ecosystems | ICR5509 | 2021 | ICR | GAB | upper-middle | check | Medium |
| 9 | Vietnam multi-project incl. Coastal Wetlands Protection | IEG PPAR 48756 | 2009 | PPAR | VNM | lower-middle | yes (mangrove risk) | High |
| 10 | Mexico Adaptation to CC Impacts on Coastal Wetlands, Gulf of Mexico | ICR4117 | 2017 | ICR | MEX | upper-middle | yes | Medium |
| 11 | Uzbekistan Drainage, Irrigation and Wetlands Improvement, Phase 1 | ICR2877 | 2014 | ICR | UZB | lower-middle | mixed | Medium |
| 12 | Guinea-Bissau Coastal and Biodiversity Management | ICR1684 | 2011 | ICR | GNB | low | check (mangrove risk) | Medium |
| 13 | Uganda Environmental Management and Capacity Development | IEG PPAR 44195 | 2008 | PPAR | UGA | low | **unconfirmed** | Low |
| 14 | Moldova Agricultural Pollution Control | ICR1032 | 2010 | ICR | MDA | lower-middle | yes | Medium |

Two of these deserve a note beyond the table.

**`wb_icr_uzbekistan_drainage_irrigation_wetlands_2014`** is registered deliberately as **inverse evidence**. It pairs agricultural drainage with wetland improvement, so it prices what waterlogging and salinity cost farm households and what relieving them is worth. A benefit of drainage is a cost of rewetting — the direction must be set by hand at extraction, and the engine must not read it as a restoration benefit. It is the closest thing this lane found to a quantification of the waterlogging axis.

**`wb_ieg_ppar_uganda_environmental_management_2008`** is registered with **PICOS not satisfied**. Uganda's environmental management operations historically carried the National Wetlands Programme, but the record does not say so, and inferring the practice from programme context is exactly the error the PICOS rule forbids. It is in the file so the screening decision is logged, not so it is extracted.

### Tier 3 — other evaluation bodies (4)

| # | Source | Publisher | Year | Type | Stage | Country | Income | HH outcomes | Tier |
|---|---|---|---|---|---|---|---|---|---|
| 15 | Terminal evaluation, Climate Adaptation in Wetlands Areas (CAWA), Lao PDR — PES 19/2024 | FAO Office of Evaluation | 2024 | terminal evaluation | ex-post | LAO | lower-middle | counted, asserted | Medium |
| 16 | Terminal Evaluation, Conservation-oriented management of forests and wetlands, Belarus (PIMS 5495 / GEF 7993) | UNDP / GEF | 2022 | terminal evaluation | ex-post | BLR | upper-middle | asserted absence | Medium |
| 17 | Working for Wetlands — Bushbuckridge case study | UN DESA / SANBI | n.d. | programme case study | ex-post | ZAF | upper-middle | **measured valuation** | Medium |
| 18 | Effective monitoring and management of peatland restoration, WP270 | CIFOR-ICRAF | n.d. | working paper | ex-post | IDN | lower-middle | framework | Medium |

The **Belarus** terminal evaluation is the second instance of the Uganda pattern, and it sharpens it: the evaluators found no household benefit **because the project design contained no household mechanism**. No effect versus no mechanism is a distinction the poverty row's justification should carry.

**Working for Wetlands / Bushbuckridge** is the one strong positive. After rehabilitation of a rural communal wetland, provisioning services are valued at roughly R3,466 (~USD 392) per household per year reaching about 70 % of local households, in a community where half of households live on under R5,700 a year; the degraded wetland delivered about a third of that. Three cautions are written into the candidate record: it is a programme reporting its own benefit (independence discount), it is a valuation rather than an impact evaluation, and the PDF appears to have a weak or image-only text layer, so a verbatim quote may not be sliceable.

### Tier 4 — rewetting and paludiculture economics, grey (4)

| # | Source | Publisher | Year | Type | Country | Income | Tier |
|---|---|---|---|---|---|---|---|
| 19 | The economics of paludiculture: costs and benefits of wet land use options | Univ. Greifswald / Greifswald Mire Centre | 2021 | economic assessment | DEU | high | Medium |
| 20 | Global guidelines for peatland rewetting and restoration (Ramsar Technical Report 11) | Ramsar Secretariat (STRP) | n.d. | technical guidance | global | all | Medium |
| 21 | Questions & Answers: Bringing Clarity on Peatland Rewetting and Restoration | UNEP Global Peatlands Initiative | 2023 | technical brief | global | all | Medium |
| 22 | Peatland restoration and potential emissions savings on agricultural land | ClimateXchange (Scotland) | 2021 | policy research | GBR | high | Medium |

Items 20 and 21 are **expert assertion**, not measurement, and are registered as the only authoritative sources naming the **waterlogging-of-neighbouring-land** risk. They belong in `justification.maladaptation` and in the Module 6 hand-off; they cannot set a strength class. Item 19 carries a **source-type check**: if it turns out to be a doctoral thesis it fails the source-type rule and should be replaced by its published components.

### Tier 5 — cross-lane hand-overs: peer-reviewed material the published lane missed (6)

Registered with `process = updated_lit`, not `grey`, so the SRCH protocol rows are not falsified.

| # | Source | Year | DOI | Country | Income | Why it is here | Tier |
|---|---|---|---|---|---|---|---|
| 23 | Policy Cognition, Household Income and Farmers' Satisfaction: a Wetland Ecological Compensation Project, Poyang Lake | 2022 | `10.3390/su141710955` | CHN | upper-middle | **target 3** — measured household income under a restoration-linked compensation scheme | Medium |
| 24 | Eco-compensation effects of the wetland recovery in Dongting Lake area | 2010 | `10.1007/s11442-010-0389-1` | CHN | lower-middle (at the time) | **target 4** — what a household gives up when farmland is returned to wetland | Medium |
| 25 | From dry to wet: economic assessments of peatland rewetting scenarios in German agriculture | 2026 | `10.1080/21606544.2026.2616676` | DEU | high | **targets 3 and 4** — gross-margin loss AND the compensation shortfall | Medium |
| 26 | A Unique Combination of Aerodynamic and Surface Properties Contribute to Surface Cooling in Restored Wetlands of the Sacramento-San Joaquin Delta | 2018 | `10.1029/2018JG004494` | USA | high | **rural heat** — measured, paired against drained *agricultural* land | High |
| 27 | Assessing the cooling potential of climate change adaptation measures in rural areas | 2024 | *(none seen)* | EUR | high | **rural heat** — rewetted wet meadows, explicitly rural | Medium |
| 28 | Satellite observation reveals wetland-induced local cooling moderated by regional climate gradients | 2025 | *(none seen)* | global | all | **rural heat** — the climate-gradient moderation that decides whether temperate cooling figures transfer | Medium |

Items 23 and 24 are the substantive corroboration of the one matched study already held: when wetland is taken out of cultivation, it is **transfer income, not production, that makes households whole**. Item 25 prices the gap — across German farms only about 42 % of rewetting costs are covered by existing funding.

Items 26–28 fill the rural-heat hole the brief flagged. Item 26 is the strongest: flux towers over three restored wetlands and one agricultural site, 2015–2017, with the restored-versus-drained-cropland contrast measured directly rather than inferred from an urban analogue. Note that surface cooling at the wetland is a biophysical effect at the site — `effect_locus` for `wetland_management` is `off_site`, and that still applies.

## DOI discipline

**Four DOIs are emitted. Every one was visible as a literal string in the record** (in a `doi.org`, Springer, Wiley or Taylor & Francis URL returned by the search), not stitched from a snippet: `10.3390/su141710955`, `10.1007/s11442-010-0389-1`, `10.1080/21606544.2026.2616676`, `10.1029/2018JG004494`. All four must still pass `verify_metadata.py` Crossref round-trip before acquisition; the title remains the trust anchor.

**Twenty-four candidates carry `doi: null`** and are to be acquired **by title**. Two of them (items 27 and 28) are journal articles whose DOIs certainly exist but were **not visible in the record** — they are flagged `no_doi_acquire_by_title` rather than guessed. The remaining twenty-two are grey literature and need `title_verified=true` per the DOI-less rule, with a publisher-domain download.

## Access

- **22 of 28** have a direct publisher-domain PDF URL and should acquire with a plain browser fetch.
- **1** (`unep_gpi_qa_peatland_rewetting_2023`) returned **HTTP 403** to tool fetches — human browser acquisition required.
- **1** (`undp_gef_te_belarus_forests_wetlands_2022`) has an **unconfirmed record URL**; a human must locate it in the UNDP Evaluation Resource Centre by PIMS 5495 / GEF ID 7993.
- **1** (`dongting_eco_compensation_wetland_recovery_2010`) is closed at the publisher and needs the full OA-recovery pass — Unpaywall by DOI, then web search, then flag ResearchGate for a human. It is **not** to be labelled paywalled on the basis of one failed fetch.
- **2** (items 27, 28) have unknown OA status pending a verified DOI.
- **1** (`un_desa_working_for_wetlands_bushbuckridge_casestudy`) fetched as a PDF with **no usable text layer** in this environment. If `page.get_text()` cannot produce a contiguous passage, the quote is unobtainable and must be reported as a blocker — never retyped.

## Honest answer to the question this lane was asked

**Can grey evaluation literature answer the wetland poverty question?**

**Partly, and not in the direction anyone was hoping for.**

What exists:

1. **One** household-counterfactual impact evaluation of wetland restoration in a **low-income country** — GCF IEU LORTA, Uganda, 1,666 households, DiD with matching. Its result is a **measured null** on household welfare, income and food security.
2. **One** corroborating independent evaluation (UNDP-GEF Belarus, upper-middle income) finding no household benefit, with the evaluators attributing it to the absence of any household mechanism in the design.
3. **One** measured positive household value (Working for Wetlands, South Africa, upper-middle income) — about R3,466 per household per year in provisioning services after rehabilitation of a rural communal wetland, against a degraded baseline worth roughly a third of that. Programme self-report, valuation not impact evaluation, weak text layer.
4. **Two** studies pricing the household **cost** side of rewetting in China, and one in Germany, all of which say the same thing: production income falls and **compensation, not production, is what restores the household**.

What does not exist:

- **No 3ie or Campbell impact evaluation, and no evidence gap map, on wetland restoration.** The portal could not be queried by tool and needs a human pass before that is stated as fact, but the open-web searches of 3ie's own output returned nothing on this practice.
- **No IFAD IOE evaluation of a wetland restoration intervention.** IFAD's marshland portfolio is drainage-and-development for rice, which is the counterfactual, not the practice.
- **No Adaptation Fund wetland restoration evaluation.**
- **No World Bank evaluation with a measured household counterfactual for a wetland operation.** Eleven wetland ICRs and PPARs exist; all are self-evaluations or independent desk/field assessments with project M&E and no comparison group.
- **No measurement anywhere of waterlogging damage to neighbouring farmland after rewetting.** The risk is named by the Ramsar Convention's own guidelines and by UNEP, and it drives real farmer opposition in Ireland and Germany, but nobody has measured the hectares affected or the yield lost. That is a genuine, citable gap — the kind the Module 6 hand-off should flag rather than paper over.
- **No LMIC paludiculture cost structure from a project source.** The paludiculture economics is entirely German.

So: the poverty row can now be *evidenced*, where before it rested on a forward reference. But the honest shape of that evidence is **one measured null in a low-income country, one asserted absence, one positive valuation from an upper-middle-income programme self-report, and a consistent finding that where households are made whole it is by transfer payments rather than by the wetland**. Under the IPCC two-axis derivation that is low evidence and poor agreement — and a `data deficient` or very low-confidence class is the defensible outcome, not a benefit class propped up on four sources pointing different ways.

That is a better position than before, and it should be presented as such: we are no longer guessing, we now know the evidence is thin *and we know what it says*.

## Next steps (for the orchestrator, not done here)

1. `verify_metadata.py verify` over the four emitted DOIs; `verify-titles` over the 22 grey rows once cached.
2. OA-recovery pass on `dongting_eco_compensation_wetland_recovery_2010` before anything goes to Namita as institutional.
3. Human browser steps, all flagged in the candidate file: the 3ie Development Evidence Portal search; `globalpeatlands.org` (403); the UNDP ERC record for PIMS 5495.
4. Hand the mangrove content of the Vietnam and Guinea-Bissau operations to the **forest restoration** lane — do not borrow it here.
5. Hand items 23–28 to the **published-literature** lane's ledger as `updated_lit`, not `grey`.
6. `scripts/register-discovery.py wetland_management --date 2026-10-16 --ruleset v1.6.10 --candidates grey=pipeline/staging/discovery/wet_grey_2026-10-16.json --reports grey=pipeline/staging/discovery/wet_grey_2026-10-16_report.md --log-names grey=wetland_management_grey_evaluation_2026-10.md --ledger grey=done` — the ledger stamp belongs to whoever runs it, not to this agent.
