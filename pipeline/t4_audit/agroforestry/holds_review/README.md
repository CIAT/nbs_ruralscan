# Agroforestry T4 holds: source-context review, 19 October 2026

**Approval update:** Pete approved all five corrected records in chat on 19 October 2026 ("I approved all"). All five now have `reviewer_ok=true`; the account below describes the preceding source-context review. Original holds and AI corrections remain in history. The chat-derived CSV explicitly identifies its provenance; browser-only notes were not recovered. `after_approval/` holds the current approval-filtered trial: **four generic rows**, unchanged. Three observed records remain excluded; Haile still needs class/applicability mapping; canopy remains selection-only. The two methodology decisions remain open. Focused tests: 15 passed; all five approval events verified.

Branch: `codex/t4-review-oct19`. Five existing units corrected after inspecting complete cached PDF pages and adjacent context. No evidence rows deleted, no new sources registered, no family definition changed. These are AI source-context corrections, not human approvals: all five remain `reviewer_ok=false`, with Pete's original notes preserved and a separate `Codex source-context review` event.

## Findings and actions

| Held unit | Full source context | Action |
|---|---|---|
| `ev_soildepth_inab_p92_aa_example` | INAB PDF p92, Photo 8: one Purulhá site has >90 cm effective soil depth and 22% slope and is allocated to Aa. Aa means annual crops with trees and/or soil conservation (p27). Regional allocation matrices include Aa on shallower soils (pp29–35). | Removed false `abs_min=90`; retained observed site depth/slope and class context as `observed_presence`. Replaced translated/stitched quote with an exact PDF slice. This is not a universal depth-to-bedrock rule. |
| `EV_wocat_1358_2017_003` | WOCAT PDF p4, **Natural Environment**: checked “flat (0–2%)” describes the documented technology site. No claim of failure above 2%. | Removed absolute bounds; retained selected site class as `observed_presence`. The clarified question is whether the sheet describes location or limits; here it describes location. |
| `EV_researchsquare_fmnr_2025_001` | PDF p5, Results: reconstruction across Sahel croplands, with 300–800 mm defining the study domain. | Removed absolute bounds; retained domain rainfall as `observed_presence`. FMNR scope proposal logged separately; domain endpoints cannot become establishment thresholds. |
| `ev_T4_precip_haile2024_2` | Haile Table 3, PDF pp4–5: <600=Low; 600–800=Medium; 800–1200=High; >1200=Very high. Regional Genale sub-basin AHP classification. | Removed false 800–1200 optimum. Preserved all four ordinal classes/ranks and 12% AHP weight. No fabricated membership scores, hard lower bound, or global inheritance. Family/context applicability and class mapping remain pending. |
| `ev_tree_canopy_cover_sprenkle24_1` | Sprenkle-Hyppolite PDF p4, Geospatial data processing: 25% prevents double counting agricultural and forestry natural climate solutions; authors explicitly acknowledge agriculture above 25%. | Removed executable threshold; retained an accounting convention as `scoping_candidate`. Added dataset fitness note: demonstrate trees within agricultural land before aggregation. Higher resolution alone does not turn this cutoff into a biological limit. |

## What this changes

The all-active trial drops from six to **five generic rows** because the false soil-depth row disappears. The approval-filtered trial stays at **four generic rows**, with no held unit contributing threshold parameters. Four crop-specific candidate rows remain separate in the all-active report; none are approved. The three observed records no longer inflate variable-support counts. Haile's classes remain visible as unresolved class mapping; canopy is selection-only.

These counts are diagnostic, not evidence of a complete or publishable recipe. Support percentages still use provisional T4 inclusion denominators. Other records, including WOCAT rainfall from the same environmental table and the inherited cross-family rainfall encoding, need their own source/applicability review; this pass does not endorse them. Live T4 recipe files remain unchanged.

## Decisions still needed

1. **FMNR scope:** recommend a scoped semi-arid Sahel pilot under existing F2, rather than redefining all regeneration-based agroforestry. Require observed cropland, trees/rootstock or regeneration opportunity, and an explicit management definition. Do not enforce 300–800 mm solely because one study selected that domain. A future geographic mask and any climate response need independent justification. See `T4_af_fmnr_scope` in the decision register.
2. **Haile transfer:** retain as regional ordinal evidence until relevant family and dataset units are established. Do not average it with FMNR or turn “Low” into exclusion. See `T4_af_haile_transfer`.
3. **Canopy data:** verify land-use/tree co-location and spatial grain; mixed forest/crop pixels are insufficient. The Sahel reconstruction source describes 15 m tree-cover mapping on croplands (p5), a candidate to assess rather than an adopted binding.

## Audit trail

`corrections.json` retains each full prior record, changed fields, rationale, cached-artifact SHA-256 and exact quote offsets. `corrected_units.json` is validated staging output. `decisions.json` contains the separate AI review events; the original human export and review log remain intact.

Cached artifacts were indexed with `build_index`, packaged with `package_for_extraction` (full tables), and inspected on cited pages. Quotes were sliced from indexed PDF text, never retyped. `validate_units` passed before staged fields were replayed onto the five existing IDs. No analytical schema or column changes.

## Validation

- Focused T4 and review-replay tests: **15 passed**.
- Source guardrail: **4,316 quotes verified against 488 cached sources**; 491 baseline-layer exemptions reported by the existing validator.
- Schema structure: **0 errors**; 3,274 existing warnings.
- Exact before/after comparison: only the five intended EV IDs changed; record count and all other rows unchanged. Each replacement quote matches the recorded character slice of its cached PDF page; all five prior attribution histories remain intact.
- All five corrected relationships lack executable absolute/optimum/threshold keys. Trial dispositions: three `observed_presence`, one `class_or_gate_requires_mapping`, one `selection_only`; no held unit provides approved threshold parameters.
- Source quote whitespace is retained verbatim, including trailing spaces inside CSV quoted fields; `git diff --check` flags those source-text spaces. No whitespace normalization applied to evidence.
- This is a bounded correction of existing review records, not a discovery/extraction sweep. Known site-description/class-rank defects are already in the extraction catalogue. No search/ledger completion or learning-loop cursor advancement claimed.
- Generated-schema check: **0 stale files**. Decision-dashboard check also passes after using the supported `open` status for the two unresolved decisions.
