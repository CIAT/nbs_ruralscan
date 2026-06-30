#!/usr/bin/env bash
# Custom git merge driver for GENERATED JSON (dashboard_data.json, progress.json, the
# register *.json). These are committed (GitHub Pages serves them statically) but are a
# deterministic function of the CSV source of truth — so any two branches that both touch
# the registers collide on the regenerated JSON with a meaningless line-level conflict.
#
# Instead of a 3-way text merge, this driver ignores BOTH sides and rebuilds the file from
# the (already-merged) CSVs via generate.py, then drops the fresh content into git's result
# slot. Registered in .gitattributes as `merge=regen`; activated per-clone by scripts/setup-repo.sh.
#
# git calls:  git-merge-regen.sh %O %A %B %P
#   %O ($1) = common-ancestor blob   %A ($2) = OUR/result file (driver must leave result here)
#   %B ($3) = THEIR blob             %P ($4) = pathname of the file in the repo
set -u
root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 1
cd "$root" || exit 1

# Rebuild ALL generated JSON from the merged CSVs (one call regenerates everything).
# Never abort the merge if generate fails (e.g. a CSV still conflicted, or missing deps);
# CI's `generate.py --check` is the backstop that catches any staleness left behind.
if command -v uv >/dev/null 2>&1; then
  uv run python3 src/nbs_ruralscan/schema_tools/generate.py schema >/dev/null 2>&1 || true
else
  python3 src/nbs_ruralscan/schema_tools/generate.py schema >/dev/null 2>&1 || true
fi

# Copy the freshly-generated canonical file ($4 = repo path) into git's result slot ($2 = %A).
if [ -f "$4" ]; then
  cp "$4" "$2"
  exit 0
fi
# Couldn't regenerate the target — fall back to OUR version (no conflict markers); CI will
# flag it stale until someone runs generate.py.
exit 0
