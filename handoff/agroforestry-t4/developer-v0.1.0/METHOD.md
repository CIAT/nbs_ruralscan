# T4 developer contract: evidence to executable configuration

Version: developer-v0.1.0. Prepared 26 October 2026 for agroforestry.

## Purpose and status

The developer handoff translates the reviewed evidence and recipe into a reproducible, inspectable configuration for spatial implementation. It supports dataset selection and response evaluation before a pilot is run. It does not certify that every published regional rule transfers to the pilot country, or that every configured dataset has a working download adapter.

The developer table is a **generated, non-authoritative view**. CSV registers and recipe tables remain the analytical source of truth; their JSON is generated through the schema tooling. Corrections belong upstream and then flow through regeneration. This contract adds no evidence approvals, changes no runtime implementation, and establishes no new ecological thresholds.

The earlier v0.1.x handoff is an evidence/configuration catalogue. The developer package makes function choices, unresolved inputs and execution roles explicit. A record being reviewed, a function being mathematically executable and a function being applicable to a target country are three different states.

## Reproducible chain

1. **Read the corpus registers and recorded decisions.** Keep source identity, page/locator, quote, claim scope, review state and citation lineage. Dropped records remain recoverable history. An unresolved review is not converted to approval by compilation.
2. **Classify each claim's contribution.** A source can establish variable use, direction, relative importance, a numeric response, a categorical condition or observed site context. These contributions are not interchangeable. An observed slope or rainfall range does not become a suitability boundary.
3. **Resolve the analytical concept.** Use the ontology's canonical variable and units, theme/group, agroforestry system and allowed scope. Keep soil depths, different climate periods and genuinely different measurements separate. Related proxies may share a group without becoming equivalent response inputs.
4. **Compile eligible response options.** Preserve source profiles and approved compatible pools; retain source/context applicability and all gaps. A cross-family reference is not an automatic default for each named agroforestry system.
5. **Select explicitly.** Record the chosen function/profile/pool identifier and any transfer decision. Where selection is absent or applicability unresolved, publish options and a blocking reason rather than choosing a convenient first row.
6. **Resolve dataset context.** Select the target-context binding and retain recipe fallback, asset/band, units, temporal support, resolution, preprocessing requirements and upload needs. Check that the selected data measure the variable required by the function.
7. **Export the developer table and supporting records.** Emit the readable CSV and equivalent JSON, function options/intervals, decision manifest and provenance hashes. Record source revision, selected scope and inputs so another developer can reproduce the package.
8. **Validate before spatial execution.** Confirm identifiers, selected function parameters, dimensions, canonical units and unknown handling. The consuming implementation then validates acquisition, alignment and raster calculations. Pilot testing remains a separate activity.

## Target country and evidence country are different filters

`--country HTI` identifies Haiti as the target for dataset-binding resolution. It does not assert that an Indian or Ethiopian response is valid in Haiti and must not silently choose such a response. Global fallback bindings and unresolved local inputs remain visible.

`--evidence-country 'India'` is an optional exact recorded-name filter, compared case-insensitively. Recorded country labels are split on semicolons, commas and pipes, then matched as complete tokens; this is not substring matching or an ISO-code conversion. Repeat the argument for OR-selection across countries. Use `--list-evidence-countries` to inspect available labels. Missing geography is unknown, not evidence that a source is global. This is not a climate-similarity model, transfer approval or substitute for applicability assessment.

The evidence filter narrows numeric source profiles and recomputes their compatible pools. It also filters the complete model-use cohort and importance inventory, so inclusion denominators refer to the same declared geographic selection. A typed threshold is retained only if **all** linked typed contributors match: the compiler does not partially recalculate a threshold from a subset of its contributors. Authored host gates, legal exclusions and operational scenarios remain unchanged even when references fall outside the evidence-country selection; the output explicitly identifies that distinction. A country-filtered package is therefore not a claim that every included design rule originated in that country.

`--context` supplies an additional registered T7/BIND context identifier and can be repeated. Dataset-context matching remains separate from evidence-country filtering.

