#!/usr/bin/env python3
"""Promote acquired acquisition-queue rows into the Source Register (SRC).

    python3 scripts/promote-queue-to-src.py --run-id <id> --nbs <nbs_id> \
        --sources <ids.txt | lane.json ...> --meta <overrides.json> [--extractor "..."] [--dry-run]

Mechanical fields come from the queue row + the cached artefact (citation, verified DOI, url,
library path, sha1, access, process → source_category/source_kind, note tags → method_type /
study_country / income group). Judgement fields (benchmark_tier, venue_type, region, overrides
of country / income group) come from `--meta` = {source_id: {...}} authored by the orchestrator
from the six-axis rubric (T4 method §3). Rows already in SRC are skipped. Queue `status` is NOT
touched here — the orchestrator marks `extracted` only for sources that produced EV rows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"
CORPUS = ROOT / ".cache" / "corpus"

_METHOD = {
    "review": "review",
    "systematic_review": "systematic_review",
    "meta_analysis": "meta_analysis",
    "synthesis_brief": "review",
    "case_study_synthesis": "review",
    "institutional_synthesis": "review",
    "programme_evaluation_synthesis": "review",
    "ppar": "mel_report",
    "icr": "mel_report",
    "evaluation_brief": "mel_report",
    "programme_evaluation": "mel_report",
    "programme_evaluation_survey": "mel_report",
    "impact_evaluation": "empirical",
    "quasi_experimental_impact_evaluation": "empirical",
    "field_assessment": "empirical",
    "review_plus_experiment": "empirical",
    "case_analysis_hydraulic": "empirical",
    "multi_site_evaluation": "empirical",
}
_ISO3 = re.compile(r"^[A-Z]{3}$")


def _tag(note: str, key: str) -> str:
    m = re.search(rf"{key}=(\[[^\]]*\]|[^;]+)", note)
    return m.group(1).strip() if m else ""


def _list(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("["):
        try:
            return [str(x) for x in json.loads(raw.replace("'", '"'))]
        except json.JSONDecodeError:
            return []
    return [raw] if raw else []


def _sha1(p: Path) -> str:
    h = hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ids(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        pth = Path(p)
        if pth.suffix == ".json":
            for it in json.loads(pth.read_text(encoding="utf-8")):
                out.append(it["sid"] if isinstance(it, dict) else str(it))
        else:
            out += [ln.strip() for ln in pth.read_text().splitlines() if ln.strip()]
    return out


def build_row(q: dict, meta: dict, cols: list[str], a) -> dict:
    note = q["note"]
    proc = _tag(note, "process") or "updated_lit"
    sub = _tag(note, "method_subtype")
    scope = _list(_tag(note, "study_scope"))
    iso = [s for s in scope if _ISO3.match(s)]
    inc = _list(_tag(note, "income_groups_covered"))
    pdf = CORPUS / f"{q['source_id']}.pdf"
    row = {c: "" for c in cols}
    row.update(
        {
            "source_id": q["source_id"],
            "citation": q["citation"],
            "doi": q["doi"] if q.get("doi_verified") == "true" else "",
            "benchmark_tier": meta.get("benchmark_tier", "medium"),
            "study_country": meta.get("study_country", "; ".join(iso)),
            "region": meta.get("region", "" if iso else "; ".join(scope)),
            "method_type": meta.get("method_type", _METHOD.get(sub, "empirical")),
            "nbs_ids": a.nbs,
            "vars_extracted": "",
            "extraction_status": "swept",
            "extraction_date": a.date,
            "extraction_run_id": a.run_id,
            "extractor": a.extractor,
            "source_kind": "paper" if proc == "updated_lit" else "grey_lit",
            "url": q["url"],
            "artifact_sha1": _sha1(pdf) if pdf.exists() else "",
            "retrieved_at": a.date,
            "access_status": "open_access",
            "source_category": proc,
            "library_path": q["target_library_path"],
            "study_income_group": meta.get(
                "study_income_group", inc[0] if len(inc) == 1 else ""
            ),
            "venue_type": meta.get(
                "venue_type",
                "peer_reviewed_journal"
                if proc == "updated_lit"
                else "institutional_report",
            ),
        }
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--nbs", required=True)
    ap.add_argument("--sources", nargs="+", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--extractor", default="claude-opus-5 (gated pipeline)")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    meta = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    ids = _ids(a.sources)
    with QUEUE.open(newline="", encoding="utf-8") as f:
        queue = {r["source_id"]: r for r in csv.DictReader(f)}
    with SRC.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        cols = list(rd.fieldnames or [])
        existing = {r["source_id"] for r in rd}
    new: list[dict] = []
    for sid in ids:
        if sid in existing:
            print(f"  skip (in SRC): {sid}")
            continue
        q = queue.get(sid)
        if q is None or q["status"] != "acquired":
            print(f"  skip (not acquired in queue): {sid}")
            continue
        row = build_row(q, meta.get(sid, {}), cols, a)
        if not row["artifact_sha1"]:
            print(f"  skip (no cached PDF): {sid}")
            continue
        new.append(row)
        print(
            f"  + {sid:40} {row['benchmark_tier']:6} {row['method_type']:17} "
            f"{row['source_category']:11} {row['venue_type']:22} {row['study_country']:12} "
            f"{row['study_income_group']}"
        )
    print(f"{len(new)} row(s) to append")
    if a.dry_run or not new:
        return 0
    with SRC.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        for r in new:
            w.writerow(r)
    print(f"appended {len(new)} row(s) to {SRC.relative_to(ROOT)}; now regenerate JSON")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
