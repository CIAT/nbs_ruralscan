# NbS Recipes

Per-NbS configuration of the cross-cutting methodology. One file per NbS (or NbS cluster).

## Index

| NbS | File | Cluster | Status | Lead |
|---|---|---|---|---|
| Water Harvesting & Conservation | [`water_harvesting.md`](./water_harvesting.md) | soil_water | **canonical pattern** | Benson |
| Agroforestry | [`agroforestry.md`](./agroforestry.md) | tree_based | skeleton (pilot NbS) | Benson + Namita |

> *More recipes will be added through the project as the team progresses. Use `/new-recipe <nbs_id>` in Claude Code to scaffold a new one.*

## Status legend

- **canonical pattern** — fully populated; serves as template for other recipes
- **draft** — substantive content; under team review
- **skeleton** — structure in place; content TBD
- **planned** — not yet started

## How to author a new recipe

1. Open an issue using the **NbS Recipe** template (`.github/ISSUE_TEMPLATE/recipe.md`).
2. In Claude Code, run `/new-recipe <nbs_id>` to scaffold the file with the right structure.
3. Inherit the section structure of `water_harvesting.md` — eight sections from Context & Scope through to Indicative Workflow Summary.
4. Variable Cards: six slots each (What / Why / How to read / What it represents / Where it comes from / Membership function preview).
5. Get one MFL-team reviewer (Sarah / Chris / Evert / Hannes — match by domain).
6. Raise a PR using the PR template; the structural-decisions checklist must pass.

## Cluster conventions

The NbS clusters in T0 (`cluster` field):

- `tree_based` — Agroforestry, sylvo-pastoral, agrosilvopastoral, forest restoration, forest conservation, ANR, reforestation, community forestry, woodlots, windbreaks, vegetative buffers, roadside bio-engineering, terracing with trees
- `soil_water` — Water harvesting & conservation, groundwater recharge, terracing, infiltration pits, cross-slope measures, bioengineered check-dams, conservation agriculture, mulching, ISFM, cover crops
- `wetland` — Wetland management (natural), constructed wetlands, riparian buffers, floodplain management
- `pastoral` — Rangeland restoration, grazing corridor management
- `landscape_scale` — Integrated fire management, broader cross-cutting interventions

> **Cluster discipline.** Don't put water harvesting in the wetlands cluster — they share the word "water" but solve different problems on different landscapes. Cluster assignment should reflect biophysical logic, not lexical similarity.
