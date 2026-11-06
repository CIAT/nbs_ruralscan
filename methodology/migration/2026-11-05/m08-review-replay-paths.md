# M07/M08: explicit review replay paths

Date: 5 November 2026. Baseline: `904db18a4d9287141357e248ff48e28beabe9a7a` (merged PR #593). Status: merged in PR #596 at `f90cd5c`. This is another bounded portability step, not an evidence cutover or completion of M07/M08. Project administration stays in this existing workspace; this receipt is not imported into the new product repositories.

## Result

Review decisions can now be replayed on an independent snapshot without reading or writing the installed compiler checkout's evidence register or audit log. The new `replay(root)` API publishes pending clarification events and applies consensus decisions, but does not generate artifacts, run Git or contact GitHub. Its result reports applied counts, skipped conflicts, clarification count and whether the existing rebuild wrapper must run.

`ReviewFiles(evidence, log)` supplies explicit file locations to `apply_decisions` and `reopen_units`; `ReviewFiles.from_root(root)` provides the existing directory layout. Calls without this optional context retain their previous defaults. Decision reduction, reviewer identity, reason/note handling, soft deletion, reclassification and replay deduplication are unchanged.

The existing no-argument command remains a compatibility wrapper: replay first, then run the full generator when agreed decisions or new clarification events require it. A selected local root uses the same order:

```bash
PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.submit_review \
  --root /path/to/independent-snapshot
```

This command **writes** the selected snapshot and runs the existing validation, soft-quarantine and generation behavior. It is not a dry run. Use a stable independent copy with its own evidence, audit and pending-state files. Corpus validation retains its existing behavior; absence of a private corpus does not establish quote verification.

For a replay-only integration:

```python
from pathlib import Path
from nbs_ruralscan.schema_tools.submit_review import replay

result = replay(Path("/path/to/independent-snapshot"))
# No derived artifacts have been rebuilt. Inspect result, then invoke the
# maintained validation/generation boundary before using generated outputs.
```

Replay preflights its evidence, audit and clarification destinations, including the clarification temporary file. Symlink redirection, shared hard-linked files, aliased destinations and invalid parent paths are refused before writes. Malformed decision-store JSON and a missing required evidence register also fail before publishing clarification events. These checks do not provide a lock; use one writer throughout replay and rebuild.

## Writer inventory and preserved boundaries

| Route | Behavior in this step | Remaining work |
|---|---|---|
| `submit_review.replay(root)` | Explicit snapshot; writes EV, review log and clarification history only; keeps pending stores intact | Transaction/recovery across these records |
| `submit_review.main()` and local CLI | Replay followed by existing full generator; optional local root | Combined record/artifact recovery and broader layout separation |
| `submit_review.ship()` | Unchanged: snapshot pending stores, fetch main, create isolated checkout, execute that checkout's compiler, submit only fixed allowlist | Later authority/cutover controls |
| Dashboard `/api/apply` and `/api/submit` | Existing endpoints, defaults and order unchanged | Future shared replay wiring requires separate continuity tests |
| Dashboard review refresh/reopen and `apply-review-export.py` | Existing behavior retained; low-level reopen now accepts an explicit file context | Remaining caller paths and writer transaction |
| Worklist export/apply and metrics default readers | Existing installed-checkout defaults retained | Explicit contexts for remaining entrypoints |

`--root` is rejected with `--ship`: a local rehearsal option cannot redirect submission. Shipping still replays onto freshly fetched `origin/main` using that checkout's code, rather than merging a stale local evidence tree. No shipping allowlist, review endpoint, runtime pin or canonical writer changes here.

## Acceptance evidence

The previous and new compatibility wrappers ran on independent copies of the baseline with a fixed clock, the same decision store and a pending clarification event. The fixture covers keep, drop, query and reviewer disagreement against copied existing evidence records. Full generation followed replay in both copies. All **1,266 files** under schema, pipeline and docs matched byte for byte, including six changed outputs and two pending-store fixtures. No normalization was applied. The [parity receipt](m08-review-replay-parity.json) records the changed-file hashes. These are disposable rehearsal decisions; no working evidence records were edited.

Focused tests exercise two interleaved roots from an unrelated working directory, untouched compiler/live defaults, retained pending stores, conflicts, reclassification, repeat replay, reopen/reapply event history, clarification-only rebuilding, redirected destinations and missing/malformed inputs. Shipping integration uses real local Git with simulated GitHub and the real replay function: a newer-main-only evidence row survives while the stale, dirty local checkout remains unchanged. Independent review found no actionable issues.

All **1,169 tests passed** in a clean Git checkout. Lint/format, scoped type checks, schema synchronization (zero stale artifacts), structure validation and T4 coverage passed. Structure retains 4,007 existing warnings. Broad type checking retains the same 191 diagnostics on baseline and candidate; none were added. An initial archive-only test copy lacked the Git metadata required by existing tests; the successful run used a proper checkout. Clean verification copies omit the private corpus; none of these results claims source/quote verification.

## Limits and next step

The following describes this slice as merged. The subsequent [review-record recovery slice](m08-review-recovery.md) stages its three record writes and adds caught-failure rollback; generation remains separate.

Review replay is **not transactional**. Clarification publication, evidence rewriting, audit append and generation remain separate mutations. A later failure can leave some already-applied records; staged artifact publication in PR #591 does not roll them back. Shipping retains its failed isolated checkout for recovery, and migration rehearsals must keep their input snapshot. Do not run this against the live review checkout while other writes are active.

Next: make record replay failure/recovery explicit across EV, review log and clarification history, then test the interaction with artifact publication. Reader-consistent release publication, remaining intake/synthesis/export contexts, authored/generated table separation, release contracts and the all-writer cutover rehearsal remain open. Review continues under the existing authority.
