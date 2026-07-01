"""A non-UTF-8 byte in a register must fail with the FILENAME, not an opaque codec error.

Namita hit "Apply failed (gate?): 'utf-8' codec can't decode byte 0xe7" — a stray Latin-1
byte (ç) in a local file, with no clue which file. The reads now name the offender.
"""

import pytest

from nbs_ruralscan.schema_tools import generate


def test_csv_to_rows_names_the_bad_file(tmp_path):
    bad = tmp_path / "EV_evidence_register.csv"
    # 0xe7 = 'ç' in Latin-1, an invalid UTF-8 continuation byte
    bad.write_bytes(b"evidence_id,quote\ne1,caf\xe7 plantation\n")
    with pytest.raises(ValueError) as ei:
        generate._csv_to_rows(bad)
    msg = str(ei.value)
    assert "EV_evidence_register.csv" in msg  # names the file
    assert "0xe7" in msg  # names the byte
    assert "UTF-8" in msg


def test_valid_utf8_still_reads(tmp_path):
    good = tmp_path / "x.csv"
    good.write_text("a,b\ncafé,1\n", encoding="utf-8")  # é as proper UTF-8
    rows = generate._csv_to_rows(good)
    assert rows == [{"a": "café", "b": 1}]
