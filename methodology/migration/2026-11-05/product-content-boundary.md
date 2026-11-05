# Destination content boundary

Instruction recorded 5 November 2026: the new repositories must contain no project-management material, named project parties or governance documentation. This supersedes earlier migration-plan suggestions to put governance, contributor-role lists or project administration into the destination trees.

## Product repositories

`RuralScan/method`, `RuralScan/evidence` and `RuralScan/runtime` contain reusable technical material only: methodology, cookbook and recipes, data model, scientific configuration, visual assets, executable workflows, evidence, reproducible examples, tests and technical release information.

Exclude project plans, task boards, meeting notes, budgets, funding/contract narratives, deliverable administration, team assignments, named contacts, personal decision commentary, access/ownership administration and governance documents. Do not migrate this planning directory, project-specific AGENTS memory or internal handover/coordination records. No `governance/` directory or project-party/contributor-role roster is part of the target structure.

Write instructions by function and operation, not by named person or organization acting as a project party. Describe scientific limits, prerequisites, validation and reproducibility directly. Technical compatibility/release specifications belong with the data model and release artifacts; repository administration belongs outside the product repositories.

Scientific citations, provider names, required licence/copyright notices, immutable source URLs/hashes and technical standards remain part of technical provenance. Domain concepts such as governance/extension risk, review-state fields, scientific approval status and validated-method rules are not project governance; do not delete or change their semantics. Git authorship/history is retained, not rewritten by this presentation cleanup.

## Mixed source material

Classify every proposed import for both technical content and excluded administration. Whole-file copies are not appropriate where these are mixed.

- Rewrite prose and descriptive CSV notes into neutral technical language; retain the scientific rationale and unresolved status.
- For personal labels in optional draft metadata, leave the public field blank and retain an immutable link to the original source record rather than inventing a person, evidence ID or approval. Keep original named records in the existing source archive. Required provenance fields need a separately verified export mapping; do not blank them blindly.
- Preserve IDs, keys, schemas, numerical values, classifications, routing, approval/review states, dates, citations and active evidence history. No source claim or review decision is rewritten or removed from the working authority.
- Label edited references as derived copies. Upstream hashes must never be presented as hashes of the edited files.
- Validate structured differences field by field. A transformation of scientific values needs separate authorization; a content-boundary cleanup is not that authorization.

Current operational management, migration receipts, access/release administration and named accountability remain in the existing project workspace/notebook. Historical import receipts remain factual records; this instruction changes subsequent destination presentation, not what was previously imported.

## Acceptance

Before merging a destination cleanup or importing another tranche:

1. Inspect every destination file for excluded content, including embedded notes and examples.
2. Confirm retained named material is a citation, provider/standard identifier, required notice or immutable technical provenance rather than project administration.
3. Compare configuration and schema changes with the pinned source; only documented descriptive/personal-label fields may differ.
4. Check links and preserve honest draft/incomplete status. Do not replace migration narration with claims that unfinished tools already work.
5. Record the result and any remaining holds here in the existing project workspace, not in a new product-management folder.

## Initial cleanup audit

The first draft imports included mixed technical/admin content. The method cleanup removes personnel assignments, contact details, contract narrative and personal commentary from README/handbook/specification and descriptive configuration fields. The evidence scaffold introduction becomes a product description rather than a cutover plan. The [field-level diff](product-content-field-diff.json) records changes to descriptive fields and personal source labels in this existing workspace; it is not imported into a product repository. Original import receipts and source records remain unchanged.

The unchanged runtime fork also needs cleanup. Its [content audit](runtime-content-audit.csv), against `78fba87d88a6f1d1a308e06632fb7fec76032696`, identifies embedded contact/assignment/escalation text and named labels. It has no standalone management or governance document. Names also occur in public interfaces and output keys (`fp.pete`, `Overview.ciat`, `pete_*`, `ciat_index`, `ciat_package`); removing them requires the coordinated consumer/tests compatibility step in M16. This audit does not claim the runtime tree is already compliant. Existing code, pins, outputs and history remain untouched by the method/evidence text cleanup.

Cleanup pull requests are open, not yet merged:

- [RuralScan/method #1](https://github.com/RuralScan/method/pull/1), commit `747081661229d2598e6c2439c9774bb84b389c65`: technical introductions/specification and descriptive configuration cleanup.
- [RuralScan/evidence #1](https://github.com/RuralScan/evidence/pull/1): technical scaffold introduction only.

Validation compared all 5,133 configuration cells with the imported baseline: 29 descriptive/personal-label cells changed, plus three manifest note fields. Analytical values, IDs, review states, dates and manifest structure are unchanged; all 259 specification field definitions retain their names, types and requiredness. The licence is byte-identical. Independent review found no remaining material issue after corrections; whitespace checks pass. Runtime cleanup remains pending under M16.
