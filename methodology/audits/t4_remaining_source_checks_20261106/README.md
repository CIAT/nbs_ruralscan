# Remaining active T4 source checks — 6 November 2026

All **515 assigned existing records across 129 cached sources** received a bounded source-purpose, cited-page and semantic check: 450 general records and 65 records in the separate species/crop lane. This completes the remaining active source-check batch from the 5 November triage, not a new extraction sweep or a claim that every publication has been fully extracted.

## Dashboard handoff

- `t4_source_checked_20261106`: 450 general records, now source checked and ready for human review.
- `t4_species_crop_20261106`: 65 source-checked species/crop records; original scope preserved.
- Existing 64 mapped-claim priorities and original six wetland priorities are unchanged.
- Existing 57 parked/held records remain parked. No practice is reopened.

There are **416 Keep recommendations and 99 Hold/correction recommendations**. None is applied. High priority marks the 99 Holds; source and family filters support bounded review. Each card explains source facts, interpretation/encoding concerns and exact proposed decision. A Keep retains the stated source scope; it does not grant global transfer, numerical calibration or a new recipe.

Local dashboard: <http://localhost:9284/dashboard.html#review-priority=t4_source_checked_20261106>. Species/crop batch: <http://localhost:9284/dashboard.html#review-priority=t4_species_crop_20261106>.

## Findings requiring attention

- Thirteen WOCAT rainfall summaries truncate full source classes. Four incorrectly store a maximum of 1 mm; nine store 750 mm despite higher selected classes. Literal class labels survive. These are proposed audited corrections, not replacement suitability limits.
- Catchment transport distance is encoded as catchment area; drainage area is encoded as drainage density; runoff depth, runoff coefficient and Curve Number need distinct meanings and bindings.
- Alene prints “8-May” in a slope table. Its prose rejects slopes above 8%, while tables allow higher slopes. Both source contradictions remain visible; no guessed repair.
- Source map geometry, corridor designs, carbon/benefit targeting and historic programme eligibility are distinct from establishment suitability.
- Species-group model loadings, observed ranges and Boolean map outcomes are retained separately. Signed-zero loadings do not establish meaningful response direction; outcome area is not a suitability cutoff.

The 255 WOCAT observed-presence profiles remain documented implementation context. Their site checklists do not establish generalising T4 suitability rules; existing compiler exclusion from votes/thresholds remains. Handbook recommendations retain their full conditional ranges. Source-purpose evidence and its limitations are explicit in each source inventory.

## Verification and limits

All 515 stored native quotations match their cited cached artifacts. All 515 review-purpose excerpts are checked against source pages/sections and artifact hashes. Three source groups were reviewed separately; bounded cross-review challenged WOCAT class selection, water-harvesting table/weight meanings and species/proxy interpretations. Reported defects were corrected in review annotations before handoff.

Mushtaq's opening title was checked, but its legacy acquisition-queue metadata is absent; no verification stamp was invented. Del Campo's main-text depth claim was checked, but supplementary FigSM3 is unavailable in the assigned artifact; its interpretation remains held. Source checking does not establish correctness of every published number or complete extraction coverage.

`source_checks.json` contains the 515 per-record proposals and current evidence fingerprints. `source_inventory.json` contains source-purpose excerpts, hashes and inspected locations. `queue_manifest.json` separates checked, reviewed and parked denominators. Group reports retain details and deferred pointers; full source text and inspection images remain in staging/cache, not this audit.

## Bounded retrospective

This pass confirms existing defects: study-context versus suitability (#8/#16), proxy/quantity substitution (#4), missing relationships (#12), incomplete table context and numeric plausibility (#55). Full regional numeric profiles are retained under v1.9.8; regional origin alone does not justify a qualitative-only downgrade.

A narrow diagnostic compares explicit closed observed-class ranges with their stored summary bounds (`observed_summary_diagnostics.json`), independently reproducing all 13 rainfall errors. Existing number-provenance token matching allows split thousands tokens, so quote matching alone cannot catch this semantic summary defect. No numeric repair is applied here. These diagnostics are not a new universal range rule or a claim of improved global defect rates.

No source/evidence register, review decision/log, practice definition, mapping, approval, ruleset stamp, learning cursor or progress-ledger stage is changed by this review-only pass. No new source discovery or extraction is claimed.
