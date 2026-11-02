# T3/T6 developer handover: how to read and use the effect tables

For the development and design teams building the TTL tool and pilot notebooks. It covers what the T3, T6 and T6E tables contain, how their rows were aggregated from evidence, how each row turns into what a TTL sees, and how to pick the rows that apply to a study area.

The method is the same for every NbS. Agroforestry is used as the worked example only because it has the most rows. Suitability (T4) has its own handover: [T4 developer contract](T4_developer_contract.md).

**The tables are live.** Evidence is still being added (for agroforestry, 44 more papers are waiting to be extracted), and every row is regenerated when it is. Read the tables at run time. Never copy classes or confidence levels into code.

## 1. What the tables are

| Table | One row per | Answers | Feeds |
|---|---|---|---|
| **T3** `T3_nbs_hazard_farming` | NbS × hazard × farming system | Does this NbS reduce the losses a hazard causes to rural livelihoods? (`risk_role = livelihood_mitigation`) How exposed is the NbS investment itself to the hazard? (`risk_role = asset_threat`) | M2 climate risk, M2b project risk, Opportunity Space panel |
| **T6** `T6_nbs_scorecard` | NbS × T5 priority (poverty, food insecurity, biodiversity, carbon, erosion, water, gender, hazards) | How strongly does this NbS improve this priority? | NbS scorecard and NbS Comparison, optional hotspot filter |
| **T6E** `T6E_economic_profile` | NbS × cost indicator | Indicative cost and return, scoping grade only, not a cost-benefit analysis | Economic profile panel |

Files: `schema/recipes/<nbs_id>/<table>.csv` (source of truth) and `.json` (generated, what code reads). Column definitions: [schema/spec.md](../schema/spec.md).

**A flat copy of all three tables for every NbS** is at [`docs/effect_rows_flat.csv`](../docs/effect_rows_flat.csv). It is rebuilt on every schema generation and has the nested `applicability` field split into plain columns, so it can be filtered in a spreadsheet. Use it to browse; code should read the recipe JSON.

### How rows are layered within one cell

A cell (for example *agroforestry × drought × agro-pastoral*) can hold several rows:

- **Roll-up row** (`suitability_family_id` blank): agroforestry as a whole. This is the default.
- **Family rows** (`suitability_family_id` set): one per sub-practice family, such as silvopastoral or planted silvoarable. Use these when the TTL has chosen a family.
- **Global row** (`scope_type` blank): reconciled for low and lower-middle income countries, the World Bank investment target.
- **Scope rows** (`scope_type` + `scope_id`): emitted only where at least two independent sources in that context disagree with the global row, or where the global evidence does not transfer. Scope types in use today: `income_group`, `farming_system` (T6 only; in T3 the farming system is part of the cell) and `aez`.
- **T3 farming system**: `farming_system = all` is the row for any system. A named system (`agro_pastoral`, `cropping_rainfed`, …) refines it.

Example record IDs for one T3 cell:

```
agroforestry__drought__agro_pastoral                        roll-up, global, agro-pastoral
agroforestry__silvopastoral__drought__agro_pastoral         silvopastoral family
agroforestry__drought__all                                  roll-up, any farming system
agroforestry__drought__all__income_group-high               evidence from high-income countries
```

## 2. How evidence becomes a row

This is done when the tables are generated (`recipe/cell_synthesis.py`). Developers consume the result and do not recompute it. Full method: [T3_T6_generation_method.md](T3_T6_generation_method.md); latest rule changes: [scoring decisions, 22 Oct 2026](decisions/2026-10-22_t3t6_scoring_and_qa.md).

