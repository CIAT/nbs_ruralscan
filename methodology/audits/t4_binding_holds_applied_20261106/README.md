# Four T4 binding holds applied — 6 November 2026

Pete approved the four binding holds and retaining the evidence; see `user_decision.md`. The four water-harvesting mappings now have blank dataset associations and explicit `requires_matching_input` requirements in the existing relationship-parameter metadata. Approval provenance is binding-specific; it does not approve numerical calibration or source evidence.

The runoff-catchment runoff, stream-order and drainage-density mappings, plus terracing runoff, are held. Their twelve linked evidence records, source values, old numerical parameters, weights and source approvals remain unchanged. Global VONT/BIND entries, T1 and T2 are unchanged: these are mapping-scoped holds, not a global variable policy or a replacement model.

## Persistence and publication

The compiler and developer handoff share the same row/profile requirement validation. Reviewed row-level requirements are carried by exact mapping ID and override automatic dataset fallback. Other families using the same variable remain unaffected.

If a later synthesis round produces no row or no family for a held mapping, its held configuration is retained with an explicit statement that no new numerical synthesis or approval occurred. This preserves the hold through disappearance and reappearance. Only the binding requirement is carried onto newly synthesized numerical content; independent adaptation metadata and caller state are preserved. Malformed declared holds fail validation.

The two affected family JSON outputs were regenerated through `write_recipe` using the authoritative CSV requirements and the existing family outputs; unrelated family rows and numeric content were compared and preserved. The standard generator regenerates the table JSON and dashboard. An isolated approved-only water-harvesting synthesis confirms all four holds survive. That trial's other analytical changes are not published and are not approved by this decision.

All twelve existing dashboard cards now state that the binding hold is applied and needs no repeat approval. No evidence Keep/Drop decision or review-log entry was fabricated: this was a mapping-input decision.

## Next review prepared

`next_calibration_decision.json` contains a separate, unapplied proposal concerning the inherited combined runoff-catchment `abs_min=75` / `opt_low=80` function. The five underlying publications use different native quantities: Curve Number, runoff depth and runoff coefficient. All complete source profiles, classes, directions and labelled weights are retained for compatible synthesis; regional origin alone is not grounds for discarding numeric evidence.

Vema uses 75/80 as fuzzy CN input-membership parameters. Its page 4 example permits high check-dam/farm-pond suitability at medium runoff when permeability and slope are low. Those parameters cannot establish an independent 75 exclusion and 80 optimum. The numeric coincidence is verified; the historical weighted-median calculation is not reconstructed. Al-Abadi's current evidence already includes its verified page 9 rationale, so the old request to add that rationale is no longer repeated.

Five source hashes and evidence fingerprints, five stored quotes and sixteen native excerpts were rechecked; an independent reader confirmed the interpretation. The separate numeric-hold question is on the existing five source cards in the mapped-claim dashboard queue. No numeric hold, replacement curve, source drop or recalibration has been applied.

## Validation

Tests cover row/family disappearance followed by reappearance, same-variable unrelated families, malformed metadata, preserved caller state, family JSON consistency and a catalogued override unable to bypass each actual hold. `regeneration_probes.json` records the approved-only trial and blocked handoff bindings; `verification.json` records preservation and check results.
