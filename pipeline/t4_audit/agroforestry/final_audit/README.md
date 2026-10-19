# Agroforestry T4 compilation audit — completed diagnostic and branch repairs

19 October 2026 · `codex/t4-review-oct19` · not published to main.

## Answer to the original question

The thin T4 table has several causes: genuine lack of transferable numerical rules, evidence encoded as class tables rather than four trapezoid parameters, claim loss during deduplication, crop-policy routing errors, incorrect source meanings, and incomplete screened-corpus accounting. The former eight rows were not eight defensible global suitability rules. This audit separates those causes rather than treating every retained number as a threshold.

**439 T4/M2b records reconciled** (340 structural, 99 operational). All 340 structural records have exactly one disposition in each compiler mode. **148 structural records remain active; 192 remain soft-dropped. No rows were deleted.** Earlier five corrections are approved; Pete’s latest decisions are applied: seven approvals, one hold and three soft-rejections, with original records and notes preserved.

## Before and after

| Stage | Generic numerical rows | Meaning |
|---|---:|---|
| Original compilation | 8 | Included site ranges, an allocation example, and class-table shortcuts |
| After first review and five hold approvals | 4 approved | Still included source-semantic defects beyond the first batch |
| Full audit draft | 2 | Wotlolan slope rule and unapproved Mushtaq temperature claim |
| Full audit approval-filtered candidate | 1 | Wotlolan source modelling exclusion: >35% slope, approximately 19.3 degrees |

The remaining slope row is an explicit rule used by the source's crop-suitability model, not proof of a universal agroforestry limit. Regional/family transfer still needs a documented applicability decision. Mushtaq's 20–30°C sentence is secondary, in a mulberry paper; its family/host applicability remains unresolved. Four Morus crop-lane candidate rows remain separate from the generic CSV and are not approved F5 rules. Ten original design rows are preserved in the candidate CSV.

**33 active structural records carrying class/rank/code encodings are surfaced in `class_evidence.csv` and the HTML view.** They include both general and species/crop lanes: this is an inventory, not 33 validated generic rules. Their original ranges, ranks, quotes, pages and context remain visible. Legacy encodings outside this category remain in `record_reconciliation.csv` with their untouched payloads.

## Structural disposition accounting (all-active draft)

| Disposition | Records |
|---|---:|
| QA soft-dropped | 192 |
| Unsupported numerical encoding | 45 |
| Selection-only | 23 |
| Qualitative relationship | 20 |
| Class/gate mapping needed | 17 |
| Crop scope outside permitted lane | 13 |
| Observed presence/context | 8 |
| Species scope | 7 |
| Separate crop lane | 7 |
| Selection-only or missing relationship | 6 |
| Generic parameter contributor | 2 |
| **Total** | **340** |

Unsupported numeric payloads include AHP/tool weights, scenario grids, occurrence statistics and uncalibrated classes. They are not all recoverable thresholds. `source_inventory.csv` lists source IDs and evidence IDs per family, including active counts; it does not mislabel extraction coverage as completed screening.

## Further source corrections

- **Ahmad rainfall:** original Low/Medium/High regional classes retained; >985 mm is a high rank, not an independently established global optimum.
- **Haile pH:** full regional class table retained; overlapping/reversed ranges remain explicit instead of silently repairing them or extracting one class as a generic envelope.
- **Weston:** 250–500 mm describes the Sahelian part of a region extending to Sudanian rainfall up to 1,000 mm. It is not an FMNR maximum.
- **WRI:** greatest observed spread at 400–800 mm and slower growth below 400 mm; no physiological lower or upper limit established.
- **Lohbeck-labelled source, two units:** the cached paper's discussion explicitly describes the distribution of adoption evidence and calls for research outside studied climates. Both ranges now retained as observations. The cached title/DOI match the source record; its citation author is wrong (the paper is Chomba et al.). The reciprocal `chomba_2020` record names a Lohbeck-led paper. Both citations were repaired through the project Crossref verifier: titles matched exactly, authoritative authors restored, IDs and DOI/source links retained. Round-trip results are in `metadata_verification.json`.
- **WOCAT rainfall:** Natural Environment checkboxes are site conditions, consistent with the previously approved slope correction.
- **Brandt canopy:** 10% is a Kenya policy-aligned targeting proxy for low-cover cropland, not a biophysical upper limit.
- **Sprenkle-Hyppolite canopy, two units:** expert estimates of future maximum tree cover, pooled or biome-specific; not current-canopy eligibility or one optimum band.
- **Castle:** frost-free period moved to the existing `frost_free_period` variable in days; retained as selection evidence without a threshold.

