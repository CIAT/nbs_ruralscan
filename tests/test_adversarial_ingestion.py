"""Adversarial acquisition/discovery cases; synthetic artifacts, no network."""

import base64
import csv
import importlib.util
import json
from pathlib import Path

import fitz
import pytest

from nbs_ruralscan.ingest import github
from nbs_ruralscan.ingest.acquire import AcquireError, acquire
from nbs_ruralscan.ingest.integrity import copy_immutable, pdf_title_error

ROOT = Path(__file__).resolve().parents[1]
TITLE = "Landscape restoration suitability across climate and soil gradients"
CITATION = f"Example, A. (2026). {TITLE}. Example Journal."


def script(name):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), ROOT / "scripts" / f"{name}.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_pdf(path, text=TITLE):
    path.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open() as doc:
        doc.new_page().insert_text((30, 40), text, fontsize=9)
        doc.save(path)


def test_immutable_library_copy_preserves_different_prior_artifact(tmp_path):
    source, destination = tmp_path / "incoming.pdf", tmp_path / "library/paper.pdf"
    source.write_bytes(b"original")
    copy_immutable(source, destination)
    copy_immutable(source, destination)
    source.write_bytes(b"different")
    with pytest.raises(FileExistsError, match="differs"):
        copy_immutable(source, destination)
    assert destination.read_bytes() == b"original"
    assert list(destination.parent.iterdir()) == [destination]


def test_identity_gate_checks_document_not_only_verified_citation(tmp_path):
    paper = tmp_path / "paper.pdf"
    make_pdf(paper, "Unrelated economics of urban transport investments")
    assert "document identity verification" in pdf_title_error(paper, CITATION)
    paper.unlink()
    make_pdf(paper)
    assert pdf_title_error(paper, CITATION) is None


@pytest.mark.parametrize("kind", ["pdf", "website", "markdown"])
def test_acquisition_cannot_replace_another_kinds_sidecar(tmp_path, monkeypatch, kind):
    original = '{"kind": "github_code", "commit": "original"}'
    meta = tmp_path / "paper.meta.json"
    meta.write_text(original)
    monkeypatch.setattr(
        importlib.import_module("nbs_ruralscan.ingest.acquire").requests,
        "get",
        lambda *a, **k: pytest.fail("must not fetch"),
    )
    with pytest.raises(AcquireError, match="conflicting source kind"):
        acquire(
            "paper",
            "https://example.org",
            kind=kind,
            corpus_dir=tmp_path,
            overwrite=True,
        )
    assert meta.read_text() == original


@pytest.mark.parametrize(
    "path",
    ["folder/code#part.py", "folder/code?ref=main.py", "folder/code with spaces.py"],
)
def test_github_paths_cannot_override_commit_pin(tmp_path, monkeypatch, path):
    calls = []

    def api(args):
        calls.append(args[0])
        return base64.b64encode(b"weight = 0.5\n").decode()

    monkeypatch.setattr(github, "_gh", api)
    sha = "a" * 40
    github.acquire_file("owner/repo", sha, path, tmp_path)
    assert calls[0].count("?") == 1
    assert "#" not in calls[0]
    assert calls[0].endswith(f"?ref={sha}")
    assert " " not in calls[0]


