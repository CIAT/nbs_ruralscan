# T3/T6 scoring oddities — technical diagnosis (2026-11-10)

Reviewer-reported rating moves that look backwards. Diagnosed against the engine at
`e2de3081` (`src/nbs_ruralscan/recipe/cell_synthesis.py`, `t3t6_build.py`); no engine code
changed. Decision sheet for Pete: `docs/decisions/scoring_round5_2026-11-10.html`
(codes `scoring_r5_1` … `scoring_r5_3`; rows in `methodology/decisions/open_decisions.csv`).

## How to reproduce

All runs are in-memory dry runs (nothing written; synthesis reads the EV JSON):

```python
import importlib.util
spec = importlib.util.spec_from_file_location("s", "scripts/synthesise-t3t6.py")
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
inp = s.load_inputs(nbs, [])
inp["units"] = [u for u in inp["units"] if u.evidence_id not in DROP]
out = s.synthesise(nbs, inp)          # out["T3"], out["T6"] rows; compare by record_id
```

Voter dumps below come from wrapping `cs.synthesise_cell` / `cs._reconcile_group` / the
`apply_*_cap` functions to print `(sign, magnitude, weight)` per contribution.
Option impacts come from monkeypatching the candidate rule and diffing all 683 T3+T6 rows
over the six NbS (riparian, agroforestry, forest restoration, mangrove, wetland, WH).

## 1. Dropping a null finding lowers a rating

### 1a. `ev_rural_poverty_cmscr20_9` (World Bank 2020 Colombia ICR, silvopastoral poverty)

| | before | after drop |
|---|---|---|
| T6 `agroforestry__silvopastoral__rural_poverty` | strong_positive / very_high | moderate_positive / very_high |

Cell: 10 units, 6 sources. Pooled rank = 3 both times (strength voters montagnini15_1,
saucedo23_1, cmscr20_6, all `strong`). The change is in **`apply_proxy_cap`
(L1509–1550)**:

* L1524 `direct = [... proximity == "direct"]`. The only direct unit is cmscr20_9
  (`rural_poverty → rural_poverty`, XW `direct`). Every other unit is `household_income` or
  `economic_return`, both XW `proxy` (0.7).
* L1527 — direct-first branch needs a direct unit of the modal sign **with a magnitude**;
  cmscr20_9 is `direction=none`, so this branch is skipped.
* L1540–1546 — the cap fires only if **all** contributions are non-direct. The null direct
  unit makes that false, so the proxy-only cap (|rank| ≤ 2) is skipped.

Net: a direct null that sets neither direction nor strength **unlocks** a strong class built
entirely from proxies. Drop it → all-proxy → capped at moderate. (Weight shares also move:
cmscr20_6 goes 0.059 → 0.118 because `dedupe_for_cells` L1496 splits the source weight over
its own units; irrelevant to the class here.)

### 1b. `ev_drought_hazard_faosen24_17` (FAO 2024 Senegal, windbreaks under drought)

| | before | after drop |
|---|---|---|
| T6 `agroforestry__linear_boundary__drought_hazard` | slight_positive / low | data deficient / very_low |
| T3 `agroforestry__linear_boundary__drought__all` (+ `cropping_rainfed`) | low / low | data deficient |
| T6 `agroforestry__drought_hazard` (NbS roll-up) | slight_positive / medium | conflicting_evidence / high |
| T6 `agroforestry__drought_hazard__farming_system-cropping_rainfed` | slight_positive | not emitted |
| T3 `agroforestry__drought__cropping_rainfed__income_group-lic_lmic` | not emitted | conflicting_evidence |

Family cell = 2 units: `ev_drought_hazard_moran18_1` (Morantes-Toloza 2018 review, live
fences feed livestock in drought; `cited_secondary`, positive, no strength) +
faosen24_17 (`direction=none`; the quote actually says the literature has *no consensus* —
some studies find yield gains in dry years, others harm).

* **`meets_evidence_floor` (L2184–2198)**: L2188 `if n_sources >= 2: return True` counts
  sources regardless of sign. The null supplies the second source, so the cell may state a
  class; direction comes only from moran18 (`_reconcile_rank` L692–740: pos>0, neg=0 →
  modal +1; no magnitude → rank 1). Drop it → 1 source, not measured → data deficient.
* **`_family_vote` (L3117–3200)**: with linear_boundary classed, positive weight
  √2+√3+√2 = 4.56 vs negative 2.0 → dissent 0.305 < 1/3 → slight_positive. Without it,
  3.146 vs 2.0 → dissent 0.389 ≥ 1/3 → conflicting_evidence. (The pooled roll-up label is
  `conflicting_evidence` in both runs; the family vote overrides it.)

