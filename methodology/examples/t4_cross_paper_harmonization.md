# T4 cross-paper harmonization: worked proposal

Approved conventions • 20 October 2026. All papers, values and weights below are hypothetical. Conventions are implemented for step profiles in recipe/harmonization.py. See docs/review/t4-harmonization-results.html for regenerated live T4 effects. Agroforestry is the NbS type; comparisons must refer to the same agroforestry system and compatible context.

## Proposed sequence

### Preserve the source

Keep evidence ID, source and independent origin, original class labels/scores, bounds and inclusivity, units, score meaning, method and applicability.

### Establish a compatible pool

Same variable definition, agroforestry system and relevant context. Species/crop scope policies still apply. Unknown applicability is a review state, not universal applicability.

### Apply a versioned score crosswalk

Distinguish comparable cardinal scores from ordinal labels. Default anchors below are provisional conventions; missing definitions cannot be repaired by normalization.

### Evaluate functions without inventing values

For step functions use the union of breakpoints and exact boundary checks, not a coarse sampling grid. Continuous functions require an explicit evaluation tolerance and support domain.

### Combine independent contributions

One contribution per independent origin at each value. Reuse verified source-quality weighting only after applicability checks. Do not substitute study variable-importance weights.

### Publish the summary and its limits

At each interval retain median lower/upper bounds, source minimum/maximum, contributing origins, eligible pool size, weight coverage and flags. Source range is disagreement, not a confidence interval.

## Provisional common class anchors

These are explicit design choices, not values extracted from papers. Class definitions take precedence over literal labels.

| Meaning | Score |

|---|---:|

| Explicitly unsuitable | 0 |

| Very low | 0.10 |

| Low | 0.25 |

| Moderate | 0.50 |

| High | 0.75 |

| Very high | 0.90 |

| Explicit optimum / fully suitable | 1 |

## Worked scenarios

### 01. Different scores for the same classes

**Input:** A assigns low=0.2, moderate=0.6, high=0.9. B assigns low=0.3, moderate=0.5, high=1. Both describe arbitrary ordinal class scores, with matching class definitions.

**Expected output:** Map both to low=0.25, moderate=0.50, high=0.75. Keep every original score. A numeric 1 assigned to “high” does not establish a measured optimum.

**Use / review:** Common scores can be compared after the definitions are checked. Flag convention-based scoring; original scores remain available for sensitivity analysis.

### 02. Three classes versus five

**Input:** A: low / moderate / high. B: very low / low / moderate / high / very high. Both use those meanings, rather than merely numbered ranks.

**Expected output:** A maps to 0.25 / 0.50 / 0.75. B maps to 0.10 / 0.25 / 0.50 / 0.75 / 0.90. Neither scale is stretched to 0–1.

**Use / review:** Combine at common slope values, not by matching “class 1” or dividing rank by class count. If A’s “high” includes B’s high and very high classes, preserve that broader meaning as crosswalk uncertainty; do not claim exact semantic equivalence.

### 03. Named classes with no scores

**Input:** A reports low, moderate and high slope-suitability bands but supplies no numerical scores.

**Expected output:** Use the proposed common anchors only after verifying class definitions. Mark each numerical score as a design convention, with its policy version.

**Use / review:** Eligible for harmonization with convention-based-score flag. Do not claim the paper reported 0.25, 0.50 or 0.75.

### 04. Numbered ranks without definitions

**Input:** A reports classes 1–3; B reports classes 1–5. Direction or endpoint meanings are absent.

**Expected output:** Retain ranks and source text. Do not infer that 1 means unsuitable or 5 means optimal.

**Use / review:** Hold score crosswalk. Known order alone supports ordinal comparison, not an exact common cardinal scale.

### 05. Different numerical scales, equivalent meaning

**Input:** A reports 0–100 with 0=unsuitable and 100=fully suitable. B reports the same construct and endpoints on 0–1.

**Expected output:** Divide A by 100: 20 becomes 0.20; 75 becomes 0.75. Do not use observed minimum and maximum to rescale a partial table.

**Use / review:** Combine only if score definitions and construction are comparable. Equivalent endpoints alone do not prove equivalent intermediate values.

### 06. Probability or yield versus ordinal suitability

**Input:** A gives establishment probability 0.8. B gives relative yield 80%. C assigns “high suitability” 0.8.

**Expected output:** Keep three separate response meanings. Probability, relative yield and an ordinal utility are not interchangeable because all can be written on 0–1.

**Use / review:** Hold cross-meaning aggregation unless an explicit, justified conversion model exists. Preserve useful source-specific functions.

### 07. Different slope cutoffs

**Input:** A: high below 5°, moderate from 5° to below 15°, low from 15° upward. B: high below 8°, moderate from 8° to 20°, unsuitable above 20°. These hypothetical endpoints are explicitly defined.

**Expected output:** Compare at the union of breakpoints (5°, 8°, 15°, 20°), on intervals between them, and at each boundary separately. Example interior points are shown below.

**Use / review:** Return weighted median bounds, source range, coverage and conflict flags. Do not smooth away abrupt class changes or conceal an exclusion conflict.

### 08. One paper says unsuitable, another says low

**Input:** At 25°, A assigns low=0.25; B explicitly assigns unsuitable=0. Both have weight 1.

**Expected output:** Median set is [0, 0.25]; source range is [0, 0.25]. Set exclusion_conflict. No single consensus score is selected in this proposal.

**Use / review:** Retain both profiles. Do not create a hard mask from a zero median, majority vote or low suitability. Resolving a hard exclusion requires an explicit evidence/context decision.

### 09. Low is the lowest class reported

