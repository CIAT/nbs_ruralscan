# Water-harvesting scope and review handoff

4 November 2026 · proposal for #547 and #232 · no family changes applied.

## Pete's proposal approval — 4 November 2026

Pete approved the following proposed groupings **for domain review** in the project chat ("yes approve, next"), responding to the explicit distinction between proposal approval and analytical implementation:

- Retain in-situ, micro-catchment and terracing distinctions.
- Group farm ponds and communal tanks under surface storage.
- Treat percolation tanks as a separate recharge branch.
- Group sand and subsurface dams under alluvial storage, retaining variants.
- Classify check dams by purpose before grouping.
- Keep spate distinct pending domain review.

This records Pete's approval to advance these proposals, not completed domain/team sign-off, NbS certification, approval of thresholds, or authorization to migrate analytical families. The crosswalk retains `proposal_not_ratified` until that gate is met. No low-evidence exclusions were proposed or approved. Existing rooftop and homegarden exclusions remain unchanged. The hydrology reviewer remains to be identified; no assignment or consultation is claimed.

## Decision requested

Keep the in-situ, micro-catchment and terracing distinction **where the actual water source and slope modification justify it**. Do not merge similar names automatically. Replace the single storage/recharge assumption within runoff-catchment work with purpose-specific review: surface storage, intentional recharge, and alluvial/sediment storage. Check dams require a stated purpose before routing. These are proposed analytical distinctions, not ratified new family IDs.

Rooftop harvesting is already out of project scope. It needs consistent exclusion wording, not another eligibility vote. Cross-family and macro-catchment umbrella records are not extra interventions. Homegardens remain an existing out-of-scope decision in the separate agroforestry/dashboard track.

The [18-row crosswalk](subpractice_crosswalk.csv) covers every current WH FAM record exactly once. Its eligibility labels are **review proposals, not NbS certification**. The registry establishes water-harvesting functions; it does not establish that every engineered implementation restores or manages an ecosystem. Conditional nature-compatible practices need their soil/vegetation/ecosystem management specified. Conditional hybrids need an explicit nature-based component, ecological compatibility and downstream-impact review; the infrastructure name alone is insufficient. Purely engineered versions are not admitted merely because they conserve water.

## Why these boundaries matter

| Decision | Evidence / existing definition | Consequence for review |
|---|---|---|
| Capture in place versus a separate donor catchment | Current FAM definitions for in-situ and micro-catchment; August family scheme §§3–4 | Classify contour bunds and pits by actual configuration. Do not merge every bund or every on-field practice. |
| Micro-catchment versus slope reshaping | FAM eyebrow terraces versus bench terraces | An eyebrow terrace is not a bench terrace solely because both use “terrace.” Split the combined stone-bund/fanya-juu label for domain review. |
| Surface storage versus recharge | Jha 2014 Table 1 p7: fine soils for ponds/check dams versus light soils for percolation; Bera 2023 pp10–14 mixed storage/recharge rationale | Preserve opposite permeability requirements. A single family-wide soil response is not justified. |
| Check-dam purpose and channel context | Alene 2022 Table 4 p6; Jha 2014 Table 1 p7; Bera 2023 pp13–14 | Preserve source-specific joint criteria. Do not turn a stream order or slope value into a universal check-dam rule. |
| Alluvial storage | Existing FAM sand-dam and subsurface-dam definitions and October ratification | Keep identities. Consider a distinct branch; no automatic transfer of pond or percolation criteria. No new review of those original sources is claimed here. |
| Spate versus storage | Existing spate FAM definition: ephemeral flood spreading, channel and sediment context | Retain a separate decision. Thin evidence and pilot scope are unresolved, not reasons to silently merge. |
| Priority versus establishment | Terêncio 2017 Table 1 p5 and planning-stage explanation p7 | Population, ecological priority and irrigation demand cannot become general T4 establishment limits. |

Source pages, native quotes and EV IDs are retained in [the five-source criterion inventory](../wh_five_extraction_20261104/criterion_inventory.json). This package reuses that completed reading; it does not claim a new source sweep. Its proposals about grouping are analytical inferences for domain review, not quotations from the papers.

## Human QA order

1. **Namita with Pete:** confirm scope and intended use before reviewing threshold values. Decide purpose labels, conditional eligibility and whether the proposed distinctions require new FAM branches. Name a hydrology reviewer; the August scheme records that this role is vacant. Pete + domain/team sign-off is required before structural changes.
2. **Namita:** review the 53 new claims from Adham (5), Alene (13), Bera (16), Jha (15), and Terêncio (4), retaining each source's purpose, units and joint conditions. All are unapproved. Review source-specific use, direction and reported values independently of whether numeric calibration is possible.
3. **Charity, after onboarding with Namita/Pete:** check source identity, page/quote match, full table/header context, units and missing rows. Escalate hydrological conflicts; do not resolve them by choosing the majority direction. This is a proposed allocation, not a claim that work was assigned or messages sent.
4. Use existing dashboard Keep/Drop/Query and Apply/submit workflow. Keep preserves a scoped evidence claim; it does not approve new family grouping, universal cutoffs, interpolation, runtime weights or all engineered variants. Do not maintain a second decision store in this package.

