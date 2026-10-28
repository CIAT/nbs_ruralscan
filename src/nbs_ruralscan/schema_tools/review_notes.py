"""Read source-audit notes onto existing evidence cards without granting approval."""

import csv
import hashlib
import json
from pathlib import Path


def evidence_fingerprint(unit):
    fields = (
        "source_id",
        "page",
        "variable",
        "suitability_family_id",
        "use_role",
        "claim_scope",
        "quote",
        "relationship",
        "context",
    )
    values = {k: unit.get(k, "") for k in fields}
    for key in ("relationship", "context"):
        if isinstance(values[key], str):
            values[key] = json.loads(values[key] or "null")
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


def load_review_notes(root):
    root = Path(root)
    path = root / "schema/registers/EV_evidence_register.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        evidence = {r["evidence_id"]: r for r in csv.DictReader(handle)}
    result = {}
    for path in sorted(
        (root / "pipeline/t4_audit").glob("*/first_pass_review_notes.json")
    ):
        for eid, note in json.loads(path.read_text(encoding="utf-8")).items():
            unit = evidence.get(eid)
            if unit is None or eid in result:
                raise ValueError(f"Missing or duplicate audit-note evidence: {eid}")
            digest = evidence_fingerprint(unit)
            if note.get("evidence_sha256") != digest:
                raise ValueError(f"Source-audit note is stale: {eid}")
            if not all(
                note.get(k)
                for k in (
                    "finding",
                    "intended_use",
                    "remaining_decision",
                    "source_check",
                )
            ):
                raise ValueError(f"Incomplete source-audit note: {eid}")
            result[eid] = note
    return result
