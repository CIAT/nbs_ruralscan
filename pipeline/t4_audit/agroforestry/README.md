# Agroforestry T4 branch trial — 19 October 2026

**Status: experimental draft, not validated suitability rules.** Branch `codex/t4-compilation-audit`; baseline commit `51750fa2afc1dc7c00652dee329c8708bced885e`. Live recipes and evidence registers were not rewritten.

## Comparison

| Family | Baseline generated rows | Draft generic rows | Separate crop rows | Approval-filtered generic rows |
|---|---:|---:|---:|---:|
| cross_family | 2 | 2 | 0 | 2 |
| homegardens_proximity | 0 | 0 | 0 | 0 |
| linear_boundary | 0 | 0 | 0 | 0 |
| planted_silvoarable | 3 | 1 | 0 | 2 |
| regeneration_farmland | 2 | 1 | 0 | 1 |
| shaded_perennial | 1 | 1 | 4 | 0 |
| silvopastoral | 0 | 0 | 0 | 0 |

All ten design rows are preserved in both isolated trial CSVs. Approval-filtered output is still a draft: approval flags do not establish that old encoded bounds are scientifically correct. The four crop rows concern **Morus spp.**, not a generic coffee/cocoa envelope; their F5 applicability needs review. They appear only in the report’s crop lanes, never in the generic recipe CSV.

## Structural evidence dispositions (all-active draft)

| Disposition | Records |
|---|---:|
| qa_dropped | 188 |
| unsupported_numeric_encoding | 47 |
| selection_only | 23 |
| qualitative_relationship | 20 |
| class_or_gate_requires_mapping | 15 |
| crop_scope | 13 |
| parameter_contributor | 9 |
| species_scope | 7 |
| crop_lane | 7 |
| selection_only_or_missing_relationship | 6 |
| inconsistent_bound_order | 3 |
| mixed_relationship_types | 2 |

Each of 340 structural records has one top-level disposition. The 188 QA-dropped records remain retained; 152 remain active. Crop-lane details are nested separately. Unsupported numerical encodings include weights and scenario grids as well as possible thresholds: this count is not a claim that all are recoverable suitability rules.

## What changed

- T4 runner reads source CSV directly, avoiding stale generated JSON inputs.
- Support denominator uses T4 searches only and labels its basis provisional. It is not yet a deduplicated screened-paper denominator.
- Crop policy matches the real F5 family; different taxa are kept separate.
- Narrative claims cannot displace numeric claims. Distinct claims/contexts survive; each origin gets at most one weighted vote per parameter.
- Only actual parameter contributors enter threshold provenance and independent-source uncertainty counts. Selection support remains separate.
- Explicit hard thresholds, canonical class maps and piecewise curves preserve their types and units. Differing typed rules require a decision rather than an invented averaging policy.
- Inconsistent bound order and mixed response shapes are held for review. Selection-only evidence cannot set shape parameters.
- Reports preserve all evidence dispositions, selection candidates, original relationship payloads, per-parameter provenance, crop lanes and input hashes.
- T3/T6 shared lineage function is unchanged. No evidence decisions were applied.

## Why fewer generic rows

Planted slope now exposes a hard-exclusion threshold versus a terrain-envelope conflict. Canopy now exposes optima above the old absolute maximum, rather than discarding those claims. FMNR slope was carried by selection-only WOCAT evidence. Those three rows are withheld from the all-active draft. Five generic rows remain, including suspect old bounds awaiting human correction; do not use them operationally.

## Decisions still needed

1. **Source semantics:** review the 12-item batch in `docs/review.html`, selecting “Agroforestry T4 compilation: bounds and encoding review”. Review questions and highlighted PDF passages are included. Evidence IDs/questions also live in `review_items.csv` for batch rebuilds.
2. **Cross-family applicability:** decide between explicit applicability-based inheritance and separately reviewed family-specific mappings. Recommendation: inherit only claims explicitly applicable to the selected family, preserving original evidence IDs; never blanket-copy all general claims. No inheritance implemented pending the existing methodology decision.
3. **Class-table mapping:** review source-specific class meanings, units and dataset coding before converting legacy nested/free-form tables. No “low” class becomes an exclusion automatically.
4. **Support denominator:** reconcile unique screened sources across overlapping T4 searches and historical table-level searches. Current percentages are diagnostics only.
5. **Review policy:** choose when approved-only synthesis becomes the publication default. Both modes are available for comparison; unresolved records are explicitly labelled.

## Reproduce

```sh
uv run python scripts/synthesise-recipe.py agroforestry --output-dir pipeline/t4_audit/agroforestry/draft --report pipeline/t4_audit/agroforestry/draft/report.json
uv run python scripts/synthesise-recipe.py agroforestry --approved-only --output-dir pipeline/t4_audit/agroforestry/approved --report pipeline/t4_audit/agroforestry/approved/report.json
uv run python scripts/build-review-batch.py agroforestry-t4-compilation-oct19 --title "Agroforestry T4 compilation: bounds and encoding review" --items pipeline/t4_audit/agroforestry/review_items.csv
```

The baseline records the starting commit, source-file hashes and original recipe rows. Reports are generated trial artifacts, outside the frozen schema tables. Use `--report` with `--dry-run` to write only a report; without `--report`, dry-run writes nothing. Normal writes also emit a `T4_synthesis_report.json` companion.

## Validation

- Full pytest suite: 352 passed; after adding three further writer/shape tests, focused T4 regression suite: 14 passed. Final combined T4/T3/T6 regression run: 112 passed.
- Ruff lint and format: passed.
- Type checks on changed Python files: passed. Repository-wide type check remains blocked by errors in unchanged files (`cell_synthesis.py`, `log-primary-references.py`, `test_access_status.py`, `test_grey_discount.py`) and an existing import warning.
- Schema structure: zero errors, existing warnings. Generator and generator `--check` passed; generated review summaries now include the new batch.
- Review batch: 12/12 evidence IDs resolved; all 12 have highlighted cached-source page crops. Soil-depth crop visually checked.
- Original live T4 file is byte-identical (tested). No EV/SRC edits, review verdict changes, or main-branch publication.
