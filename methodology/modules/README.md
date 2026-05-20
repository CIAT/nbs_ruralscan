# Module spec sheets

One spec sheet per analytical module (M0–M6). Each spec is the I/O contract for that module — what it consumes, what it produces, in what format, and how it connects to the rest of the pipeline.

Spec sheets are NbS-agnostic. They describe the framework module; per-NbS specifics live in the recipe (`../recipes/<nbs_id>.md`) and the schema (`../../schema/recipes/<nbs_id>/`).

## Index

| ID | Module | File | Owner(s) | Status |
|---|---|---|---|---|
| M0 | Setup & Scope | `M0_setup.md` *(TBD)* | Pete | planned |
| **M1** | **Suitability → Opportunity Space** | [`M1_suitability.md`](./M1_suitability.md) | Benson + Namita | **draft (v0.1)** |
| M2 | Rural Climate Risk | `M2_climate_risk.md` *(TBD)* | Brayden | planned |
| M3 | Opportunity Space Characterisation | `M3_characterisation.md` *(TBD)* | Namita + Benson | planned |
| M4 | TTL Hotspots (MCDA) | `M4_hotspots.md` *(TBD)* | Benson | planned |
| M5 | NbS Scorecard & Response | `M5_scorecard.md` *(TBD)* | Namita | planned |
| M6 | Implementation Hand-off | `M6_handoff.md` *(TBD)* | MFL team + Pete + Namita | planned |

## Authoring a module spec

1. Open an issue using the **Module Spec** template (`.github/ISSUE_TEMPLATE/module-spec.md`).
2. Inherit the section structure of `M1_suitability.md`.
3. Each sub-step has its own I/O — input format, what it computes, output format.
4. Reference schema tables (T0–T7) explicitly — what columns are consumed and produced.
5. Get Pete + one team member to review.
6. PR using the PR template.

## Why spec sheets matter

Module specs are the contracts between team members. Benson reads M1 to know what data products to produce. Namita reads M3 to know what variable cards to populate. Brayden reads M2 to know what climate risk output the rest of the pipeline expects. Without the contract, work duplicates or falls through.

The pipeline implementation in `../pipeline/` should be readable as a one-to-one mapping from these spec sheets.
