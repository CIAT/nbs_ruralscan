# Five-source riparian T4 recovery — 4 November 2026

## Result

Completed bounded intake and main-paper claim accounting for the five placement-method candidates identified in the earlier riparian stocktake. All five opening titles and unchanged PDF hashes passed intake; the team copies now live in `library/4_Riparian_Buffers/`. No discovery search was reopened.

Six unapproved, practice-level scoping candidates were admitted through the deterministic pipeline under v1.9.4. All six remain selection-only, with no calibrated suitability direction, executable function, runtime weight or new link to a live T4 mapping.

| Source | Pages accounted | New EV | Retained content / hold |
|---|---:|---:|---|
| Bentrup & Kellerman 2004 | 7 | 2 | Stream-order-based corridor inventory; total widths and explicit first-order per-bank distance. Existing patch-area/dispersal ontology and interleaved-text holds remain. |
| ElKadiri et al. 2023 | 27 | 2 | Agricultural-adjacency scenario and alternative buffer widths. Sediment priority and trapping predictors are not establishment constraints. Width-side convention remains unresolved. |
| Gu & Liu 2010 | 7 | 0 | Anchored geometry, observed agricultural cover and ranking claims retained. Planting versus regeneration/woody restoration is not established by the source. |
| Semmens & Ancona 2019 | 14 | 0 | Four anchored family holds: width, stream order, land-cover conversion and species-specific milkweed soil evidence. Mixed restoration/management scenarios do not establish one family. |
| Witing et al. 2022 | 16 | 2 | Explicit riparian reforestation: local corridor geometry and urban/water exclusions. Outcome-model predictors and allocation objectives remain separate. |
| **Total** | **71** | **6** | **Three contributing sources; five inspected sources. Neither is a screened-corpus denominator.** |

All five sources remain `in_progress`. Queue rows with admitted units are `extracted`; Gu and Semmens remain `acquired`. These labels do not claim source-wide completion or human approval. The two existing stock-family ledger rows remain `verified=in_progress`, with a dated account of this batch. Search status, family definitions and human review decisions were not changed.

## Evidence and scope

- **Geometry is not calibration.** Bentrup's 80/100/120 m widths are total corridors; only first-order 40 m per bank is explicitly given. Witing uses 100 m total / 50 m per side. ElKadiri's 10/30/60 m labels do not explicitly settle the side convention. Semmens gives fixed per-side widths but leaves its variable-width convention unresolved. No missing conversion or ecological maximum is invented.
- **Host/placement filters retain their context.** ElKadiri evaluates both all-stream and agricultural-adjacency scenarios. Its agricultural class is not a global exclusion of other land uses. Witing's urban/water exclusion is a local allocation constraint, not new project-wide policy approval.
- **Family holds preserve evidence.** Gu and Semmens are registered as relevant sources, but their queue family tags are not ratification. Exact claims, native pages and values remain available for a later explicit family decision. Milkweed soil preferences stay species-specific and are not discarded or generalized to riparian vegetation.
- **Performance is separate from establishment.** ElKadiri's slope/drainage-area/vegetation predictors estimate sediment trapping; Witing's eleven predictor rows describe ecological and production outcomes. Both are retained as page-linked deferred material, without opportunistic T3/T6 extraction.
- **Tools remain bounded referrals.** AGBUF/AnnAGNPS dependencies are identified in ElKadiri; their source code was not inspected here. The earlier CoMOLA audit remains an M4/M6 referral. No README-derived tool thresholds or new repository search are claimed.

## Outstanding holds

The per-source inventories account for every main-paper page, relevant table/figure and supplement pointer. See [Bentrup/Gu](bentrup_gu/inventory.md), [ElKadiri](elkadiri/inventory.json) and [Semmens/Witing](semmens_witing/inventory.md).

