"""Generate the schema JSON files from their CSV source-of-truth.

CSVs are the human-editable form; the JSONs are typed artefacts the code reads
(``binding.py``, ``structure.py``, Colab notebooks). Editing both by hand is a
recipe for drift, so JSON is **generated** from CSV — never edited directly.

Conversion rule, per cell: try ``json.loads`` — succeeds → typed value (numbers,
booleans, ``null``, nested ``[...]``/``{...}``); fails → kept as the raw string.
Empty cells are dropped (the structure validator treats missing == empty).

The set of tables is driven by the frozen manifest (``schema/structure/columns.json``)
so working CSVs not in the manifest (e.g. the ``CV_*`` lit-review sheets) are left alone.

Usage::

    python3 src/nbs_ruralscan/schema_tools/generate.py schema           # (re)write all JSONs
    python3 src/nbs_ruralscan/schema_tools/generate.py schema --check    # CI: fail if any JSON is stale

Stdlib only.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def _coerce(value: str):
    """Typed value for a CSV cell; raw string if it isn't valid JSON."""
    if value == "":
        return None  # signals "drop this key"
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _csv_to_rows(path: Path) -> list[dict]:
    with path.open(newline="") as fh:
        rows = []
        for raw in csv.DictReader(fh):
            row = {k: _coerce(v) for k, v in raw.items() if v is not None}
            rows.append({k: v for k, v in row.items() if v is not None})
        return rows


def _csv_files(schema_root: Path, location: str) -> list[Path]:
    """Resolve a manifest ``location`` to existing CSV source files."""
    stem = location.split(".")[0]
    glob = stem.replace("<nbs_id>", "*")
    return sorted(schema_root.glob(glob + ".csv"))


def generate(schema_root: str | Path, *, check: bool = False) -> list[Path]:
    """Write (or, under ``check``, compare) every JSON from its CSV. Returns the
    list of paths that were written / are stale."""
    schema_root = Path(schema_root)
    manifest = json.loads((schema_root / "structure" / "columns.json").read_text())
    changed: list[Path] = []
    for spec in manifest["tables"].values():
        for csv_path in _csv_files(schema_root, spec["location"]):
            json_path = csv_path.with_suffix(".json")
            text = (
                json.dumps(_csv_to_rows(csv_path), ensure_ascii=False, indent=2) + "\n"
            )
            current = json_path.read_text() if json_path.exists() else None
            if text == current:
                continue
            changed.append(json_path)
            if not check:
                json_path.write_text(text)
    return changed


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    check = "--check" in argv
    positional = [a for a in argv if not a.startswith("-")]
    root = (
        Path(positional[0])
        if positional
        else Path(__file__).resolve().parents[3] / "schema"
    )
    changed = generate(root, check=check)
    if check and changed:
        print(
            "Stale JSON (regenerate with `python3 src/nbs_ruralscan/schema_tools/generate.py schema`):"
        )
        for p in changed:
            print(f"  {p}")
        return 1
    verb = "stale" if check else "wrote"
    print(f"{verb}: {len(changed)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
