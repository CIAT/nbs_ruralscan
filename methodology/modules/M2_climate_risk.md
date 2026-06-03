# M2 — Rural Climate Risk

**Module spec sheet · v0.1 draft · May 2026**

| Field | Value |
|---|---|
| **ID** | M2 |
| **Module** | Rural Climate Risk |
| **Owner(s)** | Brayden Youngberg (lead) · Pete (oversight) · Benson (pipeline integration) |
| **Status** | Draft — pre-scaffolded for Brayden, awaiting methodology authorship in Session C |
| **Schema tables consumed** | T1 · T2 · T3 (for NbS-relevant hazards) · T7 |
| **Schema tables produced** | (none — outputs are rasters + tables) |
| **Position in pipeline** | M0 (Setup) → **M2 (Climate Risk)** ‖ M1 (Suitability) → presented alongside M1 in Opportunity Space view; informs M4 hotspot scoring |

> **Brayden — this is a v0 scaffold.** Section structure inherits from M1 so spec sheets across the project are consistent. Substantive methodology choices (which hazards per NbS, vulnerability composition logic, dataset preferences, parameter defaults) are yours to author in Session C and onwards. The spec defines the I/O surface so M1 / M3 / M4 know what to consume — change the internals freely, but try to preserve the I/O contract.

---

## 1. Purpose

For a selected NbS and area of interest, M2 produces a **rural climate risk surface** characterising where rural livelihoods (populations and production systems) are exposed to climate hazards relevant to the chosen NbS. Risk is computed under **baseline and future scenarios** so the "act now vs delay" narrative is supported. The surface is:

- Continuous (0–1) — interpretable as relative risk within the AOI
- Mode-aware — Mode A (Hazard × Exposure) by default; Mode B (full IPCC AR6 with vulnerability) optional
- NbS-aware — uses only hazards relevant to the selected NbS, as recorded in T3
- AOI-specific — exposure layers reflect local population and production patterns

M2 answers a question that is **deliberately separated from M1 suitability**: where rural livelihoods are at risk from the hazards this NbS can plausibly help with.

## 2. Question answered

> *"Within this AOI, where are rural populations and production systems exposed to climate hazards that this NbS could mitigate — under baseline conditions today, and under mid-century climate change?"*

What M2 explicitly **does not** answer:

- Risk to the *project/investment itself* (the WB Climate & Disaster Risk Screening lens) — now specified separately in [`M2b_project_risk.md`](./M2b_project_risk.md), not in this module
- Where the NbS is biophysically feasible (M1)
- What TTL development priorities concentrate where (M3 / M4)
- Whether the NbS actually reduces the risk (M5 scorecard captures this qualitatively; quantitative impact modelling is downstream of scoping)

Crucially, **vulnerability variables that also appear in M3 / M4** (poverty, adaptive capacity, GESI proxies) are gated by the **double-count guard** in T2 — see §9.

## 3. Inputs

| Input | Source | Schema | Notes |
|---|---|---|---|
| Selected NbS | M0 Setup | `T0.nbs_id` | Resolves to T3 rows that list NbS-relevant hazards |
| Area of Interest | M0 Setup | `T7` row(s) | Country / admin unit / hydrobasin polygon |
| Analysis resolution | M0 Setup | (run config) | Default 1 km; same as M1 |
| Climate risk **mode** | M0 Setup | (run config) | `mode_a` (Hazard × Exposure — default) or `mode_b` (× Vulnerability) |
| Climate scenarios | M0 Setup | (run config) | Always includes `baseline`; one or more `future_*` |
| NbS-relevant hazards | T3 | `T3.hazard_type` rows for this `nbs_id` | List of hazards to include — drought, flood, heat, fire, wind/cyclone, waterlogging, frost |
| Hazard variables | T2 + T1 | `T2` rows where `risk_component=hazard` | One or more variables per hazard type |
| Exposure variables | T2 + T1 | `T2` rows where `risk_component=exposure` | Rural pop, smallholder farms, production value, livestock density |
| Sensitivity variables (Mode B only) | T2 + T1 | `T2` rows where `risk_component=sensitivity` | Crop sensitivity to drought, livelihood diversification, etc. |
| Adaptive capacity variables (Mode B only) | T2 + T1 | `T2` rows where `risk_component=adaptive_capacity` | Education, financial access, governance — context-dependent |
| Double-count flags | T2 | `T2.double_count_risk` per variable | Controls whether a variable flows here, to M3/M4, or both |
| Geographic context | T7 | AEZ / farming system masks | For zone-specific weighting if defined |

