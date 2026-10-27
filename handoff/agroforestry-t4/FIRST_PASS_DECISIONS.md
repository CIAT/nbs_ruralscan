# T4 first-pass configuration decisions

**Approved by Pete — 27 October 2026. Analytical policy recorded; target applicability and input validation remain open.** Based on [developer-v0.1.1](developer-v0.1.1/README.md). Approval is encoded in `schema/recipes/agroforestry/T4_run_policy.csv`; source evidence approvals and published response functions are unchanged. Diego and Brayden implement the approved selection through the existing contract; pilot testing remains theirs.

The recommended first step is a **conditional planted-silvoarable terrain-and-soil comparison**, alongside system-specific host eligibility. It is not yet a complete global biophysical suitability model. The available numeric pools come from regional Indian models; using them elsewhere needs an explicit transfer decision. A country filter selects evidence or dataset context; it does not establish transferability.

## One decision table

Rows originally marked **new decision** below are now approved for this conditional comparison. Target transfer and technical input checks remain required. No repeated extract review is requested.

| Decision | Recommended choice | Rationale | Alternative | Effect on output / status |
|---|---|---|---|---|
| 1. First comparison scope | Planted silvoarable: slope, topsoil SOC and topsoil pH, subject to depth/unit checks and declared target applicability. Call output a **partial terrain-and-soil index**. | Three existing compatible scoping pools can be compared without claiming climate coverage or global calibration. | Choose a documented regional source model for its matching context; wait for a complete broader recipe. | Approved policy. No target selected yet; does not authorize a Haiti run or universal transfer. |
| 2. Numeric response choices | Compare the three `india_planted_scoping` pools, preserving step classes, source coverage and disagreements. Keep individual source profiles available as sensitivity alternatives. | Uses compatible evidence already assembled; does not pick the most favourable paper per pixel. | Select one source profile per criterion for the entire declared context, with justification. | Approved policy. Pool pH at 6 and slope at 25° remain unknown. Exact function IDs below. |
| 3. Incomplete curves | Add a missing continuation only when verified from the source, recording provenance. Never raise the best available class to 1 merely because 1 is absent. | A common score of 0.9 means very high; it is not a missing optimum. Missing source coverage differs from a missing extracted table continuation. | Author an explicit extrapolation policy as a separate assumption and sensitivity case. | Retain safeguard. Haile SOC continuation is already repaired; unresolved units and system scope remain visible. |
| 4. Combine criteria | Weighted linear combination (WLC) for the proposed partial index; run minimum-factor scoring as a separate sensitivity comparison. Keep legal exclusions and host gates outside the weighted sum. | WLC matches the current implementation direction and makes compensation visible; minimum tests whether one weak criterion dominates. | Minimum-factor baseline, with WLC as sensitivity. | Approved policy. Strong soil scores can offset weak slope under WLC; cannot under minimum. Zero response score is not automatically a legal exclusion. |
| 5. Baseline weights | For this three-criterion comparison only: terrain 50%, soil 50%; hence slope 50%, SOC 25%, pH 25%, if both soil criteria survive selection. | Equal group budgets prevent a group gaining importance merely because it has more measured variables. This is a transparent design baseline, not an estimated ecological truth. | Flat equal weights: ⅓ each. Compare both before adopting a baseline. | Approved policy. Use theme → group → criterion allocation when expanding. Recompute and record weights once per run after criterion/cluster selection, never per pixel. |
| 6. Evidence-based importance | Report each paper's raw weight, within-group importance and hierarchy-adjusted relative importance. Use compatible, lineage-deduplicated source panels for weight sensitivity; do not promote the mixed panel to default weights. | Published weights describe different model objectives and hierarchies, sometimes including operational factors. Frequency of use, importance and response agreement measure different things. | After panel compatibility is resolved, explicitly adopt normalized cross-study relative importance for the selected criterion set. | Retain separation. Existing equal slope/rainfall comparison remains approved only for that pair; it does not approve row 5. The 73.75/26.25 slope/rainfall diagnostic is a sensitivity result. |
| 7. Related variables and inclusion | Preserve theme and group as separate fields. Count unique study lineages per variable and per group, with named eligible-study denominator and review status. Select one representative per AOI correlation cluster, using fitness, depth, time and resolution. | Two measurements of the same construct must not gain two votes; SOC and pH are different soil properties and should not be merged merely because both concern soil. | Retain correlated alternatives in sensitivity runs. | Retain method. Adding proxies does not inflate group support. Dataset resolution alone does not decide quality. AOI clustering belongs to implementation. |
| 8. Climate and unassigned systems | Keep Nath climate profiles regional; keep Haile parkland and other unresolved system assignments explicit. Do not assume unassigned means planted silvoarable. | A regional precipitation zero can be inappropriate for dryland systems. Haile's planting-versus-regeneration scope remains unresolved. | Explicit, documented source-to-target transfer or an approved system-specific profile. | Genuine applicability decision remains. FMNR rainfall context does not yet supply an executable cutoff. The partial index must not be labelled full suitability. |
| 9. Other systems and operational module | Show configured host eligibility for FMNR, silvopasture, boundary and shaded-perennial systems where inputs allow. Keep soft operational factors in their own M2b/implementation module. | Host presence answers where a system can integrate; it does not establish complete biophysical suitability. Operational placeholders lack calibrated raw endpoints. | Supply approved system-specific response profiles and operational calibrations later. | Retain routing. Coffee/cocoa/other approved hosts combine by OR; local grazing confirmation remains required; boundaries remain placement zones/lengths. Unknown inputs stay unknown. |
| 10. Missing data and disagreement | Fixed criterion set; unknown required score makes the composite unknown. Publish valid-coverage and disagreement layers alongside scores. | Prevents a pixel appearing better simply because a difficult criterion is missing. A source-pool tie is not a missing raster value. | Separately approve bounded-score or tie-resolution sensitivity logic; never silently average the competing scores. | Retain current contract. No per-pixel renormalization. No extrapolation across gaps or artificial smoothing of pooled tails. |
| 11. Dataset and delivery readiness | Resolve climate CHELSA/WorldClim mismatch, native scale/band/depth and time contracts, legal-mask categories, and required local host inputs before executing affected rows. Freeze selected function fingerprints and policy in a versioned selection. | Dataset compatibility and reproducibility are necessary even when extraction is reviewed. | Leave affected outputs explicitly unavailable while delivering the working subset. | Technical work, not new extraction review. Continue using the existing dashboard's Evidence trail, Suitability & weights, Global synthesis, and Rules & method tabs. |

