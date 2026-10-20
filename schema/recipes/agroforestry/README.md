> **Current T4 handoff (20 October 2026):** use `T4_suitability_mappings.csv` / generated JSON: 17 rows (1 numeric, 7 categorical, 9 operational/design). See [Diego handoff](../../../handoff/agroforestry-t4/README.md). The October 19 synthesis narrative below is historical and superseded for T4; per-family synthesis JSON is not the audited live table.

# recipes/agroforestry/ — draft-0 example

**Status: draft 0 — worked example, not yet review-signed.** Populated schema tables for the pilot NbS
(Agroforestry). They demonstrate the schema spec ([`../../spec.md`](../../spec.md)) with real, sourced content,
and serve as a template for subsequent NbS recipes.

## What's here (per-NbS tables — carry `nbs_id`)

| File | Table | Rows |
|---|---|---|
| `T0_nbs_registry.{csv,json}` | T0 — NbS Registry | 1 |
| `T3_nbs_hazard_farming.{csv,json}` | T3 — NbS × Hazard × Farming (**generated**, cell synthesis) | 75 (generated; re-run 2026-10-06) |
| `T4_suitability_mappings.{csv,json}` | T4 — Suitability Mappings (**generated** for evidence rows + kept design rows) | 18 (8 evidence + 10 design; re-run 2026-10-19) |
| `T6_nbs_scorecard.{csv,json}` | T6 — NbS Scorecard (**generated**, cell synthesis) | 74 (generated; re-run 2026-10-06) |

The cross-NbS tables this recipe joins to — `T1_data_registry`, `T2_climate_risk`, `T5_opportunity_space`,
`T7_geographic_context` — live at the [schema root](../../) and merge rows from every recipe.

## T4 is generated from the QC'd evidence (2026-10-19)

`T4_suitability_mappings.csv` is written by **`scripts/synthesise-recipe.py agroforestry`** from the active
`structural_suitability` units after human QA/QC (every active unit reviewed by Namita or Pete). Per-family rows
and provenance are in `T4_agroforestry__<family>.json`. Do not hand-edit evidence rows — fix the evidence unit and
re-run. The generator keeps hand-set **design rows** it does not produce (land-cover eligibility filter,
protected-area hard exclusion, the eight M2b Stream-B scenario levers) and carries design fields
(scenario flags, future-climate links) onto regenerated rows.

**Status: thin, honest, traceable — not complete.** Of 152 active T4 units (41 sources), only 14 carry a numeric
threshold; 88 are qualitative, 27 species/crop-specific (kept out by design), 23 observed-presence. Result:

| Family | Evidence rows | Note |
|---|---|---|
| cross_family | 2 (rainfall, pH) | applies to all agroforestry |
| planted_silvoarable | 3 (slope, canopy, soil depth) | slope `abs_min` 4.6 is an artefact — see below |
| regeneration_farmland | 2 (rainfall, slope) | |
| shaded_perennial | 1 (temperature) | |
| silvopastoral · linear_boundary · homegardens_proximity | **0** | insufficient numeric evidence |

Every row is below the 20% support floor (`review_low_support` — decide & record). **Known issue:**
`ev_T4_slope_seja2022_1` encodes the lowest slope CLASS bound of the study's table (8%) as `abs_min`, which drags the
planted-silvoarable slope minimum to 4.6% — re-open in QA/QC and re-run. Routes to a complete table (raised with
Pete): expert-elicited rows for the gaps (Task H protocol, `evidence_type=expert`) and a re-read of the 88
qualitative units for stated ranges (needs T4 extraction un-paused).

The June 2026 T4 (one placeholder family, empty `evidence_ids`) is superseded; it is in git history.

## T3 / T6 are generated (2026-10-01)

`T3_nbs_hazard_farming.csv` and `T6_nbs_scorecard.csv` are **written by `scripts/synthesise-t3t6.py agroforestry`**
from the pooled `nbs_effect` / `asset_vulnerability` evidence units (method `methodology/T3_T6_generation_method.md`;
run report `T3T6_synthesis_report.json`). Do not hand-edit them — add evidence and re-run. The 17 hand-authored
seed rows from May 2026 are frozen as a **benchmark only** in
[`../../design/seed_benchmark/`](../../design/seed_benchmark/) (never fed to synthesis); the seed-vs-generated
comparison is `T3T6_BENCHMARK.md`. CSV is the source of truth and the JSON is regenerated from it (the
"fix the JSON" sentence below predates that rule).

## Provenance

Populated by Namita Joshi (May 2026) from the Rural NbS stocktake — 220 peer-reviewed papers filtered to the
23 that address agroforestry spatial prioritisation. Anchored on five High-benchmark papers: Brandt et al.
(2015), Castle et al. (2025), Mendonça et al. (2022, 2023), Palma et al. (2007).

Generated from `RuralNbS_Agroforestry_Tables_T0-T7.xlsx` (archived at [`../../design/`](../../design/)). Both
formats describe the same content: **JSON is the machine-readable source of truth; CSV is the human-editing
view.** Fix the JSON, then regenerate the CSV.

## Structure & validation status

Conformant to the **frozen v0.2 structure** ([`../../structure/columns.json`](../../structure/columns.json)).
Verify with `python3 src/nbs_ruralscan/schema_tools/structure.py schema` (expect 0 errors).

- Columns match the manifest; FKs resolve to VONT (`variable`), FAM (`suitability_family_id`), T1 (`dataset_id`).
- T2 baseline weights normalised to sum to 1.000.
- T4 `is_scenario_candidate = true` only for investment-influenceable variables (road access).

**Content still pending (not structural):**
- T4: see *T4 is generated from the QC'd evidence* above (evidence rows carry `evidence_ids`; design rows stay on the placeholder family `agroforestry__planted_silvoarable`).
- Free-text `references`/`justification` were replaced by `evidence_ids` (→ EV) in the v0.2 trim.

> Draft-0 content still needs literature-team review before the pilot review milestone.
