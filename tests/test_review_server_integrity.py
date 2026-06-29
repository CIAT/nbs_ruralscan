"""Review-server startup integrity check — catches the Windows cp1252/CRLF register
corruption (#123) BEFORE Apply fails with a cryptic codec error."""

from nbs_ruralscan.schema_tools import review_server as RS


def test_clean_utf8_lf_is_ok(tmp_path):
    p = tmp_path / "EV.csv"
    p.write_text(
        "evidence_id,quote\ne1,café plantation\n", encoding="utf-8"
    )  # UTF-8 + LF
    assert RS.integrity_problems([p]) == []


def test_latin1_byte_flagged(tmp_path):
    p = tmp_path / "EV.csv"
    p.write_bytes(b"evidence_id,quote\ne1,caf\xe7 plantation\n")  # 0xe7 = cp1252 'ç'
    probs = RS.integrity_problems([p])
    assert len(probs) == 1
    assert "EV.csv" in probs[0] and "0xe7" in probs[0] and "git restore" in probs[0]


def test_crlf_flagged(tmp_path):
    p = tmp_path / "review_log.csv"
    p.write_bytes(b"date,id\r\n2026,e1\r\n")  # CRLF
    probs = RS.integrity_problems([p])
    assert len(probs) == 1
    assert "CRLF" in probs[0]


def test_missing_file_skipped(tmp_path):
    assert RS.integrity_problems([tmp_path / "nope.csv"]) == []
