# Soil depth for in-field and microcatchment water harvesting

On 9 November 2026 Pete retained four soil-depth profiles by technique and requested a check of the spatial input before scoring. Two FAO profiles come from the same manual. The previous accepted recipe at `9e8587b6` had no depth score for either family. The reviewed inputs carry these profiles forward with scoring held.

| Technique and source | Published profile | Spatial measurement needed |
|---|---|---|
| In-field harvesting, Kahinda et al. (2008), PDF p. 3 §2.2.1.5 and p. 4 Table 5 | Below 0.2 m ranks 1, 0.2–0.3 ranks 2, 0.3–0.4 ranks 3, 0.4–0.75 ranks 4 and above 0.75 ranks 5. The printed intervals overlap at 0.3 and 0.4 m. Exactly 0.75 m ranks 4. | Sum of topsoil and subsoil horizon thicknesses. Rock depth could represent that sum only where those horizons extend to rock and the local evidence demonstrates the correspondence. |
| Contour bunds for tree planting, Critchley & Siegert (1991), §5.3, “Suitability” | Soil at least 1.5 m deep, preferably 2 m. In arid to semi-arid areas the manual also specifies 200–750 mm rain, flat to 5% slope, and even ground without gullies or rills. | Soil depth available for tree roots and storage of harvested water. A dense or cemented layer above the rock can limit the usable depth. |
| Negarim tree microcatchments, same FAO manual, §5.2, “Suitability” | At least 1.5 m, preferably 2 m. Rainfall can be as low as 150 mm/year. Slopes from flat to 5%. Uneven ground may require subdivision of the block. | Confirm usable rooting and storage depth in the planted infiltration area. The technique and receiving area matter when validating a spatial input. |
| Cultivated strips, WOCAT (2013), PDF p. 127, printed p. 114 | Soil at least 1 m deep, slope at most 4% and rainfall greater than 200 mm/year. | The guide specifies soil depth without defining its lower horizon or a bedrock contact. Document how the candidate layer represents soil depth in the cropped strip. |

At 1.2 m of **confirmed usable soil** the strip's depth condition is met while both tree techniques fall short of the FAO minimum. At 1.7 m the tree minimum is met and the preference remains unmet. Neither statement supplies a numerical suitability score.

## Dataset check

The ontology lists `ssurgo_statsgo` and `isric_soilgrids250_v2` as candidates for `soil_depth_to_bedrock`. The former ID has no T1 registry entry. Neither family has a BIND row for this variable. The SoilGrids 2.0 product describes properties for six fixed intervals down to 200 cm. A prediction in the 100–200 cm interval gives no site-specific thickness of the topsoil and subsoil, rooting depth or storage depth. ISRIC's older 2017 product separately estimated depth to the R horizon. That estimate describes another soil boundary. [SoilGrids 2.0 layer definitions](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html) · [2017 product definition](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_2017.html)

The USDA distinguishes the depth to bedrock from the depth to a root-restricting horizon, which may occur above rock. For example, a tree basin with rock at 2 m and a continuous cemented layer at 0.9 m could appear to meet FAO's preferred depth on a rock map despite less than 1.5 m available to roots. For these four profiles, equivalence remains unverified. A replacement must identify its quantity, units, restrictive horizon or other lower boundary, local coverage and soil-profile evidence supporting the technique-specific interpretation. [USDA Soil Survey Manual, chapter 3](https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf)

The [synthesis run record](soil_depth_run.json) pins sources, instructions, model settings, binding inputs and the two accepted row fingerprints.
