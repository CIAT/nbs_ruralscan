# Rainfall for external runoff harvesting

On 9 November 2026 Pete approved holding the shared rainfall score, retaining all four source profiles and using both published bund ranges together for trapezoidal bunds. The decision covers `water_harvesting__runoff_catchment__annual_precipitation`. It concerns this mapping’s calibration. The evidence register retains each source’s original review history.

The previous mapping used a 200 mm minimum, a 600–800 mm optimum, a 500 mm maximum and 60% uncertainty. A site receiving 700 mm consequently fell inside the optimum and above the maximum. The reviewed hold archives the original values. Direct evaluation and developer function selection are blocked while the hold is active.

| Source and locator | Practice and spatial evidence | Approved use |
|---|---|---|
| Kahinda et al. (2008), PDF p. 3 (printed p. 790), §2.2.1.2 and Table 3 | South African external-catchment suitability model. Annual rainfall with an 80% probability of exceedance. | Keep the full external-catchment ranking below, tied to that rainfall statistic. A mean annual rainfall layer cannot reproduce it. |
| Ngugi et al. (2020), PDF p. 9 Table 3 and p. 24 rainfall discussion | The study tests a pre-existing ≥200 mm sand-dam siting guideline. In the Tiva catchment sample there were no dams in the 200–400 mm band. In the 400–600 mm band only 2 of 29 had water. | Retain guideline and field observations together. The empty band has no measured success rate. The authors question the minimum and suggest considering additional criteria. |
| Critchley & Siegert (1991), §5.6.1 and §5.6.2, “Suitability” | Common crop-production sites with trapezoidal bunds capturing long-slope runoff in arid to semi-arid areas receive 250–500 mm. The manual describes low slopes, even ground inside the bund, and agricultural soil with non-cracking clay suitable for construction. | Retain the manual’s full range as guidance for trapezoidal bunds. |
| WOCAT (2013), PDF p. 86 (printed p. 73), “Water storage in soil”, trapezoidal-bund paragraph | Large trapezoidal bunds collect external upslope runoff. Published suitability range is 200–400 mm annual rainfall. The following sentence on semi-circular bunds covers a separate structure. | Retain the full range alongside Critchley & Siegert for trapezoidal bunds. |

Kahinda's printed external-catchment ranks are 1 for 0–100 mm, 2 for 100–200, 3 for 200–400, 4 for 400–600, 5 for 600–800, 3 for 800–1,000 and 1 for >1,000. Rank 1 is the lowest class. The table prints shared endpoints without an assignment convention.

For trapezoidal bunds the stated ranges overlap at **250–400 mm**. The portion below 250 mm down to 200 mm is covered only by WOCAT, and the portion above 400 mm up to 500 mm only by the FAO manual. These intervals describe the guidance available. The sources supply no common score for those intervals or measured failure probability outside them. WOCAT credits its layout figure to Oweis et al. (2012), adapted from Critchley & Siegert. That establishes shared design lineage. Independence of the rainfall estimates is unverified.

Each retained profile carries its source ID, evidence ID, locator, evidence fingerprint and cached-source SHA-256 in the [declared hold](../../../schema/recipe_inputs/t4/water_harvesting_conservation/review_holds.csv). The four source profiles contribute to the held decision. A replacement executable response requires evidence compatible with the target structure, rainfall statistic and dataset.

An approved-only rebuild reproduces the held mapping field for field. The batch updates one accepted mapping. The new declared-input layout also receives the previously approved catchment-area and drainage-density holds so subsequent builds preserve them. This batch issued no whole-practice release. The [synthesis run record](rainfall_run.json) pins the inputs, agent prompts, model settings and accepted output fingerprint.
