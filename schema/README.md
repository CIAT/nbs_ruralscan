# schema/

The analytical backbone. All analytical rules, datasets, response functions, weights — read from these tables by the pipeline. **Never hardcoded in code.**

> Schema v0.2 — 8 analytical tables (T0–T7) joined on `nbs_id` / `dataset_id` / `variable_id`, **plus an evidence &
> configuration layer** (Source / Evidence / Variable-Ontology / Subpractice-Family registers) that makes every
> T3/T4/T6 value traceable. Field-level spec: [`spec.md`](spec.md). ERD: [`design/NbS_ERD_v01.html`](design/NbS_ERD_v01.html)
> (published on the [Pages site](https://ciat.github.io/nbs_ruralscan/schema.html)). Architecture: [`../docs/pipeline.html`](../docs/pipeline.html).
> How the evidence-based tables are generated from literature: [`../methodology/T4_generation_method.md`](../methodology/T4_generation_method.md).

## Structure is LOCKED · content is in progress

The **column structure** of every table is frozen at `v0.3.0-structure-frozen` (v0.3.0 = large methodology batch — T5 ratification (`mcda_role` priority/descriptor + 5 themes incl. `equity_inclusion`, renamed from `equity_gender`, with `infrastructure` dropped; 11 priorities + 4 descriptors replacing draft-0 14); EO-derived farming_system vocab swap (6 classes: cropping_rainfed · cropping_irrigated · mixed_crop_livestock · agro_pastoral · pastoral_rangeland · tree_perennial — Dixon as crosswalk in FS_DIXON_CROSSWALK.md); `production_gap` variable + BIND per-farming-system examples (with v0.2.9 `band` populated); T4 method §3 + IPLC tenure/rights sources (LandMark, WWF/ICCA); T6 cost-effectiveness denominators (`cost_per_beneficiary`/`cost_per_hectare_restored`/`cost_per_tco2e_avoided`/`cost_per_farmer_reached`) + `economic_value_range` generalised to `{low,high,unit,source_note}`; M2b Stream-B operational/enabling levers + 8 T4 `operational_constraint` scenario rows. Companion docs: `methodology/opportunity_space_T5.md`, `methodology/modules/M2b_project_risk.md` §12. v0.2.9 = focused T1 reshape to unblock Brayden's data-download layer: `description` (Required), `grain_type` (Required: grid/admin/vector), `spatial_resolution_m` → Conditional (iff grid), new `admin_level` (Conditional, iff admin), `scenario_type` → Conditional (iff climate module), `geographic_coverage` is now a list of ISO3 / `global` / region tokens, new `access_params` (Optional object); BIND adds `band` field for multi-band assets; ISO3 case alignment across T1/T7/BIND (`sle` → `SLE`). v0.2.8 = T5 opportunity-space theme ratification — equity/gender is its own theme (`equity_gender`), not folded into `people_production`; pilot theme-weight defaults shift to 5 × 0.20; manifest enum-polices `T5.theme`. v0.2.7 = discovery-and-evidence-sourcing SOP: SRC fields `study_income_group` / `is_seminal` / `venue_type` to make the six-axis credibility rubric auditable; spec/method-doc reconciliation of the C/I/D rubric with the six-axis view; diamond source classes (WOCAT, EGMs, WB project evidence, ICRAF/Ecocrop/TECA) added to the seed-set rule; PRISMA-lite discovery log SOP under `methodology/discovery_logs/`. v0.2.6 = methodology sharpenings:
`suitability_dimension` sharpened with three ordered-by-changeability definitions, T4 enum_values now police
`suitability_dimension` and `relationship_type` under `--strict`, `SRC.method_type` extended with `adoption_study`
and `mel_report`. v0.2.5 added paper-first sweep fields on EV/SRC + Namita's attribution capture
(`raw_name`/`attribution`/`justification_quote`/`selection_justification`) + the immutability rule for
`canonical_variable_id`. v0.2.1–4 added the BIND registry, vocab policing, and `context_sensitivity`). The team can populate rows against it
without fear the columns will move under them. **What's locked:** the column set, required/optional/conditional/derived
status, and foreign keys — captured machine-readably in [`structure/columns.json`](structure/columns.json) (the
authoritative manifest, generated from `spec.md`). **What's still open:** the row *content* — most `evidence_ids` are
empty pending literature extraction, and the suitability-family scheme is a draft (see below).

Check any data file against the frozen structure:

```bash
python3 src/nbs_ruralscan/schema_tools/structure.py schema          # STRUCTURE only — must pass (0 errors)
python3 src/nbs_ruralscan/schema_tools/structure.py schema --strict  # + CONTENT completeness (expect gaps until populated)
```

Default run validates column conformance + FK shape (fatal). `--strict` additionally flags empty required values and
unresolved FKs — these are *expected* to be non-zero until the tables are populated. **To change the structure,** edit
`spec.md`, regenerate `structure/columns.json`, and raise an issue tagging the team — don't edit data files into a new
shape silently.

## Draft-0 worked examples

The first populated tables — pilot NbS **Agroforestry** and **Water Harvesting & Conservation**, sourced from the agroforestry/water-harvesting stocktake. They demonstrate the spec and are the template every subsequent NbS recipe follows. CSV + JSON for all eight tables, conformant to the frozen structure.

- Per-NbS tables (T0, T3, T4, T6): [`recipes/agroforestry/`](recipes/agroforestry/) and [`recipes/water_harvesting_conservation/`](recipes/water_harvesting_conservation/) — each with its own README.
- Cross-NbS tables (T1, T2, T5, T7): at this schema root — `T1_data_registry.*` (21 datasets), `T2_climate_risk.*` (11 risk variables), `T5_opportunity_space.*` (14 priority layers), `T7_geographic_context.*` (15 contexts). Rows from both recipes are merged and **deduplicated** — see [`DEDUP_NOTES.md`](DEDUP_NOTES.md). (Which NbS use a shared dataset is now derived from the T2/T4 joins, not stored.)
- Evidence & configuration registers (cross-NbS): [`registers/`](registers/) — `VONT` (canonical variables), `FAM` (subpractice / suitability families), `SRC` (source register), `EV` (atomic evidence units), and `BIND` (context-aware variable→dataset binding: global default + country/AEZ overrides; `requires_upload` flags better local data to supply).
- Design sources archived in [`design/`](design/): the ERD, the Schema Reference docx, and the human-readable workbooks the tables were generated from.

**Draft-0 content caveats (not structural):** Only the **agroforestry F1 × slope** row is a fully-populated, `--strict`-passing chain (T4 → 3 `EV` units with quotes/pages → `SRC`, keyed to family `agroforestry__planted_silvoarable`, variable `slope` in `VONT`). Every other row is structure-conformant with `evidence_ids` pending. All draft-0 T4 rows are currently tagged to a single placeholder family per NbS; the full family scheme (F1–F5) awaits Namita + MFL review.

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

- **CSV is the source of truth; JSON is generated.** Edit the CSV (cells verbatim — object/list fields as JSON literals); the typed JSON the code reads is generated from it. **Never hand-edit the JSON.** After editing a CSV run `python3 src/nbs_ruralscan/schema_tools/generate.py schema` (CI fails on stale JSON via `--check`).
- **One folder per recipe** — `schema/recipes/<nbs_id>/` holds the tables that carry an `nbs_id` (T0, T3, T4, T6) for that NbS. Cross-NbS tables (T1, T2, T5, T7) live at the schema root.
- **Snake_case IDs throughout** — `nbs_id`, `dataset_id`, `variable_id`, `context_id`.
- **Schema migrations are PRs.** Don't add columns without an RFC issue. Don't change the meaning of an existing column.

## How the pipeline reads schema

The pipeline expects to import the schema as Python dicts (via `pandas.read_csv` or `json.load`). The reference implementation lives in `../src/nbs_ruralscan/runtime/schema_loader.py` *(to be authored)*.

Validation: `src/nbs_ruralscan/schema_tools/structure.py` checks every data file against the frozen manifest
([`structure/columns.json`](structure/columns.json)) — column conformance + FK shape (always), and required-value /
FK completeness (under `--strict`). Run it before any PR that touches `schema/`; wire it into CI.

## Sourcing the canonical structure

The canonical field-level definitions now live in-repo at [`spec.md`](spec.md) (ported from the v0.1 Schema Reference). The original design documents are archived under [`design/`](design/) for reference.
