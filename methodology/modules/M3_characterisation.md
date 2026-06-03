# M3 — Opportunity Space Characterisation

**Module spec sheet · v0.1 draft · June 2026**

| Field | Value |
|---|---|
| **ID** | M3 |
| **Module** | Opportunity Space Characterisation |
| **Owner(s)** | Namita Joshi (variable content) · Benson (QA/QC) · implemented in Python via Claude Code |
| **Status** | Draft — authored to match the v0.6 wireframe (Opportunity Space panels) |
| **Schema tables consumed** | T1 · T5 · T7 (+ M1 opportunity-space mask) |
| **Schema tables produced** | (none — outputs are rasters + tables) |
| **Position in pipeline** | M1 (Opp Space) → **M3 (Characterisation)** → M4 (Hotspots) |

> M3 *describes* the opportunity space; M4 *prioritises* within it. M3 assembles and characterises the priority/development variables (the "fingerprint", climate-risk-to-livelihoods profile, and problem-variable distributions) and hands the clustered priority layers to M4. Computed in **Python** (numpy/rasterio); layers pulled via the Earth Engine API or direct source.

---

## 1. Purpose

Within M1's opportunity-space mask, M3 extracts and characterises the **development/priority variables** — poverty, biodiversity loss, GESI, agricultural production, rural population, farm size, and hazard exposure — and summarises *who and what is in the opportunity space*. It produces the descriptive panels the TTL reads on the Opportunity Space tab and the clustered priority layers M4 weights into hotspots.

## 2. Question answered

> *"Within the area where this NbS could work, who lives there, what is produced, and which development problems (poverty, biodiversity loss, climate exposure) are most present?"*

What M3 explicitly **does not** do:

- Decide where the NbS is feasible (M1) or weight priorities into hotspots (M4).
- Score the NbS's *response* to these problems (M5) or assess investment risk (M2b).
- Apply the TTL conceptual weights (that is M4).

## 3. Inputs

| Input | Source | Schema | Notes |
|---|---|---|---|
| Opportunity-space mask | M1 | `maps/opp_space_mask.tif` | M3 characterises only within this mask |
| Priority variables | T5 | `T5` rows for the AOI | Themes: climate hazards · NbS-response outcomes · people & production · infrastructure & access |
| Dataset access info | T1 | `T1` rows referenced by T5 | Hosting status, native resolution |
| Double-count flags | T5 / T2 | `double_count_risk` | A variable active here must not be active in M2 (guard) |
| Geographic context | T7 | admin / AEZ / farming-system masks | For per-unit summaries |

## 4. Outputs

| Output | Format | Path | Consumer |
|---|---|---|---|
| Standardised priority layers | COGs, 0–1 | `…/maps/characterisation/<var>.tif` | M4 (weighted into hotspots) |
| Raw priority layers | COGs | `…/maps/characterisation/raw/<var>.tif` | Variable detail raw-vs-transformed maps |
| Opportunity fingerprint | CSV | `…/tables/fingerprint.csv` | "Opportunity fingerprint" panel (coverage, rural pop, farms, production, farm size; share in opp space) |
| Problem-variable distribution | CSV | `…/tables/characterisation.csv` | "What this NbS can address" bars; "Risk to rural livelihoods" hazard profile |
| Cluster log | JSON | `…/tables/characterisation_cluster_log.json` | Variable Config; reproducibility |
| Run metadata | JSON | `…/characterisation_meta.json` | Double-count decisions, AOI, scenario |

## 5. Dependencies

**Upstream:** M1 (mask). May read M2's climate-risk surface to render the "risk to rural livelihoods" profile within the opp space.

**Downstream:** M4 consumes the standardised priority layers + cluster log. The wireframe Opportunity Space tab consumes the fingerprint and distribution tables. M5 reuses the problem-variable distributions to pair "problem present × response strength".

## 6. Sub-steps

