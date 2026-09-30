# Synthesis Contract — T3 / T6 cell generation (ruleset v1.6.0)

What `recipe/cell_synthesis.py` (PR3) must implement, and what the prose writer may and may not do. Normative
source: `methodology/T3_T6_generation_method.md` §2, §5, §7, §8. Schema: `schema/spec.md` v0.4.0. This file is
the acceptance spec for the engine; where it and the method doc differ, the method doc wins and this file is fixed.

---

## 1. Inputs

- Live EV units (`review_state != dropped`) with `use_role ∈ {nbs_effect, asset_vulnerability}`.
- SRC (tier, `source_category`, `study_income_group`, `venue_type`), FAM, T7, T5 (`priority` rows +
  `directionality_of_concern`), `XW`, `BANDS`, `schema/lookups/ipcc_confidence_matrix.csv`,
  `schema/lookups/wb_income_groups.csv`.
- Reused from `recipe/synthesis.py`: `TIER_W`, `BASIS_W`, `GREY_DISCOUNT` (+ new key
  `asset_vulnerability: 0.6`), `_weight`, `_dedupe_lineage`, `_weighted_median`, `SynthesisReport`.
  `synthesise_t4_row` and `_EMITTABLE_ROLES` are **not** modified.

## 2. Cells

| Table | Cell | Role |
|---|---|---|
| T3 mitigation | `nbs_id × hazard_type × farming_system` (`all` = universal) | `nbs_effect` via `XW.target_table = T3` |
| T3 asset threat | `nbs_id × hazard_type` (`farming_system = all`) | `asset_vulnerability` |
| T6 effect | `nbs_id × T5.variable_id` | `nbs_effect` via `XW.target_table = T6` |
| T6 economic | `nbs_id × economic_indicator_type` | `nbs_effect` with an economic `target_key` |

A unit reaches a cell through **every** matching XW row (many-to-many). A unit whose `variable` has no XW row is
reported under `unmapped` and feeds nothing.

## 3. Per-cell algorithm (deterministic; same register → byte-identical output)

1. **Gather** units for the cell; apply `claim_scope` routing (species out; crop in only where the family allows).
2. **Lineage dedupe** (`_dedupe_lineage`) → independent sources.
3. **Polarity** — apply `XW.polarity`; rank = sign × {`slight` 1, `moderate` 2, `strong` 3}; `unspecified` → sign
   only; `direction = none` → 0.
4. **Weight** — `w = TIER_W[tier] × BASIS_W[claim_basis] × grey_discount × TRANSFER_W[d] × XW.weight_factor × (0.5 if significance = ns)`.
   - `d` = max context distance over populated dimensions (method §5.2): income band 0/1/2 · AEZ same / same
     `climate_zone` / other · farming system same / adjacent pair / other. `TRANSFER_W = {0: 1.0, 1: 0.7, 2: 0.3}`.
   - Target for the **global** row = `{income_band: lic_lmic}`; for a scope row = its scope.
5. **Reconcile** — modal sign = sign with the larger weight share (zeros split). Cell rank = `_weighted_median`
   over ranks of modal-sign units (+ zeros). Opposite-sign units are **not** averaged in.
   Sign agreement `A` = modal-sign weight share.
6. **Evidence level** — `limited` (≤ 2 independent, or all `cited_secondary`/`expert_assertion`/`practitioner_rating`) ·
   `medium` (3–4) · `robust` (≥ 5 with ≥ 2 `primary_measured`/`table`, or a high-tier meta-analysis).
7. **Agreement level** — `high` A ≥ 0.8 · `medium` 0.6 ≤ A < 0.8 · `low` A < 0.6.
8. **Confidence** — lookup `ipcc_confidence_matrix.csv`.
9. **Enum mapping** — T6 `effect_direction`: ±1/±2/±3 → slight/moderate/strong, 0 → `no_relationship`
   (only when modal sign is zero). T3 `mitigation_potential`: +1 low · +2 moderate · +3 high · 0 none ·
   −1/−2 negative · −3 very_negative; `very_high` iff rank = 3 **and** confidence ≥ `high`.
   T3 `asset_sensitivity`: 0 none · 1 low · 2 moderate · 3 high; `very_high` same gate.
10. **Scope rows** — for each context dimension, group units; re-run 4–9 per group against the group's scope; emit
    when ≥ 2 independent sources **and** (rank differs from global by ≥ 1 **or** global `transfer_class` for that
    scope = `out_of_context`). `context_dependent = true` on the global row iff ≥ 2 scope rows differ in sign or
    rank after a global `agreement_level ∈ {low, medium}`.
