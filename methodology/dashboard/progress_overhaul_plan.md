# Dashboard Progress overhaul — 4 November 2026

User: Pete. Audience: Laurent / Bank project lead, then evidence-review team.

## Accepted design

- Rename Evidence & Discovery to Progress. Overview first; practice navigation beneath. Overview summarises effort, then an expandable NbS → suitability-family table with named subpractices. No invented analytical hierarchy, top statistic boxes or default status badges.
- Two workflow bands: discovery/screening search records, then identifiable sources → retained excerpts → compiled T4 relationships. These are different populations, not a single shrinking funnel.
- Collapse source type into a compact literature / grey / tools mix, retaining unknown. Stocktake is an origin, not a fourth source type.
- One Bibliography workspace combines registered/queued sources and legacy stocktake/tool entries. Conservative identity joins; evidence drawer stays beside publication details. Discovery search and citation-parent links appear only where recorded. T3/T6 contribution counts use actual generated-row evidence links; M2b counts are explicitly role-based. T6 economics is not silently mixed with T6 benefits.
- Methods owns search protocols, dates, terms, raw counts, limitations and count definitions. Evidence Query owns sourcing flow and analytics, scoped to the selected compiled recipe/family.
- Reviewer QA queues, consensus/apply/submit and local stores remain separate and unchanged.
- Header exposes dashboard release, UI content build and data snapshot. Generated payload retains a bounded build history; git preserves earlier snapshots. Print overview includes scope, definitions, totals, expanded families and build identity.

## Adversarial review and adjustments

Two independent agents reviewed the plan; a third audited UI dependencies.

1. Search registers repeat searches across tables. Combine shared retrieval events and preserve linked search IDs/tables and original screening protocols. Different table-specific screening criteria do not establish a new retrieval. Where screening protocols differ, do not aggregate their screened/included counts. Conflicting counts, missing counts and prose remain visible; never parse approximate prose as exact integers.
2. Screening, full-text review and expert approval differ. `reviewer_ok` means approved excerpt; never call it whole-paper review. Screening-to-reviewed-source percentage is unavailable without a linked source screening denominator.
3. Catalogue identity is incomplete. Count known source records after explicit alias reconciliation, not unique publications. Unmatched legacy bibliography resources are excluded from that headline, shown separately with reconciliation caveat.
4. Global totals are set unions, not sums of practice/family rows. Practice-wide evidence is not copied into every family. No fabricated subpractice counts.
5. Dropped evidence remains historical effort, excluded from active contribution counts. Compiled references to absent/dropped EV are exposed as unresolved, not valid support. Operational constraints embedded in T4 are distinguished.
6. Preserve navigation IDs, stable feedback targets, keyboard drawer close/focus return and source permalinks. No review mutations in the bibliography.

## Validation

Metric fixtures: overlaps, aliases/cycles, shared searches, prose/blank counts, invalid denominators, dropped/approved evidence, generic scope, compiled references and operational rows. Browser checks: Overview/practice switching, expanded families, source search/filter/drawer/permalink, Methods navigation, unchanged QA queues, theme and print. Generator must detect stale new payload sections and stable builds. Run relevant tests and project gates; review resulting diff adversarially before PR.

## Implementation review

The adversarial implementation review corrected five issues before release: hard legal exclusions stay in core suitability (51 core mappings, 8 soft operational records in this snapshot); extracted excerpts are shown separately from compiled citations; explicit legacy practice labels remain filterable; source counts contributing to compiled T4 are visible; dark and print themes use consistent text colours. A further review separated shared retrieval identity from table-specific screening rules to prevent multiplying the same stocktake search across tables.

Existing feedback targets remain recoverable through collapsed family rows and filtered bibliography records. Source drawers support aliases, deep links, keyboard close and focus return. No source/evidence register, review decision, family definition or analytical mapping was edited for this dashboard change.

## Visual verification — 4 November 2026

Chrome inspection confirmed readable dark/light overview and practice views, practice-filtered bibliography, search and the source evidence drawer. Print preview exposed nested-table fragmentation and repeated total rows; print now renders the complete summary first, followed by six standalone practice appendices (seven pages for this snapshot). First and final print pages were inspected, including margins, source/build identity, family labels and absence of reviewer controls. Targeted UI/build/count tests pass after the print fix; the prior complete suite and CI passed all 1,020 tests.
