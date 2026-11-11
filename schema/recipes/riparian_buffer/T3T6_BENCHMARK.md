# riparian_buffer — generated T3/T6 vs published syntheses (benchmark, 2026-11-11)

Outside comparison for the headline rows of `schema/recipes/riparian_buffer/T3_nbs_hazard_farming.csv` and `T6_nbs_scorecard.csv` (no scope, no family, farming system `all`). Seed rows are in `riparian_buffer_T3_nbs_hazard_farming.seed.csv` (2) and `riparian_buffer_T6_nbs_scorecard.seed.csv` (10). Each seed row is one synthesis conclusion with a verbatim quote sliced from the cached PDF (`slice_quotes.py` → `quotes.json`). Classes follow the BANDS register; a stated direction with no size is `slight` / `low`. Benchmark only — never fed to synthesis.

**Syntheses used (4):** Mayer 2007 (nitrogen-removal meta-analysis, 89 buffers) · Dosskey 2010 (review, chemical water quality) · Osborne & Kovacic 1993 (review, water quality and stream management) · Cole 2020 (review, ecosystem services of buffer strips). The riparian synthesis base is thin and temperate (US / UK); only one is a quantitative meta-analysis. No cached synthesis covers riparian buffers and livelihoods, income or climate hazards in low-income countries. No uncached synthesis was added.

**Circularity warning:** all four are already in our evidence pool (Cole 2020 alone has 27 EV units). Agreement is partly circular.

## T3 — hazard (livelihood mitigation)

| cell | synthesis says | we say | verdict |
|---|---|---|---|
| flood × all | Cole 2020: low (valuable for moderate floods; depends on extent, age, density) | low / medium | agree |
| heat_stress × mixed_crop_livestock | Cole 2020: low (shade and shelter alleviate livestock temperature stress) | no row | no evidence our side |
| drought · fire · wind · waterlogging | — | no rows | not covered by syntheses |

## T6 — scorecard priorities

| priority | synthesis says | we say | verdict |
|---|---|---|---|
| water_quality_risk | Mayer 2007: strong (mean 67.5 % N removed); Dosskey 2010: moderate ("substantial influence"); Cole 2020: slight (mitigate diffuse pollution) | strong_positive / very_high | agree with the meta-analysis; we are stronger than the two reviews |
| soil_erosion_risk | Osborne 1993: slight; Cole 2020: slight (both narrative: reduce sediment, stabilise banks) | moderate_positive / very_high | we are stronger |
| biodiversity_priority | Cole 2020: slight | slight_positive / very_high | agree |
| carbon_sequestration_potential | Cole 2020: strong ("extremely effective" for wooded buffers) | slight_positive / high | we are weaker |
| flood_hazard | Cole 2020: slight | slight_positive / medium | agree |
| heat_stress_hazard | Cole 2020: slight (livestock shade) | no row | no evidence our side |
| production_gap | Cole 2020: slight negative (wider buffers take land out of production) | blank class / very_low | we are weaker (no class) |

## Meaningful disagreements

- **Land taken out of production is missing.** Cole states plainly that wider buffers cut food production and cost most on productive land. Our `production_gap` row has no class. For a World Bank rural scoping tool this trade-off matters more than most benefits; it should show as a cost, not a blank.
- **Livestock heat shelter is not in our tables.** The one livelihood-hazard benefit the review names besides flood (shade and shelter for livestock) has no T3 or T6 row. It is a narrative claim from a temperate review, so only `low` / `slight`, but it is a gap.
- **Carbon: we are weaker.** Cole calls wooded buffers "extremely effective" at sequestration; we say slight. The narrow strip area means per-hectare strength and landscape total differ — worth stating which one the row means.
- **Erosion: we are stronger than the reviews.** Both reviews give direction only; our moderate class must come from primary studies with numbers (likely sediment-trapping plots). Not necessarily wrong, but the outside check does not support more than slight.
- **Water quality agrees with the only meta-analysis**, but Mayer and Dosskey both stress wide variation (buffer width, soils, groundwater paths, saturation). Our very_high confidence is at the edge of what they support.
- **Applicability:** all four syntheses are from high-income temperate settings; none checks the LIC/LMIC context the tool targets.
