# Bounded extraction retrospective

Scope: 53 new T4 units from five existing acquired sources; no global review-feedback sweep.

## Checks and fixes before ingestion

The first dry-run caught missing income-group context on all 53 units. Added the groups from the repository's versioned WB lookup, not a guessed current classification. The source countries and lookup provenance remain distinguishable from the paper's findings.

The narrow-quote checker initially flagged 12 short table-row excerpts. Each already had a native header anchor; the final primary quotes now include contiguous page context through the relevant row, preserving headers without stitching. This applies existing context/quote rules rather than inventing a new defect category. Final batch number, scope, species and narrow-quote flags are zero.

Semantic review also caught Alene's header/row mismatch and conflicting slope prose, and distinguished Terêncio's project weights from its generic stage using p7. The criteria and conflicts remain reviewable instead of silently repaired. Table coverage checks explicitly retain unmapped rows and continuations; no unsupported proxies were substituted.

## Metrics and limits

The global sweep ledger was updated with label `wh_five_t4_20261104`. It reports 291 number-provenance flags and 16 historical mismatch flags. Neither tally increased because of this batch. Its comparison row predates intervening work: the global delta is 90 units, while this batch contributes 53. Do not attribute that whole delta to this extraction.

The global `numeric` metric counts any nonempty relationship, including direction-only dictionaries. Thus its denominator and a lower global number-provenance percentage do not establish improved numeric calibration. This batch creates zero executable functions. The global mismatch-rate increase likewise cannot measure this bounded batch's quality. Comparable batch checks, source-page review and explicit holds provide the relevant evidence.

No new final-batch defect pattern remains that requires a skill/ruleset change. Existing rules on native headers, scope, table consistency and separate importance/calibration apply. The global human-feedback learning cursor was not advanced, and no review was marked incorporated or approved on a human's behalf.

## Work remaining

Resolve source ambiguities and ontology/family mappings, audit Bera's referenced site supplements if needed for validation, then conduct human QA/QC. These tasks are explicit holds rather than another unrestricted discovery sweep. Sources stay in progress.
