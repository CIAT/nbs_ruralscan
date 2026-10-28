import csv
import json

import pytest
from nbs_ruralscan.schema_tools.review_notes import (
    evidence_fingerprint,
    load_review_notes,
)


def test_audit_notes_pin_semantics_and_never_approve(tmp_path):
    row = dict(
        evidence_id="e",
        source_id="s",
        page="1",
        variable="slope",
        quote="Slope",
        relationship='{"abs_max":20}',
        context="{}",
        reviewer_ok="false",
    )
    ev = tmp_path / "schema/registers/EV_evidence_register.csv"
    ev.parent.mkdir(parents=True)

    def write():
        with ev.open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)

    write()
    path = (
        tmp_path / "pipeline/t4_audit/forest_restoration/first_pass_review_notes.json"
    )
    path.parent.mkdir(parents=True)
    note = dict(
        finding="Hold",
        intended_use="Reference",
        remaining_decision="Resolve scope",
        source_check="PDF p1",
        evidence_sha256=evidence_fingerprint(row),
    )
    path.write_text(json.dumps({"e": note}))
    assert load_review_notes(tmp_path) == {"e": note}
    row["relationship"] = '{"abs_max":10}'
    write()
    with pytest.raises(ValueError, match="stale"):
        load_review_notes(tmp_path)
    assert "true" not in ev.read_text()