Other faosen24 drops checked: `_10`, `_11`, `_14`, `soil_water_retention_3` → no change.
`microclimate_buffering_16` (a *negative* unit) lowers two T6 heat-stress breakdown
confidences (very_high → high) and removes the `tree_perennial` breakdown line — scope
emission side effect, not pursued.

### Common mechanism

Two gates treat "a unit exists" as evidence for the class: the proxy-only cap (any direct
unit lifts it) and the two-source evidence floor (any second source licenses a class).
Neither checks that the unit agrees with the class it licenses. Nulls do not vote on
strength (`_reconcile_rank` L731–733) and only lower agreement, so a null can raise a
rating via a gate but never lower it via the median — hence "remove a null, rating falls".

### Option impact (all six NbS, 683 rows)

* **B — null/opposite units never open a gate** (floor counts only non-zero-sign units unless
  the cell is all-null; proxy cap lifted only by a direct unit of the modal sign): **14 rows
  change.** silvopastoral poverty strong → moderate; linear_boundary drought T3×2 + T6 →
  data deficient; AF drought roll-up slight_positive → conflicting; FR plantation fire
  (T3) negative → data deficient; FR protection_cbfm water quality moderate → data deficient;
  5 scope rows → data deficient (FR flood lic_lmic T3+T6, WH production_gap pastoral, wetland
  production_gap lic_lmic, wetland water_stress mixed); 2 new scope rows (AF wind_cyclone
  upper_middle T3 low; WH soil_erosion pastoral conflicting).
* **C — proxy-cap fix only**: 3 rows (silvopastoral poverty strong → moderate + the two new
  scope rows).

## 2. One unreplicated unit (Akber 2018) caps a whole row

`ev_flood_hazard_akber18_7`: post-Sidr recall survey, waterlogging 5 days (mangrove-sheltered
site) vs 8 days (unsheltered); one site per arm → `context.unreplicated=true`;
`contrast` class = strong, capped to moderate by **#57 in `unit_rank` L599–602**
(`mag = min(mag, STRENGTH_RANK["moderate"])`). Weight 0.600 — the **largest in the cell**
(Narayan 2016 meta-analysis line = 0.45 because its source weight is split over 2 units by
`dedupe_for_cells` L1496).

| | with Akber | without |
|---|---|---|
| T3 `mangrove_restoration__tidal_coastal__flood__all` | moderate | very_high |
| T3 `…__flood__cropping_rainfed` | moderate | very_high |
| T6 `mangrove_restoration__tidal_coastal__flood_hazard` | moderate_positive | strong_positive |

Every unit in both cells has sign +1 (agreement 0.95–1.0).

**How many units vote on strength (T6 family cell):** 25 units from 11 sources; 13 state a
strength in the modal direction. Pooled median = 3. Then **`apply_proxy_cap` direct-first
(L1527–1538)** re-reconciles on direct (`flood_hazard`) units only: **9 voters** —
strong ×5 (Narayan 2016, Gijsman 2021, McIvor 2012 ×3; weight 0.831), moderate ×3 (Akber
capped 0.600, Menéndez 2020 ×2 at 0.14; 0.880), slight ×1 (Menéndez 0.14). Total 1.851,
half 0.926; cumulative at moderate = 1.020 → **rank 2**. Without Akber: half 0.626,
cumulative at moderate 0.420 → rank 3. Akber = 32 % of the direct strength weight.
T3 `flood__all` cell: 22 units, 11 strength voters (9 direct + 2 erosion components); same
arithmetic, pooled median already 2 with Akber.

**Answer:** yes — the #57 cap is applied to the unit's magnitude before the weighted median
(L599–602), with weight untouched, so a capped unit casts a full-weight vote *for* moderate
and can pull a row below what every uncapped measured unit says. #57 was written as "this
unit alone cannot claim more than moderate"; in a pool it acts as "this unit argues for
moderate".

Option impact: **B (capped unit abstains from the strength vote when others state a
size; cap applies only if it is the sole sizer)** and **C (half weight)** both change only
these 3 rows today. Register has 30 live `unreplicated=true` units (Roose 2017 ×19 in WH,
Akber 2018 ×7, Rahn 2014 / Fiener 2005 / Botoni 2010 / Caramori 1996 ×1 each); only Akber's flood unit currently sits in a pool
where it is decisive.

## 3. Within-source subgroups vote alongside the pooled figure (Nguyen 2026)

