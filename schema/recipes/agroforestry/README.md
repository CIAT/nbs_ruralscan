# recipes/agroforestry/ — draft-0 example

**Status: draft 0 — worked example, not yet review-signed.** Populated schema tables for the pilot NbS
(Agroforestry). They demonstrate the schema spec ([`../../spec.md`](../../spec.md)) with real, sourced content,
and serve as a template for subsequent NbS recipes.

## What's here (per-NbS tables — carry `nbs_id`)

| File | Table | Rows |
|---|---|---|
| `T0_nbs_registry.{csv,json}` | T0 — NbS Registry | 1 |
| `T3_nbs_hazard_farming.{csv,json}` | T3 — NbS × Hazard × Farming | 8 |
| `T4_suitability_mappings.{csv,json}` | T4 — Suitability Mappings | 11 |
| `T6_nbs_scorecard.{csv,json}` | T6 — NbS Scorecard | 8 |

The cross-NbS tables this recipe joins to — `T1_data_registry`, `T2_climate_risk`, `T5_opportunity_space`,
`T7_geographic_context` — live at the [schema root](../../) and merge rows from every recipe.

## Provenance

Populated by Namita Joshi (May 2026) from the Rural NbS stocktake — 220 peer-reviewed papers filtered to the
23 that address agroforestry spatial prioritisation. Anchored on five High-benchmark papers: Brandt et al.
(2015), Castle et al. (2025), Mendonça et al. (2022, 2023), Palma et al. (2007).

Generated from `RuralNbS_Agroforestry_Tables_T0-T7.xlsx` (archived at [`../../design/`](../../design/)). Both
formats describe the same content: **JSON is the machine-readable source of truth; CSV is the human-editing
view.** Fix the JSON, then regenerate the CSV.

## Structure & validation status

Conformant to the **frozen v0.2 structure** ([`../../structure/columns.json`](../../structure/columns.json)).
Verify with `python3 src/nbs_ruralscan/structure.py schema` (expect 0 errors).

- Columns match the manifest; FKs resolve to VONT (`variable`), FAM (`suitability_family_id`), T1 (`dataset_id`).
- T2 baseline weights normalised to sum to 1.000.
- T4 `is_scenario_candidate = true` only for investment-influenceable variables (road access).

**Content still pending (not structural):**
- Only the **F1 × slope** row carries real evidence (`ev_slope_nath21/zomer14/nair93`, with quotes + pages); it
  passes `--strict`. Every other row has `evidence_ids` empty pending literature extraction.
- All 11 T4 rows are tagged to the placeholder family `agroforestry__planted_silvoarable`; the full F1–F5 scheme
  awaits Namita + MFL review.
- Free-text `references`/`justification` were replaced by `evidence_ids` (→ EV) in the v0.2 trim.

> Draft-0 content still needs literature-team review before the pilot review milestone.
