# Cross-source weight normalisation

*Resolves the synthesis half of the `uninterpretable_weight` QA flag (2026-06-23): "how do we standardise to interpret weightings between sources?"*

## The problem

Extracted weights arrive in **incompatible encodings**. A bare `5` or `0.24` cannot be compared across sources without putting it on a common footing:

| Encoding (`relationship` key) | Example | Scale | Σ=1? |
|---|---|---|---|
| `ahp_weight` | moisa_2025 slope = 0.24 | 0–1 (Saaty priority) | yes |
| `relative_weight` | singh_2026 dist_road = 0.28 | 0–1 (RF normalised) | yes |
| `variable_importance` | singh_2026 dist_road = 21.29 | raw RF | no |
| `weight` (tool slider) | saraheb3 water-erosion = 5 | 0–N (per-practice) | **no** |

## The rule — two bases that must NOT be averaged together

- **SHARE** — a fraction of a source's *total* importance (Σ=1 across that source's variables). AHP and RF weights are shares. Comparable as "what fraction of importance did this source give the variable."
- **INTENSITY** — a value on its own fixed scale (e.g. a 0–10 slider), set independently per variable, **not** a share. Tool defaults are intensities → `normalised = value / scale_max`.

A tool weight of `5/10` (intensity 0.5) is **not** the same thing as an AHP weight of `0.5` (half of all importance). Conflating them is the trap. The normaliser tags every value with its `basis` and an `is_share` flag; comparison views report the basis alongside the number and never merge the two.

## Normalisation (deterministic)

| kind | → normalised | basis |
|---|---|---|
| `ahp_weight` | unchanged (already 0–1 share) | `ahp_priority_share` (share) |
| `relative_weight` | unchanged (already 0–1 share) | `rf_relative_share` (share) |
| `variable_importance` | ÷ source's total raw importance | `rf_importance_share` (share) |
| `weight` (tool) | ÷ `scale_max` (saraheb3: erosion/SOC 10, water-quality 5) | `tool_slider_intensity` (intensity) |

Implemented in `src/nbs_ruralscan/schema_tools/weight_norm.py`:
- `extract()` — pull weight-bearing active EV rows.
- `normalise()` — add a 0–1 `normalised` per basis.
- `compare()` — group by variable for cross-source comparison.
- CLI: `python3 src/nbs_ruralscan/schema_tools/weight_norm.py schema`.

## Scope — evidence, not an MCDA input

This is an **evidence-comparison** view. The MCDA still computes its own weights at runtime (AHP + CRITIC + Entropy, α-reconciled — Benson's framework); extracted literature/tool weights are **benchmark**, never injected as MCDA inputs. Normalisation answers "is variable X consistently weighted high across sources?", not "what weight should the MCDA use."

## Limits

- Tool-slider intensities are normalised *per their own scale* — comparable as "how strongly weighted on its own scale," not as a share of a variable set.
- Shares are only comparable *within the same variable set*; a source weighting 3 variables vs one weighting 12 gives shares of different denominators (noted, not corrected — rank-based comparison is the fallback when this matters).