## What the choices change

These are synthetic criterion scores, not pilot results. All three examples assume required host and legal checks pass, all inputs are known, and the same three criteria are retained.

| Example | Slope score | SOC score | pH score | Proposed group-balanced WLC (50/25/25) | Flat WLC (⅓ each) | Minimum |
|---|---:|---:|---:|---:|---:|---:|
| A: weak slope, strong soil | 0.25 | 0.90 | 0.90 | 0.575 | 0.683 | 0.250 |
| B: strong slope, weak soil | 0.90 | 0.25 | 0.25 | 0.575 | 0.467 | 0.250 |
| C: mixed conditions | 0.75 | 0.50 | 0.90 | 0.725 | 0.717 | 0.500 |

Flat criterion weights give soil two-thirds of the budget because it has two criteria. Equal group budgets treat A and B equally. Minimum ignores the compensating strength. These differences are the policy choice to approve; none is demonstrated ecological truth.

Actual package responses were also checked with the numeric executor:

| Pooled criterion | Inputs → scores | Interpretation |
|---|---|---|
| Slope (degrees) | 3 → 0.90; 12 → 0.50; 25 → unknown; 45 → 0.25 | At 25°, zero-versus-positive evidence conflicts. At 45°, only Ahmad contributes. The return of a score is a coverage change, not evidence that steeper land improves. |
| SOC (g/kg) | 4 → 0.25; 8 → 0.50; 15 → 0.75; 25 → 0.90; 40 → 0.75 | Above Nath's reported range, Ahmad alone supplies the score. Retain coverage warning; do not smooth this into an inferred response. |
| pH | 5 → 0.75; 6 → unknown; 7 → 0.90; 7.45 → unknown; 8 → 0.50 | The pool retains tied medians as unknown; single-source intervals remain distinguishable from agreement. |

## Selection and implementation notes

Approved first-pass function IDs (target applicability remains separate):

- `pool:india_planted_scoping__slope`
- `pool:india_planted_scoping__soil_organic_carbon`
- `pool:india_planted_scoping__soil_ph`

Use their exact intervals, endpoint inclusivity, units and fingerprints from [developer_contract.json](developer-v0.1.1/developer_contract.json). Do not transcribe rounded values from this document into the recipe. The calculations above use `runtime.numeric.evaluate_numeric` with those published intervals. WLC examples use `0.5 × slope + 0.25 × SOC + 0.25 × pH`; minimum is the smallest of the three scores.

The approved schema policy records the analytical choices. For a target run, record scope, target applicability, criterion set, function selections, group/criterion weights, aggregation and unknown-value policy in versioned configuration. Validate against the [developer contract method](../../methodology/T4_developer_contract.md). Any unsupported configuration field needs an explicit format change, not a silently ignored extra key. Rebuild the package with provenance and conformance cases before Diego implements the selected run.

Source-importance calculations and limitations are documented in [T4 variable importance](../../methodology/T4_variable_importance.md); [source_importance.json](developer-v0.1.1/source_importance.json) preserves the model-specific diagnostics. Source importance is not the credibility weight used to combine response evidence.
