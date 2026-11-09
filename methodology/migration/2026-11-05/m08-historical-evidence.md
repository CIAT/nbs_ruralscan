# Historical evidence intake, corrections and quarantine

This CIAT migration step follows PR #628. It lets an operator rehearse historical maintenance against a selected checkout while dashboard review continues. CIAT still holds the working registers.

| Writer | Inputs and saved records |
|---|---|
| Stocktake geography (W25) | Reads the selected peer-reviewed and grey stocktakes. Fills `study_country` only where country, region and AEZ are empty. Matches DOI first, then title. Existing source IDs and geography survive. A changed CSV uses LF; a repeat with no matches preserves the file bytes. |
| Archived effect intake (W32) | Reads the deferred archive, source register, income, T7 and effect-band lookups. Saves evidence, updated source metadata and the dated list of selected IDs together. The reported append count identifies newly inserted evidence. An existing ID with changed scientific content requires an audited correction. |
| Direct intake helpers (W33) | Operate on the supplied registers. Their updates retain the first extraction stamp, resynchronise variables against active evidence and fill missing source context. The active intake workflow still runs its own eligibility and provenance checks. |
| Unit corrections (W34) | Applies an identified correction and appends its review event together. A refused field stops the batch. Repeating an identical correction leaves evidence and its history intact. |
| Bundle and severity annotations (W35–W36) | Read the selected annotation file. A numeric component share needs a verbatim basis on the specified page in the selected PDF. An exclusion recommendation remains available for human review. Severity tags retain their existing hazard and cue requirements. |
| Direction audit (W37) | Compare produces a disagreements file from the selected recodes. Apply publishes evidence, review events and run metrics together. Each completed apply records one metrics block, including intentional reruns. |
| Automatic quarantine (W38) | Reads evidence, source categories, operational-risk policy, applied review history and pending decisions. Eligible records get a reversible soft drop and a reason in their attribution. Signed-off, previously dropped, reviewed and pending-decision records retain their protection. |

## Preview on an isolated checkout

Run from the compiler checkout with its Python dependencies. Replace the example path with the selected data checkout.

```sh
uv run python -m nbs_ruralscan.schema_tools.migrate_effects --root /path/to/data --dry-run
uv run python scripts/direction-audit.py compare --root /path/to/data --dry-run
uv run python -m nbs_ruralscan.schema_tools.quarantine /path/to/data/schema
```

The archive preview reports the transformation. Write mode also checks existing evidence and the dated import receipt. A replay on a later day keeps each record’s original migration date and writes a receipt for the new run. The original September archive retains its historical receipt format. Other archives record the SHA-256 digest of their bytes, so they can be distinguished even when filenames match. Pass `--deferred` to select a different archive. The four specialist scripts accept `--root` and `--dry-run`. Bundle backfill accepts `--corpus-dir` and direction audit accepts `--recode-dir` for their respective inputs. Quarantine lists candidates by default; `--apply` saves the drops.

## Recovery and verification

These writers stage changes on private copies. They check destinations and read-only inputs before installing the results. They recheck the selected inputs and installed records before reporting success. A caught failure restores any installed files that still belong to this operation. If an independent edit prevents rollback, the error identifies a recovery directory. Maintain one active writer per storage set during cutover. A power loss between replacements still requires reconciliation. [Recovery procedure](m08-review-recovery.md#recovery-procedure)

The baseline was the merge of PR #628, commit `6a67a0db`. Comparisons ran on disposable data. [Comparison results and hashes](m08-historical-evidence-parity.json)

- All 72 selected units from the shipped archive transformed identically, including both prior drops. Synthetic imports exercised installation, repeated imports, source updates and refusal of modified evidence.
- Four specialist commands and the repeated direction audit produced the same evidence, review log, disagreements and metrics as their predecessors. The comparison used all 6,447 evidence records, 395 severity tags, 3,431 recodes and 601 adjudications. One synthetic PDF-backed share exercised the page check.
- The geographic backfill selected the same 17 changes from 747 source records. Quarantine found zero candidates on the copied register. After adding two eligible cases to the copy, both implementations selected those two and wrote byte-identical evidence.
- Failure tests cover partial installation, changes to pending decisions or annotation inputs during publication, and retention of human edits. Private full-text verification remains a separate evidence-release check.

The next migration step separates authored configuration from compiled recipe rows and defines how readers select a complete published release. The historical writer inventory stays available for the eventual cutover rehearsal.
