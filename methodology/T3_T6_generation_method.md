# T3 / T6 Generation Method — cell-level synthesis of NbS effects from pooled evidence

**Status:** v0.1 draft for team ratification · 2026-09-29 · **no build before sign-off** (green-light rule)
**Owners:** Pete (framework, engine) · Namita (T6 / M5 consumer, XW ratification for T6) · Brayden (T3 / M2b Stream A consumer, XW ratification for T3) · MFL team (agroforestry content at the volume test)
**Produces:** rows of **T3 — NbS × Hazard × Farming System** and **T6 — NbS Scorecard** (see [`../schema/spec.md`](../schema/spec.md) §T3, §T5, §T6)
**Replaces:** the per-paper T3/T6 row extraction deferred on 2026-09-17 (ruleset v1.5.0, [`../schema/registers/_deferred/`](../schema/registers/_deferred/README.md))
**Scope:** scoping-grade effect direction, strength class and calibrated confidence per NbS, bounded by where the evidence comes from. Not CBA, not ecosystem-service modelling, not site feasibility.

---

## 0. Why this method exists

The first T3/T6 attempt extracted **rows** from **papers**: each paper was asked to yield a finished T3 or T6
record (a mitigation class, an effect direction, a cost range). It failed, and the 264 archived evidence units
show why. The quotes were real and page-verified (the verbatim guardrail held), but the *shape* around them was
unusable:

- numbers with incompatible denominators (Hedges *g*, NPV per acre, B:C ratios, `Mt CO2e/yr`, WB PAD budget lines
  with no unit at all) that no engine could pool;
- context recorded under ~15 different key spellings (`country`, `study_region`, `location`, `countries`…) so
  nothing could be grouped by where it applied;
- outcome names (`erosion_hazard`, `household_income`) with no mapping to what the consumers key on (T3
  `hazard_type`, T5 `variable_id`);
- one paper = one row, so a Swedish boreal cost figure and a Sahel parkland yield claim sat as equals;
- and the synthesis engine never read any of it (`_EMITTABLE_ROLES` was T4-only).

This method keeps what worked (verbatim, page-stamped **evidence units** through the deterministic pipeline)
and changes the unit of output:

> **Generate per table CELL, not per paper.** Pool every evidence unit that hits a cell
> (T3: NbS × hazard × farming system · T6: NbS × T5 priority variable), reconcile them deterministically
> with the same tier / claim-basis / grey-literature weighting the T4 engine already uses, and emit **one
> synthesised row per cell per applicability scope** with `evidence_ids` provenance and IPCC-calibrated
> confidence.

**Tenets (in addition to the T4 method's six):**

1. **Ordinal first.** The synthesised value is a direction + strength class + calibrated confidence. Numbers appear only under the gates in §7.6–§7.7.
2. **Context bounds applicability.** Every row carries the envelope of contexts its evidence came from, and a `transfer_class` against the WB-investable LMIC target. A row built from HIC-temperate evidence never silently sets a Sahel value.
3. **Role = kind of claim, table = where the crosswalk sends it.** One evidence unit can feed T3 and T6; the routing is a ratified, reviewable table, not an extraction-time relabel.
4. **Reuse the T4 engine.** Weights, lineage dedupe, weighted median, grey discount and the report object are imported, not re-invented. Only the ordinal reconciler, the agreement/evidence axes and the envelope are new.
5. **Confidence is derived, never asserted.** IPCC two-axis matrix (evidence × agreement) computed from the units; the AI writes prose, never a level.

---

## 1. Consumers and their minimum columns

The generated tables exist for two consumers. Their needs define the minimum viable row.

| Consumer | Owner | Reads | Minimum columns |
|---|---|---|---|
| **M2b Stream A** — project disaster-risk screen | Brayden | T3 rows with `risk_role ∈ {asset_threat, both}` | `nbs_id` · `hazard_type` · `risk_role` · `asset_sensitivity` · `asset_risk_weight` · `timescale_of_effect` (vulnerability window) · `confidence` · `applicability` |
| **M2 need layer** | Brayden | T3 rows with `risk_role ∈ {livelihood_mitigation, both}` | `nbs_id` · `hazard_type` · `farming_system` · `mitigation_potential` · `confidence` · `landscape_scale_only` · `applicability` |
| **M5 scorecard + T5 `nbs_response` join** | Namita | T6 rows joined to T5 `priority` rows on `variable_id` × `nbs_id` | `nbs_id` · `variable_id` · `effect_direction` · `confidence` · `evidence_level` · `agreement_level` · `effect_mechanism` · `conditionality` · `context_dependent` · `applicability` · `magnitude_summary` · `economic_value_range` (economic rows) |

T6 effect rows link only to T5 `mcda_role = priority` rows (12 today: `drought_hazard` · `flood_hazard` ·
`heat_stress_hazard` · `soil_erosion_risk` · `carbon_sequestration_potential` · `biodiversity_priority` ·
`water_stress` · `rural_poverty` · `production_gap` · `agricultural_dependency` · `gender_inequity` · `iplc_lands`)
plus the `economic_indicator` rows. Descriptor rows get no T6 row (T5 ratification, v0.3.0).

---

## 2. The unit of synthesis: cells and scope rows

### 2.1 Cell keys

| Table | Cell key | Notes |
|---|---|---|
| T3 | `nbs_id` × `hazard_type` × `farming_system` | `farming_system = all` is the universal row; specific farming systems are separate cells (consumer contract, kept from v0.3.0). Hazard enum unchanged: `drought · flood · heat_stress · fire · wind_cyclone · waterlogging · frost`. |
| T6 effect | `nbs_id` × `variable_id` (T5 priority) | `variable_type = opportunity_space_variable` or `climate_hazard_mitigation` (when `variable_id` is a T5 `climate_hazard` priority). |
| T6 economic | `nbs_id` × `economic_indicator_type` | `variable_type = economic_indicator`. |

### 2.2 Family rows and the NbS roll-up (decision 1)

Evidence arrives per **suitability family** (agroforestry F1 127 · F2 73 · F3 29 · cross 29 · F4 4 archived
units) and effects genuinely differ by family: FMNR vs planted silvoarable differ ~10× on establishment cost and
by years on carbon accrual. Consumers, however, compare **NbS**.

- T3 and T6 gain an optional **`suitability_family_id`**. Blank = the NbS-level row.
- A **family row** is emitted where ≥ 2 independent sources hit the cell for that family.
- The **NbS row is always emitted**, as a pooled synthesis over *all* the NbS's units (not a mean of family
  medians — pooling keeps tier / grey / transfer weighting intact and matches how T4 `cross_family` rows behave).
