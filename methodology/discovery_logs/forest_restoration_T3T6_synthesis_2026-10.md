# Forest restoration × T3/T6: peer-reviewed synthesis pass (2026-10-06)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `forest_synthesis_first_2026-10-06_lit`, ruleset **v1.6.2**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-06: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `forest_synthesis_first_2026-10-06_lit`, ledger per `--ledger`.


- **Scope:** `nbs_id=forest_restoration`, generic parent search (`suitability_family_id=""`; family tags per candidate), tables T3 + T6, processes **`updated_lit`** (2015+) and **`stock`** (seminal pre-2015), ruleset v1.6.0. Suggested run id: `fr_synthesis_first_lit_2026-10-06`.
- **Synthesis-first.** Meta-analyses, systematic reviews (Campbell/3ie), global syntheses and quasi-experimental pooled studies came first. Primaries were kept only where a cell had no synthesis: mangrove asset failure (Kodikara 2017), wind asset (Gardiner 2021, a review).
- **Staging only.** Nothing was registered, queued or ledger-stamped, and no git commands were run.
- **Dedup:** candidates were checked against all 495 acquisition-queue rows, 253 SRC rows and every candidate in the 2026-08/09/10 FR discovery logs, by DOI and normalised title. None of the 26 included items is already known. Known items the nets surfaced were excluded as duplicates (see below).
- **DOI verification:** every DOI was round-tripped against Crossref (`api.crossref.org/works/<doi>`). The title, first author and year match the citation. Citations were rebuilt from the Crossref author list. `verify_metadata.py verify` must still run at registration.
- **OA:** checked with Unpaywall by DOI for every candidate. Every Unpaywall-closed item was then web-searched for a repository copy.

## Funnel
| stage | n |
|---|---|
| returned (OpenAlex title.search totals, 21 successful queries) + 20 Crossref canon lookups | 1,632 + 20 |
| screened (titles + metadata of top-20 by citations per query; abstracts or web summaries for borderline items) | 338 titles → ~70 metadata/abstract |
| included | **26** (cap ≈ 25) |

## Channel 1: OpenAlex `/works`, `filter=title.search:<q>`, `sort=cited_by_count:desc`, `per-page=20`
The first batch hit HTTP 500 on `|` syntax and then HTTP 429. Queries were rewritten with explicit AND/OR and rerun with a 2 s throttle. The 7 queries that errored are counted once, in their successful rerun.

| # | query (verbatim) | total |
|---|---|---|
| L1 | `(reforestation OR afforestation OR "forest restoration" OR "tree planting") AND ("meta-analysis" OR "systematic review" OR "meta analysis")` | 58 |
| L2 | `("natural regeneration" OR "secondary forest" OR "secondary forests" OR "assisted natural regeneration") AND ("meta-analysis" OR "systematic review" OR synthesis)` | 15 |
| L3 | `mangrove AND ("meta-analysis" OR "systematic review") AND (restoration OR protection OR coastal OR wave OR storm OR carbon)` | 35 |
| L4 | `mangrove AND ("wave attenuation" OR "coastal protection" OR "storm surge" OR cyclone OR tsunami OR "flood protection")` | 517 |
| L5 | `("community forest" OR "community forestry" OR "community-based forest" OR "participatory forest" OR "decentralized forest" OR "forest conservation" OR "protected areas") AND (poverty OR livelihood OR livelihoods OR income OR welfare) AND ("meta-analysis" OR "systematic review" OR review)` | 17 |
| L6 | `(afforestation OR reforestation OR "forest cover" OR forests OR "tree cover") AND ("water yield" OR streamflow OR runoff OR "water availability") AND ("meta-analysis" OR global OR review)` | 44 |
| L7 | `(forest OR forests OR deforestation OR reforestation) AND (flood OR floods OR flooding) AND (global OR review OR developing OR "meta-analysis")` | 42 |
| L8 | `(restoration OR reforestation OR afforestation OR revegetation) AND (erosion OR sediment OR landslide OR landslides) AND ("meta-analysis" OR "systematic review" OR global)` | 5 |
| L9 | `(restoration OR reforestation OR "tree planting" OR "natural regeneration") AND (cost OR costs OR "cost-effectiveness") AND (tropical OR global OR review)` | 35 |
| L10 | `(reforestation OR restoration OR "tree planting" OR seedling OR seedlings) AND (survival OR mortality OR failure) AND ("meta-analysis" OR global OR "systematic review" OR synthesis)` | 108 (dominated by dental "restorations" noise) |
| L11 | `(restoration OR reforestation OR "secondary forest" OR "secondary forests") AND (biodiversity OR carbon) AND recovery AND ("meta-analysis" OR global)` | 9 |
| L12 | `("payments for ecosystem services" OR "payment for environmental services" OR "payments for environmental services" OR REDD OR "REDD+") AND ("meta-analysis" OR "systematic review")` | 33 |
| L13 | `(afforestation OR reforestation OR plantation OR plantations) AND (fire OR wildfire) AND (risk OR severity) AND (review OR "meta-analysis" OR global)` | 0 |
| L14 | `(forest OR forests OR trees) AND ("food security" OR nutrition OR "dietary diversity") AND ("systematic review" OR "meta-analysis" OR global)` | 13 |
| L15 | `(restoration OR reforestation OR afforestation OR forest) AND (biodiversity OR "species richness") AND ("meta-analysis") AND (tropical OR recovery OR restored)` | 4 |
| L16 | `(plantation OR plantations OR "planted forests") AND (fire OR wildfire OR flammability)` | 388 |
| L17 | `(mangrove OR mangroves) AND (restoration OR planting OR rehabilitation) AND (survival OR mortality OR failure OR success)` | 40 |
| L18 | `(tree OR trees OR forest) AND (windthrow OR "wind damage" OR cyclone OR typhoon OR hurricane) AND (review OR "meta-analysis" OR global)` | 53 |
| L19 | `(forests OR "forest cover" OR trees) AND (landslide OR landslides) AND ("root reinforcement" OR review OR global)` | 23 |
| L20 | `(afforestation OR reforestation OR "forest cover" OR deforestation OR "tree cover") AND (cooling OR "land surface temperature" OR "heat stress" OR "local temperature" OR "heat exposure")` | 122 |
| L21 | `("forest landscape restoration" OR reforestation OR "tree planting") AND (livelihoods OR income OR poverty OR "household welfare")` | 71 |