@pytest.mark.parametrize("body", [b"\xff\xfe\x00\x01", b"PDF\x00data"])
def test_github_binary_file_is_not_relabelled_text(tmp_path, monkeypatch, body):
    monkeypatch.setattr(github, "_gh", lambda args: base64.b64encode(body).decode())
    with pytest.raises(github.GithubIngestError, match="binary"):
        github.acquire_file("owner/repo", "a" * 40, "data.bin", tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_github_invalid_sidecar_shape_is_clear_hold(tmp_path, monkeypatch):
    monkeypatch.setattr(
        github, "_gh", lambda args: base64.b64encode(b"slope = 1").decode()
    )
    (tmp_path / "paper.txt").write_bytes(b"slope = 1")
    (tmp_path / "paper.meta.json").write_text("[]")
    with pytest.raises(github.GithubIngestError, match="Refusing to replace"):
        github.acquire_file("owner/repo", "a" * 40, "code.py", tmp_path, "paper")


@pytest.mark.parametrize("unrelated", [False, True])
def test_queue_holds_library_collision_and_unrelated_pdf(
    tmp_path, monkeypatch, unrelated
):
    module = script("acquire-queue")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(module, "LIB_ROOT", tmp_path / "library")
    monkeypatch.setattr(module, "LIB_REL", "team")
    monkeypatch.setattr(module, "_acquire", lambda *a: True)
    monkeypatch.setattr(module.time, "sleep", lambda *a: None)
    make_pdf(
        module.CACHE / "paper.pdf", "Unrelated highway study" if unrelated else TITLE
    )
    mirror = module.LIB_ROOT / "team/forest"
    mirror.mkdir(parents=True)
    old = mirror / "paper.pdf"
    old.write_bytes(b"existing original")
    row = dict(
        source_id="paper",
        nbs_id="forest_restoration",
        date_added="2026-10-28",
        status="pending",
        citation=CITATION,
        doi="10.123/example",
        doi_verified="true",
        url="https://example.org/p.pdf",
        blocker="",
        note="",
        target_library_path="",
    )
    queue = tmp_path / "pipeline/acquisition_queue.csv"
    write_csv(queue, [row], list(row))
    assert (
        module.main(
            [
                "--date",
                "2026-10-28",
                "--nbs",
                "forest_restoration",
                "--library-subdir",
                "forest",
            ]
        )
        == 0
    )
    result = next(csv.DictReader(queue.open()))
    assert result["status"] == "pending"
    assert result["target_library_path"] == ""
    assert ("document identity hold" if unrelated else "library copy held") in result[
        "blocker"
    ]
    assert old.read_bytes() == b"existing original"


def test_library_subdir_cannot_escape_team_library(tmp_path, monkeypatch):
    module = script("acquire-queue")
    monkeypatch.setattr(module, "LIB_ROOT", tmp_path)
    monkeypatch.setattr(module, "LIB_REL", "team")
    with pytest.raises(SystemExit):
        module.main(
            [
                "--date",
                "2026-10-28",
                "--nbs",
                "forest_restoration",
                "--library-subdir",
                "../outside",
            ]
        )


@pytest.fixture
def discovery(tmp_path, monkeypatch):
    module = script("register-discovery")
    columns = next(csv.reader((ROOT / "pipeline/acquisition_queue.csv").open()))
    row = {c: "" for c in columns}
    row.update(
        source_id="known",
        citation=CITATION,
        doi="10.123/example",
        nbs_id="agroforestry",
        tables="T3",
    )
    queue = tmp_path / "queue.csv"
    write_csv(queue, [row], columns)
    source = tmp_path / "source.csv"
    write_csv(source, [], ["source_id", "citation", "doi", "nbs_ids"])
    monkeypatch.setattr(module, "QUEUE", queue)
    monkeypatch.setattr(module, "SRC", source)
    monkeypatch.setattr(module, "LOGS", tmp_path / "logs")
    monkeypatch.setattr(
        module.search_log, "log_search", lambda **kw: pytest.fail("must not write SRCH")
    )
    monkeypatch.setattr(
        module.ledger, "mark", lambda *a, **kw: pytest.fail("must not mark ledger")
    )
    candidate = tmp_path / "candidates.json"
    candidate.write_text(
        json.dumps(
            [
                dict(
                    candidate_id="rediscovered",
                    citation=CITATION,
                    doi="10.123/example",
                    tables="T4",
                    process="updated_lit",
                )
            ]
        )
    )
    report = tmp_path / "report.md"
    report.write_text("# Report\n## Verbatim queries\nforest suitability\n")
    args = [
        "forest_restoration",
        "--date",
        "2026-10-28",
        "--ruleset",
        "v1.7.0",
        "--candidates",
        f"lit={candidate}",
        "--reports",
        f"lit={report}",
        "--log-names",
        "lit=forest.md",
    ]
    return module, args, queue


@pytest.mark.parametrize("nbs", ["forest_restoration", "agroforestry"])
def test_cross_scope_duplicate_does_not_erase_new_work(discovery, capsys, nbs):
    module, args, queue = discovery
    args[0] = nbs
    before = queue.read_bytes()
    with pytest.raises(SystemExit):
        module.main(args)
    assert "new NbS/table reuse tracking" in capsys.readouterr().err
    assert queue.read_bytes() == before


def test_unknown_nbs_is_rejected_before_registration(discovery, capsys):
    module, args, queue = discovery
    args[0] = "typo_unknown_nbs"
    before = queue.read_bytes()
    with pytest.raises(SystemExit):
        module.main(args)
    assert "unknown NbS" in capsys.readouterr().err
    assert queue.read_bytes() == before


def test_existing_discovery_report_cannot_be_overwritten(discovery, capsys):
    module, args, queue = discovery
    module.LOGS.mkdir()
    report = module.LOGS / "forest.md"
    report.write_text("historical queries and counts")
    before = queue.read_bytes()
    with pytest.raises(SystemExit):
        module.main(args)
    assert "tracked discovery log differs" in capsys.readouterr().err
    assert report.read_text() == "historical queries and counts"
    assert queue.read_bytes() == before


@pytest.fixture
def intake(tmp_path, monkeypatch):
    module = script("intake-downloads")
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    library = tmp_path / "library"
    library.mkdir()
    monkeypatch.setattr(module, "CORPUS", tmp_path / "corpus")
    monkeypatch.setattr(module, "QUEUE", tmp_path / "queue.csv")
    monkeypatch.setattr(module._H, "library_root", lambda: library)
    rows = [
        dict(
            source_id=sid,
            citation=CITATION,
            target_library_path=f"forest/{sid}.pdf",
            status="pending",
            title_verified="",
            blocker="",
            note="",
        )
        for sid in ("a_broken", "z_good")
    ]
    write_csv(module.QUEUE, rows, list(rows[0]))
    (downloads / "a_broken.pdf").write_bytes(b"not a PDF")
    make_pdf(downloads / "z_good.pdf")
    return module, downloads


def test_corrupt_download_does_not_abort_valid_intake(intake):
    module, downloads = intake
    assert module.main(["--dir", str(downloads)]) == 1
    rows = list(csv.DictReader(module.QUEUE.open()))
    assert rows[0]["status"] == "pending"
    assert rows[1]["status"] == "acquired"
    assert (downloads / "a_broken.pdf").exists()
    assert not (downloads / "z_good.pdf").exists()
    assert (downloads / "nbs_ingested/z_good.pdf").exists()


def test_prior_download_archive_is_never_overwritten(intake):
    module, downloads = intake
    archive = downloads / "nbs_ingested/z_good.pdf"
    archive.parent.mkdir()
    archive.write_bytes(b"previous original")
    before = module.QUEUE.read_bytes()
    assert module.main(["--dir", str(downloads)]) == 1
    assert archive.read_bytes() == b"previous original"
    assert (downloads / "z_good.pdf").exists()
    assert module.QUEUE.read_bytes() == before


def test_failed_queue_persistence_keeps_download_for_retry(intake, monkeypatch):
    module, downloads = intake
    before = module.QUEUE.read_bytes()

    def fail_write(*args):
        raise OSError("simulated full disk")

    monkeypatch.setattr(module, "atomic_write", fail_write)
    with pytest.raises(OSError, match="full disk"):
        module.main(["--dir", str(downloads)])
    assert module.QUEUE.read_bytes() == before
    assert (downloads / "z_good.pdf").exists()
    assert (downloads / "nbs_ingested/z_good.pdf").exists()


def test_same_doi_with_conflicting_title_is_not_silently_deduplicated(
    discovery, capsys
):
    module, args, queue = discovery
    candidate_path = Path(args[args.index("--candidates") + 1].split("=", 1)[1])
    candidate = json.loads(candidate_path.read_text())
    candidate[0]["citation"] = (
        "Different author (2026). Entirely different paper about transport. Journal."
    )
    candidate_path.write_text(json.dumps(candidate))
    before = queue.read_bytes()
    with pytest.raises(SystemExit):
        module.main(args)
    assert "same DOI has different citation titles" in capsys.readouterr().err
    assert queue.read_bytes() == before


def test_duplicate_scopes_within_batch_do_not_lose_second_table(discovery, capsys):
    module, args, queue = discovery
    path = Path(args[args.index("--candidates") + 1].split("=", 1)[1])
    path.write_text(
        json.dumps(
            [
                dict(
                    candidate_id=f"new_{table}",
                    citation="Author (2026). Novel canopy regeneration research. Journal.",
                    doi="10.123/new",
                    tables=table,
                    process="updated_lit",
                )
                for table in ("T3", "T4")
            ]
        )
    )
    before = queue.read_bytes()
    with pytest.raises(SystemExit):
        module.main(args)
    assert "new NbS/table reuse tracking" in capsys.readouterr().err
    assert queue.read_bytes() == before


def test_existing_source_new_family_requires_explicit_reuse_tracking(discovery, capsys):
    module, args, queue = discovery
    args[0] = "agroforestry"
    rows = list(csv.DictReader(queue.open()))
    rows[0]["tables"] = "T4"
    rows[0]["family"] = "agroforestry__planted_silvoarable"
    write_csv(queue, rows, list(rows[0]))
    path = Path(args[args.index("--candidates") + 1].split("=", 1)[1])
    candidates = json.loads(path.read_text())
    candidates[0]["families"] = ["agroforestry__regeneration_farmland"]
    path.write_text(json.dumps(candidates))
    before = queue.read_bytes()
    with pytest.raises(SystemExit):
        module.main(args)
    assert "families=['agroforestry__regeneration_farmland']" in capsys.readouterr().err
    assert queue.read_bytes() == before


@pytest.mark.parametrize("valid_fallback", [False, True])
def test_wrong_candidate_pdf_never_publishes_and_fallback_can_succeed(
    tmp_path, monkeypatch, valid_fallback
):
    from types import SimpleNamespace

    module = script("acquire-queue")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(module, "LIB_ROOT", tmp_path / "library")
    monkeypatch.setattr(module, "LIB_REL", "team")
    monkeypatch.setattr(module.time, "sleep", lambda *a: None)
    mirror = module.LIB_ROOT / "team/forest"
    mirror.mkdir(parents=True)
    wrong, correct = tmp_path / "wrong.pdf", tmp_path / "correct.pdf"
    make_pdf(wrong, "Unrelated highway engineering study")
    make_pdf(correct)
    first_url, second_url = (
        "https://example.org/wrong.pdf",
        "https://example.org/correct.pdf",
    )
    monkeypatch.setattr(
        module, "_candidates", lambda *a: [second_url] if valid_fallback else []
    )
    fetched = []

    def get(url, **kwargs):
        fetched.append(url)
        assert not (module.CACHE / "paper.pdf").exists()
        body = correct.read_bytes() if url == second_url else wrong.read_bytes()
        return SimpleNamespace(
            status_code=200, headers={"Content-Type": "application/pdf"}, content=body
        )

    monkeypatch.setattr(
        importlib.import_module("nbs_ruralscan.ingest.acquire").requests, "get", get
    )
    row = dict(
        source_id="paper",
        nbs_id="forest_restoration",
        date_added="2026-10-28",
        status="pending",
        citation=CITATION,
        doi="10.123/example",
        doi_verified="true",
        url=first_url,
        blocker="",
        note="",
        target_library_path="",
    )
    queue = tmp_path / "pipeline/acquisition_queue.csv"
    write_csv(queue, [row], list(row))
    assert (
        module.main(
            [
                "--date",
                "2026-10-28",
                "--nbs",
                "forest_restoration",
                "--library-subdir",
                "forest",
            ]
        )
        == 0
    )
    result = next(csv.DictReader(queue.open()))
    if valid_fallback:
        assert fetched == [first_url, second_url]
        assert result["status"] == "acquired"
        assert result["url"] == second_url
        assert (module.CACHE / "paper.pdf").read_bytes() == correct.read_bytes()
        assert (mirror / "paper.pdf").read_bytes() == correct.read_bytes()
    else:
        assert fetched == [first_url]
        assert result["status"] == "pending"
        assert "document identity hold" in result["blocker"]
        assert first_url in result["blocker"]
        assert not (module.CACHE / "paper.pdf").exists()
        assert not (module.CACHE / "paper.meta.json").exists()
        assert not (mirror / "paper.pdf").exists()


def test_existing_wrong_cache_stays_intact_and_held(tmp_path, monkeypatch):
    module = script("acquire-queue")
    dest = tmp_path / "paper.pdf"
    make_pdf(dest, "Unrelated highway engineering study")
    original = dest.read_bytes()
    monkeypatch.setattr(
        module,
        "acquire",
        lambda *a, **k: pytest.fail("must not replace existing cache"),
    )
    holds = []
    assert not module._acquire(
        "paper", "https://example.org/p.pdf", dest, CITATION, holds
    )
    assert dest.read_bytes() == original
    assert "document identity verification" in holds[0]


@pytest.mark.parametrize(
    "registered,target,expected",
    [
        ("wetland_management| mangrove_restoration", "mangrove_restoration", True),
        ("forest_restoration|mangrove_restoration", "forest_restoration", True),
        (
            "forest_restoration_extended|mangrove_restoration",
            "forest_restoration",
            False,
        ),
        ("mangrove_restoration_extended", "mangrove_restoration", False),
    ],
)
def test_acquisition_selector_uses_exact_registered_nbs_tokens(
    tmp_path, monkeypatch, registered, target, expected
):
    module = script("acquire-queue")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(module, "LIB_ROOT", tmp_path / "library")
    monkeypatch.setattr(module, "LIB_REL", "team")
    (module.LIB_ROOT / "team/destination").mkdir(parents=True)
    calls = []

    def acquire_candidate(*args):
        calls.append(args[0])
        return False

    monkeypatch.setattr(module, "_acquire", acquire_candidate)
    monkeypatch.setattr(module, "_candidates", lambda *args: [])
    row = dict(
        source_id="paper",
        nbs_id=registered,
        date_added="2026-10-28",
        status="pending",
        citation=CITATION,
        doi="",
        url="https://example.org/p.pdf",
        blocker="",
        note="",
        target_library_path="",
    )
    queue = tmp_path / "pipeline/acquisition_queue.csv"
    write_csv(queue, [row], list(row))
    assert (
        module.main(
            ["--date", "2026-10-28", "--nbs", target, "--library-subdir", "destination"]
        )
        == 0
    )
    assert calls == (["paper"] if expected else [])
    result = next(csv.DictReader(queue.open()))
    assert result["nbs_id"] == registered
    assert result["status"] == "pending"


def test_existing_multinbs_table_and_family_scope_is_recognised(discovery, monkeypatch):
    module, args, queue = discovery
    rows = list(csv.DictReader(queue.open()))
    family = "forest_restoration__passive_regeneration"
    rows[0].update(
        nbs_id="wetland_management| forest_restoration", tables="T4", family=family
    )
    write_csv(queue, rows, list(rows[0]))
    candidate_path = Path(args[args.index("--candidates") + 1].split("=", 1)[1])
    candidates = json.loads(candidate_path.read_text())
    candidates[0]["families"] = [family]
    candidate_path.write_text(json.dumps(candidates))
    calls = []
    monkeypatch.setattr(
        module.search_log, "log_search", lambda **kwargs: calls.append(kwargs)
    )
    assert module.main(args) == 0
    result = list(csv.DictReader(queue.open()))
    assert len(result) == 1
    assert result[0]["nbs_id"] == rows[0]["nbs_id"]
    assert result[0]["family"] == family
    assert len(calls) == 1 and calls[0]["table"] == "T4"
