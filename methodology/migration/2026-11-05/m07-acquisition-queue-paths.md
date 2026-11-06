# M07/M08: acquisition queue, cache and library coordination

Date: 6 November 2026. Baseline: `f31f0d1de8932958517866d16683475bf89674cc` (merged PR #619). Status: implemented; pending merge. This internal receipt stays in CIAT, outside destination product repositories.

## Result and boundary

PDF queue acquisition now prepares its selected queue rows, cache PDFs/provenance and local library copies privately. It validates the resulting files, installs new cache/library files without replacing existing ones, and publishes the queue last. A caught publication failure rolls back owned changes across those outputs; incomplete recovery stops the batch and retains recovery copies.

This extends the artifact/provenance pair boundary from PR #619 to the PDF queue operation. It does not acquire live sources as part of migration, change review records, copy material into destination repositories or switch working authority. CIAT remains the working authority and review work continues alongside migration.

## Explicit inputs and compatibility

`ingest.acquisition_queue.AcquisitionPaths` names the queue CSV, corpus directory, physical library root and logical library prefix. `run_acquisition()` selects the acquisition date, NbS, library subdirectory, optional all-dates behavior and optional Wayback mapping. `AcquisitionResult` returns row outcomes and changed paths. The compiler does not need its own schema or pipeline directories for this operation.

`scripts/acquire-queue.py` remains the existing command and retains its importable acquisition/candidate helpers and defaults. New options are:

| Option | Meaning |
|---|---|
| `--root` | Selected data root containing `pipeline/acquisition_queue.csv`; defaults its corpus to `.cache/corpus` |
| `--corpus-dir` | Independent cache location |
| `--library-dir` | Full physical library root, before `--library-subdir` |
| `--library-prefix` | Relative prefix stored in each queue row's `target_library_path`; independent of physical storage |
| `--dry-run` | Perform downloads, identity checks and private preparation, but publish no selected files |

For example, a caller can select `/data/records`, `/data/cache` and `/team/library` while retaining `archive/library/<subdir>/<source_id>.pdf` in queue records. The physical mirror subdirectory must already exist. Dry-run still performs network requests; it is not an offline preview.

The original date/status selectors, exact pipe-delimited NbS matching, human/paywall skips, DOI-gated Unpaywall lookup, direct/Wayback/HTML fallback order, PDF/title checks, OCR flags and queue notes remain intact. Successful acquisition still records the selected URL and stored library path. A library collision remains a pending hold with its valid cache retained; the original queue URL remains unchanged on that hold. The cache validator tracks the actual successful fallback URL separately so those two states are not confused.

Header-only queues now return cleanly. Malformed rows, missing/duplicate columns and blank/duplicate source IDs fail before fetching. Untouched historical IDs are not newly subjected to strict acquisition-ID validation; selected invalid IDs retain their original row-level failure behavior. No acquisition, DOI, format or scientific policy is broadened here.

## Publication and recovery

Before private work, the operation snapshots every potentially selected queue/cache/library path and optional Wayback input. The bytes parsed from the queue and Wayback file must match their captured snapshots. It checks again after copying inputs, after preparation and inside the publisher. Observed changes abort rather than being adopted into a later snapshot.

Only new or byte-changed cache/library files become publication outputs. Unchanged held inputs, including malformed provenance, remain byte-identical and do not accidentally become mandatory JSON publication outputs. Every new cache pair is checked for source ID, actual acquired URL, PDF kind, SHA1, byte count, null commit pin, PDF signature and citation title. A new library copy must equal its cached PDF. Collision messages point to the selected physical library, not a private temporary path.

The shared publisher adds `create_only_destinations`, restricted to its existing explicit allowlist. Identical existing bytes are a no-op; different existing bytes are rejected before installation. New files use an exclusive sibling hard link, then remove the temporary name, so a competing file cannot be overwritten between checking and installation. Rollback recognizes the narrow interval in which both owned links exist and removes only its proven temporary link before normal recovery checks. Existing callers retain their previous replacement behavior.

Cache/library publication precedes queue replacement. Caught errors restore owned queue changes and remove newly installed owned artifacts. Competing edits are preserved; uncertain or incomplete recovery raises `PublicationRecoveryError` with retained recovery locations. Existing files keep their original bytes, modes and modification times when unchanged or successfully restored.

This remains a stable-input, single-writer operation. It is not a writer lock, process/machine-crash transaction, simultaneous-reader snapshot or remote SharePoint/OneDrive synchronization guarantee. Exclusive publication requires local filesystem hard-link support; unsupported filesystems fail rather than falling back to an overwrite. Hydration and other acquisition adapters remain separate writers.

## Verification

The [parity receipt](m07-acquisition-queue-parity.json) compares the merged wrapper against the new explicit-path CLI in separate processes, using the same disposable selected paths. Across **22 synthetic cases and three passes** (selected date, all dates and repeat), queue/cache/library bytes, output messages and HTTP request sequences match exactly, without byte or message normalization. Cases cover successful downloads, OCR, title holds, Wayback/Unpaywall/HTML routes, absent routes, HTTP failures, immutable library collisions/reuse, valid cache reuse, malformed/orphan provenance and selection/skip behavior.

Copies of all **922 maintained queue rows and 743 SRC rows** accompany the fixture. Existing queue records retain all field values and the SRC file stays byte-identical. These rows are selector/read-only guards, not reacquired or reverified sources. During comparison the candidate compiler has no schema or pipeline directories and runs from an unrelated working directory. PDFs are synthetic, the fetch clock fixed and HTTP mocked; no private corpus or real library is used.

**73 new tests** cover explicit layouts, CLI behavior, selection, identity/fallback/OCR, dry-run, malformed inputs, aliases, input drift and rollback across cache, library and queue. They include failures before and after exclusive file creation, queue replacement after several installs, read-only existing files, competing files and retained recovery. The Wayback regression changes its file between reading and snapshot capture, then confirms rejection before network activity while preserving that edit.

Full suite: **1,618 passed**, with five existing Swig warnings. Repository lint/format and changed-module type checks pass. Configured baseline/candidate type diagnostics are identical: **16** for the source package and **191** across the whole repository. Schema synchronization reports zero stale files; structure reports zero errors and 4,049 existing warnings; T4 coverage reports zero errors. The disposable validation checkout has no private corpus, so quote verification is explicitly skipped there; this is not full-corpus attestation.

Independent adversarial review found the fallback-URL/library-hold distinction and private collision-path message issue during design, and verified the final create-only recovery and Wayback fix. No remaining blocker was identified.

Before submission, main advanced through `81805625` (PR #620) with runoff-review documentation, review priorities and generated dashboard updates. It was incorporated without conflicts. The full-suite and parity results above precede that integration; schema synchronization is rechecked on the combined tree and PR CI validates the submitted head.

## Next boundary

Continue with corpus hydration and remaining acquisition/manual-intake writers, then the authored/generated layout split and reader-consistent release publication. Operator-specific defaults still need configuration before product import. Contracts, training fixtures, full-corpus attestation and an all-writer cutover rehearsal remain separate migration gates.
