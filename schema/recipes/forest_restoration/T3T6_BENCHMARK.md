# forest_restoration — generated T3/T6 vs published syntheses (benchmark, 2026-11-11)

Outside comparison for the headline rows of `schema/recipes/forest_restoration/T3_nbs_hazard_farming.csv` and `T6_nbs_scorecard.csv` (no scope, no family, farming system `all`). Seed rows are in `forest_restoration_T3_nbs_hazard_farming.seed.csv` (5) and `forest_restoration_T6_nbs_scorecard.seed.csv` (11). Each seed row is one synthesis conclusion, with a verbatim quote sliced from the cached PDF (`slice_quotes.py` → `quotes.json`; whitespace collapsed, nothing else changed). Classes follow the BANDS register (10 / 30 % change; |g| 0.2 / 0.5); a stated direction with no size is `slight` / `low`. Benchmark only — never fed to synthesis.

**Syntheses used (11):** Herath 2025 (flood SR) · FAO & CIFOR 2005 (forests and floods) · Meaza 2022 (Ethiopia catchment meta-analysis) · Farley 2005 (afforestation and water yield) · Filoso 2017 (water-yield SR) · Prevedello 2019 (forest change and temperature) · Crouzeilles 2016 and Atkinson 2022 (biodiversity meta-analyses) · Yang 2023 (erosion meta-analysis) · Bernal 2018 (carbon removal rates) · IUFRO GFEP 2020 (forests and poverty).

**Circularity warning:** every one of these is already in our evidence pool (they have live EV units for forest_restoration). Agreement below is therefore partly us agreeing with ourselves. The useful signal is where we *disagree* with a synthesis that we have already ingested — that points to weighting, not missing evidence.

## T3 — hazard (livelihood mitigation, farming system `all`)

| cell | synthesis says | we say | verdict |
|---|---|---|---|
| flood | Herath 2025: moderate (20 % more forest → ~10 % lower peak flow) | moderate / very_high | agree |
| flood | FAO-CIFOR 2005: low ("only a limited influence on major downstream flooding") | moderate / very_high | we are stronger |
| drought | Meaza 2022: low (drought effects reduced; bundled with bunds) | low / very_high | agree |
| drought | Farley 2005: negative (runoff and low flow cut; "could cause or intensify water shortages") | low / very_high | we are stronger |
| heat_stress | Prevedello 2019: low (forestation cools land surface by 0.18–0.19 °C on average) | low / very_low | agree |
| fire | — | moderate / high | not covered by syntheses |
| wind_cyclone | — | blank / very_low | not covered by syntheses |
| asset-threat rows (8 hazards) | — | various | not covered by syntheses |

## T6 — scorecard priorities

| priority | synthesis says | we say | verdict |
|---|---|---|---|
| biodiversity_priority | Crouzeilles 2016: moderate (+15–84 %, range reaches strong); Atkinson 2022: moderate (+20 %) | moderate_positive / very_high | agree |
| soil_erosion_risk | Yang 2023: strong (soil loss SMD −6.23) | strong_positive / very_high | agree |
| carbon_sequestration_potential | Bernal 2018: positive, 9.1–18.8 t CO2/ha/yr (no band → slight by rule) | slight_positive / very_high | agree (both probably understate) |
| catchment_water_yield | Farley 2005: strong negative (−44 % grassland, −31 % shrubland); Filoso 2017: slight negative (most studies show decreases) | conflicting_evidence / medium | we are weaker |
| flood_hazard | Herath 2025: moderate; FAO-CIFOR 2005: slight | moderate_positive / very_high | agree (Herath) / we are stronger (FAO-CIFOR) |
| drought_hazard | Meaza 2022: slight (bundled) | moderate_positive / high | we are stronger |
| heat_stress_hazard | Prevedello 2019: slight | slight_positive / medium | agree |
| rural_poverty | IUFRO 2020: slight, confidence low (short-term planting income; "little evidence" of poverty reduction from the forest's services) | moderate_positive / very_high | we are stronger |
| food_insecurity · production_gap · water_quality_risk · water_stress | — | various | not covered by syntheses |

## Meaningful disagreements

- **Poverty: we are clearly stronger than the main assessment.** IUFRO's global assessment finds short-term income from paid planting but little evidence that a restored forest itself reduces local poverty, with few robust counterfactual studies. We say moderate benefit at very_high confidence. Our pool is likely dominated by project reports and case studies that describe payment-phase gains; the very_high confidence in particular looks hard to defend.
- **Water yield: we blur a consistent warning.** Two syntheses (one strong, one narrative) agree that planting trees reduces water leaving the catchment. We report `conflicting_evidence` because lower-income exclosure studies (e.g. Meaza baseflow) pull the other way. The split by income group in our table carries this, but the headline row hides the main global finding; a planted-forest / regeneration split would be clearer than a headline conflict.
- **Drought: the downstream cost is not in T3.** Farley shows low flows fall even more than annual flows after afforestation, especially in dry regions. Our T3 drought cell is a positive `low` and T6 drought is `moderate_positive`; neither surfaces the downstream water-shortage risk. The only drought-positive synthesis (Meaza) is bundled with stone/soil bunds and from one country.
- **Flood: depends on which synthesis you believe for big events.** Herath (recent, quantitative) supports our moderate; FAO-CIFOR (older, policy-facing) says forests have little effect on major floods. Our class is fair for small/medium events; the statement should say it does not hold for large basin floods.
- **Carbon is probably understated on both sides.** Absolute removal rates have no strength band, so they fall to `slight` by rule. This is a band gap, not a disagreement.
- **Fire and wind are untested here.** No synthesis in the cached corpus states an overall fire or wind effect of forest restoration on livelihoods; our `moderate` fire class has no outside check.
