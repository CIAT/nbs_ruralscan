# M1 — Suitability → Opportunity Space

**Module spec sheet · v0.1 draft · May 2026**

| Field | Value |
|---|---|
| **ID** | M1 |
| **Module** | Suitability → Opportunity Space |
| **Owner(s)** | Pete Steward (operational lead) · Namita Joshi (variable content) · Benson Kenduiywo (QA/QC) |
| **Status** | Draft — based on Benson's v2 methodology plan + water-harvesting recipe |
| **Schema tables consumed** | T0 · T1 · T4 · T7 |
| **Schema tables produced** | (none — outputs are rasters + tables, not schema rows) |
| **Position in pipeline** | M0 (Setup) → **M1 (Suitability)** → M2 (Climate Risk) || M3 (Characterisation) || M4 (Hotspots) |

> **Source materials.** This spec is the I/O contract for the analytical pipeline Benson has already designed in his v2 methodology plan and demonstrated in the water-harvesting recipe. The spec doesn't add new analytical methods — it names Benson's existing work as Module 1 of the framework and defines the I/O surface so M2–M6 know what to consume.

---

## 1. Purpose

For a selected NbS and area of interest, M1 produces a **continuous suitability surface** expressing where the NbS could biophysically be implemented and is likely to function. The surface is:

- Continuous (0–1) — not binary suitable / unsuitable
- Classified into ordinal classes (very high · high · moderate · low · excluded) for visualisation
- NbS-specific — the variables and response functions vary by recipe
- AOI-specific — correlation reduction runs per AOI; the result reflects local conditions

M1 answers the TTL's first question: *"Where could this NbS work?"* — *prior to* layering on TTL priorities (which M3/M4 do separately).

## 2. Question answered

> *"Within this geography, where is the NbS biophysically feasible — accounting for terrain, climate, soil, land use, hazard exposure, and structural constraints — and how is feasibility distributed across the landscape?"*

What M1 explicitly **does not** answer:

- Where the NbS is *strategically desirable* given TTL priorities (M4)
- Where development outcomes are most concentrated (M3 + M4)
- What benefits the NbS delivers (M5)
- What comes next operationally (M6)

These are deliberately downstream so M1 stays NbS-specific and interpretable.

## 3. Inputs

| Input | Source | Schema | Notes |
|---|---|---|---|
| Selected NbS | M0 Setup | `T0.nbs_id` | Resolves to the recipe in `methodology/recipes/<nbs_id>.md` and schema rows in `schema/recipes/<nbs_id>/` |
| Area of Interest (AOI) | M0 Setup | `T7` row(s) | Country / admin unit / hydrobasin polygon |
| Analysis resolution | M0 Setup | (run config) | One of 10km / 5km / 1km / 500m / 100m. Default 1km. |
| Climate scenario | M0 Setup | (run config) | `baseline` and optionally one or more `future_*` |
| Suitability variables | Recipe + T4 | `T4` rows for this `nbs_id` | Each row defines the variable, the response function, the dataset, and the weight |
| Dataset access info | T1 | `T1` rows referenced by T4 | GEE asset IDs, hosting status, native resolution |
| Geographic context overrides | T7 | `T4.context_overrides` | AEZ-specific or farming-system-specific parameter sets |
| Variable Cards | Recipe markdown | Six slots per variable | Drives UI display; not analytical input but coupled |

## 4. Outputs

| Output | Format | Path | Consumer |
|---|---|---|---|
| **Continuous suitability raster** | Cloud-Optimised GeoTIFF, 0–1, single band | `pipeline/outputs/<pilot_id>/maps/suitability.tif` | M3, M4, wireframe, Colab |
| **Classified suitability raster** | COG, 5 classes | `pipeline/outputs/<pilot_id>/maps/suitability_class.tif` | Wireframe map; demo views |
| **Opportunity space mask** | Boolean COG (high + very-high cells) | `pipeline/outputs/<pilot_id>/maps/opp_space_mask.tif` | M3 (extracts characterisation vars within this mask) · M4 (constrains hotspot MCDA) |
| **Opportunity fingerprint table** | CSV | `pipeline/outputs/<pilot_id>/tables/fingerprint.csv` | Wireframe right-panel; M6 hand-off summary |
| **Sensitivity map** | COG (suitability variance under ±10% weight perturbation) | `pipeline/outputs/<pilot_id>/maps/sensitivity.tif` | Uncertainty section of the notebook |
| **Variable cluster log** | JSON | `pipeline/outputs/<pilot_id>/tables/cluster_log.json` | Variable Config tab in wireframe; reproducibility audit |
| **Weight derivation log** | CSV | `pipeline/outputs/<pilot_id>/tables/weight_log.csv` | AHP matrices, CRITIC weights, Entropy weights, α-reconciled final weights |
| **Resolution audit table** | CSV | `pipeline/outputs/<pilot_id>/tables/resolution_audit.csv` | Audit trail of which inputs were upsampled / downsampled |
| **Run configuration** | JSON | `pipeline/outputs/<pilot_id>/run_config.json` | Reproducibility — full record of the run |

