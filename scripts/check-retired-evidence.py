"""Reject changes to CIAT's retired evidence registers and generated review records."""

import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / ".ciat-evidence-readonly").read_text())
paths = [
    *manifest["paths"],
    ":(glob)schema/recipes/*/T3*",
    ":(glob)schema/recipes/*/T6*",
    ":(glob)schema/recipes/*/T4_suitability_mappings.*",
]
changed = subprocess.check_output(
    [
        "git",
        "diff",
        "--no-renames",
        "--name-only",
        manifest["source_revision"],
        "HEAD",
        "--",
        *paths,
    ],
    cwd=root,
    text=True,
)
if changed:
    raise SystemExit(
        f"These evidence paths retired to {manifest['destination']}:\n{changed}"
    )