1. **Priority variable assembly** — load T5 variables, harmonise to analysis resolution, clip to the opportunity-space mask. Generate resolution-audit rows.
2. **Correlation reduction** — cluster correlated priority variables per AOI (|r| > 0.7), one representative per cluster (reuse M1 §6.3); log membership. Reduction runs *within each theme*.
3. **Standardisation** — produce 0–1 layers per each variable's T5 normalization rule (method · direction · reference frame · clip). *(The normalization methodology is specified in `M4_hotspots.md` §9; M3 applies it.)*
4. **Fingerprint extraction** — within the mask: total area, area by suitability class, rural population, smallholder farms, production value, average farm size, and the share of each in the opportunity space.
5. **Problem-variable distribution** — per priority/hazard: share of opp-space land at each severity level (None → Very High), baseline and future, for the bars in the Opportunity Space panels.
6. **Per-unit summaries** — aggregate the above to ADM units for downstream ranking.

## 7. Variable Cards consumed

All T5 priority variables for the AOI, grouped by the four themes. Each carries its six-slot card; M3 produces the raw + transformed layers behind the Variable detail "raw-vs-transformed" maps for the priority/hotspot variable surface.

## 8. Variable selection — Ani's three principles

1. **Reduce** — thematic grouping (per T5 theme) + correlation clustering per AOI; one representative per cluster passes to M4.
2. **Source** — three-tier dataset preference; pulled into Python.
3. **Explain** — six-slot Variable Card metadata flows through to the UI.

## 9. Double-count guard

Variables here (T5) must not also be active in T2 (M2) for the same `nbs_id`. Common cases: poverty, GESI, adaptive-capacity proxies belong in M3/M4 (TTL priorities), not in M2 Mode-B vulnerability. The guard raises a validation error if a variable is active in both (see M2 §10).

## 10. Tests / acceptance criteria

- [ ] Reads all rules from T5/T1/T7; nothing hardcoded.
- [ ] Characterisation runs within the M1 mask only.
- [ ] Each priority variable produces raw + standardised layers; cluster log maps every variable to a representative.
- [ ] Fingerprint and distribution tables match the wireframe panel fields.
- [ ] Double-count guard passes against T2.
- [ ] Resolution audit includes all M3 inputs.

## 11. Definition of done

- [ ] T5 rows populated (variables, themes, normalization rules, double-count flags)
- [ ] All variables have access/upload + six-slot Variable Cards
- [ ] Pipeline runs end-to-end for agroforestry Sierra Leone
- [ ] Outputs sanity-checked against regional knowledge

## 12. Implementation notes (Python)

```python
def assemble_priorities(t5_rows, aoi, resolution, opp_mask) -> "xr.Dataset":
    """§6.1 — load + harmonise + clip priority variables to the opportunity space."""

def reduce_correlated(stack, threshold=0.7) -> "Tuple[xr.Dataset, dict]":
    """§6.2 — per-theme correlation clustering; reuse M1 logic."""

def standardise_priorities(stack, t5_rows) -> "xr.Dataset":
    """§6.3 — apply each variable's normalization rule (see M4 §9)."""

def extract_fingerprint(opp_mask, exposure_layers, admin_vector) -> "pd.DataFrame":
    """§6.4 — coverage, population, farms, production, farm size within the mask."""

def problem_distribution(standardised, opp_mask, scenarios) -> "pd.DataFrame":
    """§6.5 — share of opp-space land at each severity level, per variable × scenario."""
```

## 13. Open questions

1. Should M3 standardise (own the normalization application) or only assemble, leaving standardisation to M4? *(Current spec: M3 applies; M4 specifies + validates.)*
2. Which exposure layers are framework-default vs recipe-specific (rural pop, farms, production value, livestock)?
3. Future-scenario characterisation — characterise under baseline only, or baseline + future?

---

## Version history

- **v0.1** (June 2026) — authored to match the v0.6 wireframe Opportunity Space panels. Splits cleanly from M4 (M3 describes, M4 prioritises). Computed in Python (post native-GEE).
