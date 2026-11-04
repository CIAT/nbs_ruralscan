"""Read-only register/source triage. Outputs audit files, never review decisions."""

import csv
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
import subprocess

import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools import clarifications, ledger  # noqa: E402


def read(path):
    with (ROOT / path).open() as f:
        return list(csv.DictReader(f))


def save(name, rows):
    if not rows:
        (OUT / name).unlink(missing_ok=True)
        return
    with (OUT / name).open("w", newline="") as f:
        writer = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


sources = {r["source_id"]: r for r in read("schema/registers/SRC_source_register.csv")}
ev = [
    r
    for r in read("schema/registers/EV_evidence_register.csv")
    if r["review_state"] != "dropped"
]
families = read("schema/registers/FAM_family_registry.csv")
search = read("schema/registers/SRCH_search_register.csv")
lib = (
    Path.home() / "Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects"
)
cache = ROOT / ".cache/corpus"
issues, availability = [], {}
for sid in sorted({r["source_id"] for r in ev}):
    s = sources.get(sid, {})
    library = lib / s["library_path"] if s.get("library_path") else None
    local = next(
        (
            cache / (sid + ext)
            for ext in [".pdf", ".txt", ".html", ".md"]
            if (cache / (sid + ext)).exists()
        ),
        None,
    )
    path = local or (library if library and library.exists() else None)
    state = dict(
        source_id=sid,
        kind=s.get("source_kind", ""),
        library_path=s.get("library_path", ""),
        url=s.get("url", ""),
        cached=bool(local),
        library_exists=bool(library and library.exists()),
        artifact_available=bool(path),
        pages=0,
        read_error="",
    )
    if path and path.suffix == ".pdf":
        try:
            with fitz.open(path) as doc:
                state["pages"] = len(doc)
                if doc.needs_pass:
                    state["read_error"] = "encrypted_pdf"
        except Exception as exc:
            state["read_error"] = str(exc)
    availability[sid] = state
for r in ev:
    s = sources.get(r["source_id"], {})
    a = availability[r["source_id"]]
    defects = []
    if not s:
        defects.append("missing_SRC")
    if not s.get("library_path") and not s.get("url"):
        defects.append("no_team_link")
    if not a["artifact_available"]:
        defects.append("missing_local_artifact")
    if s.get("library_path") and not a["library_exists"]:
        defects.append("library_path_not_found")
    if a["read_error"]:
        defects.append("unreadable_artifact")
    if a["pages"]:
        if not r["page"].isdigit():
            defects.append(
                "section_locator_pdf_starts_at_page_1"
                if r["locator_type"] and r["locator"]
                else "missing_page_and_locator"
            )
        elif not 1 <= int(r["page"]) <= a["pages"]:
            defects.append("page_out_of_range")
    elif a["artifact_available"] and (not r["locator_type"] or not r["locator"]):
        defects.append("web_code_locator_missing")
    for defect in defects:
        issues.append(
            dict(
                evidence_id=r["evidence_id"],
                source_id=r["source_id"],
                nbs_id=r["nbs_id"],
                use_role=r["use_role"],
                reviewer_ok=r["reviewer_ok"],
                claim_scope=r["claim_scope"],
                page=r["page"],
                defect=defect,
            )
        )
save("source_readiness.csv", list(availability.values()))
save("technical_issues.csv", issues)
# Isolate shared state from ignored decisions in any developer checkout.
with tempfile.TemporaryDirectory() as temp:
    view = Path(temp)
    (view / "schema").symlink_to(ROOT / "schema", target_is_directory=True)
    (view / "pipeline").mkdir()
    for part in ["metrics", "t4_audit"]:
        (view / "pipeline" / part).symlink_to(
            ROOT / "pipeline" / part, target_is_directory=True
        )
    groups = clarifications.build(view)
questions = []
for g in groups:
    for r in g["records"]:
        if r["review_status"] == "resolved":
            continue
        original = (
            next(e for e in ev if e["evidence_id"] == r["evidence_id"])
            if any(e["evidence_id"] == r["evidence_id"] for e in ev)
            else None
        )
        if not original:
            continue
        questions.append(
            dict(
                issue_id=g["id"],
                evidence_id=r["evidence_id"],
                nbs_id=original["nbs_id"],
                reviewer=g["reviewer"],
                review_origin="automated_audit"
                if g["reviewer"].startswith("Codex ")
                else "human",
                status=r["review_status"],
                question=g["question"],
                source_id=g["source"],
            )
        )
save("open_clarifications.csv", questions)
progress = read("pipeline/progress_ledger.csv")
coverage = []
for nbs in sorted({r["nbs_id"] for r in families}):
    es = [r for r in ev if r["nbs_id"] == nbs]
    fams = sorted({r["suitability_family_id"] for r in families if r["nbs_id"] == nbs})
    for fam in fams:
        fs = [r for r in families if r["suitability_family_id"] == fam]
        t4 = [
            r
            for r in es
            if r["suitability_family_id"] == fam
            and r["use_role"] == "structural_suitability"
        ]
        practice = [r for r in t4 if r["claim_scope"] == "practice_technology"]
        crop = [r for r in t4 if r["claim_scope"] == "crop_specific"]
        species = [r for r in t4 if r["claim_scope"] == "species_specific"]
        effects = [
            r
            for r in es
            if r["suitability_family_id"] == fam and r["use_role"] == "nbs_effect"
        ]
        protocols = [
            r
            for r in search
            if r["nbs_id"] == nbs
            and r.get("table") == "T4"
            and r.get("suitability_family_id") == fam
        ]
        coverage.append(
            dict(
                nbs_id=nbs,
                family=fam,
                practices="; ".join(r["name"] for r in fs),
                spatial_product_type=fs[0]["spatial_product_type"],
                active_t4=len(t4),
                practice_t4=len(practice),
                crop_t4=len(crop),
                species_t4=len(species),
                approved_t4=sum(r["reviewer_ok"].lower() == "true" for r in t4),
                active_effect_claims=len(effects),
                t4_protocol_rows=len(protocols),
                t4_ledger="; ".join(
                    x["category"]
                    + ":"
                    + x["searched"]
                    + "/"
                    + x["screened"]
                    + "/"
                    + x["verified"]
                    for x in progress
                    if x["nbs_id"] == nbs and x["family"] == fam and x["table"] == "T4"
                )
                or "no family-specific T4 ledger row",
            )
        )
save("practice_coverage.csv", coverage)
summary = dict(
    baseline=subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip(),
    active_evidence=len(ev),
    active_sources=len(availability),
    technical_issues=dict(Counter(r["defect"] for r in issues)),
    technical_issue_records=len({r["evidence_id"] for r in issues}),
    open_clarification_record_pairs=len(questions),
    open_clarification_status=dict(Counter(r["status"] for r in questions)),
    ledger_errors=ledger.check(ROOT / "schema"),
    coverage=coverage,
)
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: v for k, v in summary.items() if k != "coverage"}, indent=2))