1. **Pool.** Every evidence unit (a verbatim, page-located claim from a paper) whose outcome maps to the cell is pooled. The mapping is the target crosswalk register; indirect proxies count at 0.7.
2. **Weight.** Each unit is weighted by source quality tier × study design (meta-analysis 1.5, review 1.25, trial 1.2, practitioner rating 0.5) × share of a bundled intervention × how far its context is from the target (same 1.0, adjacent 0.7, far 0.3, so high-income evidence counts 0.3 toward a low-income row). One original study gets one vote however many papers repeat it.
3. **Direction.** A weighted vote on benefit vs harm. If the minority holds at least a third of the weight, the row is `conflicting_evidence` rather than a false average.
4. **Strength.** The median strength among the units on the winning side that state a size. Caps apply: modelled-only evidence, sparse size data or proxy-only evidence cap the class at moderate. In T3, measured failures under the same hazard scale the class down.
5. **Confidence.** Two axes, following IPCC: amount of evidence (`evidence_level`: limited · medium · robust) × agreement (`agreement_level`: low · medium · high). The two combine through `schema/lookups/ipcc_confidence_matrix.csv` into `confidence` / `effect_confidence`: very_low · low · medium · high · very_high.
6. **Family vote.** The roll-up row's class is a vote of its family rows, each weighted by √(number of sources).
7. **Applicability.** Every row records where its evidence came from (countries, income groups, farming systems, climate zones) and a `transfer_class`: `in_context` (more than half the evidence weight is from the target context), `adjacent`, `out_of_context` (more than half from far contexts) or `mixed`.

**Strength and confidence are separate.** "Slight benefit, very high confidence" is a well-established small effect. "Strong benefit, low confidence" is a promising but thin finding. Show both, never one number.

### Class vocabulary

| Field | Values (best to worst) |
|---|---|
| T6 `effect_direction` | strong_positive · moderate_positive · slight_positive · no_relationship · slight_negative · moderate_negative · strong_negative · conflicting_evidence |
| T3 `mitigation_potential` (livelihood rows) | very_high · high · moderate · low · none · negative · very_negative · conflicting_evidence |
| T3 `asset_sensitivity` (asset rows) | very_high · high · moderate · low · none: how badly the hazard damages the NbS itself |
| Blank class | Too little evidence. `justification.data_deficient = true` explains why. Show "?" not zero. |

Display symbols and labels for each class: `schema/lookups/scorecard_chip_scale.csv`.

## 3. How rows become what the TTL sees

| Output | Rule | Status |
|---|---|---|
| **Scorecard chip** (Opportunity Space panels, NbS Comparison) | One chip per problem row in `schema/lookups/scorecard_rows.csv`. A chip can pool several T6 rows (for example, water-table depletion pools water stress, catchment water yield and water quality). Chip class = median of the pooled rows at medium confidence or better, shown as ± when at least a third dissent. Symbol matches the class (+ slight · ++ moderate · +++ strong; − for harm). Confidence is shown beside the symbol, not inside it. The chip is outlined as a caution where any study measured harm. | Implemented: `runtime/scorecard.py` → `docs/scorecard.json`. Currently uses roll-up global rows only. |
| **Hotspot filter** (M4) | The priorities an NbS is evidenced to improve can optionally filter which need layers the hotspot map shows. T6 never changes the hotspot weights. | Specified (M4 module) |
| **Climate risk to livelihoods** (M2) | T3 livelihood rows decide which hazards count for the chosen NbS. | Hazard selection specified. **Open: the hazard × exposure formula is Brayden's decision** ([M2 module](modules/M2_climate_risk.md) §6.5). |
| **Risk to the investment** (M2b Stream A) | T3 asset rows give how sensitive the NbS is to each hazard. Hazard weights (`asset_risk_weight`) are emitted only when all seven hazards have a row; otherwise M2b uses equal weights and says so. | Specified ([M2b module](modules/M2b_project_risk.md)) |
| **Economic profile** | Show T6E `economic_value_range` (low, high, unit, source note) as is. Never convert currencies or price years, and never compute new ratios. | Specified (M5 module) |
| **Statement text** | `justification.statement` is a generated one-sentence reading of the row and is safe to show to TTLs. Mechanism and conditions are in `justification.mechanism` / `conditionality`. | Generated |

