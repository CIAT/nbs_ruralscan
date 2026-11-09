# Climate evidence for in-field water harvesting

Pete approved this block on 9 November 2026. It applies to the in-field family of water harvesting and conservation. The six-practice baseline at `f75e54c7` omitted these two mappings. Explicit holds preserve the reviewed profiles when compiling future recipes.

| Source | Retained evidence | Application |
|---|---|---|
| Kahinda et al. (2008), PDF p. 3, §2.2.1.2 and Table 3, in-field column | Annual rainfall with 80% probability of exceedance. Classes in mm are 0–100, 100–200, 200–400, 400–600, 600–800, 800–1,000 and >1,000. Ranks in order are 1, 2, 5, 4, 3, 3 and 1. | Hold the calculation until a layer measures the study statistic. A site with 300 mm mean annual rainfall and 150 mm exceeded in 8 of 10 years falls in the study’s rank-2 band. Applying the mean would incorrectly assign rank 5. |
| Critchley & Siegert (1991), §5.3.2, “Suitability” | Tree-planting contour bunds in arid to semi-arid conditions. Rainfall 200–750 mm, soils at least 1.5 m deep and preferably 2 m, flat to 5% slope, even terrain without gullies or rills. | Keep this as a conditional recommendation for the specified structure and use. |
| Kahinda et al. (2008), PDF p. 3, §§2.2.1.1–2.2.1.2 and Table 2, in-field column | Precipitation divided by potential evapotranspiration. The five published bands <0.05, 0.05–0.2, 0.2–0.5, 0.5–0.65 and >0.65 receive ranks 1, 4, 5, 3 and 1. | Preserve the ranks. At 0.70 the source assigns rank 1. Its conversion to a numeric map score remains open. |
| FAO, *Sustainable Land Management in Practice* (2011), PDF pp. 74–75, conservation agriculture | Reduced tillage and soil cover or mulch are relevant to the registered conservation tillage/mulching subpractice. Benefits can be greater under low or uneven rainfall. | Keep qualitative subpractice guidance. The passage provides no quantitative aridity response. This supersedes the proposed wrong-practice drop. |

Kahinda offers **one climate input**, chosen from rainfall and aridity. The two tables are alternative representations from one model. If both become usable later, select at most one for that application and record the choice. Printed shared endpoints in both tables retain their source ambiguity. Rank 1 signifies the lowest published rank. Converting it to zero suitability requires a separate decision.

The machine-readable [synthesis run record](in_field_climate_run.json) identifies the exact sources, instructions, model settings and compiler outputs used in this block.
