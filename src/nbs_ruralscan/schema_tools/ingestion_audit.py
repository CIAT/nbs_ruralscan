"""Read-only discovery/intake reconciliation. Findings are holds, never auto-deletions.

Run ``python -m nbs_ruralscan.schema_tools.ingestion_audit [--json]``. This checks
register consistency, not PDF semantics, search completeness or human approval.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from nbs_ruralscan.ingest.integrity import identity_error, source_identity_differs

ROOT = Path(__file__).resolve().parents[3]


def audit(root: Path = ROOT) -> dict:
    def rows(relative):
        with (root / relative).open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    queue = rows("pipeline/acquisition_queue.csv")
    sources = rows("schema/registers/SRC_source_register.csv")
    evidence = rows("schema/registers/EV_evidence_register.csv")
    q_by_id = {r["source_id"]: r for r in queue}
    src_ids = {r["source_id"] for r in sources}
    ev_by_src = Counter(r["source_id"] for r in evidence)
    findings = []

    def add(kind, identifier, detail):
        findings.append(dict(kind=kind, identifier=identifier, detail=detail))

    for name, records, key in [
        ("queue", queue, "source_id"),
        ("SRC", sources, "source_id"),
        ("EV", evidence, "evidence_id"),
    ]:
        for identifier, count in Counter(r[key] for r in records).items():
            if count > 1:
                add(
                    "duplicate_id",
                    identifier,
                    f"{name}: {count} rows; reconcile before using a keyed lookup",
                )
    for source in sources:
        sid = source["source_id"]
        identity = q_by_id.get(sid)
        error = identity_error(identity)
        if error:
            add("source_identity_hold", sid, error)
        elif identity and source_identity_differs(source, identity):
            add(
                "source_identity_mismatch",
                sid,
                "SRC and verified queue identity differ",
            )
        if source.get("source_kind") in {"paper", "grey_lit"} and not source.get(
            "library_path"
        ):
            add("team_access_missing", sid, "PDF source lacks team library path")
        if (
            source.get("extraction_status") in {"swept", "signed_off"}
            and not ev_by_src[sid]
        ):
            add(
                "completion_needs_inventory",
                sid,
                "No EV rows; zero-yield sweep may be valid, but requires its claim inventory",
            )
    for row in queue:
        if row.get("status") == "acquired" and row["source_id"] not in src_ids:
            add(
                "acquired_not_registered",
                row["source_id"],
                "Acquired source awaiting identity/credibility check and promotion; not necessarily a defect",
            )
    for sid, count in ev_by_src.items():
        if sid not in src_ids:
            add("evidence_without_source", sid, f"{count} EV rows refer to missing SRC")
    return {
        "counts": {
            "queue": len(queue),
            "sources": len(sources),
            "evidence": len(evidence),
        },
        "findings_by_kind": dict(sorted(Counter(f["kind"] for f in findings).items())),
        "findings": findings,
        "limits": "Read-only register audit. Historical identity flags are reconciliation work, not automatic rejection. No corpus sweep or semantic verification performed.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit()
    print(
        json.dumps(
            result
            if args.json
            else {k: v for k, v in result.items() if k != "findings"},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
