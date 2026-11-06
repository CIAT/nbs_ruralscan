# M08: direct review writers and dashboard refresh

Date: 6 November 2026. Baseline: `0aca2f3763fafb7cc98ef3637ff9af509e34ba6e` (merged PR #599). Status: implemented; pending merge. This migration receipt stays in the existing project workspace, outside the destination product repositories.

## Result

Direct review actions now prepare their related records privately before publication. They reuse the caught-failure recovery introduced for headless replay, rather than maintaining a second rollback implementation. The existing evidence transformations, event history, reviewer identities, soft deletion, reason codes, response fields and consensus decisions are preserved.

| Entry point | Publication set | Following operation |
|---|---|---|
| `review.apply_decisions` / `review.reopen_units` | Evidence CSV and review log | Caller chooses when to rebuild. |
| Dashboard Apply | Evidence CSV, review log and saved decisions with applied flags | Existing full validation, quarantine and artifact generation. |
| Dashboard Reopen | Evidence CSV, review log and saved decisions with only the requesting reviewer's call removed | Fast review refresh. |
| Dashboard Challenge when disagreement requires reopening | Evidence CSV, review log and the newly saved disagreement | Fast review refresh. |
| Challenge without reopening | Existing single-file saved-decision write | No refresh, as before. |
| Review-page CSV import | Evidence CSV and review log for the entire reviewer batch | Existing explicit rebuild instruction. |
| Worklist export | Complete worklist CSV | No register mutation. |
| Worklist apply | Evidence CSV and review log | Existing explicit rebuild instruction. |
| Fast review refresh | Evidence JSON, dashboard JSON and progress JSON | No full source/PDF validation; Apply still runs that gate. |

A reviewer batch is one publication set. If a later reviewer's application fails, earlier reviewers in that CSV are not left partly applied. PICOS annotations and reviewer order retain their previous meaning. Public record functions also protect callers outside the dashboard. Nested calls stage only private copies; their outer operation decides when the selected snapshot changes.

Both worklist operations and review-page CSV import accept `--root /path/to/independent-snapshot`. Existing invocations retain their defaults. No source content, scientific rules, runtime pins, shipping allowlists or live service configuration changes in this step.

## Failure and recovery

A staged-write failure leaves the selected records unchanged. Caught installation failure restores prior bytes, permissions and modification times, removing newly installed files. A failed rollback or cleanup reports retained recovery copies. That outcome is **indeterminate**, not proof that nothing saved: inspect the reported error and manifest before retrying.

Dashboard Apply now saves its applied flags in the same publication as evidence and audit records. The flag means the review call was saved. It does not assert that artifact generation succeeded. If generation or fast refresh then fails, the endpoint returns `records_saved: true`, `rebuild_required: true` and an error containing the explicit rebuild command. Successful review records remain saved. Apply can be retried without duplicating its audit events; Reopen and Challenge must use the supplied refresh-only command because repeating those actions can add another reopen event.

A failed Challenge publication does not save the new disagreement when rollback succeeds; its input remains in the caller's request. An incomplete rollback must be reconciled before treating the operation as saved or unsaved. No success response is returned for an incomplete publication.

Fast refresh has its own publication boundary. Rendering or installation failure preserves its previous artifact set when rollback succeeds. Records and artifacts are **not one combined transaction**. The existing full generator's validation/quarantine can still change source evidence independently of later artifact publication.

Use the [record recovery procedure](m08-review-recovery.md#recovery-procedure) for retained copies. Inspect every manifest's `output_root` before restoring anything. Nested staging may report a temporary private stage, not the selected working snapshot; never copy intermediate records onto the live snapshot blindly. Recovery directories can be incomplete after cleanup failure. Preserve remaining material and the complete error first.

Individual replacements are atomic, but readers can observe intermediate combinations. This is not crash-safe recovery for power loss or forced termination. The dashboard serializes its own POST handlers; other processes still require one writer per selected snapshot and stable inputs. Publication detects observed competing changes and refuses to overwrite them; it is not a global lock.

## Verification

Failure tests exercise staged audit/store writes, second and third record installations, an interrupt after the decision store replacement, incomplete rollback/error propagation, redirected targets, and isolated live defaults. Continuity cases cover exact Apply responses and conflicts, repeated Apply, empty/conflict-only stores, reviewer-scoped Reopen, Challenge paths that do not reopen, and rebuild failure after a coherent record commit.

CSV tests cover a later-reviewer failure, dry run, PICOS notes, per-reviewer audit entries and repeat import. Worklist tests cover explicit-root export/apply and failed export replacement. Fast-refresh tests cover the final producer failing, replacement failures and interrupts, absent source-register behavior, and byte-identical real-data outputs against the prior implementation with stable repeated output files.

All **1,270 tests passed** in a clean checkout. The final root-path normalization and test type assertion were followed by all 31 direct-writer tests passing again. Lint/format, scoped type checks, schema synchronization (zero stale artifacts), structure and T4 coverage passed. Broad type checking retains the same 194 baseline diagnostics by type, file and count; none were introduced. Structure retains 4,028 existing warnings.

The independent [success-parity receipt](m08-review-writers-parity.json) compares ten sequential dashboard/CSV/worklist steps against the previous implementation in separate processes using 6,369 real copied evidence rows and a fixed clock. Responses and record bytes matched after every step. The record comparison stubs generation; real refresh output parity is covered separately by the tests above. Verification copies contain no private corpus, so these checks do not establish source/quote verification. Independent code and failure-path review found no blocking issues.

## Remaining boundary

This closes the listed direct record-writing and fast-refresh paths. M07/M08 remain open for intake/synthesis entrypoints, authored/generated configuration separation, reader-consistent releases and durable interruption recovery. Evidence cutover still requires the later all-writer rehearsal.

Single-decision and clarification-reply recording, clear/backup actions, row-review exports, evidence-intake writers and source quarantine retain their existing separate boundaries. The pre-existing dashboard/headless difference in forwarding reclassification `claim_scope`/`taxon` is unchanged; reconciling that decision behavior needs its own review, rather than being hidden in a migration refactor. Review continues under the existing working authority.
