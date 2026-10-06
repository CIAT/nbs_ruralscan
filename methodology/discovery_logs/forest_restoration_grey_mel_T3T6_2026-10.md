# Forest restoration × T3/T6: grey MEL / impact-assessment pass (2026-10-06)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `forest_synthesis_first_2026-10-06_grey`, ruleset **v1.6.2**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-06: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `forest_synthesis_first_2026-10-06_grey`, ledger per `--ledger`.


- **Scope:** `nbs_id=forest_restoration`, generic parent search, tables T3 + T6, process **`grey`**, ruleset v1.6.0. Suggested run id: `fr_synthesis_first_grey_2026-10-06`.
- **Channels:** WB IEG (thematic evaluations, PPARs), GEF IEO, 3ie EGMs, IUFRO GFEP assessments, FAO/CIFOR RAP syntheses, TNC/Wetlands International, IFRC evaluations, WRI. PADs are ex-ante documents and are not used as evidence.
- **Staging only.** Nothing was registered and no git commands were run. No DOIs are emitted, because all items are DOI-less grey literature, so `title_verified` is needed at acquisition.
- **Dedup:** checked against the queue, SRC and FR logs. FAO drylands guidelines (FP175), ITTO FLR guidelines, IUCN ROAM, GMA mangrove guidelines, FAO IFM guidelines and FAO resilience guidelines are already known and were excluded.
- **Live-link check:** each URL was checked with `curl` (HTTP 200 + PDF content type) on 2026-10-06. **ieg.worldbankgroup.org returns HTTP 403 to tools**, so IEG items need a human browser download. The TNC conservationgateway PDF is now 404, so a mirror is given.

## Funnel
| stage | n |
|---|---|
| returned (web-search result links over 14 queries) | ≈ 135 |
| screened (title + landing page / summary) | 34 |
| included | **13** (cap ≈ 15) |

## Search strings (WebSearch, verbatim)
| # | query | outcome |
|---|---|---|
| G1 | `3ie evidence gap map forest conservation restoration land-use outcomes livelihoods` | 3ie EGM 4 (incl.), GCF IEU LP02 (excl.) |
| G2 | `IEG Project Performance Assessment Report forest landscape restoration project World Bank PPAR` | Vietnam FSDP PPAR (incl.); China Loess PPAR 41122, Brazil Rio Rural PPAR, Bangladesh/Nepal wildlife PPAR (excl.) |
| G3 | `IEG evaluation "World Bank Group support to forests" OR "Managing Forest Resources for Sustainable Development" evaluation report pdf` | IEG 2013 (incl.) |
| G4 | `GEF Independent Evaluation Office evaluation sustainable forest management restoration impact report` | GEF IEO SFM 2022 (incl.), GEF VfM 2019 (incl.), GEF NbS evaluation (excl.) |
| G5 | `Implementation Completion Report World Bank "natural resources management" Ethiopia OR Nepal OR Vietnam forest restoration ICR outcomes area closure` | Ethiopia SLMP ICR, CWA II ICR (excl.: bundled SLM) |
| G6 | `IFRC "Mangrove plantation in Viet Nam: measuring impact and cost benefit" pdf` | incl. |
| G7 | `FAO CIFOR 2005 "Forests and floods: drowning in fiction or thriving on facts" pdf` | incl. |
| G8 | `McIvor Spencer Möller Spalding "Storm surge reduction by mangroves" Natural Coastal Protection Series Report 2 pdf` | incl. |
| G9 | `Forbes Broadhead FAO "Forests and landslides" RAP publication 2011 pdf` | incl. |
| G10 | `GEF IEO "Value for Money Analysis of GEF Interventions in Support of Sustainable Forest Management" pdf 2019` | incl. |
| G11 | `Humbo Ethiopia assisted natural regeneration project evaluation World Bank BioCarbon Fund results report pdf` | excl. (see below) |
| G12 | `WRI "Roots of Prosperity: The Economics and Finance of Restoring Land" Ding 2017 pdf` | incl. |
| G13 | `IUFRO GFEP "Forest and Water on a Changing Planet" 2018 World Series pdf` | incl. |
| G14 | `IUFRO GFEP "Forests, Trees and the Eradication of Poverty" global assessment report 2020 pdf` | incl. (+ GFEP 2015 food-security, found via OpenAlex hdl 10568/94088) |
| G15 | `IEG PPAR "41122" China Loess Plateau Watershed Rehabilitation Xiaolangdi Tarim Basin performance assessment report year` | confirmed record; excluded (bundled) |

