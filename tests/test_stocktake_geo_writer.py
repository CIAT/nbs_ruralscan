import csv
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/backfill_stocktake_geo.py"


def run(root, *flags):
    return subprocess.run(
        [sys.executable, SCRIPT, "--root", root, *flags],
        cwd=root.parent,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def source(tmp_path):
    src = tmp_path / "schema/registers/SRC_source_register.csv"
    src.parent.mkdir(parents=True)
    src.write_text(
        "source_id,citation,doi,study_country,region,aez,keep\n"
        "a,Grey title,https://doi.org/10.example/x,,,,unchanged\n"
        "b,  GREY Title  ,,,,,unchanged\n"
        "c,Grey title,,recorded,,,unchanged\n"
        "d,Grey title,,,Asia,,unchanged\n"
        "e,Grey title,,,,AEZ1,unchanged\n"
        "f,No match,,,,,unchanged\n",
        encoding="utf-8",
    )
    refs = tmp_path / "reference/stocktake"
    refs.mkdir(parents=True)
    (refs / "peer_reviewed_benchmarked.csv").write_text(
        "Geographic_Scope,doi_extracted,oa_title\nNational: India,10.example/x,Paper\nNational: Brazil,10.example/x,Later\n"
    )
    (refs / "grey_lit_benchmarked.csv").write_text(
        "Geography,Source_title\nNational: Haiti,Grey title\n"
    )
    return src


def test_relocation_preview_doi_precedence_and_repeated_write(tmp_path, source):
    before = source.read_bytes()
    dry = run(tmp_path, "--dry-run")
    assert dry.returncode == 0 and "would fill study_country on 2" in dry.stdout
    assert source.read_bytes() == before
    written = run(tmp_path)
    assert written.returncode == 0 and "filled study_country on 2" in written.stdout
    with source.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert [r["study_country"] for r in rows] == [
        "India",
        "Haiti",
        "recorded",
        "",
        "",
        "",
    ]
    assert [r["source_id"] for r in rows] == list("abcdef")
    assert all(r["keep"] == "unchanged" for r in rows)
    assert b"\r\n" not in source.read_bytes()
    stable = source.stat()
    assert "filled study_country on 0" in run(tmp_path).stdout
    assert source.stat().st_mtime_ns == stable.st_mtime_ns


def test_lookup_failure_cannot_touch_source_register(tmp_path, source):
    before = source.read_bytes()
    (tmp_path / "reference/stocktake/grey_lit_benchmarked.csv").write_text(
        'Geography,Source_title\n"broken'
    )
    assert run(tmp_path).returncode != 0
    assert source.read_bytes() == before


def test_missing_optional_benchmarks_and_header_only_source_survive(tmp_path, source):
    for path in (tmp_path / "reference/stocktake").glob("*.csv"):
        path.unlink()
    before = source.read_bytes()
    assert run(tmp_path).returncode == 0
    assert source.read_bytes() == before
    source.write_bytes(before.splitlines(keepends=True)[0])
    header = source.read_bytes()
    assert run(tmp_path).returncode == 0
    assert source.read_bytes() == header
