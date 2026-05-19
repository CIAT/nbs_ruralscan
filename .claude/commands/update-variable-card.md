---
description: Update or author a Variable Card for a specific NbS recipe
---

You are updating a Variable Card in the Rural NbS Scan project.

The user will give you a variable name and an NbS ID. If either is missing, ask.

Steps:

1. **Locate** the recipe at `methodology/recipes/<nbs_id>.md` and the schema CSV at `schema/recipes/<nbs_id>/T4_suitability_variables.csv`. If either is missing, suggest running `/new-recipe <nbs_id>` first.

2. **Find or create** the variable row. If the variable already exists in T4, update it; otherwise add a new row.

3. **Populate / update the six Variable Card slots**, asking the user concisely for any missing piece:
   - **What it is** — one-sentence plain-language definition
   - **Why it's included** — NbS-specific rationale (1-3 sentences)
   - **How to read it** — interpretation: what high/low values mean for suitability, with ranges
   - **What it represents (cluster)** — default representative status; correlated variables it stands for (leave correlation values blank until an AOI run produces them)
   - **Where it comes from** — dataset name, source, hosting status (`native_gee` / `community_gee` / `requires_upload`), GEE asset ID if applicable, native resolution
   - **Membership function preview** — function type and parameters

4. **Update the recipe markdown** with the populated card content. Use the same formatting as the slope card in `docs/wireframe.html` (you can read it for the visual reference).

5. **Run a quick consistency check**:
   - Is the variable's theme correct (topographic / climatic / soil / LULC / socio-econ / hazard)?
   - Does the hosting status reflect reality? If not native GEE, has an upload path been considered?
   - Does the membership function shape match the rationale (e.g. a steep-slope variable should not have an increasing-sigmoid)?

6. **Confirm to the user** what was updated, and remind them that:
   - References should be cited
   - PR should use the PR template; the structural checklist should be re-ticked
   - If this is a new cluster representative, related variables need to be updated to point to it

Structural rules:
- Six slots are mandatory; no slot can be omitted
- Don't hardcode dataset URLs — they go in the T1 Data Registry
- Mark hosting status explicitly; "fitness for purpose precedes platform" — don't substitute a worse dataset just to keep it GEE-native
