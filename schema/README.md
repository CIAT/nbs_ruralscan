# schema/

The analytical backbone. All analytical rules, datasets, response functions, weights — read from these tables by the pipeline. **Never hardcoded in code.**

> Schema v0.1 — designed as 8 tables (T0–T7) joined on `nbs_id` / `dataset_id` / `variable_id`. See the ERD at [`../docs/pipeline.html`](../docs/pipeline.html) (informal) and the field-level schema reference at `2_Technical_&_Data/Claude Outputs/NbS_Schema_Reference_v01_1.docx`.

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

- **JSON or CSV** — both supported. CSV for tables that humans edit (T0, T2, T4, T5, T6); JSON for tables with nested structures (e.g. T4's `context_overrides` and `relationship_params`).
- **One folder per recipe** — `schema/recipes/<nbs_id>/` contains the rows of T0, T4, T6 for that NbS. Cross-NbS tables (T1, T7) live at the schema root.
- **Snake_case IDs throughout** — `nbs_id`, `dataset_id`, `variable_id`, `context_id`.
- **Schema migrations are PRs.** Don't add columns without an RFC issue. Don't change the meaning of an existing column.

## How the pipeline reads schema

The pipeline expects to import the schema as Python dicts (via `pandas.read_csv` or `json.load`). The reference implementation lives in `../pipeline/schema_loader.py` *(to be authored)*.

Validation: every recipe's schema rows must pass validation (referential integrity across foreign keys, required field coverage, valid enum values) before pipeline execution.

## Sourcing the canonical structure

The canonical field-level definitions live in `2_Technical_&_Data/Claude Outputs/NbS_Schema_Reference_v01_1.docx`. As the schema stabilises we'll port the definitions into a Markdown spec here (`schema/spec.md`) for in-repo discoverability.
