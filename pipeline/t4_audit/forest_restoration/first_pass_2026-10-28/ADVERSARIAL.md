# Independent adversarial review — forest and mangrove T4

2026-10-28. Read-only assessment; no human approval granted. Production files were not edited by this reviewer. Current extraction skill is v1.8.0; T4 review contract is v1.6.16. Current FAM, crop/roll-up policy, generation method and hardening audit were inspected.

## Recomputed baseline

| Scope | Active structural | Active operational | Total active | Sources across all T4/operational rows | Active approval flags |
|---|---:|---:|---:|---:|---:|
| Forest, all families |110|100|210|53|0|
| Active planting only |31|40|71|See source inventory|0|
| Mangrove tidal/coastal |12|27|39|17|0|

Forest includes one additional dropped record (211 total). Active forest family counts: assisted regeneration 17, passive regeneration 62, plantation 17, active planting 71, protection/CBFM 37, cross-family 6. Forest has 84 observed-presence rows; mangrove has nine. These observations are not numeric calibration. Four forest and two mangrove active rows carry species scope.

No exact target evidence-ID matches were found in tracked `pipeline/metrics/review_log.csv` or `docs/review/decisions.json`, primary checkout's ignored `pipeline/review/decisions.json`, or handoff worktree's ignored `pipeline/review/decisions.json` and `clarifications.json`. This bounded search establishes no matching recorded decisions in those inspected files; it does not claim nobody ever read a source or decided a family policy. Family-scheme and plantation-rollup decisions remain binding.

Existing SRCH has 18 forest T4 rows, including all four categories for active planting (two grey entries). No standalone mangrove T4 row exists. Historical forest mangrove-coastal grey search exists and must be retained/reconciled, not erased or interpreted as no prior search. Queue has 46 forest T4 memberships (41 acquired, four duplicate, one pending), four standalone mangrove T4 memberships (all acquired). Queue counts do not certify complete extraction. All 53/17 source IDs had at least one cache artifact after hydration; this is presence only, not metadata, quote or identity certification. `reconciliation.json` contains detail.

## Confirmed technical findings

1. `scripts/synthesise-recipe.py::write_recipe` assigned `1/n_rows` automatically. New variables must retain unknown weights; existing configuration is not proof of human ratification. Parent was notified and is fixing. Developer weight-basis prose must also stop claiming every configured weight is an equal-weight placeholder.
2. Legacy forest CSV contains 11 synthesized rows, including retired forest `mangrove_coastal` inundation and active-planting `distance_to_plantation` whose evidence moved to plantation. Baseline saved as `forest_legacy_T4_baseline.csv`. Current approved-only compilation should replace these stale rows, preserving EV history. Header-only approved T4 is honest when no eligible approved evidence exists; it means no approved rule, not no suitability/evidence.
3. Developer run-contract prose unconditionally announces weighted-linear combination and perennial-host OR logic. For these recipes, no aggregation/host policy is approved by that text. Neutral recipe-specific prose needed; no agroforestry host inheritance.
4. Developer source-importance diagnostics load only the agroforestry source tree. Forest/mangrove importance must either use their own recorded trees or report explicit absence; no copied vector or silently complete-looking report.

## Source-semantic findings from actual PDF pages

