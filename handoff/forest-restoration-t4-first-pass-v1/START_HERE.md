# T4 implementation brief

These are shared implementation instructions. The package's `developer_contract.json`
identifies its NbS, families, selected functions and unresolved decisions. No other
recipe's masks, weights, crop requirements or assumptions are inherited.

1. Read [the developer contract](developer_contract.json) and [table](developer_table.csv).
   Keep suitability scores, host gates, hard exclusions and operational evidence distinct.
2. Inspect `readiness` and [outstanding decisions](decisions.json). Missing functions,
   applicability or analytical policy are holds, not permission to invent defaults.
3. Use [dataset instructions](DATASET_INPUTS.md) to select and reconcile spatial inputs.
4. Implement [the contract](IMPLEMENTATION.md) in the developer repository and run its
   conformance examples before spatial testing. Pilot testing belongs to the developers.

The source evidence and analytical configuration remain authoritative in CIAT's repository.
Return evidence/methodology corrections upstream; regenerate rather than edit this bundle.

This generic brief does not establish recipe-specific policy approval. Any required new
family mapping, pooled function, transfer assumption or weight vector needs a recorded decision.
