"""Review refresh publishes a complete artifact set without full corpus validation."""

import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from nbs_ruralscan.schema_tools import generate, publication


ROOT = Path(__file__).resolve().parents[1]


def fingerprint(root):
    return {
        p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


def outputs(root):
    return [
        root / "schema/registers/EV_evidence_register.json",
        root / "docs/dashboard_data.json",
        root / "docs/progress.json",
    ]


def sparse_snapshot(root):
    registers = root / "schema/registers"
    registers.mkdir(parents=True)
    (registers / "EV_evidence_register.csv").write_text(
        "evidence_id,source_id,reviewer_ok,review_state,attribution\n"
        "one,paper,false,,[VERIFY-FLAG mismatch: reopened]\n"
    )
    (registers / "SRC_source_register.csv").write_text(
        "source_id,nbs_ids,extraction_status\npaper,agroforestry,pending\n"
    )
    for p in outputs(root):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"old":true}\n')
    return root


def forbid(*args, **kwargs):
    raise AssertionError("Review refresh must not invoke full validation/quarantine")


def test_refresh_renderer_failure_preserves_all_artifacts(tmp_path, monkeypatch):
    root = sparse_snapshot(tmp_path)
    before = fingerprint(root)
    monkeypatch.setattr(generate, "validate_inputs", forbid)
    monkeypatch.setattr(generate, "quarantine_inputs", forbid)

    def fail(*args, **kwargs):
        raise OSError("progress rendering failed")

    monkeypatch.setattr(generate, "generate_progress_report", fail)
    with pytest.raises(OSError, match="progress rendering failed"):
        generate.refresh_review_state(root / "schema")
    assert fingerprint(root) == before


@pytest.mark.parametrize("after_replace", [False, True])
def test_refresh_second_install_failure_restores_artifacts(
    tmp_path, monkeypatch, after_replace
):
    root = sparse_snapshot(tmp_path)
    before = fingerprint(root)
    replace = publication.os.replace
    count = 0

    def fail(source, destination):
        nonlocal count
        if destination in outputs(root):
            count += 1
            if count == 2:
                if after_replace:
                    replace(source, destination)
                    raise KeyboardInterrupt("interrupted after dashboard replacement")
                raise OSError("dashboard replacement failed")
        return replace(source, destination)

    monkeypatch.setattr(publication.os, "replace", fail)
    with pytest.raises(KeyboardInterrupt if after_replace else OSError):
        generate.refresh_review_state(root / "schema")
    assert fingerprint(root) == before


def test_refresh_without_source_register_keeps_progress_untouched(tmp_path):
    root = sparse_snapshot(tmp_path)
    (root / "schema/registers/SRC_source_register.csv").unlink()
    progress = outputs(root)[2]
    before = progress.read_bytes()
    assert generate.refresh_review_state(root / "schema") is None
    assert progress.read_bytes() == before
    progress.unlink()
    assert generate.refresh_review_state(root / "schema") is None
    assert not progress.exists()


def test_real_refresh_matches_previous_outputs_and_repeat_is_noop(
    tmp_path, monkeypatch
):
    baseline = tmp_path / "previous"
    names = (
        subprocess.check_output(
            [
                "git",
                "ls-files",
                "-z",
                "schema",
                "docs",
                "pipeline",
                "methodology",
                "reference",
            ],
            cwd=ROOT,
        )
        .decode()
        .split("\0")
    )
    for name in filter(None, names):
        target = baseline / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    evidence = baseline / "schema/registers/EV_evidence_register.csv"
    with evidence.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    assert fields
    rows[0]["reviewer_ok"] = "false"
    rows[0]["attribution"] = "[VERIFY-FLAG mismatch: refresh rehearsal]"
    with evidence.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    candidate = tmp_path / "staged"
    shutil.copytree(baseline, candidate)

    # Generated outputs no longer read the clock, so no frozen time is needed.
    monkeypatch.setattr(generate, "validate_inputs", forbid)
    monkeypatch.setattr(generate, "quarantine_inputs", forbid)
    # Exact pre-migration call sequence, against an independent snapshot.
    evidence.with_suffix(".json").write_text(
        json.dumps(generate._csv_to_rows(evidence), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    generate.generate_dashboard_data(baseline / "schema")
    generate.generate_progress_report(baseline / "schema")
    assert generate.refresh_review_state(candidate / "schema") is None
    assert fingerprint(candidate) == fingerprint(baseline)
    before = {
        p: (p.read_bytes(), p.stat().st_mtime_ns, p.stat().st_ino)
        for p in outputs(candidate)
    }
    assert generate.refresh_review_state(candidate / "schema") is None
    assert {
        p: (p.read_bytes(), p.stat().st_mtime_ns, p.stat().st_ino)
        for p in outputs(candidate)
    } == before