`corrections.json` stores full before records, changed fields, reasons, artifact SHA-256, page and exact quote offsets. `corrected_units.json` passed EvidenceUnit validation before replay. Source texts were cached, indexed and packaged; quotes were sliced, not retyped. The separate Codex review events do not impersonate human approval.

## Compiler repairs

1. Distinct source claims survive deduplication; narrative records cannot displace thresholds. Per-origin parameter votes remain capped.
2. F5 uses the actual crop policy ID and separates taxa. Species/crop evidence remains retained.
3. Parameter provenance and independent-source uncertainty use numerical contributors. Row `n_sources` still means variable support under the frozen schema; companion `n_parameter_sources` and `parameter_source_ids` make the distinction explicit.
4. Unknown screened corpus produces **null/blank support and corpus counts**, with `review_unknown_support`. The 20% floor cannot be evaluated. Counts in SRCH overlap and record included rather than complete screened membership; table-level searches also cannot be allocated to families by assumption. Discovery logs and acquisition queues contain useful subsets but cannot reconstruct the complete denominator.
5. `--screened-corpus` accepts a complete, provenanced source-ID manifest. Unknown IDs and supporting evidence absent from supplied membership fail. Denominator membership stays fixed across approval filtering. No inferred manifest was supplied for this audit.
6. Source tiers are normalized for T4 (`High` and `high` agree); enriched output resolves one dataset ID rather than an encoded list string.
7. Original design rows remain intact; every input record has a visible disposition. Live analytical T4 has not been replaced.

## What can and cannot be recovered automatically

**Recover now:** source classes, original numerical ranges, candidate variables, source-specific modelling choices, provenance, and explicit unresolved cases. This audit delivers those inventories and fixes deterministic losses.

**Do not infer:** normalized membership scores from ordinal labels; zero suitability from “Low”; dataset classes from unexplained numerical codes; generic practice rules from species/crop envelopes; universal rainfall limits from study domains; cross-family transfer from a broad “agroforestry” label.

Nath Table 2 (PDF p11) explicitly defines ranks 1=Very good through 5=Unsuitable; slope bands are 0–5, 5–10, 10–15, 15–20, and 20–44 degrees. These ranks and the observed domain endpoint 44 are not automatically a calibrated response curve. Temperature classes similarly cover the source domain up to 25.5°C; that endpoint is not proof of failure above it. Review source geography, dataset support and intended family before mapping these classes.

## Remaining decisions and bounded follow-ups

1. **Haile pH remains held:** nutrient-suitability rationale is supported, but source classes overlap. Pete approved Sprenkle’s pooled canopy summary for combination with other sources and excluded Brandt. The pooled Sprenkle estimate remains selection/design evidence until comparable context-specific target estimates can be synthesised; approval alone does not create a generic current-canopy cutoff.
2. **FMNR applicability:** the existing scoped Sahel pilot proposal remains open. Use observed agricultural systems and regeneration potential, not a hard 300–800 mm domain borrowed from one paper.
3. **Class calibration and cross-family transfer:** record family/context applicability and a justified membership convention before turning regional ordinal evidence into executable T4. This is a methodology decision, not a parser repair. Existing Haile transfer and cross-family decision records remain relevant.
4. **Screening membership:** recover complete source-level screened sets, including screened-out sources and cross-search deduplication. Current records support an honest “unknown,” not a recreated percentage. `source_inventory.csv` is a reconciliation seed, not the denominator.
5. **Bibliographic repair completed:** the project Crossref verifier confirmed both titles (overlap 1.0). SRC now uses authoritative citations: `chomba_2020` cites Lohbeck et al.; `lohbeck_2020` cites Chomba et al. Stable source IDs were preserved.
6. **Publication:** review final applicability, then replace live recipe through a PR. This branch audit is reviewable now; it is not a scientifically validated global suitability product.

## Reproduce