`nguyen_2026` (global silvopastoral biodiversity meta-analysis) has 12 units in the
silvopastoral `biodiversity_priority` cell: pooled lnRR 0.25 (_1), native-tree subset (_2),
planted-tree subset (_3), 6 subsets vs native forest (_4,_5,_6,_7,_9,_11 — `comparator =
reference_forest`, held out by `partition_voters` L2256–2260), invertebrates native vs
pasture (_8, lnRR 0.43 → strong), invertebrate abundance (_10, 0.47 → strong), abstract
restatement of the pooled +28.4 % (_12).

| drop | AF silvopastoral biodiversity | AF biodiversity roll-up |
|---|---|---|
| none | strong_positive | strong_positive |
| `_8` | moderate_positive | moderate_positive |
| `_8,_10` | moderate_positive | moderate_positive |

Voters (silvopastoral cell): moderate 4 × 0.087 (Nguyen _1,_2,_3,_12) = 0.348; strong =
Nguyen _8 0.087 + _10 0.044 + Giraldo 2010 0.21 + Montagnini 2015 2 × 0.05 = 0.441 →
median strong (knife-edge). Without _8 the Nguyen lines each rise to 0.095 → moderate 0.38
vs strong 0.358 → moderate. Roll-up follows via `_family_vote` (silvopastoral = 6 sources,
largest vote).

**Is it double counting?** Not of *weight*: `dedupe_for_cells` L1460–1501 splits one source
weight equally across that source's own units (L1496) and `_apply_shares` L2492 applies it, so
Nguyen never counts as more than one study. But the **composition** of that one study's vote
is set by how many lines the extractor took: the pooled figure and its own partitions
(native ⊂ pooled, invertebrates ⊂ native) and an abstract restatement of the pooled figure
all enter the median as separate pairs (`_reconcile_rank` L729–736). Here 4 lines restate
the moderate pooled result and 2 sub-subgroup lines say strong; the study's middle is moderate,
but its strong lines combine with other studies' strong lines to tip the cell.

**Side finding (bug candidate, no card):** shares are assigned at L2492 *before*
`partition_voters` (L2504) removes held-out units, so Nguyen's 6 reference-forest lines
take 6/12 of its weight and then do not vote — the study's voting weight is half a
study. Same pattern anywhere a source mixes held-out and voting units.

Option impact: **B (per-source weighted median first; even split → midpoint; then
cross-source median at the source's summed voting weight)**: **12 rows change** — strong →
moderate ×7 (AF biodiversity roll-up, AF silvopastoral biodiversity, AF silvopastoral
soil_erosion, FR protection_cbfm rural_poverty, mangrove tidal_coastal soil_erosion, wetland
biodiversity roll-up, wetland restoration_rewetting biodiversity); moderate → low ×1
(wetland flood cropping_rainfed T3); slight → moderate ×2 (FR biodiversity mixed-income
scope; WH spate production_gap); 2 scope rows no longer emitted (AF production_gap lic_lmic,
FR carbon mixed). With the engine's current lower-median tie rule instead of midpoint, 9 rows
change and two drop two steps (strong → slight: AF silvopastoral soil_erosion, mangrove
soil_erosion) because cmscr20 has one strong + one slight line — hence the midpoint rule in B.
**C (pooled/headline line only; subgroups → range + conditionality)** needs a new
extraction tag and a re-check of multi-line sources; impact not computable now.

## 4. Scope (breakdown) rows appear only when they differ — confirmed

`synthesise_cell` L2703–2800: a scope row is built per AEZ / income band (+ farming system in
T6) with ≥ 2 sources (`min_scope_sources`), and **emitted only if** (L2791–2795)
`|scope rank − global rank| ≥ 1` **or** the global row's transfer class for that scope is
`out_of_context` **or** the global agreement level is `low`.

Documented: `methodology/T3_T6_generation_method.md` §2 "Emission rule" (L97–99) states the
first two triggers. **Not documented:** the third trigger (global agreement `low` → every
qualifying scope row is emitted). Also undocumented: family rows never get scope rows
(`emit_scope_rows=False`, L3026), and the comparison uses the **pooled** rank `g["rank"]`,
computed before `_family_vote` (L3063) can reset the roll-up label — 21 of 139 roll-up rows
across the six NbS currently have a published class set by the family vote, so their scope
rows were filtered against a class the reader never sees. Nothing on the scorecard or
review pages tells a reader that an absent breakdown means "same as overall" rather than
"no evidence". Recommended (no decision needed): add the third trigger and the
family-row/pooled-rank notes to §2, and a one-line legend on the scorecard; consider
comparing scope rows against the post-vote class.
