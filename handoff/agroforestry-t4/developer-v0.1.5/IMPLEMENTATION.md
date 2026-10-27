# Agroforestry developer package: integration guide

Updated 27 October 2026. Package version: `developer-v0.1.5`; contract/selection format: `0.2.0`.

## Integration boundary

This package supplies a repeatable corpus-to-configuration handoff. It does **not** replace Diego and Brayden's runtime, define their repository layout, or require a new pipeline. Authoritative analytical configuration remains in CIAT registers and schema CSVs. The developer table, function options/intervals and decision manifest are generated views for selecting and checking the configuration a runtime will consume.

Start with [the implementation task brief](START_HERE.md). Read [the methodology contract](METHOD.md) for evidence eligibility, context transfer, functions, weighting and unknown handling. Inspect evidence in the existing dashboard's **Evidence Query → T4 analysis** subtabs. Versioned HTML files are offline snapshots, not additional live review queues.

## Current implementation context and verification limits

The team screenshot supplied on 26 October 2026 describes a newer private fork/local rewrite. Its proposed interfaces include:

- notebooks such as `notebooks/01_agroforestry.ipynb`;
- `models.py` with `Request`, `RunManifest`, `RunResult` and `JobStatus`;
- `schema.py` to load an NbS and family;
- `data.py`, `cache.py`, `mcda.py` and module steps such as `steps/m1_suitability.py`;
- `pipeline.py` for planning/running, and `outputs.py`;
- a read-only schema copy pinned by a `VERSION` commit, with shared T1/T2/T5 and recipe T0/T3/T4/T6;
- developer-owned `dataset_access.csv` for access locations and scale fixes.

These are team-reported design details, not a code audit of the private rewrite. Align the handoff to this boundary; do not rebuild those components from this guide. Whether the newer implementation already supports each contract item must be checked against its actual revision.

The public repository was inspected at the fixed revision below. It is **historical compatibility context**, not evidence of defects in the newer implementation:

