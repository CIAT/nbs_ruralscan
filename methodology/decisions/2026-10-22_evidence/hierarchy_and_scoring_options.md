# How variables nest, and how evidence becomes an indicator score: options

*Read-only design study, 2026-10-22. Written for Pete. Nothing in the repo was changed except this file.*

**Your question:** "how variables will nest together into a hierarchy and how the evidence will be weighted and combined into the indicator score compatible with the dashboard design."

**Short answer:** the hierarchy up to **one cell per NbS × priority** (T6) and **one cell per NbS × hazard × farming system** (T3) is built, and the weighting inside a cell is well specified. **Nothing combines cells above that point.** There is no theme summary, no NbS-level score, no runtime scorecard, and nothing links T6 to the M4 hotspot. The wireframe doesn't ask for a single NbS score either. It asks for a **per-outcome Likert chip with a confidence badge**, grouped into sections, plus economic rows. So the main work is (a) translating our richer cell outputs into the wireframe's chip, and (b) deciding whether and how T6 should change the hotspot map. My recommendation is in §5.

---

## 1. The hierarchy as it exists

### 1.1 Tree

`[AGG]` = aggregation happens here today (with file:line). `[NONE]` = no aggregation exists.

```
NbS  (T0.nbs_id, e.g. agroforestry)
│
├── [NONE] NbS-level score / profile ........... nothing above the T6/T3 row (no runtime/scorecard.py;
│                                                runtime/outputs.py and schema_loader.py are empty files)
│
├── T5 THEME (climate_hazard · nbs_response · people_production · equity_inclusion · context)
│   │   [NONE] no theme roll-up of T6 classes. T5.theme is used only to group M4 hotspot weights
│   │          (spec.md:588, :603). The `theme_weights` lookup that spec.md:603 describes
│   │          does not exist in schema/.
│   │
│   └── T5 PRIORITY  (mcda_role = priority; 14 rows in schema/T5_opportunity_space.csv)
│       │   e.g. rural_poverty, soil_erosion_risk, drought_hazard, catchment_water_yield
│       │
│       └── T6 CELL = nbs × variable_id      (effect_direction 7-pt + conflicting_evidence | blank = data-deficient;
│           │                                  evidence_level × agreement_level → effect_confidence (IPCC))
│           │
│           ├── NbS ROLL-UP ROW (suitability_family_id blank)
│           │     [AGG] family vote: each classed family row votes with weight √n_sources; weighted
│           │           median of modal-sign family ranks; conflict if minority ≥ 1/3
│           │           (cell_synthesis.py:2937-2960, CONFLICT_MIN_SHARE = 1/3 at :758).
│           │           Falls back to a pooled synthesis when < 2 classed families or < 50% source
│           │           coverage. NB: this replaces the "pooled, not a mean of families" rule in
│           │           T3_T6_generation_method.md:79-83 (the doc is behind the code).
│           │     family_spread = true when families differ by ≥ 2 ranks.
│           │     family_rollup_policy.csv can bar a family (forest plantation) from the roll-up.
│           │
│           ├── FAMILY ROWS (suitability_family_id set; emitted at ≥ 2 independent sources)
│           │
│           └── SCOPE ROWS (scope_type/scope_id: income_group · aez · farming_system · admin…)
│                 [NO AGGREGATION — SELECTION] runtime picks the most specific matching row
│                 (spec.md:430 precedence; T3_T6_generation_method.md:100). Each row carries
│                 `applicability.transfer_class`; out_of_context → `no_applicable_evidence`.
│
│               ↑ [AGG] CELL SYNTHESIS (cell_synthesis.py:_reconcile_rank :660-700)
│                   unit rank −3..+3 → modal sign → weighted median of modal-sign ranks (strength);
│                   opposite/null units lower agreement, never strength; conflicting if minority ≥ 1/3.
│                   Unit weight = TIER × BASIS × grey discount × TRANSFER × XW.weight_factor × design
│                   weight × bundle/normal-year/ns factors (T3_T6_generation_method.md:460-473 + AGENTS locks).
│                   Caps: very_high only at rank 3 + conf ≥ high; modelled-only → moderate;
│                   size-sparse → moderate; hazard-intensity discount on T3.
│
│               ↑ [AGG-light] XW CROSSWALK  (schema/registers/XW_target_crosswalk.csv, 94 rows)
│                   EV outcome variable → T6 priority / T3 hazard / economic indicator.
│                   polarity (benefit frame), proximity direct 1.0 · proxy 0.7 · component 0.7.
│                   Many-to-many: drought_hazard → T3 drought AND T6 drought_hazard.
│                   xw_route_policy.csv switches routes off per NbS (e.g. wetland cooling).
│
│               ↑ EV OUTCOME VARIABLE  (VONT canonical id, e.g. household_income, crop_yield)
│                   VONT.group_id (socio_economic, hydrological, …) is a T4 clustering /
│                   prevalence group (spec.md:525, :748). It is NOT part of the effect
│                   hierarchy and does not match the T5 themes.
│
│               ↑ [AGG] EVIDENCE UNIT  (direction + strength_class via BANDS; context incl.
│                   income group, AEZ, farming system, hazard_severity, comparator, attribution)
│
├── T3 CELL = nbs × hazard_type × farming_system   (parallel branch, same units via XW)
│     mitigation_potential (very_negative … very_high, conflicting_evidence, blank = data-deficient)
│     risk_role livelihood_mitigation → M2;  asset_threat → M2b (asset_sensitivity)
│     [AGG] asset_risk_weight = rank_h / Σ rank over 7 hazards (the ONLY cross-cell
│           derivation in the system; T3_T6_generation_method.md:428-436)
│     [NONE] no reconciliation between T3 drought×farming_system and T6 drought_hazard.
│
└── ECONOMICS = T6 rows with variable_type = economic_indicator
      no direction (spec.md:638); economic_value_range only under hard gates (spec.md:648);
      [NONE] never aggregated, never normalised, never linked to any effect cell.
      Currently: 72 economic rows across 6 NbS, 14 carry a range; economic_archetype_id is
      blank everywhere.
```