The current corpus contains both country names and codes (for example `India` and `IND`). These are distinct recorded labels, not automatically harmonised. To include both, repeat `--evidence-country India --evidence-country IND`. The package exposes the complete label inventory and the matching result for every relevant evidence record. This conservative filter does not claim a complete country literature search. A future reviewed country-alias registry can replace exact labels without changing the target-country binding interface.

Country filters must be recorded separately in the decision manifest. Counts must identify their denominator and whether they describe the full compiled evidence inventory or the filtered subset. A filtered inventory must not be presented as the entire agroforestry literature base. Changing a filter cannot create new human review decisions.

## Developer table and related files

One row identifies a recipe mapping for a system and canonical variable, together with its selected response option when supplied. Distinct source options must not be collapsed into a variable-only lookup. Scenario/context selections must remain recoverable. The derived package should expose the following information directly or by stable links to its companion tables:

| Information | Required interpretation |
|---|---|
| Mapping/system/variable identifiers | Stable joins; theme and group are separate fields; shared evidence remains recognisable |
| Module and execution role | M1 numeric score, host gate, hard exclusion, operational scenario, or reference-only evidence |
| Dataset and binding | Target-context selection, recipe fallback, asset/band, unit, period, native resolution, transformation and local-input requirements |
| Function selection | Type, selected option/profile/pool ID, machine parameters or intervals, explicit applicability/transfer decision |
| Response meaning | Direction, score interpretation, domain, inclusive/exclusive endpoints, interpolation policy and unknown/gap handling |
| MCDA inputs | Configured weight and its status, grouping/representative information; any final run weights are explicitly distinguished |
| Evidence | Source/evidence identifiers, provenance links, review status, variable-use counts and numeric-rule contributors |
| Execution readiness | Missing selection, applicability, dataset or adapter requirements; never infer readiness from review approval alone |

`developer_table.csv` and `developer_contract.json` are the human/machine entry points. Supporting files are `function_options.csv`, `function_intervals.csv`, `evidence_accounting.csv`, `inclusion.csv`, `source_importance.json`, `synthesis_report.json`, `decisions.json`, `conformance_examples.json`, `run_contract.json` and `selection_template.json`. The package also includes `index.html`, `README.md`, `manifest.json`, `VERSION`, `METHOD.md` and `IMPLEMENTATION.md`, plus full-registry snapshots `datasets.csv`, `dataset_bindings.csv`, `variables.csv` and `practice_vocabulary.csv`. These registry snapshots provide join context; their presence does not mean every dataset or variable is selected.

The unchanged full-corpus `T4_suitability_mappings.csv` is included for provenance and comparison. **Never use that snapshot as the filtered, resolved developer contract.** Use `developer_contract.json` and its selected function identifiers for the compiled view.

The decision manifest records selections and unresolved choices. The provenance manifest records hashes and source revision. Neither is a new editable schema register. Function intervals must remain machine-readable rather than requiring developers to parse prose such as “low below 5”. The human view should show the same function as a small curve or interval table, with gaps visible.

`datasets.csv`, `dataset_bindings.csv`, `variables.csv` and `practice_vocabulary.csv` are unchanged registry snapshots for joining the contract to the wider methodology. They include other recipes' records; join by the identifiers in the developer table. Generation happens in a temporary directory and checks every input hash before publication. Changed inputs, stale recipes, invalid selections or attempted overwrite of a published package fail the build.

## Relationship functions and cross-paper harmonisation

