"""Synthetic manual-download intake: selected paths and bounded local recovery."""

import csv
from dataclasses import replace
from pathlib import Path
import shutil
import subprocess
import sys

import fitz
import pytest

from nbs_ruralscan.ingest import download_intake as intake
from nbs_ruralscan.schema_tools import publication

TITLE = "Contour ridges raise maize yields in semi-arid Zimbabwe"
CITATION = f"Smith (2020). {TITLE}. Field Crops Research."
COLS = [
    "source_id",
    "citation",
    "status",
    "blocker",
    "note",
    "title_verified",
    "target_library_path",
]


def pdf(path, text=TITLE):
    path.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open() as doc:
        doc.new_page().insert_text((72, 72), text)
        doc.save(path)


def setup(root, *, count=1):
    paths = intake.DownloadIntakePaths(
        root / "records/queue.csv", root / "cache", root / "downloads", root / "library"
    )
    paths.queue.parent.mkdir(parents=True)
    paths.downloads.mkdir()
    rows = []
    for index in range(count):
        sid = f"paper_{index}"
        rows.append(
            dict(
                zip(
                    COLS,
                    [
                        sid,
                        CITATION,
                        "pending",
                        "old blocker",
                        "old note",
                        "",
                        f"archive/{sid}.pdf",
                    ],
                )
            )
        )
        pdf(paths.downloads / f"{sid}.pdf")
    write_rows(paths.queue, rows)
    return paths


def write_rows(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_rows(paths):
    with paths.queue.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def inventory(root):
    return {
        str(p.relative_to(root)): (
            p.read_bytes(),
            p.stat().st_mode,
            p.stat().st_mtime_ns,
        )
        for p in root.rglob("*")
        if p.is_file()
    }


def targets(paths, sid="paper_0"):
    return [
        paths.corpus / f"{sid}.pdf",
        paths.library / f"archive/{sid}.pdf",
        paths.downloads / f"nbs_ingested/{sid}.pdf",
    ]


def run(paths, **kwargs):
    return intake.run_intake(paths, today="2026-11-06", **kwargs)


@pytest.mark.parametrize("keep", [False, True])
def test_success_preserves_original_semantics_and_outputs_queue_last(
    tmp_path, monkeypatch, keep
):
    paths = setup(tmp_path, count=2)
    original = {p.name: p.read_bytes() for p in paths.downloads.glob("*.pdf")}
    events = []
    link, replace_file = publication.os.link, publication.os.replace

    def record_link(src, dst):
        if Path(dst).is_relative_to(tmp_path):
            events.append(Path(dst))
        return link(src, dst)

    def record_replace(src, dst):
        if Path(dst).is_relative_to(tmp_path):
            events.append(Path(dst))
        return replace_file(src, dst)

    monkeypatch.setattr(publication.os, "link", record_link)
    monkeypatch.setattr(publication.os, "replace", record_replace)
    result = run(paths, keep=keep)
    assert result.returncode == 0 and len(result.done) == 2
    assert events[-1] == paths.queue
    assert len(events) == (5 if keep else 7)
    for row in read_rows(paths):
        assert row["status"] == "acquired" and row["title_verified"] == "true"
        assert row["blocker"] == "" and row["note"].startswith(
            "old note | acquired 2026-11-06"
        )
        name = row["source_id"] + ".pdf"
        assert (paths.corpus / name).read_bytes() == original[name]
        assert (paths.library / "archive" / name).read_bytes() == original[name]
        assert (paths.downloads / name).exists() == keep
        assert (paths.downloads / "nbs_ingested" / name).exists() != keep


@pytest.mark.parametrize("existing", [False, True])
def test_dry_run_validates_without_selected_writes_or_removals(tmp_path, existing):
    paths = setup(tmp_path)
    if existing:
        for target in targets(paths):
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(paths.downloads / "paper_0.pdf", target)
    before = inventory(tmp_path)
    result = run(paths, dry_run=True)
    assert result.returncode == 0 and result.done
    assert inventory(tmp_path) == before


@pytest.mark.parametrize("collision", [0, 1, 2])
def test_existing_different_copy_is_held_without_mutating_any_output(
    tmp_path, collision
):
    paths = setup(tmp_path)
    target = targets(paths)[collision]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"previous retained artifact")
    before = inventory(tmp_path)
    result = run(paths)
    assert result.returncode == 1 and "artifact differs" in result.bad[0]
    assert inventory(tmp_path) == before


