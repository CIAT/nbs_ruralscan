#!/usr/bin/env bash
# Compatibility wrapper. Windows reviewers can invoke the Python module directly.
set -euo pipefail
auto=(); positional=()
for arg in "$@"; do
  if [ "$arg" = "--auto" ]; then auto=(--auto); else positional+=("$arg"); fi
done
reviewer="${positional[0]:?usage: submit-review.sh <handle> [title] [--auto]}"
title="${positional[1]:-qaqc: review decisions ($reviewer)}"
exec uv run python -m nbs_ruralscan.schema_tools.submit_review --ship "$reviewer" --title "$title" "${auto[@]}"
