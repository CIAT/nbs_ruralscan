"""The DOI<->citation gate (schema_tools/verify_metadata.check) must fail the build
when a pending acquisition-queue row carries a DOI that isn't doi_verified=true — a
wrong DOI fetches the wrong PDF -> extraction contamination. Offline (no network)."""

import csv

from nbs_ruralscan.schema_tools import verify_metadata

_COLS = ["source_id", "status", "doi", "doi_verified", "citation"]


def _write_queue(tmp_path, rows):
    p = tmp_path / "acquisition_queue.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=_COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in _COLS})
    return p


def _run_check(tmp_path, monkeypatch, rows):
    monkeypatch.setattr(verify_metadata, "QUEUE", _write_queue(tmp_path, rows))
    return verify_metadata.check()


def test_verified_doi_passes(tmp_path, monkeypatch):
    rows = [
        {"source_id": "a", "status": "pending", "doi": "10.1/x", "doi_verified": "true"}
    ]
    assert _run_check(tmp_path, monkeypatch, rows) == 0


def test_unverified_doi_fails(tmp_path, monkeypatch):
    rows = [
        {
            "source_id": "a",
            "status": "pending",
            "doi": "10.1/x",
            "doi_verified": "false",
        }
    ]
    assert _run_check(tmp_path, monkeypatch, rows) == 1


def test_missing_doi_verified_flag_fails(tmp_path, monkeypatch):
    # DOI present but never verified (blank flag) is exactly the pre-fix defect.
    rows = [
        {"source_id": "a", "status": "pending", "doi": "10.1/x", "doi_verified": ""}
    ]
    assert _run_check(tmp_path, monkeypatch, rows) == 1


def test_blank_doi_is_ignored(tmp_path, monkeypatch):
    # No DOI -> acquire by title -> nothing to verify.
    rows = [{"source_id": "a", "status": "pending", "doi": "", "doi_verified": ""}]
    assert _run_check(tmp_path, monkeypatch, rows) == 0


def test_non_pending_rows_ignored(tmp_path, monkeypatch):
    # Already-acquired rows are out of scope for the gate.
    rows = [
        {"source_id": "a", "status": "acquired", "doi": "10.1/x", "doi_verified": ""}
    ]
    assert _run_check(tmp_path, monkeypatch, rows) == 0


def test_real_queue_is_clean():
    # The committed queue must pass the gate (regression guard for the 2026-08 fix).
    assert verify_metadata.check() == 0
