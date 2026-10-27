#!/usr/bin/env python3
"""Reconcile T4/M2b source records against two isolated compiler reports.

Outputs are audit artifacts, not analytical schema or new extracted evidence.
"""

from __future__ import annotations

import argparse
import csv
import html
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.recipe.numeric_bands import source_completion
from nbs_ruralscan.schema_tools.generate import _csv_to_rows

ROOT = Path(__file__).resolve().parents[1]


def validated_completions(root: Path) -> dict:
    """Revalidate exceptions from source CSVs, never from report assertions."""
    with (root / "schema/lookups/t4_numeric_compilation_policy.csv").open(
        encoding="utf-8"
    ) as handle:
        policies = {row["evidence_id"]: row for row in csv.DictReader(handle)}
    units = {
        row["evidence_id"]: EvidenceUnit(
            **{k: v for k, v in row.items() if k in EvidenceUnit.__dataclass_fields__}
        )
        for row in _csv_to_rows(root / "schema/registers/EV_evidence_register.csv")
        if row["evidence_id"] in policies
    }
    completions = {}
    for eid, unit in units.items():
        correction = source_completion(unit, units, policies)
        if not correction:
            continue
        pdf = root / ".cache/corpus" / (unit.source_id + ".pdf")
        if (
            pdf.exists()
            and hashlib.sha256(pdf.read_bytes()).hexdigest()
            != correction["source_pdf_sha256"]
        ):
            raise ValueError(f"Source completion PDF changed: {eid}")
        completions[eid] = correction
    return completions


