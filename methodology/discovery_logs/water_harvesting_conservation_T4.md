# Discovery log — Water Harvesting and Conservation × T4 (suitability)

**Date(s):** June 2026
**Author(s):** Pete Steward · Claude Code (operator)
**Seed-set rule:** T4 method §3 Bounded, authority-weighted seed-set (v0.2.6 / v0.2.7 SOP).

## Sources & databases queried

- **WOCAT SLM Database (Mekdaschi Studer & Liniger, 2013)** — targeted search for "Water Harvesting: Guidelines to Good Practice" to extract biophysical thresholds (slope, rainfall) and baseline establishment costs for the `water_harvesting__runoff_catchment` family.
- **CGIAR (Simelton et al., 2021)** — agricultural NBS functions mapping to priority themes.
- **WRI (Collins et al., 2025)** — Sub-Saharan Africa climate-resilience cost-effectiveness.

## PRISMA-lite counts

| Stage | Count | Notes |
|---|---:|---|
| Query targeting synthesis sources | 3 | Focused search for WOCAT water harvesting guidelines and institutional synthesis papers |
| Retained for metadata register extraction | **3** | All 3 documents evaluated for biophysical, cost-effectiveness, or priority enablers |
| Added to SRC Register | **3** | Registered as High-tier synthesis sources (`wocat_studer_2013`, `simelton_2021`, `wri_2025`) |
| Added to EV Register (Water Harvesting) | **3** | `ev_slope_wocat_studer13`, `ev_precip_wocat_studer13`, `ev_estcost_wocat_studer13` |

## Inclusions

The following sources were registered in `schema/registers/SRC_source_register.json` (`nbs_ids` contains `water_harvesting_conservation`):

| `source_id` | tier | first author / year | aez · country | variables extracted |
|---|---|---|---|---|
| `wocat_studer_2013` | High | Mekdaschi Studer 2013 | global · Global | slope, annual_precipitation, establishment_cost |
| `simelton_2021` | High | Simelton 2021 | global · Global | biodiversity_conservation_priority |
| `wri_2025` | High | Collins 2025 | continental · SSA | establishment_cost (shared with agroforestry) |

## Exclusions

- **wocat_liniger_2011** — Sustainable Land Management in Practice. Excluded from water harvesting suitability mapping because its biophysical guidelines are heavily tailored toward agricultural soil-and-water conservation rather than the runoff-catchment structure thresholds defined under Mekdaschi Studer & Liniger (2013).
- **gca_2022** — GCA State and Trends in Adaptation 2022. Excluded because its NbS chapter focuses entirely on agroforestry, without explicit quantitative parameters or enabler analyses for structural water harvesting.

## Notes

- Siting thresholds for slope (optimal 0–3°, absolute maximum 31° / 60%) and precipitation (optimal 200–750 mm) are derived directly from the Mekdaschi Studer & Liniger (2013) global guidelines.
- The cost estimates (150–300 USD/ha) serve as the baseline for `establishment_cost` in the `T6_nbs_scorecard.json` for Water Harvesting.

---

## Sign-off

| Step | Sign-off |
|---|---|
| Phase 2 Ingestion (Issue #24) | Pete Steward (2026-06-09) — database-first sweep |
| QA / dataset-fitness review | **Benson Kenduiywo (pending)** |
