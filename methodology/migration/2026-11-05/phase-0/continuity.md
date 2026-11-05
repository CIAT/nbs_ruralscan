# Evidence continuity and recovery

Observed 5 November 2026 against CIAT `dd80226700432e9abd4aa9262262b9ad5ad6dfd5`. Pete confirmed he is the sole current evidence writer, on this Mac. This is a dated scope confirmation, not a permanent assumption. Add other operators before they resume work.

## Preserved state

The private backup `20261105T073850Z` contains 5,439 regular files (456,738,808 bytes), plus one staged PDF symlink's target and original link metadata. Each payload was copied to an isolated restore directory and SHA-256 checked. It covers review stores, staging, inbox, verification outputs, cached intake and known November 4/5 feedback exports. Checkout HEADs and working/index patches are also retained. Private paths, review content and source text are not committed here.

This proves byte recovery, not semantic replay or a running-service restore. Files were captured while work continued; the backup is not an atomic cutover watermark. Corpus caches and every browser profile were not copied. No live state was restored, applied, cleared or pruned. The original files remain in place.

Two inspected checkouts contain decision stores: 239 and 190 reviewer-decision records. All have local applied flags; **that does not prove submission to current main**. Thirteen local clarification events in the October 19 checkout already occur in that checkout's shared log. Reconcile against current canonical events before any replay. No submit lock was found in the eight inspected worktrees.

## Current execution surfaces

| Surface | Observation | Cutover treatment |
|---|---|---|
| Review service | Listening on `127.0.0.1:8766`, October 19 checkout at `ee91527`; process exists, no claim that a write was in flight | Preserve stores; identify loaded version and drain Apply/submit before switching |
| Local dashboard | `8876` now serves PR #582's v1.5.0 static preview; `8877` is another preview of that build | Feedback belongs to each origin; neither preview supplies a review API |
| Other local previews | Ports 8000/8001 observed; port 8765 is an unrelated project | Inventory relevant browser notes before changing origins; leave unrelated service alone |
| Git worktrees | Eight recorded in [local-workstreams.csv](local-workstreams.csv) | Refresh dirty state, in-flight jobs and open PRs immediately before final drain |
| Local scheduled agent | ACTIVE `fix-pr-582-after-pr-579-merges`; waits for #579 then repairs/pushes #582; expected to pause after success | Recheck status and output branch during cutover; do not assume absence because no process is running |
| Other schedules | No matching project definition in 37 inspected local launch plists; no active current-user crontab lines; 10 Codex automation files inspected | Bounded observation only; recheck if configuration changes |
| GitHub | Protected CIAT main requires `checks` and one approval; admin enforcement is off. Two tracked workflows plus Pages deployment observed | Include ordinary PRs, auto-merge and administrative/direct paths in retirement controls |

Current in-app browser at origin 8876 showed zero dashboard notes. Other browser origins/profiles remain a pre-cutover export check. The sole-writer confirmation removes the need for absent colleagues to provide machine inventories; it does not make uninspected browser storage empty.

## Writer controls required

The [57-route writer inventory](writer-inventory.csv) distinguishes observed processes, inspected code capabilities, configured automation and unknown execution state. Source references refer to the pinned baseline, not necessarily the code loaded by the older review process.

- Review uses in-process locks and per-checkout submission locking. There is no universal transaction across EV, SRC, logs, generation and all independent writers. Preserve paired inputs/events after a failed operation.
- Write-mode generation can quarantine EV. The Git merge driver calls this path and suppresses generation errors. A migration rebuild must verify canonical inputs did not change; valid output hashes alone are insufficient.
- Gap reports append separately to `gaps.csv`, outside normal review submission. Their count-based IDs and publication route require separate reconciliation.
- Clarification history is included in submit's file list but excluded from automatic review-PR approval. Keep ordinary approval for those PRs unless governance is explicitly changed.
- Fixed `decisions.bak.json` and the existing freeze exporter are not complete rollback backups. Preserve immutable dated snapshots and later deltas.

## Restore and switch sequence

1. Continue normal review in CIAT. Treat this backup as recovery material, not a request to replay old decisions. Keep the code/table ownership proposals separate from scientific decisions.
2. In M23, rehearse agreement, conflict, query/reply, reopen, reclassification, partial Apply, failed submission, duplicate replay, staged intake, gap publication and quarantine on isolated copies with outbound submission disabled. Verify event identity, approval meaning and later changes, not only totals.
3. Before M24, refresh the writer inventory and browser exports, drain or explicitly hold every job and PR, and take final source/event/run watermarks. Pause every canonical writer, including the configured agent and manual Git routes. New local staging needs an explicit later-intake plan.
4. Reconcile pending decisions against current EV/review history; deduplicate clarification events by recorded digest; reconcile gaps, intake and publication separately. Rebuild with pinned policy/compiler inputs and full-corpus parity before filtering. Never overwrite current registers with an old checkout's whole files.
5. Test refusal of writes through the retired API, CLI, jobs, merge automation and direct/admin routes. Only then switch authority and resume writers at one destination.
6. For rollback, pause again and reconcile the reverse delta of every register, queue, event, recipe/prose output and publication change. Preserve new reviews; an old EV snapshot must not erase them.

M01's local audit and byte-recovery work are complete for the observed stores. Browser-origin checks, semantic replay, corpus attestation and the final atomic pause remain explicit gates in M23/M24. None has been claimed complete by this packet.