### 1.2 Where things sit

| Concept | Where it sits | Aggregated? |
|---|---|---|
| **Suitability family** | A row variant of each T6/T3 cell. The NbS row is the family vote. | Yes: family → NbS (√n vote). |
| **Scope (income group, AEZ, farming system, country)** | A row variant of each cell. Runtime selects the most specific one. T3 uses farming_system as a cell key, not a scope. | No. Selected, not combined. |
| **Transferability** | `applicability.transfer_class` on every row, kept out of confidence on purpose (method :424-426). | No. It's a flag. |
| **Economics** | Separate T6 rows keyed by `economic_indicator_type`. | No. |
| **TTL priority weights** | Only in M4 (hotspot map): — · L · M · H → 0 · 1 · 2 · 3, normalised (M4_hotspots.md:69). | Spatial only. |
| **AHP + CRITIC + Entropy** | runtime/mcda.py (port of reference/R/spatMCDA.R) on pixel stacks. M1 uses it. M4 makes it optional, and by default TTL weights are used directly (M4_hotspots.md:70). | Spatial only. |

### 1.3 What the current data look like (NbS roll-up, global rows)

Agroforestry T6 (schema/recipes/agroforestry/T6_nbs_scorecard.csv):

| variable_id | effect_direction | confidence | flags |
|---|---|---|---|
| biodiversity_priority | moderate_positive | very_high | family_spread |
| carbon_sequestration_potential | moderate_positive | very_high | family_spread |
| rural_poverty | moderate_positive | very_high | family_spread |
| soil_erosion_risk | moderate_positive | very_high | family_spread |
| drought / heat_stress_hazard | slight_positive | very_high | |
| flood_hazard | slight_positive | high | |
| catchment_water_yield | slight_positive | medium | |
| production_gap | **conflicting_evidence** | medium | family_spread, context_dependent |
| water_stress | **conflicting_evidence** | medium | family_spread |
| gender_inequity, water_quality_risk | *(blank: data-deficient)* | very_low | |
| agricultural_dependency, iplc_lands | *(no row at all)* | | |

Every NbS shows the same mix: mostly positive classes, 1–2 `conflicting_evidence`, some data-deficient rows, and some priorities with no row. Any combining rule has to handle all four states. Treating the last three as zero would be wrong.

### 1.4 Inconsistencies found along the way (fix regardless of option)

