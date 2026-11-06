# M07/M08: explicit metadata verification and recoverable queue/audit writes

Date: 6 November 2026. Baseline: `7f41289bda9529a21c65ed5175e4c748d2b58101` (merged PR #614). Status: implemented; pending merge. This internal migration receipt stays outside destination product repositories.

## Result

`MetadataVerificationPaths` selects the acquisition queue, source register, cached-artifact directory and DOI audit report independently of compiler location. Existing `verify()`, `verify_titles()` and `check()` calls remain available. Explicit verification calls no longer read the compiler's queue, corpus or source register.

DOI verification prepares queue and audit report together before publishing either. Title verification prepares only the queue; it leaves the DOI audit report unchanged. The shared publication helper validates complete CSV/JSON output and restores previous files after caught installation failures. Incomplete recovery retains its recovery material and raises `PublicationRecoveryError` rather than reporting success. Successful counts print only after publication or completed preview.

## Commands and API

Use the project's Python 3.12+ environment. Rehearse against a disposable data copy:

```bash
uv run python /path/to/compiler/src/nbs_ruralscan/schema_tools/verify_metadata.py \
  verify-titles --root /path/to/disposable-data --corpus-dir /path/to/cached-artifacts --dry-run

uv run python /path/to/compiler/src/nbs_ruralscan/schema_tools/verify_metadata.py \
  verify --root /path/to/disposable-data --dry-run

uv run python /path/to/compiler/src/nbs_ruralscan/schema_tools/verify_metadata.py \
  check --root /path/to/disposable-data
```

`verify --dry-run` still queries Crossref and runs the normal identity checks; it saves neither queue nor audit report. `verify-titles --dry-run` checks cached files without saving. Remove `--dry-run` only when intending to publish the selected records. `check` remains read-only and is still the default command; it rejects the redundant `--dry-run` option. `--corpus-dir` is relative to the caller's working directory when relative; otherwise the selected root's `.cache/corpus` is used. Direct-file invocation works without an installed project or `PYTHONPATH`; PDF checks still require PyMuPDF.

Library callers construct `MetadataVerificationPaths(queue, sources, corpus, report)` or `.from_root(root, corpus=...)`, then call `verify(paths=..., dry_run=...)` or `verify_titles(paths=..., dry_run=...)`. No-argument calls retain the existing checkout defaults. `check(queue_path=..., sources_path=...)` is unchanged. The source register is protected but never written; its absence retains the existing optional-SRC check behavior. A missing corpus leaves uncached title candidates unchanged.

## Identity behavior preserved

- DOI verification targets pending rows (including blank status as pending), keeps two workers and the existing Crossref retries. Matching titles stamp verification and rebuild citations from authoritative metadata. Definitive missing DOI or title mismatch blanks the DOI and preserves the title-bearing citation and explanatory note. An unavailable service leaves every existing field unchanged; an outage is never treated as a proven mismatch.
- Title verification targets acquired/extracted DOI-less rows. URL-only code/web snapshots skip the title-page check. Existing manual confirmations remain valid; missing cached files leave rows unchanged. Opening-title checks, text/HTML/Markdown support and PDF body/reference detection retain their previous logic. A body-only match remains a hold with a manual-identity note, not an automatic pass.
- Thresholds, scientific routing, source categories, extraction state and historical notes are unchanged. This work performs no acquisition, evidence extraction, library upload or live metadata verification.

## Deliberate hardening

Blank/duplicate source IDs, unsafe filename characters and duplicate/missing identity columns now fail before checks or writes, avoiding last-row shadowing and cache-path traversal. Historical `#ref...` citation-chasing IDs remain valid: a full maintained-data comparison caught and corrected an initially over-strict filename check. Nothing rewrites those IDs.

Queue and report destinations cannot alias each other or the selected SRC/corpus, including case-only aliases. Redirected write paths and shared hard links fail preflight. Preview runs complete serialization and validation. Pre-installation failures leave originals untouched; caught installation failures trigger rollback, with incomplete recovery reported explicitly. These are write-boundary and malformed-input changes, not identity-method changes.

## Verification

The [parity receipt](m07-metadata-verification-parity.json) compares separate old/new processes using all **918 maintained queue rows and 741 SRC rows**, plus **15 synthetic queue/document cases**. Five steps cover title verification, title rerun, DOI verification, DOI rerun and the offline check. Selected-data inventories, queue/report bytes, stdout summaries and return codes match without normalization. Only queue/report change; source register and cached artifacts remain unchanged. During comparison, the candidate compiler has no schema or pipeline directories and its legacy path constants point to nonexistent locations.

Synthetic PDFs exercise opening-title matches, wrong documents, body-only chapters, reference-list matches and manual confirmation. Synthetic text snapshots cover the other supported formats. A deterministic Crossref adapter supplies success, mismatch, missing and unreachable responses; real matching/citation logic runs unchanged. No private corpus or real network was used. This is a compatibility rehearsal, not full historical quote verification or a new metadata attestation for maintained sources.

The 44 new tests cover independent layouts/corpora, foreign working directories, direct isolated CLI invocation, legacy calls, DOI outcomes and worker bound, title/skip behavior, citation-chasing IDs, complete previews, malformed identities, aliases and two-file recovery before/after replacement. The existing metadata/title and UTF-8 checks also pass.

Full suite: **1,463 passed**, with five existing Swig deprecation warnings. Lint/format and scoped type checks pass. Broader source-package type output is identical to baseline, retaining 16 existing diagnostics. Schema synchronization reports zero stale files; structure reports zero errors and 4,039 existing warnings; T4 coverage reports zero errors. Independent implementation, test and parity review found no blocking issue. Validation ran against disposable clones, without touching the live review checkout.

## Remaining work

Acquisition is the next separate writer slice: queue status, immutable cached artifacts and shared-library copies need an explicit recovery boundary. Other writers, authored/generated configuration separation, release manifests, read-consistent publication, training material and all-writer cutover rehearsal remain open under M07/M08 and later steps. Existing hardcoded operator-contact configuration is not changed here and must be externalized before product import under the content-boundary review.

Publication requires stable inputs and a single writer. It covers caught failures, not machine/process crashes or concurrent writers; readers may see different file generations during the brief multi-file installation. CIAT remains the working authority; live reviews and runtime pins continue unchanged.
