# fr_tool_gaps — forest_restoration T3/T6 tool lane and gap-fill literature (2026-11-10)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `fr_t3t6_tool_gaps_20261110_frgap`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-10: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `fr_t3t6_tool_gaps_20261110_frgap`, ledger per `--ledger`.


- Lane: `fr_tool_gaps`. NbS: `forest_restoration`, generic search (families: []). Tables: T3, T6. Processes: `tool` and narrow `updated_lit`. Discovery ruleset: v1.8.1.
- Channels used: GitHub REST API (repo trees and raw files at pinned commits), web search, WebFetch of tool documentation, OpenAlex `title.search`, Crossref DOI round-trip, Unpaywall (OA hint only).
- Channels omitted: Lens (no LENS_TOKEN), AGRIS (manual lane), WoS/Scopus/CAB (skipped by policy), GitLab. FAO openknowledge returned HTTP 403 and pdf.usaid.gov failed DNS; neither was circumvented.
- No PDFs were downloaded. One WB EX-ACT manual PDF was auto-saved by WebFetch to the session tool-results folder and read for screening only. It is not cached in `.cache/corpus`.

## Counts (inspected, not engine totals)

| table | process | returned | screened | included |
|---|---|---|---|---|
| T3 | tool | 15 | 15 | 0 |
| T6 | tool | 15 | 15 | 4 |
| T3 | updated_lit | 136 | 136 | 12 |
| T6 | updated_lit | 204 | 204 | 19 |

There are 28 candidate records in total. Some candidates feed both tables, so the T3 and T6 rows overlap. There are 3 reuse candidates for existing sources: Cook-Patton 2020 and Latawiec 2016 (both T4-only today) and Reed 2017 (agroforestry-only today).

## Tool findings (actual code/docs)

- **Included, T6 carbon**
  - IPCC 2019 Refinement Vol4 Ch4 (Table 4.9/4.10 Tier-1 growth rates). This is the primary source.
  - FAO EX-ACT. The WB user manual shows the A/R module carries built-in Tier-1 growth rates for the first 20 yr and after (pdf pp. 46-49, 131). The values sit in the Excel workbook, which must be pinned.
  - wri/carbon-budget @ab90fec. Hardcodes C fraction 0.47 and root:shoot 0.26 (constants_and_names.py L53, L75). It routes young secondary forest to the Cook-Patton raster and older forest to IPCC Table 4.9 (removals/annual_gain_rate_IPCC_defaults.py). This is a derivative source; weight it low.
  - naturalclimatesolutions/nat_for_regen_c_accumulation @8c76900. Holds the Chapman-Richards curve code plus country × biome rate CSVs. It is the companion to Robinson 2025. The CSVs fall under the dataset-intake pause.
- **Excluded or held**
  - InVEST @f02f5e2 is data-driven. Every effect parameter (usle_c/p, k, IC0, sdr_max, Kc, root_depth, carbon pools) is user-supplied. This is the same pattern as spatMCDA.
  - RIOS ships demo configs only.
  - ROAM is already queued and has no hardcoded values.
  - Naturebase has no public method docs (hold).
  - The Winrock FLR calculator is Bernal 2018 lineage (already queued).
  - USAID AFOLU-CC docs were unreachable (hold).
  - EX-ACT v9 guidelines returned 403 (hold).
  - TerraMatch and Restor are monitoring platforms with no effect parameters.
  - LandPKS is a T4 referral.
  - GROA is a dataset (paused).
- **No tool encodes a T3 livelihood effect for forest restoration.** The T3 tool protocol is an explicit zero-yield.

## Gap-cell outcome

- **T6 biodiversity:** Hua 2022 Science, Atkinson 2022, Rey Benayas 2009, plus Latawiec 2016 (reuse).
- **T6 carbon:** Robinson 2025, Requena Suarez 2019, Bonner 2013, Silver 2000, Griscom 2017, Cook-Patton 2020 (reuse), plus the 4 tools above.
- **T6 production_gap:** Reed 2017 (reuse) and the Yang 2024 preprint. Both are existing-habitat comparators, and no restoration-specific synthesis was found.
- **T6 heat_stress_hazard and T3 heat_stress:** Peng 2014 (afforestation explicit), Alkama 2016 (forest-gain arm), Ellison 2017, Lawrence 2022, Parsons 2021, Wolff 2018, Li 2015. Most of these are existing-forest comparators.
- **T3 drought livelihood:** Wunder 2014 (limited safety-net role, which counts as counter-evidence), Noack 2019, Fisher & Shively 2005 (borderline). All three are existing-habitat comparators.
- **T3 wind_cyclone livelihood:** Lazos-Chavero 2018 (LMIC, existing dry forest) and Wiener 2020 (HIC review). Evidence is genuinely thin. The cyclone hits that turned up were mangrove studies and were referred to the mangrove lane. Expect this cell to stay low confidence.

