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

The remaining slope row is an explicit rule used by the source's crop-suitability model, not proof of a universal agroforestry limit. Regional/family transfer still needs a documented applicability decision. Mushtaq's 20–30°C sentence is secondary, in a mulberry paper; its family/host applicability remains unresolved. Four Morus crop-lane candidate rows remain separate from the generic CSV and are not approved F5 rules. The original ten design rows were preserved at that audit stage; the categorical follow-up below retires the placeholder and carries nine other design rows plus three evidence-linked gates into the candidate CSV.

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
7. Every input record has a visible disposition. Numeric live T4 has not been replaced; the categorical follow-up below replaces its land-cover placeholder.

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


## Executable categorical gates — 19 October follow-up

The live recipe now replaces `agro_land_cover_eligibility` with three family-specific,
evidence-linked binary gates. The old row is archived in
`executable_categories/retired_placeholder.csv`. Other live numeric rows are unchanged;
the isolated numerical audit remains a separate candidate, not a deployed recipe.
The nine other design rows remain preserved. Categorical gates are protected from
replacement by numeric synthesis and have zero MCDA weight: apply them as hard masks.
Numeric threshold uncertainty buffers are blank because they do not apply to class codes.

| Family | Rule and evidence | Default execution |
|---|---|---|
| Planted silvoarable | Castle p8 (`ev_t4_land_cover_castle2025_1`): annual cropland; grassland only with confirmed managed forage without grazing | Approved evidence; conditional gate |
| Regeneration farmland | WOCAT 507 p1 (`EV_wocat_507_2019_008`): depleted/degraded farmland | Approved evidence; every positive class requires a farmland/degradation mask |
| Silvopastoral | Castle p8 (`ev_t4_land_cover_castle2025_2`): grassland with confirmed grazing system | Pending evidence review; default result unknown |
| Linear/boundary | No usable reviewed class gate | Unknown; boundary geometry required, never infer boundary area from cropland pixels |
| Shaded perennial | No reviewed generic host class gate | Unknown; observed host-crop distribution required; tree cover cannot identify crop |
| Homegardens | FAM qualitative-only | No raster eligibility surface |

Crosswalk uses ESA WorldCover 2021 v200, Product User Manual Table 3 (p15):
https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PUM_V2.0.pdf
Annual cropland is code 40; perennial woody crops belong to tree/shrub classes.
Grassland 30 includes grazed and ungrazed land. Tree cover 10 includes forest and
plantations, so cannot establish an agroforestry host. Built-up 50, permanent snow/ice
70 and permanent water 80 are excluded as incompatible with these agricultural hosts.
Other unmapped classes remain unknown, not automatically excluded.

These are explicit applicability crosswalks, not numerical suitability claims from the
papers. The WOCAT example is Kenyan; its farmland restoration applicability must not
be interpreted as globally validated regeneration performance. Each gate rests on one
source. Source approval is retained; no new human approval or support denominator was
invented. Castle silvopasture remains blocked. Other ordinal evidence remains tabulated
without invented 0–1 scores (notably Haile pH, Nath drainage and Singh texture).

### Runtime contract

`nbs_ruralscan.runtime.categorical.evaluate_family(schema_root, nbs_id, family,
datasets, masks=...)` reads generated T4, FAM and EV JSON. Dataset keys must identify the
exact codebook. Arrays must already be spatially aligned; equal shape is checked but
CRS/transform alignment remains caller responsibility. No download or host-mask derivation
is implied. Mask arrays use 1 = confirmed, 0 = absent, NaN = unknown. Their inputs must
be independently justified; never derive grazing or degradation from grassland alone.

Required mask names live in T4 `relationship_params.class_requirements`:
`managed_forage_without_grazing`, `depleted_farmland`, `degraded_farmland`,
`grazing_system_present`. Unmapped codes, missing masks/datasets and pending/dropped
or missing evidence return NaN plus a reason. `approved_only=False` allows an explicit
trial of pending evidence, never dropped evidence. Outputs preserve FAM spatial product
type. `apply_eligibility(suitability, result.values)` applies non-compensatory gates:
0 excludes, 1 keeps the independently computed suitability, unknown stays unknown.
Do not feed gates into a weighted average or count unknown as opportunity area.

```python
import numpy as np
from nbs_ruralscan.runtime.categorical import evaluate_family, apply_eligibility

result = evaluate_family(
    "schema", "agroforestry", "agroforestry__planted_silvoarable",
    {"esa_worldcover_2021": np.array([40, 30, 10, 80])},
    masks={"managed_forage_without_grazing": np.array([0, 1, 0, 0])},
)
# result.values = [1, 1, NaN, 0]
output = apply_eligibility(np.array([0.7, 0.8, 0.9, 1.0]), result.values)
# output = [0.7, 0.8, NaN, 0]
```

