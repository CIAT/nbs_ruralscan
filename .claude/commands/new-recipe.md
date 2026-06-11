---
description: Scaffold a new NbS recipe with the standard structure and starter files
---

You are creating a new NbS recipe for the Rural NbS Scan project.

The user will give you an NbS ID in `snake_case` (e.g. `agroforestry`, `forest_restoration`, `riparian_buffer`). If they didn't, ask for it.

Scaffold the following:

1. **Create** `methodology/recipes/<nbs_id>.md` using the structure of `methodology/recipes/water_harvesting.md` (or, if that doesn't exist, the Variable Card schema in AGENTS.md). Pre-fill the front-matter with the NbS ID; leave content sections marked `TODO`. The six-theme master variable table structure must be present even if empty.

2. **Create** `schema/recipes/<nbs_id>/` folder with placeholder CSV files:
   - `T0_nbs_registry.csv` — one row for this NbS
   - `T4_suitability_variables.csv` — empty with headers from AGENTS.md schema description
   - `T6_scorecard.csv` — empty with headers

3. **Pre-populate `T0_nbs_registry.csv`** with one row including the NbS ID, default cluster (ask user if uncertain), economic archetype placeholder, evidence quality `emerging`, is_active `false` (set true after recipe review), created date, updated_by current user.

4. **Add an entry to the recipe index** in `methodology/recipes/README.md` (create the file if missing). Status should be `draft`.

5. **Create a GitHub issue** body the user can paste, using the **NbS Recipe** template structure from `.github/ISSUE_TEMPLATE/recipe.md`. Pre-fill the NbS name, ID, cluster. Leave reviewer assignment for the user.

6. **Confirm to the user** what was created, what the next step is (populate the master variable table), and remind them to assign an MFL reviewer.

Structural rules to respect:
- Follow the six-theme structure (topographic · hydrological · soil · climatic · LULC · socio-econ + hazard)
- Don't hardcode variable lists — they live in the schema CSV
- Variable cards inside the recipe markdown follow the six-slot structure (What · Why · How to read · What it represents · Where it comes from · Membership function preview)
- If you're unsure about cluster assignment for a non-obvious NbS (especially something with the word "water" — water harvesting is NOT in wetlands cluster), ask before deciding.
