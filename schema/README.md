# schema/

The analytical backbone. All analytical rules, datasets, response functions, weights — read from these tables by the pipeline. **Never hardcoded in code.**

> Schema v0.2 — 8 analytical tables (T0–T7) joined on `nbs_id` / `dataset_id` / `variable_id`, **plus an evidence &
> configuration layer** (Source / Evidence / Variable-Ontology / Subpractice-Family registers) that makes every
> T3/T4/T6 value traceable. Field-level spec: [`spec.md`](spec.md). ERD: [`design/NbS_ERD_v01.html`](design/NbS_ERD_v01.html)
> (published on the [Pages site](https://ciat.github.io/nbs_ruralscan/schema.html)). Architecture: [`../docs/pipeline.html`](../docs/pipeline.html).
> How the evidence-based tables are generated from literature: [`../methodology/T4_generation_method.md`](../methodology/T4_generation_method.md).

## Draft-0 worked examples

The first populated tables — pilot NbS **Agroforestry** and **Water Harvesting & Conservation**, sourced from the agroforestry/water-harvesting stocktake. They demonstrate the spec and are the template every subsequent NbS recipe follows. CSV + JSON for all eight tables; foreign keys validated.

- Per-NbS tables (T0, T3, T4, T6): [`recipes/agroforestry/`](recipes/agroforestry/) and [`recipes/water_harvesting_conservation/`](recipes/water_harvesting_conservation/) — each with its own README.
- Cross-NbS tables (T1, T2, T5, T7): at this schema root — `T1_data_registry.*` (21 datasets), `T2_climate_risk.*` (11 risk variables), `T5_opportunity_space.*` (14 priority layers), `T7_geographic_context.*` (15 contexts). Rows from both recipes are merged and **deduplicated** — see [`DEDUP_NOTES.md`](DEDUP_NOTES.md); shared datasets carry a unioned `nbs_ids_using`.
- Design sources archived in [`design/`](design/): the ERD, the Schema Reference docx, and the human-readable workbooks the tables were generated from.

> **Deduplication (June 2026).** The two source workbooks were authored standalone, so the water-harvesting workbook aliased shared datasets, risk variables, priority layers and geographic contexts with a `_wh` suffix. These clones have been collapsed into single shared rows so the framework layer (T1/T2/T5/T7) is one source of truth; genuinely water-specific entries were kept (with the `_wh` alias stripped). Full decision log: [`DEDUP_NOTES.md`](DEDUP_NOTES.md). One item needs methodology sign-off (Brayden): the merged T2 baseline risk weights were renormalised proportionally as a **provisional** placeholder.

## Tables

| Table | Primary purpose | Owner |
|---|---|---|
| **T0** NbS Registry | Master record per NbS, economic archetype, evidence quality | Namita |
| **T1** Data Registry | Dataset catalog, access routes, citations, limitations, hosting status | Namita + Benson |
| **T2** Climate Risk Formulation | Risk variables, hazard / exposure formula, Mode A/B toggle, double-count guard | Namita (lit) + Brayden |
| **T3** NbS × Hazard × Farming System | Qualitative mitigation potential matrix | Namita (lit) |
| **T4** Suitability Variable Mappings | Response functions, scenario flags, context overrides | Namita |
| **T5** Opportunity Space Variables | TTL-facing priority layers | Namita + Benson |
| **T6** NbS Scorecard | Likert effects, economic profile per NbS | Namita (lit) + MFL team |
| **T7** Geographic Context | AEZ, farming system, admin context definitions | Benson |

## Conventions

- **JSON and CSV — both maintained.** JSON is the machine-readable source of truth (object/list fields parsed to nested structures); CSV is the human-editing view (cells verbatim). Fix the JSON, then regenerate the CSV.
- **One folder per recipe** — `schema/recipes/<nbs_id>/` holds the tables that carry an `nbs_id` (T0, T3, T4, T6) for that NbS. Cross-NbS tables (T1, T2, T5, T7) live at the schema root.
- **Snake_case IDs throughout** — `nbs_id`, `dataset_id`, `variable_id`, `context_id`.
- **Schema migrations are PRs.** Don't add columns without an RFC issue. Don't change the meaning of an existing column.

## How the pipeline reads schema

The pipeline expects to import the schema as Python dicts (via `pandas.read_csv` or `json.load`). The reference implementation lives in `../src/nbs_ruralscan/schema_loader.py` *(to be authored)*.

Validation: every recipe's schema rows must pass validation (referential integrity across foreign keys, required field coverage, valid enum values) before pipeline execution.

## Sourcing the canonical structure

The canonical field-level definitions now live in-repo at [`spec.md`](spec.md) (ported from the v0.1 Schema Reference). The original design documents are archived under [`design/`](design/) for reference.
