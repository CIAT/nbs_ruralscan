# Agroforestry — NbS Recipe (skeleton)

*Skeleton · v0 · May 2026. Phase 3 pilot NbS.*

> **Companion documents:**
> - Methodological framework: [`../framework.md`](../framework.md)
> - Canonical recipe pattern: [`water_harvesting.md`](./water_harvesting.md)
> - Schema rows: `schema/recipes/agroforestry/` *(to be populated)*
> - Source schema xlsx: `2_Technical_&_Data/Claude Outputs/RuralNbS_Agroforestry_Tables_T0-T7.xlsx`

> **Status: skeleton.** Section structure inherited from the water-harvesting recipe. Substantive content to be authored by Benson + Namita, reviewed by MFL team (Sarah / Chris / Evert / Hannes — agroforestry domain).

---

## 1. Context and Scope

**Subpractice typology → suitability families is now drafted for sign-off:
[`../families/agroforestry.md`](../families/agroforestry.md)** (F1 planted silvoarable · F2 regeneration-based ·
F3 silvopastoral · F4 linear/boundary · F5 shaded perennial-crop; homegardens parked as `qualitative_only`,
riparian buffers split to their own NbS). T4 is keyed to `suitability_family_id` per that scheme. Author the
narrative scope here against the agreed families once MFL has signed off.

*TODO* — write the NbS definition and scope narrative, drawing the subpractice list from the family scheme above
rather than re-listing it. The grouping principle (group by *dominant limiting factor*, not visual structure) is
why, e.g., planted parkland (F1) and retained/FMNR parkland (F2) are separate families despite looking identical.

### 1.1 Position within the generic methodological framework

Agroforestry inherits the generic 11-phase framework. Customises Phases 2 (input data inventory), 3 (suitability logic), 4 (standardisation), 6 (climate risk profiling), 7 (weighting), 8 (MCDA integration).

## 2. Recommended Input Variables for Suitability Analysis

*TODO* — author the master variable table. Anticipated themes:

### 2.1 Variable categories

- **Topographic** — slope, elevation, aspect
- **Climatic** — annual rainfall, rainfall variability, PET, aridity, temperature, heat stress
- **Soil** — depth, pH, organic carbon, texture, fertility class
- **LULC / vegetation** — current land cover, existing tree cover, NDVI, recent forest change
- **Socio-economic & infrastructure** — distance to road, population, market access, electrification, farm size proxy
- **Hazard** — drought (SPEI), flood hazard, fire risk

### 2.2 Master variable table

*TODO* — fill table with the same columns as water_harvesting.md §2.2:

| Input variable | Definition / purpose | Relevance to agroforestry | Expected influence | Recommended normalisation | Suggested dataset |
|---|---|---|---|---|---|
| Slope | … | … | … | … | … |
| Annual rainfall | … | … | … | … | … |
| *(continue for all variables)* | | | | | |

## 3. Variable Descriptions and Rationale

*TODO* — six subsections, one per theme (matches WH recipe structure).

## 4. Potential Data Sources and Spatial Data Types

*TODO* — dataset table (Table 2 equivalent). Per variable: recommended dataset · native resolution · data type · GEE asset ID or source · hosting status (`native_gee` / `community_gee` / `requires_upload`).

## 5. Normalisation Using Fuzzy Membership Functions

*Inherited from framework.* Variables use the five fuzzy functions defined in `../framework.md` and demonstrated in `water_harvesting.md §5`. Per-variable parameterisation goes in T4.relationship_params in the schema.

### 5.1 Recommended membership functions

*TODO* — list each variable and which function applies. Cite slope ranges, rainfall optima, etc.

### 5.2 Practice-specific normalisation guidance

*TODO* — note where parameters differ by subpractice (e.g. shade-trees vs. parkland have different slope optima).

## 6. Weighting Approaches for the MCDA

*Inherited from framework.* AHP starting weights → CRITIC + Entropy objective optimisation → α-reconciled final weights. See `../framework.md` and `water_harvesting.md §6` for the engine.

### 6.1 Step 1 — Expert-based starting weights (AHP)

*TODO* — define top-level criteria for agroforestry. Candidate criteria: (a) tree-growth feasibility, (b) climate suitability, (c) demand and accessibility, (d) climate risk.

### 6.2 Step 2 — Objective weighting

Use the framework's CRITIC + Entropy methods. Run order, α default, sensitivity range per framework.

### 6.3 Step 3 — Weight reconciliation

Default α = 0.4 (60% objective, 40% expert). Sensitivity tested across α ∈ {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}.

## 7. Suitability Analysis Considerations, Assumptions and Constraints

*TODO* — author. Anticipated content:

### 7.1 Aggregation rule

Weighted Linear Combination (WLC) inherited from framework.

### 7.2 Subpractice-specific suitability surfaces

Multiple surfaces — one per subpractice family (perennial tree-crop · parkland · alley cropping · boundary planting). Composite via max-across-subpractice.

### 7.3 Structural exclusion masks

Recommended exclusions: water bodies, built-up areas, strictly-protected areas (WDPA I–IV), dense closed-canopy forest, glaciers, slopes > 35° (subpractice-specific), soil depth < 25 cm.

### 7.4 Climate risk integration

Per framework. Drought hazard included as positive criterion (high drought → high need). Flood hazard above 50-yr return period: constraint mask for low-lying subpractice variants. Cyclones: structural vulnerability per T3.

### 7.5 Key assumptions

*TODO*

### 7.6 Constraints and limitations

*TODO*

## 8. Indicative Workflow Summary

*TODO* — phase-by-phase workflow table inheriting the WH recipe's structure.

---

## Authoring checklist (before status changes from skeleton → draft)

- [ ] Section 1 (Context and Scope) authored with subpractice typology
- [ ] Master variable table (§2.2) populated
- [ ] Variable Descriptions (§3) — six subsections
- [ ] Data Sources table (§4) — including hosting status per dataset
- [ ] Fuzzy parameter assignments (§5)
- [ ] AHP criteria hierarchy (§6.1)
- [ ] Exclusion masks (§7.3)
- [ ] Climate risk integration (§7.4) — Mode A and B handling
- [ ] Assumptions + constraints (§7.5, §7.6)
- [ ] Workflow summary table (§8)
- [ ] MFL reviewer signed off (agroforestry domain — Evert / Hannes typically)
- [ ] PR raised; structural checklist passed

---

## Version history

- **v0** (May 2026) — skeleton created with the section structure of `water_harvesting.md`. Content authoring in flight (Benson + Namita, with MFL review).