def test_identical_readonly_copies_remain_unchanged(tmp_path):
    paths = setup(tmp_path)
    saved = {}
    for target in targets(paths):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths.downloads / "paper_0.pdf", target)
        target.chmod(0o444)
        saved[target] = (
            target.read_bytes(),
            target.stat().st_mode,
            target.stat().st_mtime_ns,
        )
    assert run(paths).returncode == 0
    assert {
        p: (p.read_bytes(), p.stat().st_mode, p.stat().st_mtime_ns) for p in saved
    } == saved


@pytest.mark.parametrize("position", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("after", [False, True])
def test_create_only_failure_restores_batch_and_keeps_all_originals(
    tmp_path, monkeypatch, position, after
):
    paths = setup(tmp_path, count=2)
    before = inventory(tmp_path)
    target = (targets(paths, "paper_0") + targets(paths, "paper_1"))[position]
    link = publication.os.link

    def fail(src, dst):
        if Path(dst) == target:
            if after:
                link(src, dst)
            raise OSError("fixture link failure")
        return link(src, dst)

    monkeypatch.setattr(publication.os, "link", fail)
    with pytest.raises(OSError, match="fixture link failure"):
        run(paths)
    assert inventory(tmp_path) == before


@pytest.mark.parametrize("after", [False, True])
def test_queue_failure_rolls_back_new_copies_across_multiple_downloads(
    tmp_path, monkeypatch, after
):
    paths = setup(tmp_path, count=2)
    before = inventory(tmp_path)
    replace_file = publication.os.replace
    hit = False

    def fail(src, dst):
        nonlocal hit
        if Path(dst) == paths.queue and not hit:
            hit = True
            if after:
                replace_file(src, dst)
            raise OSError("fixture queue failure")
        return replace_file(src, dst)

    monkeypatch.setattr(publication.os, "replace", fail)
    with pytest.raises(OSError, match="fixture queue failure"):
        run(paths)
    assert hit and inventory(tmp_path) == before


def test_private_queue_write_failure_never_publishes_copies(tmp_path):
    paths = setup(tmp_path)
    before = inventory(tmp_path)

    def fail(*args):
        raise OSError("fixture staging disk full")

    with pytest.raises(OSError, match="staging disk full"):
        run(paths, write_queue=fail)
    assert inventory(tmp_path) == before


@pytest.mark.parametrize("changed", ["queue", "source", "library"])
def test_input_output_drift_during_identity_check_preserves_competing_change(
    tmp_path, changed
):
    paths = setup(tmp_path)
    source = paths.downloads / "paper_0.pdf"
    target = {"queue": paths.queue, "source": source, "library": targets(paths)[1]}[
        changed
    ]
    body = target.read_bytes() if target.exists() else b"new competitor library"
    mutation = body + b"\ncompeting update"

    def check(path, citation):
        answer = intake.title_check(path, citation)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(mutation)
        return answer

    with pytest.raises(ValueError, match="input/output changed"):
        run(paths, title_checker=check)
    assert target.read_bytes() == mutation
    assert source.exists()
    assert not targets(paths)[0].exists()
    assert not targets(paths)[2].exists()


def test_queue_read_capture_race_rejected_before_private_checks(tmp_path, monkeypatch):
    paths = setup(tmp_path)
    raw = Path.read_bytes
    changed = paths.queue.read_bytes().replace(b"old note", b"new note")

    def race(path):
        body = raw(path)
        if path == paths.queue:
            path.write_bytes(changed)
        return body

    monkeypatch.setattr(Path, "read_bytes", race)
    with pytest.raises(ValueError, match="queue changed while reading"):
        run(paths)
    assert raw(paths.queue) == changed
    assert not paths.corpus.exists()


@pytest.mark.parametrize("keep", [False, True])
def test_source_drift_during_staged_title_check_aborts_before_publication(
    tmp_path, keep
):
    paths = setup(tmp_path)
    source = paths.downloads / "paper_0.pdf"
    queue_before = paths.queue.read_bytes()
    calls = 0

    def check(path, citation):
        nonlocal calls
        calls += 1
        answer = intake.title_check(path, citation)
        if calls == 2:  # First staged artifact, after the private preparation check.
            source.write_bytes(b"competing source update during staged validation")
        return answer

    with pytest.raises(ValueError, match="input/output changed"):
        run(paths, title_checker=check, keep=keep)
    assert calls > 1
    assert source.read_bytes() == b"competing source update during staged validation"
    assert paths.queue.read_bytes() == queue_before
    assert not any(target.exists() for target in targets(paths))


@pytest.mark.parametrize("changed", ["source", "archive"])
def test_postpublication_drift_retains_original_and_reports_cleanup_separately(
    tmp_path, monkeypatch, changed
):
    paths = setup(tmp_path)
    source = paths.downloads / "paper_0.pdf"
    target = source if changed == "source" else targets(paths)[2]
    publish = intake.staged_publish

    def concurrent_edit(*args, **kwargs):
        result = publish(*args, **kwargs)
        target.write_bytes(b"competing postpublication edit")
        return result

    monkeypatch.setattr(intake, "staged_publish", concurrent_edit)
    result = run(paths)
    assert result.returncode == 1 and result.cleanup_pending
    assert source.exists() and target.read_bytes() == b"competing postpublication edit"
    assert read_rows(paths)[0]["status"] == "acquired"
    assert all(path.exists() for path in targets(paths))


def test_cleanup_failure_after_one_deletion_keeps_published_state_and_remaining_original(
    tmp_path, monkeypatch
):
    paths = setup(tmp_path, count=2)
    unlink = Path.unlink
    refused = paths.downloads / "paper_1.pdf"

    def fail(path, *args, **kwargs):
        if path == refused:
            raise OSError("fixture original cleanup denied")
        return unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail)
    result = run(paths)
    assert result.returncode == 1 and "cleanup denied" in result.cleanup_pending[0]
    assert not (paths.downloads / "paper_0.pdf").exists() and refused.exists()
    assert all(row["status"] == "acquired" for row in read_rows(paths))
    assert all(
        path.exists() for sid in ("paper_0", "paper_1") for path in targets(paths, sid)
    )


