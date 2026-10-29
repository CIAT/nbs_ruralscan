# Restoration source review — 28 October 2026

This is a bounded first extraction batch after acquisition PR #468: the WCS Fiji planting manual and Lewis (2005) mangrove review. It is not a completed review of the 29-candidate discovery round. The other 27 queue candidates and the separate ITTO reuse task remain at their previous states.

## Results

- Read all 48 PDF pages across two sources, including references and blank pages. Inspected the Fiji species-table continuations and Lewis's elevation table and tidal figures visually.
- Added three unapproved evidence units: one operational governance/participation claim for forest planting; two mangrove structural claims concerning local-reference hydroperiod assessment and propagule availability for natural recovery.
- Inventoried all 58 Fiji species-table row occurrences and all 10 Lewis elevation-table rows. These are not 68 independent studies or admitted family-level thresholds.
- Retained no executable numeric suitability function. One supported direction concerns increasing propagule availability for natural recovery. The combined hydrology recommendation establishes relevance/importance, not a monotonic duration response or numeric weight. No fitted-model use is claimed.
- Both sources remain `SRC.extraction_status=in_progress`. Queue `extracted` means some EV exists, not that all claims are resolved. No human approval, existing evidence changes, runtime threshold changes, new search, or corpus-saturation claim.

## Scope and credibility

WCS explicitly defines the manual's restoration as replanting native forest trees on page 8, establishing active-planting relevance. Its page-10 ANR sidebar and page-18 buffer design remain separate practice pointers. Lewis defines ecological restoration on page 2 and distinguishes it from monospecific wood-production planting on page 4, establishing tidal-coastal restoration relevance.

| Axis | WCS Fiji manual | Lewis review |
|---|---|---|
| Evidence strength | Expert operational guidance; no independent validation of a suitability model | Narrative review with referenced field examples; not a meta-analysis or independently validated global model |
| Transparency | Clear steps and species table, but species-table evidence lineage and nursery/site distinction need review | Named references, local datums, figures and contrary observations; several claims require cited-primary retrieval |
| Authority/venue | WCS institutional manual, with Fiji ministry, university and conservation contributors | Peer-reviewed Ecological Engineering article |
| Context | Fiji community planting; transfer outside local systems unapproved | International discussion, with much numeric material from Florida/Australia; no global numeric transfer |
| Recency | 2022; operational guidance rather than current legal requirements | 2005; foundational hydrological-restoration argument, not a current dataset |
| Seminality | No seminality claim | Foundational role documented by the later guidance in this corpus; no invented citation count |
| Independence/COI | Conservation implementation perspective and philanthropy/project support disclosed on p2; discounted versus independently validated guidance | Author's restoration consulting affiliation and own project examples limit independence; repeated citations are not new votes |
| Summary | **medium** | **medium** |

These assessments support source admission for the retained claims; they do not approve borderline classifications. The SRC CSV has no `is_seminal` column, so the narrative assessment is recorded here without changing the frozen table structure. WCS page 2 prints a report DOI; it remains a metadata follow-up, not an unverified DOI added to the queue.

## Holds that matter

1. **Lewis's 30% figure is not a universal cutoff.** Page 9 describes typical-year inundation curves; pages 9–10 also report 35.3% and 59.4% over two years, with basin water trapping. Frequency, duration, drainage, rainfall and tidal datum must remain distinct. The general recommendation survives; no `abs_max=30` was created.
2. **Elevation occurrence is not tolerance.** Table 1 is one undisturbed control transect, using NGVD. Its ten species rows remain observed values, with columns and datum preserved. They cannot define global terrain-elevation limits.
3. **Fiji land types are not slope classes.** “Slopes”, “flats”, “gullies” and “creekbanks” are species-selection categories. No numeric slope ranges were invented. The 58 row occurrences retain individual locators and scope holds. Crop/service-tree usage and native/naturalised status need checking before routing.
4. **Nursery notes need interpretation.** Trema's “well-drained sandy soil” appears in the seed-pre-treatment/notes column. It is retained for review rather than silently treated as an adult-site drainage/texture envelope.
5. **Safeguards do not automatically become land-cover masks.** WCS p9 prohibits damage to existing native forest; that does not exclude enrichment planting everywhere with trees. Lewis p6 cautions against converting natural mudflats; it does not provide an EO-class crosswalk or blanket mask.
6. **Propagule limitation is pathway-specific.** It limits natural recovery; hydrological repair or planting may address it. The retained increasing direction is not a hard exclusion for the whole mangrove family.

Page-level dispositions include operational management, effect/economic pointers and out-of-family material. See `page_claim_inventory.json`; table rows are in `species_row_inventory.json` and `lewis_table1_observed_values.json`. Short row leads are locator aids, not automatically parsed botanical names or suitability values. Full text and rendered pages remain in the ignored local cache/staging, not in Git.

## Verification and retrospective

Ruleset v1.8.0 and the T4 review contract were applied. Deterministic indexes were built, with hash checks and retrieval across all canonical variables; the read was not restricted to search hits. The PDF/table layout was inspected directly where the table detector returned zero Fiji tables.

Three units passed the central ingestion gates: identity, opening title, anchored native quote, numbers, context, VONT, family, role and ruleset. Ingestion dry-run after writing is idempotent (zero new units). Batch scope, species, quote-width and numeric checks return no flags (`batch_checks.json`). The initial gate caught missing country-income context on the Fiji unit; this was corrected before ingestion. An intermediate metadata write attempted an unsupported SRC field and was repaired before validation; final reconciliation checks preserve every pre-existing SRC/EV row.

No new semantic defect class was found: existing rules for site-context, species routing, proxies and source completeness cover these holds. Global sweep metrics are logged as an administrative snapshot; this three-unit batch cannot establish improvement in global error rates. The full human-feedback cursor is unchanged. Family/category verification stays `in_progress`; human review is outstanding.

## Remaining work

Resolve the explicit table/ontology/safeguard holds before further registration. Continue the acquired literature and manuals, then code-source identity/locator and practice-scope admission. The three acquisition blockers (Ioki, CONAFOR, Sidik) and ITTO reuse review remain open. No implied approval of any of those sources is recorded here.

Validation results: schema generation verified 3,872 quotes against 532 cached sources; metadata check passed. Structure validation reports zero errors (3,459 warnings, including the known standalone-mangrove/T0 gap); T4 coverage reports zero errors. Existing 537 SRC rows and 5,203 EV rows are byte-equivalent at parsed-record level; only the two intended queue rows changed. Source-sliced quotes preserve original line-ending spaces, which `git diff --check` reports inside the new CSV quote cell.
