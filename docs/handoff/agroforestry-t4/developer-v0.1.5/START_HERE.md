# T4 implementation task brief — Diego and Brayden

27 October 2026 · developer-v0.1.5 · work in progress

## Start here

Use [developer_contract.json](developer_contract.json) as the machine entry point and [developer_table.csv](developer_table.csv) for inspection. Pin the source commit in [manifest.json](manifest.json). The package contains the full evidence inventory, with no target country selected. The approved first-pass policy pins the slope/SOC/pH pools and 50/25/25 weights for a conditional partial terrain-and-soil index. It is ready for integration work, not a completed spatial analysis.

Evidence inspection stays in the existing dashboard: **Evidence Query → T4 analysis → Evidence trail / Suitability & weights / Global synthesis / Rules & method**. Review decisions stay in QA/QC.

## What the package contains

| Rows | Meaning | Immediate use |
|---|---|---|
| 10 numeric suitability mappings | Source profiles and compatible pools; explicit selection required | Implement numeric response dispatch and selection by function ID |
| 7 categorical host gates | Configured rules; input and adapter checks still required | Implement host masks, fractions and missing-value behaviour |
| 1 hard legal exclusion | Planted-system mask interface defined; target legal rules and coverage required | Supply assessed true/false/unknown exclusion; no IUCN category shortcut |
| 8 operational scenarios | Existing normalized endpoints are placeholders | Route to operational feasibility; do not execute placeholders as calibrated raw-input responses |
| 12 operational evidence references | Variable use, direction or importance without configured response | Retain for scenario design and implementation guidance |

These are 38 developer rows representing 26 configured mappings plus 12 references. The 19 blocked / 7 conditional / 12 reference-only statuses describe configuration readiness, not human-review completion.

## Implementation sequence

1. **Load and pin.** Read the generated contract and retain its source commit, filters, function fingerprints and evidence identifiers. Join by mapping/system/function, not variable name alone. Treat CIAT schema as read-only.
2. **Plan by role.** Dispatch numeric scores, host eligibility, legal exclusion and operational feasibility separately. Shared evidence is not inherited automatically by every system.
3. **Check response semantics.** Run [40 conformance cases](conformance_examples.json): 19 numeric functions and 21 host-gate cases. Numeric tests include exact boundaries, adjacent values and unknowns; gate cases cover present/absent/unknown hosts. JSON null means unknown, never zero. These are small-array adapter checks, not pilot validation.
4. **Resolve data access.** Use each row's binding and canonical input requirements alongside the developers' `dataset_access.csv`. Record actual asset/version, band, native units, scaling, temporal reducer, depth and resampling. Confirm the three climate bindings where CHELSA overrides recipe WorldClim. Check equivalence before using a response calibrated to a particular input.
5. **Record analytical selections.** Use [selection_template.json](selection_template.json), selecting exact function IDs and fingerprints with target-system/context applicability and a decision reference. Rebuild into a new directory. A regional source response is an option, not a global default.
6. **Define the run.** Fix the criterion set, representative variables, aggregation method and final weights before evaluation. Keep host gates and legal masks outside the weighted sum, and operational scenarios outside M1. Propagate missing required scores; no pixel-by-pixel weight renormalization.
7. **Pilot separately.** Diego's implementation owns raster acquisition, alignment and pilot testing. Report incompatible contract fields or failed conformance cases against the pinned package; do not silently repair analytical values in the runtime.

## Decisions and inputs still open

| Item | Proposed lead | Required result |
|---|---|---|
| Ten numeric response selections; five mappings have unresolved system applicability | Pete / domain review | Function and target-system/context decision; no automatic planted-silvoarable assignment |
| Approved partial-index policy; target applicability still open | Pete with Diego | Read `run_contract.approved_policies`: WLC baseline, minimum sensitivity, terrain/soil 50/50; validate target transfer and inputs before use |
| Climate binding differences and native asset metadata | Brayden with Diego | Validated band/unit/time/depth transformations and acquisition adapters |
| Field boundaries, farmland context, grazing confirmation and ungrazed forage management | Runtime team / local data providers | Inputs for the relevant host branches; unknowns retained where absent |
| Legal category mask and family coverage | Pete with runtime team | Explicit exclusion specification and adapter |
| Operational scenarios | Brayden with Pete | Raw-variable domains, direction and filter/flag rules; no automatic core-suitability weights |

Source importance is available, including whole-model shares and relative-to-equal-share diagnostics. These describe the papers' models and do not automatically set run weights. Inclusion counts likewise describe variable use, not weighting or review completion.

## Approved analytical policy

Use `run_contract.approved_policies` and per-row `approved_policy` for the agreed baseline. It is not a full biophysical model. Regional transfer remains required; a changed or missing function fingerprint holds the policy. Keep source-importance diagnostics separate from these design weights. Legal/host masks carry no weight; retain eligible fraction separately. Country-specific selections remain unset until applicability is recorded.

## Change from previous developer package

Haile SOC now includes the printed high and very-high continuation bands, with scores 0.75 and 0.9 above the earlier low/medium bands. Original extraction review status remains unchanged; correction provenance records source pages and fingerprints. Assumed percent units, the overlapping 0.7 boundary, system applicability and source-weight disagreement remain explicit. The package adds no new extraction approvals or geographic-transfer decisions.

Package version is 0.1.5; machine contract/selection format is 0.2.0. Six additional `policy_conformance.json` cases check aggregation, gates, host fractions and unknown propagation. Earlier packages remain immutable. See [implementation guide](IMPLEMENTATION.md) for build/verification commands and [method](METHOD.md) for the full corpus → compiler → developer-table chain.

## Soil inputs for the first pass

Read [dataset input assumptions](DATASET_INPUTS.md). The policy criteria carry an unselected 0–30 cm SoilGrids proposal with exact layer weights, operation order, limitations and sensitivity checks. Record any adoption in the implementation run manifest with a decision reference; the build does not activate it. Laboratory equivalence and geographic transfer are not implied. The same proposal is visible in the existing dashboard, under Global synthesis.

## Start with the five-row policy scope

The policy's `implementation_readiness` counts its three numeric criteria and two gates. Slope and gate interfaces are defined; SOC and pH are provisional because input depth/measurement assumptions remain. Use row `readiness.next_actions` to separate methodology decisions, target-team assessments and implementation checks. The wider 38-row catalogue includes unselected alternatives and operational references; it is not the minimum criterion set for this first pass. Every `readiness.execution_ready` remains false until a separately documented spatial implementation is validated.
