# How agroforestry T3/T6 rows are generated, and whether a TTL can use them (2026-10-22)

**Scope.** This is a read-only review. I did not edit any register, recipe or code file.
**Inputs.** The register at HEAD of `feat/ouattara-2017-round` (commit 9650b2e), plus the AF recipe files.
**Reproducibility.** I re-ran `scripts/synthesise-t3t6.py` logic in memory against the current register. It reproduces the CSVs on disk exactly: 94 T3 rows and 93 T6 rows, with 0 class differences and 0 evidence-id differences. The AF tables are therefore fresh and deterministic.
**Sensitivity runs.** I ran two tests. In the first I removed each unit on its own, re-ran the whole AF synthesis, and recorded which rows changed. In the second I did the same for each source. Scripts are in the session scratchpad (`loo.py`, `fit.py`).
**Companion file.** `pipeline/staging/eval_oct22/af_high_leverage_units.csv` lists 167 units with columns `evidence_id,record_ids,why`.

---

## 1. The pipeline as it runs today, with the AF numbers at each step

| # | Step | Where in the code | AF numbers |
|---|---|---|---|
| 0 | **Load units.** Units must be AF, with role `nbs_effect` or `asset_vulnerability`, not dropped, and not in a parked family | `synthesise-t3t6.py:139-187` | There are 675 AF effect units in EV; 57 are dropped, leaving 618 live. The 4 homegardens units are parked (`qualitative_only`), so **614 are pooled** (585 `nbs_effect`, 29 `asset_vulnerability`) from 83 sources. |
| 1 | **Claim-scope gate.** Species-specific units are removed. Crop-specific units are removed unless `allow_crop_scope` is set | `cell_synthesis.py:2233-2237`; policy reader at `synthesise-t3t6.py:121-136` | 17 species-specific and **113 crop-specific units are excluded from every cell**, 95 of them F5 shaded-perennial (see drift D1). That leaves **488 practice units from 74 sources** able to vote. |
| 2 | **Route through XW.** A unit's variable must have an XW row to the cell. In T3, a unit that states no hazard is dropped when its variable reaches more than one hazard, or reaches the hazard only through a component or proxy route | `:2242-2317` | The run tries 43 cells (16 T6, 21 T3 livelihood, 6 asset-threat). Most T3 losses are units with no stated hazard. The drop log records 1,256 drops of `crop_yield` and 661 of `household_income` for this reason (counted per cell attempt). 8 variables are unmapped (ecosystem_service 10, soil_permeability 5, tree_canopy_cover 5, …). |
| 3 | **Lineage dedupe.** Each source's own arms are kept, with the source's weight split equally across them; echoes are collapsed | `dedupe_for_cells :1348-1389` | 8 echoes were collapsed. |
| 4 | **Rank and weight.** Weight = tier × basis × **design** × grey × transfer × XW factor × ns × scoping-candidate 0.5 × bundle share × no-normal-year 0.7 | `unit_rank :536-583`, `unit_weight :629-654` | Of the 488 practice units, 318 (65%) have `strength_class=unspecified` and so vote on direction only. Design mix: meta-analysis 114, observational 86, quasi-experimental 77, expert 48, practitioner rating 42, RCT 24, review 23, model 21, none 28. Basis mix: cited_secondary 221, primary_measured 213, expert_assertion 37, table 13, modelled 4. |
| 5 | **Partition the voters.** Units with a reference comparator, a non-net carbon gas, an existing-use comparator, an unmanaged comparator (T3), an envelope misfit (production) or a society-level beneficiary (poverty) are held out of the vote but stay on the row | `partition_voters :2120-2191` | For AF this mainly affects the Batcheler fire units (`unmanaged_state`), which makes both fire roll-ups data-deficient. |
| 6 | **Evidence floor.** A cell may state a class only with ≥2 sources **or** at least 1 `primary_measured`/`table` unit. Below that the row is published as DATA DEFICIENT | `meets_evidence_floor :2062-2076` | **39 rows are data-deficient: 24 in T3 (15 livelihood, 9 asset) and 15 in T6.** |
| 7 | **Sign vote.** Modal sign, agreement A, and a conflict flag when the minority share is ≥1/3 | `_reconcile_rank :660-708` | — |
| 8 | **Strength.** Weighted median over modal-sign units that state a size, followed by caps in order: proxy cap (direct units set the strength) → modelled cap → size-sparse cap → intensity discount (T3) → maladaptation list | `:2379-2407`, `:1397-1630` | 2 roll-ups carry `size_sparse` (drought×all, drought×cropping_rainfed). 10 roll-ups are `intensity_limited`; the discount is small (share 0.07–0.25), so no roll-up class actually moved. |
| 9 | **Confidence.** Evidence level × agreement, read from the IPCC matrix. Agreement is forced to 0 when there is only 1 independent source | `_reconcile_group :1126-1163`, `evidence_level :736-749` | T3 confidence: very_low 37, low 4, medium 29, high 15, very_high 9. T6 confidence: very_low 24, low 4, medium 29, high 16, very_high 20. |
| 10 | **Scope rows.** Rows by `aez` and `income_group` (T6 also by `farming_system`), each with ≥2 sources | `:2551-2649` | **33 scope rows (10 T3, 23 T6).** 11 of these are high-income scope rows. `context_dependent` is set on 1 row. |
| 11 | **Family rows.** A family row is produced when the family has ≥2 sources anywhere in the register. It is dropped if identical to the roll-up | `synthesise_cell_with_families :2798-2909` | **111 family rows (57 T3, 54 T6).** `family_spread` is set on 11 roll-ups. |
| 12 | **Family vote.** The roll-up class is re-derived from family-row votes weighted by sqrt(n_sources). Dissent ≥1/3 → `conflicting_evidence` | `_family_vote :2960-3069` | **The vote changed 6 of 43 roll-up classes:** production_gap strong_positive→conflicting, water_stress slight_positive→conflicting, drought×cropping_rainfed moderate→conflicting, wind_cyclone×all moderate→conflicting, soil_erosion strong→moderate, drought×pastoral_rangeland low→moderate. |
| 13 | **Effect locus, asset weights, prose.** Prose is applied from the sidecar only where the evidence ids match | `synthesise-t3t6.py:309-322`, `prose.apply_prose` | AF effect locus is `on_farm`. Asset weights are blank (`weights_incomplete`; there are asset rows for only 6 of the 7 hazards, and 2 of them are data-deficient). 0 rows are "prose pending". |