Review these disagreements together:

- Drainage density increases suitability in Alene/Bera but decreases it in Jha. Preserve measurement and purpose; no pooled vote yet.
- Runoff depth, runoff coefficient and curve number share a broad ontology ID but are different measurements. Terêncio's decreasing CN scores cannot be pooled with increasing runoff-depth scores.
- Adham's runoff scores are nonmonotonic and omit stream order 4. Alene prints `8-May` in its slope classes and a mismatched drainage-density table header. Query the source; do not repair by guesswork.
- Jha slope is percent; Bera's placement slope is degrees. Bera/Jha percolation orders differ. Singh's reuse of Jha is not independent corroboration.
- Source weights describe each original model. They are not runtime weights. The 27 supported non-unclear directions among the 53 units are not 27 independent studies.

## Outstanding work, with a stop rule

The previous inventory holds 15 criterion groups. Each has a native quote/page and reason; none is silently discarded:

| Hold | Groups | Next action / proposed owner |
|---|---:|---|
| Ontology: Bera curvature, lineament density, geomorphology; Terêncio soil profile depth | 4 | Schema/domain review of mappings. Do not substitute slope, drainage density or bedrock depth. |
| Bera gully plugs | 1 | Pete + domain reviewer decide family/purpose. No current dedicated FAM record. |
| Alene road/town proximity; Bera groundwater demand; six Terêncio priority/demand groups | 8 | Preserve deferred pointers for M2b/M4/M6 owners. No unilateral T3/T6 extraction or rerouting. |
| Adham and Alene cited slope cautions | 2 | Human review alongside the graded tables. No universal exclusion inferred. |

Bera supplementary S1–S6 validation-site tables remain unacquired, separately from these 15 groups. Their acquisition is a bounded follow-up if site-validation claims are needed; not a new literature chain. Source ambiguity may remain Query even after checking the original. Lack of calibration does not require dropping a supported direction.

**Stop new broad discovery here.** Review the available priority evidence and resolve purpose/scope first. Five sources remain `in_progress`; this document does not stamp them complete. No overall project completion percentage, family sign-off, extraction stage or human approval is inferred from record counts.

## Implementation handoff after sign-off

- Update FAM and family/recipe prose together. Record any new IDs and mapping rationale; preserve old evidence IDs and review history. Generic umbrella evidence stays broad unless its source supports a narrower purpose.
- Inventory T4 mappings by family, then reassess only affected rows. Do not copy a broad-family threshold into every new branch. Preserve numeric and categorical calibration holds.
- Coordinate T3/T6 routing with that track's owner. Do not alter their claims or synthesis in this batch. Family splitting must not multiply independent-study votes.
- Keep point/linear structure footprints distinct from candidate areas. Current `area_suitability` for field systems is not proof that pits/bunds occupy every pixel. `applicability_zone` is not a measured count of constructible sites; site density requires separate site-selection evidence.
- Dashboard track: reflect existing rooftop/homegarden exclusions in status and target totals while retaining historical/contextual evidence. Verify the current implementation there; this data-review package does not claim that display cleanup is done.

The August scheme remains historical rationale. Its “no WH T4 rows,” rooftop “Scope Q,” and example slope/stream-order bands must not be used as current status or approved global rules. A notice links here; substantive family changes remain pending sign-off.

## Reproducible inventory

Run `python3 methodology/audits/wh_scope_review_20261104/build_snapshot.py` from the repository. [snapshot.json](snapshot.json) records input hashes, source commit and counts per family. Counts include all claim scopes and distinguish dropped records, role, human approval and existing T4 mappings. Non-dropped does not mean in-scope or approved. FAM has 18 WH records across seven family IDs; this includes umbrella/tag records and is not the promised target-practice count.

| Current family | Non-dropped T4 claims | Marked reviewer_ok | Existing T4 mappings |
|---|---:|---:|---:|
| In situ | 45 | 0 | 5 |
| Micro-catchment | 42 | 0 | 3 |
| Runoff catchment | 159 | 0 | 9 |
| Terracing | 74 | 0 | 5 |
| Spate | 32 | 0 | 2 |
| Rooftop (out of scope) | 10 | 0 | 1 |
| Cross-family | 0 | 0 | 0 |
| **Total, including historical out-of-scope records** | **362** | **0** | **25** |

These are register flags at the recorded commit, not a claim that no reviewer has read any paper or that every non-dropped claim should enter the human queue. The 53 new units are a subset of runoff-catchment claims. Scope cleanup must not hard-delete rooftop history.

Validation covers all 18 FAM records exactly once, current family/footprint matching, all EV/T4 family references, all 53 new units still unapproved and all 15 held groups present. No register, ledger, review decision, analytical rule or dashboard code is modified.