1. **Family applicability:** Gu and Semmens need an explicit interpretation before assigning retained claims to planted or natural/restored families. Do not duplicate them into both families to manufacture coverage.
2. **Ontology/text:** Bentrup's existing riparian patch size and inter-remnant dispersal distance do not match proposed restoration area, forest-only fragment size or gap ratio. Native text interleaves selected land-cover statements and continuations; inspected images do not authorize stitched quotes.
3. **Source inconsistencies:** ElKadiri p9 mean/SD differ from pp13–14 wording. P21 Figure-13 narrative also differs from corresponding Table-4 figures, but sediment yield versus outlet sediment load and aggregation may explain the difference. This remains an unresolved comparability question, not a declared source error or corrected value.
4. **Supplements:** Semmens' supplementary crop-value table is outside this T4 pass. Witing S1–S14 pointers include methods and model details not inspected here; its mixed data/code archive remains subject to the paused dataset-intake rule. No full-source completion claim follows from main-paper coverage.
5. **Human QA:** reviewers may retain, query or reject the six scoped claims. Retention does not authorize ecological transfer, new masks, interpolation, family regrouping or executable widths.

## Pipeline and preservation

Built full-table deterministic indexes, retrieved multi-variable packages, read native pages and inspected layout-dependent images. Quotes were sliced programmatically and emitted with `validate_units`/`save_units`, then passed central staging dry-run and admission with `--allow-structural`. Source records were promoted as pending and explicitly left in progress after the bounded pass; the ingestion helper's automatic `swept` stamp was not retained.

The staging gate omitted current v1.9.4 despite the canonical skill declaring it. This batch adds that accepted version and a regression test that reads the canonical skill version and exercises the real gate. The test failed before the change and passed afterwards. No historical evidence is restamped.

`preservation.json` and `batch_checks.json` verify existing EV records, unrelated queue/SRC rows, review/clarification histories, learning cursor and analytical files. `relationship_visibility.json` exposes all six claims independently of numerical compilation: zero mapping links; two categorical-content visibility flags. Reported widths remain in the records even when the flag does not recognize geometry as a response shape. The isolated unreviewed compiler diagnostic was not published as a recipe.

## Bounded retrospective

One of six new units receives the advisory `site_context` scope signal: ElKadiri's agricultural-adjacency scenario. Source inspection confirms an explicitly used placement filter, not a site observation. It remains an unapproved scoping candidate with both alternative scenarios and transfer limits visible; the checker was not weakened to erase the flag. Batch number, quote, species, PICOS, direction and context checks have no flags.

Independent review corrected a misplaced selection-justification passage before admission and retained the additional metric-comparability hold. Staging context-key errors were corrected before admission. These are covered by existing provenance, context and scope rules; no new scientific extraction rule or retroactive ruleset change is claimed. The version-gate regression supplies the deterministic integration improvement.

Automated table counts are not a coverage measure: Semmens has eleven numbered tables but only five detected table blocks; Witing has one numbered table but two detected blocks. Manual inventories account for the actual objects, following existing completeness rules.

Global sweep metrics were logged. The number-provenance rate changed from 4.9% to 4.8% and verify rate remained 0.3%, across intervening unrelated work; this is not evidence that this six-unit batch improved corpus-wide quality. The global human-feedback learning cursor remains unchanged. Detailed validation and baseline limitations are recorded in `validation.json`.

## Merge repair

Integrated main commit `004c3a1` after the effect-backlog batch. The two CSV conflicts were concurrent appends: the merged register preserves all 6,142 branch evidence records and all 6,158 main records unchanged, yielding 6,164 distinct evidence IDs; the corresponding source union contains 703 records. `merge_preservation.json` records both-parent checks. Generated outputs were rebuilt from this union rather than text-merged.

The existing main lint failures were cleared with mechanical formatting, equivalent lambda-to-function conversions and one unused import removal across eight files. Independent AST comparison confirmed unchanged expressions and control flow. This is CI repair, not a viewer feature change. Original validation snapshots above describe the pre-merge batch; merge validation is recorded separately.
