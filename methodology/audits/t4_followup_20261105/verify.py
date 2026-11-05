"""Verify this bounded T4 intake against native artifacts and its register baseline."""

import csv
import io
import json
from pathlib import Path
import subprocess

import fitz

from nbs_ruralscan.recipe.evidence import EvidenceUnit, validate_units
from nbs_ruralscan.schema_tools.validate_sources import _norm

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
BASE = "dd80226"


def baseline(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def rows(path):
    with (ROOT / path).open() as stream:
        return list(csv.DictReader(stream))


units = json.loads((HERE / "admitted_units.json").read_text())
assert len(units) == 14
assert not validate_units([EvidenceUnit(**unit) for unit in units])
live = {r["evidence_id"]: r for r in rows("schema/registers/EV_evidence_register.csv")}
anchors = 0
for unit in units:
    record = live[unit["evidence_id"]]
    assert record["use_role"] == "structural_suitability"
    assert record["reviewer_ok"].lower() == "false"
    assert record["review_state"] != "dropped"
    assert record["ruleset_version"] == "v1.9.5"
    with fitz.open(ROOT / ".cache/corpus" / f"{unit['source_id']}.pdf") as pdf:
        for quote_key, page_key in [
            ("quote", "page"),
            ("justification_quote", "justification_page"),
            ("selection_justification", "selection_justification_page"),
        ]:
            quote = unit.get(quote_key)
            if quote:
                page = unit[page_key]
                assert _norm(quote) in _norm(pdf[page - 1].get_text()), unit[
                    "evidence_id"
                ]
                anchors += 1

preservation = {}
for path, key in [
    ("schema/registers/EV_evidence_register.csv", "evidence_id"),
    ("schema/registers/SRC_source_register.csv", "source_id"),
    ("pipeline/acquisition_queue.csv", "source_id"),
]:
    old = list(csv.DictReader(io.StringIO(baseline(path).decode())))
    current = {r[key]: r for r in rows(path)}
    changed = {}
    for row in old:
        now = current[row[key]]
        fields = {field for field in row if row[field] != now[field]}
        if fields:
            changed[row[key]] = sorted(fields)
    if key == "evidence_id":
        assert not changed
    elif path.endswith("SRC_source_register.csv"):
        assert changed == {
            "wet_potential_distribution_china_ml_2023": ["vars_extracted"]
        }
    else:
        assert set(changed) == {
            "wolka2018_swc_ssa_meta",
            "watershed_restoration_targets_hydro_2022",
            "excessive_afforestation_arid_china_2010",
        }
        assert all(fields == ["note", "status"] for fields in changed.values())
    preservation[path] = {
        "baseline_rows": len(old),
        "current_rows": len(current),
        "changes_to_prior_rows": changed,
    }
for path in [
    "pipeline/metrics/review_log.csv",
    "schema/registers/FAM_family_registry.csv",
]:
    assert baseline(path) == (ROOT / path).read_bytes()
for path in (ROOT / "schema/recipes").glob("*/T4_suitability_mappings.csv"):
    assert baseline(path.relative_to(ROOT)) == path.read_bytes()
sources = {r["source_id"]: r for r in rows("schema/registers/SRC_source_register.csv")}
assert all(
    sources[unit["source_id"]]["extraction_status"] == "in_progress" for unit in units
)
priority = json.loads((HERE / "parity/priority_review_batch.json").read_text())
assert len(priority["items"]) == 6
assert all(item["evidence_id"] in live for item in priority["items"])
result = {
    "new_active_unapproved_t4_claims": len(units),
    "native_claim_and_support_anchors": anchors,
    "human_approvals": 0,
    "changed_runtime_mappings": 0,
    "priority_review_records": 6,
    "preservation": preservation,
}
(HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