```sh
PYTHONPATH=src python scripts/synthesise-recipe.py agroforestry --output-dir pipeline/t4_audit/agroforestry/final_audit/draft --report pipeline/t4_audit/agroforestry/final_audit/draft/report.json
PYTHONPATH=src python scripts/synthesise-recipe.py agroforestry --approved-only --output-dir pipeline/t4_audit/agroforestry/final_audit/approved --report pipeline/t4_audit/agroforestry/final_audit/approved/report.json
PYTHONPATH=src python scripts/audit-t4-compilation.py agroforestry pipeline/t4_audit/agroforestry/final_audit
```

## Validation

Before this CSV import, branch validation: 363 tests passed, including generated-JSON synchronization; five dependency deprecation warnings. Schema structure: zero errors, 3,274 advisory warnings. Changed compiler and audit files pass lint and type checks. All 439 T4/M2b records reconcile exactly once in each mode; no evidence IDs deleted. CSV import applied six approvals, three holds and two soft-rejections; five earlier human approvals remain intact. Live T4 was not replaced. Generator advisory QA and learning-loop notes remain visible; passing checks does not establish global scientific applicability.

CSV-import validation: 27 review/compilation tests and four generation tests passed. Shared review-display and table-progress generators also passed synchronization checks after archiving the export in `docs/review/exports`. Exactly the eleven supplied EV records changed; their analytical relationships were unchanged. Structure: zero errors.

## Follow-up: pH rationale and chat decisions

Pete explicitly approved Sprenkle for combination with other sources and rejected Brandt; applied through the standard review importer. Latest batch: seven approved, one held, three soft-deleted. Haile remains unchanged.

Haile §3.1.1 (PDF p5) treats pH as one of five equally weighted nutrient-availability indicators, alongside N, P, K and organic carbon. Its 20% is an internal equal weight, not an empirical response coefficient. The stated basis is researcher/expert judgement, FAO plant-growth standards and reference [22]. That reference is Ahmad & Goparaju’s Dumka study, not the different Palamu paper cached under `ahmad_2017`. The Dumka publisher Table 6 assigns pH 6.6–7.3 high; 7.4–8.4 and 6.5–5.6 medium; <5.5 and >8.5 low. Haile’s four-class adaptation retains 6.6–7.3 but overlaps the alkaline classes. This supports the nutrient-availability interpretation, not a validated global pH optimum. No source bounds were silently repaired and no newly browsed source was registered as extracted evidence.

Publisher precedent: https://www.biotech-asia.org/vol14no2/geospatial-approach-for-agroforestry-suitability-mapping-to-enhance-livelihood-and-reduce-poverty-fao-based-documented-procedure-case-study-of-dumka-district-jharkhand-india/
General mechanism: https://www.fao.org/soils-portal/data-hub/soil-classification/numerical-systems/chemical-properties/en/

## Categorical class tables

`categorical_source_classes.csv` expands 63 active structural evidence records into 157 source class/gate rows (36 land-cover rows). Selection includes the class inventory plus categorical/class/ordinal variables from VONT. Named classes, source codes, ordinal bands, gates and missing encodings remain visible with family, source, scope, review status, original payload and quote. No class rank is automatically converted to a 0–1 score. `categorical_current_t4.csv` exposes the 11 currently configured land-cover classes separately. HTML: `docs/review/t4-categorical-tables.html`. The main audit regenerates both tables.

Current live `agro_land_cover_eligibility` is a preserved design row with no evidence IDs. Its description calls it an eligibility filter, but scores are graduated (tree cover 1.0, cropland 0.5). These scores are not endorsed by this audit and need an evidence-backed family-specific replacement. Ordinary tree cover cannot establish existing agroforestry. Dataset-code crosswalks and ordinal calibration remain unresolved; labels are never guessed from numeric codes. No live schema or EV modifications were made by tabulation.

Additional quality concerns surfaced without silently editing records: source-specific exclusion of shrubland/forest must not become a universal rule; Nath drainage codes require a source legend; the Singh land-cover code record repeats a soil-quality quotation; Seja allocation shares are not class memberships; Nath NDVI is tagged as land cover. These remain reviewable through original quotes and compiler dispositions.

Validation: 24 tests passed for class tabulation and T4 compilation. Every selected source record has at least one table row, and all 33 existing active class-inventory records are represented.
