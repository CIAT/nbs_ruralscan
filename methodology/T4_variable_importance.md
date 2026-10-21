# T4: standardising variable importance within studies

Decision recorded: 21 October 2026. Pete accepted the theoretical comparison below as the convention to implement and test on actual evidence. This is a methodology decision, not evidence approval or a change to runtime weights.

## Separate assessments

Keep variable-use frequency, within-study importance, and agreement on suitability response separate. Retain source weights, hierarchy, units, scope, branch identities and original ranks. Suitability-class ranks (e.g. low/medium/high) are not variable-importance ranks.

Species/crop model importance stays outside generic practice totals. Repeated records or branches do not create independent paper votes. Related publications require a lineage check; shared authorship alone is not proof of dependence. Concept-level and specific-variable support remain distinct.

## Flat-model comparison

For comparable non-negative weights w_i in a complete model with N variables:

- Mean weight = sum(w_i) / N, including the target variable.
- Relative importance R_i = w_i / mean(weight).
- 1 means average emphasis; 2 means twice average; 0.5 means half average.

Weights need not already sum to 100%, provided they share a valid comparable scale. A mean of only the other variables is not the common denominator. Do not infer zero importance from missing weights. Ordinal ranks alone do not support this ratio. Signed or incompatible importance measures require a separately justified treatment.

## Hierarchical comparison

Preserve three views:

1. Within-group ratio: variable's local share divided by the mean among its sibling variables.
2. Flat whole-model ratio: multiply source shares down the path, then divide by the mean contribution across final inputs.
3. Hierarchy-adjusted ratio (primary comparison for hierarchical studies): divide observed path contribution by an equal-allocation benchmark following the same hierarchy. At each split, allocate equally among its children; multiply those equal shares down the path.

The hierarchy-adjusted benchmark is our declared convention, not an assumption attributed to the source. Retain both flat and hierarchy-adjusted ratios so group-size effects remain visible. These quantify emphasis within a model, not predictive accuracy or universal ecological importance.

For a variable repeated in additive branches, preserve each path. Aggregate observed contributions and their matching benchmark contributions only when the source model demonstrably adds those paths and they represent the same variable and scope. Topsoil and subsoil remain distinct unless an explicit aggregation is justified. Missing siblings, unclear nesting or contradictory weight sets prevent a settled ratio; retain alternatives and flag the gap.

## Three accepted theoretical examples

### 1. Flat model with four variables

Rainfall40%, pH30%, slope20%, temperature10%. Mean25%.

| Variable | Raw weight | Relative importance |
|---|---:|---:|
| Rainfall | 40% | 1.6 |
| pH | 30% | 1.2 |
| Slope | 20% | 0.8 |
| Temperature | 10% | 0.4 |

### 2. Flat model with fifty variables

pH5%; other49 variables share95%. Mean2%; pH relative importance = 5/2 = **2.5**. Smaller raw weight than Example1, but greater emphasis relative to other model inputs.

### 3. Hierarchical model with unequal group sizes

Climate60%: rainfall50%, temperature50% within climate. Soil40%: pH50%, depth20%, texture20%, drainage10% within soil.

For pH:

- Within soil: 50/25 = **2**.
- Whole-model contribution: 0.40 × 0.50 = **20%**.
- Flat comparison across six final inputs: 20/(100/6) = **1.2**.
- Equal-hierarchy benchmark: (1/2 groups) × (1/4 soil variables) = **12.5%**.
- Hierarchy-adjusted comparison: 20/12.5 = **1.6**.

| Example | Raw whole-model pH weight | Flat ratio | Hierarchy-adjusted ratio |
|---|---:|---:|---:|
| Four-variable flat model | 30% | 1.2 | 1.2 |
| Fifty-variable flat model | 5% | 2.5 | 2.5 |
| Hierarchical model | 20% | 1.2 | 1.6 |

## Implementation and next validation

1. Implement ratios with regression tests for these examples, rescaled weights, missing siblings, repeated additive branches and incompatible scopes.
2. Reconstruct complete importance inventories for Singh, Nath and Haile from their source tables. Use Singh for flat comparison, Nath for nested/repeated branches, and Haile to test conflicting alternatives. Do not calculate a settled score from an incomplete table.
3. Present one comparison: raw weight, within-group ratio, whole-model ratio, hierarchy-adjusted ratio, source rank, provenance and unresolved assumptions.
4. Propose cross-study summaries only across independent, compatible evidence. Median ratio, spread and source count were proposed; actual eligibility and results need checking before adopting defaults.
5. Use the resulting importance evidence to propose transparent T4 weights for review. No automatic runtime-weight change follows from this decision.

Scope remains the current bounded T4 evidence base. No new discovery sweep or pilot testing is authorised by this note.

## Implemented diagnostic, 21 October 2026

`recipe/importance.py` calculates the comparisons. `scripts/report-t4-importance.py` regenerates the bounded audit CSV/JSON and side-by-side HTML from `pipeline/t4_audit/agroforestry/importance_2026-10-21/source_weight_trees.csv`. These are diagnostic artefacts, not schema tables or runtime weights.

Flat **path** ratios use all leaf slots; flat **variable** ratios use distinct variable/scope inputs after additive consolidation. Nath therefore has 26 paths and 24 distinct inputs. Hierarchy benchmarks retain each original branch. All source inputs, including operational variables, remain in the original model denominator. Source names in this audit are not newly approved ontology bindings.

Singh's printed weights total 99%, Haile Table 5 totals 99.9%; ratios normalise the observed sums and retain printed values. Singh's RF importance column is a separate comparison, not an extra source. Haile's two conflicting tables remain alternatives. Source model lineage, PDF hash and table/page locators are retained.

## Candidate-weight sensitivity follow-up

The three-paper diagnostic now includes an explicit slope/rainfall subset. Normalising median hierarchy-adjusted ratios gives provisional 73.75%/26.25%; substituting Haile Table 3 gives 71.43%/28.57%. Excluding Singh moves the pair close to equal weights. These outcomes expose panel sensitivity, not a validated runtime-weight recommendation. Retain equal weights as the comparison baseline pending system/context compatibility and full variable-selection review.

Haile Table 5 approximately reproduces its printed pairwise matrix using the stated algorithm; this supports its use as the provisional computed-AHP representation. It does not resolve which weights generated the published map. Both tables remain available; no human approval or runtime rule is changed.

## Pete's decision — 21 October 2026

Pete approved the candidate-comparison recommendation in chat ("ok proveed agreed"):

- Retain equal weights as the baseline for the declared slope/rainfall comparison.
- Keep pooled importance-based weights as sensitivity scenarios, not runtime defaults.
- Retain Haile Table 5 as the provisional computed-AHP representation, with Table 3 as an alternative; which weights generated the published map remains unresolved.

This approves the comparison approach and recommendation. It does not approve new evidence records, global transfer, a complete family-specific variable set, or changed runtime weights.

### Review status of model-use counts

The variable-use inventory retains all source-checked model-use claims, including
claims carried only by quarantined records. Its summary partitions papers, within
each variable and claim scope, into reviewed (at least one active `reviewer_ok`
record), pending (active records but none approved), and quarantined-only. Repeated
records and DOI aliases count once; a reviewed paper with additional pending
records is counted as reviewed, while the detailed inventory lists those pending
records explicitly. Approval is record-level: later metadata corrections and
reported importance weights may still require review. These are counts of paper
use, not independent-origin agreement, compatible-context support, or agreement
on numerical suitability thresholds. No runtime weight changes follow from them.
