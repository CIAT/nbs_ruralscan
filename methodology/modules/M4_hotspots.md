# M4 — Priority Hotspots (MCDA)

**Module spec sheet · v0.1 draft · June 2026**

| Field | Value |
|---|---|
| **ID** | M4 |
| **Module** | Priority Hotspots (MCDA) |
| **Owner(s)** | Pete Steward (operational lead, methods) · Brayden (methods support) · Benson Kenduiywo (QA/QC) · implemented in Python via Claude Code |
| **Status** | Draft — authored to match the v0.6 wireframe (Priority Hotspots tab) |
| **Schema tables consumed** | T5 · T7 (+ M1 opportunity-space mask, M3 priority layers, optional M2b project-risk rating) |
| **Schema tables produced** | (none — outputs are rasters + tables) |
| **Position in pipeline** | M1 (Opp Space) + M3 (Characterisation) → **M4 (Hotspots)**; M2b applied as a scope filter |

> Renamed from "TTL Hotspots" → **Priority Hotspots** (v0.6). M4 reuses M1's weighting engine (AHP + CRITIC + Entropy) with **TTL-supplied conceptual weights** replacing the recipe defaults. Computed in **Python** (numpy/rasterio); layers pulled via the Earth Engine API or direct source — there is no native server-side GEE pipeline.

---

## 1. Purpose

