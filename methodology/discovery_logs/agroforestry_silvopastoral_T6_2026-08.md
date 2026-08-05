# Discovery log — Agroforestry · silvopastoral · T6

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 371 | 15 | 5 |
| updated_lit | 33 | 15 | 5 |
| grey | 25 | 12 | 4 |
| tool | 10 | 6 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: (silvopastoral OR silvopasture OR silvopastoril OR sylvopastoral) AND (carbon OR yield OR income OR adoption OR biodiversity OR livestock) | sort=cited_by_count:desc`
- **updated_lit:** `OpenAlex title.search: (silvopastoral OR silvopasture OR silvopastoril OR sylvopastoral) AND (adoption OR income OR cost OR profitability OR smallholder) , from_publication_date:2015-01-01 | sort=cited_by_count:desc`
- **grey:** `WebSearch EN: 'silvopastoral systems cost per hectare adoption benefits carbon livestock manual World Bank FAO WOCAT' ; WebSearch ES: 'CIPAV sistemas silvopastoriles costos beneficios ganaderia carbono adopcion Colombia informe' ; WebSearch EN: 'World Bank GEF Mainstreaming Sustainable Cattle Ranching Colombia silvopastoral implementation completion report cost per hectare'`
- **tool:** `GitHub API: q=silvopast OR silvopasture OR silvopastoral (rate-limited 403) ; q=agroforestry+suitability OR agroforestry+carbon+model (rate-limited 403) ; WebSearch fallback (allowed_domains=github.com): 'github silvopastoral OR agroforestry carbon sequestration model tool R python repository cost benefit livestock' ; WebSearch: 'Drawdown silvopasture cost per hectare tCO2 net cost model data'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `shrestha2003_florida_sps_adoption` | stock | paywalled | ok | high | Exploring the potential for silvopasture adoption in south-central Florida: an application of SWOT-AHP method — Seminal (330 cites) SPS adoption study; SWOT-AHP of adoption drivers |
| `jose2019_sps_review` | stock | oa | ok | high | Silvopasture: a sustainable livestock production system — OA-bronze editorial/review synthesising SPS outcomes (forage, animal production, carbon, biodiversity). Good T6 anchor + c |
| `dagang2003_centralamerica_sps_adoption` | stock | paywalled | ok | high | Silvopastoral research and adoption in Central America: recent findings and recommendations — LMIC (Central America) adoption + research synthesis; observed-reality adoption eviden |
| `giraldo2010_colombia_dungbeetle` | stock | paywalled | ok | med | The adoption of silvopastoral systems promotes the recovery of ecological processes regulated by dung beetles — Colombia (LMIC) biodiversity outcome tied explicitly to SPS adoption |
| `garbach2012_nicaragua_pes` | stock | paywalled | ok | high | Payment for Ecosystem Services: positive incentives and information sharing in stimulating adoption of silvopastoral practices — Nicaragua (LMIC) PES-driven adoption; incentives/co |
| `jararojas2020_chile_agroforestry_adoption` | updated_lit | oa | ok | high | Factors Affecting the Adoption of Agroforestry Practices: Insights from Silvopastoral Systems of Chile — OA-gold. Chile SPS adoption determinants (econometric). T6 adoption, LMIC-a |
| `orefice2016_forage_profitability` | updated_lit | paywalled | ok | high | Forage productivity and profitability in newly-established open pasture, silvopasture, and thinned forest production systems — Direct T6 yield+profitability comparison across pastu |
| `tschopp2020_argentina_granchaco_adoption` | updated_lit | oa | ok | high | Understanding the adoption of sustainable silvopastoral practices in Northern Argentina — OA-green. Argentina Gran Chaco (LMIC) adoption drivers, multilevel. Observed-reality adopt |
| `alvaradosandino2023_colombia_amazon_adoption` | updated_lit | oa | ok | high | Examining factors for the adoption of silvopastoral agroforestry in the Colombian Amazon — OA-gold, recent, Colombian Amazon (LMIC frontier). T6 adoption determinants incl. economi |
| `chamorrovargas2025_latam_barriers_review` | updated_lit | oa | ok | high | Review of enablers and barriers to the adoption of silvopastoral systems in Latin America — OA-gold 2025 systematic review of LatAm SPS adoption enablers/barriers -> high-yield T6  |
| `worldbank_gcs_colombia_p104687` | grey | oa | ok | high | Colombia - Mainstreaming Sustainable Cattle Ranching Project (P104687) / Ganaderia Colombiana Sostenible - project & completion docs — Diamond WB project-evidence (GEF). Quantified |
| `cipav_gcs_participatory` | grey | oa | ok | med | Investigacion participativa en sistemas silvopastoriles integrados: la experiencia de CIPAV en Colombia (LEISA) — CIPAV (LatAm-grounded practitioner org, LMIC diamond-ish) particip |
| `wwf_foodforward_ndc_sps_brief` | grey | oa | ok | med | Implementing silvo-pastoral practices - WWF Food Forward NDCs & NBSAPs — NGO field-guidance brief: benefits (up to 4x cattle production/ha, dry-season resilience, carbon), establis |
| `nicaragua_pes_silvopastoral_elti` | grey | oa | ok | med | Paying for the Environmental Services of Silvopastoral Practices in Nicaragua — Nicaragua (LMIC) PES-for-SPS programme write-up; cost/incentive + adoption evidence complementing Ga |
| `projectdrawdown_silvopasture_model` | tool | repo | ok | high | Project Drawdown - Silvopasture solution model (net cost/ha, establishment range, cost per tCO2e) — Practice-explicit model: hardcoded net-net cost US$424.20/ha (regional weighted  |

## Gaps / next iteration

Africa/Asia coverage is thin: the corpus is overwhelmingly Latin American (Colombia, Argentina, Chile, Nicaragua) plus US/Iberian temperate carbon studies, with only isolated Sub-Saharan hits (Oyelami 2022 Nigeria, Sasu 2023 SSA bamboo agro-silvopastoral) and effectively no South/Southeast Asian silvopasture T6 evidence — next iteration should run AGROVOC title-only queries in French/Portuguese and target ICRAF/TECA + WOCAT SLM DB directly for African drylands. Hard T6 cost indicators (cost_per_ha, cost_per_tCO2e) currently rest mainly on grey/model sources (Drawdown, WB-GCS, CIPAV) that carry positive-bias and design-choice caveats, so peer-reviewed establishment-cost/profitability primaries beyond Orefice 2016 are under-represented. The tool lane is weak: no silvopasture-specific codebase exists and GitHub API was rate-limited — the Drawdown model still needs a commit-pinned file:line interrogation before any parameter can become an EV row.
