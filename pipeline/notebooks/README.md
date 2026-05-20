# Pilot notebooks

One Colab notebook per pilot. Each notebook is end-to-end: authenticate GEE, load recipe, run pipeline, write outputs, render maps and tables inline.

## Naming convention

`<nbs_id>_<iso3_country>.ipynb`

Examples:

- `agroforestry_sle.ipynb` — agroforestry in Sierra Leone (FSRP pilot candidate)
- `water_harvesting_ken.ipynb` — water harvesting in Kenya
- `forest_restoration_idn.ipynb` — forest restoration in Indonesia

If sub-national: `<nbs_id>_<iso3_country>_<region>.ipynb` (e.g. `agroforestry_sle_kenema.ipynb`).

## Notebook structure (recommended)

1. **Header** — title, pilot ID, authors, date, recipe version, schema version.
2. **Setup** — install dependencies (Earth Engine, geemap, pandas, etc.); authenticate GEE.
3. **Configuration** — define AOI, NbS, resolution, climate scenario. Load recipe from `../schema/recipes/<nbs_id>/`.
4. **Data ingestion** — call `data_loaders` for each variable; show the resolution audit table.
5. **Variable reduction** — thematic grouping (from recipe) + correlation clustering (per AOI); show cluster membership.
6. **M1 Suitability** — fuzzy standardisation, weighting (CRITIC + Entropy + AHP), weighted overlay; classify into 4 classes; sensitivity perturbation.
7. **M2 Climate Risk** — hazard × exposure (Mode A) baseline + future scenario.
8. **M3 Characterisation** — extract priority variables within the opportunity space.
9. **M4 Hotspots** — TTL-weighted MCDA on M3 variables; show top-5 list.
10. **M5 Scorecard** — render the NbS Likert effects + economic archetype from T6.
11. **Outputs** — export GeoTIFFs and CSVs to `pipeline/outputs/<pilot_id>/`; render PNG maps for documentation.
12. **Summary** — one paragraph plain-language summary; written for a WB analyst to read first.

## Don't

- Don't hardcode AOI extents or variable lists in the notebook — read from schema + a small config cell.
- Don't commit `outputs/` rasters unless they're small (< 10 MB total per pilot). Use the `outputs/<pilot_id>/README.md` summary instead.
- Don't skip the resolution audit. It catches misleading high-resolution outputs derived from coarse inputs.

## Where to get the first pilot started

The first agroforestry pilot in Sierra Leone is the active Phase 3 priority. Use `/new-recipe agroforestry` first if the recipe isn't fully populated, then ask Claude Code to scaffold the notebook (prompt #2 in the Claude Code uplift note).