`executable_categories/family_execution.csv` runs every family against all eleven
WorldCover codes without auxiliary masks, exposing missing context. Regenerate it and
the browser table with `PYTHONPATH=src python scripts/tabulate-t4-classes.py`.
Per-family enriched synthesis JSON describes evidence synthesis; configured gates live
in the canonical T4 CSV/generated JSON and must be executed from that canonical table.

## Boundary and shaded-perennial follow-up

The previous coverage gap is now narrowed to **reviewable candidate mappings**, not
silently approved rules. `agro_linear_boundary_land_cover_gate` covers windbreaks and
shelterbelts on cropland/managed-pasture field boundaries. It requires an independent
`field_boundary_zone` mask, with `data_basis=observed_geometry`,
`placement=field_boundary`, `dataset_id` and `source_reference` metadata. Grassland also
requires `managed_pasture_present`. Castle's 10 m US-study buffer is preserved in the
source quote only; no global width is encoded. Contour buffers, other boundary practices
and target-country transfer remain unvalidated. Result carries `applicability_zone` and
`applicable_subpractices`; no eligible-pixel area is a planting footprint.

F5 has two candidate rows, `agro_shaded_coffee_host_gate` and
`agro_shaded_cocoa_host_gate`. They follow the existing F5 method, requiring independent
`coffee_observed_present` / `cocoa_observed_present` masks. Each mask needs metadata:
`data_basis=observed`, matching `host_crop`, `dataset_id` and `source_reference`.
Modelled allocation (including MapSPAM), niche predictions, missing provenance and the
wrong crop do not satisfy that contract. WorldCover vegetation classes only carry the
host mask; tree cover never proves crop presence. Crop-specific evaluation uses
`crop="coffee"` or `crop="cocoa"`; the default takes the binary maximum across configured
crops and retains every tied positive driver in `driver_crops`. Unknown alternatives
cannot erase a known pass; absence in one crop cannot erase an unknown alternative.

This gate implements **host-system applicability**, not shade benefit, shade deficit,
yield potential or a planting recommendation. Jezeer et al.'s existing economic EV is
linked **only as evidence of the coffee/cocoa-with-shade host system**; its economic
magnitude is never read by the gate and it remains in its original effect role. The
observed-host restriction comes from the project F5 method, not from reinterpreting the
economic paper. Mapping P1 explicitly asks for review of this methodological crosswalk.
For area reporting, require observed crop area/fraction; do not count whole mixed pixels.
No AOI layers were supplied, downloaded or derived in this follow-up.

All three new rows have `mapping_review_status=pending`. Production execution requires
both source-evidence approval and mapping approval. `approved_only=False` runs explicit
trials, still refusing dropped evidence and invalid/missing host provenance. Evidence
approval alone never clears mapping review. Existing source approvals are unchanged.
The browser table lists mapping decisions B1/P1 and links four source cards: new Castle
windbreak claim, Jezeer host-system/economic evidence, existing Castle silvopastoral hold,
and unresolved Haile pH. Other F5 crops and remaining ordinal crosswalks stay unresolved.

### Targeted extraction and retrospective

One new Castle land-cover/placement unit was extracted from a page-stamped bundle,
programmatically sliced, visually checked against PDF p8, validated as an EvidenceUnit,
and ingested through `ingest-effects-staging.py --allow-structural`. All central staging
gates passed. The source DOI/title was verified using the project's Crossref verifier;
proof is in `executable_categories/metadata_verification.json`. The Jezeer citation was
also round-trip verified and repaired in SRC, keeping its stable source ID, PDF and
existing evidence. No F5 outcome was relabelled as a structural extraction.

Reconciliation now covers 440 T4/M2b records: 341 structural, 99 operational; 149 active
structural and 192 soft-dropped. The ledger records only partial verification for the
boundary family, not a completed family sweep. No new search is claimed. The single new
claim has zero staging flags; existing source-geometry-as-global-threshold and
observed-vs-modelled distinctions are covered by the existing extraction rules. New
runtime regressions prevent modelled crop layers passing as observations, preserve crop
alternatives and enforce independent mapping review.

Sweep metrics were recorded under `agroforestry-categorical-boundary-oct19`: global
number-provenance rate 5.9%, verification rate 0.5%. Changes since the previous October 16
snapshot include unrelated intervening work; they are not attributed to this one-unit
follow-up. No review feedback cursor or human approval was advanced.


## Pete review applied — 20 October 2026 (supersedes pending policies above)

All four decisions in the categorical-followup export were applied through the review
workflow: Castle boundary and silvopastoral claims, Jezeer economic return, and Haile pH.
Jezeer remains an effect record for T6, not a hazard claim. Haile approval preserves the
quoted table; reversed/overlapping classes are not silently converted to pH thresholds.

