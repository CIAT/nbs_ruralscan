---
name: Pilot Task
about: Apply the methodology to a specific country / NbS combination (Phase 3 deliverable)
title: "[Pilot] <NbS> in <country>"
labels: ["pilot", "phase-3"]
assignees: []
---

## Pilot scope

- **NbS:** <!-- e.g. agroforestry -->
- **Country:** <!-- e.g. Sierra Leone -->
- **Sub-national focus:** <!-- e.g. all districts, or Bo + Kenema -->
- **AOI rationale:** <!-- e.g. FSRP target landscapes -->

## Use case context

- **Linked WB project:** <!-- e.g. Sierra Leone FSRP -->
- **WB contact:** <!-- e.g. @dakhmetova -->
- **Why this pilot:** <!-- 2-3 sentences -->

## Deliverables

- [ ] Reproducible Colab notebook in `pipeline/notebooks/<nbs>_<country>.ipynb`
- [ ] Outputs in `pipeline/outputs/<pilot_id>/` (maps, summary tables, opportunity fingerprint, scorecard)
- [ ] One-page pilot summary in this issue
- [ ] Demo-ready wireframe view (if time allows)

## Data readiness check (before running)

- [ ] All recipe variables have a GEE catalog or community GEE source — or
- [ ] Any user-supplied datasets identified and lined up
- [ ] Country-specific datasets reviewed (national land cover, finer DEM if available)
- [ ] AOI vector available

## Run checklist

- [ ] Recipe loaded from schema
- [ ] Pipeline runs end-to-end without manual intervention
- [ ] Outputs reviewed for plausibility (sanity check by domain expert)
- [ ] Resolution audit table generated
- [ ] Future scenario run (SSP2-4.5 mid-century at minimum)

## Validation

- [ ] Sanity-check map against known regional knowledge
- [ ] WB feedback gathered (if available within timeline)
- [ ] Edge cases / data issues documented

## Definition of done

- [ ] Notebook reproducible from clean environment
- [ ] Outputs interpretable without verbal explanation
- [ ] Summary presented to team
- [ ] PR merged