## Included (13)
puri_2016_3ie_egm · gefieo_2022_sfm · gefieo_2019_vfm_sfm · ieg_2013_managing_forest_resources · ieg_2018_ppar_vietnam_forest_sector · fao_cifor_2005_forests_floods · forbes_broadhead_2011_fao_forests_landslides · mcivor_2012_storm_surge_mangroves · ifrc_2011_mangrove_vietnam_cba · iufro_2018_gfep_forest_water · iufro_2020_gfep_forests_poverty · iufro_2015_gfep_food_security · wri_2017_roots_of_prosperity

**Grey positive-bias discount:** IFRC (implementer-commissioned) and WRI (advocacy-adjacent) carry the biggest bias risk. FAO/CIFOR 2005 is a *myth-busting* synthesis that counter-indicates spin, as the IEG items do. The GFEP reports are expert-panel assessments, IPCC-like in form.

## Screened out
| item | reason |
|---|---|
| IEG PPAR 41122 China Loess Plateau / Xiaolangdi / Tarim | practice bundled (terraces, check dams, grazing bans + afforestation); FR effect not separable |
| Ethiopia SLMP ICR (ICR00004449); CWA II ICR | bundled SLM / watershed packages; FR not disaggregated |
| IEG PPAR Brazil Rio Rural (88960); Bangladesh/Nepal wildlife PPAR (128169) | not forest restoration outcomes (rural development / wildlife enforcement) |
| IEG "Natural resource degradation and vulnerability nexus" (2021) | thematic, NRM-wide; FR not separable. Pointer for the M2 team |
| GCF IEU Learning Paper 02 (2019) Effectiveness of forest conservation | review overlapping 3ie EGM 4 + Campbell SRs (lineage) |
| GEF IEO NbS evaluation | NbS-wide, FR outcomes not separable on a first read. Revisit if T6 cells are thin |
| Humbo ANR (Oxford Economics case study; CCB validation; WB brief) | validation report is ex-ante; case study and brief are promotional summaries without method. The **IEG case study** cited in search snippets (165,000 tCO2e delivered 2007–18) was not located. **Human:** find the IEG BioCarbon Fund evaluation that contains it |
| McIvor 2012 Report 1 (wind & swell waves) | trimmed; the storm-surge report covers the T3 flood/cyclone cell. Add if wave attenuation is needed separately |
| Regional ROAM reports (e.g. Madagascar AFR100 RPF) | T4/opportunity, not effects |
| FAO IFM guidelines, FAO resilience guidelines, ITTO PS24, FAO FP175, IUCN ROAM, GMA mangrove guidelines | already known |

## Needs a human
- **IEG downloads (403 to tools):** ieg_2013, ieg_2018_ppar_vietnam. Use a browser, then upload to SharePoint.
- **McIvor 2012:** the TNC PDF is now 404. The UNAM mirror works, but fetch the publisher copy from Wetlands International if possible (library of record).
- **GEF VfM 2019 and WRI 2017:** the landing pages link the PDFs, but the exact PDF URL needs to be captured at acquisition.
- **SPIA:** no SPIA study on forest restoration or protection exists to my knowledge. Nothing was found, so the channel is recorded as saturated-null.
- **GEF terminal evaluations** of individual FLR/mangrove projects were not pulled one by one (portfolio evaluations were preferred). That is a possible second round if a family cell stays `limited`.
