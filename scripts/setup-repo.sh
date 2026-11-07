#!/usr/bin/env bash
# One-time per-clone setup. Run after cloning:  bash scripts/setup-repo.sh
#
# Registers the `regen` merge driver (.gitattributes references it by name; the driver
# COMMAND can't live in .gitattributes, so each clone must set it in .git/config). After
# this, generated JSON (dashboard_data.json / progress.json / register *.json) never throws
# a spurious merge conflict — it's rebuilt from the merged CSVs instead. See
# scripts/git-merge-regen.sh.
#
# Also pins git config that the cross-platform register handling relies on.
set -e
root="$(git rev-parse --show-toplevel)"
cd "$root"

git config merge.regen.name "Regenerate generated JSON from the source CSVs"
git config merge.regen.driver "bash scripts/git-merge-regen.sh %O %A %B %P"
git config merge.keycsv.name "Key-level 3-way merge for register CSVs"
git config merge.keycsv.driver "python3 scripts/git-merge-keycsv.py %O %A %B %P"
git config merge.jsonunion.name "Key-union merge for id-keyed JSON"
git config merge.jsonunion.driver "python3 scripts/git-merge-jsonunion.py %O %A %B %P"

# Windows register hygiene (issue #104/#123): keep CSV line endings as committed.
git config core.autocrlf false

chmod +x scripts/git-merge-regen.sh 2>/dev/null || true

echo "✓ git merge drivers registered: regen (generated files; regenerate once after the merge), keycsv (registers), jsonunion (follow-ups)."
echo "✓ core.autocrlf=false (CSV registers stay LF)."
