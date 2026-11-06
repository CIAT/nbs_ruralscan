# M07/M08: explicit evidence-intake inputs and joint register publication

Date: 6 November 2026. Baseline: `aee4c16dfbe5aec44892cb6763923ec54354db6f` (merged PR #606). Status: merged in PR #609 (`cf0ecdcb3adeeaa70c407fc7199741144f780435`). This migration receipt remains in the existing project workspace, outside destination product repositories.

## Result

The active gated staging-to-register entrypoint now uses `schema_tools.evidence_intake`. Its `EvidenceIntakePaths` context declares nine files and a corpus directory. Inputs no longer depend on where the compiler is installed or the command's working directory.

| Input | Purpose | Written by intake? |
|---|---|---|
| EV CSV | Existing evidence, field names, ID deduplication and correction protection | Yes: append new gated units |
| SRC CSV | Source identity and extraction state | Yes: resync variables and stamp pending sources |
| Acquisition queue CSV | Verified source identity | No |
| FAM, VONT, BANDS CSVs | Family/practice agreement, variable IDs and magnitude checks | No |
| T7 CSV | Accepted geographic context values | No |
| Direction-sense and M2b policy CSVs | Direction interpretation and operational-risk exclusions | No |
| Corpus directory | Cached PDF or section snapshot used to verify claims | No |

All declared inputs must exist. Incomplete snapshots fail before any register changes; missing policy files cannot silently disable checks. Existing empty policy tables keep their meaning. Direction senses are read once per gate call and passed as values, so successive calls observe updates to a selected policy file without using an old path-keyed cache.

The script remains a compatibility entrypoint. Existing arguments and checkout defaults remain available, including explicit opt-in for structural and operational roles, the family-decision reference, run ID, extractor and dry-run behavior. Current gate decisions are preserved: source identity, cached artifact checks, native and supplementary quotes, numbers, context, bands, direction, variable/family membership, role and ruleset. This is not a new scientific review or an expansion of supported artifact adapters.

## Usage

Existing checkout workflow:

```bash
PYTHONPATH=src uv run python scripts/ingest-effects-staging.py \
  /path/to/staged-units.json --run-id authorised-run --dry-run
```

Isolated rehearsal with explicit data and artifact locations:

```bash
PYTHONPATH=/path/to/compiler/src uv run python \
  /path/to/compiler/scripts/ingest-effects-staging.py \
  /path/to/staged-units.json --root /path/to/disposable-data-copy \
  --corpus-dir /path/to/cached-artifacts --run-id authorised-run --dry-run
```

Remove `--dry-run` only when intending to update the selected data copy. `--root` selects the records to validate **and write**; it is not an output-only directory. Relative staging paths and explicit corpus paths are resolved against the caller's working directory. The default corpus is `<selected root>/.cache/corpus`.

Direct callers construct `EvidenceIntakePaths` with individual paths, then call `gate(..., paths=...)` for validation or `ingest(..., paths=..., run_id=...)` for validation plus publication. Flat or split EV/SRC layouts are supported. The script retains its importable `gate` compatibility entrypoint.

## Publication boundary

EV and SRC are copied to private staging before the gate runs. The existing append, variable-resync and extraction-stamp functions receive those explicit staged filenames. Both complete successfully before either destination is installed. Publication is restricted to these two files, rejects redirected/shared targets and input aliases, and checks for destination changes before replacement. A rejected batch never saves a partial append.

The existing ID rules remain: identical units are skipped; differing claims under an existing ID require an audited correction; existing approval/drop fields survive reruns. Active variables exclude dropped and dataset rows. Already swept or signed-off sources retain their first extraction metadata.

Caught publication failures roll back. Incomplete rollback or cleanup retains recovery material and reports its location; stop writers and reconcile before retrying. This uses the existing publication helper: it is not crash-safe, atomically visible across both files, or a lock against concurrent review. Use stable inputs and one writer for the selected copy.

Intake does not stamp the progress ledger or SRCH, regenerate JSON, compile recipes, submit a PR, move artifacts into the library or alter review decisions. These remain separate steps in the existing authorized workflow. The source-to-evidence boundary still requires acquired and verified sources; explicit paths do not bypass it.

## Verification

The [parity receipt](m07-evidence-intake-parity.json) compares separate baseline and candidate processes using the complete maintained register: 6,369 evidence rows and 741 source rows before the synthetic fixture. Both gates emitted the same 8,367 ordered findings for those records with no private corpus. This checks unchanged diagnostics, not validity of historical records or their source quotes.

A clearly synthetic cached PDF supplies two test claims, one structural and one effect claim. Its exact bytes are shared between comparisons. Against the full existing registers, old and new commands produce byte-identical EV/SRC results for dry-run, append, identical rerun, rerun after a simulated review/drop, and a conflicting batch. Only EV and SRC change. The candidate compiler has no schema directory during this rehearsal and reads a separate data copy. No output normalization is used.

The 33 focused cases exercise flat and split input layouts, foreign working directories, selected policies, same-path policy edits, required missing inputs, dry-run immutability, existing review/drop state, signed-off sources, whole-batch conflicts, failure in each staged mutation, second-file installation failures before and after replacement, linked/aliased targets and the relocated CLI. Independent code and receipt review found no blocking issue.

Lint/format, scoped type checks, schema synchronization (zero stale artifacts), structure and T4 coverage passed. The broad source-package type check retains the same 16 baseline diagnostics by type, file and count; none were added. Structure retains 4,028 existing warnings. All **1,336 tests passed** in the disposable candidate checkout (five existing Swig deprecation warnings). The candidate includes the subsequently merged UI-only changes through `f813fde`; intake parity remains pinned to PR #606 because those upstream changes do not affect intake.

## Remaining boundary

This slice covers active `ingest-effects-staging.py` intake only. Discovery registration, acquisition, metadata verification, source promotion, historical `migrate_effects.run`, quarantine, and other review/local-state writers still require their own migration and failure-recovery work. Direct lower-level historical helpers retain their existing behavior.

M07/M08 remain open for those paths, authored/generated configuration separation, contracts and reader-consistent releases. No evidence authority has moved. Live review services, pending decisions, canonical registers and runtime pins remain untouched by this rehearsal.
