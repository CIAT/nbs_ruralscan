# Runoff-catchment calibration hold applied — 6 November 2026

Pete approved holding the inherited combined `abs_min=75` / `opt_low=80` function while keeping all five source profiles. The exact approval is in `user_decision.md`; `applied_hold.json` records the before/after mapping and complete retained profile inventory.

Only `water_harvesting__runoff_catchment__runoff_potential_index` changes. Its active parameters no longer contain the inherited bounds or the derived ±60% uncertainty. These remain historical values inside the numerical-hold metadata and audit. The declared relationship type is retained for provenance; it has no active bounds and cannot execute while held. All five source links, source records, native classes/ranges, directions, weights and evidence review states remain unchanged. Five publications do not automatically represent five independent calibration votes.

Vema's 75/80 parameters describe fuzzy Curve Number input memberships, not an independent 75 exclusion and 80 optimum. Other retained sources use CN, runoff depth or runoff coefficient. Their complete quantitative profiles remain available for compatible synthesis; this decision neither pools unlike measurements nor downgrades regional tables to qualitative evidence. The earlier source pack remains an unchanged historical proposal, superseded by this recorded approval.

## Enforcement

The mapping-level `reviewed_adaptation.numerical_calibration` hold is separate from the existing dataset-binding requirement. Numeric evaluation rejects held rows before profile or pool selection. Developer handoff offers no selectable function and reports the calibration blocker; a stale selection cannot release it. Malformed declared holds fail closed.

The compiler preserves the exact held configuration and its source links through empty synthesis rounds, missing families and later regeneration. A new synthesis does not supersede the human decision. Generated references and units cannot relabel the retained configuration. Binding-only decisions retain their existing behavior, allowing independent numerical content to evolve while holding dataset fallback. The four approved dataset-binding holds remain in force.

CSV is authoritative. The affected family output was refreshed through `write_recipe`; only the target mapping changed. The standard generator rebuilds table and dashboard JSON. No analytical JSON was hand-edited. An isolated approved-only synthesis preserved the hold and five source links; its other proposed recipe changes were not published. The existing water-harvesting developer export still needs reviewed evidence and recipe parity; this work does not claim a runnable water-harvesting release.

## Dashboard and next decision

Five existing runoff-catchment cards now say the numerical and binding holds are applied, with no repeat mapping approval needed. Evidence-level review remains separate. All 642 priority memberships remain unchanged.

The next existing card is Krois & Schulte (2014), terracing runoff coefficient. `next_terracing_decision.json` preserves its complete four-class profile: >0.9 optimal (9), 0.6–0.9 high (7), 0.3–0.6 moderate (5), 0–0.3 marginal (3), with no runoff exclusion class. Source criterion weight 0.14 is separate from the class scores. Its event-runoff coefficient uses wet antecedent conditions and a maximum-daily design storm, not annual runoff or CN.

Unlike the Vema interpretation, >0.9 is a genuine source optimum class. The dashboard asks whether to retain that full profile and hold only the incomplete singleton `opt_low=0.9` encoding pending an explicit class-preserving function, endpoints and score convention. That proposal is **not applied**. The terracing mapping is unchanged, including its previously approved binding hold. An independent reader verified its PDF hash, stored quote, nine native slices and source tables.

## Validation

`verification.json` records preservation and automated-check results. Regression tests cover direct/profile/pool bypasses, malformed holds, developer selection, empty-round regeneration and unrelated same-variable mappings. No extraction sweep, source promotion, human Keep/Drop decision, review-log entry or progress-ledger advancement is claimed.
