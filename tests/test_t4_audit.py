"""Audit admits verified corrections without changing human approval history."""

import csv
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTINUATION = "ev_T4_soc_haile2024_continuation"


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / name)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def reports(tmp_path):
    runner = script("synthesise-recipe.py")
    for mode in ("draft", "approved"):
        result = runner.synthesise("agroforestry", approved_only=mode == "approved")
        folder = tmp_path / mode
        folder.mkdir()
        (folder / "report.json").write_text(
            json.dumps(
                {
                    "input_sha256": {},
                    "families": {key: asdict(value) for key, value in result.items()},
                }
            )
        )
    return tmp_path


def test_data_audit_retains_correction_and_human_status(reports, monkeypatch):
    audit = script("audit-t4-compilation.py")
    historical = ROOT / "docs/review/t4-pipeline-audit.html"
    before = historical.read_bytes()
    monkeypatch.setattr(
        "sys.argv", ["audit", "agroforestry", str(reports), "--data-only"]
    )
    audit.main()
    with (reports / "record_reconciliation.csv").open() as handle:
        rows = {r["evidence_id"]: r for r in csv.DictReader(handle)}
    row = rows[CONTINUATION]
    assert row["reviewer_ok"] == "false"
    assert row["final_disposition"] == "live_verified_source_completion"
    assert "human review status unchanged" in row["disposition_reason"]
    summary = json.loads((reports / "summary.json").read_text())
    assert summary["authorized_source_completions"] == [CONTINUATION]
    assert summary["all_records_accounted_for"]
    assert historical.read_bytes() == before


def test_report_cannot_authorize_unreviewed_live_link(reports, monkeypatch):
    audit = script("audit-t4-compilation.py")
    # Even a compiler report claiming completion cannot supply authorization.
    monkeypatch.setattr(audit, "validated_completions", lambda root: {})
    monkeypatch.setattr(
        "sys.argv", ["audit", "agroforestry", str(reports), "--data-only"]
    )
    with pytest.raises(ValueError, match="unapproved/dropped evidence"):
        audit.main()


def test_audit_revalidates_source_content_and_artifact(tmp_path):
    audit = script("audit-t4-compilation.py")
    for name in (
        "registers/EV_evidence_register.csv",
        "lookups/t4_numeric_compilation_policy.csv",
    ):
        target = tmp_path / "schema" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "schema" / name, target)
    assert CONTINUATION in audit.validated_completions(tmp_path)
    pdf = tmp_path / ".cache/corpus/haile_2024.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"different source artifact")
    with pytest.raises(ValueError, match="PDF changed"):
        audit.validated_completions(tmp_path)
    pdf.unlink()
    ev = tmp_path / "schema/registers/EV_evidence_register.csv"
    with ev.open() as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    assert fields is not None
    next(r for r in rows if r["evidence_id"] == CONTINUATION)["quote"] = (
        "Changed source claim"
    )
    with ev.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="Invalid or stale source completion"):
        audit.validated_completions(tmp_path)