- **spec.md:588** still lists the old theme enum (`infrastructure`, `equity_gender`). AGENTS.md:87 and opportunity_space_T5.md:23-37 have the ratified five. **M4_hotspots.md:147** lists a third version (`people`, `production`, `equity_gender`).
- **T5 `weight_default` within-theme sums:** nbs_response sums to **1.25** (five rows × 0.25, after water_quality_risk and catchment_water_yield were added). The spec says these normalise to 1 (spec.md:596).
- **T5 row count:** AGENTS.md says 17 (13 priorities). The CSV has 18 (14 priorities) since `catchment_water_yield` was added.
- **`theme_weights` lookup** is described in spec.md:603-607 but doesn't exist.
- **M5_scorecard.md:141** fixes a 5-point Likert and :96 a 3-level confidence. Both predate the 7-point + conflicting scale and IPCC 5-level confidence.
- **The T5↔T6 join for `nbs_response` layers** ("per-NbS strength comes from the matching T6 effect", spec.md:609-615) is a stated design. No module (M3, M4) or code implements it.

---

## 2. What the dashboard expects (docs/wireframe.html)

### 2.1 NbS Comparison tab (`panel-compare`, :3612-4008)

- **Columns** = NbS (picker :3618-3624). Each header shows the NbS name, sub-practice line and an **economic archetype tag** ("LONG HORIZON", :3695-3710).
- **There is no single NbS score and no total row.** The matrix is built from sections (`cmp-section`), each holding metric rows (`cmp-row`):
  - Opportunity space: area, coverage by class (:3713-3731). From M1.
  - Who it reaches: rural population, smallholder farms, production value, farm size (:3733-3765). T5 descriptors.
  - Climate resilience: Δ suitable area 2050, High+VH risk share, dominant hazard (:3767-3792). From M1/M2.
  - **NbS response · Likert** (:3794-3847). Seven outcome rows: *Erosion mitigation · Drought resilience · Biodiversity · Carbon mitigation · Rural income · Food security · Fire risk*. Per cell:
    ```html
    <div class="cmp-likert"><span class="lik pp">++</span><span class="conf high">HIGH</span></div>   (:3801)
    <div class="cmp-likert"><span class="lik n">−</span><span class="conf low">CAUTION</span></div>   (:3843)
    ```
    So the **per-cell data shape is `{likert ∈ {++,+,0,−,−−}, confidence ∈ {HIGH, MED, LOW} | "CAUTION"}`**. The legend reads "++ very high · + moderate · 0 neutral · − caution" (:3797).
  - **Economic profile** (:3849-3881): archetype tag; `$/ha establishment` range; `Time to first income` (yr range); `Revenue streams` (free text).
  - **Cost-effectiveness · indicative** (:3883-3919): `$ / beneficiary`, `$ / ha restored`, `$ / tCO₂e avoided`, `$ / farmer reached`, each a `low–high` range, with an "indicative" badge and a linear-NbS asterisk. These match the T6 `economic_indicator_type` denominators.
- **Pairwise overlap** (:3965-4006): "size = shared area · colour = priority score". This is the only place the comparison tab uses a priority score, and it is the **M4 spatial hotspot class mix**, not a T6 roll-up.
- **Scope bands** (suitability scope + priority scope, :3643-3660) mask the area metrics to suit ∩ hotspot (:6037-6058). The Likert rows do not change with scope.

### 2.2 Opportunity Space "What this NbS can address" (:3550-3594)

Per row: the **problem name**, a **5-class distribution bar of the problem within the opportunity space** (`pp-bar`, none/low/mod/high/vh shares), a headline (e.g. "35% high+ · 1.5M ppl"), and the **Likert chip + confidence** (`rating`). Rows: Biodiversity loss, Carbon, Rural poverty, Gender inequality, Food insecurity, Fire risk. The M5 spec calls this "problem present (bar) × response strength (chip)" (M5_scorecard.md:59). The economic archetype card sits underneath (:3598-3604).

### 2.3 Priority Hotspots (`panel-hotspot`)

- **TTL priority rail** (:4104-4141): per priority, a 4-state control `— · L · M · H` (`data-p` 0–3). There are three weighted pillars (Climate hazard, NbS response, People & production) with **percent tags** ("4 vars · 35%", :4105). Equity & inclusion is a **"flag · not weighted"** pillar (gender national flag, :4131-4140). Descriptors are filters only (:4144-4155).
- **Presets** in JS (:5896-5901): `{drought:3, flood:2, …}` on the 0–3 scale, plus saved profiles (:5953-5956).
- The **masked NbS response profile** (:4414-4456) repeats the chip list within the hotspot intersection. It says "Likert response strength stays the same, but the underlying problems are more severe here" (:4416). So the design assumes **T6 doesn't vary spatially, and only the problem bar changes**.
- "Why Kenema is #1" (:4288-4297) explains the rank by **need drivers and TTL weights only**. NbS effect doesn't enter the hotspot score.

