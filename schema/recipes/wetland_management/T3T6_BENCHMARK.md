# Wetland management: outside benchmark for T3/T6 (published syntheses)

Staging draft, 2026-11-11 (lane `bench_mg_wet`). This is a comparison only and must never be fed into synthesis.
The seed rows are in `wetland_management_T3_nbs_hazard_farming.seed.csv` (5 rows) and
`wetland_management_T6_nbs_scorecard.seed.csv` (8 rows). Every quote in their `justification` field was sliced by
a script from the cached PDF in `.cache/corpus/`. Page numbers are PDF page numbers.

**Syntheses used (6):** Kadykalo & Findlay 2016 (meta-analysis of wetland flow regulation, 28 studies) ·
Acreman & Holden 2013 (review: how wetlands affect floods) · Meli et al. 2014 (meta-analysis of 70 restoration
studies: biodiversity and ecosystem services) · Land et al. 2016 (CEE systematic review: nitrogen and phosphorus
removal in created or restored wetlands) · IPCC 2013 Wetlands Supplement (ch. 3, rewetted organic soils) · Ramsar
Global Wetland Outlook 2025. I did not use the UNEP Global Peatlands Assessment 2022 or Taillardat 2020. Their
conclusions overlap the IPCC rows, and the brief caps the list at six. Taillardat adds a methane caveat for
inland wetlands; see the bullets below.

**Grading rules.** These are the same as for mangrove. Sizes are graded on the project's size bands (above 30% =
strong). The Kadykalo row uses the authors' own word, "medium". An "improves" with no size is graded slight
(T3 `low`). Our side is the generated headline row: no scope, no family, farming_system `all`.

## T3: hazard

| cell | syntheses say | we say (class / confidence) | verdict |
|---|---|---|---|
| flood · livelihood | Kadykalo: moderate (pooled flow-regulation effect "medium") · Acreman: conflicting (floodplain wetlands reduce floods, upland wetlands generate them) | moderate / very_high | agree with Kadykalo. Acreman's split shows up only in our family rows (restoration_rewetting = low; mixed-income scope = conflicting) |
| drought · livelihood | Kadykalo: low (wetlands "augment low flows", no size) | low / low | agree |
| fire · livelihood | IPCC 2013: low (fire on rewetted peat "considered low", no size) · GWO 2025: low (rewetting "attenuates fire risk") | moderate / very_high | we are stronger |
| waterlogging, wind_cyclone · livelihood | — | no class / very_low | not covered by syntheses |
| drought, flood, fire, extreme_rainfall · asset | — | moderate, low, low, low | not covered by syntheses |

## T6: priority

| cell | syntheses say | we say (direction / confidence) | verdict |
|---|---|---|---|
| biodiversity_priority | Meli: strong ("excellent recovery", varies by organism group) | strong_positive / very_high | agree |
| water_quality_risk | Land: strong (median removal: nitrogen 37%, phosphorus 46%) | strong_positive / very_high | agree |
| flood_hazard | Kadykalo: moderate · Acreman: conflicting | moderate_positive / very_high | agree (with Kadykalo) |
| carbon_sequestration_potential | IPCC 2013: strong (rewetting cuts CO2 and N2O; can become a net sink; methane rises) | moderate_positive / very_high | we are weaker |
| catchment_water_yield | Kadykalo: conflicting (more dry-season low flow, but less total runoff and streamflow) | slight_positive / medium | we are stronger (we show only the positive half) |
| production_gap | GWO 2025: strong_negative ("large loss of arable food production"; one UK case) | conflicting_evidence / medium | the synthesis is more negative; we partly agree (we show a conflict) |
| rural_poverty | GWO 2025: slight_negative (benefits move from local farmers to distant visitors; one UK case) | conflicting_evidence / high | the synthesis is more negative; we partly agree |
| food_insecurity · soil_erosion_risk · water_stress | — | moderate_positive (all three) | not covered by syntheses |

## Meaningful disagreements

- **Fire: we are stronger than the syntheses.** Both global syntheses describe lower fire risk after rewetting
  but give no size, and the IPCC says fire risk "may still be real". Our `moderate / very_high` rests on measured
  case evidence from Indonesian peat (fire counts and burned area), which the global syntheses do not quantify.
  This is defensible, but the headline should say the evidence is mostly tropical peat.
- **Catchment water yield: the syntheses report a trade-off that our row hides.** Kadykalo finds wetlands raise
  low flows but *decrease* total runoff and streamflow. Our row is `slight_positive` and does not mention
  the drop in total yield. Downstream users who depend on total yield could be misled. Consider stating the
  trade-off in the row's conditionality, or re-reading the Kadykalo units (in our pool, but tagged as existing
  wetlands, so not in the headline).
- **Production and income: the outside view leans negative.** The Ramsar Outlook's worked case (Wicken Fen)
  reports a large loss of arable production and benefits moving away from local farmers, even though the net
  benefit to society was positive. Our `conflicting_evidence` on both cells is consistent with that. Our
  `food_insecurity = moderate_positive`, however, has no outside support, and the same case points the other
  way for drained farmland. It is a single high-income case, so this is a caution, not a correction.
- **Flood depends on wetland type.** Acreman's central message is that upland wetlands tend to generate floods
  and floodplain wetlands reduce them. Our headline `moderate / very_high` smooths over this. The family rows
  carry the difference (restoration_rewetting = `low`), so the risk is in how the headline is presented, not in the data.
- **Carbon: we are one step weaker.** The IPCC states that rewetting greatly reduces emissions and can make the
  site a net sink. Taillardat 2020 (not seeded) adds that inland wetlands can have a net warming effect over
  100 years because of methane, and advises conservation over restoration inland. Our `moderate_positive` sits
  between the two, which is defensible.

## Circularity

All six syntheses are SRC rows for this practice. The overlap comes from live evidence units matched against
`evidence_ids` on the headline rows:
- **Acreman 2013:** feeds headline T3 flood, T6 flood_hazard and T6 water_stress.
- **Meli 2014:** feeds headline T6 biodiversity and water_quality. The biodiversity agreement is partly circular.
- **Land 2016:** feeds headline T6 water_quality. The water-quality agreement is largely circular.
- **IPCC 2013 Supplement:** feeds headline T3 fire and T6 carbon.
- **GWO 2025:** feeds headline T6 biodiversity, production_gap and rural_poverty.
- **Kadykalo 2016:** in the pool (4 units), but tagged as describing existing wetlands, so it reaches family rows
  and not the headline. It is the most independent check here.

The agreements on biodiversity, water quality and flood are therefore weak confirmation, because the same
syntheses sit on both sides. The disagreements are on fire, catchment yield and food/production, and those
are the informative results.
