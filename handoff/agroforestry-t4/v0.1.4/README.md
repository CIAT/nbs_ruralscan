# Agroforestry T4 v0.1.4 — reviewed evidence refresh

[Open combined table and rule plots](index.html) · [Readable CSV](T4_review.csv) · [Runtime T4 snapshot](T4_suitability_mappings.csv)

Built 26 October 2026 from the merged source state identified in [manifest.json](manifest.json). Pilot testing remains Diego's work.

## Changes since v0.1.3

The snapshot still contains 26 configured rows: 10 numeric responses, 7 categorical host gates, 1 hard exclusion and 8 operational scenarios. Operational evidence-only variables remain visible alongside these rows, outside the core suitability score.

Across the same 500 structural/operational records, active records with `reviewer_ok=true` increased from 163 to 246; quarantined records increased from 198 to 242. The remaining 12 active records have no approval flag. These are register states, not counts of pending dashboard tasks, distinct studies, or executable curves. Queries, conflicts and reviewer histories remain in the live dashboard.

Recipe source counts changed for shared slope (3 → 4), rainfall (4 → 5) and elevation (1 → 3). These are the live recipe's evidence counts, not new independent calibrated curves. The planted-system soil-carbon row also carries updated source context. Numeric class boundaries, configured weights and dataset bindings were not changed by this release.

All plots were regenerated from the current recipe. The [evidence accounting](evidence_accounting.csv) preserves every record's current approval/quarantine state. [Original-source follow-ups](source_followups.csv) include the Ahmad/Mushtaq climate mismatch, Sanogo/Yossi labour attribution and unresolved Lasco tenure citation; these checks do not authorize additional rules or source votes.

## Remaining execution limits

- Source/context selection remains explicit; regional profiles are not universal curves.
- Rainfall and temperature recipe/BIND dataset differences still require reconciliation.
- Protected-area text needs a legal-mask adapter; local host/boundary inputs remain required for affected branches.
- Source importance ratios are supplied separately from configured equal numeric weights.
- No raster pilot or field validation has been performed.

See [handoff guide](../README.md) for scope and rebuild instructions. Earlier versions remain unchanged.
