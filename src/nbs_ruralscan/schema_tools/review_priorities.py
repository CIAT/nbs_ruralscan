"""Load review triage annotations; never alter evidence, decisions or recipes."""

import csv
import re
from pathlib import Path

from nbs_ruralscan.schema_tools.review_notes import evidence_fingerprint


def load_review_priorities(root):
    root = Path(root)
    path = root / "pipeline/review_priorities.csv"
    if not path.exists():
        return []
    with (root / "schema/registers/EV_evidence_register.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        evidence = {row["evidence_id"]: row for row in csv.DictReader(stream)}
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    seen, batches = set(), {}
    required = (
        "batch_id",
        "batch_label",
        "priority",
        "evidence_id",
        "source_id",
        "reason",
        "decision_needed",
        "requested_by",
        "requested_date",
        "evidence_sha256",
    )
    for row in rows:
        eid, bid = row.get("evidence_id"), row.get("batch_id")
        page = (row.get("page") or "").strip()
        source_locator = (row.get("source_locator") or "").strip()
        if not all(row.get(key, "").strip() for key in required) or not (
            page or source_locator
        ):
            raise ValueError(f"Incomplete review priority: {eid}")
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", bid):
            raise ValueError(f"Invalid priority batch ID: {bid}")
        if row["priority"] not in {"high", "normal"}:
            raise ValueError(f"Invalid review priority: {eid}")
        if (bid, eid) in seen or eid not in evidence:
            raise ValueError(f"Missing or duplicate priority evidence: {eid}")
        seen.add((bid, eid))
        label = batches.setdefault(bid, row["batch_label"])
        if label != row["batch_label"]:
            raise ValueError(f"Inconsistent priority batch label: {bid}")
        if not re.fullmatch(r"[a-f0-9]{64}", row["evidence_sha256"]):
            raise ValueError(f"Invalid priority evidence fingerprint: {eid}")
        # Ongoing review may correct the record. Keep the original request visible,
        # label its old context, and do not block review or silently bless its advice.
        row["context_changed"] = (
            evidence_fingerprint(evidence[eid]) != row["evidence_sha256"]
            or row["source_id"] != evidence[eid]["source_id"]
            or page != str(evidence[eid].get("page") or "").strip()
            or (
                bool(source_locator)
                and source_locator != str(evidence[eid].get("locator") or "").strip()
            )
        )
    return rows
