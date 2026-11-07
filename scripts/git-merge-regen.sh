#!/usr/bin/env bash
# Custom git merge driver for GENERATED files (dashboard/progress/scorecard JSON, register
# and recipe *.json, the flat effect-row CSV). They are a deterministic function of the
# source CSVs, so a 3-way text merge of them is noise.
#
# FAST PATH (2026-11-07): the driver no longer regenerates. It used to run the full
# generate.py once PER conflicting file (~2 min each), so a merge touching eight generated
# files spent ~16 min inside git. Now it keeps OUR copy (no conflict markers) and drops a
# marker; regenerate ONCE after the merge. `scripts/resolve-pr-conflicts.sh` does that, and
# CI's `generate.py --check` catches anyone who forgets.
#
# git calls:  git-merge-regen.sh %O %A %B %P   (result must be left in %A)
set -u
root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
touch "$(git rev-parse --git-dir)/REGEN_NEEDED" 2>/dev/null || true
exit 0