def payload_kind(rel: dict) -> str:
    if rel.get("type"):
        return str(rel["type"])

    def has_labelled_ranges(value: object) -> bool:
        if isinstance(value, dict):
            return ("label" in value and "range" in value) or any(
                has_labelled_ranges(v) for v in value.values()
            )
        if isinstance(value, list):
            return any(has_labelled_ranges(v) for v in value)
        return False

    if has_labelled_ranges(rel):
        return "source_classes_or_codes"
    keys = set(rel)
    if any(
        "class" in k or k.startswith(("very_good", "very_high", "good_min", "group1_"))
        for k in keys
    ):
        return "source_classes_or_codes"
    if any("weight" in k or "importance" in k for k in keys):
        return "weights_or_importance"
    if any("threshold_range" in k or "threshold_values" in k for k in keys):
        return "scenario_grid"
    return "other_relationship"


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("nbs")
    ap.add_argument("directory", type=Path)
    ap.add_argument(
        "--data-only",
        action="store_true",
        help="Write reconciliation data only; preserve historical HTML reports",
    )
    args = ap.parse_args()
    out = args.directory
    completions = validated_completions(ROOT)
    reports = {
        mode: json.loads((out / mode / "report.json").read_text())
        for mode in ("draft", "approved")
    }
    for report in reports.values():
        for relative, expected in report["input_sha256"].items():
            if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
                raise ValueError(f"Stale synthesis report input: {relative}")
    with (ROOT / f"schema/recipes/{args.nbs}/T4_suitability_mappings.csv").open(
        encoding="utf-8"
    ) as handle:
        live = list(csv.DictReader(handle))
    live_links = {}
    for mapping in live:
        for eid in json.loads(mapping["evidence_ids"] or "[]"):
            live_links.setdefault(eid, []).append(mapping)
    parked_path = out / "parked_mappings.csv"
    parked = {}
    if parked_path.exists():
        with parked_path.open(encoding="utf-8") as handle:
            parked = {r["evidence_id"]: r for r in csv.DictReader(handle)}
    dispositions = {}
    for mode, report in reports.items():
        flat = {}
        for family in report["families"].values():
            overlap = flat.keys() & family["dispositions"].keys()
            if overlap:
                raise ValueError(f"Duplicate evidence dispositions: {overlap}")
            flat.update(family["dispositions"])
        dispositions[mode] = flat
    with (ROOT / "schema/registers/EV_evidence_register.csv").open() as f:
        units = [
            r
            for r in csv.DictReader(f)
            if r["nbs_id"] == args.nbs
            and (
                r["use_role"] in {"structural_suitability", "operational_risk"}
                or r["evidence_id"] in live_links
            )
        ]
    reconciliation = []
    classes = []
    for u in units:
        eid = u["evidence_id"]
        if any(eid not in dispositions[mode] for mode in reports):
            if (
                u["use_role"] not in {"structural_suitability", "operational_risk"}
                and eid in live_links
            ):
                for mode in reports:
                    dispositions[mode][eid] = {
                        "status": "other_role_host_identity_reference"
                    }
            else:
                raise ValueError(f"Missing disposition: {eid}")
        mappings = live_links.get(eid, [])
        if mappings and (
            u["review_state"] == "dropped"
            or (u["reviewer_ok"].lower() != "true" and eid not in completions)
        ):
            raise ValueError(f"Live T4 references unapproved/dropped evidence: {eid}")
        if mappings and eid in parked:
            raise ValueError(f"Parked mapping entered live T4: {eid}")
        rel = json.loads(u["relationship"] or "{}")
        row = {
            key: u[key]
            for key in (
                "evidence_id",
                "source_id",
                "suitability_family_id",
                "variable",
                "use_role",
                "claim_scope",
                "reviewer_ok",
                "review_state",
                "relationship",
                "page",
            )
        }
        row.update(
            draft_status=dispositions["draft"][eid]["status"],
            approved_status=dispositions["approved"][eid]["status"],
            payload_kind=payload_kind(rel),
            live_mapping_ids="|".join(r["mapping_id"] for r in mappings),
            final_disposition=(
                "live_verified_source_completion"
                if mappings and eid in completions
                else "live_categorical_host_reference"
                if mappings
                and all(r["relationship_type"] == "ranked_classes" for r in mappings)
                else "live_numeric_contributor"
                if mappings
                else "parked_source_mapping"
                if eid in parked
                else "operational_risk_retained"
                if u["use_role"] == "operational_risk"
                and u["review_state"] != "dropped"
                else dispositions["approved"][eid]["status"]
            ),
            disposition_reason=(
                parked[eid]["reason"]
                if eid in parked
                else "Authorized source-table completion; human review status unchanged. "
                + completions[eid].get("note", "")
                if mappings and eid in completions
                else "Evidence-linked categorical host identity; not numeric suitability or effect magnitude."
                if mappings
                and all(r["relationship_type"] == "ranked_classes" for r in mappings)
                else "Contributes to reviewed numeric rule."
                if mappings
                else "M2b/implementation evidence retained outside structural T4."
                if u["use_role"] == "operational_risk"
                and u["review_state"] != "dropped"
                else dispositions["approved"][eid].get(
                    "reason", dispositions["approved"][eid]["status"]
                )
            ),
        )
        if "pending" in (row["draft_status"], row["approved_status"]):
            raise ValueError(f"Unaccounted compiler disposition: {eid}")
        reconciliation.append(row)
        if (
            row["payload_kind"] in {"source_ordinal_classes", "source_classes_or_codes"}
            and u["review_state"] != "dropped"
            and u["use_role"] == "structural_suitability"
        ):
            classes.append({**row, "quote": u["quote"], "context": u["context"]})
    missing_links = set(live_links) - {u["evidence_id"] for u in units}
    if missing_links:
        raise ValueError(
            f"Live mapping references missing evidence: {sorted(missing_links)}"
        )
    if set(parked) - {u["evidence_id"] for u in units}:
        raise ValueError("Parked mapping references missing evidence")
    write_csv(
        out / "record_reconciliation.csv", reconciliation, list(reconciliation[0])
    )
    write_csv(
        out / "class_evidence.csv", classes, [*reconciliation[0], "quote", "context"]
    )
    source_rows = []
    for family in sorted({u["suitability_family_id"] for u in units}):
        for sid in sorted(
            {u["source_id"] for u in units if u["suitability_family_id"] == family}
        ):
            members = [
                u
                for u in units
                if u["suitability_family_id"] == family and u["source_id"] == sid
            ]
            source_rows.append(
                dict(
                    family=family,
                    source_id=sid,
                    evidence_ids="|".join(u["evidence_id"] for u in members),
                    active_records=sum(u["review_state"] != "dropped" for u in members),
                    basis="registered_evidence_only_not_complete_screened_membership",
                )
            )
    write_csv(out / "source_inventory.csv", source_rows, list(source_rows[0]))
    summary = {
        "nbs": args.nbs,
        "records": len(units),
        "roles": dict(Counter(u["use_role"] for u in units)),
        "structural_active": sum(
            u["use_role"] == "structural_suitability" and u["review_state"] != "dropped"
            for u in units
        ),
        "structural_dropped": sum(
            u["use_role"] == "structural_suitability" and u["review_state"] == "dropped"
            for u in units
        ),
        "structural_dispositions": {
            mode: dict(
                Counter(
                    r[mode + "_status"]
                    for r in reconciliation
                    if r["use_role"] == "structural_suitability"
                )
            )
            for mode in reports
        },
        "generic_rows": {
            mode: sum(len(f["rows"]) for f in report["families"].values())
            for mode, report in reports.items()
        },
        "active_class_records": len(classes),
        "screened_corpus": "unknown: aggregate search counts and acquisition lists are not complete source-level screening records",
        "all_records_accounted_for": True,
        "final_dispositions": dict(
            Counter(r["final_disposition"] for r in reconciliation)
        ),
        "live_rows": len(live),
        "live_categorical_rows": sum(
            r["relationship_type"] == "ranked_classes" for r in live
        ),
        "unique_live_evidence_references": len(live_links),
        "authorized_source_completions": sorted(set(live_links) & completions.keys()),
        "parked_mapping_records": len(parked),
        "support_percentages_present": sum(bool(r["paper_support_pct"]) for r in live),
        "live_t4_sha256": hashlib.sha256(
            (
                ROOT / f"schema/recipes/{args.nbs}/T4_suitability_mappings.csv"
            ).read_bytes()
        ).hexdigest(),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if args.data_only:
        print(json.dumps(summary, indent=2))
        return
    heads = [
        "evidence_id",
        "source_id",
        "variable",
        "draft_status",
        "approved_status",
        "payload_kind",
        "final_disposition",
        "live_mapping_ids",
        "disposition_reason",
    ]
    table = "".join(
        "<tr>"
        + "".join("<td>" + html.escape(str(r[k])) + "</td>" for k in heads)
        + "</tr>"
        for r in reconciliation
    )
    class_cards = "".join(
        "<details><summary>"
        + html.escape(r["source_id"] + " · " + r["variable"] + " · " + r["evidence_id"])
        + "</summary><p>Source page "
        + html.escape(r["page"])
        + "; family "
        + html.escape(r["suitability_family_id"])
        + "</p><pre>"
        + html.escape(
            json.dumps(json.loads(r["relationship"]), indent=2, ensure_ascii=False)
        )
        + "</pre><blockquote>"
        + html.escape(r["quote"])
        + "</blockquote></details>"
        for r in classes
    )
    active = [u for u in units if u["review_state"] != "dropped"]
    reviewed = sum(u["reviewer_ok"].lower() == "true" for u in active)
    review_status = (
        f"Current register: {reviewed} of {len(active)} active audited records have reviewer_ok=true. "
        f"{len(parked)} source mappings are explicitly parked; source approval does not resolve their class semantics."
    )
    document = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Agroforestry T4 pipeline audit</title>
<style>body{font:16px system-ui;max-width:1400px;margin:40px auto;padding:0 24px;color:#16362b;background:#f6f8f5}h1{font-size:34px}section{padding:24px;background:white;border:1px solid #dce5df;margin:20px 0;border-radius:12px}table{border-collapse:collapse;font-size:12px;width:100%}td,th{text-align:left;padding:9px;border-bottom:1px solid #ddd;overflow-wrap:anywhere}input{font:inherit;padding:12px;width:90%}pre,blockquote{white-space:pre-wrap;overflow-wrap:anywhere}summary{cursor:pointer;padding:12px}a{color:#17694c}.warn{background:#fff0cf;padding:18px;border-radius:8px}</style>
<h1>Agroforestry T4: where evidence goes</h1><p>Final branch reconciliation · 20 October 2026 · Reviewed live T4; pilot testing belongs to Diego.</p>
<section><h2>Result</h2><p><strong>SUMMARY_COUNTS</strong></p><p class="warn">Screened-source denominator unknown. No support percentages or 20% floor decisions inferred from overlapping search totals. One approved numeric rule is a source modelling choice requiring applicability review, not a universal validation.</p><p>REVIEW_STATUS Quarantined records remain retained.</p><p><a href="../review.html?batch=agroforestry-t4-final-audit-oct19">Review eleven corrections</a> · <a href="../review.html?batch=agroforestry-t4-holds-oct19">Earlier five approvals</a></p></section>
<section><p><a href="t4-categorical-tables.html">Land-use and categorical class tables</a></p><h2>Retained class evidence</h2><p>Original source ranks, ranges and codes preserved. These do not become calibrated 0–1 membership scores automatically. “Low” does not mean excluded; unknown dataset codes do not become land-cover classes.</p>CLASS_CARDS</section>
<section><h2>Every record accounted for</h2><input id="search" aria-label="Filter records" placeholder="Filter by source, variable, evidence ID or disposition"><table><thead><tr>TABLE_HEAD</tr></thead><tbody>TABLE_ROWS</tbody></table></section>
<script>document.getElementById('search').addEventListener('input',e=>{let q=e.target.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))})</script></html>"""
    document = document.replace(
        "SUMMARY_COUNTS",
        f"{len(live)} live T4 rows · {len(live_links)} unique linked evidence records · {len(parked)} mappings explicitly parked · {len(units)} records reconciled (including cross-role host references) · {summary['structural_active']} active structural records · {summary['generic_rows']['draft']} draft numeric rows · {summary['generic_rows']['approved']} approval-filtered numeric row · {len(classes)} active class records retained",
    )
    document = (
        document.replace("REVIEW_STATUS", html.escape(review_status))
        .replace("CLASS_CARDS", class_cards)
        .replace("TABLE_HEAD", "".join("<th>" + k + "</th>" for k in heads))
        .replace("TABLE_ROWS", table)
    )
    (ROOT / "docs/review/t4-pipeline-audit.html").write_text(document)
    if args.nbs == "agroforestry":
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/tabulate-t4-classes.py"),
                "--directory",
                str(out),
            ],
            check=True,
        )
    if args.nbs == "agroforestry":
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/report-t4-harmonization.py")],
            check=True,
        )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
