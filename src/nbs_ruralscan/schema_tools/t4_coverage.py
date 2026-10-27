"""Regression gates for documented T4 source, table and review coverage.

Inventories are independently reviewed expectations, not inferred completeness.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata

from nbs_ruralscan.recipe.numeric_bands import parse_profiles, source_completion
from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.schema_tools.generate import _csv_to_rows


def read(root, path):
    with (root / path).open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def followup_key(row):
    return hashlib.sha256(
        (row["evidence_id"] + "|" + row["reviewer"] + "|" + row["note"]).encode()
    ).hexdigest()


# Defect codes must work even when a reviewer leaves no free-text note.
FOLLOWUP_REASONS = {
    "relationship_missed",
    "insufficient_context",
    "wrong_table",
    "wrong_variable",
    "unusable_value",
    "uninterpretable_weight",
    "quote_too_narrow",
    "smuggled_number",
    "table_error",
    "cross_row_stitch",
    "table_garble",
    "missed_error",
}


def needs_followup(row, evidence):
    unit = evidence.get(row["evidence_id"])
    if not unit or row["reviewer"].lower().startswith(("codex", "ai")):
        return False
    # Preserve historically tracked notes; expand coded defects only in T4/M2b.
    return bool(
        re.search(
            r"figure|fig\.?\s*\d|table\s*\d|screen.?grab|missing", row["note"], re.I
        )
        or (
            unit["use_role"] in ("structural_suitability", "operational_risk")
            and row.get("reason") in FOLLOWUP_REASONS
        )
    )


def check_review_followups(log, evidence, followups, root=None):
    errors = []
    for row in log:
        if needs_followup(row, evidence) and followup_key(row) not in followups:
            errors.append("Untracked review follow-up: " + row["evidence_id"])
    # Validate historical entries too, including evidence subsequently rerouted.
    for key, item in followups.items():
        eid = item.get("evidence_id", "")
        status = item.get("status")
        if key != followup_key(item) or eid not in evidence:
            errors.append("Invalid follow-up identity: " + eid)
        if status not in ("needs_review", "resolved", "quarantined") or not item.get(
            "resolution"
        ):
            errors.append("Invalid follow-up disposition: " + eid)
        if (
            status == "quarantined"
            and evidence.get(eid, {}).get("review_state") != "dropped"
        ):
            errors.append("Follow-up quarantine no longer holds: " + eid)
        if status != "resolved":
            continue
        for artifact in item.get("resolution_artifacts", []):
            path = (root / artifact["path"]) if root is not None else None
            content = (
                path.read_text(encoding="utf-8")
                if path is not None and path.is_file()
                else ""
            )
            start, end = (
                artifact.get("start_marker", ""),
                artifact.get("end_marker", ""),
            )
            if start and end and start in content and end in content:
                content = content[
                    content.index(start) : content.index(end, content.index(start))
                ]
            else:
                content = ""
            if not content or hashlib.sha256(
                content.encode()
            ).hexdigest() != artifact.get("sha256"):
                errors.append("Resolved follow-up display artifact changed: " + eid)
        ids = item.get("resolution_evidence_ids", [])
        checks = item.get("resolution_checks", [])
        if not ids or any(ref not in evidence for ref in ids):
            errors.append("Resolved follow-up lacks valid evidence: " + eid)
        if not checks:
            errors.append("Resolved follow-up lacks corrective field checks: " + eid)
        for assertion in checks:
            ref, field = assertion.get("evidence_id"), assertion.get("field")
            value = evidence.get(ref, {}).get(field)
            if (
                ref not in ids
                or value is None
                or not value
                or hashlib.sha256(value.encode()).hexdigest() != assertion.get("sha256")
            ):
                errors.append("Resolved follow-up corrective field changed: " + eid)
    return errors


def check_direction_inventory(root, evidence, live_ids):
    """Check source-audited expectations, never infer calibration from endpoints."""
    path = root / "pipeline/t4_audit/agroforestry/direction_retention_inventory.json"
    if not path.is_file():
        return ["Missing direction-retention inventory"]
    inventory = json.loads(path.read_text(encoding="utf-8"))
    records = inventory.get("records", [])
    errors = []
    if (
        not records
        or len(records) != inventory.get("expected_records")
        or len({r["evidence_id"] for r in records}) != len(records)
    ):
        errors.append("Incomplete direction-retention inventory")
    for expected in records:
        eid = expected["evidence_id"]
        row = evidence.get(eid)
        if not row:
            errors.append("Missing audited directional evidence: " + eid)
            continue
        rel = json.loads(row["relationship"] or "{}")
        context = json.loads(row["context"] or "{}")
        actual = {
            "source_id": row["source_id"],
            "variable": row["variable"],
            "relationship": rel,
            "reported_values": context.get("reported_values"),
            "weight_path_pct": context.get("model_use", {}).get("weight_path_pct"),
            "direction_provenance": context.get("direction_provenance"),
            "calibration_status": context.get("t4_assessment", {}).get(
                "calibration_status"
            ),
        }
        for field, value in actual.items():
            if value != expected[field]:
                errors.append(f"Audited directional {field} changed: {eid}")
        provenance = expected["direction_provenance"]
        image = root / provenance["image"]
        if (
            not image.is_file()
            or hashlib.sha256(image.read_bytes()).hexdigest() != provenance["sha256"]
        ):
            errors.append("Audited direction source image changed: " + eid)
        if eid in live_ids:
            errors.append("Uncalibrated direction entered executable T4: " + eid)
    return errors


def check(root):
    errors = []
    audit = root / "pipeline/t4_audit/agroforestry"
    coverage = read(root, audit / "stocktake_coverage_2026-10-20.csv")

    def norm(value):
        return unicodedata.normalize("NFC", value.removesuffix(".pdf"))

    covered = {norm(row["paper"]): row for row in coverage}
    sources = {
        row["source_id"]
        for row in read(root, "schema/registers/SRC_source_register.csv")
    }
    for paper in read(root, "reference/stocktake/peer_reviewed_benchmarked.csv"):
        if "agroforest" not in paper["NbS_Practice"].lower():
            continue
        record = covered.get(norm(paper["File"]))
        if not record or record["source_id"] not in sources or not record["finding"]:
            errors.append("Unaccounted stocktake source: " + paper["File"])
    evidence = {
        row["evidence_id"]: row
        for row in read(root, "schema/registers/EV_evidence_register.csv")
        if row["nbs_id"] == "agroforestry"
    }
    policies = {
        row["evidence_id"]: row
        for row in read(root, "schema/lookups/t4_numeric_compilation_policy.csv")
    }
    units = {
        row["evidence_id"]: EvidenceUnit(
            **{k: v for k, v in row.items() if k in EvidenceUnit.__dataclass_fields__}
        )
        for row in _csv_to_rows(root / "schema/registers/EV_evidence_register.csv")
        if row["evidence_id"] in policies
    }
    completions = set()
    for eid, unit in units.items():
        try:
            correction = source_completion(unit, units, policies)
            if correction:
                completions.add(eid)
                pdf = root / ".cache/corpus" / (unit.source_id + ".pdf")
                if (
                    pdf.exists()
                    and hashlib.sha256(pdf.read_bytes()).hexdigest()
                    != correction["source_pdf_sha256"]
                ):
                    errors.append("Source completion PDF changed: " + eid)
        except ValueError as exc:
            errors.append(str(exc))
    live_ids = set()
    for row in read(root, "schema/recipes/agroforestry/T4_suitability_mappings.csv"):
        live_ids.update(json.loads(row["evidence_ids"] or "[]"))
    inventory = json.loads((audit / "table_inventory.json").read_text(encoding="utf-8"))
    for eid, count in inventory.items():
        try:
            row, policy = evidence[eid], policies[eid]
            profiles = parse_profiles(json.loads(row["relationship"]), policy)
            if sum(map(len, profiles.values())) != count:
                errors.append("Incomplete inventoried table: " + eid)
            if row["reviewer_ok"].lower() == "true" and eid not in live_ids:
                errors.append("Approved numeric evidence absent from live T4: " + eid)
            if (
                row["reviewer_ok"].lower() != "true"
                and eid in live_ids
                and eid not in completions
            ):
                errors.append("Unapproved recovery entered live T4: " + eid)
        except (KeyError, ValueError, TypeError) as exc:
            errors.append(f"Uncompilable inventoried table: {eid}: {exc}")
    for eid, row in evidence.items():
        if (
            row["reviewer_ok"].lower() != "true"
            or row["review_state"] == "dropped"
            or row["use_role"] != "structural_suitability"
        ):
            continue
        rel = json.loads(row["relationship"] or "{}")
        # Range-valued class fields: catches the formerly silent Chuma encoding.
        class_fields = [
            key
            for key, value in rel.items()
            if re.search(r"^(very_high|very_good|high|medium|moderate|low)", key)
            and isinstance(value, str)
            and re.search(r"\d", value)
        ]
        if class_fields and eid not in live_ids and eid not in policies:
            errors.append(
                "Approved class payload has neither executable row nor explicit policy: "
                + eid
            )
    followups = json.loads(
        (audit / "review_followups.json").read_text(encoding="utf-8")
    )
    errors.extend(
        check_review_followups(
            read(root, "pipeline/metrics/review_log.csv"), evidence, followups, root
        )
    )
    for row in evidence.values():
        context = json.loads(row["context"] or "{}")
        provenance = context.get("model_use_provenance", {})
        if provenance.get("kind") == "figure_read":
            image = root / provenance["image"]
            if (
                not image.is_file()
                or hashlib.sha256(image.read_bytes()).hexdigest()
                != provenance["sha256"]
            ):
                errors.append(
                    "Missing/changed model-weight image: " + row["evidence_id"]
                )
    errors.extend(check_direction_inventory(root, evidence, live_ids))
    errors.extend(check_extraction_inventory(root, evidence, live_ids))
    return errors


FIVE_SOURCES = {
    "baldwin_2022",
    "pinto_2019",
    "ellis_2000",
    "mendonca_2022",
    "mendonca_2023",
}


def check_extraction_inventory(root, evidence, live_ids):
    """A screened source cannot masquerade as an accounted extraction sweep."""
    path = root / "pipeline/t4_audit/agroforestry/five_source_extraction.json"
    if not path.exists():
        return ["Missing five-source extraction inventory"]
    inventory = json.loads(path.read_text(encoding="utf-8"))["sources"]
    errors = []
    for sid in sorted(FIVE_SOURCES):
        source = inventory.get(sid)
        if not source or source.get("main_paper_status") != "extracted":
            errors.append("Missing completed main-paper extraction: " + sid)
            continue
        pages = set(source.get("pages_inspected", []))
        claims = source.get("claims", [])
        accounted = {page for claim in claims for page in claim.get("pages", [])}
        if pages != set(range(1, source["page_count"] + 1)) or not pages <= accounted:
            errors.append("Unaccounted paper pages: " + sid)
        if not claims or any(
            not c.get("destination") or not c.get("reason") for c in claims
        ):
            errors.append("Missing claim disposition: " + sid)
        claimed_ids = {c["evidence_id"] for c in claims if c.get("evidence_id")}
        if claimed_ids != set(source.get("evidence_ids", [])):
            errors.append("Claim/register inventory mismatch: " + sid)
        for eid in claimed_ids:
            unit = evidence.get(eid)
            if not unit or unit["source_id"] != sid:
                errors.append("Missing extracted evidence: " + eid)
                continue
            claim = next(c for c in claims if c.get("evidence_id") == eid)
            if (
                unit["quote"] != claim["quote"]
                or unit["use_role"] != claim["destination"]
            ):
                errors.append("Extraction provenance or routing changed: " + eid)
            if unit["reviewer_ok"].lower() != "true" and eid in live_ids:
                errors.append("Unapproved extraction entered live T4: " + eid)
        pdf = root / ".cache/corpus" / (sid + ".pdf")
        if (
            pdf.exists()
            and hashlib.sha256(pdf.read_bytes()).hexdigest() != source["pdf_sha256"]
        ):
            errors.append("Extraction source artifact changed: " + sid)
    return errors


def main():
    errors = check(Path(__file__).resolve().parents[3])
    for error in errors:
        print(error)
    print(f"T4 coverage: {len(errors)} errors")
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
