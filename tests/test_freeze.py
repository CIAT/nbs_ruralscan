"""Tests for corpus snapshotting and manifest verification."""

from __future__ import annotations

import json
from pathlib import Path
import zipfile

from nbs_ruralscan.freeze import (
    create_manifest_and_snapshot,
    get_sha256,
    verify_manifest,
)


def test_freeze_lifecycle(tmp_path: Path):
    # Setup mock folders
    registers_dir = tmp_path / "registers"
    registers_dir.mkdir()
    cache_dir = tmp_path / "ingest"
    cache_dir.mkdir()

    # Create mock register files
    reg_file = registers_dir / "EV_evidence_register.json"
    reg_file.write_text('{"mock": "register"}', encoding="utf-8")

    # Create mock index files
    idx_file = cache_dir / "index_1.json"
    idx_file.write_text('{"mock": "index"}', encoding="utf-8")

    manifest_path = tmp_path / "run_manifest.json"
    zip_path = tmp_path / "run_snapshot.zip"

    # Checksum verification helper check
    expected_reg_sha = get_sha256(reg_file)
    expected_idx_sha = get_sha256(idx_file)

    # Run creation
    exit_code = create_manifest_and_snapshot(
        manifest_path=manifest_path,
        zip_path=zip_path,
        registers_dir=registers_dir,
        cache_dir=cache_dir,
    )

    assert exit_code == 0
    assert manifest_path.exists()
    assert zip_path.exists()

    # Check manifest contents
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "timestamp" in data
    assert "git_commit" in data
    assert "files" in data
    assert data["files"].get(str(reg_file)) == expected_reg_sha
    assert data["files"].get(str(idx_file)) == expected_idx_sha

    # Path relative keys in files dict
    # Since find_files searches using registers_dir and cache_dir relative paths, let's verify keys exist
    files_keys = list(data["files"].keys())
    assert any("EV_evidence_register.json" in k for k in files_keys)
    assert any("index_1.json" in k for k in files_keys)

    # Verify ZIP file contains files
    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        assert any("EV_evidence_register.json" in name for name in namelist)
        assert any("index_1.json" in name for name in namelist)


def test_verify_manifest_success_and_failures(tmp_path: Path, monkeypatch):
    # Create files relative to current working directory of the process
    # Let's mock/monkeypatch CWD or pass absolute/relative paths carefully.
    # verify_manifest opens paths exactly as written in the manifest.
    # Let's create a custom manifest using paths relative to project root, or let's use monkeypatch to change CWD to tmp_path!
    monkeypatch.chdir(tmp_path)

    registers_dir = Path("registers")
    registers_dir.mkdir()
    cache_dir = Path("ingest")
    cache_dir.mkdir()

    f1 = registers_dir / "EV_evidence_register.json"
    f1.write_text("hello", encoding="utf-8")
    f2 = cache_dir / "index_1.json"
    f2.write_text("world", encoding="utf-8")

    manifest_path = Path("run_manifest.json")

    # 1. Create valid manifest
    exit_code = create_manifest_and_snapshot(
        manifest_path=manifest_path,
        zip_path=None,
        registers_dir=registers_dir,
        cache_dir=cache_dir,
    )
    assert exit_code == 0

    # 2. Verify should succeed
    assert verify_manifest(manifest_path) == 0

    # 3. Modify a file -> verification failure (checksum mismatch)
    f1.write_text("corrupted", encoding="utf-8")
    assert verify_manifest(manifest_path) == 1

    # Restore f1
    f1.write_text("hello", encoding="utf-8")
    assert verify_manifest(manifest_path) == 0

    # 4. Remove a file -> verification failure (missing file)
    f2.unlink()
    assert verify_manifest(manifest_path) == 1
