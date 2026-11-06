# M07/M08: discovery registration and linked search/progress records

Date: 6 November 2026. Baseline: `ef70f10ed2898ba67d5c69e7d5c77cce6cc85f7c` (after merged PR #609). Status: implemented; pending merge. This migration receipt stays in the existing project workspace, outside destination product repositories.

## Result

The active discovery registrar now runs from `schema_tools.discovery_registration`. Its `DiscoveryRegistrationPaths` declares the acquisition queue, SRC, FAM, SRCH, progress ledger and discovery-log directory. SRC/FAM and the supplied candidate/report/protocol files are read-only. The compiler checkout and current working directory no longer choose registration data for an explicit context.

One invocation stages its complete output set before publishing any of it:

- acquisition queue CSV;
- SRCH search-protocol CSV;
- progress-ledger CSV, only when `--ledger` requests stamps;
- one named Markdown report per lane;
- optional named JSON log for canonical-source reuse tasks.

Validation, deduplication, same-run history checks and all existing writer calls operate on private output copies. Success messages are emitted after the full batch succeeds. A failure in a later ledger/report write cannot leave an earlier queue update saved. Caught installation failures restore old files and remove newly created files; incomplete rollback retains recovery material for reconciliation.

The shared publication helper now accepts Markdown only for explicitly named `.md` destinations and verifies UTF-8 decoding. Its new dry-run option renders and validates the same complete allowlist, including CSV/JSON parsing and destination-drift checks, then skips installation. Other callers retain their previous defaults and file-type restrictions.

## Commands and API

Existing script arguments and checkout defaults are preserved. To rehearse an already prepared discovery batch against a disposable data copy:

```bash
PYTHONPATH=/path/to/compiler/src uv run python \
  /path/to/compiler/scripts/register-discovery.py agroforestry \
  --root /path/to/disposable-data-copy --dry-run \
  --date 2026-11-06 --ruleset v1.8.1 --run-prefix actual-search-run \
  --candidates lit=/path/to/candidates.json \
  --reports lit=/path/to/report.md --log-names lit=actual-search-run.md \
  --ledger updated_lit=done
```

Use the actual search date, ruleset, run ID and supported status. Family-targeted searches still require their actual `--protocols` and `--family`; these are not inferred from candidate or evidence presence. Remove `--dry-run` only when intending to update the selected data copy. `--root` chooses both records to read and records to write. Relative input filenames remain relative to the caller's working directory.

Direct callers use `discovery_registration.main(argv, paths=DiscoveryRegistrationPaths(...))`; individual paths support flat or split layouts. `ledger.mark(..., path=...)` now accepts a selected ledger, while omitted paths preserve legacy behavior. The standalone ledger/search commands do not gain the registrar's batch recovery guarantee.

## Preserved behavior and deliberate boundaries

Search counts remain those reported before acquisition-queue deduplication. Unknown retrieved/screened totals stay blank. Explicit zero-yield protocols remain valid. Exact table/process/family scope is retained in both SRCH and ledger stamps; no unsearched pair is marked complete. Search dates remain the supplied historical dates; ledger update dates remain the current UTC dates.

Existing cross-scope sources still require explicit canonical reuse tracking and a reason. Conflicting reports, reuse logs or same-run protocols require a new run/log identity. Original report provenance text and `discovery_log_ref` values retain their logical project-relative form; staging paths never enter them.

A header-only queue is now accepted using its own column header rather than reading the first data row. The queue file must exist and carry unique columns including source ID, citation and DOI. No columns are invented. SRC and FAM must exist. Missing SRCH/ledger retain their existing bootstrap behavior; a missing ledger remains absent when no stamps are requested.

All declared output targets must be distinct, including case-only variants, and cannot alias candidate/report/protocol inputs, SRC/FAM or an unrequested ledger. Redirected targets and shared hard links are rejected. These guards also apply to preview mode.

This remains registration, not source verification or evidence extraction. Newly queued candidates remain pending and unverified. Metadata verification, acquisition, source promotion, evidence intake, ledger reconciliation against evidence, generation and submission remain separate authorized operations.

Publication requires stable inputs and one writer. It is not crash-safe, simultaneously visible across files, or a lock against concurrent review. CIAT remains authoritative; no cutover, runtime pin change or live review-service restart occurred.

## Verification

The [parity receipt](m07-discovery-registration-parity.json) compares separate old/new processes over the complete selected baseline: 916 queue rows, 741 SRC rows, 56 FAM rows, 229 SRCH rows, 184 ledger rows and 147 existing discovery-log files. Six invocations cover two-lane registration, identical rerun, a family-targeted search with deduplicated membership plus an explicit zero-yield protocol, cross-scope reuse, a rejected changed protocol, and a rejected source-ID collision.

Return codes and complete inventories/hashes of declared registration artifacts match byte for byte, without normalization. All prior logs and SRC/FAM remain unchanged. The candidate compiler has neither a schema nor a pipeline directory during parity; inputs live in a separate data copy. The test pins only the ledger UTC clock to 6 November while retaining supplied historical search dates. It uses synthetic discovery candidates and performs no acquisition or extraction. This is not a whole-repository or stdout comparison.

The 34 new integration cases exercise independent layouts, poisoned compiler defaults, interleaved selected contexts, bootstrap, exact counts, reuse, history, full-manifest dry-runs, staged writer failures and post-replacement rollback at each later destination. Seven additional shared-publication cases cover preview validation and narrowly allowed Markdown. Existing discovery/ledger/search/publication tests pass. Independent code, test and parity review found no remaining blocking issue.

All **1,377 tests passed** in a disposable checkout (five existing Swig deprecation warnings). Lint/format, scoped type checks, schema synchronization (zero stale files), structure and T4 coverage passed. The broader source-package type check retains the same 16 baseline diagnostics by type, file and count. Structure retains 4,028 existing warnings. No private corpus was used.

## Remaining work

Acquisition, metadata verification, source promotion, historical intake/quarantine and other remaining writers still need their explicit-path/recovery slices. M07/M08 remain open for those paths, authored/generated configuration separation, contracts and reader-consistent publication. This change does not authorize moving canonical data to a destination repository.
