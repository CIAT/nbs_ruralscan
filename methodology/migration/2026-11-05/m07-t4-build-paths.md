# M07, first slice: explicit T4 build inputs

Date: 5 November 2026. Baseline: `1703e20bbf82896985beee0397e7b6838b4c00b1` (merged PR #585). Status: implemented and reviewed; pending merge. M07 remains partial.

## Result and boundary

T4 compilation can now read a separate data snapshot without loading code from that snapshot or changing module-level paths. The existing command remains available. This removes one dependency on the original checkout layout before any evidence migration.

Previously, the developer-package rebuild loaded `scripts/synthesise-recipe.py` from the selected data checkout, rewrote its global paths and patched its CSV reader. Imported helpers could still come from a different installed checkout while provenance recorded the copied code. The rebuild now calls one explicit-input adapter and records data and compiler source fingerprints separately.

CIAT remains the working authority. This change does not move registers, change scientific rules, update runtime pins, publish an analytical release or change the running review service. Authored gates, scenario fields and weights remain in the audited recipe; separating that mixed authored/generated table requires the ownership decisions already recorded in Phase 0.

## Interface

`nbs_ruralscan.recipe.t4_build.T4BuildInputs` declares six files:

| Input | Purpose |
|---|---|
| `evidence` | EV evidence register |
| `sources` | SRC source metadata and credibility |
| `ontology` | VONT grouping, units, conversions and dataset choices |
| `crop_scope_policy` | Authorized crop-scope inclusion |
| `numeric_policy` | Authorized numerical compilation policies |
| `audited_recipe` | Accepted comparison baseline and authored design fields |

Construct the object directly for arbitrary file locations, or use `T4BuildInputs.from_root(root, nbs_id)` for the current CIAT layout. The adapter's `synthesise` requires these inputs; `write_recipe` also requires an output directory. Neither changes global paths or the current working directory.

The compatibility command keeps its existing default paths and arguments. To build an isolated candidate from another input snapshot:

```bash
PYTHONPATH=src uv run python scripts/synthesise-recipe.py agroforestry \
  --source-root /path/to/input-snapshot \
  --output-dir /path/to/new-trial-output
```

`--dry-run` writes nothing. Without `--output-dir`, the established command writes to the selected snapshot's recipe directory, as it did for the default checkout. Diagnostic `--include-unreviewed` output and reports must stay outside the input, launcher and executing compiler checkouts, except their existing `pipeline/staging/` area. The guard also works when those three roots differ.

`developer_corpus.rebuild(root, nbs_id)` accepts a data-only snapshot containing the six input files. It compiles the full authorized practice corpus before downstream country filtering, compares against the audited recipe and returns evidence dispositions. Stale audited recipes still fail closed. The rebuild writes only temporary outputs and checks input/compiler source hashes before and after execution.

## Provenance and publication

The rebuild report's `input_sha256` now identifies the six data/baseline inputs. `compiler_source_sha256` separately fingerprints the executing installation's recipe/runtime Python files and typed CSV reader. These are source-tree fingerprints, not an environment lock or a claim that every listed file executed. Python, dependency and runtime-environment contracts remain future work.

The full developer package still requires its existing complete checkout, documents and manifest inputs. Before staging and before publication, it refuses copied compiler sources that differ from the executing installation. Data-only rebuild portability does not yet make the whole package publisher independent of repository layout. Existing published packages and pins are unchanged.

## Acceptance evidence

- All six practices reproduced their pre-change outputs: 47 comparison artifacts covering recipe CSVs, per-family JSON, complete family reports, normalized corpus reports and existing refusal messages. See [hash record](m07-t4-parity.json).
- Only provenance fields `input_sha256` and `compiler_source_sha256` were excluded from corpus-report parity; all scientific results and dispositions were compared unchanged.
- Agroforestry, forest restoration and mangrove restoration reproduced their audited baselines. Riparian buffer, water harvesting/conservation and wetland management already refused stale audited recipes before this change; those exact refusals remain. This refactor does not approve replacement recipes.
- Focused tests cover data-only snapshots, arbitrary file names, unrelated working directories, failed-build isolation, ignored copied scripts, source fingerprints, publication mismatch refusal and draft-output guards with three separate roots. Existing full-corpus and package-mutation tests remain in place.
- Independent adversarial review found a relocated-launcher guard gap; the fix and both output/report regression cases passed re-review.

Validation: 1,092 tests passed in a clean checkout with Git metadata; 93 focused tests passed in the working checkout. Lint/format, changed-module and CI-core type checks, schema synchronization (zero stale files), frozen structure and T4 coverage passed. The clean checkout contains no private corpus, matching CI's documented validation mode.

Local quote verification is limited by 14 missing cached source artifacts: the initial working-checkout run passed 1,089 tests and failed its one corpus-dependent generator check, before two additional guard cases were added. Clean-checkout success cannot establish quote validation. No source-validation guard was changed. The broad type checker has 191 existing diagnostics, identical to the baseline; these are separate from the passing scoped type checks.

## Next bounded change

Continue M07 by giving the schema/workbook generator explicit input, corpus and output paths. First separate its read-only validation path from quarantine/register mutation; write-mode `generate.py` currently combines those responsibilities. Preserve existing wrappers and compare schema JSON, workbook data and review exports on copies. M08 then separates validation, compilation, UI publication and submission into independently callable boundaries. Review authority and live writer paths move only at the later continuity/cutover gates.
