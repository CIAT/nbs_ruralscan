# Discovery log — Forest Restoration · active_planting · T6

- Run `forest_restoration_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** discovery + screening only. No extraction.
- **grey + tool = complete.** **stock + updated_lit = IN PROGRESS** — OpenAlex hit its daily budget (HTTP 429, resets midnight UTC); candidates below are provisional (WebSearch/canon fallback), to be finalised with real OpenAlex nets on rerun.

## grey + tool candidates (final)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `trillion_trees_real_cost_2022` | grey | oa | ok | high | Defining the Real Cost of Restoring Forests (Trillion Trees / WWF-BirdLife-WCS) — Grey diamond-ish; per-ha cost ranges for active planting vs ANR (planting+fencing up to ~$3,750/ha; active restoration |
| `iucn_flr_costbenefit_framework_2015` | grey | oa | ok | med | A Cost-Benefit Framework for Analyzing Forest Landscape Restoration Decisions — IUCN; scoping-grade cost-benefit structure for restoration interventions incl. active planting. Method/framework rather  |
| `fao_flr_cost_effective_note` | grey | oa | ok | med | Forest landscape restoration measures as a cost-effective solution (FAO OpenKnowledge) — FAO grey; ANR direct establishment ~USD 257/ha yr1 + up to USD 213/ha/yr maintenance 5 yrs — indicative cost an |
| `forest_carbon_lite_tool` | tool | repo | ok | med | forest-carbon-lite (FullCAM-lite TYF carbon + economics model) — Confirmed code branch, not README: hardcoded reforestation cost + carbon params and an explicit reforestation management flag = active- |
| `wri_iucn_roam_2014` | tool | oa | ok | high | Restoration Opportunities Assessment Methodology (ROAM) — a guide (WRI/IUCN) — Decision-support platform/methodology (not open code): delivers quantified per-intervention costs, carbon sequestered, an |
| `groa_natural_regrowth` | tool | repo | NO | low | GROA — Global Reforestation Opportunity Assessment (forc-db/GROA) — EXCLUDED from active_planting: repo model = natural-regrowth carbon mapping + field DB (F2 passive), practice mismatch per PICOS. Cr |

## stock + updated_lit candidates (PROVISIONAL — OpenAlex pending)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `road_to_recovery_asia_2023` | stock | oa | ok | high | The road to recovery: a synthesis of outcomes from ecosystem restoration in tropical and sub-tropical Asian forests — Phil Trans R Soc B synthesis, 176 sites; planted-tree mortality 18% at yr1 rising  |
| `reforestation_planting_methods_2023` | stock | paywalled | ok | high | Reforestation success can be enhanced by improving tree planting methods — J Environ Management synthesis directly on planting-method effects on survival/establishment (post-planting care ~50% surviva |
| `costeff_regen_vs_plantation_ncc_2024` | updated_lit | paywalled | ok | high | Cost-effectiveness of natural forest regeneration and plantations for climate mitigation — Nature Climate Change 2024; spatial cost_per_tCO2e comparing active plantations vs natural regen across pixel |
| `tropical_dryforest_constraints_frontiers_2024` | updated_lit | oa | ok | med | Restoration of tropical dry forest: an analysis of constraints and successes across a highly threatened biome — OA; success/failure determinants of active dry-forest restoration (survival, site select |

### Verbatim search terms (as run / attempted)

- **stock:** `OpenAlex (ATTEMPTED, BLOCKED): title.search:(reforestation OR afforestation OR "restoration planting") AND (survival OR success OR carbon), sort=cited_by_count:desc. FALLBACK WebSearch: reforestation tree planting seedling survival rate restoration success meta-analysis tropical`
- **updated_lit:** `OpenAlex (ATTEMPTED, BLOCKED): title.search:(reforestation OR "tree planting" OR "forest restoration") AND (cost OR "seedling survival" OR "restoration success"),from_publication_date:2015-01-01. FALLBACK WebSearch: cost per hectare reforestation active tree planting restoration developing countries USD`
- **grey:** `WebSearch EN: FAO reforestation restoration cost per hectare survival monitoring guidelines forest landscape restoration | WebSearch ES: costo por hectárea reforestación restauración supervivencia plantación América Latina FAO CIFOR`
- **tool:** `WebSearch: github restoration opportunity mapping reforestation potential suitability carbon cost model repository | WebSearch: WRI restoration diagnostic ROAM reforestation opportunity atlas methodology carbon cost tool | GitHub API tree/commit interrogation of forc-db/GROA and forestsystemtransformation/forest-carbon-lite`

## Gaps / next iteration

BLOCKER: OpenAlex is budget-exhausted (HTTP 429, 'Insufficient budget... resets midnight UTC') across both the account (mailto) and IP, so the stock and updated_lit processes could NOT return REAL cited_by totals — those srch.retrieved counts are WebSearch-fallback proxies, not OpenAlex meta.count. ACTION: re-run the two verbatim OpenAlex booleans after 00:00 UTC to capture true high-cite/recent totals and top-cited classics (e.g. Crouzeilles, Holl & Aide, Chazdon syntheses not surfaced via WebSearch). COVERAGE GAPS: (1) grey run covered EN+ES only; FR (Sahel/Central Africa reforestation cost) and PT (Brazil Atlantic Forest restoration cost/survival — a major active-planting evidence base) NOT queried — high priority given LMIC tie-break. (2) WOCAT SLM-technologies DB and 3ie/Campbell Evidence Gap Maps not yet queried for restoration T6. (3) World Bank project evidence (PADs/ICRs/IEG on reforestation programmes) not searched — key for scoping-grade cost + MEL/adoption reality. (4) No dedicated MEL/MELIA restoration-programme survival-audit source yet (Bonn Challenge / AFR100 monitoring reports). PICOS NOTE: forest-carbon-lite is Australia-calibrated (low LMIC transferability); GROA routed OUT to the natural-regeneration family. Two paywalled high-value sources queued for Namita-J.

---

## stock + updated_lit — FINALISED (OpenAlex online, run `fr_stocklit_finish_2026-08`, 2026-08-05)

Supersedes the provisional section above (OpenAlex was budget-blocked at first pass).

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 1683 | 15 | 4 |
| updated_lit | 120 | 15 | 5 |

**Verbatim terms:**
- **stock:** `title.search:(reforestation OR afforestation OR "restoration planting" OR "enrichment planting") AND (survival OR success OR carbon OR biodiversity OR cost) ; sort=cited_by_count:desc`
- **updated_lit:** `title.search:(reforestation OR "active restoration" OR "restoration planting" OR "tree planting") AND (survival OR "seedling survival" OR success OR cost OR "cost-effectiveness") ,from_publication_date:2015-01-01 ; sort=cited_by_count:desc`

**Screened-in (stock/lit):**

| source_id | process | access | rel | title / note |
|---|---|---|---|---|
| `ten_golden_rules_reforestation_2021` | stock | oa | high | Ten golden rules for reforestation to optimize carbon sequestration, biodiversity recovery and livelihood benefits — Active-planting practice explicit; canonical T6 principles link |
| `biodiversity_gains_worlds_largest_reforestation_2016` | stock | oa | high | Opportunities for biodiversity gains under the world's largest reforestation programme — China Grain-for-Green afforestation/reforestation; biodiversity outcome of active planting  |
| `more_than_just_trees_reforestation_success_ldc_2011` | stock | paywalled | high | More than just trees: Assessing reforestation success in tropical developing countries — Reforestation success metrics in tropical developing countries (LMIC tie-break). Directly T |
| `carbon_accumulation_afforestation_metaanalysis_2009` | stock | paywalled | med | Carbon accumulation in agricultural soils after afforestation: a meta-analysis — Afforestation carbon-outcome meta-analysis (967 cites); quantitative T6 carbon-sequestration magnit |
| `restoration_success_nr_vs_active_tropical_2017` | updated_lit | oa | high | Ecological restoration success is higher for natural regeneration than for active restoration in tropical forests — Sci Adv meta-analysis directly comparing active planting vs natu |
| `lowcost_co2_removal_tropical_reforestation_2019` | updated_lit | paywalled | high | Potential for low-cost carbon dioxide removal through tropical reforestation — Cost_per_tCO2e for tropical reforestation with spatial cost surfaces; direct T6 cost-effectiveness me |
| `measuring_reforestation_success_biodiversity_ecofunction_2016` | updated_lit | oa | high | Measuring the success of reforestation for restoring biodiversity and ecosystem functioning — Biodiversity + ecosystem-function outcome metrics for reforestation success; defines m |
| `topography_functional_traits_tropical_reforestation_success_2017` | updated_lit | oa | med | The role of topography and plant functional traits in determining tropical reforestation success — Links reforestation success to topography (spatial/suitability) + traits; bridges |
| `reforestation_success_improved_planting_methods_2023` | updated_lit | oa | med | Reforestation success can be enhanced by improving tree planting methods — Active-planting method effects on survival/success; T6 conditionality (technique -> outcome). Hybrid OA,  |