### 2.4 docs/dashboard.html

This is the evidence/QA dashboard. It labels T3/T6 units (:2660-2664, :3063-3078) but doesn't render scorecard output. Not relevant to the indicator shape.

---

## 3. The gap between §1 and §2

| # | The wireframe expects | What we produce | Gap |
|---|---|---|---|
| G1 | A 5-glyph Likert (`++ + 0 − −−`) | A 7-point scale plus `conflicting_evidence`, plus blank (data-deficient), plus missing rows | We need a display mapping, and three extra states need their own glyphs. The wireframe has nowhere to put "conflicting", "data-deficient" or "not assessed". M5:141 already says *n/a ≠ 0*. |
| G2 | 3-level confidence (HIGH/MED/LOW) | IPCC 5-level, plus separate evidence and agreement axes | We need a collapse rule, or the badge widens to 5. **"CAUTION" is in the confidence slot, but it is a direction property (negative effect).** The cell has to show both. |
| G3 | Rows are *outcomes* (Rural income, Food security, Fire risk, Drought resilience) | Rows are T5 priority ids (rural_poverty, production_gap…) and T3 hazards | Food security and rural income are XW proxies into `rural_poverty` / `production_gap`. Fire is a T3 hazard with no T5 priority. Several T5 priorities have no wireframe row: water_quality_risk, catchment_water_yield, water_stress, flood, heat, agricultural_dependency, iplc_lands. **Row labels must come from T5 `ttl_priority_label` (+ T3 hazards), not be hard-written.** |
| G4 | One chip per NbS × outcome | Family rows, scope rows, `family_spread`, `context_dependent`, `transfer_class` | No slot exists for "varies by sub-practice", "depends on context" or "evidence not from LIC/LMIC". The runtime scope resolver for T3/T6 (income_group/AEZ) isn't built, so we can't yet pick "the row for this AOI". |
| G5 | Likert is the same inside and outside the hotspot (:4416) | AEZ / farming-system scope rows can make the class differ by location | Mostly true today (most scope rows are income_group, so they are AOI-wide). AEZ-scoped rows (WH: semi_arid, highland_tropics) would vary inside a country. |
| G6 | Economics: archetype, time-to-first-income, revenue streams, $ ranges | `economic_archetype_id` blank everywhere; no time-to-income or revenue-stream field; ranges on 14 of 72 economic rows | Three economic rows in the wireframe have **no schema source**. Most range cells would show "insufficient evidence". `cost_reduction` has a confidence but no class. What should it show? |
| G7 | TTL weights live on the hotspot tab only | No link from TTL weights to the comparison or response rows | The wireframe never uses TTL weights to order or emphasise the response rows. Cheap to add: sort or dim by the TTL's L/M/H. |
| G8 | Theme percentages ("35%") on the rail | No `theme_weights` lookup; within-theme defaults don't sum to 1 (nbs_response = 1.25) | The schema can't reproduce the rail's numbers yet. |
| G9 | Rail grouping: water stress under Climate hazard; gender unweighted; 10 priorities | T5: water_stress under people_production; gender_inequity and iplc_lands are priorities with weight 0.5; 14 priorities | Wireframe and T5 disagree. The spatial-grain rule (national gender = flag) explains gender. Water stress placement and the missing water_quality, catchment and IPLC rows do not. |
| G10 | Hotspot = need only (Why #1 has no NbS effect) | T5 spec says nbs_response layers are *modulated* by T6 (spec.md:609) | This is an unresolved design fork, not just a missing feature. See Option D. |
| **G11** | **No theme or NbS score is shown anywhere** | **None computed** | **There is no gap here unless we choose to create one.** The decision is whether to add a summary (Options B/C) or keep a profile (Option A). |

---

## 4. Options for combining T6/T3 classes and confidence

Constraints every option must respect (from AGENTS.md / spec):
- **Ordinal first.** Classes are the product. Numbers sit under the class (spec.md:646).
- **Economics are ordinal and never currency-normalised.** They stay separate from effects.
- **AHP + CRITIC + Entropy are for spatial priority layers only** (mcda.py operates on pixel stacks).
- **T6 links only to `priority` rows.** Descriptors get nothing.
- **No hidden averaging of opposite signs.** `conflicting_evidence` is a state, not a zero (spec.md:638; cell_synthesis.py:691-697).
- **M2b is a filter, never summed** (separate lens).

Shared building block (all options): a display mapping from our scale to the wireframe chip.

| T6 effect_direction / T3 mitigation_potential | Rank | Chip |
|---|---|---|
| strong_positive / high, very_high | +3 | `++` |
| moderate_positive / moderate | +2 | `+` (or `++` if you want the 5-glyph to keep the top two) |
| slight_positive / low | +1 | `+` faint |
| no_relationship / none (a reported null) | 0 | `0` |
| slight/moderate_negative / negative | −1/−2 | `−` (and the cell is a **caution**) |
| strong_negative / very_negative | −3 | `−−` |
| conflicting_evidence | n/a | **`±`** (new glyph: "studies disagree") |
| blank + data_deficient | n/a | **`?`** ("evidence exists but can't set a class", with the reason on hover) |
| no row | n/a | **`n/a`** ("not assessed": nobody searched, or no XW route) |

Confidence badge: collapse very_low+low → LOW, medium → MED, high+very_high → HIGH, **or** show the 5 IPCC words. Move **CAUTION** out of the confidence slot into the chip colour, so a negative effect still shows its confidence.

### Option A — No single score: a per-priority profile with confidence

**What it is.** The comparison matrix stays a matrix. Rows are T5 priorities (label from `ttl_priority_label`) grouped under the four weighted themes, plus a T3 hazard block. Each cell shows chip + confidence + up to three small markers: `◐` varies by sub-practice (`family_spread`), `⇄` depends on context (`context_dependent`), `⚠` evidence mostly outside LIC/LMIC (`transfer_class` out_of_context/mixed). Economics stay as their own section with ranges or "insufficient evidence".

- **Ordinal → number:** none.
- **Confidence:** display only.
- **Priorities → themes → NbS:** no arithmetic. The TTL's L/M/H from Priority Hotspots **orders and emphasises** rows: H rows first and bold, "—" rows collapsed. A per-NbS **count strip** in the header ("6 positive · 1 conflicting · 1 caution · 2 not assessed" across the TTL's weighted priorities) gives a quick read without a score.
- **Conflicting / data-deficient:** their own glyphs, never folded in.
- **Locked rules:** fully consistent. It is what M5 already says ("qualitative ratings are the deliverable", M5_scorecard.md:66).
- **Weakness:** no ranking. With six NbS and 14 priorities, a TTL has to read 84 cells. The count strip partly addresses this.