## Channel 2: Crossref canon lookups (`query.bibliographic`)
Twenty known syntheses were looked up to confirm the exact DOI and record. Examples: Crouzeilles 2017, Bernal 2018, Hajjar 2021, Naidoo 2019, Poorter 2021, Brancalion 2019, Crouzeilles 2020, Su 2021, Kodikara 2017, Gijsman 2021, Rasolofoson 2018, Gardiner 2021, Ellison 2017, Farley 2005, Filoso 2017, Menéndez 2020 and Bradshaw 2007. Rozendaal 2019 and Poorter 2021 were confirmed through the DOI endpoint.

## Channel 3: OA recovery (web search)
Search strings, verbatim:
- `Farley Jobbágy Jackson 2005 "Effects of afforestation on water yield: a global synthesis" pdf`
- `Kandel 2022 "Do protected areas increase household income? Evidence from a Meta-Analysis" pdf`
- `Coleman 2021 "Limited effects of tree planting on forest canopy cover and rural livelihoods in Northern India" pdf`
- `Kodikara 2017 "Have mangrove restoration projects worked? An in-depth study in Sri Lanka" pdf`
- `Yang 2023 "Effect of vegetation restoration on soil erosion control and soil carbon and nitrogen dynamics: A meta-analysis"`

Results: Kodikara has a free PDF on bluemangrove.fund. Kandel appears as a chapter of the author's UWA thesis, which is a different artefact. Farley, Yang and van Dijk have no repository copy found. ResearchGate was not tool-verifiable, so these items are marked `HUMAN CHECK ResearchGate first`.

## Included (26), by cell
| cell | candidates |
|---|---|
| T6 biodiversity | crouzeilles_2016, crouzeilles_2017, poorter_2021, su_2021, hajjar_2021 |
| T6 carbon | bernal_2018, poorter_2021, yang_2023, su_2021, jakovac_2020 |
| T3 drought / T6 water_stress (trade-off sign) | filoso_2017, farley_2005 |
| T3 flood (both signs) | bradshaw_2007 **+** vandijk_2009 (rebuttal), herath_2025 |
| T3 heat_stress | prevedello_2019 |
| T6 soil_erosion_risk | yang_2023, poorter_2021 (soil recovery) |
| T3 coastal flood / wind_cyclone (mangrove) | menendez_2020, gijsman_2021, marois_mitsch_2015 |
| T3 asset_vulnerability | gorman_2022 + kodikara_2017 (mangrove), gardiner_2021 (wind on plantations) |
| T6 rural_poverty / food_security | samii_2014_dfm, snilstveit_2019 (PES), hajjar_2021, naidoo_2019, kandel_2022, rasolofoson_2018 |
| T6 costs / cost-effectiveness | brancalion_2019, jakovac_2020, su_2021 (economic outcomes) |