**What comes out.** There are **187 rows: 43 roll-ups (27 T3 + 16 T6), 111 family rows and 33 scope rows.**

| | T3 | T6 |
|---|---|---|
| Classed rows | 70 (of which 6 conflicting) | 70 (of which 10 conflicting), plus 8 economic rows |
| Data-deficient | 24 | 15 |
| Single-source rows (all rows) | 32 | 25 |
| Transfer class | in_context 49, adjacent 39, out_of_context 6 | in_context 62, adjacent 27, out_of_context 4 |

**Roll-up classes**
- **T3 livelihood (21):** moderate 6, low 9, conflicting 2, data-deficient 4.
- **T3 asset (6):** very_high 1 (drought), high 1 (fire), low 2 (flood, wind), and "none" 2 — but both "none" rows are actually data-deficient (see R3).
- **T6 (16):** moderate_positive 4 (biodiversity, carbon, rural_poverty, soil_erosion), slight_positive 4, conflicting 2 (production_gap, water_stress), data-deficient 3 (gender, water_quality, cost_per_tco2e), economic 3.

---

## 2. Where the method doc and the code disagree

The method doc (`methodology/T3_T6_generation_method.md`, still marked "v0.1 draft 2026-09-29") has not been updated since about 2026-10-05. It never mentions the evidence floor or data-deficient rows, the `conflicting_evidence` class, the family vote, voter partitioning, the design weights or the size/modelled/intensity caps. The spec (`schema/spec.md:429`, `:638`, v0.4.2) and the AGENTS lock carry part of that. The doc should be revised before anyone outside the team reads it.

**Code drift that changes output**