### Option B — Per-theme ordinal summary with explicit rules

**What it is.** Option A, plus one **theme summary chip** per NbS × theme (four themes, since `context` holds only descriptors), computed by fixed ordinal rules over the theme's priority cells that the TTL has switched on.

Proposed rules (each could be decided separately):
1. **Eligible cells:** priorities in the theme with TTL weight > 0, global or AOI-resolved scope row, class set, confidence ≥ **medium** (gate), `transfer_class` ≠ out_of_context.
2. **Theme class = the TTL-weighted median rank of eligible cells** (weights 1/2/3 from L/M/H). This is a median of ordinals, so it is not arithmetic averaging, and with all weights equal it is a plain median. Alternative rule: **the modal class**.
3. **Harm is never hidden:** if any cell in the theme is negative with confidence ≥ medium, the summary gets a caution marker, whatever the median says.
4. **Conflict is never hidden:** if eligible cells have opposite signs and the minority holds ≥ 1/3 of the TTL weight (the same 1/3 rule the engine uses at cell and family level, cell_synthesis.py:758), the theme summary is `±` (conflicting). It is not a median.
5. **Coverage:** the summary always carries `k of n priorities assessed`. If fewer than half the TTL weight in the theme is eligible, it shows `?` (insufficient) instead of a class.
6. **Theme confidence = the lowest confidence among the cells that set the median** (conservative, IPCC-style). Alternative: the median confidence.

- **Ordinal → number:** only as an ordering key for the median, never as an average.
- **Confidence:** gate (rule 1) plus a conservative carry (rule 6).
- **NbS level:** Option B stops at themes. An NbS-level line, if wanted, would be the same rules applied over the four theme chips. **I recommend stopping at themes:** a theme profile like "climate ++ · environment + · people ± · equity ?" is the honest top level.
- **Locked rules:** consistent. It is a direct reuse of the engine's own philosophy (modal sign, median, conflict ≥ 1/3), applied one level up.
- **Weakness:** the four sets of rules need ratifying. Medians over 2–4 cells are coarse (fine at scoping grade). Also, `drought_hazard` sits in T6 under `climate_hazard` and again in T3, so the climate theme must read **one** of them (recommend T6 for the summary, T3 for the farming-system drill-down).

