# methodology/

Rural Scan uses evidence about a practice family to scope where a nature-based solution could be considered, what risks it faces and which priorities it could support. To follow one claim through the method, start with terrace rainfall. The example shows what an analyst can report when a site lies within a documented use range and the scoring relationship still needs calibration. [Worked recipe](https://github.com/RuralScan/method/blob/9288bd55ba420350039631a2a6ac05493e0875ef/handbook/read-a-suitability-recipe.md)

## Which reference answers my question?

| Question | Reference to use |
|---|---|
| What is being scoped? | Use the module descriptions for the analytical questions and outputs. M1 scopes suitability by family, M2 examines risk to livelihoods and M2b screens risk to the investment. [Module guide](modules/README.md) · [Investment risk](modules/M2b_project_risk.md) |
| Where did a relationship come from? | Follow a T4 mapping's evidence IDs to the underlying claims, source locators and review decision. For hazard, scorecard or economic effects, use the effect synthesis method. [T4 method](T4_generation_method.md) · [T3/T6 method](T3_T6_generation_method.md) |
| Which files can I edit? | Edit source records in their CSV registers. For T4 configuration, use the declared inputs for the practice. The compiler combines those settings with reviewed evidence. Generate the typed JSON after the source edits. [Source registers](../schema/registers/) · [T4 authoring instructions](../schema/recipe_inputs/t4/README.md) |
| Which tables belong together? | Read the T0 definition, settings, generated tables and readiness reports from one recipe release ID. Consult its readiness report for scoring holds. [Recipe release guide](../docs/RECIPE_RELEASES.md) |

The early water-harvesting and agroforestry narratives document the recipe outline and rationale. For current mapping values, evidence support and readiness, use the versioned tables and reports above. The Sierra Leone examples in the early prototype documentation describe mock screens. The Haiti notebook has its own data inputs, run configuration and limitations. [Recipe narratives](recipes/) · [Prototype documentation](../docs/README.md) · [Haiti notebook](https://github.com/RuralScan/runtime/blob/e690d4e413d925c28c273945a5268ddbfb2d67cc/notebooks/01_agroforestry.ipynb)

## Structure

| File | Contents |
|---|---|
| `framework.md` | Cross-cutting methodology — the analytical strategy that applies to all NbS. NbS-agnostic. |
| `T4_generation_method.md` | **How suitability mappings (T4) are generated from literature** — evidence-first, defensible: discovery → ingestion (vectorless) → evidence registers → synthesis. Covers suitability families, `spatial_product_type`, species-vs-technology, publication-bias handling. |
| `families/` | Per-NbS **suitability-family schemes** for sign-off — subpractices grouped by dominant limiting factor, keyed to `suitability_family_id`. `families/agroforestry.md` (F1–F5) is in MFL review. |
| `examples/` | Worked gold standards (e.g. `t4_slice_agroforestry_F1_slope.md`) — one variable end-to-end with full provenance. |
| `modules/` | M0–M6 (+ M2b) module specs — per-module I/O contracts. |
| `recipes/water_harvesting.md` | May 2026 recipe narrative and outline. Consult the release for current tables. |
| `recipes/agroforestry.md` | Agroforestry recipe narrative and pilot context. |
| `recipes/<nbs_id>.md` | One file per NbS as the catalogue grows. Use `/new-recipe <nbs_id>` in Claude Code to scaffold. |

## Authoring conventions

- Filenames in `snake_case` matching the NbS ID from T0 (e.g. `water_harvesting`, `agroforestry`, `forest_restoration`).
- Each recipe inherits the section structure of `water_harvesting.md`.
- Variables follow the six-theme grouping: topographic · hydrological · soil · climatic · LULC · socio-econ + hazard.
- Each variable in a recipe corresponds to a Variable Card — six slots: What / Why / How to read / What it represents (cluster) / Where it comes from / Membership function preview.
- Use Variable Cards to explain the variables. For a calculation, read the compiled rule and its readiness from the selected release.

## What lives where

- **Methodology prose** (definitions, rationale, narrative) → here.
- **Analytical rules** (response functions, thresholds, weights, datasets) → `schema/`.
- **Pipeline code** that reads schema + executes the methodology → `pipeline/`.
- **Source references** (R prototype, stocktake findings) → `reference/`.

See `AGENTS.md` at the repo root for the architectural overview and what's locked vs open.