| # | Rule in the doc / lock | What the code does | Effect on AF |
|---|---|---|---|
| D1 | AGENTS lock: crop-specific evidence is re-included for **AF F5 shaded systems** (`crop_scope_policy.csv` row `agroforestry,agroforestry__shaded_perennial,true`) | `synthesise-t3t6.py:132` reads only rows with an **empty** family. AF therefore gets `allow_crop_scope=False` everywhere, and the engine has no per-family switch (`cell_synthesis.py:2233-2235`). | **95 F5 units (cocoa and coffee shade evidence) never vote.** The F5 family rows rest on 17 practice units, and the cocoa evidence from Niether, Philpott, Vaast, Gateau-Rey and Mensah is invisible. This is the largest silent loss in the AF corpus. |
| D2 | §2.2: a family row needs ≥2 independent sources **hitting the cell** | `:2865-2866` counts the family's sources over the whole pre-XW register slice; the code comment at `:2887-2890` admits this over-counts. The cell-level floor (`:2062`) then lets 1 measured unit through. | **13 classed family rows rest on 1 source** (e.g. `planted_silvoarable__carbon_sequestration_potential` = no_relationship from snapp_2010_econ alone; `silvopastoral__asset_threat__drought` = high from the WB CMSCR ICR alone). These rows also vote in the family vote. |
| D3 | §7.3: evidence level counts independent sources after dedupe | `independent_sources :711-733` counts a meta-analysis as its `n`. Meanwhile `meets_evidence_floor` and `n_sources` count source ids, so the two disagree. | `cross_family__water_stress` reads **robust×high→very_high from 2 sources** (Kuyah 2019 carries 90% of the weight). `cross_family__cost_reduction` reads **high from 1 source**. `silvopastoral__biodiversity_priority` reads robust from 4 sources. |
| D4 | §7.6–7.7: economic magnitude only with ≥2 sources | `:2525` passes `min_sources=1 if is_econ` (Pete's 2026-10-05 ruling that economics are ordinal) | `cost_per_hectare_restored` and `cost_per_beneficiary` are classed from 1 source (CRS 2023, 2 units). Dropping one of its units flips cost_per_hectare_restored from slight to strong. |
| D5 | §2.3: a scope row is emitted when its rank differs or the global row is out of context | `:2637-2641` adds a third trigger: **any scope group when global agreement is low** | This adds rows; it is part of why there are 33 scope rows. |
| D6 | Spec: `asset_sensitivity` is blank (not "none") when there is no class | `:2462-2468` writes `asset_sensitivity(rank=0)` = **`none`** for data-deficient asset rows (no data-deficient guard, unlike `mitigation_potential` at `:2473`) | **9 AF asset rows say "none"** (no damage), including `cross_family__asset_threat__drought`, whose own prose says "severe drought can raise seedling mortality by 35 to 40%". M2b would read these as tolerant. This is a bug. |
| D7 | One definition of "measured" | There are three: `_MEASURED_BASES` (`:1438`, which includes cited_secondary and modelled) for the intensity cap and maladaptation; `{primary_measured, cited_secondary}` (`:1596`) for the modelled cap; `MEASURED_BASES` (`:2059`, primary_measured and table only) for the evidence floor. The intensity cap leaves out `table`. | The rules disagree on which units count. Cited-secondary review statements trigger intensity discounts and harm flags, but cannot lift a cell over the floor. |
| D8 | §7.2: a proxy-only cell is capped at moderate | The direct-first branch (`:1415-1427`) **replaces** the pooled rank with a direct-only median. That can move the rank **up** as well as down. | `strength_from=direct` on drought×pastoral_rangeland, wind_cyclone×all and water_stress. It is a design choice, but it is not a cap. |
| D9 | Family vote (lock, 2026-10-19) | When the vote changes the label, `:3042-3066` updates the class (and confidence only when the result is conflicting), then **appends** a sentence to the pooled statement instead of rewriting it. It does not re-apply the `very_high` gate or the caps. | **4 roll-ups have a statement whose confidence differs from the field:** drought×cropping_rainfed ("very_high" vs medium), wind_cyclone×all (high vs low), production_gap (high vs medium), water_stress (high vs medium). Their statements open with "agroforestry strongly reduces production_gap…" and then say "conflicting". |
| D10 | §3.3: `income_group` takes values from a fixed vocabulary; `check_context` enforces it | SRC/unit values `lic_lmic`, `mixed`, `mostly_upper_middle` and `low_/_lower_middle` reach the engine and show up in envelopes. 43 of 74 AF sources have a blank `study_income_group`, against the §11 promise of a deterministic back-fill. | Unknown income scores distance 1. 7 classed roll-ups get more than 50% of their weight from unknown-income units (all the heat_stress farming-system rows, wind×mixed, biodiversity 0.78, catchment_water_yield 1.0). |
| D11 | §7.1 weight formula and §7.8 table | The code adds design weight (`design_weights.csv`), scoping-candidate 0.5, bundle share, no-normal-year 0.7, and a split of each source's weight across its arms. These are ratified in AGENTS and the lookups but not in the doc. | Documentation only, but `review` ×1.25 combined with cited_secondary 0.4 lets review sentences dominate (R2). |
| D12 | §14 PR6 acceptance: compare against the 17 seed rows | `T3T6_BENCHMARK.md` is from the 72-unit era, with its last update at "T3 75 / T6 74 rows". | There is no current benchmark for 614 units and 187 rows. |

---

## 3. Fitness problems a TTL would hit

All counts are over **140 classed rows**: 31 roll-ups, 76 family rows, 33 scope rows. Data-deficient and economic rows are excluded. Weights are those the engine actually applied, including the per-arm split.

**Too many rows to read**
- There are 187 rows for one NbS, and a single cell such as `production_gap` has 11 rows.
- A TTL needs the 43 roll-ups at most. 9 of those are data-deficient, and the 6 asset roll-ups belong to M2b.
- The `production_gap` conditionality is **7,551 characters** long, and several more run past 2,000.

**Rows that rest on one or two sources**
- 13 classed family rows have 1 voting source; 31 have ≤2.
- Among roll-ups, 2 have ≤2 sources, but **12 roll-ups get more than 40% of their weight from a single source**:
  - Quandt 2017 (a farmer-perception survey): 61% of `flood_hazard`.
  - IPCC AR6 WG3: 71% of `catchment_water_yield`.
  - Souza 2011: 62% of `frost__all`.
  - Kuyah 2019: 42% of `water_stress`.
  - Philpott 2008: 53% of `asset_threat__wind`.
  - Seghieri 2019: 57% of `asset_threat__fire`.
- Across all classed rows, 76 of 140 have one source carrying more than half the weight.

**Practitioner and expert ratings**
- Most rows are not driven by ratings: 6 classed rows get more than 50% of their weight from practitioner or expert design, and 25 get more than 25%.
- Where ratings do drive a row, it matters:
  - `silvopastoral__drought__pastoral_rangeland` (moderate) is **100%** expert or practitioner weight.
  - Through the family vote, that row **raises the roll-up `drought×pastoral_rangeland` from low to moderate**. Dropping any one of 5 units (Montagnini, Navas, Cisneros, Saucedo, FAO-Senegal) puts it back to low.
  - `regeneration_farmland__drought__agro_pastoral` is 74% ratings.
  - The asset roll-ups for flood (52%), wind (47%) and fire (35%) are mostly WOCAT ratings.

**Second-hand review sentences**
- `cited_secondary` evidence carries more than 50% of the weight in **18 of 31 classed roll-ups**. This includes every heat_stress roll-up, all three wind roll-ups, drought×agro_pastoral (80%), drought×pastoral_rangeland (81%), and T6 `drought_hazard` and `heat_stress_hazard`.
- The T3 hazard layer is largely built from review statements, not measured hazard-year contrasts. Only 15 practice units state a hazard severity other than unspecified.

**High-income and unknown-context evidence**
- HIC evidence never carries more than 50% of a roll-up (the transfer weights work).
- 14 classed family or scope rows are more than 50% HIC; 10 of these are `income_group-high` scope rows that are in context only for HIC.
- Out-of-context family rows include `shaded_perennial__soil_erosion_risk` (100% HIC) and `planted_silvoarable__drought__cropping_rainfed` (56% HIC). The second one votes "conflicting" in the family vote and helps turn the drought×cropping_rainfed roll-up into conflicting.
- The family vote does not discount out-of-context family rows.
- The larger problem is unknown income: 7 classed roll-ups are more than 50% unknown-income.

**Conflicting rows**
- 16 rows are conflicting (4 of them roll-ups). Every one has substantive "what separates the sides" prose, so guidance exists.
- But 3 of the 4 conflicting roll-ups are conflicting only because of the family vote. Their pooled agreement was high or medium (0.77–0.93).
- Removing **any one of 12 units** turns `production_gap` back to strong_positive. The conflict verdict is that fragile (see section 5).

**Prose that does not match the class**
- (a) 4 roll-up statements quote a different confidence from the field (D9).
- (b) 9 asset rows say `none` while being data-deficient (D6), including one whose prose describes 35–40% seedling mortality.
- (c) **Data-deficient rows carry mechanism prose written on 10-05/10-06, when they still had a class.** For example, `regeneration_farmland__flood__all`: "FMNR … mitigates the impact of annual floods". `apply_prose` only refuses a mismatch when the sidecar entry has a `class` key, and 254 of 293 AF entries do not (`prose.py:109`). That is 80 T3 and 68 T6 rows whose prose is protected only by an evidence-id match.

**High confidence on weak classes**
- 25 rows pair a weak class (low or slight) with high or very_high confidence. Examples: `heat_stress__all` low / very_high; `drought__mixed_crop_livestock` low / very_high; T6 `drought_hazard` slight / very_high.
- This is correct IPCC usage, but a TTL will read "very_high" as "very effective". The display needs to show the class first and say it explicitly.

**Little human review behind the output**
- 6 of 488 practice units are `reviewer_ok=true`.
- 313 of 488 are still at ruleset v1.6.0 (the migrated era).
- Of the 167 high-leverage units, 1 is reviewed.

---

## 4. Top 5 risks to the credibility of the AF output, ranked

1. **Roll-up verdicts flip when a single unit is removed.**
   - Removing one unit changes the class of **119 of 187 rows**: 110 units each flip at least one class or remove a row, and 37 of them flip a roll-up.
   - `agroforestry__production_gap` (conflicting) goes back to strong_positive if any one of 12 units is removed: ev_crop_yield_watts22_10, castle21s_2, reed17_2, dsantos23_3/_4, santos25_5, sileshi12_1, place05_6, baker25h2_6/_7, coulibaly16_2, and others.
   - `agroforestry__drought__cropping_rainfed` (conflicting) goes back to moderate without ev_crop_yield_watts22_10.
   - `agroforestry__wind_cyclone__all` (conflicting) goes back to moderate without taboada20_5 **or** lasco14_1.
   - `agroforestry__water_stress` (conflicting) goes back to moderate_positive without sida18_1.
   - `agroforestry__drought__all` becomes conflicting if Quandt 2017 is removed.
   - The family vote takes small, thinly sourced family rows (some with 1 source, some out of context, some 100% ratings) and gives them a sqrt(n) say over a 44-source pool.
2. **The F5 shaded-perennial evidence is silently excluded (D1).**
   - 95 units across 28 sources never reach a cell, against a locked policy.
   - Affected rows include every `agroforestry__shaded_perennial__*` row (e.g. `shaded_perennial__heat_stress__all`, which rests on 1 source) and the `farming_system-tree_perennial` scope rows. The `production_gap` and `rural_poverty` roll-ups lack the cocoa and coffee arm.
3. **Asset rows report false tolerance (D6), and the asset layer is thin.**
   - 9 data-deficient asset rows say `none`, e.g. `agroforestry__asset_threat__heat_stress` and `agroforestry__cross_family__asset_threat__drought`.
   - `agroforestry__asset_threat__drought = very_high` (confidence high) rests on 3 sources. It drops to high without ev_establishment_survival_gateau18_2 alone, or without the WB CMSCR ICR (cmscr20_4/_5) or Watts 2022.
   - M2b weights are blank (`weights_incomplete`).
4. **Statements contradict their own fields after the family vote (D9), and prose can outlive its class (prose.py:109).**
   - `agroforestry__production_gap`, `__drought__cropping_rainfed`, `__wind_cyclone__all` and `__water_stress` all open by asserting the pooled class with the wrong confidence.
   - 15 data-deficient livelihood rows carry pre-floor mechanism prose that reads like a positive finding.
5. **The hazard layer rests on second-hand and context-less evidence.**
   - cited_secondary carries more than 50% of the weight in 18 of 31 classed roll-ups.
   - 65% of units state no strength.
   - 7 roll-ups are more than 50% unknown-income (`agroforestry__heat_stress__{agro_pastoral, mixed_crop_livestock, pastoral_rangeland, tree_perennial}`, `__wind_cyclone__mixed_crop_livestock`, `__biodiversity_priority`, `__catchment_water_yield`).
   - Single sources dominate key cells: `flood_hazard` (Quandt 61%), `catchment_water_yield` (IPCC 71%).
   - Meta-analysis n inflation (D3) gives `agroforestry__cross_family__water_stress` very_high confidence from 2 sources.

---

## 5. High-leverage units (for a risk-based QA sample)

**Method.** I removed each of the 443 units that appear on any row, one at a time, re-synthesised all of AF, and recorded every row whose class (or data-deficient status) changed, or that vanished. I then ran the same test per source for roll-ups and attributed a roll-up flip to the source's units in that row.

**Result.** 167 units are high-leverage:
- 110 flip a class at unit level; the rest only via their source.
- **99 touch a roll-up.**
- By source: Baker 2025 (16), Quandt 2017 (11), Castle SR 2021 (8), Dobhal 2024 (8), WOCAT 507 (8), Batcheler 2024 (7), Watts 2022 (6), WB CMSCR 2020 (6), Nguyen 2026 (6), WOCAT 1358 (5), Sileshi 2012 (5), FAO Senegal (5).
- By basis: 81 cited_secondary, 72 primary_measured, 13 expert_assertion.
- Reviewed: 1 of 167.

Units that flip a **roll-up** on their own (the QA priority):

| evidence_id | roll-up it drives (current → without it) |
|---|---|
| ev_crop_yield_watts22_10 | production_gap conflicting→strong_positive; drought×cropping_rainfed conflicting→moderate |
| ev_crop_yield_{castle21s_2, reed17_2, dsantos23_3, dsantos23_4, santos25_5, sileshi12_1, place05_6, baker25h2_6, baker25h2_7}, ev_agricultural_production_value_coulibaly16_2 | production_gap conflicting→strong_positive |
| ev_soil_water_retention_sida18_1 | water_stress conflicting→moderate_positive |
| ev_wind_cyclone_hazard_taboada20_5, ev_windbreak_protection_lasco14_1 | wind_cyclone×all conflicting→moderate |
| ev_livestock_productivity_montagnini15_4, ev_livestock_productivity_navas10_3, ev_forage_productivity_{faosen24_21, cisneros24_1, saucedo23_1} | drought×pastoral_rangeland moderate→low |
| ev_erosion_hazard_cmscr20_2 / ev_erosion_hazard_wocat_1358_2017_soil_loss | soil_erosion_risk moderate→strong / →slight |
| ev_establishment_survival_gateau18_2 | asset_threat×drought very_high→high |
| ev_asset_flood_wocat_1358_2017_general_river_flood | asset_threat×flood low→moderate |
| ev_microclimate_buffering_santos25_10 | heat_stress×mixed_crop_livestock moderate→low |
| ev_microclimate_buffering_mensah23_1 | heat_stress×tree_perennial: the row disappears (sole driver) |
| ev_t3_wind_buffer_quandt17_4, ev_crop_yield_dobhal24_7 | wind_cyclone×mixed_crop_livestock: the row disappears / moderate→low |
| ev_groundwater_recharge_potential_{vannoordwijk21_6, ipccar6_1} | catchment_water_yield slight_positive→data-deficient |
| ev_project_cost_crs23_1 / _2 | cost_per_beneficiary / cost_per_hectare_restored class changes |
| ev_waterlogging_hazard_dobhal24_9; ev_sediment_retention_wocat_507_2019_downstream_siltation; ev_asset_extreme_rainfall_wocat_1358_2017_local_rainstorm; ev_crop_yield_ipccar6ch5_1; ev_project_cost_ipccsrccl6_4 | the sole unit of a roll-up row (waterlogging ×2, water_quality_risk, asset extreme_rainfall, asset heat_stress, cost_per_tco2e) |

Roll-ups that flip only when a whole source is removed:
- Quandt 2017 → drought×all becomes conflicting.
- Nguyen 2026 → biodiversity moderate→strong.
- Souza 2011 → frost becomes data-deficient.
- Batcheler 2024 → fire×agro_pastoral row disappears.
- Kiptot 2011 → gender row disappears.
- WOCAT 507 → asset fire high→low.
- WB CMSCR and Watts 2022 → asset drought very_high→high.

The full list, with every row each unit drives (family and scope rows included), is in `af_high_leverage_units.csv`, ordered with roll-up drivers first.

**Suggested QA order**
1. The 11 production_gap swing units together with Watts22_10 (they decide the headline yield verdict).
2. The 5 silvopastoral rating units that lift drought×pastoral_rangeland.
3. The asset-drought trio.
4. Sole-unit roll-ups.

**Caveat.** Confidence-only changes (93 unit-level instances) are not in the CSV.

---

## 6. Fix list (not applied)

- **D1:** have `crop_scope_policy` return per-family settings and pass them into `synthesise_cell`.
- **D6:** add a data-deficient guard in the `asset_sensitivity` assignment.
- **D9:** after the family vote, rebuild the statement from the new class and confidence instead of appending to it.
- **Prose:** stamp `class` on every sidecar entry and refuse prose without it (`prose.py:109`).
- **D2:** count family sources per cell.
- **D3:** pick one way of counting sources.
- **D7:** use one "measured" basis set.
- **Family vote:** require each voting family row to clear the floor with ≥2 sources, and discount out-of-context family rows in the vote.
- **Method doc:** update to v0.2 covering the floor, conflicting class, family vote, voter partition, caps and design weights.
- **D12:** regenerate the AF benchmark.
- **TTL display:** show roll-ups only, class before confidence, and a one-line conditionality digest.
