# Implementing a T4 contract

Start with [the implementation task brief](START_HERE.md). The [developer contract](developer_contract.json)
is the interface; [method](METHOD.md) explains how evidence becomes configuration.

- Join by stable rule, family, variable, dataset and function IDs. Keep context and crop/species
  scope attached. A common variable name alone does not establish compatible evidence.
- Apply only explicitly selected, applicable functions. Preserve units, endpoint inclusivity,
  unknown gaps and reported domain. Do not fill a missing tail or fit an unreported curve.
- Read `run_contract.json` for approved aggregation and gate semantics. If no policy is
  execution-ready, stop execution and report the missing decision. A configured row weight,
  source importance weight or source count is not independent approval of an MCDA vector.
- Keep soft enabling factors in the operational module. Keep hard exclusions and eligibility
  gates separate from compensatory scores. Unknown inputs must remain distinguishable from zero.
- Match [conformance cases](conformance_examples.json) and `policy_conformance.json`, including
  boundaries, missing data and conflicting conditions. These tests do not validate spatial transfer.
- Record the package version and manifest hashes, target context, selected functions, input
  versions, transformations, resolution, weights and remaining flags in the run manifest.

An empty or blocked contract is a visible evidence/configuration gap, not a successful pilot.
