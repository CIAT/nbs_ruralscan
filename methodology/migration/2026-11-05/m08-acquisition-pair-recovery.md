# M08: acquired artifact and provenance recovery

Date: 6 November 2026. Baseline: `0223429763d6f23597479b00f96bc6f891f6d749` (merged PR #616). Status: merged in PR #619 at `f31f0d1de8932958517866d16683475bf89674cc`. This internal receipt stays in CIAT, outside destination product repositories.

## Result and boundary

A downloaded artifact and its `.meta.json` provenance are prepared and validated together before either is installed. `ingest.artifact_publication.PairSnapshot` captures the selected destinations before a fetch; `publish_pair` refuses observed drift and uses the existing staged publisher for caught-error recovery. The low-level `acquire()` adapter and the PDF queue wrapper's final promotion both use this boundary.

New cache pairs stay absent after successfully rolled-back failures; explicit overwrites restore the previous pair. Existing bytes, modes and modification times are preserved on successful rollback. If rollback or cleanup is incomplete, `PublicationRecoveryError` retains recovery information and stops the queue wrapper rather than becoming an ordinary failed URL. Owned temporary acquisition files are retained when that error is raised, and their directory is attached to the exception. Other temporary-workspace cleanup errors are also surfaced explicitly.

This slice covers one artifact/provenance pair. It does **not** make the acquisition queue, cache and shared library one transaction. The queue wrapper still publishes library copies before saving its queue; those operations, path selection and their recovery boundary are the next slice. No live acquisition, library synchronization or evidence cutover was performed here.

## Compatibility and checks

`acquire(source_id, url, kind=..., corpus_dir=..., commit_sha=..., overwrite=...)`, its CLI, result fields and package exports remain available. A relative corpus path remains relative to the caller, and returned paths retain that form. Low-level acquisition already accepted an explicit corpus directory; this change adds pair recovery rather than claiming to relocate the queue orchestrator.

Supported kinds remain PDF, website and Markdown. HTTP status/content-type handling, user-agent fallback, body checks, default cache reuse, explicit overwrite, source-ID validation and commit-pin behavior remain intact. Existing cached pairs must still match source ID, requested URL, kind, body SHA1, byte count and pin. An orphan sidecar remains a low-level hold even with overwrite; final queue promotion now applies that hold too, instead of overwriting existing provenance when its expected PDF is absent.

The pair validator binds the actual staged bytes to the staged sidecar's source ID, URL, kind, hash, size and commit pin, and enforces matching filenames. It retains the original sidecar serialization and artifact bytes. Low-level PDF validation remains signature-only; the queue wrapper still parses the PDF and checks its citation title before promotion. Raw website/Markdown bytes are not silently re-encoded or normalized.

A cached queue candidate is checked against its original snapshot after reuse, so a file replaced after title checking cannot be accepted under a newer inner snapshot. Symlink redirection, shared hard links, aliased pair destinations and observed changes during fetching or publication are refused. These checks detect observed drift; they do not replace a lock or make concurrent writers supported.

## Shared publication extension

The existing publisher still rejects unsupported formats by default. Its new `artifact_validators` argument names specific destinations already in the publication allowlist, each with a read-only validation function that must raise on rejection. It does not expand that allowlist. CSV/JSON parsing remains mandatory even when a custom validator is provided. The acquisition pair supplies a validator that reads both staged files and checks their relationship before installation.

This explicit extension allows PDF/HTML/raw Markdown acquisition without silently allowing arbitrary generated formats in the compiler. Existing publication callers keep their prior validation behavior. Parent directories for final cache outputs are created only when installation needs them. The queue wrapper's workspace is an owned system temporary directory; its OS alias is resolved without relaxing checks on caller-supplied output paths.

## Verification

The [parity receipt](m08-acquisition-pair-parity.json) compares separate baseline/candidate processes across **21 synthetic acquisition scenarios**: PDF/HTML/Markdown creation and cache reuse, explicit overwrite, URL/pin mismatch, kind collision, HTTP/content-type/signature/empty-body failures, user-agent fallback, queue PDF/title validation and reuse, invalid IDs, orphan provenance and network errors. HTTP responses are mocked and the fetch clock fixed. Artifact/sidecar bytes, selected-file inventories, request sequences and recorded outcomes match; returned paths are expressed relative to each selected data root.

Copies of all **918 maintained queue rows and 741 SRC rows** are included as read-only guards and remain byte-identical. Those rows are not reacquired or reverified. The candidate compiler has no schema or pipeline directories during comparison. No private corpus, real network or library is used, and no historical source-identity or full-corpus attestation is implied.

The **50 new tests** exercise fresh/overwrite publication failure before and after either replacement, staging/validation failures, during-fetch drift, retained recovery, raw artifact bytes, cache reuse, title checks, isolated CLI behavior and explicit format validators. Three review-driven regressions cover cached replacement after the real title check, an inner recovery failure combined with a cleanup path that would fail, and visible normal-workspace cleanup failure. All 120 baseline acquisition/ingestion/publication gate tests pass. Full suite: **1,513 passed**, with five existing Swig deprecation warnings.

Before submission, main advanced through `8d10b709` (PR #617) and was incorporated without conflicts. On the combined tree, **204 targeted tests** pass, including the new acquisition cases and upstream rainfall guards. Lint/format and scoped type checks pass; broader source-package diagnostics are identical to the current-main baseline (16 existing issues). Schema synchronization reports zero stale files; structure reports zero errors and 4,039 existing warnings; T4 coverage reports zero errors. The full-suite result above precedes that upstream integration; PR CI validates the submitted head.

Independent review identified two edge cases in the initial implementation: cached reuse needed the outer snapshot recheck, and temporary cleanup could mask an incomplete recovery error. Both are fixed and regression-tested. A Mac system-temp alias exposed by tests was also resolved for owned temporary paths only.

## Remaining work and limits

Next: relocate PDF queue orchestration with explicit queue/corpus/library paths, preserve stored library-path semantics, and define recovery across owned cache/library objects and queue status. Hydration, other acquisition adapters and manual-download intake remain separate corpus writers. Operator-specific paths/contact strings still need configuration before product import.

Publication assumes stable inputs and one writer. It handles caught errors, not process/machine crashes, simultaneous-reader consistency or remote SharePoint/OneDrive transactions. CIAT remains the working authority; review records, running services, destination repositories and runtime pins are unchanged.
