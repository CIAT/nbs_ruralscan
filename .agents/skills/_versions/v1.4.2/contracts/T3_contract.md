# Extraction Contract — T3 (NbS × Hazard × Farming System)

Use this contract as instruction when extracting evidence units intended to support **T3** registry rows.

## Target Objective
T3 models the qualitative mitigation potential of a Nature-based Solution (NbS) against specific climate hazards within particular farming systems, or identifies hazards that act as direct threats to the NbS asset itself (the two-risk split).

---

## 1. Required Variables & Fields

For each extracted hazard claim, populate the following parameters under `context` or `relationship` within the `EvidenceUnit`:

### `hazard_type` (Enum)
Must map exactly to one of:
* `drought`
* `flood`
* `heat_stress`
* `fire`
* `wind_cyclone`
* `waterlogging`
* `frost`

### `farming_system` (String)
Must map to a T7 farming system class or `all`:
* `cropping_rainfed`
* `cropping_irrigated`
* `mixed_crop_livestock`
* `agro_pastoral`
* `pastoral_rangeland`
* `tree_perennial`
* `all` (holds universally)

### `risk_role` (Enum)
Classify based on what the source states:
* `livelihood_mitigation` — The NbS *mitigates* the hazard for people/livelihoods (M2 need layer).
* `asset_threat` — The hazard *threatens/damages the NbS itself* (M2b risk to investment).
* `both` — The hazard is both mitigated by and threatens the NbS.

### `mitigation_potential` (Enum)
Select the most accurate level from the 7-point scale:
* `very_high` / `high` / `moderate` / `low` / `none` / `negative` / `very_negative`
* *Note:* Use negative values where the NbS *worsens* a hazard (e.g., dense monoculture planting increasing fire risk).

---

## 2. In-Paper Evidence Guidelines

1. **Mitigation Mechanism**: Look for verbatim quotes describing *how* the NbS reduces the hazard impact (e.g. "shading reduces evapotranspiration under drought stress").
2. **Timescale of Effect**: Extract when the benefit materializes:
   * `immediate`
   * `short_term_1_3yr`
   * `medium_term_3_7yr`
   * `long_term_7yr_plus`
3. **Landscape Scale Only**: Note if the effect is only realized at the catchment/landscape scale (e.g., windbreaks need contiguous design, forest restoration for catchment hydrology) vs the individual farm scale.
