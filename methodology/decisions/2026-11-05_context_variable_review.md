# Context-specific review of variables and distributions

**Status:** Proposed workflow for methodological development; not yet a ratified analytical rule.  
**Raised by:** Pete Steward, 5 November 2026, during the Stage 03 / C.5 wireframe review.

## Proposal

Before interpreting opportunity-space summaries or proceeding to hotspot prioritisation, review the variables and their distributions for the chosen context. Classification defaults provide a starting point for review, not an automatic conclusion about local conditions.

## Suggested workflow

1. Establish the context: area of interest, practice, selected opportunity-space extent and climate period.
2. Review each variable's relevance and meaning in that context, including its dataset, units, coverage and spatial resolution. Check whether higher values mean better or worse conditions, or higher or lower livelihood risk.
3. Inspect the spatial pattern and distribution within the opportunity space, alongside an appropriate wider reference. Identify missing data, limited variation, outliers and concentrations that affect interpretation.
4. Review the classification method, class count and cut points against that distribution and the variable's meaning. Distinguish relative quantile classes from evidence-backed substantive thresholds; do not interpret a relative “high” class as an absolute risk threshold.
5. Inspect maps and summaries together. Select the classes of interest and compare table and plot views; state the denominator (area or people), reference extent and classes actually included for each variable.
6. Record the context, data sources, direction, classification settings and rationale before carrying the reviewed variables forward into prioritisation. Retain defaults and subsequent changes for reproducibility.

## Development considerations

- Sections 3.2 and 3.3 with the C.5 panel illustrate this review loop. People/land condition labels and livelihood-risk labels should match each variable's meaning and direction.
- Baseline/future comparisons should retain common cut points and explicit spatial and population denominators so changes remain interpretable. The current demonstrator fixes cut points from the baseline opportunity extent.
- Livelihood hazard-exposure screening remains distinct from risk to the investment. Classification does not by itself estimate loss probability or establish feasibility.
- Review of distributions informs interpretation; it does not silently change evidence-backed suitability rules, MCDA weights or scientific schema. Any analytical changes need their own recorded rationale and established schema workflow.

Related specifications: [M3 characterisation](../modules/M3_characterisation.md), [M2 climate risk](../modules/M2_climate_risk.md), [T5 opportunity-space variables](../opportunity_space_T5.md). Prototype discussion: [wireframe feedback log](../../docs/redesign/FEEDBACK_LOG.md).
