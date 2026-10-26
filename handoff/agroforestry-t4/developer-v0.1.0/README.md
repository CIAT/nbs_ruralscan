# T4 developer contract

Start with [the table and function plots](index.html), [implementation notes](IMPLEMENTATION.md) and [method](METHOD.md).

This package contains 26 configured mappings and 12 operational evidence-only rows. It is an implementation handoff, not a completed spatial run. Select response functions and record applicability before execution. Blocked means an analytical or binding choice remains; conditional means the function is configured but input/adapter checks remain.

- `developer_contract.json`: mappings, explicit function options, dataset bindings, host dependencies and readiness.
- `developer_table.csv`: same rows for inspection; nested fields are JSON, not free-text instructions.
- `function_options.csv` and `function_intervals.csv`: join by `(rule_id, function_id)`.
- `T4_suitability_mappings.csv`: unchanged full-corpus recipe snapshot; NEVER apply it as the filtered or resolved contract.
- `inclusion.csv` and `source_importance.json`: evidence diagnostics, not runtime weights.
- `conformance_examples.json`: expected numeric and host-gate responses for adapter tests; null means unknown.
- `manifest.json` and `VERSION`: source revision, exact inputs, filters, selections and output hashes.

Developer implementation remains in Diego/Brayden's repository. This bundle does not fetch spatial data, alter review decisions, select a universal function, or run MCDA. CIAT source registers remain authoritative.
