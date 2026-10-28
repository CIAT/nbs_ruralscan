# T4 developer contract

Start with [the implementation task brief](START_HERE.md), [developer table](developer_table.csv), [implementation notes](IMPLEMENTATION.md) and [method](METHOD.md). Use the existing Evidence Query dashboard for ongoing inspection; [offline table and plots](index.html) are a pinned package snapshot.

This package contains 0 configured mappings and 6 operational evidence-only rows. It is an implementation handoff, not a completed spatial run. Select response functions and record applicability before execution. Use row readiness for implementation state, reasons and next actions. Defined logic is not a validated spatial run. Legacy status/blockers describe response selection only.

- `developer_contract.json`: mappings, explicit function options, dataset bindings, host dependencies and readiness.
- `developer_table.csv`: same rows for inspection; nested fields are JSON, not free-text instructions.
- `function_options.csv` and `function_intervals.csv`: join by `(rule_id, function_id)`.
- `T4_suitability_mappings.csv`: unchanged full-corpus recipe snapshot; NEVER apply it as the filtered or resolved contract.
- `inclusion.csv` and `source_importance.json`: evidence diagnostics, not runtime weights.
- `conformance_examples.json`: expected numeric and host-gate responses for adapter tests; null means unknown.
- `run_contract.json` and `policy_conformance.json`: approved analytical policy and scalar aggregation/gate checks; target transfer remains required.
- `manifest.json` and `VERSION`: source revision, exact inputs, filters, selections and output hashes.

Developer implementation remains in Diego/Brayden's repository. This bundle does not fetch spatial data, alter review decisions, select a universal function, or run MCDA. CIAT source registers remain authoritative.
