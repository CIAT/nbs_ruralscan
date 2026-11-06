# Runoff dataset binding audit — 6 November 2026

**Confirmed mixed dataset identity, not a valid runoff input.** `scs_cn_runoff_composite` has HydroSHEDS/HydroBASINS name, citation, asset and preparation notes, but an SCS runoff-composite identifier/description and grid metadata. This mismatch already exists in draft-0 commit `2cd541fa15a48a692d7a721f52997cd1fa900329` (3 June 2026); it was not introduced by the recent source-review changes.

The linked asset is a watershed-polygon FeatureCollection. It supplies area/topology attributes, not runoff depth, coefficient, Curve Number or drainage density. Its `ORDER` is a classical main-stem hierarchy, not Strahler order. The polygons derive from 15 arc-second delineation; calling this a 90 m runoff grid is incorrect. See the [official Earth Engine catalogue](https://developers.google.com/earth-engine/datasets/catalog/WWF_HydroSHEDS_v1_Basins_hybas_12) and [HydroBASINS provider description](https://www.hydrosheds.org/products/hydrobasins). Provider facts and scope are recorded in `provider_checks.json`.

## Affected configuration

| Surface | Current reach | Finding |
|---|---:|---|
| Water-harvesting T4 mappings | 4 | Runoff-catchment runoff, stream order, drainage density; terracing runoff |
| Evidence IDs linked by those mappings | 12 | All remain unapproved; existing dashboard cards now high priority |
| T2 climate-risk rows | 1 | Flood-hazard runoff depth; separate cross-module follow-up, not changed here |
| VONT candidate lists | 6 | Runoff, stream order, drainage density, flood-hazard runoff depth, groundwater recharge and flood risk |
| Corresponding BIND rows | 0 | No declared matching input or override |

`consumer_trace.json` retains exact current rows and stored evidence quantities. `binding_reproduction.json` records four direct local probes. This is a configuration/consumer audit, not fresh verification of the cited research papers.

## Actual software behaviour

The BIND resolver raises a missing-binding error. The developer-contract helper catches that case and falls back to the recipe dataset, publishing the HydroBASINS asset with `needs_upload=false`, no band, no source unit and no temporal reducer. It does still warn that access has not been fetched/validated. The T4 writer takes the first VONT candidate again during regeneration; editing only recipe dataset cells would not provide a durable repair.

No incorrect raster execution was demonstrated. Geospatial acquisition remains a stub in the inspected runtime, and the current array evaluator rejects all four legacy `trapezoidal` mappings as unsupported. The confirmed fault is misleading dataset configuration and fallback metadata; this audit does not claim a bad output map was produced or that every potential consumer is safe.

## Separate scientific compatibility problem

The existing runoff-catchment `abs_min=75` / `opt_low=80` mapping cites Curve Number, runoff depth in millimetres and runoff-coefficient evidence together. Current Vema evidence describes fuzzy **input** classes, explicitly not standalone suitability thresholds; current Singh evidence retains ordinal coefficient classes without absolute/optimum bounds. Both remain cited by the older mapping. Replacing the asset cannot validate that pooled curve. The terracing 0.9 value has coefficient semantics and cannot be applied to an unspecified runoff surface either.

All source evidence, original numeric profiles, approvals and mapping values remain unchanged. No source is dropped or silently reclassified.

## Concrete review proposals

`mapping_review_proposals.json` identifies the four mappings and all 12 linked evidence IDs. Proposed containment is to mark each dataset binding unresolved until a matching quantity, unit, statistic, spatial support and transformation are specified. Preserve evidence and source values. No replacement dataset, runoff model, global conversion or new threshold is selected.

A durable repair must address the T4 association, VONT default and developer fallback together. Separate the genuine basin-context product from any future derived runoff input; do not repurpose its `ORDER` field as Strahler order. Review T2's affected reference separately. Numeric calibration and family-specific source compatibility remain independent of dataset repair.

These are **unapplied hold proposals**, placed on the existing 12 high-priority cards in [the mapped-claim dashboard queue](http://localhost:9284/dashboard.html#review-priority=t4_mapped_claims_20261106). Query requests the hold; Keep alone neither applies it nor validates the existing curve. Previous source-specific questions remain visible. All 642 queue memberships are preserved; no evidence, recipe, ontology, binding or T1/T2 record changes.

## Verification

Reproduced all four developer fallbacks and numeric-evaluator rejections locally. Independent trace checked consumer paths and six runoff-linked evidence records; source quantity statements here refer to the stored records. Preservation checks, independent review and dashboard validation results are recorded in `verification.json`. No extraction, scientific approval, learning-cursor advance or progress-ledger completion is claimed.
