# Agroforestry T4 v0.1.2

Adds observed group and variable inclusion estimates to the [single rule table](index.html). Analytical rules, weights and system assignments remain unchanged.

- **Group inclusion:** unique papers using any member variable / contributing model-paper cohort.
- **Variable inclusion:** unique papers using that variable / the same cohort.
- **Variable within group:** unique papers using that variable / papers using any member of its group; included in the downloadable CSV.

Displayed estimates cover general-practice models across agroforestry systems. The cohort contains papers with at least one active, explicitly verified structural model input. Reviewed estimates require human-reviewed numerator records and use reviewed model papers as denominator. Including-pending estimates use all active verified model-use records. Approval of another variable never approves this variable. DOI aliases and repeated records count once; group members do not inflate group counts.

[inclusion_estimates.csv](inclusion_estimates.csv) lists exact numerator/denominator paper keys, supporting evidence IDs, review lanes, scope/system breakdowns and within-group estimates. Source completeness is not established: missing records are not proof of non-use. Percentages describe observed inventory coverage, not systematic-review prevalence, independent-study agreement, effectiveness, or runtime weights. Reused models are not asserted independent. No system transfer is implied.

Current general-practice cohort: eight reporting papers. Reviewed terrain inclusion is 6/8 (75%); climate and soil each 5/8 (62.5%). Slope is 6/8 (75%); soil pH 3/8 (37.5%). These are record-level review counts, not new approval of later metadata edits.

Prior versions remain preserved. [Handoff limits and rebuild instructions](../README.md) still apply.
