# Local review decisions, drafts and exports

This M07/M08 change follows PR #625. CIAT continues to hold the working review records. All comparisons used disposable copies.

| Writer | What it reads and saves |
|---|---|
| Dashboard decisions and questions | A decision belongs to one evidence ID and reviewer. A query can append one reply for each matching answered question on that record. Replies and the decision publish together. Missing or unrelated issue IDs retain the original skip behavior. |
| Reset and encoding repair | Scoped reset keeps applied decisions and other reviewers. Explicit `*` clears the whole store. Reset publishes the previous valid contents to `decisions.bak.json` with the changed store. A valid Windows-1252 file can be repaired on read. Unreadable records produce an error and remain available for recovery. |
| Gap reports | Reports append to the selected gap CSV. Earlier bytes survive. The next numeric ID follows the highest existing suffix, including after gaps in numbering. |
| Clarification and submission history | Replay checks the selected decision and event files through staging. Shipping captures their contents before replay. A first clarification-only submission now includes the newly created shared history file. Event identity and the existing submission allowlist apply. Pending copies stay available locally. |
| Batch import and production | Row decisions append idempotently to the row-review log. Both batch builders install images or cards before the index and restore previous files after a caught installation failure. Direction labels and scoring inputs come from the selected snapshot. The seven historical input cards also render from the selected snapshot. |
| Browser storage | **How to review** links to a private backup of browser drafts, indexed batch reviews, reviewer settings, dashboard feedback including its clear-all backup, and the two historical T4 draft tools. The restore checks every supplied key before writing, keeps identical entries and stops on conflicting values. A failed review-state read or unconfirmed server reset preserves browser drafts. |

## Running an isolated review

The server accepts a positional port and `--root`. The default serves its installed checkout. With a different root, it serves the selected dashboard, schema, review records and corpus. GitHub submission continues to run from the installed Git checkout. A server pointed at a separate data copy reports that boundary when submission is requested.

Both batch builders accept `--root`, `--out-dir` and `--dry-run`. The evidence batch also accepts `--corpus-dir`. The row CSV importer accepts `--root` or a specific `--log`. The historical decision-card renderer accepts `--root` and `--output-dir`. Source bytes, inclusion rules, approval status and decisions are preserved through these operations.

Browser backups are specific to the browser profile, scheme, host and port. Capture the original origin before switching. Close other review tabs while restoring. Use a private copy of the selected checkout's `pipeline/review/` files for server-side state. [Reviewer instructions](../../../docs/REVIEWER_GUIDE.md#move-review-drafts-between-browser-profiles-or-addresses)

## Recovery and limits

One server serializes local review edits. The linked decision/reply installer and the submission reader also share a short OS-backed SQLite reservation under the local account's cache. This closes the window in which a separate submission process could capture only half a save. The reservation ends before network operations. Review can continue during a push.

The staging publisher restores earlier files after caught failures. An incomplete rollback reports a recovery directory for inspection. Use stable inputs and one writer per storage set during migration. Power loss between replacements and concurrent legacy writers still require reconciliation. Browser backup files can contain reviewer notes and screenshots and belong in private storage. [Record recovery procedure](m08-review-recovery.md#recovery-procedure)

## Verification

- Nineteen old/new handler actions matched on HTTP status, response content and the bytes of every selected record after each action. The comparison included Windows-1252 recovery, repeated decisions, questions, gap reports, challenges and both reset modes. [Review parity receipt](m08-review-local-parity.json)
- Both batch builders and the row importer produced byte-identical outputs for 51 evidence cards, 45 row cards, a synthetic PDF crop and a history starting with 37 prior decisions. The comparison used the maintained 6,376-row evidence and 743-row source registers at `f5f387f6`. [Batch parity receipt](m08-review-batches-parity.json)
- Regression tests cover malformed requests and stores, failure after either linked replacement, historical fields, concurrent gap reports, failed browser reads and resets, fresh or repeated imports, quota failures and conflicting browser drafts. A separate process waits for a complete linked save and another review proceeds during a simulated push.
- An isolated HTTP server served the selected checkout and retained six concurrent reviewer decisions. The desktop app displayed the backup page on a disposable origin. After integration of PR #626, both card renderers produced identical seven-card HTML with SHA-256 `af21db123e1e386ff4b798dc38b4d2e8f73ec56f54fa3b0aa31b4351f1767821`. Schema synchronization, structure validation and T4 coverage passed in a clone without private source files. Quote verification requires the private corpus.

Next, inventory and relocate historical intake, specialist correction and quarantine writes. The later cutover rehearsal covers all writers, browser profiles and private server files before review authority moves.
