#!/usr/bin/env python3
"""Verify the pinned migration inventory without copying or changing source data."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess


def main() -> None:
    folder = Path(__file__).resolve().parent
    repo = Path(
        subprocess.check_output(
            ["git", "-C", str(folder), "rev-parse", "--show-toplevel"], text=True
        ).strip()
    )
    baseline = json.loads((folder / "baseline.json").read_text())
    commit = baseline["source_commit"]

    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(repo), *args])

    expected = {}
    for line in git("ls-tree", "-r", "-l", commit).decode().splitlines():
        metadata, path = line.split("\t", 1)
        mode, _kind, blob, size = metadata.split()
        expected[path] = (mode, blob, size)
    with (folder / "source-inventory.csv").open(newline="") as stream:
        inventory = list(csv.DictReader(stream))
    observed = {
        row["source_path"]: (row["git_mode"], row["git_blob_sha"], row["bytes"])
        for row in inventory
    }
    assert len(observed) == len(inventory), "Duplicate source inventory paths"
    assert observed == expected, "Source inventory differs from pinned Git tree"

    with (folder / "table-ownership.csv").open(newline="") as stream:
        tables = list(csv.DictReader(stream))
    expected_tables = {
        p for p in expected if p.startswith("schema/") and p.endswith(".csv")
    }
    assert {row["source_path"] for row in tables} == expected_tables
    assert len(tables) == len(expected_tables), "Duplicate or missing table ownership"
    for row in tables:
        assert row["source_commit"] == commit
        payload = git("show", f"{commit}:{row['source_path']}")
        assert hashlib.sha256(payload).hexdigest() == row["sha256"], row["source_path"]
        parsed = list(csv.reader(payload.decode("utf-8-sig").splitlines()))
        assert parsed[0] == json.loads(row["headers_json"]), row["source_path"]
        assert len(parsed) - 1 == int(row["row_count"]), row["source_path"]

    with (folder / "first-import-manifest.csv").open(newline="") as stream:
        imports = list(csv.DictReader(stream))
    destinations = set()
    for row in imports:
        assert row["source_commit"] == commit
        assert row["source_path"] in expected
        payload = git("show", f"{commit}:{row['source_path']}")
        assert hashlib.sha256(payload).hexdigest() == row["sha256"], row["source_path"]
        destination = PurePosixPath(row["destination_path"])
        assert not destination.is_absolute() and ".." not in destination.parts
        key = (row["destination_repository"], str(destination))
        assert key not in destinations, f"Duplicate destination: {key}"
        destinations.add(key)
        assert row["approved_for_import"] == "false", "This is an unapproved proposal"
        assert row["authority_after_staging"] == "CIAT/nbs_ruralscan"
    with (folder / "scaffold-manifest.csv").open(newline="") as stream:
        scaffolds = list(csv.DictReader(stream))
    for row in scaffolds:
        source = PurePosixPath(row["source_path"])
        assert source.parts[0] == "drafts" and ".." not in source.parts
        payload = (folder / source).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == row["sha256"], source
        destination = PurePosixPath(row["destination_path"])
        assert not destination.is_absolute() and ".." not in destination.parts
        key = (row["destination_repository"], str(destination))
        assert key not in destinations, f"Duplicate destination: {key}"
        destinations.add(key)
        assert row["approved_for_import"] == "false"
    print(
        f"Verified {len(inventory)} source files, {len(tables)} tables, "
        f"{len(imports)} proposed imports against {commit} and "
        f"{len(scaffolds)} new documents. No import performed."
    )


if __name__ == "__main__":
    main()