B1: field boundaries required. Buffer width remains context-specific, derived across
publications/regions. No universal source 10 m width. Pete noted field delineation is
more practical in intensive systems than many African settings. No missing-geometry
substitution or pixel-area planting footprint.

P1: OR across suitable crop hosts. Accurate commodity maps preferred; MapSPAM allocated
crop fractions accepted for high-level scoping, explicitly labelled modelled allocation.
Masks are now `<crop>_host_fraction`, in 0–1 fraction of pixel (percent/100; crop hectares
divided by pixel hectares). Positive fraction passes the binary host gate; fractional
coverage is retained in `CategoricalResult.crop_fractions`, not used as suitability
strength. Crop identities retained; overlapping crops are not summed automatically.
Metadata requires dataset_id, source_reference, data_basis, host_crop and
unit=fraction_of_pixel. Niche predictions still do not establish existing crop presence.
Coffee/cocoa retain source identity evidence. Tea is an explicit Pete design decision;
the coffee/cocoa paper does not supply tea-specific shade response evidence. Other
suitable crops can be configured through schema, not hardcoded runtime rules.

Silvopastoral: approved grassland plus grazing requirement; Pete suggests Global Pasture
Watch and GLW4 2020 as potential input layers. No AOI data acquired or dataset binding
claimed. Remaining: boundary widths/geometry, host data, contour buffers, other crop
mappings, Nath drainage legend, Singh class crosswalk and quote mismatch, and Haile
class interpretation.


## Live promotion and dataset bindings — 20 October 2026

Approval-filtered numeric output promoted to live T4: eight stale numeric rows replaced
by one source-model slope exclusion (>19.3 degrees, converted from 35% source slope).
Seven categorical gates and nine design/operational rows retained. One-source regional
transfer remains a limitation; missing numeric evidence is not an inferred optimum.
CSV is source of truth; runtime JSON regenerated. No frozen columns changed.

Host requirements now declare `host_bindings` inside T4 relationship_params.
`runtime.host_inputs.plan_family_inputs` resolves each variable through BIND and returns
used dataset, band, upload flag and source metadata. BIND loader now retains band.
Country overrides still win; SLE cocoa upload request falls back to global MapSPAM.

MapSPAM 2020 v2r2: verified CGIAR-hosted COG physical_area/all; bands 32 Arabica,
33 Robusta, 34 cocoa, 35 tea. Both coffee components needed. Physical area / native
pixel area yields host fraction; do not use harvested-area intensity, sum all plus
irrigated/rainfed, silently clip >1, or resample hectares as if intensive. Converter
`crop_area_fraction` preserves missing components as unknown and rejects invalid extents.
Accurate commodity-map overrides must provide compatible units/provenance; resolver
does not download, normalize an unknown upload, or align raster grids automatically.

GPW v1 grassland uses publisher GEE collection and dominant_class, aligned to 2020
where combined with GLW4. GLW4 metadata corrected from obsolete 2010-paper/2015-baseline
wording to FAO 2020 data; four ruminant species identified. These sources support
management interpretation; neither supplies confirmed grazing or no-grazing masks.
Boundary zones, grazing/forage confirmation, degraded/depleted farmland remain explicit
requires_upload bindings without invented fallbacks. No AOI data run is claimed.

Verified source documentation (20 October 2026):
- https://cgiar-climate-data-hub.github.io/catalog/spam2020/
- https://digital-atlas.s3.amazonaws.com/cdh/data/mapspam2020-v2r2/crop-codes.json
- https://developers.google.com/earth-engine/datasets/catalog/projects_global-pasture-watch_assets_ggc-30m_v1_grassland_c
- https://www.fao.org/livestock-systems/global-distributions/en/
- https://cgiar-climate-data-hub.github.io/catalog/glw4-2020/

No fitness-equivalent MapSPAM 2020 GEE asset verified in this pass; hosted COG windows
provide partial reads. Source documentation and header checks establish access metadata,
not local fitness or boundary-width defaults. Dataset acquisition here is T1/BIND
configuration, not literature EV extraction from a paused CSV/XLSX dataset adapter.


## Input decision context — 20 October 2026

Seven proposed decision cards now collect definitions, source quotes, evidence limits, candidate datasets, missing-data behaviour, ownership and exact questions. Open `docs/review/t4-input-decisions.html` (linked from categorical tables). Authoring source: `executable_categories/input_decision_cards.csv`; regenerate with `python3 scripts/build-t4-input-decisions.py`.

Version `2026-10-20-v1`; proposals only, no analytical changes or approvals applied. B2 covers boundary geometry/width; G1/G2 grazing and pasture proxies; F1 ungrazed forage; D1/D2 whether WOCAT depletion/degradation descriptions justify universal FMNR gates. C1 documents the already-approved crop-host fallback and optional local refinement. Browser choices export as a separate mapping-decision CSV; they are not Evidence Register QA decisions.
