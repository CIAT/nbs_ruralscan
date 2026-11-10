---
description: Merge latest main into a PR branch and resolve conflicts the fast way (one regeneration, targeted re-synthesis, quick gates, push)
argument-hint: <pr-number>
---

Run `bash scripts/resolve-pr-conflicts.sh $ARGUMENTS` from the repo root and report the result.

- Exit 0: pushed; give the PR link and its mergeable state. The full test suite runs in CI.
- Exit 2: a real conflict (same register row or follow-up key edited on both sides, or a
  source/code file). Resolve those rows by hand — never "take theirs" on a register or on
  `review_followups.json` — commit, and rerun the script.
- Exit 3: re-synthesis produced rows that need new prose. Write it with
  `scripts/write-prose.py bundle|check|merge` (sonnet writer, staging only), then rerun.
- Exit 4: a gate failed; fix it, then rerun.

Do not run the full pytest suite locally unless asked (`--full-tests`); CI runs it.
Check the PR is still OPEN first (the script refuses merged PRs).
- Exit 5 (only with `--generated-only`, used by the auto-resolve workflow): the rebuild would
  change a hand-edited file (e.g. auto-quarantine touching the evidence register). Run the
  script without that flag locally and review the change before pushing.

Conflicting PRs are normally fixed automatically after every merge to main by
`.github/workflows/auto-resolve-conflicts.yml`; PRs it cannot fix carry the
`needs-manual-merge` label and a comment explaining why.
