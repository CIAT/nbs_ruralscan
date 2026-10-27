# First-pass dataset inputs — Diego and Brayden

27 October 2026. Applies to the approved planted-silvoarable terrain-and-soil policy. Provider documentation is checked; authenticated access and raster processing are not tested. Existing developer-v0.1.2 remains immutable. Current compiler exports these details under each dataset's `documented_input`; rebuild from this revision to include them.

## Input table

| Criterion | Provider asset and input | Transformation | Still required |
|---|---|---|---|
| Slope | `USGS/SRTMGL1_003`, `elevation` band in metres; approximately 30 m DEM | Derive slope in degrees at the derivative scale before spatial aggregation. Do not feed elevation or percent slope into degree-based curves. | Confirm native projection, coverage, neighbourhood/edge handling and aggregation method. A coarser output grid must not redefine the derivative scale. |
| SOC | `projects/soilgrids-isric/soc_mean`; concentration, not carbon stock or density | Stored dg/kg × 0.1 → g/kg. | Inspect live bands; choose soil depth and record any aggregation. Source depth compatibility remains open. |
| Soil pH | `projects/soilgrids-isric/phh2o_mean`; pH measured in water | Stored pH × 10 × 0.1 → pH units. | Inspect live bands; choose depth; confirm compatibility with the source measurement method. |

SRTM input and Earth Engine slope conventions are documented by [the dataset catalogue](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003) and [terrain API](https://developers.google.com/earth-engine/apidocs/ee-terrain-slope). SoilGrids assets and predictive means are documented by [ISRIC's GEE access guide](https://docs.isric.org/globaldata/soilgrids/access_on_gee.html); units and depth intervals by [ISRIC's layer specification](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html).

## What is resolved, and what is not

Provider asset identities and conversion factors are recorded in the existing `T1.access_params.variable_inputs` object. This is metadata for the selected dataset, not a new dataset preference or an executable depth recipe. The compiler resolves BIND first, then attaches metadata only from the winning dataset. A local dataset override cannot inherit SoilGrids scaling accidentally. `documented_input.asset` identifies the property-specific asset; the parent registry asset can remain a folder. Any explicit BIND band must be checked against this metadata; it is not automatically replaced.

SoilGrids provides 0–5, 5–15, 15–30, 30–60, 60–100 and 100–200 cm intervals. These are available options, not six selected criteria. The older registry note suggesting 0–30 cm does not establish source-equivalent depth. Current evidence records identify Nath's topsoil branch, but the pooled record excerpts do not consistently establish an exact depth for Ahmad, Nath and Singh or a shared pH laboratory method. This metadata pass does not resolve that scientific compatibility question.

Do not silently average all depths, combine topsoil and subsoil, treat pH as a concentration, substitute carbon stock for concentration, or assign current-year measurements to a static prediction. If a 0–30 cm summary is chosen for scoping, record it as an explicit input assumption, with its calculation and sensitivity to depth choice. Do not describe it as verified cross-paper equivalence.

## Adapter acceptance checks

1. List actual bands, projection, mask and asset/version; record retrieval time. Documentation checks are not authenticated-access tests.
2. Check conversion before response evaluation: raw SOC 75 becomes 7.5 g/kg; raw pH 65 becomes 6.5. Preserve masked/nodata values as unknown, not zero. Dataset adapters may already scale values: never scale twice.
3. Record selected depth(s), measurement method, prediction statistic and spatial aggregation. Soil uncertainty layers, where available, are distinct from cross-paper disagreement.
4. Compare canonical values with the package's exact response intervals, including boundary unknowns. Passing a unit check does not authorize regional transfer.
5. Keep host eligibility, legal exclusions, numeric scores and eligible fraction separate. Unresolved required inputs keep the output unknown.

No new source-evidence approval or country-transfer decision is requested here. Diego/Brayden own live access and implementation. Pete/domain review owns any remaining depth/measurement equivalence assumption. Soft operational factors and host datasets retain their existing contracts; this pass covers the three numeric criteria only.
