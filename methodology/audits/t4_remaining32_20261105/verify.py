"""Verify the bounded source screen against local cached artifacts and preserved registers."""

from pathlib import Path
import csv
import io
import json
import subprocess

import fitz

from nbs_ruralscan.recipe.evidence import EvidenceUnit, validate_units
from nbs_ruralscan.schema_tools.validate_sources import _norm

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
BASE = "dd36350"
rows = json.loads((HERE / "sources.json").read_text())
prior = list(
    csv.DictReader(
        (HERE.parent / "all_practice_batch3_20261105/source_triage.csv").open()
    )
)
expected = {
    r["source_id"]
    for r in prior
    if "T4" in r["tables"].split("|")
    and r["classification"] == "ready_unread"
    and r["family"] != "homegardens_proximity"
}
assert len(rows) == 32 and {r["source_id"] for r in rows} == expected
pages = {
    sid: [p.get_text() for p in fitz.open(ROOT / ".cache/corpus" / (sid + ".pdf"))]
    for sid in expected
}
anchors = set()
errors = []


def check(sid, page, quote, label):
    if not quote:
        return
    if not isinstance(page, int) or not 1 <= page <= len(pages[sid]):
        errors.append(f"{label}: invalid page {page}")
    elif _norm(quote) not in _norm(pages[sid][page - 1]):
        errors.append(f"{label}: native anchor mismatch, PDF {page}")
    else:
        anchors.add((sid, page, quote))


for r in rows:
    sid = r["source_id"]
    gate = r["targeting_gate"]
    if sid == "pasture_tree_density_atlantic_2007":
        assert not gate[
            "pass"
        ]  # Explicit image-only hold; not a verified text quotation.
    else:
        check(sid, gate["evidence_page"], gate["verbatim_anchor"], sid + ":gate")
    for filename in ("inventory.json", "candidates.json"):
        p = HERE / "sources" / sid / filename
        if not p.exists():
            continue
        for item in json.loads(p.read_text()):
            quote = item.get("quote") or item.get("native_anchor")
            if isinstance(quote, str) and quote:
                check(sid, item.get("page"), quote, sid + ":" + filename)

units = json.loads((HERE / "draft_units.json").read_text())
assert len(units) == 5
assert not validate_units([EvidenceUnit(**r) for r in units])
for u in units:
    assert u["use_role"] == "structural_suitability" and u["reviewer_ok"] is False
    check(u["source_id"], u["page"], u["quote"], u["evidence_id"])
assert not errors, "\n".join(errors)

preserved = {}
for filename, key in [
    ("schema/registers/EV_evidence_register.csv", "evidence_id"),
    ("schema/registers/SRC_source_register.csv", "source_id"),
]:
    old = list(
        csv.DictReader(
            io.StringIO(
                subprocess.check_output(
                    ["git", "show", BASE + ":" + filename], cwd=ROOT, text=True
                )
            )
        )
    )
    new = list(csv.DictReader((ROOT / filename).open()))
    lookup = {r[key]: r for r in new}
    assert all(lookup.get(r[key]) == r for r in old), filename
    preserved[filename] = {
        "old_rows": len(old),
        "current_rows": len(new),
        "all_old_rows_unchanged": True,
    }
live = {
    r["evidence_id"]: r
    for r in csv.DictReader((ROOT / "schema/registers/EV_evidence_register.csv").open())
}
new = [live[r["evidence_id"]] for r in units]
assert sum(r["review_state"] == "dropped" for r in new) == 2
assert all(r["reviewer_ok"].lower() == "false" for r in new)
for mapping in (ROOT / "schema/recipes").glob("*/T4_suitability_mappings.csv"):
    rel = str(mapping.relative_to(ROOT))
    assert (
        subprocess.check_output(["git", "show", BASE + ":" + rel], cwd=ROOT)
        == mapping.read_bytes()
    )
for filename in [
    "pipeline/metrics/review_log.csv",
    "schema/registers/FAM_family_registry.csv",
]:
    assert (
        subprocess.check_output(["git", "show", BASE + ":" + filename], cwd=ROOT)
        == (ROOT / filename).read_bytes()
    )
result = {
    "sources_screened": len(rows),
    "source_purpose_passes": sum(r["targeting_gate"]["pass"] for r in rows),
    "image_only_holds": 1,
    "unique_native_anchors_verified": len(anchors),
    "anchor_errors": errors,
    "new_structural_records": 5,
    "active_new_units": 3,
    "quarantined_new_units": 2,
    "human_approvals": 0,
    "preservation": preserved,
}
(HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
