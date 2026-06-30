#!/usr/bin/env bash
# Ship your QA review decisions to a clean PR — one command.
#
# Run AFTER you've reviewed flags in the dashboard QA/QC tab (your ok/drop decisions are
# saved locally in pipeline/review/decisions.json). This replaces the fiddly manual git
# dance that kept reverting other people's work and burying tiny review edits in 50k-line
# generated-JSON conflicts.
#
# What it does:
#   1. branches fresh off the LATEST main (so nothing is stale / nothing gets reverted),
#   2. replays your decisions onto the current registers (surgical — only the rows you
#      decided change) and regenerates the JSON,
#   3. commits ONLY the registers + review_log + generated JSON (never dashboard.html etc.),
#   4. pushes and opens a PR.
#
# Your decisions.json is gitignored, so it survives the branch switch untouched.
#
# Usage:  bash scripts/submit-review.sh <your-handle> ["PR title"] [--auto]
#   e.g.  bash scripts/submit-review.sh Namita-J "qaqc: agroforestry T3 batch"
#         bash scripts/submit-review.sh Namita-J "qaqc: T3 batch" --auto   # also merges it
# Run it ONCE per review session (it ships every agreed decision in one PR) — not per flag,
# or you'll mint a PR per click. --auto squash-merges immediately (no approval needed).
set -e
# --auto (anywhere in the args): squash-merge the PR immediately after opening it, so a
# review batch needs zero manual clicks. Safe because main is unprotected + the content is
# low-risk review metadata applied via the canonical path. Drop it to leave the PR for review.
auto=0; posargs=()
for a in "$@"; do
  if [ "$a" = "--auto" ]; then auto=1; else posargs+=("$a"); fi
done
set -- "${posargs[@]}"
reviewer="${1:?usage: bash scripts/submit-review.sh <your-handle> [\"PR title\"] [--auto]}"
title="${2:-qaqc: review decisions ($reviewer)}"
root="$(git rev-parse --show-toplevel)"; cd "$root"

git fetch -q origin
branch="review/${reviewer}-$(git rev-parse --short origin/main)"

# Park any local working changes so we can branch cleanly off main. decisions.json is
# gitignored (the source of truth for your review), so it is NOT stashed and carries over.
if ! git diff --quiet || ! git diff --cached --quiet; then
  git stash push -q -u -m "submit-review wip $(date -u +%FT%TZ)" || true
  echo "• parked local changes in a git stash (recover with: git stash list / git stash pop)"
fi

git checkout -q -B "$branch" origin/main
echo "• branched $branch off latest main"

# Replay decisions.json onto the current registers + regenerate.
uv run python3 -m nbs_ruralscan.schema_tools.submit_review

if git diff --quiet -- schema/registers/EV_evidence_register.csv pipeline/metrics/review_log.csv; then
  echo "• no register changes produced — nothing agreed to apply. Stopping."
  exit 0
fi

git add schema/registers/EV_evidence_register.csv schema/registers/EV_evidence_register.json \
        pipeline/metrics/review_log.csv docs/dashboard_data.json docs/progress.json
git commit -q -m "$title"
git push -q -u origin "$branch"
echo "• pushed $branch"

if command -v gh >/dev/null 2>&1; then
  gh pr create --base main --head "$branch" --title "$title" \
    --body "QA review decisions by **$reviewer**, replayed cleanly onto main (decisions.json → consensus apply → regenerate). Registers + review_log + generated JSON only; no stale-branch reverts." \
    && echo "• PR opened"
  if [ "$auto" = "1" ]; then
    if gh pr merge "$branch" --squash --delete-branch 2>/dev/null; then
      echo "• --auto: PR squash-merged into main + branch deleted"
    else
      echo "• --auto: merge did not complete (CI pending or protection) — merge the PR manually"
    fi
  fi
else
  echo "• gh not found — open the PR manually for branch $branch"
fi