## Verbatim queries

#### T3 / tool
- `GitHub API: repos natcap/invest, natcap/rios, wri/carbon-budget, naturalclimatesolutions/nat_for_regen_c_accumulation (latest commit + tree + raw files)`
- `GitHub search API: natural regeneration carbon accumulation`
- `Web: FAO EX-ACT technical guidelines afforestation reforestation default growth rates IPCC Tier 1`
- `Web: "EX-ACT" FAO "technical guidelines" OR "user guide" carbon balance tool pdf afforestation module`
- `Web: Naturebase TNC reforestation methodology sequestration rate documentation`
- `Web: Winrock AFOLU Carbon Calculator forest restoration module documentation growth rates`
- `Fetch: naturebase.org; naturebase.org/science-and-data; fao.org EX-ACT overview (404); openknowledge.fao.org cc7977en (403); WB EX-ACT user manual 112809 (200); pdf.usaid.gov PA00JXTK (DNS fail)`

#### T6 / tool
- `GitHub API: repos natcap/invest, natcap/rios, wri/carbon-budget, naturalclimatesolutions/nat_for_regen_c_accumulation (latest commit + tree + raw files)`
- `GitHub search API: natural regeneration carbon accumulation`
- `Web: FAO EX-ACT technical guidelines afforestation reforestation default growth rates IPCC Tier 1`
- `Web: "EX-ACT" FAO "technical guidelines" OR "user guide" carbon balance tool pdf afforestation module`
- `Web: Naturebase TNC reforestation methodology sequestration rate documentation`
- `Web: Winrock AFOLU Carbon Calculator forest restoration module documentation growth rates`
- `Fetch: naturebase.org; naturebase.org/science-and-data; fao.org EX-ACT overview (404); openknowledge.fao.org cc7977en (403); WB EX-ACT user manual 112809 (200); pdf.usaid.gov PA00JXTK (DNS fail)`

#### T3 / updated_lit
- `OpenAlex title.search: (reforestation OR afforestation OR "forest restoration" OR forestation OR "forest cover change") AND (temperature OR cooling OR heat OR warming) [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (forest OR forests OR reforestation OR "forest restoration") AND (drought OR "income shock" OR "income shocks" OR "weather shocks" OR "safety net" OR "safety nets") AND (household OR households OR livelihood OR livelihoods OR income OR rural) [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (forest OR forests OR reforestation OR "tree cover" OR restoration) AND (cyclone OR cyclones OR hurricane OR hurricanes OR typhoon OR typhoons OR windstorm) AND (household OR households OR livelihood OR livelihoods OR agriculture OR crop OR crops OR income) [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (deforestation OR reforestation OR afforestation OR forestation OR "forest cover" OR "tree cover") AND ("local temperature" OR "surface temperature" OR "local climate" OR "heat exposure" OR "heat stress" OR "biophysical") [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (forest OR forests OR "environmental income" OR "forest income") AND (drought OR droughts OR "rainfall shocks" OR "climate shocks" OR "gap filling" OR "safety nets") [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (deforestation OR "forest cover" OR forests OR reforestation OR "tree cover") AND (storm OR storms OR cyclone OR cyclones OR typhoon OR typhoons OR hurricane OR hurricanes OR "wind damage") AND (damage OR damages OR losses OR protection OR mitigation OR resilience) [from 2000-01-01, sort cited_by_count desc, top 25]`
- `Crossref: Safety nets, gap filling and forests: a global-comparative perspective Wunder`
- `Crossref: Droughts, biodiversity, and rural incomes in the tropics Noack`
- `Crossref: Impact of tropical deforestation on local temperature and human well-being perceptions Wolff`
- `Crossref: Tropical deforestation accelerates local warming and loss of safe outdoor working hours`
- `Crossref: Uncovering links between livelihoods, land-use practices, vulnerability and forests after hurricane Jova`
- `Web: forest cover reduces typhoon OR cyclone damage to crops or rural households evidence reforestation protection study`

