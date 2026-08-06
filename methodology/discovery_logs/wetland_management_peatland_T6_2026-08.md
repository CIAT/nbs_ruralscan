# Discovery log — Wetland Management · peatland · T6

- Run `wetland_management_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.2 · nbs_id `wetland_management`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 1944 | 15 | 5 |
| updated_lit | 1237 | 35 | 6 |
| grey | 15 | 15 | 5 |
| tool | 2 | 2 | 0 |

### Verbatim search terms

- **stock:** `title.search:(peatland OR peat OR paludiculture OR mire OR bog OR fen) AND (restoration OR rewetting OR suitability); sort=cited_by_count:desc`
- **updated_lit:** `title.search:(peatland OR paludiculture OR peat) AND (rewetting OR restoration OR paludiculture); from_publication_date:2015-01-01; sort=cited_by_count:desc  [+ refinements: title.search:tropical peatland AND (restoration OR rewetting OR paludiculture) (count=65); title.search:paludiculture AND (economics OR cost OR carbon) (count=11)]`
- **grey:** `WebSearch EN: 'peatland restoration rewetting cost per hectare carbon Ramsar FAO IUCN Wetlands International Global Peatlands Initiative guidance'; 'paludiculture tropical peatland restoration suitability GIS site selection guidance report Indonesia Congo'`
- **tool:** `GitHub API q=peatland+rewetting+OR+paludiculture+OR+peat+suitability sort=stars; WebSearch 'github peatland restoration suitability rewetting depth-to-water index python google earth engine'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `prompt_rewetting_climate_2020` | stock | oa | ok | high | Prompt rewetting of drained peatlands reduces climate warming despite methane emissions — Top-cite (437). Core T6 CARBON outcome: rewetting -> net climate benefit despite CH4. Quantitative GWP evidenc |
| `peatland_protection_restoration_mitigation_2020` | stock | oa | ok | high | Peatland protection and restoration are key for climate change mitigation — T6 carbon-mitigation outcome + restoration rationale. Gold OA. Explicit restoration/rewetting practice. |
| `tropical_peatland_restoration_ecology_sea_2008` | stock | repo | ok | high | Restoration Ecology of Lowland Tropical Peatlands in Southeast Asia: Current Knowledge and Future Research Directions — Seminal (290) TROPICAL-peat LMIC (SE Asia) restoration reference. green OA. Hydr |
| `canal_blocking_tropical_kalimantan_2013` | stock | repo | ok | high | Canal blocking strategies for hydrological restoration of degraded tropical peatlands in Central Kalimantan, Indonesia — TROPICAL Indonesia. Rewetting technique (canal blocking) + water-table restorat |
| `peatland_restoration_ecosystem_services_2016` | stock | paywalled | ok | high | Peatland Restoration and Ecosystem Services — T6 ecosystem-services framing across water/carbon/biodiversity. Closed access -> acquisition_queue (Namita-J). |
| `global_peatlands_assessment_2022` | updated_lit | oa | ok | high | Global Peatlands Assessment: The State of the World's Peatlands - Evidence for Action (UNEP/GPI) — Authoritative global assessment. T6 outcomes + restoration action + carbon; global incl. tropical (Co |
| `tropical_peatland_restoration_techniques_review_2018` | updated_lit | paywalled | ok | high | A Review of Techniques for Effective Tropical Peatland Restoration — TROPICAL restoration techniques + implementation cost context. Closed -> acquisition_queue. |
| `degraded_tropical_peatland_indonesia_review_2021` | updated_lit | oa | ok | high | Restoration of Degraded Tropical Peatland in Indonesia: A Review — TROPICAL Indonesia LMIC review. gold OA. Restoration methods, hydrology limiter, T6 outcomes. |
| `paludiculture_tropical_peatland_landuse_2020` | updated_lit | paywalled | ok | high | Paludiculture as a sustainable land use alternative for tropical peatlands: A review — Core F3 PALUDICULTURE tropical review. T6 production + carbon + suitability of wet-crop species. Closed -> acquis |
| `paludiculture_german_fen_economy_2022` | updated_lit | oa | ok | high | Saving soil carbon, greenhouse gas emissions, biodiversity and the economy: paludiculture as sustainable land use option in German fen peatlands — Direct T6: carbon + biodiversity + ECONOMICS/cost of  |
| `smallholder_rewetting_oilpalm_sumatra_2020` | updated_lit | oa | ok | med | Smallholder perceptions of land restoration activities: rewetting tropical peatland oil palm areas in Sumatra, Indonesia — TROPICAL adoption/MEL evidence (smallholder perceptions of rewetting) -> oper |
| `ramsar_tr11_peatland_rewetting_guidelines_2021` | grey | oa | ok | high | Global guidelines for peatland rewetting and restoration (Ramsar Technical Report No. 11) — Authoritative Ramsar guidance: rewetting/restoration practice + siting principles + outcomes. OA PDF -> Shar |
| `giesen_nirmala_tropical_peatland_restoration_indonesia_2018` | grey | oa | ok | high | Tropical Peatland Restoration Report: the Indonesian case (Giesen & Nirmala, for BRG) — TROPICAL LMIC (Indonesia BRG) implementation report: paludiculture species list, rewetting techniques, cost + ar |
| `gpi_qa_peatland_rewetting_2023` | grey | oa | ok | med | Questions & Answers: Bringing Clarity on Peatland Rewetting and Restoration (Global Peatlands Initiative) — GPI/UNEP clarification on rewetting outcomes (carbon, CH4 trade-off). OA PDF. Grey positive- |
| `iucn_peatlands_climate_brief` | grey | oa | ok | med | Peatlands and climate change (IUCN issues brief) — IUCN carbon-outcome + restoration rationale. Web source -> url + snapshot + section locator on ingest. |
| `global_wetland_outlook_2025_financing` | grey | oa | ok | med | Global Wetland Outlook 2025: Valuing, Conserving, Restoring, and Financing Wetlands — Wetlands International / Ramsar. T6 valuation + FINANCING/cost framing. Peatland is a subset -> extract peat-speci |

## Gaps / next iteration

TOOL GAP (highest): no dedicated peatland-restoration/paludiculture-siting MCDA tool exists on GitHub where rewetting/restoration is an actual code branch. Closest (muaffanalfaiz agrivoltaic) is off-PICOS (solar); NASA WET is generic wetland extent; G-MCDA is NbS-agnostic. F3 siting logic (peat depth + drainage state + water-table limiter) will likely need to be authored in-recipe from literature/guidance rather than inherited from a tool.

LMIC-CONGO GAP: strong SE-Asia (Indonesia/Kalimantan/Sumatra) tropical-peat coverage but NO standalone Congo Cuvette Centrale restoration/paludiculture source surfaced; only referenced within global assessments. Targeted Congo Basin / Cuvette Centrale + FR-language grey search recommended before T6 synthesis.

COST GAP: cost-per-ha-restored figures are thin — Ramsar TR11 and grey docs give rationale not unit costs; German-fen paludiculture economics (temperate) and Giesen&Nirmala (Indonesia) are the main cost anchors. A dedicated cost/CBA search (WB peatland project PADs/ICRs; BRG budgets) would strengthen T6 economic_value_range.

CH4 TRADE-OFF: T6 carbon rows must encode the rewetting CH4 vs CO2-avoidance trade-off (multiple sources flag it) — not a net-benefit single number; site/water-table dependent.

Grey positive-bias discount (COI axis) applies to benefit/cost claims in GPI/IUCN/Wetlands-Intl outputs at synthesis.
