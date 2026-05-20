# Stocktake findings

The full Stocktake Review (April 2026) is the canonical literature synthesis behind the methodology. Lives on OneDrive — not duplicated here.

**Canonical source:** `D591_Rural-Scan_NBS/4_Outputs_&_Reporting/4_Reporting/Stocktake Review/Stocktake Review_with revisions.docx`

## What's in the stocktake (summary)

- Systematic review of NbS spatial prioritisation literature (~220 studies).
- Per-NbS pattern analysis: which variables are commonly used, which methods, at what resolution, with what assumptions.
- Method typology: rule-based GIS · MCDA · fuzzy logic · process-based modelling · ML approaches · spatial optimisation.
- Scalability assessment (quality × generalisability matrix).
- Recommendations feeding directly into the framework — the AHP + CRITIC + Entropy hybrid weighting, the five fuzzy functions, the six-theme variable structure all come from synthesis here.

## Quick references for recipe authors

When authoring a new recipe (`methodology/recipes/<nbs_id>.md`), the stocktake provides:

- A starting variable list (per NbS, with counts of how many studies use each)
- Typical thresholds and response functions from the literature
- Data source recommendations
- Common limitations and caveats

Citing back to the stocktake in a recipe is encouraged.

## Files in this folder (TBD)

As the project progresses, we may pull per-NbS distilled stocktake findings into this folder as small markdown files (`<nbs_id>.md`), so they sit alongside the recipe that uses them. Not done yet; reach out if you'd like to start that pattern.
