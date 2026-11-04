# ElKadiri effect recovery — bounded batch, 2026-11-04

Ruleset v1.9.4. Staging only, two unapproved units from one primary modelling study. This is canonical-source reuse from the previous T4 lane into T3/T6; no duplicated SRC identity, no discovery or source-completion stamp. Existing two T4 IDs retained unchanged. No existing effect units found for this source.

## What was read

Identity/opening page, study-area and objectives p2, methods pp9–10, definitions p14, validation/results pp16–19, interpretation pp20–23. Table 4 p17 rendered and visually checked, including all sixteen rows and baseline. Previous full-main-paper inventory remains at methodology/audits/riparian_recovery_20261104/elkadiri/inventory.json; that inventory does not imply this effect lane is complete. Fresh deterministic index confirms 27 pages, tables enabled, no OCR pages; retrieval package saved locally. Original artifact SHA256 and verified queue identity in validation.json.

## Staged claims

| ID | Anchor | Measured outcome | Interpretation |
|---|---|---|---|
| ev_rip_effect_elkadiri23_s4_sediment | p19 first placement example; Table 4 scenario 4 p17 | 45% annual-average outlet sediment-load reduction; 10 m agricultural-adjacent buffer; 113389.3 Mg/year versus 205880.2 baseline | positive sediment_retention; strong BANDS class; model, not measured field effect |
| ev_rip_effect_elkadiri23_s12_sediment | same contiguous p19 passage; Table 4 scenario 12 p17 | 15% reduction; 60 m high-sediment agricultural-adjacent buffer; 174124.0 Mg/year versus same baseline | positive sediment_retention; moderate BANDS class; same model study |

Each native quote contains both sides of the placement comparison (66 words), so the context names the exact scenario belonging to each magnitude. Mechanism is a separate verbatim p18 justification: buffers slow surface flow and promote infiltration/deposition. No claim implies direct measurement of within-buffer trapping efficiency: the actual metric is reduced watershed sediment export. The canonical variable's registered alias is sediment reduction; this spatial-support distinction is explicit for human review. No independence inflation: two scenarios, ONE source. No hazard or p-value inferred. No reviewer_ok granted.

## All Table 4 rows accounted

| Scenario | Width m | Reduction % | Disposition |
|---|---:|---:|---|
| 1 all streams | 10 | 65 | deferred table-row extraction; theoretical all-stream extent |
| 2 all streams | 30 | 78 | deferred table-row extraction; theoretical all-stream extent |
| 3 all streams | 60 | 81 | deferred table-row extraction; theoretical maximum, not feasible blanket rollout |
| 4 agricultural-adjacent | 10 | 45 | staged p19 narrative |
| 5 agricultural-adjacent | 30 | 52 | deferred table-row extraction |
| 6 agricultural-adjacent | 60 | 53 | deferred table-row extraction |
| 7 agricultural-adjacent above 3.7 Mg/ha/year | 10 | 43 | deferred; p19 narrative switches load to yield |
| 8 same above-3.7 group | 30 | 49 | deferred table-row extraction |
| 9 same above-3.7 group | 60 | 51 | deferred table-row extraction |
| 10 agricultural-adjacent above 14.2 Mg/ha/year | 10 | 13 | deferred; p21 gives 27% yield, not interchangeable with outlet-load result |
| 11 same above-14.2 group | 30 | 15 | deferred; p19 narrative switches load to yield |
| 12 same above-14.2 group | 60 | 15 | staged p19 narrative |
| 13 agricultural-adjacent above 19.4 Mg/ha/year | 10 | 5 | deferred; p18 summary says minimum 6%, retain table's 5% |
| 14 same above-19.4 group | 30 | 6 | deferred table-row extraction |
| 15 same above-19.4 group | 60 | 6 | deferred; p21 gives 7% yield, not interchangeable with outlet-load result |
| 16 existing riparian vegetation | variable | 13 | family hold: existing trees do not prove planted or naturally restored origin |
| baseline no buffer | 0 | 0 | comparator only, never null-effect vote |

Table-row extraction constraint: whole-table quotations are forbidden (defect 24); concatenating a distant header/caption with one row breaks contiguous-source provenance. Remaining quantified rows need an explicitly supported table-context representation or other complete native narrative anchors. This is an extraction representation task, not justification to discard rows or invent prose. Table 4 is on one page, with no continuation.

## Other claims and omissions

- p18 stated 6–81% aggregate range conflicts with Table 4 minimum 5%; not staged. Existing-vegetation 13% family held.
- p18 incremental 30-to-60 m width effects (1%, 2%, 0%, 0% in scenarios 6,9,12,15) compare practice intensification, not baseline presence. Preserve as design-response pointer; zero increments are not zero overall effect.
- p19 second example 43%/15% uses sediment yield whereas Table 4 gives outlet load. p21–22 Figure 13 gives yield reductions 7%,27%,38–48%; hold metric/aggregation reconciliation, do not silently substitute Table 4.
- Figure 11 p20 repeats scenario comparisons; no independent evidence. Figures 12–13 pp21–22 represent ranking/spatial allocation, not new causal studies.
- Table 5 p17 sediment basins, Table 6 p18 crop rotation, Table 7 p18 Conservation Reserve Program: outside this bounded riparian batch, retained for practice-scope triage, not assigned to riparian.
- Land footprint is opportunity cost proxy; not income or cost-effectiveness evidence. p23 implementation/maintenance costs and lost income are future research, not measured outcomes.
- p16 lacks observed streamflow/sediment gauges; agreement between two models does not establish independent validation. p22 channel erosion held constant. These constrain transfer, not the verbatim extraction confidence.
- Width side convention unresolved; no conversion to per-bank width. Conflicting p9/pp13–14 mean/SD preserved in prior T4 inventory, not reinterpreted.
- Data Availability Statement p23 says not applicable; no supplement named. Model dependencies not independently audited. No Witing effects extracted: establishment-method ambiguity and uninspected supplements remain separate holds.

## Validation and retrospective handoff

validate_units passed. Central number, context, direction, quote, species, scope and BANDS checks passed with zero flags; exact native quote AND justification containment passed on their pages. checks.json stores results. Orchestrator still must run supported staging-ingestion dry-run and independent adversarial review before admission; update ledger only for work actually completed. No global learning cursor advanced, no source stamped swept. Retrospective signal: table contextual quotation and source metric changes are explicit completion blockers, not evidence scarcity.