- The NbS row carries **`family_spread = true`** when family medians differ by ≥ 2 ranks, so M5 can show
  "moderate (varies by sub-practice)" instead of a false single answer. Family drill-down in the wireframe is a
  backlog item, not part of this method.

### 2.3 Scope rows (decision 2)

Context overrides are **rows, not inline objects** (the BIND pattern, not the `T4.context_overrides` pattern),
because a T3/T6 override carries a class, confidence, `evidence_ids`, envelope and prose — far too much for a
nested cell, and it must be QA-able and diffable as a first-class row.

- T3 and T6 gain optional **`scope_type`** + **`scope_id`**. Blank = the global row.
- `scope_type` enum = BIND's (`aez · farming_system · admin_country · admin_region · hydrobasin`) **plus
  `income_group`** (`low · lower_middle · upper_middle · high`, with `lic_lmic` as the pooled LIC+LMIC band).
  For T3, `farming_system` is a cell key, so its scope rows use the remaining types.
- **Emission rule:** a scope row is emitted for a context group when it has ≥ 2 independent sources **and**
  either its reconciled rank differs from the global row's by ≥ 1, or the global row's `transfer_class` for that
  scope is `out_of_context`.
- **Precedence (most-specific-wins, runtime):** `admin_region` > `admin_country` > `hydrobasin` >
  `farming_system` > `aez` > `income_group` > global. Same resolver as BIND, extended with `income_group`.
- `record_id` pattern: `<nbs>[__<family>]__<cell>[__<scope_type>-<scope_id>]`.

---

## 3. The evidence atom: effect claims

Nothing changes about **how** a unit is produced: `build_index → retrieve → EvidenceUnit from page-stamped
passages → validate_units → save_units` over a cached artefact in `.cache/corpus/`, verbatim-guarded. What
changes is the claim **shape** and the fixed **context** keys.

### 3.1 Roles (decision 6)

