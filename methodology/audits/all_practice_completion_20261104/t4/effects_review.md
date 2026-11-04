# Independent adversarial review — ElKadiri 2023 effects

Reviewer: separate T4-lane agent, 2026-11-04. Reviewed staged `effects/riparian_annagnps_elkadiri_2023__effects.json` and `effects/inventory.md` against cached primary PDF opening identity and native pp9–10,14,16–19,22; Table4 p17 additionally rendered and visually inspected. No unit edits or human approval.

## Decision: semantic HOLD for both proposed units

`ev_rip_effect_elkadiri23_s4_sediment` and `ev_rip_effect_elkadiri23_s12_sediment` have faithful numbers, provenance and baseline, but their canonical outcome mapping requires an explicit decision before ingestion.

**P1 — denominator/spatial-support mismatch with `sediment_retention`.** The VONT row defines this variable as “share of incoming sediment load retained by the buffer”; its direction-sense row likewise says “sediment trapped by the buffer”. The paper defines sediment load on p14 as annual average at the watershed outlet and distinguishes it from local field sediment yield. Table4 gives 45% and15% reduction in that outlet load compared with the same no-buffer watershed model. Those percentages are not shares of sediment incoming to the installed buffer that the buffer retains. Buffer placement and the fraction of landscape treated affect the outlet-load reduction, even at equal local trapping efficiency. Therefore `variable=sediment_retention` plus generic magnitude strength classes risks making non-comparable denominators equivalent in synthesis.

The registered aliases include “sediment reduction”, and the VONT note mentions downstream export; these make the intended broader scope ambiguous, not resolved. The units' notes candidly explain the distinction, which preserves source fidelity for a human reader but does not repair machine routing. Contract E2 prohibits nearest-variable substitution. Required resolution: explicitly ratify whether this VONT permits watershed-baseline export reductions with separately preserved denominator/scale, or provide an approved outcome mapping for this metric. Do not silently relabel as erosion hazard, soil erosion, local trapping efficiency, or invent a new ontology ID. Keep exact staged records and inventory while held; no new acquisition or deletion needed.

## Checks that pass

- **Identity:** opening title, authors and DOI identify ElKadiri et al.2023, Soil Systems7,4, DOI10.3390/soilsystems7010004. Checked cached artifact itself, not only register metadata.
- **Numbers and scenario assignment:** p19 explicitly associates scenarios4/12 with45%/15%. Table4 confirms scenario4=10m alongside agricultural fields, load113389.3Mg/year, footprint338.0ha; scenario12=60m adjoining fields above14.2Mg/ha/year, load174124.0Mg/year, footprint357.9ha. Shared baseline205880.2Mg/year, no buffer integrated. No arithmetic-derived effect substituted for published rounded values.
- **Direction:** watershed sediment export decreases; reduction magnitude increases. Positive direction is coherent if the approved variable is explicitly named as export reduction. Do not call it positive sediment load. Current cue is native and correctly describes reduction, but cannot settle the VONT denominator issue.
- **PICOS and family:** pp9–10 describe designed/established simulated buffers; scenarios1–15 represent implementation. Existing-vegetation scenario16 is distinct and remains unassigned pending establishment identity. No forced natural-regeneration reassignment.
- **Mechanism:** p18 native justification states slowing surface flow, infiltration and fine sediment deposition. It is genuinely mechanistic, separately anchored, not a bare positive rating.
- **Model limits:** no observed streamflow/sediment calibration; two-model agreement is not field validation. Channel erosion held constant. Notes preserve these limitations and model design; high extraction confidence is not high scientific credibility.
- **Baseline and framing:** correctly presence versus no-buffer model baseline, not scenario4 versus scenario12. Absolute loads and page given beside relative percentages. No fabricated hazard, significance, observed trial or width-side convention.
- **Independence:** two alternative scenarios within one model study, not two studies. Source IDs identical and notes disclose dependency; no meta-analysis vote multiplication justified. `lineage_of=null` acceptable for primary model results, provided synthesis groups by canonical source.

## Coverage assessment

Bounded batch is honestly incomplete. Inventory accounts for all16 riparian scenarios plus comparator, local-yield versus outlet-load distinction, narrative5%/6% conflict, incremental-width effects and other conservation practices. No null effect is concealed as overall zero: incremental0% does not mean zero presence effect. No source should be marked swept/extracted-complete on this batch.

Remaining Table4 rows are readable and individually contextualizable, so their deferral is an extraction-representation task rather than missing evidence or ecological uncertainty. Current explicit deferral is acceptable for a bounded batch but cannot close the all-practice pipeline. Source may supply anchored caption/header and selected row via supported separate context fields after that representation is validated; never stitch a supposedly contiguous quotation or import the whole table into every card.

## Handoff

Do not ingest these two units as analytical `sediment_retention` effects until denominator mapping is explicitly resolved. Provenance/number gates passing does not resolve semantic compatibility. Preserve staged numbers/quotes, request one shared ontology decision for this metric, then rerun central intake and synthesis checks. This reviewer grants no human QA approval.
