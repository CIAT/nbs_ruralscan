# Next T4 human-review triage — 5 November 2026

Read-only snapshot UTC 2026-11-05T13:52:32.440072+00:00. EV SHA-256 `70aaf85ac458b6b568cd291b362f8a9dd5d602fd9dc0c5b208c8e887c9b7e992`. Exactly 647 active unapproved structural-suitability records ranked; 147 source IDs. The previously reviewed 25 records are absent. No approvals, drops, evidence, ontology, binding, ledger or Git changes.

## Ranking meaning

This is a queue triage, not fresh semantic validation of 647 records. Only the next card was freshly checked against its native source page. Prior audited claims are prioritized with explicit audit references; other records require native source-purpose and measurement review. Numeric fields, model importance, a source tier or a live mapping do not prove calibrated suitability. Within a band, ordering is deterministic by NbS/family/source/ID—not a scientific quality score.

| Band | Records | Review action |
|---|---:|---|
| 1 | 1 | Next concrete source-grounded card |
| 2 | 10 | Prior audited targeting/context claims; review limited retention |
| 3 | 64 | Existing mapping references unapproved evidence; source/parameter check first |
| 4 | 450 | Source-purpose, contextual-presence and semantic verification before approval |
| 5 | 65 | Separate species/crop review lane |
| 6 | 57 | Existing measurement, geometry, source or parked/qualitative hold |

Scope split: 582 practice/technology, 55 species-specific, 10 crop-specific. Cross-family helpers are not new practices. A source-hold lane preserves the prior bounded disposition; it is not a decision to reject every existing claim from that source. Advisory checks for scope, number provenance, quote completeness and species tagging are recorded per row, not used as automatic scientific decisions.

## Family review queue

| Family | Pending | Bands 1–2 | Live-mapping review | Verification/context | Species/crop | Hold/parked |
|---|---:|---:|---:|---:|---:|---:|
| agroforestry__cross_family | 15 | 4 | 1 | 0 | 7 | 3 |
| agroforestry__linear_boundary | 24 | 0 | 0 | 0 | 24 | 0 |
| agroforestry__shaded_perennial | 1 | 0 | 0 | 1 | 0 | 0 |
| forest_restoration__active_planting | 52 | 0 | 0 | 37 | 15 | 0 |
| forest_restoration__assisted_regeneration | 19 | 2 | 0 | 17 | 0 | 0 |
| forest_restoration__passive_regeneration | 46 | 0 | 0 | 46 | 0 | 0 |
| forest_restoration__plantation | 8 | 0 | 0 | 7 | 1 | 0 |
| forest_restoration__protection_cbfm | 11 | 0 | 0 | 0 | 0 | 11 |
| mangrove_restoration__tidal_coastal | 35 | 0 | 0 | 30 | 5 | 0 |
| riparian_buffer__natural_restored | 21 | 2 | 3 | 16 | 0 | 0 |
| riparian_buffer__planted | 24 | 2 | 3 | 15 | 3 | 1 |
| water_harvesting__in_situ | 45 | 0 | 10 | 35 | 0 | 0 |
| water_harvesting__micro_catchment | 42 | 0 | 6 | 36 | 0 | 0 |
| water_harvesting__rooftop | 10 | 0 | 0 | 0 | 0 | 10 |
| water_harvesting__runoff_catchment | 159 | 0 | 28 | 126 | 5 | 0 |
| water_harvesting__spate | 32 | 0 | 0 | 0 | 0 | 32 |
| water_harvesting__terracing | 75 | 1 | 13 | 56 | 5 | 0 |
| wetland_management__creation | 7 | 0 | 0 | 7 | 0 | 0 |
| wetland_management__peatland | 1 | 0 | 0 | 1 | 0 | 0 |
| wetland_management__restoration_rewetting | 20 | 0 | 0 | 20 | 0 | 0 |

## Next concrete review card

**Evidence:** `ev_fr_distance_forest_shono07_20261105`.
**Source:** Shono et al. (2007), *Application of Assisted Natural Regeneration to Restore Degraded Tropical Forestlands*; `shono_anr_degraded_tropical_2007`; PDF p.2 / printed p.621, “Rationale for Using ANR and Required Conditions”.
**Family:** `forest_restoration__assisted_regeneration`; variable `distance_to_forest`; practice/technology scope.

**Why T4:** the source explicitly identifies where ANR is most suitable: natural succession is already occurring and tree regeneration is present. This is implementation/site-selection guidance, not merely study-site coordinates or a measured benefit.

**Actual retained claim:** remnant forest should be nearby to supply seeds for continued succession. Native quote: “To ensure further successional development, remnant forest should be in proximity so that there would be sufﬁcient input of seeds.”

**Context:** degraded tropical forestlands, with Asian practice informing the review. The paper also permits supplemental planting where natural regeneration is insufficient. This record is distinct from the already approved Trujillo-Miranda passive-regeneration claim. Both may inform related decisions but are not duplicate records or interchangeable practice assignments.

**Calibration:** qualitative proximity direction only. No distance cutoff, rate, response curve, score or proof that distant sites cannot regenerate. Seedling density ranges elsewhere on the same page concern recovery timing/site conditions and are not part of this claim.

**Proposed decision:** keep qualitative proximity-to-remnant-forest evidence for assisted natural regeneration; preserve tropical/practice context and supplemental-planting alternative. Approve neither an executable distance curve nor a hard exclusion of distant sites.

**Question:** “Keep this as qualitative siting evidence for assisted natural regeneration, without a numerical distance cutoff?”

**Verification:** fresh exact native quote and source-purpose match on PDF2. Existing seven-page independent review and central admission are recorded in `methodology/audits/all_practice_next_20261105/forest/review.md` and the batch validation. Source identity and team-copy provenance remain in the existing source metadata; no new DOI verification or fresh full-paper sweep claimed.

## Subsequent review order

After this card, inspect the other band-2 records individually. FAO175 terrace guidance retains both a general 4–50% recommendation and the >0.5% long-slope alternative, so no universal 4% minimum or 50% maximum follows. Ranchi classes are regional allocation choices; soil-depth/proxy/unit holds are separated rather than hidden behind apparently complete numerical bands. Riparian corridor widths remain study geometry, not ecological suitability limits. Shared urban/water exclusions are corroboration, not an additional weighted criterion.

Remaining band-3 records deserve scrutiny because an existing mapping references unapproved evidence. This ranking does not declare those mappings runnable or authorize changing them. Bands4–6 must not be bulk-approved. Source/native semantic preparation should precede further user-facing review cards.
