"""Generated docs files are a pure function of their inputs.

They used to stamp the build time and the commit sha, so every PR rewrote them and every
other open PR then conflicted on them. Two builds of the same inputs, under a different
"HEAD", must give the same bytes.
"""

import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from nbs_ruralscan.runtime import scorecard
from nbs_ruralscan.schema_tools import generate, review_exports, table_progress

SCHEMA = Path(__file__).resolve().parents[1] / "schema"
STAMPS = {"timestamp", "git_commit", "built", "built_at", "source_commit", "history"}

WRITERS = {
    "progress.json": lambda dest: generate.generate_progress_report(SCHEMA, dest=dest),
    "table_progress.json": lambda dest: table_progress.write(SCHEMA, dest=dest),
    "scorecard.json": lambda dest: scorecard.write(SCHEMA, dest=dest),
    "decisions.json": lambda dest: review_exports.write_decisions(
        dest=dest,
        exports_dir=SCHEMA.parent / "docs/review/exports",
        batch_dir=SCHEMA.parent / "docs/review",
    ),
}


@pytest.mark.parametrize("name", sorted(WRITERS))
def test_same_inputs_same_bytes_whatever_the_head(name, tmp_path, monkeypatch):
    write = WRITERS[name]
    real_run = subprocess.run

    def fake_head(sha):
        def run(args, *a, **k):
            if list(args[:2]) == ["git", "rev-parse"]:
                return SimpleNamespace(stdout=sha, returncode=0)
            return real_run(args, *a, **k)

        return run

    first, second = tmp_path / "a" / name, tmp_path / "b" / name
    monkeypatch.setattr(subprocess, "run", fake_head("1111111"))
    assert write(first) == [first]
    monkeypatch.setattr(subprocess, "run", fake_head("2222222"))
    assert write(second) == [second]
    assert first.read_bytes() == second.read_bytes()
    assert write(second) == []  # rebuilding unchanged inputs touches nothing

    data = json.loads(first.read_text(encoding="utf-8"))
    assert not STAMPS & set(data)
    assert not STAMPS & set(data.get("build") or {})