| Evidence | Actual source/page inspected | Variable use | Direction/calibration finding | Required disposition |
|---|---|---|---|---|
| `ev_fr_population_density_chazdon16_2` | Chazdon & Guariguata 2016, PDF p3 | Landscape restoration approach classification | Below 10 persons/km² is described as *typical* wide-scale restoration; 10–100 is mosaic. Following paragraph allows ecological restoration plantations within mosaics. It is not an active-planting maximum. | Retain source values and scale-class context; hold/repair existing `abs_max=10`; no numeric suitability curve. |
| `ev_fr_protected_area_status_zomer08_1` | Zomer 2008, PDF p5, Fig.2 and discussion | CDM-AR mapped exclusions | Caption says protected areas were excluded. It does not establish a universal legal prohibition on ecological restoration within protected areas. | Retain source model gate; universal legal mask requires applicable law/policy decision. |
| `ev_fr_land_cover_fahrudin24_1` | Fahrudin 2024, PDF p4 §2.3 and Table 1 | Historical target delineation, distinct from ES/wildfire prioritisation | Afforestation definition >50 years nonforest adapted to year-2000 data; reforestation uses 2000–2023. Simple low-tree-cover class loses temporal meaning and ecosystem safeguards. | Preserve temporal conditions and source-specific land-use gate. Do not infer native nonforest suitability. |
| `ev_fr_inundation_gma23_1` | GMA guidelines 2023, PDF p39 (printed 75–76) §3.4.4 | Establishment hydrology | “Most species” cannot establish at >50% inundation; nearby text describes site-dependent hydrology and below-MSL planting risks. No universal community-independent response, observation period, datum conversion or interpolation is supplied. | Preserve warning/value; species/community applicability and hydroperiod support remain holds. No universal 50% trapezoidal function. |

These are fidelity/calibration findings, not new methodological approvals. Existing draft synthesis indeed emits population `abs_max=10` and inundation `abs_max=50`; draft outputs must visibly carry these holds and never be mistaken for ready functions.

## T4 review checklist and limits

- **Variable use:** distinguish priority/ES/wildfire models, restoration approach classes and true establishment suitability. Source-table membership and sibling criteria are required before computing any n/N denominator.
- **Direction:** preserve explicit suitability directions separately from use; narrative observation of reforestation patterns is not a calibrated response.
- **Calibration:** unknown tails, endpoint semantics, soil depth, time support, vertical datum and weights remain explicit. Percent slope conversion does not cure unsupported applicability.
- **Scope/transfer:** active/passive/assisted/protection/plantation remain separate; standalone mangrove family is approved; no new method split or species-to-general transfer is approved.
- **Table coverage:** this independent pass inspected four source pages and existing inventories, not all tables/supplements across 70 scope sources. Full-source completeness cannot be claimed from it. Extraction agents' inventories need further cross-check before sweep completion.
- **Review presentation:** show extracted values, source context, intended destination, importance and exact remaining decision on existing cards. Header-only approved CSV requires a visible held/unreviewed evidence inventory alongside it.

Raw support n/N is headline only when complete eligible screened membership is explicit; unknown N stays blank. Existing SRCH counts overlap and do not supply that membership. Source quality weights, within-study weights and runtime MCDA weights remain separate.

## Staged-extraction review and fixes

Final forest staging contains three units. All three quotes match exact native page text. Historical CDM context (including 1990 baseline), constrained erosion-priority domain and non-modeled tenure conditions are explicit. No blocking extraction-fidelity finding remains on those three staged units. They remain unreviewed; retention does not approve a mask or transfer.

Initial mangrove staging had six units. Adversarial review identified a frequency-versus-duration ontology mismatch and missing prior-method attribution. Extraction agent removed the frequency unit to an explicit ontology hold, retained the local-tidal historical qualifier, and added WB prior-method attribution plus an exact supporting quote. Final five-unit staging has no remaining blocking fidelity finding in the inspected passages. WB lineage remains unresolved explicitly; it cannot automatically supply an independent extra vote. None is human-approved.

Mangrove inventory now accounts for 92 claim/items across a 193-page inventory, explicitly partial. This reviewer checked relevant inventory entries against GMA pp25–26/40 and WB pp6–7: sibling method branches, four hydrology measurement methods, wave/current exposure, intertidal/tidal-range, shoreline dynamics, and land-acquisition constraints all have explicit dispositions. Remaining appendix/supplement and whole-source review is not claimed complete. Forest source inventory retains missing supplements as holds.

`review_notes.json` provides same-evidence-card annotations, with `finding`, `intended_use`, `remaining_decision` and `source_check`. These are independent review findings; they never grant approval or request repeat review merely because a flag is empty.