- [Public snapshot b1cc1dc5dc4556a4c3908a9684d151988e1bc05c](https://github.com/dagudelo30/nbs-ruralscan/tree/b1cc1dc5dc4556a4c3908a9684d151988e1bc05c).
- [Historical suitability implementation](https://github.com/dagudelo30/nbs-ruralscan/blob/b1cc1dc5dc4556a4c3908a9684d151988e1bc05c/src/nbs_ruralscan/runtime/suitability.py).
- [Historical fuzzy-function implementation](https://github.com/dagudelo30/nbs-ruralscan/blob/b1cc1dc5dc4556a4c3908a9684d151988e1bc05c/src/nbs_ruralscan/runtime/fuzzy.py).

The public snapshot's variable-oriented rule selection and earlier function support motivate the checklist below. They must not be reported as current private-runtime behaviour.

## Build and deliver

The compiler is `scripts/build-t4-developer.py`. Run from the repository with `PYTHONPATH=src`. `--root` defaults to this repository and can explicitly identify another complete source checkout; `--nbs` defaults to `agroforestry`. The output directory must be empty or new.

First build an options package without a selection:

```bash
PYTHONPATH=src python3 scripts/build-t4-developer.py \
  --nbs agroforestry \
  --output /tmp/t4-developer-options \
  --country HTI
```

Inspect `index.html`, `function_options.csv` and `selection_template.json`. Fill a selection document using the exact function IDs and fingerprints, then build the selected package into a different empty directory:

```bash
PYTHONPATH=src python3 scripts/build-t4-developer.py \
  --nbs agroforestry \
  --output /tmp/t4-developer-selected \
  --country HTI \
  --selection path/to/selection.json
```

The emitted `selection_template.json` is valid JSON with empty `selections` and no instruction-only key. A completed selection has `contract_version: "0.2.0"` and `selections` keyed by mapping ID. Each entry requires `function_id`, `function_fingerprint`, `target_system`, `applicability_country` matching `--country`, `applicability_note` and `decision_reference`; `runtime_weight` is optional. Unknown fields are rejected. Authored gates select their authored rule automatically. Numeric responses require explicit selection. A selected function is not a declaration that datasets, adapters or final weights are ready.

For an explicitly narrowed evidence view, add `--evidence-country 'India'`; repeat for an OR-filter. List exact available recorded names with `--list-evidence-countries`. Matching is case-insensitive on complete country tokens split by semicolon, comma or pipe. It is not an ISO-code conversion. This differs from `--country HTI`: Haiti controls target binding context and never filters studies. `--context` can be repeated for additional registered T7/BIND identifiers. None of these options approves geographic transfer.

Evidence-country filtering narrows numeric profiles and recomputes compatible pools, model-use cohort/inclusion and source importance. Typed thresholds survive only if all their linked typed contributors match; there is no partial threshold recalculation. Authored host gates, legal exclusions and operational scenarios remain unchanged, explicitly labelled even when references are outside the evidence filter. Omit this filter for the full eligible inventory.

| File | Developer use |
|---|---|
| `developer_table.csv`, `developer_contract.json`, `index.html` | Readable table, machine contract and browser inspection |
| `function_options.csv`, `function_intervals.csv` | Explicit response alternatives and machine-readable intervals |
| `selection_template.json`, `decisions.json`, `run_contract.json` | Choice template, recorded decisions and execution requirements |
| `evidence_accounting.csv`, `inclusion.csv`, `source_importance.json`, `synthesis_report.json` | Evidence dispositions, study-use counts and importance diagnostics |
| `conformance_examples.json` | Numeric response cases and present/absent/unknown arrays for all seven host gates |
| `datasets.csv`, `dataset_bindings.csv`, `variables.csv`, `practice_vocabulary.csv` | Full-registry snapshots for joins; not a list of selected run inputs |
| `T4_suitability_mappings.csv` | Unchanged full-corpus recipe snapshot for provenance; never the filtered/resolved execution contract |
| `README.md`, `manifest.json`, `VERSION`, `METHOD.md`, `IMPLEMENTATION.md` | Provenance, immutable code commit, input/output hashes, version and consumer documentation |

The compiler rebuilds the full evidence-derived corpus and checks parity against audited live T4 **before filtering**. A mismatch fails rather than silently exporting changed analytical rules. Correct upstream CSVs/review records, run the existing recipe synthesis/reconciliation workflow, inspect its changes and regenerate schema JSON. Then build into a new empty output directory and refresh selections if function fingerprints changed. Do not repair mismatches by editing the derived developer table. This workflow adds no authoritative schema columns.

Native asset unit, scale and temporal reducer may deliberately remain null pending confirmed data-access metadata. Do not derive those values from the canonical unit by assumption. Record confirmed transformations through the developers' data-access/run-manifest interface.

Verify a delivered package against its source checkout without rebuilding:

```bash
PYTHONPATH=src python3 scripts/build-t4-developer.py \
  --verify handoff/agroforestry-t4/developer-v0.1.5
```

`--verify PATH` checks manifest inputs against the current checkout and package-output hashes. Use `--root` to identify the matching source checkout when necessary. A changed checkout may correctly fail verification. Verification establishes manifest consistency, not research authenticity, evidence approval, transfer approval or a successful spatial run. The immutable code commit and hashes support reproducibility; they do not replace scientific review.

This is a developer-ready contract, not an execution-complete spatial analysis. No new data extraction is included. The conformance examples check response semantics without acquiring pilot rasters; dataset adapters and actual pilot execution remain developer work.

Commit the package through GitHub with its source revision and selection manifest. Preserve prior versions. Do not distribute a second editable table that can diverge from the schema.

The published v0.1.5 package leaves target country unset and includes the full evidence inventory. Rebuild with the intended country and explicit selections when preparing a run. Compared with v0.1.0, it restores Haile's printed SOC continuation bands and records their separate correction provenance. It records the approved conditional analytical policy and weights, without granting human extraction approvals or geographic transfer. Package version and contract format version are recorded separately in the manifest and `VERSION` file.

## Proposed responsibilities

| Component | Methodology handoff | Developer implementation |
|---|---|---|
| Evidence and source interpretation | Maintain reviewed claims, scope, lineage, response options and applicability limits | Retain identifiers and status in run provenance |
| Analytical schema | Maintain CSV source, generate JSON, publish pinned revision | Consume read-only pinned copy; record VERSION/source commit |
| Dataset choice | State canonical variable, preferred/contextual dataset, units, meaningful resolution and constraints | Resolve available location through `dataset_access.csv`; acquire, cache and validate scale/band metadata |
| Response selection | Publish explicit function IDs, intervals/parameters and open transfer choices | Pass selected ID through request/run manifest and evaluate without guessing |
| Raster processing | State derive-before-aggregate and domain requirements | Implement alignment, derivation, resampling and nodata behaviour |
| MCDA | State module separation and distinguish configured weights from evidence statistics | Fix eligible criterion set, validate run weights and record clustering/weight decisions |
| Validation | Provide reproducible package and small expected-response examples | Test adapters and end-to-end pilot runs; report incompatibilities against pinned inputs |

This is a proposed division of work, not a claim that every component has been accepted or implemented. Diego owns pilot implementation/testing; coordinate dataset access and risk-module integration with Brayden's implementation. No changes to their runtime are made by generating this package.

A reported local → Hugging Face → GEE access sequence describes how the implementation obtains an asset. It does not change methodology's fitness-for-purpose and dataset-quality selection. An available local copy is not automatically a better scientific dataset. Preserve both analytical dataset identity and actual retrieved asset/version.

## Compatibility checklist for the newer implementation

1. **Join by mapping, system and selected function ID.** Several source profiles may exist for one variable. Shared reference rows must not override family-specific mappings or be inherited silently.
2. **Support the selected response representation.** Ordinary piecewise points and ordinal interval profiles are different payloads. For profiles/pools, preserve interval endpoints, score meaning, gaps and unknown regions. Reject unsupported representations clearly rather than using a generic linear fallback.
3. **Keep dataset selection and response selection separate.** Target-country BIND resolution does not approve transfer of a regional curve. Check selected dataset band, canonical unit, temporal aggregation and soil depth against the function input.
4. **Carry module/role into planning.** Numeric M1 scores, host gates, hard legal masks and soft operational scenarios require different execution paths. Operational rows must not join the core M1 weighted stack merely because they appear in the same T4 package.
5. **Keep the criterion set fixed for a run.** Validate final weights over that declared set. Missing pixel scores remain unknown; do not renormalise weights over available pixels. A source-use percentage or source-quality weight is not a criterion weight.
6. **Make mask and unknown precedence explicit.** Distinguish known legal exclusion, absent host, unknown mandatory input and numeric zero suitability. Validate these cases with small arrays before raster runs.
7. **Record actual data transformations.** Slope is derived before aggregation; host fractions retain their meaning; categorical classes require a crosswalk. Document unit/scale fixes from `dataset_access.csv` in the run manifest.
8. **Retain provenance.** Include package version, schema commit, input hashes, target/evidence filters, selected function IDs, applicability decisions, actual asset versions and run weight policy.

## What can proceed, and what still needs a decision

Developers can use the generated inventory to inspect/select datasets and implement supported response evaluators immediately. An unselected row remains a selectable option, not a default executable criterion. Any explicitly selected, applicable option still needs a valid data adapter and input coverage before spatial execution.

Outstanding items remain visible in the package: climate recipe/BIND reconciliation, family applicability of shared numeric profiles, target legal rules and mask coverage, local host inputs, and final criterion/weight choices. These are not all literature-review tasks. Some are methodological selection decisions; others are adapter requirements. The implementation should surface their recorded status rather than invent a missing value or ask the reviewer to approve the same extraction again.

Current CIAT numerical MCDA uses WLC with separate masks, while the original plan also described a structural rule-of-minimum. Treat this as a documented design evolution requiring an explicit consumer-facing choice, not two interchangeable algorithms. This handoff does not ratify a new aggregation rule or change the newer private implementation.


Approved first-pass policy is included in `run_contract.approved_policies` (contract format 0.2.0). Read its pinned functions, fixed criterion set, group/criterion weights and applicability hold before creating target selections. Run `policy_conformance.json` alongside numeric/gate conformance examples. These scalar cases do not authorize geographic transfer or a pilot run.
