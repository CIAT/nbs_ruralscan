"""Regression: apply_decisions must survive a ragged EV row (issue #104).

On Windows, git autocrlf rewrote the embedded LFs in multiline-quoted register cells to
CRLF on checkout, producing rows with more fields than the header. csv.DictReader puts the
overflow under a `None` restkey, and DictWriter then crashed with
"dict contains fields not in fieldnames: None", blocking QA "Apply decisions & rebuild".

The root cause is fixed in .gitattributes (`*.csv text eol=lf`); this guards the belt-and-
suspenders half — the apply-path writers use `extrasaction="ignore"`, so even a stray
`None` key never crashes the rebuild.
"""

import csv

from nbs_ruralscan.schema_tools import review


def test_apply_survives_ragged_row(tmp_path, monkeypatch):
    ev = tmp_path / "EV.csv"
    # header has 5 cols; row 2 has 6 → DictReader yields a None restkey on read.
    ev.write_text(
        "evidence_id,source_id,attribution,review_state,reviewer_ok\n"
        "e1,s1,some note,,\n"
        "e2,s2,note,,,OVERFLOW\n",  # ragged: extra field → {None: ['OVERFLOW']}
        encoding="utf-8",
    )
    monkeypatch.setattr(review, "EV", ev)
    monkeypatch.setattr(review, "LOG", tmp_path / "review_log.csv")
    monkeypatch.setattr(review, "WORKLIST", tmp_path / "worklist.csv")

    # drop e1 — must not raise despite e2's None-keyed overflow
    res = review.apply_decisions({"e1": "drop"}, reviewer="tester")
    assert res["dropped"] == 1

    rows = list(csv.DictReader(ev.open(encoding="utf-8")))
    by = {r["evidence_id"]: r for r in rows}
    assert by["e1"]["review_state"] == "dropped"
    # the None overflow was dropped on write (extrasaction="ignore"), not crashed on
    assert None not in rows[0]
    # writers emit LF, not CRLF (lineterminator="\n") — no Windows CRLF churn (#104 class)
    assert b"\r" not in ev.read_bytes()
    assert b"\r" not in (tmp_path / "review_log.csv").read_bytes()
