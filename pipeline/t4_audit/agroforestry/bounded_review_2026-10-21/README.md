# Agroforestry T4 bounded re-review — 21 October 2026

Scope: all 10 sources referenced by live T4 rows (via evidence IDs), plus six recent recovery sources. No new discovery search or full corpus sweep. Three review agents used the v1.6.16 contract; the coordinator reviewed Mushtaq, Singh and Wotłolan. Each source has a reviewed-table inventory and artifact hash in `manifest.json`.

## Result

53 source-backed companion records staged: 52 active pending human review, one Chuma land-use record automatically quarantined because it lacks land-cover classes. Existing human approval and dropped states are preserved. The quarantined record still documents model use separately from usable suitability response. Six unmapped Ahmad soil properties, categorical exclusions and other unresolved raw variables remain in source inventories rather than being assigned false aliases.

Live T4 has no added/removed mappings or newly approved curves. Three rows refresh Haile source-context metadata to expose conflicting weights. Existing wrong-variable/scope/boundary records remain explicit correction decisions; this audit does not claim those approved records have been repaired.

## Session issues checked

| Issue | Outcome |
|---|---|
| Missing sources / only checking emitted records | Live T4-to-EV source join plus recovery-source inventory; source-coverage regression check |
| Missing table rows / continuations | Whole-table inventories, numeric companions and explicit unmapped holds |
| Direction-only evidence lost | Directions preserved separately from calibration; no invented scores/endpoints |
| Paper counts and duplicate branches | Direction report separates lineage, scope, context and approval; model-use report deduplicates papers |
| Source weight vs suitability | Independent fields; conflicting table weights and multiple branches suppress a settled effective weight |
| Species/crop vs practice | Mushtaq kept species-specific; Castle/Wotłolan species-selection use separated |
| Proxy substitutions | NDVI/canopy, soil stock/concentration, bedrock/profile depth and spectral wetness/TWI explicitly checked |
| Source provenance | Native quote/page checks; graphical direction provenance has image hash and separate page |
| Approval / dropped evidence | Existing decisions preserved; new records unapproved; quarantine visible |
| Review usability | Searchable HTML table shows direction, scope and calibration issue with source details |

## Remaining review priorities

- Ahmad 2018: retire incorrect canopy-cover interpretation in favor of NDVI companion.
- Haile: reconcile Table 3 versus Table 5 importance weights; pH classes remain inconsistent.
- Nath: finite source slope domain versus existing unbounded tail; unit/class ambiguities; repeated soil branches need explicit aggregation decisions.
- Castle/Wotłolan/Mushtaq: approve species-selection use without promoting species envelopes to general practice rules.
- WOCAT: rootstock routing, selected observed slope classes and land-cover page provenance.
- Baldwin/Pinto: ownership consolidation is not tenure security; tree occupancy is not canopy cover.
- Ahmad 2020: map six raw soil properties without aliases; categorical exclusions need exact claim-specific provenance before EV staging. Nested soil weights are evidenced in Figure 1 (six ×16.66% within33.33%).
- Tea mask remains Pete's approved design choice, not empirical tea evidence from the coffee/cocoa source.

## Validation and limits

Full suite: 477 tests passed before final small weight/quote fixes; subsequent focused suite: 37 passed, including the added branch-weight regression. Source guard verified 4,385 native quotes across493 cached sources. Frozen-schema and bounded-coverage checks passed; existing advisory warnings remain.

New-record diagnostics: zero scope/species flags; six short-row quote-width advisories with separate native table headers; one numeric-parser advisory for Nath's literal `4,12` categorical codes (encoded as integer list, not decimal4.12). No rule was loosened to hide that flag. Check details include all in-scope existing records, not only additions, in `check_results.json`.

The global retrospective rates did not improve materially; no full-sweep quality claim is made. Cached GEE implementation was unavailable for the Castle paper: its published methods and dataset table were checked, not unseen code. This run does not establish regional transferability or resolve every source typo.

## Reproduce

```sh
PYTHONPATH=src python3 scripts/check-t4-bounded-review.py
PYTHONPATH=src python3 scripts/report-t4-bounded-review.py
PYTHONPATH=src python3 -m pytest tests/test_t4_bounded_review.py tests/test_evidence_assessment.py tests/test_variable_usage.py
```

The approval snapshot is an audit guard. Intentional later human-review changes require explicitly updating this audit expectation; they must never be hidden as incidental regeneration drift.

## Source corrections applied, 21 October 2026

Two previously flagged defects are now corrected against retained table images:

- Nath Table 2, PDF p11: slope classes span 0–44 degrees. Added `very_good_min_deg=0` and `unsuitable_max_deg=44` to the existing evidence relationship. Values outside this source domain remain unknown; shared class endpoints are not silently repaired.
- Ahmad Table 2, PDF p8: the 14.4% row is NDVI, with low <0.2, medium 0.2–0.5 and high >0.5. Corrected the original record's variable from canopy cover to NDVI, retained its stable evidence ID and original human-review attribution, and compiled its three regional classes. No automatic family transfer or cross-paper NDVI pool is approved.

Both records retain their prior `reviewer_ok` and `review_state`. `context.source_corrections` records exactly what Codex changed and why; no new human review is claimed. The audit's original findings remain as history with a resolution entry. Pending companion records remain pending; these corrections do not bulk-approve the bounded review queue.