### Option C — Numeric score: an ordinal→score map with confidence weighting

**What it is.** Each cell's rank becomes a number, weighted by TTL weight and confidence, summed to a −1..+1 (or 0–100) NbS score per theme and overall.

Sketch:
- `r_j` = rank / 3 ∈ {−1, −⅔, −⅓, 0, ⅓, ⅔, 1}.
- `c_j` = confidence factor, e.g. very_low 0.2 · low 0.4 · medium 0.6 · high 0.8 · very_high 1.0 (or a gate: drop < medium).
- `w_j` = TTL weight (0/1/2/3 normalised) × T5 within-theme default × theme weight.
- **Score** `S = Σ w_j c_j r_j / Σ w_j` over classed cells.
- **Coverage** `K = Σ w_j(classed) / Σ w_j(all)`. Always shown next to S.
- Conflicting and data-deficient cells are **excluded from S** and **reduce K**. They are never entered as 0.

- **Confidence:** a multiplier, which pulls uncertain effects toward 0.
- **Locked rules:** this is where it strains.
  - (i) **Ordinal-first is bent:** the equal-interval spacing slight=⅓, moderate=⅔, strong=1 is a convention, not evidence (the same issue as the open BANDS question, method :681).
  - (ii) **Confidence × magnitude mixes two different questions:** "how big" and "how sure". A strong-but-uncertain effect and a slight-but-certain one score the same. IPCC keeps them apart for this reason.
  - (iii) **Cross-priority summing adds unlike things** (tonnes of carbon and poverty headcount) through Likert ranks. MCDA does this with standardised layers, but here there is no spatial standardisation behind it.
  - (iv) **Excluding conflicting cells hides them unless K and a count are shown.** That is the spirit of the conflicting_evidence ruling.
  - Economics must stay out. Costs have no direction.
- **When it's acceptable:** as a **sort key in Technical mode**, shown with K, a sensitivity band (perturb the rank spacing and confidence factors, as M4 does for weights), and the cell matrix always visible. Not as the headline.

### Option D — T6 effects modify the M4 spatial MCDA

The hotspot today is **need only**: `H = Σ w_j p_j` over T5 priority layers inside the M1 mask (M4_hotspots.md:71). The T5 spec intends `nbs_response` layers to be NbS-modulated via T6 (spec.md:609-615). Three variants:

**D1 — Effect as a multiplier ("addressable need").** `H_nbs = Σ w_j · e_j · p_j`, where `e_j` maps the NbS's T6 class for priority j to [0, 1]: strong 1.0 · moderate 0.67 · slight 0.33 · null/negative/conflicting/data-deficient/not-assessed **0**, optionally × a confidence factor. The map then answers "where is the need *this NbS can address* highest", and it differs by NbS (which is what makes it comparable across NbS).
- *Ordinal → number:* yes, through `e_j`. This is the same equal-interval issue as Option C, but scoped to one scalar per layer.
- *Conflicting / deficient:* they **switch the layer off**, which has to be visible in the weight log and the "Why #1" panel ("drought need not counted: agroforestry evidence conflicting").
- *Negative effects:* must **not** produce negative hotspot values. Show them as a caution overlay (or a mask, like M2b), never subtracted.
- *AHP/CRITIC/Entropy:* if M4 ever turns on CRITIC/Entropy reconciliation, multiplying a layer by `e_j` changes its standard deviation and so its CRITIC weight. That double-applies the effect. **Apply `e_j` to the final weights, not to the layers**, i.e. `w'_j = w_j e_j / Σ w e`. That keeps AHP/CRITIC/Entropy purely spatial.
- *Scope rows:* AEZ / farming-system scope rows make `e_j` **vary by pixel**. That is powerful, but it contradicts the wireframe line "Likert stays the same" (:4416).
- *Risk:* the TTL's L/M/H no longer equals the effective weight. The UI must show "your weight × NbS effect = effective weight".