@pytest.mark.parametrize(
    "alias",
    [
        "source_symlink",
        "source_hardlink",
        "library_symlink",
        "cache_symlink",
        "queue_symlink",
        "roots",
    ],
)
def test_aliases_refused_without_selected_writes(tmp_path, alias):
    paths = setup(tmp_path / "selected")
    source = paths.downloads / "paper_0.pdf"
    other = tmp_path / "external.pdf"
    if alias in ("source_symlink", "source_hardlink"):
        shutil.copy2(source, other)
        source.unlink()
        if alias == "source_symlink":
            source.symlink_to(other)
        else:
            source.hardlink_to(other)
    elif alias == "roots":
        paths = replace(paths, library=paths.corpus)
    else:
        target = {
            "library_symlink": targets(paths)[1],
            "cache_symlink": targets(paths)[0],
            "queue_symlink": paths.queue,
        }[alias]
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.copy2(target, other)
            target.unlink()
        else:
            other.write_bytes(b"other data")
        target.symlink_to(other)
    before = inventory(tmp_path)
    if alias == "library_symlink":
        result = run(paths)
        assert result.returncode == 1 and "escapes" in result.bad[0]
    else:
        with pytest.raises(ValueError):
            run(paths)
    assert inventory(tmp_path) == before


@pytest.mark.parametrize(
    "label", ["../outside/paper.pdf", "/absolute/paper.pdf", "folder\\paper.pdf"]
)
def test_escaped_library_label_is_a_held_row(tmp_path, label):
    paths = setup(tmp_path)
    rows = read_rows(paths)
    rows[0]["target_library_path"] = label
    write_rows(paths.queue, rows)
    before = inventory(tmp_path)
    result = run(paths)
    assert result.returncode == 1 and "escapes" in result.bad[0]
    assert inventory(tmp_path) == before


