"""Review exports must retain new notes and invalidate approvals on hold."""

import csv

from nbs_ruralscan.schema_tools import review


def test_review_events_and_true_replays(tmp_path, monkeypatch):
    ev, log = tmp_path / "EV.csv", tmp_path / "log.csv"
    monkeypatch.setattr(review, "EV", ev)
    monkeypatch.setattr(review, "LOG", log)
    fields = ["evidence_id", "source_id", "reviewer_ok", "review_state", "attribution"]
    with ev.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerow(
            dict(
                evidence_id="ev1",
                source_id="source",
                reviewer_ok="true",
                review_state="",
                attribution="",
            )
        )

    def apply(decision, note, reviewer="Pete Steward"):
        review.apply_decisions(
            {"ev1": {"decision": decision, "note": note, "reviewer": reviewer}}
        )

    def rows():
        with log.open(newline="") as f:
            return list(csv.DictReader(f))

    apply("ok", "Already approved, but new reviewer note")
    assert len(rows()) == 1
    snapshot = ev.read_bytes(), log.read_bytes()
    apply("ok", "Already approved, but new reviewer note")
    assert (ev.read_bytes(), log.read_bytes()) == snapshot
    apply("flag", "Insufficient context")
    with ev.open(newline="") as f:
        assert next(csv.DictReader(f))["reviewer_ok"] == "false"
    apply("flag", "New context question")
    assert len(rows()) == 3
    assert rows()[-1]["note"] == "New context question"
    apply("ok", "Resolved")
    apply("ok", "Resolved", reviewer="Namita-J")
    assert len(rows()) == 5
    apply("drop", "Site description")
    snapshot = ev.read_bytes(), log.read_bytes()
    apply("drop", "Site description")
    assert (ev.read_bytes(), log.read_bytes()) == snapshot
