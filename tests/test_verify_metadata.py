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


def test_unreachable_crossref_never_blanks_a_doi(monkeypatch, tmp_path):
    """2026-10-16: a rate-limited sweep blanked 113 VALID DOIs, because every transport
    failure looked like 'this DOI does not resolve'. Only a definitive 404 may blank one."""
    from nbs_ruralscan.schema_tools import verify_metadata as vm

    queue = tmp_path / "queue.csv"
    queue.write_text(
        "source_id,citation,doi,status,doi_verified,note,title_verified\n"
        "a,Smith et al. (2020). A real paper.,10.1000/real,pending,,,\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(vm, "QUEUE", queue)
    monkeypatch.setattr(vm, "REPORT", tmp_path / "report.json")
    monkeypatch.setattr(vm, "_crossref", lambda doi: (None, "unreachable"))
    vm.verify()
    row = next(csv.DictReader(queue.open(encoding="utf-8")))
    assert row["doi"] == "10.1000/real", (
        "an unreachable lookup must leave the DOI alone"
    )
    assert "blanked" not in (row["note"] or "")


def test_a_404_still_blanks(monkeypatch, tmp_path):
    from nbs_ruralscan.schema_tools import verify_metadata as vm

    queue = tmp_path / "queue.csv"
    queue.write_text(
        "source_id,citation,doi,status,doi_verified,note,title_verified\n"
        "a,Smith et al. (2020). A real paper.,10.1000/dead,pending,,,\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(vm, "QUEUE", queue)
    monkeypatch.setattr(vm, "REPORT", tmp_path / "report.json")
    monkeypatch.setattr(vm, "_crossref", lambda doi: (None, "not_found"))
    vm.verify()
    row = next(csv.DictReader(queue.open(encoding="utf-8")))
    assert row["doi"] == ""
    assert "acquire by TITLE" in row["note"]
