# Discovery log — Agroforestry · cross_family · T6

- Run `discovery_crossfam_homegardens_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 478 | 48 | 5 |
| updated_lit | 1051 | 48 | 5 |
| grey | 24 | 24 | 4 |
| tool | 312 | 24 | 2 |

### Verbatim search terms

- **stock:** `OpenAlex title.search (cited_by_count desc): "agroforestry yield"; "agroforestry adoption"; "agroforestry carbon sequestration"; "agroforestry income"; "agroforestry profitability"; "trees on farms carbon"`
- **updated_lit:** `OpenAlex title.search + from_publication_date:2016-01-01 (cited_by_count desc): "agroforestry yield"; "agroforestry adoption determinants"; "agroforestry carbon"; "agroforestry income smallholder"; "agroforestry cost benefit"; "agroforestry biodiversity"`
- **grey:** `WebSearch (EN): "agroforestry cost benefit yield income WOCAT FAO TECA smallholder evidence"; "World Bank agroforestry economic returns adoption evidence report LMIC"; "WOCAT agroforestry technology establishment maintenance costs benefits table"`
- **tool:** `GitHub search/repositories (stars desc): "agroforestry carbon OR cost OR yield"; "agroforestry model"`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `castle2021_lmic_af_sysrev` | stock | oa | ok | high | The impacts of agroforestry interventions on agricultural productivity, ecosystem services, and human well-being in low- and middle-income countries: A systematic review (Campbell Collaboration) — Dia |
| `brown2018_af_impacts_syst_map` | stock | oa | ok | high | Evidence for the impacts of agroforestry on agricultural productivity, ecosystem services, and human well-being (systematic map, Environmental Evidence) — Cross-family EE systematic map; companion to  |
| `zomer2016_treecover_agland` | stock | oa | ok | high | Global Tree Cover and Biomass Carbon on Agricultural Land: The contribution of agroforestry to global carbon budgets (Zomer et al., Sci Rep) — Seminal (616 cites) global carbon outcome synthesis for t |
| `lorenz2014_af_soc_review` | stock | repo | ok | high | Soil organic carbon sequestration in agroforestry systems. A review (Lorenz & Lal) — OA via HAL (hal-01234833). Cross-family SOC outcome review. Practice-agnostic carbon claim. |
| `pattanayak2003_af_adoption_stock` | stock | paywalled | ok | high | Taking stock of agroforestry adoption studies (Pattanayak et al.) — Seminal adoption stocktake (460 cites); cross-family adoption/dis-adoption drivers = observed-reality T6. Paywalled -> acquisition_q |
| `destefano2018_af_soc_meta` | updated_lit | paywalled | ok | high | Soil carbon sequestration in agroforestry systems: a meta-analysis (De Stefano & Jacobson) — Cross-family SOC meta-analysis (277 cites); quantitative carbon outcome effect sizes by land-use transition |
| `carbonrevenue_profit_2019` | updated_lit | oa | ok | high | Carbon revenue in the profitability of agroforestry relative to monocultures — Cross-family economics: profitability/cost-effectiveness of AF vs monoculture incl. carbon revenue -> directly T6 cost +  |
| `torralba2016_europe_es_meta` | updated_lit | repo | ok | med | Do European agroforestry systems enhance biodiversity and ecosystem services? A meta-analysis (Torralba et al.) — OA via Cranfield dspace (1826/10205). Cross-family ES/biodiversity outcome meta but HI |
| `afyield_europe_meta_2021` | updated_lit | oa | ok | med | Crop Yields in European Agroforestry Systems: A Meta-Analysis — Cross-family yield outcome meta (LER/yield effects) but HIC/temperate context -> transferability discount for LMIC scope. |
| `chapman2022_hic_af_map` | updated_lit | oa | ok | med | Evidence for the impacts of agroforestry on ecosystem services and human well-being in high-income countries: a systematic map — Cross-family HIC companion to Castle/Brown; useful for outcome typology |
| `wocat_af_costs_africa_dataset` | grey | oa | ok | high | Dataset on Costs and Benefits of Agroforestry in Africa (Users Guide + data, Uni Bonn / bonndata) — Open dataset of establishment/maintenance costs and benefits for African agroforestry; cross-family, |
| `fao2020_af_slw_assessment` | grey | oa | ok | med | Assessing agroforestry practices and soil and water conservation (FAO, July 2020) — FAO grey report; cross-family practice outcomes. Grey positive-bias discount applies. |
| `wocat_qcat_af_technologies` | grey | repo | ok | med | WOCAT QCAT SLM technology entries — agroforestry (e.g. Multistorey agroforestry [Ethiopia], technologies_1103) — WOCAT structured technology sheets carry per-technology establishment/maintenance cost  |
| `prs_eth_agroforestry_repo` | tool | repo | NO | low | prs-eth/agroforestry — 'unrealized potential of agroforestry for an emissions-intensive agricultural sector' — UNVERIFIED. Candidate carbon-potential tool; PICOS/practice-branch and any hardcoded outc |
| `wocat_economic_db_platform` | tool | other | ok | med | WOCAT global SLM economic database (QCAT platform, cost/benefit fields) — Platform/database rather than code repo; the 'hardcoded' content is the structured cost/benefit rating schema + entries. Overl |

## Gaps / next iteration

Indexed peer-reviewed literature is thin on cross-family AGROFORESTRY COST evidence: OpenAlex title pools for 'agroforestry cost benefit' (7) and 'agroforestry income smallholder' (3) are tiny. Cost/adoption evidence at scoping grade lives in GREY databases (WOCAT global SLM economics: establishment ~US$150/ha, maintenance ~15%/yr, BCR>2 for 24% of techs) — so T6 cost extraction should lean on WOCAT + the Bonn open dataset, with grey positive-bias discount applied. LMIC-specific yield/income effect sizes remain weakly quantified (Castle 2021 SR flags evidence as 'patchy', cannot resolve effect sizes by intervention type). Carbon is the best-evidenced outcome (many OA metas); nutrition and cost_per_beneficiary / cost_per_tCO2e indicators are barely represented in cross-family sources and may need sub-practice-level or expert (Namita) elicitation. TOOL process is a genuine gap: no code tool hardcodes cross-family practice-level outcome/cost thresholds — biophysical models are species/biophysical yield engines (excluded as species-envelope-adjacent). ES/FR/PT multilingual grey searches were deferred; run at extraction for LatAm/Sahel LMIC cost coverage. Sub-practice caveat: cocoa/coffee shade and single-species papers were excluded here and route to shaded_perennial / species lane, not cross_family.
