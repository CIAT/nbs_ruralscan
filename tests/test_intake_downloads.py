"""Intake of human/browser-downloaded PDFs (scripts/intake-downloads.py)."""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "intake", ROOT / "scripts" / "intake-downloads.py"
)
assert _spec and _spec.loader
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

CIT = "Smith, J. (2020). Contour ridges raise maize yields in semi-arid Zimbabwe. Field Crops Research."


def _pdf(path: Path, text: str) -> Path:
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), text)
    doc.save(path)
    return path


def _queue(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(
            [
                "source_id",
                "citation",
                "status",
                "blocker",
                "note",
                "title_verified",
                "target_library_path",
            ]
        )
        w.writerow(
            [
                "smith_2020",
                CIT,
                "pending",
                "OA (websearch:researchgate/unverified) — HUMAN CHECK",
                "",
                "",
                "lib/x/smith_2020.pdf",
            ]
        )


def test_title_check(tmp_path):
    ok, _ = intake.title_check(
        _pdf(
            tmp_path / "a.pdf",
            "Contour ridges raise maize yields in semi-arid Zimbabwe",
        ),
        CIT,
    )
    bad, _ = intake.title_check(
        _pdf(tmp_path / "b.pdf", "An unrelated paper about coastal fisheries"), CIT
    )
    assert ok and not bad


def test_files_a_matching_download(tmp_path, monkeypatch):
    dl, lib = tmp_path / "dl", tmp_path / "lib_root"
    dl.mkdir()
    _pdf(
        dl / "smith_2020.pdf", "Contour ridges raise maize yields in semi-arid Zimbabwe"
    )
    _pdf(dl / "unrelated.pdf", "nothing")
    q = tmp_path / "queue.csv"
    _queue(q)
    monkeypatch.setattr(intake, "QUEUE", q)
    monkeypatch.setattr(intake, "CORPUS", tmp_path / "corpus")
    monkeypatch.setattr(intake._H, "library_root", lambda: lib)
    assert intake.main(["--dir", str(dl)]) == 0
    assert (tmp_path / "corpus" / "smith_2020.pdf").exists()
    assert (lib / "lib/x/smith_2020.pdf").exists()
    assert (dl / "nbs_ingested" / "smith_2020.pdf").exists() and (
        dl / "unrelated.pdf"
    ).exists()
    row = next(csv.DictReader(q.open(encoding="utf-8")))
    assert (
        row["status"] == "acquired"
        and row["title_verified"] == "true"
        and row["blocker"] == ""
    )


def test_wrong_file_is_refused(tmp_path, monkeypatch):
    dl = tmp_path / "dl"
    dl.mkdir()
    _pdf(dl / "smith_2020.pdf", "An unrelated paper about coastal fisheries")
    q = tmp_path / "queue.csv"
    _queue(q)
    monkeypatch.setattr(intake, "QUEUE", q)
    monkeypatch.setattr(intake, "CORPUS", tmp_path / "corpus")
    monkeypatch.setattr(intake._H, "library_root", lambda: tmp_path / "lib")
    assert intake.main(["--dir", str(dl)]) == 1
    assert not (tmp_path / "corpus" / "smith_2020.pdf").exists()
    assert next(csv.DictReader(q.open(encoding="utf-8")))["status"] == "pending"