The classified raster + the fingerprint table together are what the wireframe's Opportunity Space tab consumes.

## 5. Dependencies

**Upstream:** M0 Setup must have completed and emitted the run configuration (AOI, NbS, resolution, scenario, ingestion confirmation that all required datasets are accessible).

**Downstream:**
- M2 may run in parallel with M1 (independent), but M2's output is shown alongside M1's in the Opportunity Space tab.
- M3 reads the opportunity space mask from M1 to scope characterisation extraction.
- M4 reads the opportunity space mask from M1 to constrain the hotspot MCDA.
- M5 doesn't read M1 outputs directly but uses the same `nbs_id` to retrieve scorecard rows.
- M6 doesn't read M1 outputs directly — it's narrative.

## 6. Sub-steps

Eight named steps inside M1. Each has its own I/O contract:

### 6.1 Variable assembly

- **In:** T4 rows for `nbs_id`; T1 dataset references; AOI; resolution; scenario.
- **Out:** harmonised raster stack at analysis resolution; one band per variable.
- **Notes:** apply context overrides from T7 / T4.context_overrides. Generate the resolution audit table.

### 6.2 Fuzzy standardisation

- **In:** raster stack from §6.1; `T4.relationship_type` and `T4.relationship_params` per variable.
- **Out:** standardised raster stack (each band 0–1).
- **Inherited primitive:** five fuzzy membership functions from `../framework.md` (sigmoid · linear · Gaussian · bell · inverted sigmoid).

### 6.3 Correlation reduction (Ani's principle 1)

- **In:** standardised stack.
- **Out:** reduced stack (one band per cluster representative); cluster_log.json mapping every variable to its representative.
- **Algorithm:** pairwise Pearson correlation across all standardised bands; cluster variables with |r| > 0.7 (default; configurable); pick representative by highest variance unless `T4.is_cluster_default = true` flags an expert-chosen primary.

### 6.4 Weight derivation

- **In:** reduced stack; `T4.weight_default` per variable; AHP pairwise matrix from recipe (or auto-generated from CRITIC if expert weights absent).
- **Out:** weight vector + weight_log.csv recording AHP / CRITIC / Entropy / α-reconciled final weights.
- **Inherited primitive:** AHP + CRITIC + Entropy reconciliation from `../framework.md`. Default α = 0.4 (60% objective, 40% expert).

### 6.5 Structural exclusion masking

- **In:** reduced stack; exclusion mask layers (water bodies, settlements, strictly-protected areas, slope > 35°, soil depth < 25 cm — per recipe §7.3).
- **Out:** boolean exclusion mask.
- **Notes:** applied as a hard filter to the final surface (any cell in an exclusion class → 0 suitability).

### 6.6 Weighted overlay

- **In:** reduced stack; weight vector; exclusion mask.
- **Out:** continuous suitability raster (0–1).
- **Formula:** weighted linear combination per pixel: `S = Σ_j w_j × x_j` then masked.
- **Inherited primitive:** WLC pattern from `reference/R/spatMCDA.R`, ported to GEE Python in `pipeline/mcda_pipeline.py`.

### 6.7 Sensitivity analysis

- **In:** weight vector; standardised stack.
- **Out:** sensitivity raster (per-pixel variance under ±10% weight perturbation).
- **Algorithm:** N = 50 perturbed weight vectors (uniform ±10% around the reconciled weights); compute the WLC for each; per-pixel variance is the sensitivity layer.

### 6.8 Classification & fingerprint extraction

- **In:** suitability raster; AOI; T5 exposure layers (population, farming systems, production value).
- **Out:** classified raster (4 classes by quartile or natural breaks); opportunity space mask (top 2 classes); fingerprint.csv.
- **Fingerprint columns:** total area km² · area by class · share of country · rural population in opp space · smallholder farm count · production value · dominant farming systems · drought exposure stack · Δ vs future scenario.

## 7. Variable Cards consumed

All suitability variables for the selected NbS — defined in `methodology/recipes/<nbs_id>.md`. Each variable's six-slot card (What / Why / How to read / What it represents / Where it comes from / Membership function preview) flows through the pipeline as metadata so the wireframe can display it in the Variable Config tab.

Mandatory before M1 can run: every variable in T4 for `nbs_id` must have a populated card with all six slots.

## 8. Variable selection — Ani's three principles

M1 implements all three principles introduced by Ani:

