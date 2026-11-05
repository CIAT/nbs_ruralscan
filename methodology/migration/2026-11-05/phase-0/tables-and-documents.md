# M02 table and document ownership audit

Audited source: CIAT/nbs_ruralscan `dd80226700432e9abd4aa9262262b9ad5ad6dfd5`. Read-only source audit; retained outputs are in this Phase 0 packet. No repository files, registers, decisions, branches or external systems were changed.

## Files

- `table-ownership.csv`: complete 74-file schema CSV schedule. Every row includes source hash, exact header, row count, current authority, proposed canonical owner/repository/path, authorship, dependencies, code evidence, scientific/rights holds and import disposition.
- Code references in the table schedule are literal filename/stem matches; they are not proof of complete dynamic dependency closure.
- `t4-row-ownership-triage.csv`: all 59 current T4 rows with observed generator/gate markers and carried design fields. This is triage, not an approved split.
- `first-import-manifest.csv`: exact 15-file foundation candidate: MIT, spec, manifest, four shared tables, FAM/VONT/BIND and five recipe T0s. No compiled response tables, source/evidence records, PDFs, snapshots, screenshots, raster datasets or old workbooks.
- `document-ownership.csv`: field-specific carry/rewrite/history decisions for concept, module, recipe and method documents.
- `inventory-summary.json`: coverage and authority counts.

## Key decisions and blockers

1. **74 CSVs accounted for; 44 manifest-covered file headers conform.** Header checks verify required columns and reject unexpected columns; they are not full content/FK/scientific validation. Remaining30 files include lookups, external legends, exploratory inventories and historical snapshots outside the main manifest.
2. **Proposed file homes:33 method,35 evidence,6 unresolved T4.** FAM/VONT/BIND and XW/BANDS are method definitions/configuration. SRC/EV/SRCH/TOOL are evidence records. Evidence-ID direction exceptions are evidence QA. WOCAT source-field mappings belong with the evidence adapter while consuming pinned method vocabulary. Scorecard display/meaning policy remains method-owned and consumed by one evidence workbook renderer.
3. **All T4 mapping files held.** Agroforestry has7 gate markers,9 legacy/design markers and10 compiled markers; other populated recipes contribute33 compiled markers. Even generated rows carry authored weights/scenario fields from previous T4. Splitting by filename or by `Reconciled from` alone loses authority. Empty forest/mangrove CSVs are not proof that extraction or recipes are complete. First define explicit authored inputs, compile full corpus, compare with pinned baseline before filters, and adjudicate semantic differences.
4. **Numeric compilation policy is mixed at field level.** Per-EV adjudications and source quotations belong in evidence, while reusable harmonization/score conventions need method ownership. Keep this file held until that extraction is deliberate. The general convention must not be independently editable in both repositories.
5. **T4 run policy is authored but function-bound.** It contains function IDs/fingerprints plus approved weights. Preserve the accepted-function binding as a release contract; do not make evidence compilation consume an accepted output it is currently generating.
6. **The15-file first tranche is a reviewable definition baseline, not an accepted scientific or executable release.** New `README.md`, `handbook/start-here.md` and `data-model/baseline.md` explain scope, three authorities, statuses, version pins and what is held. The start-here guide is the initial concept entrypoint; the larger concepts/cookbook rewrite remains M11–M13. These are new/reconciled prose, not wholesale source copies. Missing mangrove T0 prevents a closed FAM→T0 definition set: two FAM rows refer to mangrove_restoration without a recipe T0 CSV. Resolve through an approved method change or explicitly keep it a draft baseline; never invent identity rows during migration.
7. **Pending status cannot become approval.** VONT164rows:68canonical,31pending_review,18pending,45blank,2rejected. Pending ratified_by cells: XW53/89, design_weights6/9, effect_locus11/12, comparator_policy2/10, WOCATimpact26/27 and hazard13/14. BANDS also embeds pending ratification in prose. These facts block an unqualified accepted release, not necessarily a clearly labelled baseline import.
8. **Rights-safe scope is narrow.** Preserve CIAT MIT notice and contributors for project-authored text/configuration. T1 includes restricted/noncommercial/proprietary external datasets; copying their metadata does not copy or license data. Codelists, WB income lookup and IPCC confidence adaptation need explicit source/version/attribution/reuse basis. EV quotes and numeric-policy applicability quotes require source-level publication treatment. Existing public repository presence is not a blanket third-party reuse license. No third-party payloads enter the first tranche.
9. **Generated T3/T6/T6E CSVs remain compiler artifacts.** Mechanism/conditionality prose comes from `T3T6_prose.json` and is reapplied only against matching EV IDs. Candidate authority is evidence; method acceptance references immutable bundle hashes. No hand-edited second CSV authority in method.
10. **Preserve history without promoting it.** CV sheets are legacy text prevalence, not current verified support. Deferred snapshots partly overlap restored live records. Seed T3/T6 CSVs still feed legacy progress comparisons but are not synthesis inputs. Archive by SHA or transfer immutable historical records only after rights/provenance review; no blanket restore.

## Minimum first import acceptance

- Confirm proposed ownership only; keep scientific approvals distinct and status fields intact.
- Import the15 exact paths/hashes only after the orchestrator's file allowlist approval; establish source/destination map and working documentation links.
- Include new scope/status navigation and the CIAT MIT notice. Preserve Benson/Diego attribution when their material is later imported; do not import runtime stubs in this tranche.
- Pin definitions and external provenance references; migrate no active canonical writer yet. Method baseline must not independently edit the live CIAT records while review continues.
- Resolve missing mangrove T0 before claiming closed FK conformance; report draft/pending/rejected configurations explicitly.
- No T4 mappings, T4 run policy, per-EV numeric adjudications, compiled T3/T6/T6E outputs or third-party artifacts in this initial15-file list.

This audit used local headers, rows, manifest FKs, script writers, concrete readers, project license and method documents. It did not run generators, query live data providers, declare scientific acceptance or certify external copyright permission.