def test_two_sources_cannot_alias_one_library_destination(tmp_path):
    paths = setup(tmp_path, count=2)
    rows = read_rows(paths)
    rows[1]["target_library_path"] = rows[0]["target_library_path"]
    write_rows(paths.queue, rows)
    before = inventory(tmp_path)
    with pytest.raises(ValueError, match="alias"):
        run(paths)
    assert inventory(tmp_path) == before


@pytest.mark.parametrize("damage", ["duplicate", "short_row", "columns"])
def test_malformed_queue_refused_without_writes(tmp_path, damage):
    paths = setup(tmp_path)
    if damage == "duplicate":
        write_rows(paths.queue, read_rows(paths) * 2)
    elif damage == "short_row":
        paths.queue.write_text(",".join(COLS) + "\nonly_id\n", encoding="utf-8")
    else:
        paths.queue.write_text("source_id,status\npaper_0,pending\n", encoding="utf-8")
    before = inventory(tmp_path)
    with pytest.raises(ValueError):
        run(paths)
    assert inventory(tmp_path) == before


def test_header_only_queue_and_unmatched_files_are_unchanged(tmp_path):
    paths = setup(tmp_path)
    write_rows(paths.queue, [])
    before = inventory(tmp_path)
    result = run(paths)
    assert not result.done and result.returncode == 0
    assert inventory(tmp_path) == before


def test_missing_library_keeps_original_and_queue(tmp_path):
    paths = replace(setup(tmp_path), library=None)
    before = inventory(tmp_path)
    result = run(paths)
    assert result.returncode == 1 and result.no_library == ("paper_0",)
    assert inventory(tmp_path) == before


def test_cli_selected_files_independent_of_current_directory(tmp_path):
    paths = setup(tmp_path / "selected")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    wrapper = Path(__file__).resolve().parents[1] / "scripts/intake-downloads.py"
    result = subprocess.run(
        [
            sys.executable,
            str(wrapper),
            "--dir",
            str(paths.downloads),
            "--queue-path",
            str(paths.queue),
            "--corpus-dir",
            str(paths.corpus),
            "--library-root",
            str(paths.library),
            "--keep",
        ],
        cwd=foreign,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "filed 1" in result.stdout and (paths.corpus / "paper_0.pdf").exists()
    assert (paths.downloads / "paper_0.pdf").exists()


def test_competing_library_creation_is_preserved_and_requires_reconciliation(
    tmp_path, monkeypatch
):
    paths = setup(tmp_path / "selected")
    scratch = tmp_path / "recovery"
    scratch.mkdir()
    mkdtemp = publication.tempfile.mkdtemp
    monkeypatch.setattr(
        publication.tempfile, "mkdtemp", lambda **kwargs: mkdtemp(dir=scratch, **kwargs)
    )
    target = targets(paths)[1]
    link = publication.os.link
    before_queue = paths.queue.read_bytes()

    def race(src, dst):
        if Path(dst) == target:
            target.write_bytes(b"competing library copy")
        return link(src, dst)

    monkeypatch.setattr(publication.os, "link", race)
    with pytest.raises(publication.PublicationRecoveryError) as caught:
        run(paths)
    assert caught.value.recovery_dir.exists()
    assert "Temporary acquisition files retained" in " ".join(caught.value.__notes__)
    assert target.read_bytes() == b"competing library copy"
    assert paths.queue.read_bytes() == before_queue
    assert (paths.downloads / "paper_0.pdf").exists()
    assert not targets(paths)[0].exists() and not targets(paths)[2].exists()


def test_private_filing_failure_does_not_leak_partial_row_files(tmp_path):
    paths = setup(tmp_path, count=2)
    copy = intake.copy_immutable

    def fail(src, dst):
        if Path(dst).name == "paper_1.pdf" and "archive" in Path(dst).parts:
            raise OSError("fixture private library hold")
        return copy(src, dst)

    result = run(paths, copy_file=fail)
    assert result.returncode == 1 and len(result.done) == 1
    assert read_rows(paths)[0]["status"] == "acquired"
    assert read_rows(paths)[1]["status"] == "pending"
    assert not any(path.exists() for path in targets(paths, "paper_1"))
    assert (paths.downloads / "paper_1.pdf").exists()
