# Dashboard feedback disposition — 5 November 2026

Input: `nbs-dashboard-feedback-report-2026-11-05.html`, exported 08:58:54, ten notes. Baseline: CIAT/nbs_ruralscan `598202af26669c300003c78a590624be936ea39a`. Dashboard release: 1.4.0. No analytical rules or evidence decisions are changed by the interface work.

| Note | Request | Disposition |
|---|---|---|
| 1 | Remove introductory number and box | Progress explanation is plain text; analytical sections retain consistent numbering. |
| 2 | Distinguish AI checks, later review and unexplained dark chart area | Chart explicitly measures later logged AI/team decisions, not all extraction-time checks. Unused count scale is transparent and explained. No missing decision is presented as proof that automated checks did not run or that every claim needs human review. |
| 3 | Fix whole-project source count and jargon | Visible project catalogue total is separate from the narrower T4 cohort. Sources are explained as published research, grey literature and tools/codebases. Count definitions distinguish recorded duplicate links from unresolved duplicates. |
| 4 | Review whether cross-family agroforestry sources really apply across families | Separate [source and claim audit](agroforestry_cross_family_2026-11-05.md). Classification proposals require the normal validated review/intake path; none are silently applied in this UI change. |
| 5 | Keep cross-family row in the main family table; hide empty unassigned row | Combined table with explicit broader-scope labels. An unassigned row is hidden only when its tracked source/extract/output counts are all zero. |
| 6 | Move pipeline records into section 5 | Added 5.3 Pipeline records with independent practice/family/table/channel filters, sorting and pagination. Only stages present in the input log are shown. Progress and review-queue filters remain independent. |
| 7 | Explain high-level flow from discovery to analytical tables | Progress introduction now describes the research-to-configuration purpose and explains sources, extracts and outputs as different units. |
| 8 | Bring tables and method into Overview | Added scoping sequence and compact T0–T7/T6E purpose map, with links to architecture, data model and maintained specifications. Historical snapshots are labelled. |
| 9 | Limit read-only banner to review; surface reviewer guidance | Banner moved inside Evidence review. Existing 5.2 How to review expanded from the repository's reviewer guide. No separate Charity-specific document was located or invented. |
| 10 | Make Rural Scan methodology prominent | Methods now opens on 6.1 Rural Scan method; 6.2 covers evidence workflow and 6.3 retains searchable protocols. Numbered subtabs share existing sticky navigation and keyboard behavior. |

## Compatibility and verification

- Table remains the default for T4 and the separate T2a, T3 and T6 sections.
- Existing source/family feedback identities are retained. Migrated pipeline targets and legacy Methods notes resolve to their new panels; saved subviews and filter contexts are restored.
- Reviewer decisions, clarification state, canonical registers, analytical policies and review submission behavior are unchanged.
- Focused dashboard tests, full-page DOM integration, feedback save/jump checks and desktop in-app browser inspection cover counts, panel visibility, routes, keyboard navigation, independent filters and chart presentation.
- Dashboard/data build identities are regenerated from source; JSON is not hand-edited.

## Follow-through work

The current data cannot prove per-extract coverage of every automated check. A future audit model should record check name/version, run/input hash, outcome, actor and time, separate from later review decisions. Do not infer successful AI validation from an absent flag or equate a CI run without source artifacts to complete provenance verification.

The historical architecture/framework/recipe pages need a coordinated scientific documentation refresh. Their links are now available and status is explicit; the [migration plan](https://github.com/CIAT/nbs_ruralscan/pull/577) sequences that refresh with canonical ownership and release controls.

Resolve the source-audit duplicate and scope findings through small, independently reviewed data changes. Recompute catalogue counts only after explicit identity reconciliation; preserve evidence IDs and historical dropped rows.
