# M08: staged artifact publication

Date: 5 November 2026. Baseline: `7a11a32b788756c55ae612a94e4de48752690911` (merged PR #588). Status: merged in PR #591 at `770f2d9`. This continues the [generator boundaries](m07-generator-paths.md); it does not change evidence authority or complete M08.

## Result

The full generator now compiles every derived artifact in a private staging directory before changing any published file. A late failure in dashboard, scorecard or effect-row compilation therefore leaves the previous published build intact. This applies to separate-output builds and the existing full in-place generator.

The artifact set is frozen from the schema table manifest plus the existing workbook outputs. The conditional progress output remains conditional on the source register. Staging is checked for the exact file set, independent regular files, valid JSON/CSV, sizes and SHA-256 hashes. Existing output bytes seed staging so build history and stable timestamps retain their previous behavior. Publication uses actual artifact hashes, not a producer's report of changed files.

Only changed artifacts are installed. Unchanged files and unrelated files remain untouched. Existing file permissions are preserved; new generated files use mode `0644`. Each replacement is prepared beside its destination, allowing the staging directory and outputs to live on different filesystems. Each final file replacement is atomic.

## Failure behavior and limits

| Failure | Result |
|---|---|
| Validation or compilation fails | No derived output is published. Private staging is removed. |
| An expected artifact is missing, extra, malformed or redirected | Manifest validation refuses publication. |
| Published output changes while staging or preparing replacements | Publication refuses to overwrite it. |
| A file replacement fails or a caught interrupt follows replacement | Already replaced files are restored; newly installed files and empty directories created by this run are removed. |
| Rollback fails, or another writer changes an installed file | That file is not overwritten blindly. Recovery copies and the manifest are retained, and the error identifies their location and affected paths. |
| Cleanup also fails after incomplete rollback | The recovery error remains visible; cleanup paths are attached as additional notes. |

Use stable input snapshots and **one writer per output root** through compilation, installation and rollback. Output drift checks catch observed concurrent edits but are not a shared lock with the review server. Inputs can still change while being read. Do not run an independent in-place generator against the live review checkout during review activity; use a separate snapshot and output directory for migration work.

This is staged publication with rollback for caught failures, **not whole-build atomic visibility or crash durability**. Readers may briefly see files from different generations during installation. Process termination, power failure and persistent filesystem failure can leave a partial installation. A versioned release directory and atomic reader pointer remain future work.

The legacy command still validates and explicitly soft-quarantines evidence before generating artifacts. That source mutation is outside this artifact transaction and is not reversed by a later compilation failure. The separate `--build-only` flow still refuses pending quarantine candidates. `--check` continues to compare without staging or writing. The narrower review refresh, review submission and other direct writer helpers retain their existing behavior; they are not newly transactional.

## Operator use and recovery

Commands are unchanged. From the compiler checkout:

```bash
PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.generate \
  /path/to/stable-snapshot/schema --build-only --output-root /path/to/derived-build

PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.generate \
  /path/to/stable-snapshot/schema --build-only --output-root /path/to/derived-build --check
```

An incomplete rollback reports a `ruralscan-publication-*` recovery directory. Keep it until reconciliation is complete:

1. Stop writers to the affected output root and retain the reported directory.
2. Inspect `manifest.json`: `output_root` names the destination, `artifacts` records staged hashes/sizes, and `previous` records prior states (`null` means absent). `before/` holds the original existing files; `artifacts/` holds the complete compiled build.
3. Compare affected destinations with both copies. Preserve any newer output from another writer; do not restore the entire directory over it. After deciding which build should be published, restore the affected derived files or rebuild into a fresh output directory from the stable source snapshot.
4. Run `--check` against the chosen destination, then remove retained recovery and temporary files. No automatic cleanup of an incomplete rollback is attempted on the next run.

Do not use these artifact backups to roll back source CSVs, evidence decisions or review events. They contain derived outputs only. CIAT remains the sole working authority; no RuralScan repository, consumer pin, scientific policy or live review endpoint changes here.

## Acceptance evidence

The previous generator and staged generator produced identical bytes for all 50 artifacts in independent clean copies of the baseline, with the clock fixed at `2026-11-05T10:00:00Z`. Both legacy in-place builds and fresh separate-output builds matched. See the [parity receipt](m08-publication-parity.json). No normalization was applied.

Failure-injection tests cover late compilation errors, missing/extra/invalid staged artifacts, symlink refusal, preparation failure, failed second replacement, caught interruption immediately after replacement, incomplete rollback, cleanup failure that must not hide recovery, and competing output changes. Integration tests exercise the actual full generator in place and with a separate output root; checks never stage files. Repeated successful builds retain history and do not rewrite unchanged outputs.

Independent review found the interrupt-bookkeeping and cleanup-error masking defects; both were fixed and passed regression tests and re-review. No material finding remains. All **1,127 tests passed** in a clean checkout. Lint/format, scoped type checks, schema synchronization, structure and T4 coverage passed. Structure retains 3,985 existing warnings. Broad type checking retains the same 191 pre-existing diagnostics; none were added. Remote CI results are recorded in the accompanying PR.

Clean copies contain no private corpus, so these checks do not establish source/quote verification. The existing missing/empty explicit-corpus refusal remains enforced. A complete source-verification run still requires the actual acquired corpus.

## Next boundary

M07 still has other entrypoints to make portable. M08 still needs reader-consistent release publication, further separation of compilation from low-level file writers, and review/submission boundaries. No live writer cutover is authorized by completing this slice. Continue with a read-only inventory and bounded refactor of submission/writer paths before introducing release contracts or migrating canonical evidence.
