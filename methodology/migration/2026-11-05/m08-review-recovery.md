# M08: staged review records and recovery

Date: 5 November 2026. Baseline: `f90cd5cb907ce046078bc824bdc4adc58084c501` (merged PR #596), including staged artifact publication from PR #591. Status: implemented; pending merge. This receipt stays in the existing project workspace; it is not destination product content.

## Result and scope

Headless review replay now prepares the evidence register, review log and clarification history privately before installing any of them. A failure while writing the staged evidence or audit log cannot publish an earlier clarification change. Installation reuses the existing file-publication mechanism: validate the allowed file set, preserve prior copies, prepare replacements, detect observed destination changes, then install each file. A caught installation failure restores the files already replaced; incomplete rollback retains recovery copies and raises an error identifying their location.

The exact record allowlist is:

- `schema/registers/EV_evidence_register.csv`
- `pipeline/metrics/review_log.csv`
- `pipeline/metrics/clarification_log.json`

Pending `decisions.json` and `clarifications.json` remain read-only inputs. Their contents are captured before replay and are not copied into the published output set. Consensus, reviewer identity, reason/note handling, soft deletion, reclassification, event ordering and duplicate-replay behavior are unchanged.

Optional publication destinations may remain absent only if absent before staging. An existing record cannot disappear. This avoids inventing an empty review log for unknown evidence IDs or a clarification-only batch. Every allowlisted destination is checked for observed changes, including files that were initially absent. Generator callers still require their complete exact artifact set; their default behavior is unchanged.

This protects `submit_review.replay(root)` and the replay phase of its command/shipping wrappers. Direct dashboard apply/reopen, worklist/export helpers and other low-level writers retain their existing behavior. It does not complete the all-writer boundary or change canonical authority, analytical rules, runtime pins or live endpoints.

## Failure behavior

| Failure | Result |
|---|---|
| Decision/event read or staged record write fails | Selected snapshot remains unchanged. |
| Required record is missing, an unexpected file appears, or a staged file fails structural parsing | No record installation. |
| A selected destination changes during preparation | Refuse publication; preserve the other writer's edit. |
| Installation fails or a caught interrupt follows a replacement | Restore prior bytes, permissions and modification times; remove newly installed records. |
| A restoration fails or another writer changes an installed record | Retain original/staged copies and manifest; report paths needing reconciliation. |
| Replay succeeds but later generation fails | Review records remain applied. Derived artifacts use their separate publication/recovery boundary. Explicitly retry generation after addressing the failure. |

Use stable independent snapshots and one writer per destination. These checks are not a lock shared with the dashboard. Individual file replacements are atomic; readers can still see an intermediate combination during installation. Power loss, forced process termination and persistent filesystem failure are not covered by automatic rollback. There is no claim of a crash-safe transaction or atomic visibility across the three records.

## Recovery procedure

For a caught replay failure with successful rollback, the prior record set remains available. Correct the reported cause and retry on the same stable snapshot; pending decision stores are unchanged.

If the error reports a `ruralscan-publication-*` recovery directory:

1. Stop writers to the affected snapshot. Keep that directory and the pending decision stores.
2. Inspect `manifest.json`. `output_root` identifies the affected snapshot. `previous` records each prior file state (`null` means absent), `before/` holds prior existing files, and `artifacts/` contains the prepared record set with hashes recorded in `artifacts`.
3. Compare each affected destination against both versions. Preserve any newer change from another writer; do not copy an entire old tree over it. Reconcile one coherent record set, retaining original events and evidence IDs. Do not regenerate or submit until that reconciliation is complete.
4. After records are coherent, rebuild and check derived outputs using the maintained generator. Keep the recovery copies until those checks succeed.

A cleanup failure can also retain a directory before its manifest was written or after some temporary copies were removed. If the manifest or backups are missing, preserve what remains and inspect the reported cleanup error. Missing recovery files are not proof of successful rollback; do not restore an incomplete set blindly.

An artifact-generation failure may report a separate recovery directory containing schema JSON and workbook outputs. Identify its scope from the manifest: artifact copies cannot restore review CSV/history, and review-record copies cannot restore a compiled workbook.

For a generation failure after successful replay, use the explicit generator on the selected snapshot:

```bash
PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.generate \
  /path/to/independent-snapshot/schema

PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.generate \
  /path/to/independent-snapshot/schema --check
```

Replaying an already-published clarification-only batch produces zero new events and does not automatically trigger another rebuild. The wrapper now prints this retry instruction while preserving the original exception. The generator's existing validation and soft-quarantine step remains separate from record replay; it can change source evidence before a later artifact failure. Resolve any reported incomplete artifact rollback before retrying.

## Acceptance evidence

Failure-injection tests cover each staged record write, second/third installation failure, interrupts immediately after replacement, existing audit history, removal of newly installed audit records, incomplete rollback, competing record changes, optional-file rules, unknown IDs and clarification-only first publication. Independent review also exercised third-replacement interruptions before those cases were added to the permanent suite; no blocking finding remained.

Two full-generator integration cases cover decisions plus clarification and clarification-only replay. A failure in the last artifact producer preserves every prior generated artifact while retaining successful review records. Explicit generation then succeeds, its stale check passes, and repeated replay adds no duplicate events. Pending stores remain unchanged throughout.

The [parity receipt](m08-review-recovery-parity.json) compares the previous and staged replay wrappers followed by full generation on independent copies of the pinned baseline with a fixed clock. All **1,266 files** under schema, pipeline and docs matched byte for byte, including six changed outputs and two pending-store fixtures; no normalization was applied.

All **1,207 tests passed** in a clean Git checkout. Lint/format, scoped type checks, schema synchronization (zero stale artifacts), structure validation and T4 coverage passed. Broad type checking retains the same 191 diagnostics on baseline and candidate; none were added. Structure retains 4,028 existing warnings. Clean verification copies contain no private corpus, so these checks do not establish quote/source verification.

## Remaining boundary

Record replay and generated artifacts now have separate caught-failure recovery, not a combined transaction. Next, consolidate remaining direct review writers behind the shared boundary with endpoint/export continuity tests. Reader-consistent release publication, durable interruption recovery, remaining intake/synthesis paths, authored/generated configuration separation and release contracts remain open. Evidence cutover still requires its later all-writer rehearsal; review continues under the existing authority.
