"""Verify the consolidated ITTO screening against the hydrated source."""

import csv
import hashlib
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
summary = json.loads((AUDIT / "validation.json").read_text())
pdf = ROOT / ".cache/corpus/itto_flr_guidelines_ps24_2020.pdf"
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == summary["pdf_sha256"]
doc = fitz.open(pdf)
assert len(doc) == 142
coverage = list(csv.DictReader((AUDIT / "page_coverage.csv").open()))
assert len(coverage) == 142
assert {int(row["pdf_page"]) for row in coverage} == set(range(1, 143))
new = json.loads((AUDIT / "new_page_text.json").read_text())
assert new["sha256"] == summary["pdf_sha256"]
assert len(new["pages"]) == summary["new_page_records"] == 93
new_pages = {row["pdf_page"]: row["native_text"] for row in new["pages"]}
for row in coverage:
    page = int(row["pdf_page"])
    if row["prior_audit"]:
        old = json.loads((ROOT / row["prior_audit"]).read_text())
        records = old.get(
            "pages", old.get("table_pages", old.get("reviewed_pages", []))
        )
        anchors = [
            item["native_text"]
            for item in records
            if item.get("pdf_page", item.get("page")) == page
        ]
        assert len(anchors) == 1 and anchors[0] == doc[page - 1].get_text()
    else:
        assert new_pages[page] == doc[page - 1].get_text()
    assert row["disposition"]
claims = json.loads((AUDIT / "candidate_inventory.json").read_text())
assert len(claims) == summary["candidate_records"] == 14
assert len({row["candidate_id"] for row in claims}) == 14
for claim in claims:
    assert claim["quote"] in doc[claim["pdf_page"] - 1].get_text()
    assert not claim.get("reviewer_ok", False)
    assert claim.get("evidence_id") is None
cases = list(csv.DictReader((AUDIT / "case_dispositions.csv").open()))
assert {int(row["case"]) for row in cases} == set(range(1, 19))
case_pages = []
for case in cases:
    case_pages.extend(range(int(case["pdf_start"]), int(case["pdf_end"]) + 1))
assert len(case_pages) == len(set(case_pages)) == 49
assert set(case_pages) == set(range(86, 135))
tools = list(csv.DictReader((AUDIT / "table1_inventory.csv").open()))
assert len(tools) == 26
objects = list(csv.DictReader((AUDIT / "table_figure_inventory.csv").open()))
assert sum(row["object"].startswith("Table") for row in objects) == 7
assert sum(row["object"].startswith("Figure") for row in objects) == 4
assert set(summary["resolved_ocr_flags"]) == {"81", "135", "140", "141"}
assert summary["new_ev_rows"] == 0 and not summary["full_extraction_complete"]
print(
    "PASS: 142 pages; 18 cases; 26 tool entries; 14 quote anchors; 7 tables/4 figures."
)