## 4. Outputs

| Output | Format | Path | Consumer |
|---|---|---|---|
| **Composite rural climate risk raster — baseline** | COG, 0–1 | `pipeline/outputs/<pilot_id>/maps/climate_risk_baseline.tif` | Opportunity Space view (alongside M1); M4 hotspot scoring |
| **Composite rural climate risk raster — future** | COG, 0–1 (one per future scenario) | `…/climate_risk_<scenario>.tif` | Future-state view; "act now vs delay" narrative |
| **Δ raster (future − baseline)** | COG | `…/climate_risk_delta_<scenario>.tif` | Visualisation of climate trajectory |
| **Per-hazard surfaces** | COGs (one per hazard, both scenarios) | `…/hazards/<hazard>_<scenario>.tif` | Drilldown views in the wireframe; per-hazard sensitivity |
| **Hazard summary table** | CSV | `pipeline/outputs/<pilot_id>/tables/climate_risk_summary.csv` | Right-panel readout in Opportunity Space; AOI-level stats per hazard × scenario |
| **Weight log** | CSV | `…/tables/climate_risk_weights.csv` | Audit trail of hazard weights, exposure weights, mode used |
| **Resolution audit** | CSV (merged with M1's audit) | `…/tables/resolution_audit.csv` | Per-input native vs analysis resolution |
| **Mode + scenario metadata** | JSON | `…/climate_risk_meta.json` | Records Mode A vs B, scenarios run, double-count decisions made |

The composite risk raster (both scenarios) + the summary table together are what the wireframe's Opportunity Space tab and the M4 hotspot view consume.

## 5. Dependencies

**Upstream:** M0 Setup. M2 runs *in parallel with M1* — there is no dependency between them. Both write outputs to the same pilot folder.

**Downstream:**
- **Opportunity Space view** (wireframe) shows M1 and M2 results together. The user can toggle which surface is the primary visual.
- **M4 Hotspots** consumes the M2 baseline (and optionally future) composite as one of the priority MCDA layers — TTLs can weight "climate risk to rural livelihoods" alongside poverty, biodiversity, etc. The double-count guard in T2 ensures variables used here aren't also used as standalone T5 priority variables.
- **M5 Scorecard** doesn't read M2 outputs directly; it uses T3 to render the NbS's qualitative response to the listed hazards.

## 6. Sub-steps

Eight named steps inside M2. Each has its own I/O contract.

### 6.1 NbS-relevant hazard scoping

- **In:** `nbs_id`; T3 rows for this NbS.
- **Out:** list of relevant hazards (e.g. for agroforestry: drought · heat stress · fire · wind/cyclone).
- **Notes:** if a hazard has no T3 row for this NbS, it is not included. Recipe authors must populate T3 explicitly.

### 6.2 Hazard layer assembly

- **In:** relevant hazard list; T2 hazard rows; T1 dataset references; AOI; resolution; scenario.
- **Out:** raster stack of hazard layers (one band per hazard × scenario). Bands are intensity / frequency metrics, e.g. SPEI-12 for drought, return-period flood depth, heat-days > threshold, etc.
- **Notes:** apply context overrides from T7 where defined (e.g. AEZ-specific drought thresholds). Generate resolution audit rows.

### 6.3 Exposure layer assembly

- **In:** T2 exposure rows; T1 dataset references; AOI; resolution.
- **Out:** exposure raster stack (rural population, smallholder farm density, production value).
- **Notes:** baseline only — exposure layers are not projected forward. The future risk surface uses baseline exposure × future hazard.

### 6.4 (Mode B only) Vulnerability composite

- **In:** T2 sensitivity and adaptive_capacity rows; double-count flags.
- **Out:** vulnerability raster (0–1, where higher = more vulnerable).
- **Notes:** Vulnerability = f(Sensitivity, Adaptive Capacity) per IPCC AR6. Composition function TBD by Brayden — options include weighted geometric mean, additive, or principal-component-derived. **Skip this sub-step entirely in Mode A.** Variables whose `T2.double_count_risk = opportunity_space_only` are excluded here (they belong to M3/M4).

### 6.5 Risk composition

- **In:** hazard stack; exposure stack; (Mode B) vulnerability raster; mode flag.
- **Out:** composite climate risk raster per scenario.
- **Algorithm:**
  - **Mode A:** `Risk = f_combine(Hazard, Exposure)`. Suggested default: per-hazard hazard × exposure, then weighted sum across hazards using T2 weights, normalised to 0–1.
  - **Mode B:** `Risk = f_combine(Hazard, Exposure, Vulnerability)` per IPCC AR6. Suggested default: per-hazard hazard × exposure × vulnerability, weighted sum across hazards, normalised.
- **Notes:** the exact composition function (multiplicative, additive, geometric mean) is a methodology choice for Brayden to document and justify. Whatever's chosen, the choice is logged in `climate_risk_meta.json`.

### 6.6 Future scenario run

- **In:** any `future_*` scenario in the run config.
- **Out:** Risk raster per scenario. Δ raster per scenario.
- **Notes:** re-runs §6.2 with future hazard datasets (per T1 `future_dataset_ids` or T2 `scenario_type`), keeps §6.3 exposure constant, re-composes via §6.5.

### 6.7 Sensitivity & uncertainty

- **In:** hazard weights; exposure weights.
- **Out:** sensitivity raster (variance under ±10% weight perturbation, analogous to M1's approach).
- **Notes:** uses the same perturbation pattern as M1 §6.7 — keeps the framework's uncertainty handling consistent across modules.

### 6.8 Hazard summary extraction

- **In:** composite risk raster; per-hazard rasters; AOI; T7 admin / AEZ vectors.
- **Out:** summary table — per hazard, per scenario, per admin unit: mean risk, share of area in high-risk class, exposed rural population, exposed production value, Δ vs baseline.
- **Notes:** this is the table the wireframe's right-panel reads from.

## 7. Variable Cards consumed

All T2 variables in the recipe — defined in the recipe markdown's hazard/exposure/vulnerability sections and as schema rows in `schema/recipes/<nbs_id>/T2_climate_risk.csv`. Each variable's six-slot Variable Card travels through the pipeline as metadata, displayed in the Variable Config tab.

Mandatory before M2 can run: every variable in T2 for `nbs_id` (filtered by selected mode) must have a populated card with all six slots.

## 8. Variable selection — Ani's three principles

M2 implements the same three principles as M1:

1. **Reduce** — thematic grouping is by IPCC risk component (hazard / exposure / sensitivity / adaptive capacity). Correlation clustering also runs across variables within the same component for the AOI. Cluster membership is logged.
2. **Source** — three-tier dataset preference (native GEE → community GEE → upload). For M2 specifically, the climate projection datasets (NEX-GDDP-CMIP6, CORDEX, TerraClimate future scenarios) are usually native GEE; some socio-economic exposure layers may require upload.
3. **Explain** — Variable Card metadata flows through pipeline to UI.

## 9. Mode A vs Mode B — when to use which

| | Mode A — Hazard × Exposure | Mode B — Full IPCC AR6 |
|---|---|---|
| **Formula** | Risk = H × E | Risk = H × E × V, where V = f(Sensitivity, Adaptive Capacity) |
| **Variables required** | Hazard + Exposure | Hazard + Exposure + Sensitivity + Adaptive Capacity |
| **Pilot default** | ✅ | optional |
| **Why default?** | Avoids double-counting vulnerability variables (poverty, AC) that also appear as standalone TTL priority variables in M3 / M4. Cleaner separation of "risk to livelihoods" from "TTL priorities". | Methodologically more complete per IPCC AR6. Use when the AOI has high-quality vulnerability data and the analysis is explicitly comparing Mode A vs B. |
| **Implementation effort** | Lower; ~half the dataset requirements | Higher; needs full sensitivity + adaptive capacity layers |

The mode toggle is a user-facing control (wireframe Setup tab). The selected mode is recorded in `climate_risk_meta.json` so outputs from different modes are not inadvertently compared.

## 10. Double-count guard

Variables that could plausibly belong to either M2 (climate risk) or M3/M4 (TTL priorities) are flagged in T2 with `double_count_risk`:

- `risk_only` — variable used only in M2 (never in M3/M4)
- `opportunity_space_only` — variable used only in M3/M4 (never in M2)
- `shared` — pipeline default is to use in M2 only, but the recipe author can override

**Common shared variables and recommended defaults:**

| Variable | Common temptation | Recommended placement | Why |
|---|---|---|---|
| Poverty headcount | Use as AC proxy in Mode B vulnerability | M3/M4 only | TTLs already weight poverty as a priority — don't double-count |
| Education / literacy | Use in Mode B AC | M3/M4 (GESI / equity) | Same reasoning |
| Distance to road | Use as AC proxy | Neither (it's a suitability variable in M1) | Belongs to M1 structural feasibility |
| Smallholder share | Could be exposure or priority | M2 exposure | It's structural to who's at risk |
| Crop production value | Could be exposure or priority | M2 exposure | Yes, both could work — choose M2 to avoid double-count; M3 can show it descriptively |

The guard runs as a check at start-of-pipeline; if a variable appears in both T2 (active) and T5 (active) for the same `nbs_id` without an explicit override, the pipeline raises a validation error.

## 11. Climate trajectory storyline

A primary purpose of M2 is to support Laurent's "act now vs delay" narrative for TTLs. The expected story-from-output is:

> *"Today, X km² of [country] are exposed to drought + heat stress at moderate-to-high levels, affecting Y million people. By 2050 under SSP2-4.5, the exposed area grows to Z km² and shifts geographically into [region]. [NbS] is biophysically suitable in some, not all, of this exposed area today — but the overlap shrinks 14% by 2050 if no action is taken."*

The composite + Δ rasters, the hazard summary table, and M1's suitability surface together support this narrative. The wireframe's Opportunity Space tab already has a "Δ under SSP2-4.5" panel positioned for this.

## 12. Tests / acceptance criteria

- [ ] Reads all analytical parameters from T0–T7; no hardcoded thresholds or weights in pipeline code.
- [ ] Runs end-to-end for agroforestry Sierra Leone, Mode A, baseline + SSP2-4.5.
- [ ] Mode B run produces a finite vulnerability raster (no NaN bands).
- [ ] Outputs validate: COGs are compliant, CSVs have expected headers, meta.json is valid JSON.
- [ ] Double-count guard catches a deliberately mis-flagged variable.
- [ ] Per-hazard rasters and composite raster are both produced and visually consistent.
- [ ] Resolution audit includes all M2 inputs.

## 13. Definition of done

For M2 to be considered "done" for a given NbS in a given AOI:

- [ ] T3 rows populated for this NbS — at minimum one hazard with confidence ≥ medium
- [ ] T2 rows populated for each relevant hazard, exposure, and (Mode B) vulnerability variable
- [ ] All variables have native GEE / community GEE access or upload completed
- [ ] All Variable Cards have six slots populated
- [ ] Pipeline runs end-to-end without manual intervention
- [ ] Outputs sanity-checked by Brayden + Pete against regional climate knowledge
- [ ] Mode A and Mode B both runnable; results compared in a methodology note

## 14. Implementation notes for Claude Code

Suggested Python function signatures for `pipeline/climate_risk.py`:

```python
def relevant_hazards(nbs_id: str, t3: pd.DataFrame) -> list[str]:
    """§6.1 — return list of hazard_type strings for which this NbS has a T3 row."""

def assemble_hazards(hazards: list[str], aoi, scenario: str, t1: pd.DataFrame, t2: pd.DataFrame) -> ee.Image:
    """§6.2 — multi-band image, one band per hazard × scenario, harmonised to AOI + resolution."""

def assemble_exposure(aoi, t1: pd.DataFrame, t2: pd.DataFrame) -> ee.Image:
    """§6.3 — multi-band exposure image (rural pop, farm density, production value)."""

def compose_vulnerability(aoi, t1: pd.DataFrame, t2: pd.DataFrame) -> ee.Image:
    """§6.4 — only called in Mode B. Returns single-band vulnerability (0–1)."""

def compose_risk(
    hazards: ee.Image, exposure: ee.Image, vulnerability: ee.Image | None,
    mode: str, weights: dict
) -> ee.Image:
    """§6.5 — return composite risk raster per scenario."""

def run_future(scenario: str, *args) -> ee.Image:
    """§6.6 — wrapper that re-runs §6.2 with future hazard datasets and re-composes."""

def sensitivity_perturb(stack: ee.Image, weights: dict, n: int = 50, scale: float = 0.1) -> ee.Image:
    """§6.7 — analogous to M1 sensitivity."""

def extract_summary(risk: ee.Image, hazards: ee.Image, aoi, admin_vector) -> pd.DataFrame:
    """§6.8 — return hazard summary table per admin unit + scenario."""

def double_count_check(t2: pd.DataFrame, t5: pd.DataFrame, nbs_id: str) -> list[str]:
    """§10 — validate no variable appears active in both T2 (for M2) and T5 (for M3/M4); return any violations."""
```

Each function is independently testable. The pilot notebook calls them in order; M2 outputs flow into the same pilot output folder as M1.

### Likely starting prompt for Claude Code (analogous to the M1 prompt)

> Implement `pipeline/climate_risk.py` for the Rural NbS Scan, following the spec in `methodology/modules/M2_climate_risk.md`. Use GEE Python (earthengine-api). Mode A only for the first pass — defer Mode B's vulnerability composition. Inputs are T1, T2, T3, T7 rows from the schema for a given `nbs_id`. Use the function signatures listed in the spec's "Implementation notes" section. Show me the imports + the first three functions; pause for review before the rest.

---

## Open questions for Session C

These need Brayden's call:

1. **Composition function for Mode A:** per-hazard multiplicative (H_i × E_i, sum) vs additive (H_i + E_i, weighted)? Default suggestion in §6.5 is the former; methodology note required either way.
2. **Vulnerability composition (Mode B):** weighted geometric mean? Additive? PCA-derived? Documented assumption either way.
3. **Hazard-type weights:** equal weights across NbS-relevant hazards (default), or recipe-specific weights per hazard? Latter requires T3 to carry a `relative_weight` field.
4. **Per-hazard sub-mode flexibility:** is "Mode A for drought + Mode B for flood" allowed? Probably no for v0 — global mode for simplicity.
5. **Exposure layer count:** suggested defaults are rural pop, farm density, production value. Are there others Brayden wants (livestock, irrigated cropland)? Recipe-specific or framework-wide?
6. **Mode toggle granularity:** at NbS run level, or globally for the pipeline? Suggest: NbS run level, so a TTL exploring multiple NbS in the same AOI can use Mode A for one and Mode B for another.

---

## Version history

- **v0.1** (May 2026) — pre-scaffolded spec for Brayden ahead of Session C. Structure mirrors M1_suitability.md. Substantive methodology choices flagged as open questions; I/O contract specified to enable parallel implementation of M1.