#### T6 / updated_lit
- `OpenAlex title.search: (restoration OR reforestation OR "secondary forest" OR "secondary forests" OR regeneration OR afforestation) AND (biodiversity OR "species richness") AND (meta-analysis OR "global synthesis" OR "systematic review") [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (reforestation OR "secondary forest" OR "secondary forests" OR "natural regeneration" OR "forest restoration" OR afforestation) AND (carbon OR biomass) AND (accumulation OR sequestration OR removal OR recovery) AND (global OR meta-analysis OR pantropical OR tropical) [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (reforestation OR afforestation OR "forest restoration" OR forestation OR "forest cover change") AND (temperature OR cooling OR heat OR warming) [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (forest OR "forest cover" OR "tree cover" OR reforestation OR "forest restoration") AND ("crop yield" OR "crop yields" OR "agricultural productivity" OR "agricultural production") AND (meta-analysis OR review OR global OR tropics OR tropical) [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (deforestation OR reforestation OR afforestation OR forestation OR "forest cover" OR "tree cover") AND ("local temperature" OR "surface temperature" OR "local climate" OR "heat exposure" OR "heat stress" OR "biophysical") [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (forests OR "tree cover" OR "forest loss" OR deforestation OR reforestation) AND ("agricultural productivity" OR "agricultural production" OR "crop production" OR "food production") [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: (restauración OR reforestación OR "regeneración natural") AND (biodiversidad OR carbono OR temperatura OR sequía OR "medios de vida") [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: ("restauration forestière" OR reboisement OR "régénération naturelle") AND (biodiversité OR carbone OR sécheresse OR revenus) [from 2000-01-01, sort cited_by_count desc, top 25]`
- `OpenAlex title.search: ("restauração florestal" OR reflorestamento OR "regeneração natural") AND (biodiversidade OR carbono OR temperatura OR seca OR renda) [from 2000-01-01, sort cited_by_count desc, top 25]`
- `Crossref DOI round-trip: 10.1126/science.abl4649, 10.1111/ele.14025, 10.1126/science.1172460, 10.1038/s41558-025-02355-5, 10.1111/gcb.14767, 10.1016/j.foreco.2012.11.024, 10.1046/j.1526-100x.2000.80054.x, 10.1073/pnas.1710465114, 10.1038/s41586-020-2686-x, 10.1016/j.gloenvcha.2017.01.002`
- `Crossref: Protecting forests and trees is essential for global agricultural productivity`
- `Web: "Forests and trees show scale-dependent relationships with global agricultural production"`

## Screening

Per-record decisions are in `screening.json`. Raw OpenAlex rows are in `raw/oa_en.json` and `raw/oa_r2.json`. Unpaywall hints are in `raw/unpaywall.txt`. Titles that are off-topic (random-forest ML, tree mortality, urban heat, physics) are counted as screened but are not listed individually.

## Stop reason

- T6 reached its cap. 19 of 20 included. Huang 2019 is held as the next item in line.
- T3 reached saturation for this bounded pass. Repeated queries returned no restoration-specific (non-comparator) livelihood evidence for drought, heat or cyclone, and the remaining hits were comparator or mangrove studies.
- This is not exhaustive. Lens and AGRIS were not run, and grey-literature MEL was out of scope for this lane.

## Next actions

1. Central dedupe and registration. Pass the 3 reuse IDs as scope extensions, not new votes.
2. Human: fetch the EX-ACT v9 guidelines and a pinned workbook version, and the IPCC 2019 Ch4 PDF. Record table/page locators for the Tier-1 rows. Count IPCC, Requena Suarez, EX-ACT and carbon-budget as one lineage, never as independent votes.
3. OA: Rey Benayas, Alkama, Bonner, Silver, Noack, Fisher, Lazos-Chavero are closed per Unpaywall. Each needs a web search and a ResearchGate check by a human before any paywall label.
4. Comparator routing: most heat and drought items are `comparator: existing_habitat`. Apply comparator_policy so they do not set the restoration roll-up on their own.
5. Look for a published version of the Yang 2024 preprint.
