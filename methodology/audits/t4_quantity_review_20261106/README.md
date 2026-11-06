# T4 quantity and use review — 6 November 2026

Seven existing high-priority Hold cards now contain more specific, source-backed recommendations. These refine the completed 515-record source-check batch; they are not seven new extractions or human approvals. All 642 priority memberships, existing rainfall correction drafts, parked status and scientific records remain unchanged.

## Decisions prepared

- **Boers:** retain the strict <100 m runoff-transport definition and paired runoff-area/infiltration-basin geometry. Distance is not catchment area; no conversion to hectares or landscape exclusion is justified.
- **Worley:** retain cited-secondary large-drainage-area **and** low-gradient conditions as hydraulic-benefit planning evidence. Drainage density is a different quantity. A variable rename alone would not resolve purpose and family routing; the unsupported per-project/headwater interpretation should not be retained as a source claim.
- **Qiu:** retain the full 500 m disturbance buffer for marsh rehabilitation from cropland, including transportation, residential, industrial and mining classes. The earlier annotation was too broad: `built_up_areas` explicitly allows `boolean_or_distance`, so metres are not themselves a variable mismatch. A settlement-only layer would omit source classes. The buffer remains a study-specific planning choice, distinct from the separately discussed protected-area legislation.
- **Adham:** retain all runoff-depth classes, scores and printed labels, including the non-monotonic 9-to-8 change. The rainfall/aggregation period and upper tail remain unresolved.
- **Bera:** retain mean annual SWAT runoff for 2003–2013, all six class weights and separate criterion weight. Page 9 gives structure-specific preferences: high–very high for gully plugs, moderate–high for check dams, low–moderately low for farm ponds/percolation tanks, and low runoff for recharge/subsurface structures. The overall increasing map ranking is not a universal preference for every structure.
- **Jha:** retain the annual runoff/rainfall coefficient for normal year 2003, complete source classes, assigned feature weights, normalized feature weights and separate criterion weight.
- **Terêncio:** retain the decreasing Curve Number table exactly, with planning/allocation caveats and separate factor/group weights. Do not reverse the direction or equate CN with the later engineering runoff coefficient.

The four runoff records already preserve their full numeric source tables in `context.reported_values`. No missing-number restoration is required. `runoff_potential_index` permits `index_or_native`: the shared identifier is not inherently invalid, but native quantity, units, statistic, dataset and transformation must remain distinguishable. No automatic ontology split, pooling, scoring or calibration is proposed.

## Dashboard and review mechanics

Existing cards remain in `t4_source_checked_20261106`, priority High. Each question specifies the retained source interpretation and unresolved correction/binding work. Query records the request; Keep alone approves the unchanged stored record and does not apply a patch. All recommendations remain awaiting human review. No evidence correction, source disposition, family reassignment or recipe update is applied.

Dashboard: <http://localhost:9284/dashboard.html#review-priority=t4_source_checked_20261106>.

## Separate dataset follow-up

`binding_followup.json` records an existing inconsistency: T1 `scs_cn_runoff_composite` is titled HydroSHEDS Watershed Boundaries and River Network and points to the HydroBASINS GEE asset, while its note describes a composite SCS runoff surface. BIND contains no runoff-potential override. The existing runoff-catchment mapping cites five other evidence IDs, not these four. This requires a separate binding audit, not attribution of existing executable cutoffs to this batch. No dataset or mapping is changed here.

## Verification and bounds

All seven evidence fingerprints and source artifact hashes match the inspected records. Native stored quotes and supplementary excerpts were checked against the cited cached pages. Four runoff tables and three geometry/routing pages were visually inspected. Full source recommendations, contradictory labels, original lineage and unresolved endpoint/period semantics remain visible in `source_review_drafts.json`.

This is a bounded follow-up under the existing T4 review contract: quantity/proxy fidelity, contextual use and scientific plausibility. Historical instructions, extraction stamps, approvals, source/evidence registers, recipes, learning cursor and progress-ledger stages are unchanged. Independent review and final generator validation are recorded in `verification.json`.
