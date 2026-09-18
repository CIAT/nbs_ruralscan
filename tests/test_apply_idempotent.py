"""Regression: replaying decisions must be a no-op (2026-09-18).

Apply and the submit flow both replay the FULL decisions store by design (the store is the
durable review record). Without the `_already_applied` guard every replay re-logged every
decision into review_log and prepended another [dropped/reviewed/...] tag onto attribution
(found: 445 duplicate log rows, 238 rows with stacked tags). A re-opened row must still be
re-decidable — reopen clears review_state / restores the flag, so the guard passes it.
"""

import csv

from nbs_ruralscan.schema_tools import review


def _setup(tmp_path, monkeypatch):
    ev = tmp_path / "EV.csv"
    ev.write_text(
        "evidence_id,source_id,attribution,review_state,reviewer_ok,claim_scope,taxon\n"
        "e1,s1,[VERIFY-FLAG mismatch: off] x,,,practice_technology,\n"
        "e2,s2,note,,,practice_technology,\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(review, "EV", ev)
    monkeypatch.setattr(review, "LOG", tmp_path / "review_log.csv")
    monkeypatch.setattr(review, "WORKLIST", tmp_path / "worklist.csv")
    return ev, tmp_path / "review_log.csv"


def _log_rows(log):
    return list(csv.DictReader(log.open(encoding="utf-8")))


def test_replay_is_noop(tmp_path, monkeypatch):
    ev, log = _setup(tmp_path, monkeypatch)
    decisions = {"e1": "ok", "e2": {"decision": "drop", "reason": "off_scope"}}

    first = review.apply_decisions(decisions, reviewer="tester")
    assert first["ok"] == 1 and first["dropped"] == 1
    assert len(_log_rows(log)) == 2

    # replay the exact same store — nothing new applied, nothing re-logged, no stacked tags
    second = review.apply_decisions(decisions, reviewer="tester")
    assert second["ok"] == 0 and second["dropped"] == 0
    assert len(_log_rows(log)) == 2
    rows = {r["evidence_id"]: r for r in csv.DictReader(ev.open(encoding="utf-8"))}
    assert rows["e1"]["attribution"].count("[reviewed") == 1
    assert rows["e2"]["attribution"].count("[dropped") == 1


def test_reopened_row_is_redecidable(tmp_path, monkeypatch):
    ev, log = _setup(tmp_path, monkeypatch)
    review.apply_decisions(
        {"e2": {"decision": "drop", "reason": "off_scope"}}, "tester"
    )

    # simulate reopen: review_state cleared → a new drop must apply + log again
    rows = list(csv.DictReader(ev.open(encoding="utf-8")))
    for r in rows:
        if r["evidence_id"] == "e2":
            r["review_state"] = ""
    with ev.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    res = review.apply_decisions(
        {"e2": {"decision": "drop", "reason": "off_scope"}}, "tester"
    )
    assert res["dropped"] == 1
    assert len(_log_rows(log)) == 2
