# Bibliography and evidence sidebar — 4 November 2026

Pete selected Bibliography as the next dashboard work area after PR #554.

## Plan and sequence

1. Keep one catalogue and stable source identities. Compact publication, source type/origin, practice, extraction/approval and contribution columns. Put limitations in a disclosure. Add family, origin and evidence-status filters plus reset; keep existing search, type, record-set and contribution filters.
2. Enrich source details from existing SRC records by explicit source ID/aliases. Preserve canonical and alias metadata separately. Show team library and publisher links, study method, location, benchmark tier and extraction dates when recorded. Never parse publication details from citation prose or invent missing fields.
3. Source sidebar has Evidence and Source details views. Evidence opens first for sources with excerpts. Search excerpts; filter by family, role, compiled table and approval; quarantined excerpts remain hidden unless requested. Clicking a contribution opens exactly that source's contributing excerpt subset. Full record expansion keeps inspection beside the catalogue.
4. Add valid PDF page and pinned code links where source metadata supports them; retain section/locator text otherwise. Preserve source deep links, feedback anchors, keyboard close/focus return and print restoration. No review mutations.
5. Version the dashboard and regenerate data. Verify counts/filter intersections, aliases, missing records, quarantine, safe URLs/HTML, navigation and browser layout.

## Adversarial adjustments

- Existing raw SRC has library paths for 674 of 678 registered sources, versus 637 publisher URLs. Reuse the existing SharePoint URL helper; links remain subject to team access.
- Per-source screening, exact discovery searches and citation-chasing parents are absent. Show unknown rather than infer pass from extraction or link unrelated searches.
- Claim `lineage_of` is not a discovery parent. Show attribution as recorded within evidence detail, without claiming a citation-chasing route.
- M2b counts operational-risk and asset-vulnerability roles; these can also contribute to T3. Label role counts separately from compiled T4/T3/T6 citations; do not sum table counts.
- T6E economics is absent from dashboard recipe payload. This bounded UI change does not invent a zero or merge economics into T6; state that economics contributions are not shown.
- Full Evidence Query register does not support reliable exact-evidence-ID navigation. Provide full record inspection inline instead of a misleading deep link.
- Dropped state takes precedence over stale reviewer approval. Alias metadata stays attached to its originating source ID. Source-family membership can include historical evidence; evidence filters show actual linked scope.

No schema, analytical rules, evidence decisions, source records or discovery lineage are changed.

## Implementation and validation

- Catalogue filters now start with search/practice; secondary filters sit under More filters with an active-filter count. Source table uses labelled contribution buttons.
- Evidence and Source details views preserve catalogue context. Raw registered metadata remains attached to its source ID, with aliases separate. Full evidence records stay inline.
- Adversarial implementation review found and fixed a contradictory quarantine-toggle state. Show more focuses the first new excerpt, and source permalink reloads open Bibliography.
- 1,031 tests passed; 27 targeted dashboard tests passed after final layout changes. Lint/format, type checks, schema structure and T4 coverage passed. Full dashboard DOM integration covered startup, every tab including QA, bibliography, source drawer and feedback targets.
- Desktop app browser verified dark/light views, publication metadata, catalogue filtering, contribution subsets, approval filtering, quarantine toggle and reset. Narrow-pane spacing checked and adjusted. No user notes or review decisions changed.
