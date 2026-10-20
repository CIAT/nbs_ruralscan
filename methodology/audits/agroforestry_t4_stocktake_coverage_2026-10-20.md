# Agroforestry T4 evidence coverage: return to the scoping review

20 October 2026. Requested by Pete after reviewing harmonized T4 responses.

## Scope and result

Reconciled all **23 peer-reviewed agroforestry papers** in `reference/stocktake/peer_reviewed_benchmarked.csv`, using titles rather than unchecked DOI matches. All 23 PDFs exist in the shared Stocktake Review/Manual Screening/Zotero_Full_Text_Screening/Agroforestry folder. **18 papers have a source-register entry; five have neither a source entry nor an acquisition-queue entry under their titles. Six of the 23 have evidence referenced in live T4.** This is not a count of numeric curves: Castle contributes categorical masks, and retained numeric context can still have unresolved scores.

The current harmonization page is not the evidence inventory. It displays ordinal profiles; the standalone Wotlolan slope threshold, categorical rules, species evidence and operational/priority evidence are outside that view. Singh2026 adds a numeric source beyond the original 23; Singh2024 in the stocktake is a different paper.

Method: complete register/queue/live-T4 reconciliation; targeted original-PDF methods/table checks for Chuma, Ahmad2020, Haile continuation, the five unregistered papers, Marinis, Haris, Seja, Palma and Unger; prior source audits retained for previously examined papers. This is a coverage audit, not a completed new extraction of every paper. No analytical rule or human review decision changed.

Machine-readable inventory: `pipeline/t4_audit/agroforestry/stocktake_coverage_2026-10-20.csv`. Readable/filterable view: `docs/review/t4-evidence-coverage.html`.

## Confirmed losses and recovery order

1. **Chuma2021: compilation loss.** `ev_T4_slope_chuma21_1` is human-reviewed, with numeric percentage classes, yet reconciliation calls it `qualitative_relationship`. PDF p6 Table3 gives <5%, 5–20%, >20%, with very strong/strong/moderate aptitude. Source itself labels this row “Aspects,” while directional aspect appears under “Slope orientation”; its reported suitability-index intervals overlap. A recovery must preserve those source defects, use explicit ordinal class semantics rather than interpreting overlapping index ranges as precise cardinal scores, and keep the DR Congo response separate from the India-derived pool. Table2 p5 also supplies model weights; Table3 has elevation, climate and soil classes absent from the present structured T4 surface. This is a real missed contribution, not proof all its criteria transfer globally.
2. **Haile2024: page-continuation loss.** `ev_T4_soc_haile2024_1` contains only low <0.5 and medium 0.5–0.7. PDF pp5–6 Table4 continues with high 0.7–0.75 and very high >0.75. Both pages were visually checked. Recovery adds two bands to an existing paper, not another independent source. Units and inclusive endpoints still require faithful attribution; parkland planting/regeneration and printed pH contradictions remain separate issues. Nitrogen, potassium and phosphorus rows and their model weights also need a complete inventory rather than restricting extraction to the currently selected variables.
3. **Ahmad2020: image-table loss.** PDF p10 Table2 is an image; ordinary text extraction yields only its caption. Visual review shows weights for mean annual temperature, precipitation, aridity, combined soil conditions, NDVI and slope, plus exclusion classes. Climate gradient endpoints appear, but those are not automatically physiological establishment limits or a specified interpolation function. Recover model-use/weight information and precisely described source transformations; do not fabricate a generic rainfall optimum from mapped extrema.
4. **Five papers missing from acquisition/register reconciliation.** PDFs are already available to the team, so this is not a paywall problem. Register by verified title/metadata, with shared library provenance, before extracting eligible units. See below.
5. **Rebuild model-use agreement independently of response availability.** `CV_lit_review_agroforestry.csv` reports rainfall and land cover in all 23 papers. These are legacy inventory counts, not independently verified evidence that 23 papers used those variables in suitability calculations. Keep separate: mentioned; used in model; reported a response; compiled; transferable to this system/context. Use page/code locators and independent lineages. An omitted response must not erase legitimate model-use evidence, while a mention must not become a model-use vote.

## The five missing papers

