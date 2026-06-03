# Rural NbS Scan — Cross-cutting Methodological Framework

*Living document · v0.1 draft · May 2026*

The framework defines the cross-cutting analytical strategy used across every Nature-based Solution in the Rural NbS Scan. It is **NbS-agnostic**. Per-NbS specifics (variables, thresholds, weights, datasets) live in the recipes (`methodology/recipes/`) and the schema (`schema/`).

## Architectural layering

The methodology is implemented in three explicit layers — kept separate so each can evolve independently:

| Layer | Role | Files |
|---|---|---|
| **Framework** | Cross-cutting methodology · MCDA engine · standardisation library · schema. NbS-agnostic. | `methodology/framework.md` · `schema/` |
| **Recipe** | Per-NbS configuration. Variables, response functions, weights, subpractice families. | `methodology/recipes/<nbs_id>.md` |
| **Runtime** | GEE Python pipeline · Colab pilot notebooks · GEE App. | `pipeline/` |

## Seven analytical modules (+ M2b project-risk addendum)

| ID | Module | Question answered | Schema tables |
|---|---|---|---|
| **M0** | Setup & Scope | AOI · NbS · resolution · scenario · ingestion check | T0, T1, T7 |
| **M1** | Suitability → Opportunity Space | Where could this NbS biophysically work? | T1, T4, T7 |
| **M2** | Rural Climate Risk | Where are rural **livelihoods** exposed to climate hazards (baseline + future)? | T1, T2 |
| **M2b** | Project Disaster Risk Screen *(addendum)* | Where could disasters damage/destroy the **investment**? (WB disaster-screening lens) | T2, T3 |
| **M3** | Opp Space Characterisation | What's in the opportunity space (poverty, biodiversity, GESI, production, pop)? | T1, T5 |
| **M4** | Priority Hotspots (MCDA) | Where within the opp space do TTL priorities concentrate? | T5 |
| **M5** | NbS Scorecard & Response | What can this NbS plausibly address (Likert) + economic profile? | T3, T6 |
| **M6** | Implementation Hand-off | What comes next after scoping (feasibility tools, contextualisation)? | T0, T6 |

See the architecture diagram: [`docs/pipeline.html`](../docs/pipeline.html).

## Inherited framework primitives

The components below originated in Benson's water-harvesting recipe and v2 methodology plan. They are treated as canonical framework components used across all recipes.

| Primitive | Origin | Used by |
|---|---|---|
| 5 fuzzy membership functions (sigmoid, linear, Gaussian, bell, inverted sigmoid) | v2 plan §4 / `recipes/water_harvesting.md` §5 | M1, M3, M4 |
| Hybrid AHP + CRITIC + Entropy weighting (α-reconciled) | v2 plan §7 / `recipes/water_harvesting.md` §6 | M1, M3, M4 |
| Reference MCDA implementation | `reference/R/spatMCDA.R` | M1, M3, M4 |
| Recipe template column structure | `recipes/water_harvesting.md` §2.2 | All recipes |
| Subpractice family pattern | `recipes/water_harvesting.md` §1 | All recipes with within-NbS variation |
| Sensitivity perturbation (±10% weight shuffle) | spatMCDA.R / WH recipe §9 | M1, M3, M4 |

## Climate risk formulation

The framework follows the IPCC AR6 risk decomposition: **Risk = Hazard × Exposure × Vulnerability**, where **Vulnerability = f(Sensitivity, Adaptive Capacity)**.

Two operational modes, selectable by the user (Schema T2 flag `use_in_simplified_mode` vs `use_in_advanced_mode`):

- **Mode A — Hazard × Exposure** (pilot default). Simpler, fewer assumptions; avoids double-counting vulnerability variables that also appear in M3/M4 TTL priorities.
- **Mode B — Full IPCC AR6** with vulnerability composite. Use when context warrants it.

The mode toggle is user-facing. Outputs metadata records the mode used so runs are not inadvertently compared across modes.

## Variable selection (two stages)

Every recipe applies variable reduction before variables enter the MCDA. Two stages:

1. **Thematic grouping** — expert, per-NbS, done once when the recipe is built. Six standard themes: topographic · hydrological · soil · climatic · LULC · socio-econ + hazard.
2. **Correlation-based reduction** — empirical, per study area. After fuzzy standardisation, compute pairwise correlation; cluster variables with |r| > 0.7; pick one representative per cluster (highest variance or expert-flagged primary).

The cluster membership is preserved and surfaced in the UI (Variable Config tab in the wireframe). One representative per cluster enters the MCDA — but users can promote any clustered variable to a primary in technical mode.

## Dataset sourcing (three-tier preference)

For each variable, the recipe's `T1` Data Registry entry uses the first option that satisfies fitness-for-purpose:

1. **Native GEE asset** if a credible one exists
2. **Community-hosted GEE asset** (e.g. `projects/sat-io/open-datasets/`)
3. **Upload to GEE** if the best-fit dataset isn't already hosted

Fitness for purpose precedes platform. We do not substitute the best dataset for an inferior one just because the better one isn't already in GEE.

## Spatial standardisation

All datasets resampled to a standard global coordinate reference frame and pre-processed at multiple tiers (10km · 5km · 1km · 500m · 100m) so analytical resolution is a configurable parameter. The pipeline generates a **resolution audit table** showing which datasets are at native resolution vs upsampled / downsampled. Upsampling beyond one tier triggers a visible warning — synthetic fine-scale variability is misleading.

## Uncertainty & sensitivity

Run the analysis with perturbed weights (±10% by default) and produce sensitivity maps. Where feasible, parameter ranges in the recipe (`uncertainty_pct` field in T4) propagate to confidence bands on the final surface.

## What this framework does not do

- Not ecosystem service modelling (no InVEST, ARIES, or similar)
- Not site-level feasibility design
- Not full cost-benefit analysis (only indicative economic archetypes via T6)
- Not optimisation
- Not detailed climate impact modelling beyond hazard exposure

These belong downstream of scoping — pointed to in M6 Implementation Hand-off.

## Authoring conventions

- The pipeline reads analytical rules from the schema. **Never hardcode rules in code.**
- Each new NbS is added by writing a new recipe (`methodology/recipes/<nbs_id>.md`) + schema rows in `schema/recipes/<nbs_id>/`. No code changes required.
- New analytical methods (beyond the inherited primitives above) require a methodology RFC issue and team sign-off.

## References

See `reference/` for the source R prototype (`spatMCDA.R`), the stocktake review, and supporting literature notes.

## Version history

- **v0.1** (May 2026) — initial draft, lifts the structural decisions from the inception report, stocktake, and v2 methodology plan into the repo. Sections to be deepened as Sessions B–E in the team series produce more detail.
