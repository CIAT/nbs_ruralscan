# methodology/

Written methodology for the Rural NbS Scan — the cross-cutting framework and the per-NbS recipes that parameterise it.

## Structure

| File | Contents |
|---|---|
| `framework.md` | Cross-cutting methodology — the analytical strategy that applies to all NbS. NbS-agnostic. |
| `recipes/water_harvesting.md` | Canonical recipe pattern (Benson, May 2026). Reference for all other recipes. |
| `recipes/agroforestry.md` | Pilot NbS recipe — Phase 3 deliverable. |
| `recipes/<nbs_id>.md` | One file per NbS as the catalogue grows. Use `/new-recipe <nbs_id>` in Claude Code to scaffold. |

## Authoring conventions

- Filenames in `snake_case` matching the NbS ID from T0 (e.g. `water_harvesting`, `agroforestry`, `forest_restoration`).
- Each recipe inherits the section structure of `water_harvesting.md`.
- Variables follow the six-theme grouping: topographic · hydrological · soil · climatic · LULC · socio-econ + hazard.
- Each variable in a recipe corresponds to a Variable Card — six slots: What / Why / How to read / What it represents (cluster) / Where it comes from / Membership function preview.
- Master variable tables in markdown for the document; canonical structured data lives in `schema/recipes/<nbs_id>/`.

## What lives where

- **Methodology prose** (definitions, rationale, narrative) → here.
- **Analytical rules** (response functions, thresholds, weights, datasets) → `schema/`.
- **Pipeline code** that reads schema + executes the methodology → `pipeline/`.
- **Source references** (R prototype, stocktake findings) → `reference/`.

See `CLAUDE.md` at the repo root for the architectural overview and what's locked vs open.
