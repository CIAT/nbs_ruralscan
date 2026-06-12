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
from datetime import datetime, timezone
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


def generate_progress_report(schema_root: Path, check: bool = False) -> list[Path]:
    """Generates docs/progress.json summarizing literature registers status."""
    src_csv = schema_root / "registers" / "SRC_source_register.csv"
    if not src_csv.exists():
        return []

    import subprocess
    from collections import Counter

    try:
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        ).stdout.strip()
    except Exception:
        git_commit = "unknown"

    nbs_stats = {}
    with src_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("source_id"):
                continue
            nbs_ids = [n.strip() for n in row.get("nbs_ids", "").split(";") if n.strip()]
            status = row.get("extraction_status", "pending") or "pending"
            tier = row.get("benchmark_tier", "low") or "low"
            method = row.get("method_type", "empirical") or "empirical"
            country = row.get("study_country", "") or ""
            vars_list = [v.strip() for v in row.get("vars_extracted", "").split(";") if v.strip()]

            for nbs in nbs_ids:
                if nbs not in nbs_stats:
                    nbs_stats[nbs] = {
                        "total_sources": 0,
                        "status_counts": Counter(),
                        "benchmark_tiers": Counter(),
                        "method_types": Counter(),
                        "variables_extracted": set(),
                        "countries": set()
                    }
                s = nbs_stats[nbs]
                s["total_sources"] += 1
                s["status_counts"][status] += 1
                s["benchmark_tiers"][tier] += 1
                s["method_types"][method] += 1
                for v in vars_list:
                    s["variables_extracted"].add(v)
                if country:
                    s["countries"].add(country)

    formatted_stats = {}
    for nbs, s in nbs_stats.items():
        formatted_stats[nbs] = {
            "total_sources": s["total_sources"],
            "status_counts": dict(s["status_counts"]),
            "benchmark_tiers": dict(s["benchmark_tiers"]),
            "method_types": dict(s["method_types"]),
            "variables_extracted": sorted(list(s["variables_extracted"])),
            "countries": sorted(list(s["countries"]))
        }

    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "nbs_progress": formatted_stats
    }

    dest_path = schema_root.parent / "docs" / "progress.json"
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    current_data = None
    if dest_path.exists():
        try:
            current_data = json.loads(dest_path.read_text())
        except Exception:
            pass

    if current_data and current_data.get("git_commit") == git_commit and current_data.get("nbs_progress") == formatted_stats:
        report_data["timestamp"] = current_data["timestamp"]

    text = json.dumps(report_data, ensure_ascii=False, indent=2) + "\n"
    current = dest_path.read_text() if dest_path.exists() else None

    if text == current:
        return []

    changed = [dest_path]
    if not check:
        dest_path.write_text(text)
    return changed


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
    
    # Compile the progress.json report
    changed.extend(generate_progress_report(schema_root, check=check))
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
