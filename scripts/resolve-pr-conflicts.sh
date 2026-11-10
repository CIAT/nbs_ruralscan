#!/usr/bin/env bash
# Fast path for "PR has conflicts": merge latest main into a PR branch, rebuild once,
# re-synthesise only what changed, run the quick gates, push. Full pytest is left to CI.
#
#   bash scripts/resolve-pr-conflicts.sh <pr-number|branch> [--full-tests] [--no-push] [--generated-only]
#
#   --no-push         commit locally but do not push (the auto-resolve workflow pushes itself)
#   --generated-only  refuse (exit 5) if regeneration changed anything other than generated
#                     outputs — e.g. the write-mode build auto-quarantining evidence rows. Used
#                     by the unattended workflow so a bot never edits a register on its own.
#
# Exit codes: 0 done · 2 real conflict · 3 rows need new prose · 4 a gate failed ·
#             5 regeneration touched hand-edited files (with --generated-only).
#
# Relies on the merge drivers registered by scripts/setup-repo.sh (regen / keycsv /
# jsonunion / union). Stops, without pushing, when a conflict needs a human: a row or key
# edited differently on both sides, a source file conflict, or rows needing new prose.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"; cd "$root"
target="${1:?usage: resolve-pr-conflicts.sh <pr-number|branch> [--full-tests] [--no-push] [--generated-only]}"
shift
full=""; push=1; generated_only=0
for arg in "$@"; do
  case "$arg" in
    --full-tests) full="--full-tests" ;;
    --no-push) push=0 ;;
    --generated-only) generated_only=1 ;;
    *) echo "unknown option: $arg"; exit 1 ;;
  esac
done
# Files the build itself writes (keep in step with the merge=regen lines in .gitattributes).
generated_re='^(docs/[^/]+\.json|docs/review/decisions\.json|docs/effect_rows_flat\.csv|docs/dashboard-[^/]+\.csv|schema/([^/]+|registers/[^/]+|lookups/[^/]+|recipes/.+)\.json|schema/recipes/[^/]+/(T3_nbs_hazard_farming|T6_nbs_scorecard|T6E_economic_profile)\.csv)$'
py() { uv run python "$@"; }

git config --get merge.keycsv.driver >/dev/null || bash scripts/setup-repo.sh >/dev/null
if [[ "$target" =~ ^[0-9]+$ ]]; then
  state=$(gh pr view "$target" --json state -q .state)
  [ "$state" = "OPEN" ] || { echo "PR #$target is $state — nothing to do (merged branches are frozen)"; exit 0; }
  branch=$(gh pr view "$target" --json headRefName -q .headRefName)
else
  branch="$target"
fi
[ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "working tree not clean — commit or stash first"; exit 1; }

echo "▸ $branch: merging origin/main"
git checkout -q "$branch"; git pull -q --ff-only || true
git fetch -q origin main
base_before=$(git rev-parse HEAD)
rm -f "$(git rev-parse --git-dir)/REGEN_NEEDED"
if ! git merge --no-edit origin/main >/tmp/rpc_merge.log 2>&1; then
  left=$(git diff --name-only --diff-filter=U)
  # generated files that still show as conflicted: take ours, they are rebuilt below
  for f in $left; do
    case "$f" in
      docs/*.json|docs/*.csv|schema/*.json|schema/registers/*.json|schema/recipes/*)
        git checkout --ours -- "$f" && git add "$f" ;;
    esac
  done
  left=$(git diff --name-only --diff-filter=U)
  if [ -n "$left" ]; then
    echo "✗ needs a human — conflicts left in:"; echo "$left"; grep -h "keycsv\|jsonunion" /tmp/rpc_merge.log || true
    exit 2
  fi
  git commit -q --no-edit
fi
[ "$(git rev-parse HEAD)" = "$base_before" ] && { echo "✓ already up to date with main"; }

echo "▸ regenerating (once)"
py src/nbs_ruralscan/schema_tools/generate.py schema >/dev/null 2>&1 || true

# re-synthesise NbS whose effect inputs changed relative to main
changed=$(git diff --name-only origin/main...HEAD; git diff --name-only HEAD...origin/main) || true
nbs=""
if echo "$changed" | grep -qE "src/nbs_ruralscan/recipe/(cell_synthesis|t3t6_build)|schema/registers/XW_|schema/lookups/|scripts/synthesise-t3t6"; then
  nbs="agroforestry water_harvesting_conservation wetland_management riparian_buffer forest_restoration mangrove_restoration"
elif echo "$changed" | grep -q "schema/registers/EV_evidence_register.csv"; then
  nbs=$(py - <<'PY'
import csv, io, subprocess
def rows(ref):
    t = subprocess.run(["git", "show", f"{ref}:schema/registers/EV_evidence_register.csv"], capture_output=True, text=True).stdout
    return {r["evidence_id"]: r for r in csv.DictReader(io.StringIO(t))}
a, b = rows("origin/main"), rows("HEAD")
print(" ".join(sorted({(a.get(k) or b.get(k))["nbs_id"] for k in set(a) | set(b) if a.get(k) != b.get(k)} - {""})))
PY
)
fi
if [ -n "$nbs" ]; then
  echo "▸ re-synthesising: $nbs"
  for n in $nbs; do [ -d "schema/recipes/$n" ] && py scripts/synthesise-t3t6.py "$n" >/dev/null; done
  py src/nbs_ruralscan/schema_tools/generate.py schema >/dev/null 2>&1 || true
  pending=""
  for n in $nbs; do
    c=$(py scripts/write-prose.py bundle "$n" 2>/dev/null | tail -1 | cut -d' ' -f1)
    [ "${c:-0}" != "0" ] && pending="$pending $n:$c"
  done
  [ -z "$pending" ] || { echo "✗ rows need new prose:$pending — write prose (scripts/write-prose.py), then rerun"; exit 3; }
fi

echo "▸ quick gates"
py src/nbs_ruralscan/schema_tools/generate.py schema --check 2>&1 | grep -q "^stale: 0" || { echo "✗ generated files stale"; exit 4; }
py -m nbs_ruralscan.schema_tools.ledger check >/dev/null || { echo "✗ ledger check"; exit 4; }
py src/nbs_ruralscan/schema_tools/structure.py schema >/dev/null || { echo "✗ structure check"; exit 4; }
uv run ruff check -q . || { echo "✗ ruff"; exit 4; }
if [ "$full" = "--full-tests" ]; then
  uv run pytest -q -x || exit 4
else
  uv run pytest -q -x tests/test_cell_synthesis.py tests/test_effect_checks.py tests/test_pipeline_hardening.py tests/test_t4_recovery.py >/dev/null || { echo "✗ core tests"; exit 4; }
fi

if [ "$generated_only" = 1 ]; then
  touched=$(git diff --name-only HEAD | grep -vE "$generated_re" || true)
  if [ -n "$touched" ]; then
    echo "✗ regeneration changed hand-edited files (not pushed):"; echo "$touched"
    exit 5
  fi
fi
git add -u  # tracked files only: other sessions may have untracked work in this tree
git diff --cached --quiet || git commit -q -m "chore: regenerate after merging main"
if [ "$push" = 0 ]; then
  echo "✓ $branch merged and regenerated locally (not pushed)"
  exit 0
fi
git push -q
echo "✓ pushed $branch (full test suite runs in CI)"
[[ "$target" =~ ^[0-9]+$ ]] && sleep 15 && gh pr view "$target" --json mergeable,mergeStateStatus -q '"mergeable=\(.mergeable) state=\(.mergeStateStatus)"' || true