| `use_role` | Meaning | Routed to |
|---|---|---|
| `nbs_effect` | **NbS → outcome.** The NbS changes an outcome variable (yield, erosion, carbon, income, a hazard's impact). Hazard-mitigation claims are `nbs_effect` claims whose outcome is a hazard. | T3 (`livelihood_mitigation`) and/or T6, via XW (§4) |
| `asset_vulnerability` *(new)* | **Hazard → NbS.** The hazard damages or kills the NbS asset (drought seedling mortality, plantation fire, windthrow, flood scour). | T3 `asset_threat` rows only |
| `climate_risk` | Reserved for genuine T2 hazard-index variable definitions. Unused now. | T2 (hand-authored) |
| `structural_suitability` · `operational_risk` · `dataset` | Unchanged | T4 · M2b-B · T1 |
| `priority_need` | Reserved (T5). Unused. | — |

### 3.2 The effect-claim `relationship` object

```json
{
  "direction": "positive | negative | none",
  "strength_class": "slight | moderate | strong | unspecified",
  "metric": "smd_hedges_g | pct_change | ln_response_ratio | absolute | ordinal_rating | narrative",
  "magnitude": 1.16,
  "magnitude_low": -0.35,
  "magnitude_high": 2.67,
  "unit": "unitless | percent | t_ha_yr | usd_per_ha | ...",
  "significance": "sig | ns | not_reported",
  "n": 12,
  "design": "meta_analysis | rct | quasi_experimental | observational | model | case_study | expert | practitioner_rating",
  "outcome_raw": "maize grain yield under Faidherbia canopy vs open field"
}
```

Rules:

- `direction` is **relative to the outcome variable as named**, not to "good for people". A unit on
  `erosion_hazard` with `direction = negative` means erosion goes *down*. Polarity toward the T5 variable's
  `directionality_of_concern` is applied by the engine, never by the extractor.
- Every number in `magnitude*` **must appear in the quote** (`check_numbers`, unchanged rule).
- `strength_class` is derived from `magnitude` + `metric` via the **BANDS** table (§3.4) when the metric has a
  band; otherwise `unspecified`. A unit with `direction` but no number contributes to direction, never strength.
- `significance = ns` (a CI spanning zero, a reported p > 0.05) is **kept, not dropped**: it counts toward
  direction at ×0.5 weight and never toward strength (§7.2). This is how the archived crop-yield *g* = 1.16,
  CI −0.35 to 2.67 enters honestly.
- `outcome_raw` preserves the paper's own outcome wording (the `raw_name` audit, extended to outcomes).
- `variable` remains the **VONT canonical outcome variable** the paper measured (`erosion_hazard`, not
  `soil_erosion_risk`). The hop to the consumer key is XW's job (§4), so a proxy is never relabelled silently.
- **Hazard-mitigation units** additionally carry `context.hazard_type`, `context.farming_system`,
  `context.landscape_scale_only`, `context.timescale_of_effect` (all enum-policed) — the surviving part of the
  archived T3 contract. **Asset-vulnerability units** carry `context.hazard_type` and the vulnerability window
  in `context.timescale_of_effect` (§9).
- T4 structural units are unchanged. Species/crop routing (`claim_scope` + `taxon`) applies identically:
  a per-species mortality figure is `asset_vulnerability` + `species_specific`, kept but routed out of the
  practice cell.

### 3.3 Fixed context keys

`EV.context` accepts **only** these keys for geographic / systemic context (free-text goes in `note`):

| Key | Vocab | Default source |
|---|---|---|
| `country` | ISO3 list (multi-country studies) | `SRC.study_country` |
| `region` | free text, informational only | `SRC.region` |
| `aez` | T7 `aez` ids | `SRC.aez` |
| `farming_system` | T7 `farming_system` ids | `SRC.farming_system` |
| `income_group` | `low · lower_middle · upper_middle · high` | `SRC.study_income_group`, back-filled deterministically from `country` via the WB classification lookup |
| `climate_zone` | `tropical · dryland · temperate · boreal` (coarse, for AEZ distance when `aez` is blank) | derived from `aez` or `country` |

Per-unit values override SRC defaults for multi-site papers. `check_context.py` (§12) fails a unit with an
unknown key, an out-of-vocab value, or a blank `income_group` where `country` is known.

### 3.4 BANDS — magnitude → strength class (decision 4, machine-readable)

A small register, `schema/registers/BANDS_magnitude_bands.csv`, one row per `metric` × class:

| `metric` | `slight` | `moderate` | `strong` | Basis |
|---|---|---|---|---|
| `smd_hedges_g` | \|g\| < 0.2 | 0.2 – 0.5 | > 0.5 | Cohen conventions |
| `pct_change` | < 10 % | 10 – 30 % | > 30 % | scoping convention; ratify |
| `ln_response_ratio` | < 0.10 | 0.10 – 0.35 | > 0.35 | ≈ 10 % / 40 % |
| `ordinal_rating` | source scale mapped per adapter (e.g. WOCAT 4-level) | | | adapter note |
| `absolute` / `narrative` | no band → `unspecified` | | | |

`check_bands.py` verifies `strength_class` against `magnitude` for every banded unit. The table is the single
place the team argues about bands; the contract cites it rather than restating it.

### 3.5 Single-pass extraction and deferred pointers

The read-once lock stands: a paper is swept **once** for every live role (`structural_suitability` ·
`operational_risk` · `nbs_effect` · `asset_vulnerability`). Until the v1.6.0 contract is live, T4 sweeps
(forest restoration next) emit a **structured deferred-pointer list** per paper — `{source_id, page, claim_kind,
outcome_raw, note}` — so the later effects pass is a targeted lookup, not a re-read. The riparian sweep's prose
pointers in `pipeline/staging/riparian_t4_*_sweep.json` are the informal precedent; the contract makes it a field.
**Tracked home for pointers (2026-10-01):** `pipeline/staging/` is gitignored, so pointer lists, ontology-gap notes,
denominator-less economics and blockers from each extraction report are copied into
`methodology/effect_evidence_followups.md` (per-NbS sections) in the PR that ingests the units. Lit-search
targeting for effect evidence: syntheses (meta-analyses, systematic reviews, EGMs) and project MEL /
impact-assessment grey literature first; primaries only to fill cells the syntheses leave empty.

---

## 4. XW — the target crosswalk (decision 5)

A new register, `schema/registers/XW_target_crosswalk.csv`, one row per (`ev_variable` × `target_table` ×
`target_key`). It is the only place an outcome variable becomes a consumer key.

| Field | Type | Description | Example |
|---|---|---|---|
| `xw_id` | string | Unique id. | `erosion_hazard__T6__soil_erosion_risk` |
| `ev_variable` | FK → VONT | Canonical outcome variable on the unit. | `erosion_hazard` |
| `target_table` | enum `T3 · T6` | | `T6` |
| `target_key` | string | T3 `hazard_type` or T5 `variable_id` or `economic_indicator_type`. | `soil_erosion_risk` |
| `polarity` | enum `same · inverted` | Sign flip between the outcome as measured and the target's `directionality_of_concern`. | `same` |
| `proximity` | enum `direct · proxy · component` | Direct hit, a proxy for the target, or one component of a composite target. | `direct` |
| `weight_factor` | float | Applied in synthesis. `direct` 1.0 · `proxy` 0.7 · `component` 0.7 (defaults). | `1.0` |
| `rationale` | string | Why this mapping; cite the T5 companion doc's proximate-over-distal principle where relevant. | |
| `ratified_by` · `ratified_date` | string · date | Namita for T6 targets, Brayden for T3 targets, Pete tie-break / pilot. | |

Rules:

- **Many-to-many is allowed and expected.** `drought_hazard` → T3 `drought` **and** T6 `drought_hazard`.
- **No XW row without a VONT id.** The 9 orphan archived variables (`economic_cost` · `wind_erosion` ·
  `fuelwood_fodder` · `soil_fertility` · `vegetation_cover_gain` · `carbon_biomass` · `climate_resilience` ·
  `drought` · `buffer_width`) go through ontology triage first (some are aliases: `drought` → `drought_hazard`,
  `wind_erosion` → `erosion_hazard`?).
- **Unmapped is a state, not an error.** A live variable with no XW row is catalogued, feeds no cell, and is
  listed in the run report under `unmapped`. `adoption_rate` and `ecosystem_service` start there.
- Proxies are **named as proxies** in the traceable account ("household income used as a proxy for rural
  poverty, n = 3, ×0.7").
- Seed crosswalk to ratify at PR2: `erosion_hazard → T6 soil_erosion_risk (direct)` · `carbon_sequestration →
  T6 carbon_sequestration_potential (direct)` · `soil_organic_carbon → T6 carbon_sequestration_potential
  (component)` · `biodiversity_outcome → T6 biodiversity_priority (direct)` · `crop_yield → T6 production_gap
  (direct, inverted)` · `household_income · food_security · economic_return → T6 rural_poverty (proxy,
  inverted)` · `drought_hazard → T3 drought + T6 drought_hazard` · `flood_hazard → T3 flood + T6 flood_hazard` ·
  `fire_hazard · wildfire_mitigation → T3 fire` · `windbreak_protection → T3 wind_cyclone` · `project_cost ·
  economic_cost → T6 establishment_cost / cost_per_hectare_restored (needs denominator)`.

---

## 5. Context and applicability — the core design

### 5.1 The problem stated as a test

> A Swedish boreal riparian-buffer establishment cost must never set, or even nudge, a Sahel scorecard value.
> A Kenyan semi-arid parkland yield effect should carry full weight for a Sahelian AOI and reduced weight for a
> humid-tropics one.

The design has three parts: a per-unit **transferability weight** (affects the reconciled value), a per-row
**applicability envelope** (records where the evidence came from), and a runtime **most-specific-wins resolver**
with a **gap flag** (decides whether a row may be shown for an AOI at all). Economics additionally get **hard
exclusions** (§7.7), not weights.

### 5.2 Context distance

Distance between a unit's context `C_u` and a target context `C_t`, per dimension, 0 / 1 / 2:

| Dimension | 0 (same) | 1 (adjacent) | 2 (far) |
|---|---|---|---|
| `income_group` | same band (`low`+`lower_middle` count as one band) | `lic_lmic` ↔ `upper_middle` | anything ↔ `high` |
| `aez` / `climate_zone` | same T7 `aez` | same `climate_zone` (tropical / dryland / temperate / boreal) | different `climate_zone` |
| `farming_system` | same id | `cropping_rainfed` ↔ `mixed_crop_livestock`; `agro_pastoral` ↔ `pastoral_rangeland`; `tree_perennial` ↔ `mixed_crop_livestock` | otherwise |

Unit distance `d = max` over dimensions that are populated on **both** sides; a dimension blank on either side is
ignored. `TRANSFER_W = {0: 1.0, 1: 0.7, 2: 0.3}`. This is the six-axis credibility rubric's transferability
axis made mechanical, replacing the "LMIC tie-break" prose.

**Unknown is not "same" (2026-10-05).** When the target states an income band and the unit states none, the
income dimension scores `1` (adjacent), not `0`: a context-less unit can never read as fully in-context. Found
when 129 context-less units carried a 1.0 in-context weight share.

### 5.3 The generation-time target

Global rows are reconciled against the **WB-investable default target**: `income_group = lic_lmic`, `aez` and
`farming_system` unset. So at generation, transferability reduces to the income dimension: LIC/LMIC 1.0 ·
UMIC 0.7 · HIC 0.3. Scope rows are reconciled against their own scope (`aez = semi_arid` etc.), so a
semi-arid paper carries full weight in the semi-arid scope row and 0.7 in the dryland-adjacent one.
**Non-income scope rows also keep the global income target (2026-10-05):** an AEZ or farming-system scope built
only from HIC evidence is `out_of_context`, not `in_context` within its own scope — otherwise a Costa-Rica-only
`tree_perennial` row would silently set an LMIC value, which the lock forbids.

### 5.4 The `applicability` object (every row, including global)

```json
{
  "income_groups": {"lower_middle": 3, "high": 2},
  "aezs": {"semi_arid": 2, "temperate_europe": 2, "unknown": 1},
  "farming_systems": {"mixed_crop_livestock": 3, "unknown": 2},
  "countries": ["KEN", "ETH", "IND", "SWE", "ITA"],
  "n_sources_in_scope": 5,
  "weight_share_in_context": 0.42,
  "transfer_class": "mixed"
}
```

Counts are **independent sources** after lineage dedupe. `transfer_class` is computed from the share of
contributing weight at each distance against the row's target, where the weight is the unit's
**pre-transfer** weight (tier · claim basis · grey discount · ns · XW proximity — *excluding* `TRANSFER_W`).
Measuring the share on transfer-weighted weights would be circular: the far unit is first down-weighted to
0.3 and then found to be a small share, so one LMIC unit + one HIC unit read as 0.95 "in context"
(caught 2026-10-02). Majorities are **strict**, so an even split is `mixed`:

| `transfer_class` | Rule |
|---|---|
| `in_context` | > 0.5 of pre-transfer weight at `d = 0` |
| `out_of_context` | > 0.5 at `d = 2` |
| `adjacent` | > 0.5 at `d ≤ 1`, not `in_context` |
| `mixed` | none of the above (incl. an exact 50/50 split) |

### 5.5 Runtime resolution and the gap flag

For an AOI, the runtime (or the M5 notebook) takes its T7 contexts, collects the cell's rows whose scope
matches, picks the most specific (§2.3 precedence), and **recomputes `transfer_class` against the AOI**.
If the picked row is the global row and its recomputed class is `out_of_context`, the consumer receives
**`no_applicable_evidence`** with the row attached greyed, and the statement "evidence from high-income
temperate contexts only (n = 2)". It must **not** receive the class as if it applied. M5 shows a gap; M2b
falls back to its equal-weight default and records the substitution in the run config, exactly as BIND does for
`requires_upload`.

### 5.6 The test case, resolved

The Swedish paper's cost figure is `income_group = high`. It fails the economics hard exclusion (§7.7) for the
global LIC/LMIC row and for every Sahel scope row; it can appear only in an `income_group = high` scope row if a
second HIC source agrees. Its *effect* claim (say, sediment retention `strong`) enters the global row at
×0.3 and is recorded in the envelope as HIC / boreal. If it is the only evidence, the global row's
`transfer_class = out_of_context` and a Sahel AOI gets `no_applicable_evidence`. If Kenyan and Ethiopian
evidence also exists, they dominate the median, the envelope shows the mix, and a `semi_arid` scope row is
emitted if their rank differs. This case ships as a **unit-test fixture** in PR3 and is a pilot acceptance
criterion (§14).

---

## 6. Sources — where the evidence comes from

The T4 method's discovery machinery (bounded authority-weighted seed set, five-step funnel, SRCH register,
PRISMA-lite logs) applies unchanged. What differs is **which** sources matter per claim kind:

| Claim kind | Diamond sources | Notes |
|---|---|---|
| `nbs_effect` (T6 outcomes) | Systematic reviews / meta-analyses (Campbell, 3ie, CEE evidence-gap maps — Castle 2021 is the archived exemplar) · WB IEG / ICR outcome sections · MEL/MELIA reports · adoption studies | Grey (WOCAT, CG, FAO, NGO) is positively biased on benefits → `GREY_DISCOUNT["nbs_effect"] = 0.4` (existing, now live) |
| `nbs_effect` (T3 hazard mitigation) | IPCC WGII agriculture / land chapters · FAO CSA sourcebook · hazard-specific reviews (windbreaks, fire in silvopasture, flood attenuation) | Same discount |
| `asset_vulnerability` (T3 asset threat) | **WOCAT technology questionnaire §6.3** (tolerance to extremes, per technology, ordinal) · establishment-mortality / windthrow / fire literature from the single-pass sweep · *optional* internal Alliance/CGIAR rating pass | See §9. **No external expert-elicitation programme** (no bandwidth, decision 7 revised 2026-09-30). |
| `economic_indicator` | WB PADs / ICRs (with denominators) · CrossBoundary archetypes · meta-analyses of adoption economics | Only with a per-unit denominator; raw project totals are not evidence |

**Provenance matters for reuse.** Of the 264 archived units, only **72 (5 sources)** came in via a T3/T6-targeted
search; 87 came via the T4 net (papers found for *suitability*, effects incidental) and 105 via no logged
discovery at all. Only the targeted 72 migrate (§10). Effect evidence must come from **effect-targeted**
discovery; suitability corpora are not a substitute.

---

## 7. The cell synthesis engine

New module `recipe/cell_synthesis.py` with `synthesise_t3_cell(...)` and `synthesise_t6_cell(...)`. It
**imports** `_weight`, `_dedupe_lineage`, `_weighted_median`, `GREY_DISCOUNT`, `TIER_W`, `BASIS_W` and
`SynthesisReport` from `recipe/synthesis.py`. `synthesise_t4_row` and `_EMITTABLE_ROLES` are untouched.

### 7.1 Steps

1. **Gather** — all live units (not `review_state = dropped`) whose `variable` has an XW row to this cell, with
   role `nbs_effect` (or `asset_vulnerability` for asset-threat cells). `claim_scope` routing as T4 (species out;
   crop in only where the family allows).
2. **Lineage dedupe** — `_dedupe_lineage`, unchanged. Ten echoes of one meta-analysis are one source.
3. **Polarity** — apply `XW.polarity` so every unit's sign is in the target's frame; map to an integer rank.
4. **Weight** — `w = TIER_W × BASIS_W × grey_discount × TRANSFER_W(d) × XW.weight_factor × (0.5 if ns)`.
5. **Reconcile** — weighted median over ranks (§7.2); sign agreement; evidence level (§7.3).
6. **Confidence** — IPCC matrix (§7.4).
7. **Scope rows** — group by each context dimension, re-run 4–6 per group, emit per §2.3.
8. **Envelope** — build `applicability` for every emitted row (§5.4).
9. **Numbers** — `magnitude_summary` and `economic_value_range` under their gates (§7.6, §7.7).
10. **Family / roll-up** — family rows and the NbS row with `family_spread` (§2.2).
11. **Prose** — traceable account written by the prose writer from the *used* units' quotes (§8).
12. **Report** — `SynthesisReport` extended with `unmapped`, `excluded_economics`, `scope_rows_emitted`.

### 7.2 Ordinal reconciliation

Unit rank on a shared −3..+3 scale: sign from `direction` (after polarity), magnitude from `strength_class`
(`slight` 1 · `moderate` 2 · `strong` 3 · `unspecified` → contributes to sign only). `direction = none` → 0.

- **Cell rank** = `_weighted_median` over ranks of the **modal-sign** units (plus zeros). Units of the opposite
  sign are *not* averaged in; they lower agreement instead. This is what stops two opposite findings collapsing
  into a false `no_relationship` (decision 3). `no_relationship` is emitted only when the modal sign is zero,
  i.e. the evidence actually reports no effect.
- **Weighted sign agreement** `A` = share of contributing weight on the modal sign (zeros count half toward
  whichever sign is modal, `ns` units already ×0.5).
- **Enum mapping.** T6 `effect_direction`: rank ±1 → `slight_*`, ±2 → `moderate_*`, ±3 → `strong_*`, 0 →
  `no_relationship`. T3 `mitigation_potential`: +1 `low`, +2 `moderate`, +3 `high`, 0 `none`, −1/−2 `negative`,
  −3 `very_negative`; **`very_high` only when rank = 3 and confidence ≥ `high`** (the top class is earned by
  evidence, not by one enthusiastic paper).

### 7.3 Evidence level

From independent sources after dedupe and their basis mix:

| `evidence_level` | Rule |
|---|---|
| `limited` | ≤ 2 independent sources, **or** all units `cited_secondary` / `expert_assertion` / `practitioner_rating` |
| `medium` | 3 – 4 independent sources, mixed basis |
| `robust` | ≥ 5 independent sources with ≥ 2 `primary_measured` / `table` or ≥ 1 meta-analysis of tier `high` |

### 7.4 IPCC calibrated confidence (decision 3)

`agreement_level`: `high` if `A ≥ 0.8` · `medium` if `0.6 ≤ A < 0.8` · `low` if `A < 0.6`.

| evidence ↓ / agreement → | low | medium | high |
|---|---|---|---|
| **robust** | medium | high | very_high |
| **medium** | low | medium | high |
| **limited** | very_low | low | medium |

(Mastrandrea et al. 2010; AR5 WGII Fig 1.11; unchanged in AR6.) `confidence` / `effect_confidence` enum becomes
`very_low · low · medium · high · very_high`. **`expert_opinion` is removed from the enum**: expert-only evidence
is an *evidence* property (`limited`, `source_mix = expert_only` in the traceable account), not a confidence level,
and keeping it would let an expert-only cell dodge the matrix.

`context_dependent = true` **only** when low/medium agreement at the global level resolves into ≥ 2 scope rows of
differing sign or rank — a machine-readable "go read the scope rows". Irreducible disagreement stays visible as
`agreement_level = low` with both directions named in `conditionality` / `caveats`.

Transferability is **not** folded into confidence. Confidence answers "how sure is the literature";
`applicability.transfer_class` answers "does it apply here". Merging them would hide the Sweden→Sahel problem again.

### 7.5 Asset threat rows (decision 7)

For `asset_vulnerability` units the reconciled rank (0..+3, damage direction) maps to **`asset_sensitivity`**
(`none · low · moderate · high · very_high`, same `very_high` gate). **`asset_risk_weight`** is a derived
normalisation, never extracted: `w_h = rank_h / Σ rank` over the NbS's hazard set, emitted **only when all 7
hazards have an `asset_threat` row** (including `asset_sensitivity = none`). Otherwise the weights are blank
and the NbS carries `weights_incomplete` in the report so M2b falls back to equal weights. `timescale_of_effect`
on these rows means the **vulnerability window** (e.g. `short_term_1_3yr` = establishment period), to be read
with T0 `establishment_period_years`.

### 7.6 `magnitude_summary` (T6, decision 4b)

Emitted only when ≥ 2 independent sources in the row's scope share a `metric` and a VONT-convertible `unit`:
`{metric, unit, median, low, high, n, income_groups}`. Median is `_weighted_median` over `magnitude`; `low`/`high`
are the observed extremes (never a CI we did not measure). Cross-metric pooling is forbidden. The number sits
*under* the class in M5 and in the traceable account, with its `n`; it is not the value the MCDA uses.

### 7.7 `economic_value_range` — hard gates (decision 4)

A range is emitted only when **all** hold:

1. ≥ 2 independent sources;
2. same enum `unit` (`usd_per_ha · usd_per_ha_yr · usd_per_beneficiary · usd_per_tco2e · usd_per_farmer`) or
   VONT-convertible to it — a total project cost with no denominator is not a unit;
3. same `income_group` band (`lic_lmic` pooled; UMIC and HIC never pooled with it or each other);
4. same scope row.

HIC cost figures are **excluded outright** from LIC/LMIC and global rows — an exclusion, not a weight, because
labour, land and discount regimes do not transfer. No inflation adjustment at scoping grade: `source_note` records
each source's currency year; `low`/`high` = observed extremes. `SynthesisReport.excluded_economics` lists every
unit that failed a gate and why, so the exclusion is visible.

### 7.8 Weights summary

| Factor | Values | Origin |
|---|---|---|
| `TIER_W` | high 1.0 · medium 0.6 · low 0.35 | T4 engine |
| `BASIS_W` | primary_measured 1.0 · table 0.9 · modelled 0.7 · figure_read 0.6 · expert_assertion 0.5 · cited_secondary 0.4 | T4 engine |
| `GREY_DISCOUNT` | nbs_effect 0.4 · asset_vulnerability 0.6 *(new key)* · structural_suitability 0.9 | T4 engine (+1 key) |
| `TRANSFER_W` | d=0 1.0 · d=1 0.7 · d=2 0.3 | new, §5.2 |
| `XW.weight_factor` | direct 1.0 · proxy 0.7 · component 0.7 | new, §4 |
| `ns` factor | 0.5 (direction only) | new, §3.2 |

All defaults; tune per RFC. Grey still **counts** in `n_sources` and in the envelope — it just cannot dominate.

---

## 8. The traceable account (IPCC evidence-table format)

`justification` becomes a structured object rendered as an IPCC-style evidence table row:

| Field | Written by | Content |
|---|---|---|
| `statement` | prose writer, from used quotes | Calibrated language, e.g. *"Agroforestry reduces the impact of drought on rainfed cropping in semi-arid systems (medium evidence, high agreement → high confidence)."* Levels are inserted by the engine, not composed by the writer. |
| `evidence_summary` | prose writer | Designs, n, where (envelope), magnitudes with CI and n where present, proxies named, grey named. |
| `agreement_note` | prose writer | What disagrees and whether it splits by context; cites `evidence_ids` on each side. |
| `mechanism` (→ `mitigation_mechanism` / `effect_mechanism`) | prose writer | 1–3 sentences from the quotes' mechanism statements. |
| `conditionality` / `caveats` | prose writer | Conditions from quotes; both directions when `agreement_level = low`. |
| `key_evidence_ids` | engine | Top-weight units, ≤ 5. |
| `source_mix` | engine | e.g. `{peer_reviewed: 3, grey: 2, expert: 0}`, `expert_only` when applicable. |

**Prose-writer rules** (the only AI step in synthesis): input = the *used* units' quotes + engine outputs; may
quote or paraphrase those quotes only; may not introduce a number, a source, or a direction absent from them;
every sentence carries the `evidence_ids` it rests on; output is text, never a class or level. A deterministic
check (`check_account.py`, PR3) verifies that every number in the account appears in a cited unit's quote or
`magnitude` field.

---

## 9. Asset vulnerability — layered sourcing (decision 7d, revised 2026-09-30)

**No expert-elicitation programme.** The team has no bandwidth for structured external elicitation. Asset
vulnerability is sourced from WOCAT and literature; an expert layer exists **only** as an optional, lightweight
pass by **internal Alliance / CGIAR staff** (e.g. the MFL team for agroforestry / forest restoration), and the
method must produce usable, honestly-graded rows without it.

1. **WOCAT seed.** One SRC row per relevant WOCAT technology entry (`source_category = grey`,
   `venue_type = grey`, `claim_basis = expert_assertion`, `design = practitioner_rating`), `url` + saved snapshot
   in `.cache/corpus/`, EV `locator_type = section`, `locator` = questionnaire section id (§6.3 tolerance to
   extremes). Its 4-level tolerance scale maps to `asset_sensitivity` via a BANDS `ordinal_rating` adapter row.
   The **technology → family** map is recorded and ratified like an XW row (FAM note + rationale).
   **Adapter built 2026-10-06 (`src/nbs_ruralscan/ingest/wocat.py`), PAUSE lifted.** The PDF export loses the
   ratings (the tick on the "decreased … increased" scale is graphical), so the adapter reads the structured
   questionnaire embedded in the QCAT page (`/api/database/technologies/<id>/`), caches it as
   `<sid>.source.json` and renders a deterministic markdown transcript `<sid>.md` — the artefact of record for
   `locator_type = section` evidence (one line per rated field; `validate_sources` verifies against it while the
   PDF keeps serving page-locator T4 units: a source may carry both). Units are **rule-based, no LLM**: QT 6.1/6.2
   impact values −3…+3 → `nbs_effect` (`metric = ordinal_rating`, `unit = wocat_impact`, variable + right-label
   polarity from `schema/lookups/wocat_impact_map.csv`); QT 6.3 disaster-coping → `asset_vulnerability`
   (`schema/lookups/wocat_hazard_map.csv`; BANDS `wocat_tol_*` → `asset_sensitivity`; `very well` = no damage).
   Compiler comments ride along in `outcome_raw`; nothing is inferred from them. Grey practitioner ratings carry
   `claim_basis = expert_assertion` + `design = practitioner_rating` and the grey discount. First run: 51 WH
   sheets → 690 units.
2. **Literature** from the single-pass sweep (establishment mortality, windthrow, plantation fire, flood scour
   studies), with species-specific claims routed by `claim_scope`. WOCAT-vs-literature concordance is what the
   `agreement_level` axis then measures.
3. **Optional internal rating pass.** Where an Alliance / CGIAR colleague with domain knowledge is available
   (MFL team, no external recruitment), a one-page structured form per NbS — the 7 hazards × the 5-level
   `asset_sensitivity` scale + one line of rationale each — lands as EV `evidence_type = expert`,
   `claim_basis = expert_assertion`, one SRC row per rater (`method_type = expert_elicitation`,
   `benchmark_tier = medium`), per Namita's protocol §4 mapping rules. Cost: ~30 minutes per rater per NbS.
   Never a prerequisite: a cell with WOCAT only is emitted as `evidence_level = limited` → confidence
   `low`/`very_low`, and M2b uses its equal-weight fallback more often. That is the honest state of the evidence,
   not a gap to be filled by a programme we cannot run.

---

## 10. Migrating the archived rows (decision 9c, with provenance caveat)

| Provenance class | Sources | Units | Action |
|---|---|---|---|
| T3/T6-targeted discovery (Castle 2021 · Batcheler 2024 · Quandt 2017 · WB FSRP 2022 · WB KCSAP 2016) | 5 | 72 | **Migrate** |
| T4 discovery only | 15 | 87 | Stay archived |
| No logged discovery (FMNR bundle grey/lit, WOCAT 507/1358, FAO ANR, WRI…) | 19 | 105 | Stay archived; re-enter only if a v1.6.0 targeted search includes the source |

Migration of the 72, in order:

1. **Deterministic re-shape.** Context keys → §3.3 fixed keys (country string → ISO3 → `income_group`; a
   `region = "Sahel"` cannot become an AEZ deterministically → blank + `migration_note`). `direction` copied where
   present. `magnitude` + `unit` → `strength_class` via BANDS where the metric is recognised. `variable` → VONT
   canonical via aliases. Role restamp (`climate_risk` → `nbs_effect`, or `asset_vulnerability` where
   `risk_role = asset_threat`). `ruleset_version = v1.6.0`.
2. **Quote-bounded classification** for units with a quote but no `direction` / `risk_role`: an LLM reads the
   verified quote **only** (no PDF) and emits `direction` + `strength_class = unspecified` + the phrase it relied on.
   Bounded to text a reviewer can check in seconds.
3. **QA sample.** 100 % of step-2 outputs, 10 % of step-1 rows, reviewed by Pete (outside the T4 dashboard —
   PR review of the CSV diff).
4. **Targeted re-extraction** (single-pass, v1.6.0) of a source when any holds: the cell would be `limited`
   without it · the source has only `scoping_candidate` rows · it is high tier with a pre-`v1.2` stamp · it is a
   WB PAD / MEL report (asset-vulnerability and cost-denominator content lives there).
5. **Supersession.** Where a re-extracted unit covers the same source × variable × page, the old unit →
   `review_state = dropped`, note `superseded_by=<evidence_id>`. Existing soft-delete mechanics; no hard delete;
   restorable.
6. **Unmappable** units (no VONT id, no XW target, unparseable context) stay in `_deferred/` with a
   `migration_note`. The live register holds only rows that can reach a cell.

Scoping-candidate units that survive migration count toward breadth in the report but never toward direction.

---

## 11. Schema changes — spec v0.3.0 → v0.4.0

All via `schema/structure/columns.json` + `spec.md` + generator + validator, in **PR2**, with an issue.

| Table | Change |
|---|---|
| **T3** | + `suitability_family_id` (opt) · `scope_type` (opt) · `scope_id` (opt) · `applicability` (obj) · `evidence_level` · `agreement_level` · `context_dependent` (bool) · `family_spread` (bool) · `asset_sensitivity` (cond: `risk_role ∋ asset_threat`). `confidence` enum → IPCC five. `mitigation_potential` becomes conditional (required for `livelihood_mitigation` / `both`; blank for pure `asset_threat`). `justification` → traceable-account object. |
| **T6** | + `suitability_family_id` · `scope_type` · `scope_id` · `applicability` · `evidence_level` · `agreement_level` · `context_dependent` · `family_spread` · `magnitude_summary` (obj). `effect_confidence` enum → IPCC five. `justification` → traceable-account object. |
| **EV** | `use_role` + `asset_vulnerability`. Effect-claim `relationship` shape (§3.2) and fixed `context` keys (§3.3) are content rules enforced by checks, not column changes. |
| **SRC** | No columns. `study_income_group` and `venue_type` back-filled deterministically (0/39 populated on the archived sources today; `benchmark_tier` case normalised — `Medium`/`medium` both occur). |
| **XW** *(new)* | §4. |
| **BANDS** *(new)* | §3.4. |
| **T7 / scope enum** | `income_group` added to `scope_type`; `lic_lmic` pooled band. IPCC matrix + WB income lookup as small lookup tables under `schema/lookups/`. |
| **VONT** | Rows for the 9 orphan outcome variables via ontology triage. |
| **SRCH** | `table` enum → `T4 · T3 · T6`. |

Seed rows (agroforestry T3 = 9 / T6 = 8; WH T3 = 8 / T6 = 7) get the new columns blank and are **frozen as a
validation benchmark** (§14); they are never synthesised (no `evidence_ids`, would agree with themselves).

---

## 12. Restore mechanics and ruleset v1.6.0

- **Ruleset v1.6.0** (major: new claim shape, new role, new synthesisers, T3/T6 re-activated). Snapshot
  `.agents/skills/_versions/v1.6.0/` with two contracts: `T3_T6_extraction_contract.md` (effect claims +
  asset vulnerability + fixed context + deferred pointers, single-pass with T4) and
  `T3_T6_synthesis_contract.md` (this engine + prose-writer rules). Row in `RULESET_VERSIONS.md`.
- **Code re-activation** (per `_deferred/README.md`, minus the dashboard): `ledger.py` / `search_log.py`
  `TABLES = ["T4", "T3", "T6"]`; ledger table derivation via **XW join** (variable → `target_table`) instead of
  `_ROLE_INV`, so "T3 extracted" means a variable actually routes to T3; SRCH manifest enum; `SRC.vars_extracted`
  resync. **Dashboard steps skipped** — T3/T6 generation runs outside the T4 QA/QC UI; review = PR review.
- **Deterministic checks**, wired into `generate.py` + CI like the existing gates: `check_context.py` (§3.3) ·
  `check_numbers.py` extended to `magnitude*` · `check_bands.py` (§3.4) · `check_xw.py` (every live effect
  variable has a VONT id and an XW row, or is reported `unmapped`) · `check_account.py` (§8). `validate_sources.py`
  unchanged and still the verbatim gate.
- **Skills**: `/t3t6-synthesise` mirroring `/t4-synthesise`; `/sweep-retro` and `sweep_metrics.py` extended to
  the new roles (`direction_from_quote_rate`, `unmapped_rate`, `excluded_economics_rate` must trend down).
- **AGENTS.md** lock entries added after ratification, not before.

---

## 13. Pilot and sequencing (decisions 8c, 10b)

**PR plan — each gated on the previous:**

| PR | Content | Gate |
|---|---|---|
| **PR1** | This document | Ratification by the three consumers (Pete · Namita · Brayden); MFL informed |
| **PR2** | Structure v0.4.0 + XW/BANDS/lookups + spec + ruleset v1.6.0 snapshot + contracts. No data. | Pete + Brayden (T3 columns) review |
| **PR3** | `cell_synthesis.py` + checks + tests on synthetic fixtures incl. the Sweden→Sahel case | CI green; fixture tests pass |
| **PR4** | Migration of the 72 targeted units + SRC back-fill + ledger/SRCH re-activation | QA sample reviewed |
| **PR5** | **Riparian pilot** — targeted re-extraction of the deferred-effect backlog, first generated T3/T6 rows | Acceptance criteria §14 |
| **PR6** | **Agroforestry volume test** — vs the frozen seed rows | MFL review of content |
| PR7+ | WOCAT adapter; FR / wetlands / WH swept single-pass under v1.6.0 | — |

**Why riparian first:** T4 already synthesised (#249); 10 of 12 sources hydrated; the deferred-effect backlog is
explicit (sediment/nutrient removal efficiencies, biodiversity dose-response, water-quality results, with source +
page); and the corpus is HIC-heavy, which makes it the sharpest envelope test — the global `soil_erosion_risk` row
*should* come out `out_of_context` for a Sahel AOI. Weak side: thin T3 content. Blanco-Canqui 2004 stays blocked on
its two-column text layer.

**Why agroforestry second:** 72 migrated units, LMIC-heavy corpus (tests scope rows and LIC/LMIC pooling), and
hand-authored seed rows to benchmark against.

**Forest restoration timing:** FR T4 sweep proceeds now under v1.5.1 with the structured deferred-pointer list
(§3.5), so its effects pass later is a lookup, not a re-read. Wetlands and WH the same.

---

## 14. Validation and acceptance

**Gates (every PR):** structure validation · generated JSON fresh · `validate_sources` verbatim · `check_numbers` ·
`check_context` · `check_bands` · `check_xw` · `check_account` · ledger reconciliation · pytest · ruff · ty.

**Pilot acceptance (PR5):**

1. Every emitted row has ≥ 1 `evidence_id`, all resolving to live, non-dropped units whose quotes pass the verbatim gate.
2. Every level (`evidence_level`, `agreement_level`, `confidence`) reproduces from the units by the rules in §7 — a re-run on the same register is byte-identical.
3. The Sweden→Sahel fixture yields `no_applicable_evidence` for a Sahel AOI and a correct `income_group = high` scope row only when ≥ 2 HIC sources exist.
4. No `economic_value_range` violates a §7.7 gate; every excluded economic unit is listed in the report.
5. No traceable account contains a number or source absent from its cited units (`check_account`).
6. A Pete read of every generated riparian row against its account: zero rows where the class contradicts the cited quotes.

**Volume-test acceptance (PR6):** generated agroforestry cells vs the 17 frozen seed rows — agreement within ±1
rank on ≥ 70 % of overlapping cells; every disagreement explained in the report (which is more likely to be right,
and why). Seed rows are then retired or re-authored with `evidence_ids`.

---

## 15. Decision log (2026-09-29, Pete)

| # | Decision | Choice | Key rationale |
|---|---|---|---|
| 1 | Keying | **Family rows + always an NbS roll-up**, `suitability_family_id` optional | Effects differ ~10× by family; consumers compare NbS; pooled roll-up keeps weighting intact |
| 2 | Envelope storage | **Rows per scope** (BIND pattern) + `applicability` on every row | Overrides too rich for inline blobs; one resolver; QA-able rows |
| 3 | Disagreement | **IPCC two-axis confidence**; modal-sign median; `no_relationship` only for real nulls; `context_dependent` narrowed | Familiar, respected format; separates evidence from agreement; no false zeros |
| 4 | Numeric bar | **`economic_value_range` under hard gates + `magnitude_summary`** | One numeric slot for MCDA, numbers under the class with their n |
| 5 | Crosswalk | **New `XW` register**, `proximity` + haircut, ratified | Many-to-many; proxies never relabelled silently |
| 6 | Roles | **Collapse to `nbs_effect`; new `asset_vulnerability`**; `climate_risk` reserved for T2 | Role = claim kind; one unit can feed T3 and T6 |
| 7 | Asset threat | **WOCAT seed → literature; internal Alliance/CGIAR rating pass optional only** (revised 2026-09-30: no external expert-elicitation programme, no bandwidth); `asset_sensitivity` field; weights only on complete hazard sets | Literature near-empty; WOCAT covers every hazard; weights are a normalisation; expect many `limited` cells and M2b fallback |
| 8 | Pilot | **Riparian → agroforestry → FR single-pass**; FR T4 now with deferred pointers | Envelope stress test first; seed benchmark second; no 40-paper re-read |
| 9 | Migration | **Targeted (c)**: only the 72 targeted-search units; deterministic re-shape; quote-bounded LLM; supersession via soft-delete | T4-net effect rows are incidental, not evidence-targeted |
| 10 | Sequencing | **Staged PRs 1–6**, consumers ratify PR1, seed rows = benchmark only, Brayden co-reviews T3 columns | One logical change per PR; green-light rule |

Sub-decisions taken by default (flag if wrong): LIC+LMIC pooled as one band · no inflation adjustment · BANDS
machine-readable · proxy haircut 0.7 · `priority_need` stays reserved · restamped rows get `v1.6.0` ·
`timescale_of_effect` reused as vulnerability window · WOCAT adapter = PAUSE · 100 % QA on quote-bounded calls ·
unmappable rows stay archived · `expert_opinion` dropped from the confidence enum.

---

## 16. Open questions

- **BANDS thresholds** for `pct_change` and `ln_response_ratio` are conventions, not literature — ratify or replace.
- **AEZ adjacency** (§5.2) uses a 4-class `climate_zone`; is that coarse enough to be defensible, or should it read T7 AEZ groupings?
- **`iplc_lands` and `gender_inequity`** as T6 targets: effect evidence on these is thin and almost always qualitative. Accept `limited` / `very_low` rows, or leave them as T5 context-only? (No elicitation programme will fill them.)
- **Internal rater weight**: an MFL-team rating lands at `BASIS_W["expert_assertion"] = 0.5` × `TIER_W["medium"]`, i.e. below a single grey WOCAT entry after its 0.6 discount only marginally. Acceptable, or should ≥ 2 independent internal raters lift the cell to `medium` evidence?
- **WOCAT technology → family mapping**: who owns it (Namita + MFL?), and does a WOCAT entry that spans two families go to `cross_family`?
- **M2b equal-weight fallback** when `asset_risk_weight` is blank — Brayden to confirm that is the right default.
