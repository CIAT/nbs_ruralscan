# First-pass dataset inputs — Diego and Brayden

27 October 2026. Applies to the approved planted-silvoarable terrain-and-soil policy. Provider documentation is checked; authenticated access and raster processing are not tested. Developer-v0.1.3 includes these details under each dataset's `documented_input`; v0.1.2 remains immutable.

## Input table

| Criterion | Provider asset and input | Transformation | Still required |
|---|---|---|---|
| Slope | `USGS/SRTMGL1_003`, `elevation` band in metres; approximately 30 m DEM | Derive slope in degrees at the derivative scale before spatial aggregation. Do not feed elevation or percent slope into degree-based curves. | Confirm native projection, coverage, neighbourhood/edge handling and aggregation method. A coarser output grid must not redefine the derivative scale. |
| SOC | `projects/soilgrids-isric/soc_mean`; concentration, not carbon stock or density | Stored dg/kg × 0.1 → g/kg. | Inspect live bands; choose soil depth and record any aggregation. Source depth compatibility remains open. |
| Soil pH | `projects/soilgrids-isric/phh2o_mean`; pH measured in water | Stored pH × 10 × 0.1 → pH units. | Inspect live bands; choose depth; confirm compatibility with the source measurement method. |

SRTM input and Earth Engine slope conventions are documented by [the dataset catalogue](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003) and [terrain API](https://developers.google.com/earth-engine/apidocs/ee-terrain-slope). SoilGrids assets and predictive means are documented by [ISRIC's GEE access guide](https://docs.isric.org/globaldata/soilgrids/access_on_gee.html); units and depth intervals by [ISRIC's layer specification](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html).

## What is resolved, and what is not

Provider asset identities and conversion factors are recorded in the existing `T1.access_params.variable_inputs` object. This is metadata for the selected dataset, not a new dataset preference or an executable depth recipe. The compiler resolves BIND first, then attaches metadata only from the winning dataset. A local dataset override cannot inherit SoilGrids scaling accidentally. `documented_input.asset` identifies the property-specific asset; the parent registry asset can remain a folder. Any explicit BIND band must be checked against this metadata; it is not automatically replaced.

SoilGrids provides 0–5, 5–15, 15–30, 30–60, 60–100 and 100–200 cm intervals. These are available options, not six selected criteria. A source review now distinguishes the following inputs:

| Study | Source input | Depth and measurement findings | Remaining limit |
|---|---|---|---|
| Nath 2021 | HWSD v1.2; main PDF pp4–5 and Table 1 p7 | Topsoil 0–30 cm; subsoil 30–100 cm. The selected topsoil SOC and pH rules retain their own branch. HWSD defines organic carbon as weight percent and pH in water. | Dataset definitions do not establish laboratory ratio/calibration or equivalence with SoilGrids predictions. Any multi-layer summary needs an explicit calculation. |
| Ahmad 2018 | IISS Bhopal soil fertility maps; main PDF pp3–4 | SOC percent and pH classes are reported. | Exact sampling depth and laboratory method are not established in the main paper. The historic IISS map link could not be retrieved; unrelated soil atlases cannot supply the missing depth. |
| Singh 2026 | NBSS & LUP soil resource data; main PDF p4 | Soil pH classes are reported. | Sampling depth and pH solution are not established in the main paper. Moderately deep/shallow soil categories describe profile depth, not sampling depth. The publisher lists a supplementary presentation; it has not been ingested or interpreted in this review. |

HWSD definitions are documented in the [official v1.2 manual](https://files.isric.org/public/documents/HWSD_Documentation.pdf), PDF pp13 and 24 (printed pp6 and 17). Source pages, file hashes, findings and remaining limits are retained in each existing evidence record's `context.soil_input_review`, propagated through synthesis into developer rows as `soil_input_reviews`, and displayed in the existing dashboard's Global synthesis view.

This resolves Nath's input definition, not compatibility of every contributor. The approved SOC and pH pools remain conditional scoping combinations with unresolved measurement compatibility. Their numeric functions, weights and human approval states have not changed. A 0–30 cm input can match Nath's depth definition only with an explicitly specified aggregation method; it must not silently become the verified depth for Ahmad or Singh.

Do not silently average all depths, combine topsoil and subsoil, treat pH as a concentration, substitute carbon stock for concentration, or assign current-year measurements to a static prediction. If a 0–30 cm summary is chosen for scoping, record it as an explicit input assumption, with its calculation and sensitivity to depth choice. Do not describe it as verified cross-paper equivalence.

## Concrete first-pass proposal (not activated)

For `planted_terrain_soil_v1`, proposal `planted_topsoil_0_30_v1` uses SoilGrids mean predictions over 0–30 cm. This is an agent-authored scoping design assumption, not a new finding or human evidence approval. It remains unselected until the implementation run explicitly records its identifier and decision reference. Neither a country argument nor an approved response function activates it.

Use the 0–5, 5–15 and 15–30 cm layers. Convert each native value once, then calculate `(5 × x0_5 + 10 × x5_15 + 15 × x15_30) / 30`. Apply the selected suitability response to that result. Missing any required layer produces unknown; do not renormalize onto the remaining depths. Keep depth aggregation distinct from spatial aggregation.

- **SOC:** this is a thickness-weighted concentration proxy in g/kg, not a soil-mass-weighted composite or carbon-stock estimate. A physical mass-weighted composite would require additional compatible inputs.
- **pH:** this is an arithmetic summary of predicted pH values, not the pH of physically mixed soil. Do not reinterpret it as hydrogen-ion concentration or claim equivalence to a laboratory composite. Matching water-based pH is necessary but does not resolve the unknown methods of every paper.
- **Sensitivity:** evaluate the same response separately at each of the three depths. Retain all three scores and unknown states; compare with the summary score. Report the range of known layer scores and missing layers, not a confidence interval. Do not choose whichever layer gives the highest suitability. This check can reveal threshold crossings but does not validate transfer to the target country.

Worked arithmetic only: SOC layers 12, 9 and 6 g/kg give 8 g/kg; pH layers 5, 6 and 7 give 6.333333 pH units. Averaging layer suitability scores is a different operation and is not this proposal. Unit scaling, depth weighting and MCDA weighting each occur once at their own stage.

The proposal lives in the existing T1 dataset metadata, scoped to its policy. The compiler checks contiguous coverage and documented intervals, derives weights from thickness and exports it under each policy criterion's `input_proposals`. No analytical rule is hardcoded in a dataset adapter. A local BIND override does not inherit this SoilGrids proposal. Numeric functions and MCDA weights remain unchanged.

## Adapter acceptance checks

1. List actual bands, projection, mask and asset/version; record retrieval time. Documentation checks are not authenticated-access tests.
2. Check conversion before response evaluation: raw SOC 75 becomes 7.5 g/kg; raw pH 65 becomes 6.5. Preserve masked/nodata values as unknown, not zero. Dataset adapters may already scale values: never scale twice.
3. Record selected depth(s), measurement method, prediction statistic and spatial aggregation. Soil uncertainty layers, where available, are distinct from cross-paper disagreement.
4. Compare canonical values with the package's exact response intervals, including boundary unknowns. Passing a unit check does not authorize regional transfer.
5. Keep host eligibility, legal exclusions, numeric scores and eligible fraction separate. Unresolved required inputs keep the output unknown.

No new source-evidence approval or country-transfer decision is requested here. Diego/Brayden own live access and implementation. Pete/domain review owns any remaining depth/measurement equivalence assumption. Soft operational factors and host datasets retain their existing contracts; this pass covers the three numeric criteria only.
