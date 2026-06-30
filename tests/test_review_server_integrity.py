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


def test_gitignored_bad_byte_gets_reencode_hint_not_restore(tmp_path):
    # decisions.json / .cache files are gitignored → git restore can't fix; hint must re-encode.
    p = tmp_path / ".cache" / "corpus" / "snap.txt"
    p.parent.mkdir(parents=True)
    p.write_bytes(b"web snapshot caf\xe7")
    probs = RS.integrity_problems([p])
    assert len(probs) == 1
    assert "0xe7" in probs[0]
    assert "re-encode" in probs[0] and "git restore" not in probs[0]


def test_decisions_json_self_heals_cp1252(tmp_path, monkeypatch):
    # a stray cp1252 byte in the gitignored decisions.json must NOT crash _load — self-heal it.
    store = tmp_path / "decisions.json"
    store.write_bytes(b'{"e1": {"alice": {"decision": "drop", "note": "caf\xe7"}}}')
    monkeypatch.setattr(RS, "STORE", store)
    data = RS._load()
    assert data["e1"]["alice"]["decision"] == "drop"
    store.read_text(encoding="utf-8")  # now valid UTF-8 (rewritten)


def test_pipeline_files_excludes_decisions_json():
    # decisions.json is self-healed by _load, so the blocking preflight list must omit it.
    assert all(p.name != "decisions.json" for p in RS._pipeline_text_files())
