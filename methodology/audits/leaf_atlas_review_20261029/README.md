# LEAF and Brazil Mangrove Atlas — bounded review, 29 October 2026

Two further acquired candidates reviewed under the authorised restoration T4 recovery scope and extraction ruleset v1.8.0. This batch retains 111 LEAF configuration entries, 12 selected code blocks and 11 Atlas chapter blocks. **No SRC or EV admission, synthesis change, search-stage stamp or full-source completion is claimed.** The Atlas queue's blanket OCR blocker is corrected. Both queue rows remain acquired, with identity flags unchanged.

## LEAF

The two cached files match commit `91a8b9c3e377f0ef80847c815fd640bfafd833b6` of DunlopT/LEAF. Every supplied v2.1 configuration entry is preserved with its native line. The selected main script instead points to `LEAF_inputs_v.2.0.json`; these v2.1 defaults cannot be represented as an executed scenario. The Windows/Delft3D/BMI model was not run.

Selected establishment code retains useful variable-use and directional evidence: dry windows permit probabilistic anchoring; root-dependent shear and height-dependent erosion govern removal; prolonged inundation/desiccation can trigger seedling stress. These are stage- and species-dependent rules with cited calibration, not universal mangrove suitability curves. Balke 2015 attribution requires primary-source verification. Growth, adult mortality, functionality and external model internals remain outside this bounded review.

Eight isolated probes execute original AST blocks/functions from the pinned main file:

- Erosion formula produces centimetres, then multiplies by 100 while labelling the result metres. At 0.1-m stem height, implemented value is 301.4003 versus 0.0301400 m under the stated centimetre conversion: a factor of 10,000. This diagnoses conversion, not validation of the underlying formula.
- Erosion and shear locals retain prior thresholds when a later individual fails the formula's minimum-size condition.
- Neighbour lookup uses a copied adult-state snapshot, so a subsequent adult death does not alter the copied neighbour flag.
- Percentile helper overwrites its requested percentile between columns. It has no call in the selected main file; no runtime-output impact is claimed.
- Water-level intervals include their start and exclude their end; missing intervals return NaN.
- Recurring seasonal window correctly spans December–January.
- A six-hour dry requirement with a twelve-hour timestep floors to zero, allowing a wet cell to anchor when chance is forced to one. This is a deliberately changed configuration probe; the supplied default is twelve hours.

`behavior_probes.json` holds results; rerun `python methodology/audits/leaf_atlas_review_20261029/verify_probes.py` with NumPy and the cached pinned source. Code identity, file:line admission and species/practice mapping remain unresolved. No document-title stamp is fabricated. No upstream code was changed.

## ICMBio Atlas dos Manguezais do Brasil (2018)

Publisher PDF and team-library copy match byte-for-byte. The 179-page PDF has embedded text on 178 pages. Indexing found 28 tables and sparse-page OCR flags on pages 1, 2, 8, 10, 14, 103 and 179. Those local flags do not justify the former blanket “scanned PDF, no text layer” queue blocker.

Restoration chapter text pages 95–103 was read; title page 3 and pages 100/102 were visually checked. Other pages were indexed, not exhaustively reviewed. Full native Portuguese blocks retain hydrological restoration, degradation-barrier removal, recruitment, site-specific design, conditional planting and operational monitoring guidance. The six steps on page 102 are separated; its preceding monitoring paragraph is not stitched into those boxes.

The 26-ha Florida and <1,000-m² Florianopolis examples describe case areas, not eligibility cutoffs. Florida prose cites Coastal Resources Group 2014 while the caption cites 2015; discrepancy remains explicit. Page 102's minimum five-year monitoring and resource/tenure guidance belongs to implementation/operational review, not structural suitability.

The chapter cites Lewis 2005/2009 and Lewis & Brown 2014. Review against canonical `lewis_2005_ecological_mangrove_engineering` before admitting a separate evidence vote; no claim that this existing source covers the whole chapter. Atlas chapter claims are staged for source admission and lineage/mapping review. Absence of numerical calibration is not a reason to discard the retained qualitative directions.

## Scope and retrospective

This is artifact review and candidate staging, not an EV extraction sweep. No empty sweep metric or progress-ledger completion is written. Existing safeguards caught model-default versus practice-threshold confusion, species attribution, unit errors, stale state, shared citation lineage and a false acquisition blocker. No improvement-rate claim is made from this batch.

Across the bounded 29-candidate queue, selected-artifact review now reaches 24 candidates; five untouched candidates remain (two acquired guides and three acquisition blockers), alongside ITTO reuse and prior admission holds. This count is review coverage, not completed extraction.

Only `blocker` and `note` change on the two acquisition rows. `queue_changes.json` records before/after values. SRC, EV, analytical tables, human decisions and all other queue fields are preserved.