**D2 — Effect as a filter.** Keep `H` need-only, but a priority enters the NbS's hotspot stack only if the NbS has a **positive class at confidence ≥ medium** for it. Weights among the surviving layers are renormalised. This is a binary version of D1 with no magnitude spacing. It's simpler to defend: "we only count needs the NbS is evidenced to address".

**D3 — No modification; show side by side (status quo, made explicit).** The hotspot stays NbS-agnostic need (masked by NbS suitability). The response chip sits next to each driver in the "Why #1" and masked-profile panels (*need bar × response chip*, which the wireframe already draws at :4414-4456). The TTL reads "high poverty here × agroforestry `+` HIGH on poverty". The map isn't changed.

- **All D variants:** only `mcda_role = priority` layers; T2/T5 double-count guard unchanged; M2b still a filter.
- **Spec impact:** D1/D2 make spec.md:609 real. D3 means rewording spec.md:609 to "response shown alongside, not multiplied".

---

## 5. Recommendation

**Build A as the base, add B's theme chips as the summary, use D3 now with D2 as an opt-in toggle, and keep C out of the TTL view** (Technical-mode sort key at most).

Why:
- A + B fit the wireframe's shape almost exactly: chip + confidence per row, sections as themes. They reuse the engine's own conflict and median logic one level up, so there is one philosophy from evidence unit to theme. They never invent an interval scale.
- D3 costs nothing and matches the wireframe as drawn. D2 is the defensible way to make the hotspot NbS-specific without a magnitude spacing assumption. D1 is attractive but brings in the equal-interval issue and the CRITIC double-count trap.
- C answers "rank the NbS for me", which is a feasibility-stage question. This tool is scoping. A count strip ("6 + · 1 ± · 1 caution · 2 n/a") gives most of the ranking value without the false precision.

### Decisions for Pete

1. **Is there an NbS-level number at all?**
   (a) No, profile only (A) · (b) theme chips, no NbS number (A+B) **← recommended** · (c) theme chips + a Technical-mode sort score with coverage (A+B+C) · (d) a headline NbS score (C).

2. **Theme-summary rule (if B):**
   (a) TTL-weighted median of eligible cells **← recommended** · (b) modal class · (c) best-supported cell. Plus: confidence gate for eligibility at (i) ≥ medium **← recommended** or (ii) ≥ low; theme confidence = (i) lowest of the setting cells **← recommended** or (ii) median.

3. **Should T6 change the hotspot map?**
   (a) No, show side by side (D3) · (b) filter: only priorities the NbS is evidenced to improve (D2) · (c) multiplier with class→[0,1] spacing (D1) · (d) D3 by default with D2 as a TTL toggle **← recommended**.

4. **Display scale for the chip and badge:**
   (a) widen the wireframe to our scale: 7 classes, 5 IPCC confidence words, plus `±`, `?`, `n/a` · (b) keep the 5 glyphs (strong→`++`, moderate/slight→`+`) and collapse confidence to 3, **but add `±`, `?`, `n/a` and move CAUTION to chip colour** **← recommended** · (c) keep the wireframe exactly as is (not viable: there's no place for conflicting or data-deficient).

5. **What are the comparison rows?**
   (a) T5 priority labels grouped by theme + a T3 hazard block, generated from schema **← recommended** · (b) keep the wireframe's outcome rows (Food security, Rural income, Fire risk) and map them to T5/T3 through a small display crosswalk. And: does the comparison read T6 `drought_hazard` or T3 `drought × farming_system` for the climate rows? Recommend T6 for the summary, T3 for drill-down.

6. **Economics rows the schema can't fill** (archetype, time-to-first-income, revenue streams):
   (a) add fields to T6 or a small archetype lookup (structure change: manifest + issue) · (b) drop the rows from the wireframe and show only the 4–5 denominators T6 carries, with "insufficient evidence" where the gates fail **← recommended for now** · (c) hand-authored archetype text, labelled as such (conflicts with evidence-first).

Housekeeping to do whatever you decide (no decision needed):
- Fix the spec.md:588 and M4_hotspots.md:147 theme enums.
- Renormalise nbs_response `weight_default` (sums to 1.25).
- Create the `theme_weights` lookup spec.md:603 describes.
- Update the T5 row count in AGENTS.md.
- Bring the wireframe priority rail in line with T5 (water_stress theme; water_quality, catchment, IPLC rows).
- Bring T3_T6_generation_method.md §2.2 up to date with the √n family vote.
- Update M5_scorecard.md §11 to the 7-point + conflicting scale and IPCC confidence.
