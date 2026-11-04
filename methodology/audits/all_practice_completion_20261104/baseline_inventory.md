# All-practice pipeline inventory — 4 November 2026

Read-only baseline: 6,171 EV records, 4,693 active, 1,478 dropped; 706 sources; 828 queue rows; 56 FAM entries in 28 families. No registers, recipes, ledger or review decisions changed. Input hashes in manifest.json; rerun build_inventory.py from any directory. Family/table CSV has 87 rows (28 registered families plus unassigned scope, three tables). T3/T6 counts represent XW candidate routes, not final synthesis eligibility; overlapping routes must not be added together.

| Practice | T4 active / reviewer_ok | T3 route candidates / reviewer_ok | T6 route candidates / reviewer_ok |
|---|---:|---:|---:|
| Agroforestry | 184 / 175 | 581 / 13 | 784 / 12 |
| Forest restoration | 138 / 3 | 305 / 1 | 447 / 1 |
| Mangrove restoration | 35 / 0 | 79 / 3 | 94 / 2 |
| Riparian buffers | 45 / 0 | 17 / 0 | 174 / 1 |
| Water harvesting | 362 / 0 | 834 / 1 | 914 / 5 |
| Wetland management | 34 / 0 | 206 / 0 | 538 / 5 |

Stored reviewer_ok is not reconstructed human consensus. 4,411 active records lack that flag: substantial approval gap, not 4,411 freshly discovered defects. Species/crop scopes and qualitative-only families remain visible separately in family_table_inventory.csv. Every literal family ledger state is retained; no inferred completion.

## Work already done — do not repeat

- WH priority five sources: 53 new unapproved units, 15 held/deferred groups; each source remains in_progress. Audit methodology/audits/wh_five_extraction_20261104/README.md.
- Riparian five methods sources: 71 main-paper pages accounted, six unapproved units; Gu/Semmens family ambiguity, ontology and supplement holds remain. Audit methodology/audits/riparian_recovery_20261104/README.md.
- FAO drylands Chapter 4: 19 pages, 72 anchored dispositions, one new unapproved unit. Other chapters deferred, not unread claim automatically eligible. Audit methodology/audits/fao_drylands_recovery_20261104/README.md.
- Clarification audit reports 47 answer-ready groups and 312 resolved groups, zero then awaiting source investigation; human decision still pending. These dated group totals are not independently refreshed here.
- Queue statuses acquired=117 and pending=42 are not unexplored-source counts. Many queue notes document zero-yield, existing holds, or already-read materials. SRC status swept=613 likewise cannot prove complete source accounting. source_work_inventory.csv retains actual blockers/notes for 189 rows.

## Next three bounded executable batches

1. **Admit two reviewed Bayard operational units.** reviewed_ready.json contains unchanged extension and family-labour claims. Body pp6–8 inspected, both native quotations exact; table marks significance at 5%, genuinely negative family-labour management coefficient retained. No existing exact IDs or same-source role/variable/quote duplicates, no existing Bayard EV review history. Parent central dry-run/ingest with --allow-operational; no human approval granted. These are M2b implementation factors, never T4 limits or nbs_effect claims.
2. **Resolve eight registered-source operational holds.** Original 10 registered-source units include the two above plus Bayard gender, Kormawa labour, Dagang capital/labour, Garbach four. Review source-native variable/direction and family mapping before ingestion. Labour demand is not automatically negative labour availability; PES incentive is not silently credit. Garbach specific linear live-fence outcomes need FAM applicability confirmation. Original staged files remain untouched; baseline_operational_holds.json records exact questions.
3. **Prepare intake for seven unregistered-source operational units.** Pattanayak five + Shrestha two: cache present, queue DOI verified, opening titles match; no author/title/DOI alias in SRC. Run promote-queue-to-src.py with explicit assessed metadata and --dry-run, then source context review and normal gates. Pattanayak is aggregate vote counting with mixed expanded conservation sample; do not count constituents again. Shrestha is expert perception from three respondents, not measured treatment effect. Preserve/substantiate its native subtropical context rather than nearest tropical label. These are bounded existing-source jobs, not new discovery.

17 original operational quotes all match native pages exactly. All 17 IDs absent from EV; no exact source+variable+role+quote duplicate. Copies and detailed checks in this directory. Provenance success is not semantic readiness: only two currently released to parent for admission.

## Structural and human holds

- Wetland coastal/tidal-marsh family remains only registered area_suitability family with zero active T4. Methodology/audits/review_readiness_20261103/README.md records no family-specific T4 search protocol. A bounded existing-corpus/seed review is needed; never manufacture calibration or remove family.
- Qualitative homegardens, treatment wetlands, rooftop harvesting and cross-family helper tags are not missing landscape surfaces requiring invented evidence.
- Proposed integrated fire management remains unregistered family/scope decision, per fire_management_stocktake_20261103. Four method candidates are not an authorised analytical family.
- Losada technical mangrove report: nine staged modelled units in shared e39_M_HELD_losada.json remain metadata-provider hold plus overlap with Menendez model. Do not treat Crossref failure as absent DOI or auto-lift human hold.
- Gu/Semmens establishment-family ambiguity, Bentrup ontology/text, WH structure-purpose and supplementary material holds remain domain/source tasks. Presentation consolidation did not approve new evidence assignment.
- Bullock 2003 wetland review has broken text layer; recover publisher-native text before extraction. Dataset/OCR adapters remain governed holds.
- Final synthesis and runtime calibration cannot follow from record totals. Preserve source lineage, review decisions, species/crop and operational routing; leave non-executable evidence visible.