## Screened out (main exclusions)
| item | reason |
|---|---|
| Laganière 2009 afforestation SOC MA; Busch 2019 low-cost CO2 reforestation; Latawiec/Crouzeilles 2016 Biotropica natregen-biodiversity MA; ANR bibliometric synthesis 2024 (Frontiers) | **already known** (queue/SRC/FR logs) |
| Gómez-Aparicio 2004 nurse-plant MA; biochar-restoration MA 2015 | technique/species-level growth, no T3/T6 outcome |
| Berthrong 2009; Li 2012; Deng/Chen afforestation soil MAs (N, P, cations, microbial) | soil-chemistry outcomes with no T6 target; one SOC MA (Laganière) already known |
| Busch & Ferretti-Gallon 2023 drivers MA | drivers of deforestation, not effects of the NbS |
| Shifting-cultivation secondary-forest synthesis 2015 (Env Sci Policy) | land-use dynamics, not an effect claim; borderline (kept as pointer) |
| Amphibian/reptile secondary-succession MA 2018; Japan plantation MA 2019; China woody-richness MA 2017 | taxon-narrow or HIC/single-country; Crouzeilles + Poorter cover the cell |
| Alongi 2008; Danielsen 2005; Kathiresan 2005; Das & Vincent 2009 PNAS; Hochard 2019 PNAS | seminal tsunami/cyclone primaries; contested 2004-tsunami evidence is covered through the Marois & Mitsch and Gijsman syntheses. **Hochard 2019** (economic activity sheltered from cyclones) is a strong fallback if a primary is wanted |
| Wave-attenuation field primaries (Mazda 1997; Quartel 2006; Bao 2011; Horstman 2014) | primaries, synthesised in Gijsman 2021 / McIvor 2012 (grey lane) |
| Mangrove blue-carbon SRs (land-use change 2019; Brazil stocks; Asia RS) | stock/inventory, not restoration effect; Bernal 2018 + Su 2021 cover carbon |
| Coral restoration SR; dental "restoration" survival SRs (L10) | off-topic noise |
| Plantation-fire primaries (L16: Portugal/Spain/Australia eucalypt and pine) | HIC primaries about post-fire erosion/fuel; no synthesis exists. **Fire is a gap** (see below) |
| Forest windthrow reviews (Mitchell 2000; Everham & Brokaw-type; Lin 2011 typhoon) | HIC natural forests; Gardiner 2021 targets planted forests |
| PES participation SR 2020; motivational crowding SR 2019; REDD perception SRs | process/uptake, not outcomes (adoption-side evidence for M2b, not T6) |
| Wunder et al. / Börner PES reviews | covered by Snilstveit 2019 Campbell (lineage) |
| Ellison 2017 GEC (Trees, forests and water) | **trimmed for the cap** (narrative; IUFRO GFEP 2018 in the grey lane covers it). Restore if wanted: `10.1016/j.gloenvcha.2017.01.002`, hybrid OA |
| Samii 2014 PES Campbell (`10.4073/csr.2014.11`) | **trimmed**: superseded by the Snilstveit 2019 update (lineage dedupe would collapse them) |
| Crouzeilles 2020 Conserv Lett (`10.1111/conl.12709`, gold) | **trimmed for the cap**: modelled CE; restore if the cost cells are thin |
| Liu & Kontoleon 2018 PES livelihood MA (`10.1016/j.ecolecon.2018.02.008`, green) | **trimmed for the cap**: overlaps Snilstveit; restore if T6 poverty needs a second PES MA |
| Coleman 2021 Nat Sust (tree planting, India) | primary (event study), closed; strong *null* finding on livelihoods/canopy, so a human may want it (`10.1038/s41893-021-00761-z`; ICIMOD library record lib.icimod.org/records/2vvn4-h0e30 may host a copy) |
| Erbaugh & Oldekop 2018 COSUST | short opinion review, closed, no effect sizes |
| De Groot 2013 Conserv Biol | multi-biome BCRs, superseded for forests by Brancalion/WRI |
| Rozendaal 2019 Sci Adv | passive biodiversity recovery already covered by Crouzeilles 2016/2017 + Poorter 2021 |
| Bastin/Cook-Patton style mapping papers | T4/opportunity, already in queue |

## Gaps and things that need a human
1. **Fire (T3 hazard and asset):** no synthesis was found on plantation or restoration flammability, or on fire as a planting-failure driver in LMICs (L13 = 0 hits). Only HIC Mediterranean/Australian primaries exist. Expect a `limited` cell plus the M2b fallback. A targeted grey look (FAO Integrated Fire Management guidelines, already in the 2026-08 log) is the next step.
2. **Frost and waterlogging:** nothing found for FR. Treat as WOCAT-only (§6.3) cells.
3. **Drought asset vulnerability for planted seedlings in LMICs:** covered by known items (Andivia 2021, Svejcar 2023, del Campo 2021, and "road to recovery" Asia synthesis). No new synthesis surfaced.
4. **Landslide** has no T3 hazard id. The evidence routes via `flood` / `soil_erosion_risk`, which needs an ontology call (also applies to the FAO 2011 grey item).
5. **Paywalled, ResearchGate HUMAN CHECK:** farley_2005, vandijk_2009, yang_2023, kandel_2022.
6. **Bradshaw vs van Dijk** must be acquired as a pair. Registering one without the other biases the flood cell.
