import csv
import hashlib
import json

import pytest

from nbs_ruralscan.schema_tools.clarifications import build, record


def setup(root):
    def write(name, rows):
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    ev = dict(
        evidence_id="one",
        nbs_id="agroforestry",
        use_role="structural_suitability",
        review_state="",
        source_id="paper",
        variable="slope",
        page="2",
        quote="Lower slopes preferred",
        claim_scope="practice_technology",
        relationship="{}",
        reviewer_ok="true",
    )
    write(
        "schema/registers/EV_evidence_register.csv", [ev, dict(ev, evidence_id="two")]
    )
    write(
        "pipeline/metrics/review_log.csv",
        [
            dict(
                evidence_id=e,
                reviewer="Pete",
                decision="query",
                note="Explain direction",
                reason="unclear",
            )
            for e in ["one", "two"]
        ],
    )
    p = root / "pipeline/review"
    p.mkdir(parents=True)
    answers = {
        e: dict(
            evidence_id=e,
            reviewer="Pete",
            note="Explain direction",
            status="resolved",
            resolution="Lower means more suitable; no numeric cutoff.",
            resolution_checks=[
                dict(
                    evidence_id=e,
                    field="quote",
                    sha256=hashlib.sha256(ev["quote"].encode()).hexdigest(),
                )
            ],
        )
        for e in ["one", "two"]
    }
    p = root / "pipeline/t4_audit/agroforestry/review_followups.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps(answers))


def test_shared_answer_acceptance_does_not_change_evidence(tmp_path):
    setup(tmp_path)
    ev = tmp_path / "schema/registers/EV_evidence_register.csv"
    before = ev.read_bytes()
    issues = build(tmp_path)
    assert len(issues) == 1 and len(issues[0]["records"]) == 2
    g = issues[0]
    assert g["status"] == "answer_ready"
    event = record(
        tmp_path,
        dict(
            issue_id=g["id"],
            fingerprint=g["fingerprint"],
            reviewer="Pete",
            action="accept",
        ),
    )
    assert event["evidence_ids"] == ["one", "two"]
    assert build(tmp_path)[0]["status"] == "resolved"
    assert ev.read_bytes() == before
    record(
        tmp_path,
        dict(
            issue_id=g["id"],
            fingerprint=g["fingerprint"],
            reviewer="Pete",
            action="reply",
            note="Still unclear",
        ),
    )
    assert build(tmp_path)[0]["status"] == "needs_investigation"
    assert len(build(tmp_path)[0]["history"]) == 2


def test_changed_evidence_invalidates_answer_and_acceptance(tmp_path):
    setup(tmp_path)
    g = build(tmp_path)[0]
    p = tmp_path / "schema/registers/EV_evidence_register.csv"
    p.write_text(
        p.read_text().replace("Lower slopes preferred", "Higher slopes preferred")
    )
    assert build(tmp_path)[0]["status"] == "needs_investigation"
    with pytest.raises(ValueError, match="changed"):
        record(
            tmp_path,
            dict(
                issue_id=g["id"],
                fingerprint=g["fingerprint"],
                reviewer="Pete",
                action="accept",
            ),
        )
    g = build(tmp_path)[0]
    with pytest.raises(ValueError, match="complete answer"):
        record(
            tmp_path,
            dict(
                issue_id=g["id"],
                fingerprint=g["fingerprint"],
                reviewer="Pete",
                action="accept",
            ),
        )


def test_reply_requires_author_and_note(tmp_path):
    setup(tmp_path)
    g = build(tmp_path)[0]
    with pytest.raises(ValueError):
        record(
            tmp_path,
            dict(
                issue_id=g["id"],
                fingerprint=g["fingerprint"],
                action="reply",
                reviewer="Pete",
                note="",
            ),
        )


def test_explicit_judgement_request_is_not_inferred_or_autoaccepted(tmp_path):
    setup(tmp_path)
    p = tmp_path / "pipeline/t4_audit/agroforestry/review_followups.json"
    data = json.loads(p.read_text())
    data["one"]["status"] = "needs_judgement"
    p.write_text(json.dumps(data))
    g = build(tmp_path)[0]
    assert g["status"] == "needs_judgement"
    with pytest.raises(ValueError, match="complete answer"):
        record(
            tmp_path,
            dict(
                issue_id=g["id"],
                fingerprint=g["fingerprint"],
                reviewer="Pete",
                action="accept",
            ),
        )
