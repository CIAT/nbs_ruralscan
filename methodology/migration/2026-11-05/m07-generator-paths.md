# M07/M08: generator paths and operation boundaries

Date: 5 November 2026. Baseline: `6c28a64a367eafc695d42c7fdf754e170c103d6b` (merged PR #586). Status: merged in PR #588 (`7a11a32b788756c55ae612a94e4de48752690911`). This is a bounded continuation of the [T4 adapter](m07-t4-build-paths.md), not an evidence cutover.

## Result

The schema/workbook generator now distinguishes read-only validation, explicit quarantine of evidence, and publication of derived artifacts. A separate-output build reads a selected CIAT-shaped snapshot and writes its generated schema JSON and workbook data to another directory. It does not rewrite source CSVs, review decisions or input artifacts.

The old command and review-server calls retain their established order: validate sources/ledger/policy, apply automatic soft quarantine on write runs, then regenerate artifacts in place. `--check` validates and compares without quarantine or creating directories. Review refresh and submission remain on their current authority and endpoints.

## Commands and inputs

Run from the compiler checkout, with its existing environment:

```bash
# Existing compatibility command: includes automatic quarantine on writes.
PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.generate schema

# Validate only; no quarantine, generated files or directories.
PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.generate \
  /path/to/snapshot/schema --validate-only

# Publish derived artifacts separately, without changing the source snapshot.
PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.generate \
  /path/to/snapshot/schema --build-only --output-root /path/to/derived-build

# Check that same destination without writing it.
PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.generate \
  /path/to/snapshot/schema --build-only --output-root /path/to/derived-build --check
```

`--corpus-dir /path/to/corpus` supplies an explicit source-artifact directory to any mode. An explicitly missing directory is an error; an existing empty or incomplete directory still fails source validation. Without the override, the existing local-versus-CI rule remains: use the snapshot's `.cache/corpus`; an absent directory is reported as skipped validation. This refactor does not make CI a substitute for source/quote verification.

Inputs retain the current layout: `schema/`, `pipeline/`, `methodology/`, `reference/` and source assets/metadata in `docs/`. Snapshot builds reject renamed schema directories because the downstream recipe contracts still expect `schema/`. Data-only snapshots need no copied `scripts/` or `src/`; the installed compiler supplies code. This is explicit location handling, not yet a method/evidence package format with independent directory layouts.

The Python boundaries are `SchemaBuildPaths`, `validate_inputs`, `quarantine_inputs`, `publish_outputs` and `build`. `generate(schema_root, check=...)` remains the compatibility wrapper. Low-level publication expects validated inputs; use `build` for a complete non-quarantining workflow. The existing quarantine command remains an explicit operation; no new command automatically repairs an isolated snapshot.

## Isolation and semantic safeguards

- A non-quarantining build refuses snapshots with pending automatic-quarantine candidates and lists their evidence IDs. Otherwise legacy and isolated builds could report different active evidence from the same raw input. Reconcile deliberately before publication; no hidden in-memory drops are introduced.
- Ledger, acquisition metadata, learning cursor, direction/scope/species checks, review exports/batches and class-code legends read the selected snapshot. Optional helper arguments retain old defaults for other callers. Class legends are read afresh, preventing one snapshot's labels leaking into another build.
- Source revision comes from the selected snapshot's own Git root. An unversioned snapshot reports `unknown`; an unrelated working directory or ancestor checkout cannot supply its revision. Unchanged artifact history retains its original commit stamp.
- First publication to a new destination inherits the selected dashboard snapshot's build history; subsequent builds use the destination's history. Missing destinations still report stale under `--check`.
- Flattened effect rows use current CSV inputs through the same typed reader as schema generation. Stale input JSON cannot contaminate isolated output or its stale check.
- Preflight checks all derived destinations before validation/mutation: output roots cannot overlap selected inputs, the compiler checkout or an explicit external corpus. Symlink redirection, hard-linked files, non-file leaves and non-directory parents are refused before writing.

The output directory contains derived data, not a standalone website: HTML, JavaScript, styles and other source assets are not copied. No new RuralScan repository, analytical policy, evidence row, runtime pin or live review service is changed by this implementation.

## Acceptance evidence

The old and new compatibility builds were run on independent clean copies of baseline `6c28a64`, with the same fixed clock. All **50 generated artifacts** matched byte for byte: manifest-driven schema JSON plus progress, dashboard data, review decisions, table progress, scorecard and flattened effect rows. No normalization was applied. Neither snapshot had pending quarantine candidates. See [hash receipt](m07-generator-parity.json).

Integration tests cover separate and repeated builds, unchanged source inventories, conflicting legends/reviewers, current CSV versus stale JSON, read-only validation/checks, wrong working directory, missing/empty explicit corpus, invalid selected ledger, quarantine refusal and legacy soft-drop behavior, unsupported layouts, symlink escapes and hard-linked outputs. An existing quarantine fixture was updated to carry its own policy CSV rather than depending on the installed checkout.

Independent review identified hard-linked output leaves as an overwrite route. The conservative refusal and regression test passed re-review. All 1,108 tests passed in a clean checkout. Lint/format, scoped type checks, schema synchronization, structure and T4 coverage passed. Broad type checking has the same 191 pre-existing diagnostics on baseline and candidate. Remote CI status is recorded in the accompanying PR. Clean copies contain no private corpus, so those checks do not establish source/quote verification.

## Remaining work

M07 remains bounded to explicit T4 and generator contexts. At the close of PR #588, publication still wrote files sequentially, so a late failure could leave partial derived output. The following [M08 staging slice](m08-staged-publication.md) addresses compilation isolation and caught-error rollback. Reader-consistent release publication, deeper separation of compilation from artifact writing, and submission/writer boundaries remain open. Build from stable snapshots; concurrent source edits are not locked by these interfaces.

Authored/generated T4 ownership, method/evidence release contracts and live writer cutover retain their existing approval and continuity gates. Review continues in CIAT throughout.
