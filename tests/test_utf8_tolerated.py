"""A register/log re-saved as Windows ANSI (cp1252) must READ, not crash the gate.

Namita hit "Apply failed (gate?): 'utf-8' codec can't decode byte 0xe7" — a stray cp1252
byte (ç) in her local review_log.csv, which the apply path only appends to (so it can't
heal it by rewriting). The gate now falls back UTF-8 → cp1252 instead of dying. #104's
encoding cousin.
"""

from nbs_ruralscan.schema_tools import generate


def test_csv_to_rows_tolerates_cp1252(tmp_path):
    bad = tmp_path / "review_log.csv"
    # 0xe7 = 'ç' in cp1252, an invalid UTF-8 continuation byte
    bad.write_bytes(b"evidence_id,quote\ne1,caf\xe7 plantation\n")
    # the original crash: strict UTF-8 can't read this
    import pytest

    with pytest.raises(UnicodeDecodeError):
        bad.read_text(encoding="utf-8")
    # the gate reads it anyway, decoding the byte as cp1252
    assert generate._csv_to_rows(bad) == [{"evidence_id": "e1", "quote": "cafç plantation"}]


def test_valid_utf8_still_reads(tmp_path):
    good = tmp_path / "x.csv"
    good.write_text("a,b\ncafé,1\n", encoding="utf-8")  # é as proper UTF-8
    rows = generate._csv_to_rows(good)
    assert rows == [{"a": "café", "b": 1}]
