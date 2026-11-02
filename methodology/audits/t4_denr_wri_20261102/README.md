# DENR and WRI T4 review — 2 November 2026

This bounded batch follows [primary-guidance recovery](../t4_primary_guidance_20261102/README.md). It reviews the 15-page DENR ANR bulletin and 96-page WRI Restoration Diagnostic and adds **three unapproved T4 evidence units**. No numerical suitability function, source weight, recipe change, human approval, or T3/T6 extraction is introduced.

| Source | New evidence | Direction on canonical variable | Calibration |
|---|---|---|---|
| DENR Technical Bulletin 27 | Open/degraded forest-land host context; existing vigorous wildlings assessed for ANR | Unclear for both categorical variables | None; joint density/height/spread values retained with explicit mapping holds |
| WRI Restoration Diagnostic | Native propagule/disperser capacity supports passive regeneration | Qualitative increasing direction | None; no density, distance, score or response boundaries |

These are three expert criteria, **zero verified fitted-model uses**, one qualitative directional unit, zero executable functions and zero human approvals. The two DENR criteria overlap earlier WOCAT guidance; independence is unresolved, so they are not additional independent validation. WRI is one institutional synthesis, not 217 independent observations.

## DENR: original retained, readable derivative verified

The original publisher scan remains unchanged in the team library's `2_ForestRestoration/recovery_holds/denr_fmb_tb27_2019.pdf`. A separately published derivative adds invisible Apple Vision OCR text on pages 1–12. It preserves all 15 original pages, dimensions and visible images: original and derivative render hashes match on every page at 100 dpi, independently reproduced by the reviewer. `ocr_manifest.json` records both PDF hashes, locations, per-page image hashes and three explicit visual OCR corrections. Opening-title token coverage is 1.0. This closes the primary-document identity hold without pretending a human approved evidence.

The derivative is cached under the canonical source ID and published to `2_ForestRestoration/denr_fmb_tb27_2019.pdf`, which SRC now references. Both copies reside in the local OneDrive-backed SharePoint mirror; remote synchronization was not independently confirmed. Page anchors retain the original native page numbers. OCR is a retrieval aid, not proof of every word's accuracy. Exact admitted quotes were visually checked against the scan by root and independent reviewer.

Pages 13–15 remain image-only: rotated/dense budget and wage tables have explicit transcription holds. Their headings, row identities and role were visually reviewed; no economic cells enter EV. The model's table extraction found zero DENR tables, which is not a completeness claim. `denr_claim_inventory.json` accounts for all section-D bullets, procedural content, seven figures, monitoring fields, each of 10 regenerant examples, each of 13 invasive-species entries and economic table rows.

The page-3 source gives 600–700 vigorous wildlings/ha, 15–200 cm height and relatively well-spread wildlings as a joint ideal-site criterion. It also routes below-600 sites toward reforestation and above-700 sites toward enrichment planting. That latter statement is printed in the original and was not silently reversed. Raw values and treatment routes are preserved; no `opt_low`, `opt_high`, exclusion or monotonic density function is inferred for categorical `regeneration_potential`.

The source includes optional augmentation planting within ANR; this project's FAM excludes planting from assisted regeneration. The admitted claims isolate existing regenerants and host context. Planting, spacing, firebreak geometry and management instructions remain Module 6/scope referrals. Protected-area examples require jurisdiction-specific reconciliation and do not override legal masks. Near/adjacent ecotones remain a real, unmapped spatial criterion rather than being replaced by distance to forest.

Annex C includes actual species tolerances: Acacia auricauliformis (printed spelling) pH observations with mine/sand qualifiers; Acacia mangium poor/acid/degraded-soil tolerance; Eucalyptus camaldulensis shade, soil and drought statements. These remain explicit species-lane holds with taxonomy/attribution questions. The annex describes invasive alien plants; it is not planting advice or an ANR climate/soil envelope.

## WRI: full document accounting, readiness kept distinct

Independent review read all 96 native-page text layers and inspected relevant graphical tables plus all 11 low-text pages. Low-text pages are photographs, not missing analytical tables. One photograph's seedling-count sign remains site context. `wri_page_coverage.json`, `wri_asset_inventory.json` and `wri_low_text_image_coverage.json` record coverage; `wri_REPORT.md` provides detailed findings.

The row inventory accounts for 31 diagnostic factors across seven appearances (217 occurrences), with paired diagnostic pages and continuations. Other definition, benefit and case tables are separately inventoried. Green/yellow/red readiness and historical occurrence dots are not ecological suitability scores. Empty cells do not establish factor absence. The XLSX workbook remains paused under dataset-intake rules; companion case PDFs were not silently counted as reviewed or independent sources.

Box 5, native page 38, explicitly distinguishes passive restoration and describes recovery impeded by insufficient native propagule sources or impaired dispersers. Its contiguous quote excludes purchased nursery supply. A separate exact native heading anchors the family assignment. The new unit retains qualitative direction on regeneration capacity, authors' causal limitations and the pending VONT mapping status. It does not become a fitted response function.

Physical soil/climate/fire factors and invasive-plant/uncontrolled-grazing impediments are retained as raw use/direction claims with mapping holds: unspecified soil/climate metrics cannot be renamed pH, annual rainfall or mean annual temperature. Appendix 2 and endnotes describe real global opportunity mapping: climate/soil, potential canopy definition, ecoregions, actual canopy, cropland/settlement exclusions and pasture treatment. The 10% potential-canopy definition and 1-km map grain are retained source values, not establishment thresholds. Generic family scope, cited-primary attribution and transfer remain unresolved. Natural-ecosystem safeguards are retained separately from these map exclusions.

## Verification, review and remaining work

Both candidates files passed `EvidenceUnit` validation and the central staging gate, including page-verbatim and supporting-heading containment, numbers, context, VONT, FAM, role and ruleset. Independent review challenged lineage certainty, source-versus-project planting boundaries, missing species tolerances and appendix mapping criteria. `adversarial_resolutions.json` records the fixes; `central_flags.json` has zero new-unit flags for numbers, context, scope, species and direction.

The quote-width checker retains one advisory on the nine-word DENR land-cover anchor. It contains the complete section heading and complete categorical bullet; independent image review confirms context. It was not padded with unrelated bullets, and the advisory remains visible for human review. Literal source-line trailing whitespace in the WRI quote/supporting heading is preserved in CSV; whitespace-diff warnings are not content conflicts.

All new units use extraction ruleset v1.9.2 and `reviewer_ok=false`. Existing EV and review decisions are preserved. Both SRC records remain **in_progress** despite complete main-document coverage accounting: mapping/species/supplement work is explicitly held. Queue status is `extracted` because evidence was produced, not because every source role is complete. Ledger records only bounded verification in progress for the actual ANR-grey and passive-regeneration-tool lanes; prior search stamps remain unchanged.

Next actions are human review of three cards, exact density/height/spread and ecotone mapping decisions, species-lane follow-up, and primary-method follow-up if WRI atlas rules are needed. No automatic synthesis or numerical activation follows approval of these qualitative cards.

See `retrospective.md` and `validation.json` for measured checks and limitations.