**Input:** A explicitly defines all slopes above 15° as low. It has no unsuitable class.

**Expected output:** Keep score 0.25 across that declared domain. No invented zero at 20°, 30° or any other slope.

**Use / review:** A contributes positive, limited suitability. A finite observed study range, however, is not evidence for an unbounded class.

### 10. Only a favourable range is reported

**Input:** A reports “high suitability below 10°” and gives no classification elsewhere. B reports low suitability at 15°.

**Expected output:** At 15°: A=unknown, B=0.25. Combined candidate=0.25, supported by one of two eligible independent sources; equal-weight coverage=50%.

**Use / review:** Flag single-source support and partial coverage. Never turn A’s missing value into 0, or count it as agreement. If both are unknown, output unknown.

### 11. Slope percent versus degrees

**Input:** A gives a cutoff of 10% slope. B gives a cutoff of 10°.

**Expected output:** Convert with degrees=atan(percent/100): 10%=5.7106°. Conversely, 10°=17.6327%. Convert every boundary before pooling.

**Use / review:** These cutoffs disagree; they are not the same number in different notation. Retain original units and unrounded converted values for computation.

### 12. Ambiguous boundaries or overlapping bins

**Input:** A prints high=0–5° and moderate=5–15°, without specifying which includes 5°. Another table prints high=0–10° and low=8–20°.

**Expected output:** In the first case, 5° remains unknown for A; interiors remain usable. In the second, 8–10° is internally contradictory and remains unresolved.

**Use / review:** Flag affected regions. Do not silently choose a class, move a boundary or interpolate through the defect. Other valid source regions can remain usable.

### 13. Different contexts or agroforestry systems

**Input:** A describes slope limits for mechanized alley cropping; B describes hand-managed contour hedgerows. Another pair studies distinct climate regions.

**Expected output:** Check target system, management and geographical applicability before creating a pool. Preserve separate functions when differing constraints explain the difference.

**Use / review:** Do not count contextual heterogeneity as interchangeable votes. “Agroforestry — system applicability unresolved” stays outside an executable system-level pool until assigned.

### 14. Repeated citations or multiple profiles

**Input:** A establishes a classification. B and C repeat it. D independently estimates another. A also supplies several regional profiles.

**Expected output:** A/B/C contribute one lineage, not three. D contributes one. Select compatible regional profiles before pooling; multiple profiles from A must not multiply its authority.

**Use / review:** Record contributing publications and independent origins separately. Conflicting applicable profiles within one origin require a recorded within-source resolution; do not choose whichever scores highest.

### 15. Unequal source weights

**Input:** At 17°, independent A gives 0.25 with quality weight 0.9; B gives 0.50 with weight 0.6.

**Expected output:** Weighted median is uniquely 0.25 because A carries more than half the total weight. Source range remains [0.25, 0.50]; independent n=2.

**Use / review:** Weighting does not remove disagreement. These illustrative weights concern evidence quality, not slope’s importance in MCDA. No probability or confidence interval is implied.

### 16. Opposite shapes or sparse tails

**Input:** A’s suitability decreases with slope; B peaks at intermediate slope. At steep slopes only A reports a value.

**Expected output:** First investigate score direction, practice and context. If genuinely comparable, retain the contrasting shapes and flag disagreement. At the tail report one-source support.

**Use / review:** Do not force a monotonic curve, fit a trapezoid or extrapolate the missing tail merely to obtain one clean response.

## Equal-weight slope example (scenario 07)

| Slope | A | B | Weighted median set | Interpretation |

|---|---:|---:|---|---|

| 3° | 0.75 | 0.75 | [0.75, 0.75] | Agreement |

| 7° | 0.50 | 0.75 | [0.50, 0.75] | Adjacent-class disagreement; median tie |

| 17° | 0.25 | 0.50 | [0.25, 0.50] | Adjacent-class disagreement; median tie |

| 25° | 0.25 | 0 | [0, 0.25] | Exclusion conflict; median tie |

## Aggregation limits and implementation contract

- The median set contains all minimizers of weighted absolute deviation. When exactly half the weight lies on each side of a gap, retain both endpoints rather than silently selecting the lower score or averaging them. This differs from the current compiler’s lower-median tie convention.

- No automatic live T4 adoption is proposed for a non-singleton median or an exclusion conflict. A later policy must specify how the runtime handles these cases; source-specific profiles remain available.

- Class-anchor sensitivity must be checked before live adoption. Compare plausible monotone anchor alternatives with the same semantics. If conclusions change materially, flag scoring-convention sensitivity; do not call it evidence disagreement.

- Agreement must be reported separately from variable-use frequency and model importance. A paper using slope does not necessarily support any particular slope cutoff.

- Coverage denominator is the compatible, eligible independent-source pool for this response, not every paper in the agroforestry corpus. Report eligible count and contributing count alongside weight coverage.

- Implementation adds an optional schema policy field and regenerates T4 profile scores; evidence records are preserved. Production policy belongs in schema-backed configuration; schema structure changes require the existing manifest and issue process.

## Current versus proposed behaviour

Compiler now supports the semantic anchors and median-set outputs described here. Ordinal source profiles remain separate unless an explicit compatible pool is assigned. Legacy rank/max scores remain alongside the new common scores. Continuous-curve pooling is not implemented.

## Acceptance checks before enabling live synthesis

Each scenario above becomes a regression fixture. Check unit invariance, missing-value preservation, identical-source agreement, lineage-duplication invariance, order independence, exact endpoint handling, median ties, exclusion conflict detection, changing coverage, and rejection of incompatible response meanings. Preserve source functions alongside every generated summary. Review class crosswalks against real papers before selecting a default convention.