Within the opportunity space (M1's high + very-high suitability mask), M4 produces a **priority-hotspot surface**: where the NbS is both biophysically feasible *and* aligned with the TTL's weighted development priorities. It answers *"where should investment be targeted?"* — the prescriptive layer on top of M1's *"where could it work?"*.

The surface is continuous (0–1), classified Low → Very High, recomputed **live** as the TTL adjusts conceptual priority weights, and reported alongside a **bivariate** (suitability × priority) view, a ranked list of admin units, and an intersection fingerprint.

## 2. Question answered

> *"Within the opportunity space, where do the TTL's weighted priorities — climate need, livelihoods, biodiversity, portfolio fit — concentrate most strongly, so investment can be targeted?"*

What M4 explicitly **does not** do:

- Define where the NbS is feasible (M1) or characterise the priority variables (M3).
- Decide whether the investment is durable (M2b — applied here only as a *filter/scope*, never summed).
- Quantify benefits (M5) or model ecosystem services / CBA (downstream, M6).

## 3. Inputs

| Input | Source | Schema | Notes |
|---|---|---|---|
| Opportunity-space mask | M1 | `maps/opp_space_mask.tif` | M4 runs only within this mask |
| Standardised priority layers | M3 | `maps/characterisation/*` | One 0–1 layer per priority variable (raw assembly + clustering done in M3) |
| Priority variables + scoring rules | T5 | `T5` rows | Normalization method, direction, reference frame, theme, double-count flag — see §9 |
| TTL conceptual weights | UI (run config) | — | Per priority: — · L · M · H (conceptual, **not** arithmetic) |
| Project-risk rating (optional) | M2b | `maps/project_risk_*.tif` | Applied as a **scope filter**, not an MCDA term (see §7) |
| Geographic context | T7 | admin / AEZ vectors | For ranked-unit aggregation |

## 4. Outputs

| Output | Format | Path | Consumer |
|---|---|---|---|
| Hotspot score raster | COG, 0–1 | `…/maps/hotspots.tif` | Priority Hotspots map |
| Classified hotspot raster | COG, 5 classes | `…/maps/hotspots_class.tif` | Map shading |
| Bivariate raster | COG, 5×5 (suit × priority) | `…/maps/hotspots_bivariate.tif` | Bivariate view |
| Ranked-unit table | CSV | `…/tables/hotspots_ranked.csv` | "Top hotspots" + "Why #1" panels (per ADM unit: score, top drivers, poverty/production/pop) |
| Intersection fingerprint | CSV | `…/tables/hotspot_fingerprint.csv` | suit ∩ hotspot intersection panel |
| Weight log | CSV | `…/tables/hotspot_weights.csv` | Conceptual→numeric mapping + reconciled weights |
| Sensitivity map | COG | `…/maps/hotspots_sensitivity.tif` | ±10% weight perturbation |
| Run metadata | JSON | `…/hotspots_meta.json` | Weights, reference frames, scopes active, double-count decisions |

## 5. Dependencies

**Upstream:** M1 (mask) and M3 (standardised priority layers) must have run. M2b is optional.

**Downstream:** the wireframe Priority Hotspots tab; M5 may reuse the ranked units for the comparison view. M6 reads the top-ranked units for "validate priority districts in the field".

## 6. Sub-steps

1. **Priority layer intake** — load M3's standardised priority layers, clipped to M1's opportunity-space mask.
2. **Normalization check** — confirm each layer was standardised per its T5 rule (method · direction · reference frame); see §9. (Standardisation itself is performed in M3; M4 validates and records it.)
3. **Conceptual-weight mapping** — map each priority's TTL setting (— · L · M · H) to a numeric weight (default: 0 · 1 · 2 · 3), normalise to sum 1. Weights are conceptual ordinal inputs, *not* arithmetic precision (locked).
4. **Weight reconciliation (optional)** — where the recipe supplies an AHP/CRITIC/Entropy prior, reconcile TTL weights with it (reuse M1 §6.4 engine). Default for v0: TTL weights used directly.
5. **Weighted overlay (within mask)** — `H = Σ_j w_j × p_j` per pixel, over opportunity-space cells only; normalise to 0–1.
6. **Project-risk scope filter (optional)** — if M2b is active, apply its rating as a filter: exclude / flag High + Very-High project-risk cells. Applied as a mask, **never summed** into `H` (see §7).
7. **Bivariate composition** — bin suitability (M1) × priority (`H`) into a 5×5 palette for the bivariate view.
8. **Classification, ranking & fingerprint** — classify `H`; aggregate to ADM units (rank by mean/share); compute top drivers per unit; build the suit ∩ hotspot intersection fingerprint.
9. **Sensitivity** — ±10% perturbation of the conceptual→numeric weights (reuse M1 §6.7 pattern).

## 7. Combination rules & double-count guard

- **Priority variables (T5) vs climate-risk variables (T2):** a variable active in M4 must not also be active in M2 for the same `nbs_id` — enforced by the T2 `double_count_risk` guard (see M2 §10). Climate risk to livelihoods may enter M4 *as one priority layer*, but its constituent vulnerability variables must not also be standalone priorities.
- **Project risk (M2b):** applied as a **filter/scope only**. It is never added as an MCDA term, so sharing hazard variables with M1 suitability or M4 is acceptable (a check-and-balance, not double counting). See `M2b_project_risk.md` §7.

## 8. Scopes (TTL-facing filters)

The Priority Hotspots tab exposes filters that subset the view without changing the underlying score:

- **NbS Suitability Scope** — which M1 classes count as "opportunity space" (default VH + H).
- **Priority Scope** — which hotspot-intensity classes to show (default VH + H).
- **Project-Risk Scope** *(planned, depends on M2b)* — exclude/flag high project-risk cells.

Scopes are filters; they never re-weight the MCDA.

## 9. Normalization & reference frame (the methodology decision)

Priority variables have no universal "optimal", so how each is standardised to 0–1 **defines what a hotspot means**. This is declared **per variable in T5**, never hardcoded.

Each T5 row carries: `norm_method`, `direction`, `reference_frame`, `clip`, and provenance.

**Methods**

- **Fixed / absolute** — map raw values to 0–1 against externally justified breakpoints from a lookup (e.g. IPC food-insecurity phases, SPEI drought classes, a poverty line). Comparable across AOIs and time; needs a referenced standard.
- **Statistical / relative** — rank against a distribution. Prefer **percentile/quantile** (outlier-robust) over min–max. Requires a declared **reference frame**.

**Reference frame** (statistical methods only) — the population the variable is ranked against:

| Frame | Meaning | Trade-off |
|---|---|---|
| **AOI (default)** | "highest-need areas *within this country*" | full 0–1 spread → good discrimination; purely relative |
| Sub-national region | within a region | regional comparability |
| Global dataset | severity vs a global distribution | cross-AOI comparable; may give little internal contrast |
| Fixed baseline | change vs a historical baseline | trajectory framing |

**Recommended default (pending team ratification — see backlog issue A):** percentile within the **AOI**, *labelled as relative*, with the raw value + a fixed reference band shown alongside so relative contrast isn't misread as absolute severity. Use **fixed thresholds wherever a credible standard exists** (more defensible to the WB). The chosen method, direction and reference frame are surfaced in the UI and in the map caption (Technical mode), and logged in `hotspots_meta.json`.

> Priority scoring uses monotonic rescales (direction + clip), **not** the fuzzy membership curves of M1 suitability — priority is a *need* score, not a *fitness* score.

## 10. Variable Cards consumed

All T5 priority variables for the AOI, grouped by theme (climate hazards · NbS-response outcomes · people & production · infrastructure & access). Each carries its six-slot card; the "How to read" and "Where it comes from" slots plus the normalization summary render in the Variable Config "Priority / hotspot variables" surface.

## 11. Tests / acceptance criteria

- [ ] Reads all rules from T5/T7; no hardcoded weights, thresholds or reference frames.
- [ ] Runs within the M1 opportunity-space mask only.
- [ ] Conceptual weights (— · L · M · H) map to numeric and normalise to 1; map + ranking update on weight change.
- [ ] Each priority layer's normalization method + reference frame is recorded in meta and shown in the UI.
- [ ] Bivariate raster is a valid 5×5 classification; ranked-unit table lists top drivers per unit.
- [ ] Project-Risk scope (when active) filters, never alters the MCDA score.
- [ ] Double-count guard passes (no variable active in both T2 and T5).

## 12. Definition of done

- [ ] T5 rows populated with normalization rules for the NbS/AOI
- [ ] M1 mask + M3 priority layers available
- [ ] Normalization default ratified by the team (backlog issue A)
- [ ] Pipeline runs end-to-end for agroforestry Sierra Leone
- [ ] Outputs sanity-checked; ranked units match regional knowledge

## 13. Implementation notes (Python)

```python
def map_conceptual_weights(settings: dict, scale=(0,1,2,3)) -> dict:
    """§6.3 — map {priority: '—'|'L'|'M'|'H'} to normalised numeric weights."""

def normalize_priority(layer, rule) -> "np.ndarray":
    """§9 — standardise one priority layer to 0–1 per its T5 rule (fixed | min-max |
    percentile | z-score), with direction, reference frame and clip. (Applied in M3;
    validated here.)"""

def hotspot_overlay(priority_stack, weights, opp_mask) -> "np.ndarray":
    """§6.5 — weighted linear combination within the opportunity-space mask."""

def apply_project_risk_scope(hotspot, project_risk, mode='flag') -> "np.ndarray":
    """§6.6 — filter/flag high project-risk cells; never sum into the score."""

def bivariate(suitability, hotspot, bins=5) -> "np.ndarray":
    """§6.7 — 5×5 suit × priority classification."""

def rank_units(hotspot, admin_vector) -> "pd.DataFrame":
    """§6.8 — per-ADM-unit score, top drivers, intersection fingerprint."""

def sensitivity_perturb(priority_stack, weights, n=50, scale=0.1) -> "np.ndarray":
    """§6.9 — ±10% weight perturbation variance."""
```

## 14. Open questions

1. Conceptual→numeric mapping: 0/1/2/3 (default) vs 0/0.33/0.66/1 vs exponential? Document the choice.
2. Should "climate risk to livelihoods" (M2) enter M4 as a single composite priority layer, or as its component hazards? (Composite avoids double-count; components give finer control.)
3. Reference-frame default — confirm AOI-relative vs fixed-where-available (backlog issue A).
4. Project-Risk scope default behaviour — flag vs exclude.

---

## Version history

- **v0.1** (June 2026) — authored to match the v0.6 wireframe and to capture the priority-variable normalization decision. Reuses M1's weighting engine with TTL conceptual weights. Computed in Python (post native-GEE).
