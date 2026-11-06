# M07/M08: explicit T3/T6 synthesis inputs and candidate outputs

Date: 6 November 2026. Baseline: `358b6fc370ae7d9e8934210b9d34f99962f2affd` (merged PR #602). Status: merged in PR #606 (`aee4c16dfbe5aec44892cb6763923ec54354db6f`). This migration receipt stays in the existing project workspace, outside destination product repositories.

## Result

T3/T6/T6E synthesis now runs from declared inputs without selecting data or policies from the installed compiler checkout. `recipe.t3t6_build` contains the existing synthesis orchestration and a `T3T6BuildInputs` context. The script remains a compatibility wrapper with its existing default checkout, preview behavior and four output names.

The context declares fourteen paths:

| Inputs | Role |
|---|---|
| EV typed JSON; SRC, FAM and XW CSVs | Evidence units, source context, practice families and target routing. |
| Income groups and IPCC confidence matrix | Context normalization and confidence lookup. |
| Comparator, route, family-rollup and crop-scope policies | Inclusion and aggregation decisions. |
| Effect locus, magnitude bands and design weights | Effect location, numeric interpretation and weighting. |
| Source recipe prose sidecar | Previously authored text, applied only to matching evidence/class. |

The evidence format remains the maintained **typed EV JSON** used by the existing effect pipeline. CSV remains authoritative; use the existing generator synchronization check before selecting a snapshot. This change does not regenerate or silently substitute evidence formats during synthesis.

Input loading captures all policy values. Synthesis passes selected magnitude bands and design weights through global, family and scope contributions and magnitude summaries. It never falls back to installed-checkout files for an explicit context. Lower-level engine callers that omit these optional parameters retain legacy defaults; those defaults now load lazily, avoiding schema reads at import. Explicit empty lists/dictionaries remain empty.

Every declared input except the optional prose sidecar must exist. A missing evidence file, policy or staging preview is reported before compilation can publish empty recipes. An absent prose sidecar still means no authored prose. These missing-input checks intentionally replace the old silent fallback/empty-pool behavior for incomplete snapshots.

## Commands and API

The existing command retains its default behavior:

```bash
PYTHONPATH=src uv run python scripts/synthesise-t3t6.py riparian_buffer
```

It writes the current recipe. For an independent candidate, choose separate source and output paths:

```bash
PYTHONPATH=src uv run python scripts/synthesise-t3t6.py riparian_buffer \
  --source-root /path/to/input-snapshot \
  --output-dir /path/to/candidate/riparian_buffer
```

An explicit source root requires a separate output directory for writes. Output cannot overlap the selected snapshot or compiler checkout. A dry run needs no output directory and writes nothing. `--staging` remains preview-only and requires `--dry-run`; staging is not a route around central registration gates. NbS identifiers are checked before deriving paths.

Direct callers can construct `T3T6BuildInputs` with individual file paths, so a repository-shaped directory is optional. Use `load_inputs(..., inputs=...)`, then `synthesise(nbs_id, loaded)`, then `write_recipe(..., inputs=..., output_dir=..., dry_run=False)`. The writer reads prose from the declared source sidecar, never from the output directory. Copied scripts in a data snapshot cannot select a different compiler.

The writer publishes exactly four files: T3 CSV, T6 CSV, T6E CSV and the synthesis-report JSON. It prepares all four before installation using the existing publication helper. Unrelated output files survive. Caught installation failures roll back; incomplete rollback retains recovery copies. Input aliases, redirected destinations and shared hard links are refused. Publication still requires stable inputs and one writer; it is not crash-safe or atomically visible across multiple files. Generating typed recipe JSON and accepting a release remain separate operations.

## Fragility caller

`row-fragility.py` now consumes the same captured policies and selected recipe rows. Its new `--source-root` option requires an explicit `--out` outside the snapshot/compiler; existing default invocation retains its locations. The report is published safely as one CSV. Redirected or hard-linked output files cannot truncate selected inputs. Empty roll-up tables produce a header-only report instead of truncating the report and failing on the first-row lookup.

This tool remains diagnostic. It does not edit recipes or settle evidence decisions.

## Verification

Focused tests cover foreign working directories, flat input layouts, interleaved policy sets, captured-policy synthesis with file reads forbidden, missing declared inputs, empty policy values, source-versus-destination prose, stale prose, preview-only staging, invalid identifiers, protected output paths and failed recipe installation. Engine tests verify selected bands/weights reach global, scope, family and magnitude-summary calculations. Fragility tests cover selected rows/policies, unchanged source files, output links and empty tables.

All **1,303 tests passed** in a clean checkout. Lint/format, scoped type checks, schema synchronization (zero stale artifacts), structure and T4 coverage passed. Broad type checking retains the same 194 baseline diagnostics by type, file and count; none were added. Structure retains 4,028 existing warnings. Independent code and documentation review found no remaining blocking issue.

The independent [all-practice parity receipt](m07-t3t6-parity.json) compares six practices using separate old/new compiler processes and identical selected inputs. All **24 published CSV/report files** and six pre-prose payloads matched byte for byte, without normalization. The outputs also match the committed baseline: **271 T3 rows, 378 T6 rows and 72 T6E rows**. The riparian fragility report's ten roll-up rows matched as well. A code-only candidate compiler with no schema directory successfully read a separate 185-file data snapshot; that snapshot and all six prose sidecars remained unchanged.

Clean verification copies contain no private corpus; these checks do not establish source/quote verification.

## Remaining boundary

This is a portability and publication step, not an analytical-method revision or accepted recipe release. Existing classes, thresholds, confidence rules, scope routing, row IDs, prose checks and T6/T6E separation remain unchanged for complete identical inputs. No working evidence, recipe tables, runtime pins or live review services are changed by the migration rehearsal.

M07/M08 remain open for remaining intake paths, authored/generated configuration separation, release contracts and reader-consistent publication. Full-corpus before-filter checks, semantic reconciliation against accepted recipe baselines and the all-writer cutover rehearsal remain required. Review continues under the existing working authority.
