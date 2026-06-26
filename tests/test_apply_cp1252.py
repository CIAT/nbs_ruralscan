"""Regression: apply_decisions must survive AND heal an EV register that was re-saved
as Windows ANSI (cp1252) — e.g. opened in Excel, turning a quote's 'ç'/'é' into raw
0xe7/0xe9 bytes that strict UTF-8 can't decode. This crashed QA "Apply decisions &
rebuild" on Windows with "'utf-8' codec can't decode byte 0xe7" (the encoding cousin of
the #104 CRLF bug).

review._read_evidence_register falls back to cp1252 (with a warning); the UTF-8 rewrite
then heals the file permanently — so the first successful apply fixes it for good.
"""

import csv

import pytest

from nbs_ruralscan.schema_tools import review


def test_apply_heals_cp1252_register(tmp_path, monkeypatch):
    ev = tmp_path / "EV.csv"
    content = (
        "evidence_id,source_id,attribution,review_state,reviewer_ok,quote\n"
        'e1,s1,note,,,"sécheresse"\n'  # é/ç -> 0xe9/0xe7 single bytes under cp1252
        "e2,s2,note,,,plain\n"
    )
    ev.write_bytes(content.encode("cp1252"))  # the Windows-ANSI corrupt state

    # sanity: this reproduces the original crash (strict UTF-8 can't read it)
    with pytest.raises(UnicodeDecodeError):
        ev.read_text(encoding="utf-8")

    monkeypatch.setattr(review, "EV", ev)
    monkeypatch.setattr(review, "LOG", tmp_path / "review_log.csv")
    monkeypatch.setattr(review, "WORKLIST", tmp_path / "worklist.csv")

    res = review.apply_decisions({"e1": "drop"}, reviewer="tester")
    assert res["dropped"] == 1

    # healed: the file is now valid UTF-8 with content intact
    text = ev.read_text(encoding="utf-8")
    assert "sécheresse" in text
    rows = {r["evidence_id"]: r for r in csv.DictReader(text.splitlines())}
    assert rows["e1"]["review_state"] == "dropped"
