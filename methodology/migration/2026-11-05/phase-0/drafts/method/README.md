# Rural Scan methodology

Rural Scan helps World Bank teams scope where nature-based solutions could fit rural landscapes, what climate risks matter, and which people, production systems and development priorities overlap those opportunities.

It supports early investment scoping. It does not replace feasibility studies, engineering design, ecosystem-service modelling or full cost-benefit analysis.

**Status: proposed repository introduction.** The initial import is a pinned draft baseline. It is not an accepted analytical release or a runnable application. [CIAT/nbs_ruralscan](https://github.com/CIAT/nbs_ruralscan) remains the working authority during migration. Pending scientific decisions keep their original status.

## Start here

- [Understand the approach](handbook/start-here.md): concepts, seven modules and the evidence-to-rule chain.
- Inspect the data model: field specification, table structure and versioned configuration under `data-model/` once the approved first import is staged.
- Choose a recipe: per-practice guidance and accepted release links will be added after method review.
- Run the implementation: [RuralScan/runtime](https://github.com/RuralScan/runtime), initially preserving Diego's existing package and analytical pin.
- Inspect or extend evidence: the evidence workbench remains in CIAT until its explicit migration and replay tests pass.

## Repository boundaries

`method` owns concepts, schema definitions, approved analytical policies, recipe guidance, release acceptance and visual identity. `evidence` will own source records, claims, discovery/extraction/review operations and candidate compilation. `runtime` owns data access, computation and reproducible notebooks.

Definitions flow into evidence compilation. Reviewed candidate outputs become immutable accepted analytical releases, which runtime pins. A repository move does not approve a scientific value or update a runtime pin.

The initial snapshot contains project-authored configuration and metadata. Original CIAT MIT notice is retained. Dataset and publication access conditions remain with their sources. Contributor attribution must follow imported material; runtime has a separate unresolved reuse-terms decision.

See the [pinned source map and unresolved-reference index](data-model/baseline.md) for the exact baseline, file hashes and preserved holds.
