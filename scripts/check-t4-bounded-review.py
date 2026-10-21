"""Validate bounded T4 review coverage without claiming a new literature sweep."""

import csv
import hashlib
import json
from pathlib import Path


def documented_review_transition(row, old, log, since):
    """Accept later human decisions only when ledger, attribution and state agree."""
    if (
        not row
        or not since
        or str(old.get("reviewer_ok", "false")).lower() not in {"true", "false", ""}
    ):
        return False
    entries = [
        r for r in log if r["evidence_id"] == row["evidence_id"] and r["date"] >= since
    ]
    if not entries:
        return False
    decision = entries[-1]
    reviewer = decision.get("reviewer", "")
    if not reviewer or decision.get("source_id") != row["source_id"]:
        return False
    action = decision["decision"]
    tag = {"ok": "reviewed", "flag": "query", "drop": "dropped"}.get(action)
    if not tag or f"[{tag} {decision['date']} by {reviewer}" not in row.get(
        "attribution", ""
    ):
        return False
    approved = str(row.get("reviewer_ok", "")).lower() == "true"
    state = row.get("review_state", "")
    return (
        (action == "ok" and approved and state == "")
        or (action == "flag" and not approved and state == "")
        or (action == "drop" and not approved and state == "dropped")
    )


def check(root, audit):
    manifest = json.loads((audit / "manifest.json").read_text())
    evidence = {
        r["evidence_id"]: r
        for r in csv.DictReader(
            (root / "schema/registers/EV_evidence_register.csv").open()
        )
    }
    with (root / "pipeline/metrics/review_log.csv").open() as handle:
        review_log = list(csv.DictReader(handle))
    since = manifest.get("review_snapshot_date")
    expected = set(manifest["expected_source_ids"])
    errors = []
    for row in csv.DictReader(
        (root / "schema/recipes/agroforestry/T4_suitability_mappings.csv").open()
    ):
        for eid in json.loads(row["evidence_ids"] or "[]"):
            if eid not in evidence:
                errors.append(f"Live T4 references missing evidence: {eid}")
            elif evidence[eid]["source_id"] not in expected:
                errors.append(
                    f"Live T4 source absent from bounded review: {evidence[eid]['source_id']}"
                )
    if set(manifest["sources"]) != expected:
        errors.append("Manifest source coverage differs from declared scope")
    for sid, item in manifest["sources"].items():
        if not item.get("review") or not item.get("artifact_sha256"):
            errors.append(f"Missing review or artifact identity: {sid}")
        pdf = root / ".cache/corpus" / f"{sid}.pdf"
        if (
            pdf.exists()
            and hashlib.sha256(pdf.read_bytes()).hexdigest() != item["artifact_sha256"]
        ):
            errors.append(f"Reviewed source artifact changed: {sid}")
    for eid, old in manifest["existing_approval_snapshot"].items():
        row = evidence.get(eid)
        if (
            row is None or any(row[k] != v for k, v in old.items())
        ) and not documented_review_transition(row, old, review_log, since):
            errors.append(f"Existing human review state changed: {eid}")
    declared = [
        eid
        for source in manifest["sources"].values()
        for eid in source["new_evidence_ids"]
    ]
    if sorted(declared) != sorted(manifest["new_evidence_ids"]) or len(
        set(declared)
    ) != len(declared):
        errors.append("New record inventory inconsistent or duplicated")
    for eid in manifest["new_evidence_ids"]:
        row = evidence.get(eid)
        if row is None:
            errors.append(f"Missing staged record: {eid}")
            continue
        if row["reviewer_ok"].lower() == "true" and not documented_review_transition(
            row, {}, review_log, since
        ):
            errors.append(f"Bounded review must not invent human approval: {eid}")
        c = json.loads(row["context"] or "{}")
        if not row["quote"] or not row["page"] or not c.get("review_needed"):
            errors.append(
                f"Missing reviewable provenance or intended-use caveat: {eid}"
            )
        if not c.get("t4_assessment", {}).get("source_checked"):
            errors.append(f"Missing source-check marker: {eid}")
        provenance = c.get("direction_provenance")
        if provenance:
            image = root / provenance["image"]
            if not image.exists() or hashlib.sha256(
                image.read_bytes()
            ).hexdigest() != provenance.get("sha256"):
                errors.append(f"Missing or changed directional image: {eid}")
    return errors


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    audit = root / "pipeline/t4_audit/agroforestry/bounded_review_2026-10-21"
    errors = check(root, audit)
    print(
        "\n".join(errors)
        if errors
        else "PASS: bounded source coverage, review states, provenance and pending-record inventory"
    )
    raise SystemExit(bool(errors))
