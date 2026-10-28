# ruff: noqa: E402
"""Read-only exact-filename reconciliation against synced team stocktake PDFs."""

from pathlib import Path
import csv
import json
import hashlib
import fitz
import os

ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)
OUT = ROOT / "pipeline/staging/forest_t4_20261028"
base = Path(os.environ["NBS_STOCKTAKE_ROOT"])
files = list(base.rglob("*.pdf"))
rows = list(csv.DictReader((OUT / "stocktake_reconciliation.csv").open()))
priority = []
for row in rows:
    matches = [p for p in files if p.name == row["stocktake_file"]]
    row["stocktake_mirror_paths"] = json.dumps([str(p) for p in matches])
    row["local_artifact_status"] = (
        "found exact filename; central identity/intake required"
        if matches
        else "no exact filename in Stocktake Review mirror; alternate filename/content reconciliation pending"
    )
    for p in matches:
        if any(a in p.name for a in ["Rajaonarivelo", "Poccard", "Chen et al. - 2021"]):
            with fitz.open(p) as d:
                priority.append(
                    {
                        "file": str(p),
                        "pages": len(d),
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                        "opening_text": d[0].get_text(),
                        "status": "local artifact found; candidate identity only; Crossref queue verification and central intake not performed by subagent",
                    }
                )
with (OUT / "stocktake_reconciliation.csv").open("w") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
(OUT / "stocktake_priority_artifacts.json").write_text(
    json.dumps(priority, indent=2) + "\n"
)
print(
    "Exact filename matches:",
    sum(r["stocktake_mirror_paths"] != "[]" for r in rows),
    "/",
    len(rows),
)
