# M07/M08: explicit source promotion and recoverable SRC publication

Date: 6 November 2026. Baseline: `cf864cff2e2d7a5981f8812795275fc305a8dbe6` (merged PR #611). Status: implemented; pending merge. This migration receipt stays in the existing project workspace, outside destination product repositories.

## Result

Source promotion now lives in `schema_tools.source_promotion`. `SourcePromotionPaths` declares the acquisition queue, source register and cached-PDF directory independently of the installed compiler. The queue and corpus are read-only; only SRC is published. CLI source-list files and assessed metadata are protected read-only inputs as well.

Promotion prepares a complete source-register copy before installation. It validates all requested new sources, serializes all new rows and validates the resulting CSV before replacing SRC. Existing register bytes are preserved as a prefix; they are not reserialized. Caught installation failures restore the previous file, and incomplete recovery retains the publication helper's recovery material.

The existing `scripts/promote-queue-to-src.py` command remains available, including importable `build_row()` and no-argument `main()`. New `--root` and `--corpus-dir` options select external records and artifacts. `--dry-run` now exercises complete CSV serialization and publication validation without saving anything.

## Commands and API

Rehearse a prepared promotion request against a disposable data copy:

```bash
PYTHONPATH=/path/to/compiler/src uv run python \
  /path/to/compiler/scripts/promote-queue-to-src.py \
  --root /path/to/disposable-data-copy --corpus-dir /path/to/cached-pdfs \
  --nbs agroforestry --sources /path/to/source-ids.json \
  --meta /path/to/assessed-metadata.json --run-id actual-run --dry-run
```

Remove `--dry-run` only when intending to update the selected SRC. `--root` selects the queue and SRC; its default corpus is `.cache/corpus`, unless `--corpus-dir` overrides it. Relative source-list, metadata and explicit corpus filenames remain relative to the caller's working directory.

Direct callers use `promote(source_ids, metadata, paths=..., nbs=..., retrieved_at=..., dry_run=...)`, with optional `protected_inputs` for file-backed requests. It returns a `PromotionResult`; gate rejection raises `PromotionGateError` with the collected problems. The API does not print success messages. The CLI prints success only after publication or successful preview.

## Preserved behavior

The source-row builder keeps the existing gates: filename-safe ID; exact requested-practice membership in queue scopes; DOI/title verification stamp; nonempty team-library path; PDF signature and opening-title match; assessed credibility fields; known or assessed method type. Library-path presence alone does not establish that a remote upload exists. Promotion makes no network requests and does not run metadata verification.

All queue-declared practice scopes, artifact hash, citation, access state, source category and assessed context are retained. Newly promoted sources remain `extraction_status=pending`, with blank extracted variables/date/run/extractor. The required legacy `--run-id` and optional `--extractor` arguments remain compatible but do not start stamping extraction.

Existing sources retain their scope-check/skip ordering: requested practice must belong to the queue entry, and SRC must already include every queue-declared scope. When those conditions hold, the source is skipped without rechecking acquisition status, cached PDFs or per-source assessment. Existing extraction/review-related source metadata remains unchanged. A missing corpus is therefore allowed for an all-existing no-op request; new sources still require their selected PDFs.

## Deliberate hardening

- Blank or duplicate IDs in either queue or SRC now fail before publication instead of silently selecting the last dictionary entry. Duplicate columns or a missing `source_id` header also fail; no identities are merged automatically.
- Missing final newline in SRC receives one separator before new rows, preserving existing bytes and preventing row concatenation.
- Plain source-ID lists now explicitly use UTF-8, matching the existing JSON/CSV readers and the package portability check.
- Preview validates the complete CSV rather than stopping before serialization. An incompatible SRC header cannot produce a successful preview followed by a partial append.
- SRC cannot alias queue, source-list/metadata inputs or a path inside the selected corpus. Case-only aliases, symlink redirection and shared hard links are refused.

These changes affect malformed/incomplete inputs and failure handling; valid identical inputs retain their source-row semantics. No source or evidence rows are deleted, promoted or corrected in live registers by this migration rehearsal.

## Verification

The [parity receipt](m07-source-promotion-parity.json) compares separate baseline/candidate processes using all 918 maintained queue rows and 741 SRC rows plus synthetic fixtures. Seven scenarios cover preview; two new verified sources; identical rerun; rerun for another declared practice; rejected wrong practice; rejected mixed valid/identity-held batch; and previously promoted, externally marked sources whose PDFs and verification stamps are subsequently unavailable.

Selected-input inventories, SRC bytes and return codes match without output normalization. Existing SRC bytes remain unchanged during each append. The candidate compiler has no schema or pipeline directory during parity and reads a separate data copy. Synthetic PDF bytes are shared between comparisons; no private corpus, network, acquisition or evidence extraction is used. This compares selected inputs/output and return codes, not diagnostic wording or the entire repository.

The 36 new tests cover independent flat/split/canonical layouts and corpora, original gate behavior, pending state and scope/access preservation, existing-source skips without a corpus, whole-batch rejection, duplicate/blank identities, complete previews, missing final newlines, protected aliases, failed private serialization, replacement failure before/after installation and the relocated CLI. The 67 existing gate/pipeline tests pass. Independent implementation review found no blocking issue.

Lint/format, scoped type checks, schema synchronization (zero stale files), structure and T4 coverage passed. The broader source-package type check retains the same 16 baseline diagnostics by type, file and count; structure retains 4,039 existing warnings. Independent test, receipt and documentation review found no blocking issue. Final full-suite rerun: **1,417 passed**, with five existing Swig deprecation warnings. The initial full run exposed the legacy source-list encoding omission; after the explicit UTF-8 fix, both the targeted portability/promotion checks and the complete suite passed.

Before submission, the branch incorporated main through `f9a92023` (PR #610) without conflicts. On the combined tree, all 114 portability, promotion, gate, pipeline and review-priority tests passed; lint/format and schema synchronization passed again. The full-suite result above precedes that upstream integration; PR CI checks the submitted head.

## Remaining work

Metadata verification and acquisition remain separate writer slices. Offline title verification still writes the queue; online verification writes queue plus audit report and must retain its distinction between unavailable services and definitive identity failures. Acquisition also writes cached/shared artifacts and needs its own recovery boundary.

M07/M08 remain open for those paths, other writers, authored/generated configuration separation and release contracts. Publication assumes stable inputs and one writer; it is not crash-safe or a cross-process lock. CIAT remains authoritative, with live review and runtime pins unchanged.
