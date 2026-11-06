# Remaining T4 review through the dashboard

6 November 2026. Nine explicit Keep decisions (eight reviewed cards plus elevation)
applied through normal review handling. All 6,369 evidence rows and all source payloads
preserved. See `../t4_followup_20261106/eight_plus_elevation_application.json`.

## Dashboard queues

Existing priority controls now expose the remaining **636 records from the bounded
5 November triage**, without asserting this is the total future project workload:

- `t4_mapped_claims_20261106`: 64 claims referenced by existing mappings, across 21
  sources. Source passages checked; 23 Keep proposals, 39 Hold/correction proposals,
  two wrong-practice soft-drop proposals. None of these proposals is applied. High
  priority highlights the 41 Hold/Drop proposals. Each card explains source facts,
  encoding or interpretation concerns, and the exact proposed decision.
- `t4_source_checks_pending_20261106`: 450 records awaiting agent source-purpose and
  semantic checks. Not labelled ready for human approval; no fresh verification claimed.
- `t4_species_crop_20261106`: 65 records in the separate species/crop lane, with scope
  preserved. Source checking remains pending for this new batch.
- `t4_held_parked_20261106`: 57 existing holds/parked records; no action requested and
  no practice reopened. These remain visible as gaps, not an approval queue.

Use `dashboard.html#review-priority=<batch_id>`. Existing To review / Waiting for answers /
My reviewed queues and decision controls remain authoritative. Cards retain native
quotes and full source values. Section-based web sources show their locator instead of
inventing a PDF page. Existing six-item wetland priority batch is preserved.

## Review boundary

Keep retains the extraction at its stated scope; source facts, numeric source profiles,
planning geometry and final executable recipes remain distinct. Preserve complete
quantitative tables/ranges for compatible-source synthesis. No source must establish
the global rule alone. A source-specific context is not itself a defect. Actual
mis-encodings, wrong statistics, omitted classes and source criticisms remain explicit.
No remaining record has been automatically approved, dropped, reclassified or mapped.
Existing recipes were not rewritten from unapproved diagnostics.

Current-rule clarification is in extraction v1.9.8 and shared T4 contract. No historical
evidence restamped. Agent proposals are traceable in `priority_source_checks.json`,
with source pages, artifact hashes where supplied, and current evidence fingerprints.
This is a bounded source check, not a new extraction sweep or full-publication audit.

## Source-check findings to inspect first

Examples include seasonal rainfall encoded as annual, source rank classes used as hard
limits, a soil-depth claim pointing to the wrong page, generic conservation agriculture
without a harvesting structure, and a sand-dam paper questioning the very thresholds
stored as its endorsed optimum. Source-profile retention does not waive these defects.

## Recipe application

Only the three agroforestry source-support counts changed in the authoritative T4 CSV
(NDVI, elevation and slope each +1). No response parameters, scores, exclusions, weights
or dataset bindings changed. Approved-only trials for forest restoration, riparian
buffers and water harvesting produced no new mappings; existing riparian/water-harvesting
CSV rows were preserved for the explicit priority review rather than deleted by a rebuild.
Full source tables/recommendations remain available for subsequent compatible synthesis.

## Validation and local review

1,305 tests pass after rerunning one packaging test with the new audit-note files
included in the tracked input snapshot; 82 focused tests also pass. Lint, formatting,
core types, generated-data synchronization, schema structure and T4 coverage pass.
Independent review confirms nine metadata-only approvals and exact queue membership.
Native browser check shows all 64 priority cards and the four distinct queue filters.
No new dashboard decisions were submitted during verification.

Local prepared queue: http://localhost:9284/dashboard.html#review-priority=t4_mapped_claims_20261106
Choose your reviewer handle, then use each card's Keep, Drop or Query controls. The
current shared live site gains these queues when this branch is merged; local preview
is available now. `verification.json` records checks and the resolved test-fixture issue.
