# Phase 0 execution record

5 November 2026. CIAT remains the working authority. Pete approved the exact draft import after PR #584 merged. The 15 pinned foundation files and four introductions are now staged in the public method/evidence repositories. No accepted analytical release or writer cutover has occurred.

[Import receipt](first-import-receipt.json): [RuralScan/method](https://github.com/RuralScan/method/tree/4607d5637d8578ad7a44b44435caf66334902fe8) has 18 files; [RuralScan/evidence](https://github.com/RuralScan/evidence/tree/3c85fe4bee0a060d96aafe0618b54dbc9804f456) has its one-file scope scaffold. Fresh remote clones match all 19 approved hashes, with no extra paths. All 15 existing sources were unchanged at refreshed CIAT main `a36a0f7`. M06 repository scaffolding is complete; maintainer/access and contribution/release governance remain open.

Dashboard feedback is implemented in merged [PR #578](https://github.com/CIAT/nbs_ruralscan/pull/578). The follow-on priority queue is tested in [PR #582](https://github.com/CIAT/nbs_ruralscan/pull/582), now merged with passing CI. The existing local address `http://127.0.0.1:8876/dashboard.html` now serves its v1.5.0 read-only preview. The review service on port 8766 was left running; no decisions were applied or cleared.

## What is complete

| Work item | Result | Remaining gate |
|---|---|---|
| M00 — baseline | Pinned CIAT tree, all 3,077 files, four repository service inventories, 33 open issues and four open PRs | Refresh before each actual import; this is not a frozen main |
| M01 — local continuity | Eight local worktrees inspected; private review/staging/feedback backup restored and hash-checked; 57 writer routes inventoried | Rehearse semantic replay and final drain in M23; check other browser origins and any newly active work before cutover |
| M02 — ownership proposal | All 74 schema CSVs, 59 T4 rows, 256 code/config/test files and 406 functions/classes mapped; exact 15-file first import proposed | Initial draft import accepted; broader ownership and mixed/unresolved material remain held |
| M04/M05 — organization/runtime | RuralScan exists; runtime source and fork still match all 52 blobs and refs | Runtime working location, maintainers, protections and reuse terms remain separate decisions |

Pete confirmed during this audit that he is the only current evidence writer, working on this Mac. No colleague inventory is required for today's scope. Record another writer before they resume. One local scheduled agent can repair PR #582 after #579 merges; its output branch is included in the writer inventory. It must be accounted for during the final drain.

## Approved first import (proposal preserved)

The [first import manifest](first-import-manifest.csv) identifies **15 existing files**, each by source commit, SHA-256 and destination path:

- CIAT MIT notice, field specification and frozen column manifest.
- Four shared configuration tables: T1, T2, T5 and T7.
- Family, variable and dataset-binding configuration: FAM, VONT and BIND.
- Five existing recipe identity tables (T0).

Proposed destination is `RuralScan/method`, explicitly labelled a **draft, pinned baseline**. Add the prepared [method introduction](drafts/method/README.md) and [start-here guide](drafts/method/handbook/start-here.md). Prepare `RuralScan/evidence` with its [scope and operating boundary](drafts/evidence/README.md), without copying active records or moving the review service.

Four newly authored documents are listed separately in the [scaffold manifest](scaffold-manifest.csv), including a portable [source map and unresolved-reference index](drafts/method/data-model/baseline.md). The proposal therefore contains 15 existing files plus four new documents. The start-here guide supplies the initial concepts; the larger cookbook rewrite remains M11–M13.

The original proposal manifests and four introductions are preserved byte-for-byte, including their historical `approved_for_import=false` fields and proposed-status wording. The dated [import receipt](first-import-receipt.json) records Pete’s subsequent approval and completed import; it supersedes those proposal-time flags for this exact tranche only. The staging copy remains read-only with CIAT authoritative; ownership approval is not scientific approval. Copying dataset metadata does not copy or grant access to the datasets. No PDFs, source extracts, screenshot crops, generated analytical tables, runtime stubs or pending reviews enter this first tranche.

The initial snapshot deliberately does **not** claim closed foreign-key validation or executability: FAM contains two mangrove family rows without a mangrove T0 file, VONT includes pending/rejected/blank statuses, and some fields reference evidence and policies outside the snapshot. Preserve those conditions and pinned source links; resolve them through reviewed method changes before a definition release. The exact bytes in the manifest describe the proposed source snapshot. Later editorial link repairs need a separate recorded diff.

## Findings that change the sequence

1. **Separate authored T4 inputs before moving the compiler.** All six mapping CSVs are held. Even rows marked as compiled retain authored weights or scenario fields. The [row triage](t4-row-ownership-triage.csv) identifies 7 gate markers, 9 legacy/design markers and 43 compiled markers; these markers are not approval of ownership or analytical meaning.
2. **Split the generator before treating it as a utility.** Write-mode generation can quarantine EV records. The merge driver invokes that path. M07/M08 must preserve canonical input hashes during portability tests and separate validation, serialization, mutation and publication.
3. **Resolve two effect-selection implementations explicitly.** One recomputes transfer from weighted contributor contexts; another uses a source-count approximation. Moving both into different repositories would preserve conflicting semantics. Add shared fixtures and ratify the contract before adoption.
4. **Keep runtime's current analytical pin.** Seven pinned files match their declared hashes and CIAT's historical v0.1.5 bundle. v0.1.7 changes weight metadata in ten rows and host-combination wording. M17 remains a separate compatibility/scientific review.
5. **Keep historical and current work distinguishable.** Older app notebooks, generated handoff copies and audit reports remain linked by immutable source revision. Their presence does not make them current definitions or completed Haiti runs.

## Evidence and audit navigation

| Question | Record |
|---|---|
| What exactly was inspected? | [Baseline](baseline.json), [source tree inventory](source-inventory.csv), [service settings](services.json), [open issues](open-issues.json) |
| Which table goes where? | [Table schedule](table-ownership.csv), [table/document findings](tables-and-documents.md), [document schedule](document-ownership.csv) |
| Which code moves or splits? | [Code findings](code-and-runtime.md), [file schedule](code-inventory.csv), [function schedule](function-split-schedule.csv), [import edges](local-import-edges.csv) |
| How are code changes sequenced? | [Split sequence](split-sequence.csv), [dependency ownership](dependency-ownership.csv) |
| What can write evidence today? | [Writer inventory](writer-inventory.csv), [continuity and restore notes](continuity.md) |
| Is Diego's baseline preserved? | [Remote refs](remote-refs.json), [CI observations](remote-ci.json), [pin checks](runtime-pin-checks.csv), [handoff integrity](handoff-packages.csv), [upgrade differences](pin-upgrade-diff.json) |

Machine verification reads the pinned Git revision and performs no import:

```sh
python3 methodology/migration/2026-11-05/phase-0/verify_inventory.py
```

It checks complete source-tree identity, all table paths/hashes/headers/row counts, and the original proposal's hashes, destination uniqueness and historical unapproved flags. The separate import receipt records the approved destinations and verified remote commits. It does not certify scientific validity, reuse rights, dynamic dependency closure or cutover readiness. Private state and its recovery manifest remain outside Git.

## Next order

1. Completed: approve and stage the exact 15-file draft import and four introductions; preserve mixed/scientific holds.
2. Complete M06 maintainer/access and contribution/release governance. The public scaffolds preserve CIAT authority and are not accepted analytical releases.
3. Refactor explicit build paths and separate write boundaries inside CIAT (M07/M08), with unchanged-input parity. Review continues there.
4. Define contracts, lawful training fixture and one complete recipe/SOP example (M09–M13).
5. Continue the execution board through publication, runtime/Haiti and rehearsed evidence cutover. Do not skip from scaffolding to moving live registers.