11. **Envelope** — `applicability` on every row: counts of independent sources by income group / AEZ / farming
    system, `countries`, `n_sources_in_scope`, `weight_share_in_context`, `transfer_class`
    (`in_context` ≥ 0.5 weight at d=0 · `adjacent` ≥ 0.5 at d≤1 · `out_of_context` ≥ 0.5 at d=2 · else `mixed`).
12. **Family rows + roll-up** — family row when ≥ 2 independent sources for that family; NbS row always, pooled
    over all units; `family_spread = true` when family ranks differ by ≥ 2.
13. **`magnitude_summary`** (T6) — only when ≥ 2 independent sources in the row's scope share `metric` and a
    VONT-convertible `unit`: `{metric, unit, median (weighted), low, high (observed), n, income_groups}`.
14. **`economic_value_range`** — only when ≥ 2 independent sources · same enum unit or convertible · same income
    band (`lic_lmic` pooled; UMIC, HIC never pooled) · same scope row. **HIC units excluded outright** from
    LIC/LMIC and global rows. `low`/`high` = observed extremes; `source_note` lists ISO3 + currency year per source.
    Every failing unit → `report.excluded_economics` with the failed gate.
15. **`asset_risk_weight`** — `rank_h / Σ rank` over the NbS's hazards, only when all 7 hazards have an
    `asset_threat` row; else blank + `report.weights_incomplete[nbs_id]`.
16. **Prose** (§5 below) → `mitigation_mechanism` / `effect_mechanism`, `caveats` / `conditionality`,
    `justification` traceable account.
17. **Row ids** — `<nbs>[__<family>]__<cell>[__<scope_type>-<scope_id>]`.

## 4. Report

`SynthesisReport` + `unmapped: list[(variable, n_units)]`, `excluded_economics: list[(evidence_id, gate)]`,
`scope_rows_emitted: list[record_id]`, `weights_incomplete: list[nbs_id]`, `dropped` (scope/role/claim_scope),
`collapsed` (lineage echoes), `notes`.

## 5. Prose writer — the only AI step

**Input:** the row's *used* units (quotes, `outcome_raw`, `relationship`, `context`) + the engine's outputs
(rank, levels, confidence, envelope, magnitude/economic summaries, proxies).

**May:** quote or closely paraphrase those quotes; state mechanisms the quotes state; name proxies and grey sources;
describe both directions when `agreement_level = low`; describe where the evidence comes from using the envelope.

**May not:** introduce a number, source, direction, mechanism or context absent from the inputs; compose or alter a
level or class (the engine inserts them into `statement` via template); soften an `out_of_context` envelope.

**Output fields:** `statement` (calibrated language: "<NbS> <raises/lowers/has no effect on> <outcome> in <envelope>
(<evidence_level> evidence, <agreement_level> agreement → <confidence> confidence)"), `evidence_summary`,
`agreement_note`, `mechanism`, `conditionality`/`caveats`, each sentence tagged with the `evidence_ids` it rests on.
`key_evidence_ids` (≤ 5 by weight) and `source_mix` are engine-filled.

**Check:** `check_account.py` — every number in the account appears in a cited unit's quote or `magnitude*`; every
cited `evidence_id` is in `evidence_ids`; no `evidence_id` outside the row's used set.

## 6. Fixtures PR3 must ship

1. **Sweden→Sahel**: one HIC/boreal unit (effect strong, cost 4 000 usd/ha) + zero LMIC units → global row
   `transfer_class = out_of_context`, no `economic_value_range`, runtime resolve for a Sahel AOI returns
   `no_applicable_evidence`. Add two LIC semi-arid units → global row `mixed`, `aez = semi_arid` scope row emitted,
   HIC cost still excluded, LMIC cost range emitted only if the two LIC units share a unit.
2. **False-zero guard**: two `strong_positive` + two `strong_negative` equal-weight units → not `no_relationship`;
   `agreement_level = low`; if they split by AEZ → two scope rows + `context_dependent = true`.
3. **ns handling**: one `sig` moderate positive + one `ns` positive → direction positive, `ns` unit at ×0.5, no
   strength contribution from it.
4. **Lineage**: three `cited_secondary` echoes of one primary → `evidence_level = limited`, one independent source.
5. **Asset weights**: 6 of 7 hazards rated → `asset_risk_weight` blank, `weights_incomplete`; 7 of 7 → weights sum to 1.
6. **Determinism**: two runs on the same register → identical JSON.

## 7. Out of scope for the engine

Dashboard rendering; VONT triage; SRC back-fill (PR4 script); WOCAT acquisition adapter (own PR, PAUSE); any
change to `synthesise_t4_row`.
