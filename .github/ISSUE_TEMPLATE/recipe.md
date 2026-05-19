---
name: NbS Recipe
about: Author or update a per-NbS recipe (variables, response functions, weights, datasets)
title: "[Recipe] <NbS name>"
labels: ["recipe", "methodology"]
assignees: []
---

## NbS

**Name:** <!-- e.g. Agroforestry -->
**ID (snake_case):** <!-- e.g. agroforestry -->
**Cluster:** <!-- tree_based · soil_water · wetland · pastoral · landscape_scale -->
**Subpractice variants (if any):** <!-- e.g. perennial tree-crop, parkland, alley cropping, boundary planting -->

## Lead author & reviewer

- **Lead author:** <!-- @namita -->
- **MFL reviewer:** <!-- @sarah · @chris · @evert · @hannes — pick by domain -->
- **Target completion:**

## Source material

- [ ] Stocktake findings reviewed (`reference/stocktake_findings.md`)
- [ ] Water-harvesting recipe consulted as template (`methodology/recipes/water_harvesting.md`)
- [ ] Relevant literature listed below:

<!-- bullet list of key references -->

## Master variable table

Use the six-theme structure. Fill each variable's row with:

- Definition / purpose
- Relevance to this NbS
- Expected influence on suitability (positive / negative / non-monotonic)
- Recommended normalisation (fuzzy membership)
- Suggested spatial dataset + hosting status

Themes:

- [ ] Topographic and morphometric
- [ ] Hydrological (if relevant)
- [ ] Soil and lithology
- [ ] Climatic
- [ ] Land cover and ecological
- [ ] Socio-economic, infrastructure, risk

## Variable Cards

For each variable, fill all six slots:

- [ ] What it is
- [ ] Why included (NbS-specific rationale)
- [ ] How to read it (interpretation: what high/low means)
- [ ] What it represents (correlation cluster — populated after first AOI run)
- [ ] Where it comes from (dataset + hosting status)
- [ ] Membership function preview

## NbS scorecard (T6)

Fill the Likert effect matrix across outcomes:

- [ ] Erosion mitigation
- [ ] Drought resilience
- [ ] Biodiversity
- [ ] Carbon mitigation
- [ ] Rural income
- [ ] Gender equity
- [ ] Food security
- [ ] Fire risk
- [ ] (Add others relevant to this NbS)

## Economic profile

- [ ] Establishment cost range ($/ha)
- [ ] Recurring cost level (very_low → very_high)
- [ ] Time-to-benefit (years)
- [ ] CrossBoundary economic archetype (high_capital · long_horizon · fragile_gains · quick_returns)

## Definition of done

- [ ] All variables in master table have hosting status (`native_gee` · `community_gee` · `requires_upload`)
- [ ] All Variable Cards have six slots populated
- [ ] Scorecard rows filled with effect direction + confidence + mechanism
- [ ] References cited
- [ ] MFL reviewer signed off
- [ ] PR raised using PR template
