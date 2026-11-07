# M07/M08: corpus hydration and remaining acquisition writers

Date: 6 November 2026. Baseline: `788b72c3268bc0f446f70963c759a0da9d55debc` (merged PR #622). Status: implemented; pending merge. This internal receipt stays in CIAT, outside destination product repositories.

## Result

The remaining active corpus acquisition/hydration paths now use explicit inputs and recoverable publication: batch hydration, manual-download intake, GitHub code acquisition, both WOCAT adapters and review-preview hydration. Existing entrypoints/defaults remain available. No live corpus, library, queue, review service or destination repository was changed by this migration work. CIAT remains the working authority.

| Writer | Selected inputs and outputs | Recovery boundary |
|---|---|---|
| `ingest.hydration` / `hydrate-corpus.py` | SRC, optional acquired queue, library and tracked approach archives → corpus | Whole prepared hydration batch; only selected new/changed files published |
| `ingest.download_intake` / `intake-downloads.py` | Queue and local downloads → cache, library, archive, queue | File copies first, queue last; original-download cleanup is a separate post-publication step |
| `ingest.github.acquire_file` | Repository/path at a resolved commit → code text and provenance | One immutable pair; an interrogation still progresses file by file |
| WOCAT technology/approach `acquire` | Selected questionnaire/version → source JSON, Markdown, provenance | One refreshable triplet; multi-source acquisition still progresses source by source |
| Review-server preview helpers | SRC plus GitHub/library → missing code/PDF cache file | One file per request, with process-local hydration serialization |

`ingest.source_publication.SourceSnapshot` provides an explicit same-directory bundle boundary. It captures destinations before content acquisition, binds a named file set to staged bytes and adapter-owned validators, rejects observed changes and uses the existing publisher for rollback/recovery. Existing publication callers and format defaults are unchanged.

## Preserved behavior and deliberate hardening

Hydration's `--nbs` still filters only the queue and matches its entire `nbs_id` cell. SRC remains unfiltered. SRC library hydration skips an existing PDF specifically; generic web/queue routes accept any existing supported snapshot. Approach hydration checks Markdown, prefers the tracked artifact matching the recorded SHA1, then uses its dedicated adapter. Technology transcripts are independently restored even when a PDF is already cached. Partial WOCAT bundles still refresh their sidecars when their transcript is missing.

Batch hydration parses captured register bytes, guards selected library/archive inputs and cache destinations, and prepares privately. Existing snapshot markers avoid copying large cached PDFs just to skip them; original hashes remain guarded. WOCAT adapter work is isolated per source so an ordinary failed/incomplete adapter cannot leak partial files into the outer batch. Generic copies are create-only; only successful WOCAT repairs may refresh existing bundle members. Read-only inputs are checked again after rendering and before installation. Success summaries are returned only after publication/validated dry-run.

Hydration preserves source bytes, including legacy library/code bytes; it does not turn copying into source identity verification. Existing queue/status/DOI/title policy and scientific rendering remain intact. Invalid source IDs, path traversal, aliases, malformed record structures and observed competing changes now fail before publication. GitHub cache identity/pin checks remain immutable. WOCAT validators bind the staged payload, rendered transcript, selected version and provenance hashes; technology acquisition also refuses a questionnaire whose ID differs from the requested ID.

Manual intake retains opening-title checking, body-only identity holds, queue notes/stamps, collision holds, `--keep` and local-only `--dry-run`. Successful prepared copies are published create-only, followed by the queue. A queue failure now removes newly installed cache/library/archive files while retaining original downloads; the previous adversarial test expecting a leftover archive was updated to verify this stronger recovery boundary.

Original downloads are removed only after successful publication. Their captured state and published archive are checked before cleanup. Changed originals/archives or failed deletion produce an explicit **CLEANUP PENDING** result and nonzero exit; published records/copies stay committed. Cleanup can finish for some files before another cleanup fails. This is reported separately, never described as a rollback of the published batch.

Review preview hydration preserves cached extension precedence, raw bytes, network headers/timeout/size cap and ordinary missing-source returns. It now checks SRC/library inputs and publishes exclusively. A separate reentrant lock spans cache check through publication within the server, preventing two normal preview requests from racing on the same miss. It does not lock other processes. Incomplete recovery propagates through the preview routes rather than becoming a missing-file response.

New files use the publisher's file metadata defaults; existing identical or successfully restored files preserve their previous bytes/modes/timestamps. The old/new comparisons below compare file bytes and outcomes, not new-file metadata.

## Explicit paths

Hydration adds `--root`, `--corpus-dir`, `--archive-dir`, `--library-root` and `--dry-run`. Manual intake adds `--root`, `--queue-path`, `--corpus-dir` and `--library-root`. Their library root precedes the relative library path stored in records. Hydration dry-run can still fetch source material; intake dry-run only reads local downloads. Examples and recovery guidance are in [the hydration guide](../../../docs/HYDRATION.md).

GitHub/WOCAT acquisition CLIs expose `--corpus-dir`. WOCAT evidence emission also accepts explicit data/lookup/evidence/corpus paths, including the previously hidden country-income lookup and PDF cost-check input; its analytical logic is unchanged. Evidence-staging JSON output remains a separate writer and is not claimed as a corpus acquisition transaction.

## Verification

- [Hydration parity](m07-hydration-parity.json): 19 synthetic cases across missing-cache and repeat runs; exact corpus bytes, stdout, return code and request sequences match between the merged wrapper and explicit-path CLI. All 743 maintained SRC rows and 922 queue rows remain byte-identical as record inputs. Synthetic cache markers exercise skip routes for maintained sources; their real documents are not imported or reverified. The candidate compiler contains only source/scripts, no schema/pipeline directories, and runs from an unrelated working directory.
- [Manual-intake parity](m07-manual-intake-parity.json): seven synthetic download scenarios, exact output bytes/stdout/return codes, with 922 maintained queue rows preserved as unmatched guards. Separate old/new wrapper processes share unchanged metadata helpers. No source files were downloaded.
- [Adapter parity](m07-adapter-writer-parity.json): 14 sequential synthetic GitHub/WOCAT cases, exact files, outcomes/errors, stdout and mocked request sequences. Covers create/cache/refresh/restore, pin/content/orphan/binary holds and approach hash/identity holds. Both compiler copies lack schema/pipeline directories; clocks are fixed and all network responses mocked.

New tests cover independent layouts and compatibility wrappers, malformed records, aliases, input-read races, observed drift before/after rendering, later-file failure, rollback/recovery, incomplete adapters, cleanup failures and simultaneous review preview requests. Independent reviews identified the late input-drift gaps in hydration/manual intake; final validators and regression tests now cover both. The additional preview race is covered by concurrency and lock-release tests.

There are **170 new test cases** across hydration, adapter publication, manual intake and review previews. Full local suite: **1,787 passed, one skipped**, with five existing Swig warnings. The skip is a case-alias fixture requiring a case-sensitive filesystem. Repository lint/format and changed-module types pass. Configured baseline/candidate diagnostics match exactly: 16 source-package and 191 whole-repository type diagnostics. Schema synchronization reports zero stale files; structure reports zero errors and 4,049 existing warnings; T4 coverage reports zero errors. No private corpus is present in the verification clone, so quote verification is explicitly skipped rather than claimed as full-corpus attestation.

Before submission, main advanced through `b118c6c4` (PR #623), retaining approved T4 binding holds. It was incorporated without conflicts. On the combined tree, **246 targeted tests pass, with one platform skip**; schema synchronization, structure and T4 coverage pass again, and broad type diagnostics remain identical to the updated baseline. The full-suite/parity results above precede that upstream integration; PR CI validates the submitted head.

## Writer inventory and remaining boundaries

The tracked Python/shell audit found no additional active canonical corpus acquisition writer. `submit_review.py` copies/links existing corpus into a disposable submission checkout; `ingest.cache` writes derived DocIndex files; crop scripts write derived images; historical reconciliation reads corpus and writes its own audit outputs. Those are distinct from canonical source acquisition and are not silently recategorized as completed migration work.

This closes the listed acquisition/hydration portability and caught-error boundaries once merged. Other review/local-state writers, historical intake/quarantine, authored/generated separation and reader-consistent releases remain M07/M08 work; contracts, reproducible training fixtures, full-corpus attestation and an all-writer cutover rehearsal remain later gates. Operator-specific legacy defaults still need configuration before product import.

Use stable inputs and one writer per selected storage set. Caught-error recovery is not process/machine-crash durability, a cross-process lock, simultaneous-reader consistency or confirmation of remote SharePoint/OneDrive synchronization. Retain reported recovery directories when cleanup/rollback is incomplete. No live cutover or runtime-pin change occurred.
