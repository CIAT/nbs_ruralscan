# T4 extraction and adversarial review contract — v1.6.16

Decision: Pete, 21 October 2026. Applies to extraction, verification, synthesis and human-review presentation. This supersedes instructions that discard a supported suitability direction solely because no numeric scale is available.

## Three independent assessments

1. **Variable use:** did the paper actually use this variable in its suitability calculation? Record source method, scope and any source-specific weight in `context.model_use`. Mention alone is not use. Species-selection methods, restoration-priority models and practice-level suitability remain separate lanes.
2. **Suitability direction:** does increasing the measured variable increase or decrease suitability, or is there an optimum range/non-monotonic response? Retain explicit directional evidence in `relationship.direction` (`increasing`, `decreasing`, `optimum_range`, `non_monotonic`, `unclear`). This refers to suitability as a function of the variable, not the sign of an NbS effect. Preserve the source's wording/legend, scope and provenance. Unknown direction is not evidence of no relationship. These conventions apply to new T4 extractions; do not relabel existing effect evidence.
3. **Numeric calibration:** are units, class boundaries, endpoint meanings and response scores sufficient for an executable function? If not, retain the claim and report the calibration gap. Direction-only evidence cannot create numeric scores, interpolation, exclusion cutoffs or default weights.

A claim can pass assessments 1 and 2 while assessment 3 remains unresolved. Do not drop it or label the whole claim unusable for that reason. Do not substitute a model weight for a suitability score.

## Required source-table sweep

Inventory EVERY row, including unweighted rows, combined criteria, categorical exclusions and continuations. Each row receives evidence IDs or a page-linked reason for deferral/exclusion. Existing source × variable records are not proof of complete extraction: check whether use, direction, numeric values and source context were captured before skipping. A weight-only record cannot close a row with a supported direction or response.

For graphical tables inspect caption, row labels and suitability colour key together. A raw-variable map marked low/high proves range, not suitability direction. A table explicitly mapping green to high suitability and red to low suitability can establish direction, even with no cutoffs. Record image/page provenance; preserve a distinct locator for explanatory prose when the image is on another page.

Preserve reported values even when not compilable: keep literal endpoints, units, qualifiers and unresolved scale/endpoint semantics in a source-value inventory or `context.reported_values`. Do not put map extrema into `abs_min`, `abs_max` or optimum fields without evidence they mean those things. Conflicts between table and map endpoints stay explicit.

For a group weight, record the named group and its members. Count member use only where the source shows they were used. Do not assign the entire group weight to each member or invent equal shares. No canonical variable match: retain raw property and flag ontology mapping; never silently lose the row or substitute an unrelated proxy.

## Adversarial reviewer checklist

Return separate findings for variable use, direction, numeric calibration, scope/transfer and table coverage. Challenge both unsupported additions AND omitted supported information. Ask:

- Was every row inventoried, including soil properties and unsuitable classes?
- Did extraction keep directions and source values as well as weights?
- Does the legend describe suitability rather than merely low/high measurements?
- Are shared weights kept at their stated level, and missing units/scales explicit?
- Are source-page/image references correct and distinct from explanatory prose?
- Are regional, crop/species and priority contexts kept separate?
- Does the review card explain what approval retains and what it cannot activate?

Use `relationship_missed` for omitted supported direction/response. Use `insufficient_context` when legend/caption cannot establish meaning. Lack of cutoffs alone is a calibration hold, not a reason to remove supported directional evidence. Never grant human approval on the reviewer's behalf.

## Agreement and review output

Report variable-use counts, direction counts and calibrated-function counts separately. Deduplicate by independent source lineage × variable × compatible system/context; repeated EV rows and companion publications are not extra votes. Preserve opposite directions as disagreement. Keep unreviewed and reviewed tallies distinct. A count is not a runtime weight, confidence score or percentage without an explicit eligible denominator.

Review cards must show: extracted values/direction, source-specific weight when available, intended destination, calibration/transfer holds, source table, and exact approval question. Do not ask users to approve “(none)” when direction, model use or unresolved source values were retained elsewhere.

## Ahmad 2020 worked review expectation

Table 2 supports increasing suitability with temperature, precipitation, aridity index and NDVI, and decreasing suitability with slope. Its six soil properties also carry directions: nutrient availability, nutrient retention, rooting conditions and root-zone oxygen availability increase suitability; toxicity and excess salts decrease it. Soil group weight remains combined. The table's categorical exclusions require their own mapping. These are source readings to capture and review, not globally transferable thresholds or an implicit human approval. Temperature map/table endpoint discrepancies and aridity scaling remain explicit calibration questions.