The canonical response vocabulary is defined in [schema/spec.md](https://github.com/CIAT/nbs_ruralscan/blob/bd6a37f87d5628d0adc38f144af2c1b842becf9b/schema/spec.md#relationship-type-reference-relationship_type--relationship_params). A source may report a smooth curve, a threshold, a ranked categorical map or ordinal numeric intervals. The compiler must preserve that distinction. The existence of a generic sigmoid evaluator does not justify fitting a sigmoid to a paper that reports only classes.

For current ordinal numeric profiles, the approved common scale is very low 0.10, low 0.25, moderate 0.50, high 0.75 and very high 0.90. Explicit unsuitable maps to 0; explicit optimum maps to 1. These are documented design scores, not empirically calibrated probabilities. Source scores, source labels and harmonised scores remain distinguishable. Do not stretch a source's observed subset to fill 0–1.

Profiles retain their original contexts. Only an explicitly approved compatible pool can combine them. The existing harmonisation partitions responses at their breakpoints and evaluates a source-quality-weighted median set, with one independent origin receiving one vote. It retains disagreement and coverage. Tied medians or zero-versus-positive conflicts do not manufacture an executable scalar. See [the T4 generation method](https://github.com/CIAT/nbs_ruralscan/blob/bd6a37f87d5628d0adc38f144af2c1b842becf9b/methodology/T4_generation_method.md) and [worked harmonisation scenarios](https://github.com/CIAT/nbs_ruralscan/blob/bd6a37f87d5628d0adc38f144af2c1b842becf9b/methodology/examples/t4_cross_paper_harmonization.md).

Missing tails, internal gaps and conflicting shared boundaries remain unknown. Do not interpolate between classes or extrapolate beyond reported bounds unless the selected function explicitly defines that operation. A source's low suitability is not a legal exclusion. A favourable-only statement does not establish an unsuitable complement.

## Counts, importance and runtime weights

Four quantities serve different purposes:

| Quantity | Purpose | Must not be treated as |
|---|---|---|
| Studies using a variable/group | Describes inclusion within a stated eligible study cohort; group counts use the union of sources | Review completion or automatic MCDA weight |
| Source-quality/lineage weights | Reconcile compatible source responses while avoiding duplicate origin votes | Variable importance in a spatial run |
| Within-study relative importance | Describes emphasis relative to other inputs and hierarchy in that source model | Universal ecological importance or an automatic runtime default |
| Runtime MCDA weight | Combines selected criteria in a declared spatial run | Evidence strength or percentage of papers mentioning a variable |

The count denominator must be visible. “All three studies reviewed” means reviewed evidence of variable use exists for those studies; it does not claim every extract in each study is approved. Numeric-rule contributors are counted separately. Reporting-paper counts are not proof of independent origins.

The [variable-importance convention](https://github.com/CIAT/nbs_ruralscan/blob/bd6a37f87d5628d0adc38f144af2c1b842becf9b/methodology/T4_variable_importance.md) preserves raw weights, sibling comparisons, whole-model contributions and hierarchy-adjusted ratios. Incomplete or contradictory models retain alternatives. Existing source-relative importance diagnostics are not silently promoted to runtime defaults. The equal-weight baseline approved for the slope/rainfall comparison does not approve equal weights for every family or every possible criterion set.

## Aggregation baseline and design history

The original spatial methodological plan described a limiting-factor minimum for structural suitability and weighted combinations in later prioritisation. The current Python MCDA implementation and M1 module describe a weighted linear combination with separate exclusion masks. These are different analytical choices: a minimum is non-compensatory, while a weighted sum can compensate a low criterion score with higher scores elsewhere.

For developer integration, **WLC plus separate masks is the current implementation baseline**, not a newly ratified resolution of every earlier design statement. This package records the baseline and exposes the decision; it does not alter runtime mathematics or claim a new policy approval. Historical M1 text includes examples and infrastructure-scenario wording superseded by later evidence and module-routing decisions; it must not supply hidden thresholds or override the current recipe.

For a declared eligible criterion set J, the baseline score is `S(x) = sum(w_j * f_j(x))`, with non-negative weights summing to one over J. Establish J and its weight vector before evaluation. Do not change J per pixel or renormalise weights over whichever inputs happen to be available. The current numerical overlay propagates missing values. Report input/score coverage alongside the result; unknown is not zero and is not suitable by default.

Thematic grouping and AOI correlation analysis determine representative criteria before the final run weights are assigned. The developer table carries grouping and configured weights, but cannot certify AOI-specific redundancy or objective weights without spatial data. Hard legal exclusions and host eligibility gates remain explicit, distinct from compensatory scoring. Missing mandatory gate information is unknown. The consuming implementation must define and test precedence between known exclusions and unknown inputs, rather than rely on arithmetic multiplication by a mask.

## Module boundaries and output meaning

- **M1:** biophysical suitability responses, existing-system host eligibility and hard exclusions define opportunity space. Named systems have separate applicability and product types.
- **Operational feasibility / M2b Stream B:** road and market access, tenure, finance, extension and labour remain operational scenarios or flags. They appear in the T4 analysis package for developer completeness but do not enter the core M1 weighted score.
- **M2b Stream A:** risk to the investment is a separate hazard-exposure screen, not an additional suitability criterion.
- **M4:** priority/hotspot MCDA uses TTL priorities within opportunity space. It is not the same weight vector or evidence denominator as M1 suitability.

Boundary plantings produce placement zones or linear quantities, not planted pixel area. Crop-host gates use observed host distributions where configured; OR-combination across permitted crops does not establish their biophysical response. Field boundaries, local grazing confirmation and other required local inputs remain explicit requirements. Scoping outputs do not substitute for site-level feasibility validation.

## Acceptance and limitations

A useful handoff allows a developer to trace one row from evidence through selected response and dataset to an expected score without interpreting prose. Tiny synthetic input arrays should demonstrate score values, interval boundaries, gaps, host gates, exclusions and weighted-output behaviour. These are contract tests, not pilot validation.

The release is not execution-complete merely because its files generate successfully. Outstanding choices must remain visible: regional transfer/profile selection, dataset/band/unit reconciliation, legal-mask implementation, local host inputs and final criterion/weight configuration. The versioned package makes those choices reviewable without requiring another literature audit or another review interface.

## Selections, corrections and rebuilds

The emitted `selection_template.json` is valid JSON with an empty `selections` object and no instruction-only keys. A selection document has `contract_version: "0.1.0"` and a `selections` object keyed by `mapping_id`. Each entry declares `function_id`, `function_fingerprint`, `target_system`, `applicability_country` matching the requested target country, `applicability_note` and `decision_reference`; `runtime_weight` is optional. Use the emitted template and exact function fingerprints, not manually invented identifiers. Unknown fields are rejected. The fingerprint binds a decision to the inspected function content and prevents a stale choice from silently selecting a changed rule. Authored gates are selected automatically as authored; numeric responses require an explicit selection. Neither behaviour supplies automatic final weights or certifies that the spatial run is ready.

The compiler rebuilds the **full** evidence-derived corpus in temporary outputs and checks parity with the audited live T4 recipe **before** applying country filters. A stale recipe fails the build even if the chosen country filter would hide the changed records. This prevents an apparently successful export from concealing an unreconciled upstream change. Source registers and recipe files are not overwritten by this check.

To correct a claim, update its authoritative CSV record, provenance and review status through the established workflow. Regenerate/reconcile the recipe through `scripts/synthesise-recipe.py`, inspect the analytical diff and any newly required review, then regenerate typed schema JSON with `python3 src/nbs_ruralscan/schema_tools/generate.py schema`. Once the audited recipe and full-corpus synthesis agree, rerun the developer compiler into a new or empty output directory. Refresh selections against the newly emitted function options if fingerprints changed. Do not bypass parity by editing developer outputs or by narrowing the evidence filter.

This export does not reshape authoritative columns. Any schema-column change still requires the structure manifest and normal project change process. Deliberately unresolved data-access fields such as native unit, scale and temporal reducer remain null until the developers confirm actual asset metadata. Canonical response units alone do not establish an asset's storage scale or aggregation period.

## Verify a delivered package

Run `PYTHONPATH=src python3 scripts/build-t4-developer.py --verify PATH` against the matching source checkout; use `--root` if that checkout is elsewhere. Verification checks recorded manifest inputs against the current checkout and checks package-output hashes. It does not rebuild the package, acquire data or run the spatial analysis. The immutable code commit and content hashes identify the implementation and inputs used; a newer checkout can legitimately fail verification and should not be treated as the original build environment.

Hash verification establishes consistency with the recorded manifest, not authenticity of the underlying research or a new human approval. Evidence review, source verification and geographic-transfer decisions retain their separate recorded status. This release adds no new data extraction. It is a developer-ready interface and reproducible configuration package, **not an execution-complete spatial run**.

`conformance_examples.json` includes numeric response examples and present/absent/unknown input arrays for all seven host gates. These make response semantics testable without acquiring pilot rasters; passing them does not establish full data-adapter compatibility, legal-mask completion or real-world transfer validity.
