# Discovery log — Wetland Management · creation · T6

- Run `wetland_management_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.2 · nbs_id `wetland_management`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 255 | 18 | 4 |
| updated_lit | 70 | 22 | 6 |
| grey | 16 | 16 | 3 |
| tool | 11 | 11 | 2 |

### Verbatim search terms

- **stock:** `OpenAlex title.search:"wetland creation" (sort cited_by_count desc). Companion runs: title.search:"created wetlands"; title.search:"constructed wetland siting OR created wetland restoration"`
- **updated_lit:** `OpenAlex title.search:"wetland creation" + from_publication_date:2016-01-01; companion runs title.search:"paludiculture peatland" + from:2016; title.search:"wetland siting suitability" + from:2016`
- **grey:** `WebSearch EN: "wetland creation restoration cost per hectare guidance Ramsar Wetlands International report"; "Global Peatlands Initiative peatland rewetting carbon cost report paludiculture tropical". (ES/FR/PT AGROVOC synonyms available but EN Ramsar/UNEP/GPI corpus saturated the cost+carbon T6 need.)`
- **tool:** `GitHub API search/repositories q="wetland suitability MCDA" (0); q="wetland restoration siting" (1); q="peatland mapping" (10), sort=stars. Plus WebSearch "wetland site suitability MCDA GIS github".`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `created_wl_NP_removal_syst_2016` | stock | oa | ok | high | How effective are created or restored freshwater wetlands for nitrogen and phosphorus removal? A systematic review — gold OA systematic review; core T6 water-quality outcome (N/P/sediment removal effi |
| `wl_econ_value_creation_meta_2008` | stock | repo | ok | high | The Economic Value of Wetland Conservation and Creation: A Meta-Analysis — green OA (SSRN) meta-analysis; T6 economic value / cost-benefit of wetland creation across services. 133 cites. Feeds economi |
| `wl_creation_ag_biodiv_2009` | stock | paywalled | ok | high | Wetland creation in agricultural landscapes: Biodiversity benefits on local and regional scales — Directly on F2 creation on agricultural (non-wetland) land; T6 biodiversity/habitat outcome. 205 cites |
| `riverine_wl_nutrient_retention_2005` | stock | paywalled | ok | med | Creating riverine wetlands: Ecological succession, nutrient retention, and pulsing effects — Mitsch created-wetland experiment; T6 nutrient retention + self-design. 272 cites. Paywalled; secondary to  |
| `wl_creation_suitability_catchment_2018` | updated_lit | oa | ok | high | Identifying Feasible Locations for Wetland Creation or Restoration in Catchments by Suitability Modelling — gold OA; F2 siting core (water availability + low-lying terrain + soil + not-currently-wetla |
| `national_wl_creation_ag_nutrient_2016` | updated_lit | oa | ok | high | National Large-Scale Wetland Creation in Agricultural Areas: Potential versus Realized Effects on Nutrient Transports — gold OA; created wetlands in agricultural land, T6 nutrient-transport reduction  |
| `soilC_N_recovery_wl_creation_2017` | updated_lit | oa | ok | high | A synthesis of soil carbon and nitrogen recovery after wetland restoration and creation in the United States — gold OA synthesis; T6 CARBON (+N) sequestration/recovery trajectories after creation. Qua |
| `paludiculture_indonesia_2020` | updated_lit | oa | ok | high | Progress of paludiculture projects in supporting peatland ecosystem restoration in Indonesia — gold OA; TROPICAL PEAT SE-Asia LMIC tie-break. Adoption/MEL of paludiculture (rewetting) programmes; T6 c |
| `paludiculture_fen_economy_2022` | updated_lit | oa | ok | med | Saving soil carbon, GHG emissions, biodiversity and the economy: paludiculture as sustainable land use option in German fen peatlands — hybrid OA; T6 carbon + biodiversity + economics of paludiculture |
| `paludiculture_tropical_review_2020` | updated_lit | paywalled | ok | high | Paludiculture as a sustainable land use alternative for tropical peatlands: A review — Tropical-peat review (LMIC tie-break, high value for F3-peat carbon/cost). Paywalled -> acquisition_queue. |
| `ramsar_global_wetland_outlook_2025` | grey | oa | ok | high | Global Wetland Outlook 2025 (Ramsar Convention STRP) — Authoritative Ramsar; T6 restoration cost per ha (~US$1k-150k/ha) + financing gap + ~123 Mha restoration need. Needs snapshot + section locator o |
| `ramsar_peatland_rewetting_briefing` | grey | oa | ok | high | Ramsar Briefing Note: Peatland Rewetting and Restoration — OA PDF; peat rewetting practice + T6 carbon/GHG + guidance. Cache PDF to .cache/corpus, page-level locator on extraction. |
| `unep_gpi_peatland_carbon_report` | grey | oa | ok | med | UNEP / Global Peatlands Initiative: peatland conservation & restoration emissions report — T6 CARBON at scale (~800 MtCO2e/yr abatement) + cost (~US$46bn/yr by 2050). Press-release landing; locate the |
| `pointblue_cv_wetland_prioritization` | tool | repo | ok | low | pointblue/cv-wetland-restoration-prioritization-fws (GitHub) — Real wetland-restoration siting/prioritization pipeline (Central Valley Joint Venture, practice explicit). BUT parameters_static.R is an  |

## Gaps / next iteration

Term contamination: \"constructed wetland\" and \"farm wetland\" in OpenAlex are dominated by treatment-engineering (subsurface-flow CWs for dairy/aquaculture/stormwater effluent) which is OUT of scope; the productive signal sits under \"wetland creation\" / \"created wetlands (freshwater/riverine, agricultural landscape)\" and \"paludiculture\". CROSS-FAMILY OVERLAP: peat rewetting/paludiculture is boundary between F2 creation (new wetland on non-wetland land) and restoration/rewetting of drained peat; included here only for the T6 carbon/adoption outcomes per unit spec but should be de-duplicated against a wetland_management restoration family if one exists. LMIC/TROPICAL-PEAT thin in OA: strong Indonesia paludiculture hit, but the highest-value tropical-peat synthesis is paywalled (acquisition_queue); Congo Basin only as a mapping baseline. TOOL GAP: no open GIS-MCDA wetland-creation siting tool with hardcoded, extractable thresholds surfaced (pointblue pipeline is data-driven/stubbed; treat like spatMCDA.R -> no EV). Cost/ha figures so far are grey (Ramsar/UNEP) -> apply grey positive-bias discount and seek a peer-reviewed cost-per-ha-restored source before locking T6 economic ranges. ES/FR/PT title searches not exhausted (EN corpus saturated the T6 need); a Congo-basin (FR) / Amazon-Andes (ES/PT) pass would strengthen LMIC coverage if F3-peat becomes priority.
