# Extraction Contract — T6 (NbS Scorecard)

Use this contract as instruction when extracting evidence units intended to support **T6** registry rows.

## Target Objective
T6 defines the qualitative and quantitative impact scorecard of the NbS (benefits, trade-offs, and costs), including cost-effectiveness denominators.

---

## 1. Required Variables & Fields

For each extracted scorecard effect or economic claim, map to the following:

### `variable_type` (Enum)
* `opportunity_space_variable` — Qualitative effect on a T5 priority.
* `climate_hazard_mitigation` — Qualitative effect on a T3 hazard.
* `economic_indicator` — Quantitative cost or revenue profile.

### `effect_direction` (Enum)
For qualitative effects:
* `strong_positive` / `moderate_positive` / `slight_positive`
* `no_relationship`
* `slight_negative` / `moderate_negative` / `strong_negative`

### `economic_indicator_type` (Enum)
For quantitative cost/effectiveness claims:
* `establishment_cost` / `recurrent_cost`
* `income_potential` / `cost_reduction` / `carbon_revenue`
* `cost_per_beneficiary` / `cost_per_hectare_restored` / `cost_per_tco2e_avoided` / `cost_per_farmer_reached`

### `economic_value_range` (Object)
Extract costs and ranges in the standard schema format:
```json
{
  "low": 200,
  "high": 1200,
  "unit": "usd_per_ha",
  "source_note": "Free-text study description/context"
}
```
*Note:* `unit` must map exactly to one of:
* `usd_per_ha`
* `usd_per_ha_yr`
* `usd_per_beneficiary`
* `usd_per_tco2e`
* `usd_per_farmer`

---

## 2. In-Paper Evidence Guidelines

1. **Effect Mechanism**: Look for quotes explaining *how/why* the NbS delivers the benefit or creates a trade-off.
2. **Conditionality**: Note constraints where the effect only holds under certain conditions (e.g. "Only where tenure security is established", "Requires extension services support").
3. **Timescale of Effect**: Immediate vs short/medium/long-term.