## 4. Picking the rows for a study area

Use `nbs_ruralscan.runtime.effect_rows`:

```python
from nbs_ruralscan.runtime import effect_rows as E

t3 = E.load_rows("schema", "T3")
aoi = {"income_group": "low", "farming_system": "agro_pastoral", "admin_country": "NER"}
r = E.resolve(t3, "agroforestry", aoi, hazard_type="drought", risk_role="livelihood_mitigation")
r.status          # "ok" | "no_applicable_evidence" | "no_row"
r.row             # the chosen row
r.scope_matched   # "global" or e.g. "income_group-high"
r.transfer_class  # against this AOI
```

For T6 or T6E pass `variable_id="rural_poverty"`. Pass `family="agroforestry__silvopastoral"` when the TTL has chosen a family.

The rules it applies (method §2.3, §5.5):

1. **Cell:** NbS × hazard (or priority) × family. For T3, a row for the study area's own farming system wins over `all`.
2. **Most specific scope wins:** admin region > country > hydrobasin > farming system > climate zone (`aez`) > income group > global. Income groups match by band: `low` and `lower_middle` both match `lic_lmic`.
3. **Does the evidence apply here?** A scope row keeps its own `transfer_class`. A global row keeps its stored class for low- and lower-middle-income areas. For other areas the class is re-derived from the row's income-group source counts (`transfer_basis = source_counts`). This is an approximation, because the per-unit weights are not stored on the row.
4. **Gap, not a class:** if a global row is `out_of_context` for the area, the status is `no_applicable_evidence`. Show the gap ("evidence from high-income countries only, n = 2") with the row greyed, never the class as if it applied.

**Several farming systems in one area:** resolve once per farming system and show per system, or summarise and say so. Do not average classes across systems silently.

### Filtering in a spreadsheet

In `docs/effect_rows_flat.csv`:

| To get | Filter |
|---|---|
| One NbS | `nbs_id` |
| Whole-NbS rows only | `suitability_family_id` blank |
| One family | `suitability_family_id` |
| Rows for a farming system | T3: `farming_system` = system or `all`. T6: `scope_type = farming_system`, `scope_id` = system, else the blank-scope row |
| Evidence from low- and lower-middle-income contexts | `transfer_class = in_context` on global rows |
| Evidence from a country | `countries` contains the ISO3 code |
| Usable today | `confidence` ≥ medium and `class` not blank |

## 5. What is not there yet

- **No country- or region-specific rows yet.** Scope rows are income group, farming system and (a few) climate zone. The resolver will pick country or region rows when they exist, without code changes.
- **Climate zone is mostly unknown** in the evidence records, so `aez` scope rows are rare.
- **The scorecard ignores family and scope rows** today. Wiring `resolve` into the scorecard is the next step once the tool knows the study area.
- **Thin cells:** many rows are low or very low confidence because evidence is sparse, not because the NbS has no effect. Display them with their confidence; do not hide them.
- **Values move.** Each extraction round adds evidence and regenerates every row. Classes can change between builds.

## 6. Where to look

| Need | File |
|---|---|
| Generation method (full) | [T3_T6_generation_method.md](T3_T6_generation_method.md) |
| Column definitions | [schema/spec.md](../schema/spec.md) |
| Scorecard rows, symbols, badges | `schema/lookups/scorecard_rows.csv`, `scorecard_chip_scale.csv`, `scorecard_confidence_badge.csv` |
| Confidence matrix | `schema/lookups/ipcc_confidence_matrix.csv` |
| Row selection code | `src/nbs_ruralscan/runtime/effect_rows.py` |
| Scorecard code | `src/nbs_ruralscan/runtime/scorecard.py` |
| Suitability (T4) handover | [T4_developer_contract.md](T4_developer_contract.md) |
| Live scorecard and pipeline progress | [scorecard](https://ciat.github.io/nbs_ruralscan/scorecard.html) · [progress](https://ciat.github.io/nbs_ruralscan/progress.html) |