1. **Reduce** — §6.3 above. Two-stage: thematic grouping (in the recipe) + correlation clustering (per AOI). One representative per cluster enters the MCDA. Cluster membership is preserved in cluster_log.json and shown in the UI.
2. **Source** — three-tier dataset preference (GEE catalog → community GEE → upload). Each variable's `T1.hosting_status` is checked at §6.1; missing assets trigger the ingestion sub-pipeline in M0.
3. **Explain** — every variable carries its six-slot Variable Card metadata through the pipeline. Outputs include the variable cards as a JSON sidecar so downstream displays can render them.

## 9. Climate scenario handling

M1 runs once per scenario. For each `scenario_type` in the run config (e.g. `baseline`, `future_ssp245_2050`), variables with `T4.has_future_projection = true` use the corresponding `T4.future_dataset_ids[scenario_type]` instead of the baseline dataset. All other variables use their baseline dataset.

Outputs include a Δ raster (`future_minus_baseline_suitability.tif`) showing where suitability shifts under the future scenario — central to Laurent's "act now vs delay" narrative.

## 10. What-if scenarios

For variables flagged `T4.is_scenario_candidate = true` (i.e. infrastructure variables a project investment could plausibly change — distance to road, electrification, market access), M1 can be re-run with the variable toggled off / removed from the MCDA. The Δ vs the default run is the "what-if" opportunity surface — e.g. "+12,400 km² becomes viable if road access were universal."

Implementation note: the what-if engine is a re-run of §6.4–§6.8 with a modified weight vector (representing the toggled variable's weight redistributed). Sufficient for scoping; not a full counterfactual analysis.

## 11. Tests / acceptance criteria

- [ ] Reads all analytical parameters from T0–T7; no hardcoded thresholds, weights, or dataset URLs in the pipeline code.
- [ ] Runs end-to-end on the agroforestry Sierra Leone pilot from a clean Colab environment.
- [ ] Outputs validate: all GeoTIFFs are COG-compliant; all CSVs have expected column headers; cluster_log.json is valid JSON.
- [ ] Resolution audit table flags every input with native vs analysis resolution; upsampling > 1 tier triggers a warning.
- [ ] Sensitivity analysis produces a finite variance surface (no NaN bands).
- [ ] Weight log shows AHP / CRITIC / Entropy / α-reconciled weights and the sum-to-1 check passes.
- [ ] Cluster log shows every input variable mapped to a cluster, with the chosen representative flagged.
- [ ] All variables consumed have populated Variable Cards in the recipe markdown.

## 12. Definition of done

For M1 to be considered "done" for a given NbS in a given AOI:

- [ ] Recipe authored and reviewed (`methodology/recipes/<nbs_id>.md` status ≥ draft)
- [ ] Schema rows populated (`schema/recipes/<nbs_id>/T4_*.csv`)
- [ ] All variables have GEE catalog / community GEE access or upload completed
- [ ] All Variable Cards have six slots populated
- [ ] Pipeline runs end-to-end without manual intervention
- [ ] Outputs sanity-checked against regional knowledge by a domain expert
- [ ] Documentation: notebook cells explain each step in plain language

## 13. Implementation notes for Claude Code

When porting `spatMCDA.R` to GEE Python (`pipeline/mcda_pipeline.py`), preserve the function structure so each sub-step (§6.1 – §6.8) is a separately callable function. Suggested signatures:

```python
def assemble_variables(nbs_id, aoi, resolution, scenario, schema) -> ee.Image:
    """§6.1 — fetch and harmonise variables for the NbS into a single multi-band image."""

def standardise(image_stack, t4_rows) -> ee.Image:
    """§6.2 — apply fuzzy membership functions per variable."""

def reduce_correlated(standardised_stack, threshold=0.7) -> Tuple[ee.Image, dict]:
    """§6.3 — cluster correlated variables, return reduced stack + cluster membership."""

def derive_weights(reduced_stack, ahp_matrix, alpha=0.4) -> dict:
    """§6.4 — AHP + CRITIC + Entropy reconciliation."""

def apply_exclusions(stack, exclusion_layers) -> ee.Image:
    """§6.5 — return boolean exclusion mask."""

def weighted_overlay(stack, weights, exclusion_mask) -> ee.Image:
    """§6.6 — WLC + mask."""

def sensitivity_perturb(stack, weights, n=50, scale=0.1) -> ee.Image:
    """§6.7 — return per-pixel variance under perturbed weights."""

def classify_and_fingerprint(suitability, aoi, exposure_layers) -> Tuple[ee.Image, pd.DataFrame]:
    """§6.8 — return classified raster and fingerprint table."""
```

Each function is independently testable. The pilot notebook calls them in sequence.

---

## Version history

- **v0.1** (May 2026) — initial draft. Lifts Benson's v2 methodology plan + water-harvesting recipe into the framework module structure. To be deepened in Session B (M1 deep dive).
