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

from nbs_ruralscan.recipe.numeric_bands import parse_profiles


def read(root, path):
    with (root / path).open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def followup_key(row):
    return hashlib.sha256(
        (row["evidence_id"] + "|" + row["reviewer"] + "|" + row["note"]).encode()
    ).hexdigest()


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
            if row["reviewer_ok"].lower() != "true" and eid in live_ids:
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
    for row in read(root, "pipeline/metrics/review_log.csv"):
        if row["evidence_id"] not in evidence or row["reviewer"].lower().startswith(
            ("codex", "ai")
        ):
            continue
        if not re.search(
            r"figure|fig\.?\s*\d|table\s*\d|screen.?grab|missing", row["note"], re.I
        ):
            continue
        followup = followups.get(followup_key(row))
        if (
            not followup
            or followup["status"] not in ("needs_review", "resolved")
            or not followup["resolution"]
        ):
            errors.append("Untracked review follow-up: " + row["evidence_id"])
        elif followup["status"] == "resolved" and not followup.get(
            "resolution_evidence_ids"
        ):
            errors.append("Resolved follow-up lacks evidence: " + row["evidence_id"])
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
