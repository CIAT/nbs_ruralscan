# Mangrove restoration: outside benchmark for T3/T6 (published syntheses)

Staging draft, 2026-11-11 (lane `bench_mg_wet`). This is a comparison only and must never be fed into synthesis.
The seed rows are in `mangrove_restoration_T3_nbs_hazard_farming.seed.csv` (5 rows) and
`mangrove_restoration_T6_nbs_scorecard.seed.csv` (9 rows). Every quote in their `justification` field was
sliced by a script from the cached PDF in `.cache/corpus/`. Page numbers are PDF page numbers, not printed page numbers.

**Syntheses used (5):** Narayan et al. 2016 (meta-analysis of 69 field measurements of wave reduction) ·
Spalding et al. 2014, *Mangroves for coastal defence* (review guidebook) · Su et al. 2021 (meta-analysis of
restoration outcomes) · Worthington & Spalding 2018, *Mangrove Restoration Potential* (global modelled
assessment) · IPCC 2014 Wetlands Supplement, ch. 4 Coastal Wetlands.
Two candidates were left out. Gerona-Daga 2022 counts studies but gives no conclusion about effects. Malhotra 2025
does not report mangrove-specific results.

**Grading rules.** Where a synthesis gives a size, I applied the project's size bands (`BANDS`). A percentage
above 30% or a log response ratio (lnRR) above 0.35 counts as strong (T3 `high`). Where a synthesis says something
improves but gives no size, the row is graded slight (T3 `low`), unless the synthesis itself calls the effect
large or strong. Our side is the generated headline row: no scope, no family, farming_system `all`.

## T3: hazard

| cell | syntheses say | we say (class / confidence) | verdict |
|---|---|---|---|
| wind_cyclone · livelihood | Narayan: high (mangroves cut wave height by 31%) · Spalding: high (waves "rapidly reduced") | very_high / very_high | we are stronger (by one step, broadly agree) |
| flood · livelihood | Spalding: moderate (storm surge cut by 5–50 cm per km; wide belts needed) · Worthington: low (modelled people protected) | low / high | we are weaker than Spalding; agree with Worthington |
| wind_cyclone · asset | Spalding: low (trees can be torn up in the worst storms, but this is "relatively rare") | moderate / very_high | we are stronger (we treat the planting as more fragile) |
| drought, waterlogging, sedimentation, extreme_rainfall, wave_exposure · asset | — | low or blank | not covered by syntheses |

## T6: priority

| cell | syntheses say | we say (direction / confidence) | verdict |
|---|---|---|---|
| carbon_sequestration_potential | Su: strong (lnRR 0.64 vs bare tidal flats) · IPCC: strong ("potentially large carbon removals") · Worthington: slight (global modelled totals) | moderate_positive / very_high | we are weaker |
| biodiversity_priority | Su: strong (crab production and diversity, lnRR 0.80 vs degraded stands) | strong_positive / high | agree |
| flood_hazard | Spalding: moderate ("significantly reduce flood extent", wide belts) | slight_positive / high | we are weaker |
| soil_erosion_risk | Spalding: slight (narrative, no size) | moderate_positive / very_high | we are stronger |
| water_quality_risk | Su: moderate (wastewater treatment, lnRR 0.28 vs bare tidal flats) | no class / very_low | no evidence our side |
| food_insecurity | Su: no relationship (fish production and diversity; CI spans zero) · Worthington: slight (modelled extra juvenile fish and shellfish) | slight_positive / high | agree |
| rural_poverty | — | moderate_positive / very_high | not covered by syntheses |
| production_gap · gender_inequity | — | slight_positive · slight_negative | not covered by syntheses |

## Meaningful disagreements

- **Coastal flooding: our headline is weaker, and it does not match our own family row.** Spalding says wide
  belts "significantly reduce flood extent". Our headline flood cell is `low`, and flood_hazard in T6 is only
  `slight_positive`. The tidal_coastal family row (the only mangrove family) says `very_high` for the same hazard. A
  headline that disagrees with the only family below it looks like an engine or routing problem rather than
  an evidence gap, and should be checked. Part of the cause: Spalding's surge and wave units were dropped at review,
  and its remaining units are tagged as describing existing forest, so the comparator policy keeps them out of the headline.
- **Carbon: we are one step below two of the three syntheses.** Su (strong against bare tidal flats) and the
  IPCC (potentially large removals) both point higher than our `moderate_positive`. The cause is a rule, not
  the evidence. Our pool includes Su's strong result (lnRR 0.64), but only 3 of the 22 same-direction units state
  a size. The size-sparse rule therefore caps the class at moderate (the `size_sparse` flag on the row). The
  syntheses suggest the cap understates carbon here. If Pete wants carbon at strong, the fix is to extract sizes
  (for example Bernal 2018 and Song 2023 already give tonnes per hectare), not to relax the rule.
- **Storm and wave protection: we are slightly stronger, and the syntheses describe existing forest.**
  Narayan's 31% wave-height reduction was measured in natural mangroves, and mangroves were the weakest of its
  four habitats. Spalding also mostly describes existing forests. Our `very_high` headline sits above both.
  Our own low-income and lower-middle-income scope row is only `low`, which suggests the headline strength comes
  from evidence outside our target countries.
- **How fragile the planting is.** Spalding says storm breakage is relatively rare. We rate the asset's sensitivity
  to wind and cyclones as `moderate`. Our pool includes post-hurricane die-off and planting-survival studies,
  which the coastal-defence syntheses do not address, so this difference is defensible.
- **Rural poverty has no outside check.** None of the five syntheses states a household income effect.
  Prayunita et al. 2026 (cached, not used for seed rows) says "only a small fraction of the literature provides
  empirical evidence linking these services to welfare benefits" (PDF p.2). Our `moderate_positive / very_high`
  is the cell an outside reviewer would most likely question.
- **Water quality is a gap on our side.** Su gives a moderate wastewater-treatment effect. Our row has no
  class.

## Circularity

These syntheses are also in our own evidence pool. The overlap comes from the evidence register (live units)
matched against `evidence_ids` on the headline rows:
- **Narayan 2016:** in the pool, and feeds headline T3 flood, T6 flood_hazard and T6 rural_poverty.
- **Su 2021:** in the pool, and feeds headline T6 biodiversity, carbon and rural_poverty. The biodiversity
  agreement is therefore partly circular.
- **IPCC 2014 ch. 4:** in the pool, and feeds headline T6 carbon.
- **Spalding 2014:** in the pool, but none of its live units reach a headline row (surge and wave units dropped;
  the rest are tagged as describing existing forest).
- **Worthington & Spalding 2018:** in the pool for T4 only (suitability and operational units). It is independent for T3/T6.

Agreement on a cell is therefore weak confirmation wherever the same synthesis feeds both sides. The
disagreements above are the more informative result.