| Paper | Original-source finding | Correct route |
|---|---|---|
| Baldwin2022 | PDF p6 Table1 describes mixed pine/pasture agroforestry, cropland/open land; pp9–10 explain low-productivity land and five-acre feasibility criteria. p16 explicitly says forestry/agroforestry could occur on any existing agricultural/open land. | Recover categorical host evidence and context. Low productivity/parcel size belong to prioritization or operational feasibility. Do not import the <2% wetland/dry-dam slope criterion into agroforestry. |
| Mendonça2022 | PDF pp5–6 Table1/equation1 model natural vulnerability and restoration priorities; higher erosion risk is treated as higher restoration priority. | Register and preserve for priority/targeting methods. Do not reverse this into establishment suitability. |
| Mendonça2023 | Original PDF is MethodsX 10 (2023), article102052; stocktake incorrectly reuses the 2022 paper's DOI. It describes the related SIPA-AFS method. | Verify metadata by title using the standard metadata tool, correct stocktake provenance, connect methodological lineage. Do not count two independent confirmations of the same method. No replacement DOI is asserted here without round-trip verification. |
| Pinto2019 | PDF p4 (printed p253) describes MARZONE conservation-priority selection in existing Montado, with biodiversity, costs and planning zones. | Retain as conservation/priority evidence; observed habitat densities are not generic silvopasture establishment limits. |
| Ellis2000 | PDF pp5–7 Tables2–3 and pp10–13 describe FADSS queries against plant tolerances and management objectives. | Species-selection/tool method evidence. Climate and pH fields do not establish one universal agroforestry envelope. |

## The remembered codebase

**Castle, Miller and Wardropper: AgroforestrySuitability_GEE**

- Repository: https://github.com/saraheb3/AgroforestrySuitability_GEE
- Accompanies `castle_2025`; already catalogued separately as `saraheb3_af_midwest` and `saraheb3_af_map`. Paper and scripts are one methodological lineage, not independent corroborating studies.
- Existing cached map script: `.cache/corpus/saraheb3_af_map.txt`, registered pinned URL at commit `af338e8251c6bde4fa46caccf4e92124f80d7623`. Current repository file listing and README checked 20 October 2026.
- Map-script lines137–145 define crop/pasture/tree-crop predicates. These support family-specific host rules; they are already partly reflected in live T4.
- Lines578–579 sum nine binary tree-suitability rasters and divide by nine. Repository contains individual growth-suitability scripts for apple, black walnut, chestnut, hazelnut, pecan, persimmon, poplar, sycamore and white oak. Those are species envelopes. They deserve retained species-level evidence, not an unlabelled generic practice pH/rainfall function.
- Field-Buffer-Areas: 10 m inward field-edge strip and >=10-acre source field selection (cached lines27–30). Riparian-Buffer-Areas: 30 m source buffer (line51). These are source design choices for geometry/scenarios, not universal prescribed widths. Pete already approved variable boundary buffers.
- Overall map combines environmental priorities, species growth, social feasibility and economics (map line689). Environmental-priority sliders/weights are not T4 biophysical variable importance. Preserve analytical dimensions rather than importing the entire weighted index into T4.
- Deeper species-script extraction remains outstanding. This audit verified architecture, source files and existing cached practice-level code, not every species threshold.

## Preserved exclusions and practical expectations

Brandt remains excluded per Pete. Ahmad2017 rainfall remains excluded per Pete's explicit rejection of its narrow regional classes. Marinis Table3 (p8) scores seven separate land uses, not an integrated agroforestry system; prior scope exclusion is supported. Haris/Wotlolan crop-specific evidence and Yadav/Mushtaq species evidence remain retained in their appropriate lanes.

Expected recovery is **more complete curves, categorical support, model-use counts, and species evidence**, not 23 interchangeable global response functions. The immediate numeric win is Chuma plus the missing Haile continuation. The five registration gaps must be closed even where their eventual destination is outside T4.

Recommended next bounded implementation: recover Chuma and Haile faithfully through the existing evidence/QA pipeline; extract Ahmad2020 image-table method evidence; register/screen the five missing papers; rebuild independent model-use agreement; then audit the species scripts. Run the extraction retrospective for that recovery sweep. This report makes no claim that those recovery actions have already been applied.
