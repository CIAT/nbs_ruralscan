"""Discovery registration stays within selected artifacts and publishes one batch.

Candidates and reports are synthetic test fixtures, never discovered project sources.
Real registration, search-log and ledger writers run except injected failure cases.
"""

import csv
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from nbs_ruralscan.schema_tools import discovery_registration as registration
from nbs_ruralscan.schema_tools import publication


ROOT = Path(__file__).resolve().parents[1]
FAMILY = "agroforestry__planted_silvoarable"
CITATION = (
    "Synthetic fixture (2026). Synthetic discovery source alpha. Test publication."
)


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def tree(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def candidate(**changes):
    return {
        "candidate_id": "synthetic_alpha",
        "citation": CITATION,
        "tables": "T3|T6",
        "process": "updated_lit",
        "families": [FAMILY],
        "oa_status": "unknown",
        "relevance_note": "Synthetic test fixture, not a discovered source.",
        **changes,
    }


def protocol(**changes):
    return {
        "table": "T3",
        "category": "updated_lit",
        "search_terms": 'synthetic fixture AND "agroforestry"',
        "inclusion_criteria": "Synthetic test membership only",
        "limits": "Synthetic bounded fixture, no external search performed",
        "n_retrieved": 12,
        "n_screened": 8,
        "n_included": 1,
        **changes,
    }


def input_path(args, option):
    return Path(args[args.index(option) + 1].split("=", 1)[1])


def make_batch(root, *, layout="flat", mark=True, reuse=False, candidates=None):
    root = root.resolve()
    if layout == "canonical":
        paths = registration.DiscoveryRegistrationPaths.from_root(root)
    else:
        paths = registration.DiscoveryRegistrationPaths(
            queue=root / "queue.csv",
            sources=root / "sources.csv",
            families=root / "families.csv",
            searches=root / "searches.csv",
            ledger=root / "ledger.csv",
            logs=root / "logs",
        )
        if layout == "split":
            paths = replace(
                paths,
                queue=root / "acquisition/queue.csv",
                sources=root / "read-only/sources.csv",
                families=root / "vocabulary/families.csv",
                searches=root / "methods/searches.csv",
                ledger=root / "progress/stages.csv",
                logs=root / "reports/discovery",
            )
    with (ROOT / "pipeline/acquisition_queue.csv").open(newline="") as stream:
        queue_columns = next(csv.reader(stream))
    write_csv(paths.queue, [], queue_columns)
    write_csv(paths.sources, [], ["source_id", "citation", "doi", "nbs_ids"])
    paths.families.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "schema/registers/FAM_family_registry.csv", paths.families)
    inputs = root / "inputs"
    inputs.mkdir()
    candidates_file, report = inputs / "candidates.json", inputs / "report.md"
    candidates_file.write_text(
        json.dumps([candidate()] if candidates is None else candidates),
        encoding="utf-8",
    )
    report.write_text(
        "# Synthetic discovery fixture\n## Verbatim queries\n"
        'synthetic fixture AND "agroforestry"\n'
        "## Limits\nSynthetic test records, no external search performed.\n",
        encoding="utf-8",
    )
    args = [
        "agroforestry",
        "--date",
        "2026-11-06",
        "--ruleset",
        "v1.8.1",
        "--run-prefix",
        "synthetic_round",
        "--searched-by",
        "synthetic-test",
        "--assigned",
        "synthetic-test",
        "--candidates",
        f"lit={candidates_file}",
        "--reports",
        f"lit={report}",
        "--log-names",
        "lit=synthetic.md",
    ]
    if mark:
        args += ["--ledger", "updated_lit=done"]
    if reuse:
        args += ["--reuse-log", "reuse.json"]
    return paths, args


def add_protocols(args, items, *, targeted=True):
    path = input_path(args, "--candidates").with_name("protocols.json")
    path.write_text(json.dumps(items), encoding="utf-8")
    args += ["--protocols", f"lit={path}"]
    if targeted:
        args += ["--family", FAMILY]
    return path


def outputs(paths, *, mark=True, reuse=False):
    result = [paths.queue, paths.searches, paths.logs / "synthetic.md"]
    if mark:
        result.append(paths.ledger)
    if reuse:
        result.append(paths.logs / "reuse.json")
    return result


@pytest.mark.parametrize("layout", ["flat", "split", "canonical"])
def test_selected_paths_from_foreign_cwd_ignore_poisoned_defaults(
    tmp_path, monkeypatch, layout
):
    paths, args = make_batch(tmp_path / "selected", layout=layout)
    poison = tmp_path / "compiler-defaults"
    poison.mkdir()
    poison_search, poison_ledger = poison / "search.csv", poison / "ledger.csv"
    poison_search.write_text("invalid compiler search default\n")
    poison_ledger.write_text("invalid compiler ledger default\n")
    monkeypatch.setattr(registration.search_log, "SRCH", poison_search)
    monkeypatch.setattr(registration.search_log.rows, "__defaults__", (poison_search,))
    monkeypatch.setattr(
        registration.search_log.log_search,
        "__kwdefaults__",
        {
            **(registration.search_log.log_search.__kwdefaults__ or {}),
            "path": poison_search,
        },
    )
    monkeypatch.setattr(registration.ledger, "LEDGER", poison_ledger)
    foreign = tmp_path / "unrelated-working-directory"
    foreign.mkdir()
    monkeypatch.chdir(foreign)
    before = tree(tmp_path)
    assert registration.main(args, paths=paths) == 0
    after_first = tree(tmp_path)
    changed = {
        p for p in set(before) | set(after_first) if before.get(p) != after_first.get(p)
    }
    assert changed == {p.relative_to(tmp_path) for p in outputs(paths)}
    queued = read_csv(paths.queue)
    assert len(queued) == 1
    assert queued[0]["source_id"] == "synthetic_alpha"
    assert queued[0]["status"] == "pending"
    assert queued[0]["family"] == FAMILY
    assert queued[0]["doi_verified"] == queued[0]["title_verified"] == ""
    assert {r["table"] for r in read_csv(paths.searches)} == {"T3", "T6"}
    assert all(
        r["n_retrieved"] == r["n_screened"] == "" for r in read_csv(paths.searches)
    )
    assert all(r["searched"] == r["screened"] == "done" for r in read_csv(paths.ledger))
    assert "ruleset **v1.8.1**" in (paths.logs / "synthetic.md").read_text()
    after = tree(tmp_path)
    stats = {p: (p.stat().st_mtime_ns, p.stat().st_ino) for p in outputs(paths)}
    assert registration.main(args, paths=paths) == 0
    assert tree(tmp_path) == after
    assert stats == {p: (p.stat().st_mtime_ns, p.stat().st_ino) for p in outputs(paths)}


def test_interleaved_contexts_keep_independent_families_and_history(tmp_path):
    first, first_args = make_batch(tmp_path / "first")
    second, second_args = make_batch(tmp_path / "second")
    # The second selected registry maps the same subpractice to a distinct fixture family.
    rows = read_csv(second.families)
    for row in rows:
        if row["subpractice_id"] == "alley_cropping":
            row["suitability_family_id"] = "agroforestry__synthetic_selected_family"
    write_csv(second.families, rows, list(rows[0]))
    for args in (first_args, second_args):
        input_path(args, "--candidates").write_text(
            json.dumps([candidate(families=["alley_cropping"])])
        )
    registration.main(first_args, paths=first)
    first_state = tree(tmp_path / "first")
    registration.main(second_args, paths=second)
    second_state = tree(tmp_path / "second")
    registration.main(first_args, paths=first)
    assert tree(tmp_path / "first") == first_state
    assert tree(tmp_path / "second") == second_state
    assert read_csv(first.queue)[0]["family"] == FAMILY
    assert (
        read_csv(second.queue)[0]["family"] == "agroforestry__synthetic_selected_family"
    )


@pytest.mark.parametrize("mark", [False, True])
def test_header_only_queue_bootstraps_only_requested_registers(tmp_path, mark):
    paths, args = make_batch(tmp_path, mark=mark)
    assert read_csv(paths.queue) == []
    assert not paths.searches.exists() and not paths.ledger.exists()
    registration.main(args, paths=paths)
    assert len(read_csv(paths.queue)) == 1
    assert len(read_csv(paths.searches)) == 2
    assert paths.ledger.exists() is mark
    if mark:
        assert len(read_csv(paths.ledger)) == 2


@pytest.mark.parametrize("empty", [False, True])
def test_targeted_protocol_keeps_measured_counts_including_zero_yield(tmp_path, empty):
    rows = [] if empty else [candidate(tables="T3")]
    paths, args = make_batch(tmp_path, candidates=rows)
    add_protocols(args, [protocol(n_included=len(rows))])
    registration.main(args, paths=paths)
    assert len(read_csv(paths.queue)) == len(rows)
    (search,) = read_csv(paths.searches)
    assert (search["n_retrieved"], search["n_screened"], search["n_included"]) == (
        "12",
        "8",
        str(len(rows)),
    )
    assert search["suitability_family_id"] == FAMILY
    assert search["search_terms"] == protocol()["search_terms"]
    assert search["inclusion_criteria"] == protocol()["inclusion_criteria"]
    (stage,) = read_csv(paths.ledger)
    assert stage["table"] == "T3" and stage["family"] == FAMILY
    assert stage["searched"] == stage["screened"] == "done"
    assert stage["verified"] == "not_started"


def test_counts_precede_deduplication_within_batch_and_against_queue(tmp_path):
    paths, args = make_batch(
        tmp_path,
        candidates=[
            candidate(tables="T3"),
            candidate(candidate_id="synthetic_duplicate", tables="T3"),
        ],
    )
    add_protocols(args, [protocol(n_included=2)])
    registration.main(args, paths=paths)
    assert len(read_csv(paths.queue)) == 1
    assert read_csv(paths.searches)[0]["n_included"] == "2"
    args[args.index("--run-prefix") + 1] = "synthetic_second_round"
    args[args.index("--log-names") + 1] = "lit=second.md"
    registration.main(args, paths=paths)
    assert len(read_csv(paths.queue)) == 1
    assert [r["n_included"] for r in read_csv(paths.searches)] == ["2", "2"]


def test_explicit_reuse_keeps_canonical_source_and_records_new_scope(tmp_path):
    paths, args = make_batch(
        tmp_path,
        reuse=True,
        candidates=[
            candidate(
                reuse_source_id="canonical_fixture",
                reuse_reason="Synthetic new table scope",
            )
        ],
    )
    write_csv(
        paths.sources,
        [
            {
                "source_id": "canonical_fixture",
                "citation": CITATION,
                "doi": "",
                "nbs_ids": "forest_restoration",
            }
        ],
        ["source_id", "citation", "doi", "nbs_ids"],
    )
    before = paths.sources.read_bytes()
    registration.main(args, paths=paths)
    assert read_csv(paths.queue) == []
    assert paths.sources.read_bytes() == before
    (task,) = json.loads((paths.logs / "reuse.json").read_text())
    assert task == {
        "source_id": "canonical_fixture",
        "candidate_id": "synthetic_alpha",
        "lane": "lit",
        "nbs_id": "agroforestry",
        "tables": ["T3", "T6"],
        "families": [FAMILY],
        "reason": "Synthetic new table scope",
        "status": "pending_scope_review",
        "run_id": "synthetic_round_lit",
        "search_date": "2026-11-06",
    }
    assert all(r["n_included"] == "1" for r in read_csv(paths.searches))


@pytest.mark.parametrize("conflict", ["report", "protocol", "reuse"])
def test_same_run_history_conflict_preserves_all_outputs(tmp_path, capsys, conflict):
    paths, args = make_batch(tmp_path, reuse=True, candidates=[candidate(tables="T3")])
    protocol_path = add_protocols(args, [protocol()])
    registration.main(args, paths=paths)
    if conflict == "report":
        with input_path(args, "--reports").open("a") as stream:
            stream.write("\nChanged historical report text.\n")
    elif conflict == "protocol":
        protocol_path.write_text(
            json.dumps([protocol(search_terms="changed historical query")])
        )
    else:
        input_path(args, "--candidates").write_text(
            json.dumps(
                [
                    candidate(
                        tables="T3",
                        reuse_source_id="synthetic_alpha",
                        reuse_reason="new reuse task in old run",
                    )
                ]
            )
        )
    before = tree(tmp_path)
    with pytest.raises(SystemExit, match="2"):
        registration.main(args, paths=paths)
    message = capsys.readouterr().err
    assert {
        "report": "tracked discovery log differs",
        "protocol": "existing search protocol differs",
        "reuse": "reuse log differs",
    }[conflict] in message
    assert tree(tmp_path) == before


@pytest.mark.parametrize("malformed", [False, True])
def test_dry_run_renders_and_validates_whole_manifest_without_publishing(
    tmp_path, monkeypatch, malformed
):
    paths, args = make_batch(tmp_path, reuse=True)
    original = registration.atomic_write
    writes = []

    def write(path, data):
        writes.append(Path(path).suffix)
        if malformed and Path(path).name == "reuse.json":
            data = b"invalid staged JSON"
        return original(path, data)

    monkeypatch.setattr(registration, "atomic_write", write)
    before = tree(tmp_path)
    if malformed:
        with pytest.raises(json.JSONDecodeError):
            registration.main(args + ["--dry-run"], paths=paths)
    else:
        assert registration.main(args + ["--dry-run"], paths=paths) == 0
    assert {".md", ".csv", ".json"} <= set(writes)
    assert tree(tmp_path) == before
    assert not paths.logs.exists()


def test_dry_run_rejects_invalid_final_protocol_without_any_output(tmp_path):
    paths, args = make_batch(tmp_path, candidates=[candidate(tables="T3")])
    add_protocols(args, [protocol(), protocol(table="T6", n_included=1)])
    before = tree(tmp_path)
    with pytest.raises(SystemExit, match="2"):
        registration.main(args + ["--dry-run"], paths=paths)
    assert tree(tmp_path) == before


@pytest.mark.parametrize("writer", ["ledger", "report"])
def test_late_writer_failure_preserves_existing_outputs_and_new_reuse(
    tmp_path, monkeypatch, writer
):
    paths, args = make_batch(tmp_path)
    registration.main(args, paths=paths)
    args[args.index("--run-prefix") + 1] = "synthetic_second_round"
    args[args.index("--log-names") + 1] = "lit=second.md"
    args += ["--reuse-log", "second-reuse.json"]
    input_path(args, "--candidates").write_text(
        json.dumps(
            [
                candidate(
                    candidate_id="synthetic_beta",
                    citation="Synthetic fixture (2026). Synthetic source beta. Test publication.",
                )
            ]
        )
    )
    if writer == "ledger":
        original_mark = registration.ledger.mark

        def failing_mark(*a, **kw):
            original_mark(*a, **kw)
            raise RuntimeError("injected ledger writer failure")

        monkeypatch.setattr(registration.ledger, "mark", failing_mark)
    else:
        original_write = registration.atomic_write

        def failing_write(path, data):
            original_write(path, data)
            if Path(path).suffix == ".md":
                raise RuntimeError("injected report writer failure")

        monkeypatch.setattr(registration, "atomic_write", failing_write)
    before = tree(tmp_path)
    with pytest.raises(RuntimeError, match=f"injected {writer} writer failure"):
        registration.main(args, paths=paths)
    assert tree(tmp_path) == before


@pytest.mark.parametrize("fail_at", [2, 3, 4, 5])
def test_each_later_installation_failure_rolls_back_existing_and_new_files(
    tmp_path, monkeypatch, fail_at
):
    paths, args = make_batch(tmp_path, reuse=True)
    destinations = outputs(paths, reuse=True)
    original_replace = publication.os.replace
    installs = []

    def fail_after_install(source, destination):
        if Path(destination) in destinations and Path(source).name.startswith(
            ".nbs-publish-"
        ):
            installs.append(Path(destination))
            if len(installs) == fail_at:
                original_replace(source, destination)
                raise OSError("injected installation failure after replacement")
        return original_replace(source, destination)

    monkeypatch.setattr(publication.os, "replace", fail_after_install)
    before = tree(tmp_path)
    with pytest.raises(OSError, match="injected installation failure"):
        registration.main(args, paths=paths)
    assert installs[:fail_at] == destinations[:fail_at]
    assert tree(tmp_path) == before
    assert not paths.logs.exists()
    assert not list(tmp_path.rglob(".nbs-publish-*"))


@pytest.mark.parametrize(
    "collision",
    [
        "sources",
        "families",
        "candidate",
        "report",
        "protocol",
        "symlink",
        "parent_symlink",
        "hardlink",
        "duplicate",
        "case",
        "unrequested_ledger_case",
    ],
)
def test_output_aliases_are_rejected_before_any_write(tmp_path, collision):
    paths, args = make_batch(tmp_path, mark=False)
    protocols = add_protocols(args, [protocol(), protocol(table="T6")])
    if collision in {"sources", "families"}:
        paths = replace(paths, searches=getattr(paths, collision))
    elif collision in {"candidate", "report", "protocol"}:
        selected = {
            "candidate": input_path(args, "--candidates"),
            "report": input_path(args, "--reports"),
            "protocol": protocols,
        }[collision]
        paths = replace(paths, searches=selected)
    elif collision == "symlink":
        paths.searches.symlink_to(paths.sources)
    elif collision == "parent_symlink":
        target = tmp_path / "real-logs"
        target.mkdir()
        paths.logs.symlink_to(target, target_is_directory=True)
    elif collision == "hardlink":
        os.link(paths.sources, paths.searches)
    elif collision == "duplicate":
        paths = replace(paths, searches=paths.queue)
    elif collision == "case":
        paths = replace(paths, searches=paths.queue.with_name(paths.queue.name.upper()))
    else:
        paths = replace(
            paths, searches=paths.ledger.with_name(paths.ledger.name.upper())
        )
    before = tree(tmp_path)
    with pytest.raises(ValueError):
        registration.main(args, paths=paths)
    assert tree(tmp_path) == before


def test_relocated_cli_uses_explicit_data_only_root(tmp_path):
    data_root = tmp_path / "selected-data"
    paths, args = make_batch(data_root, layout="canonical")
    compiler = tmp_path / "compiler"
    wrapper = compiler / "scripts/register-discovery.py"
    wrapper.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "scripts/register-discovery.py", wrapper)
    foreign = tmp_path / "foreign-cwd"
    foreign.mkdir()
    root_alias = tmp_path / "selected-root-alias"
    root_alias.symlink_to(data_root, target_is_directory=True)
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    command = [sys.executable, str(wrapper), *args, "--root", str(root_alias)]
    before = tree(tmp_path)
    dry = subprocess.run(
        command + ["--dry-run"], cwd=foreign, env=env, capture_output=True, text=True
    )
    assert dry.returncode == 0, dry.stderr
    assert "nothing published" in dry.stdout
    assert tree(tmp_path) == before
    result = subprocess.run(
        command, cwd=foreign, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert len(read_csv(paths.queue)) == 1
    assert len(read_csv(paths.searches)) == len(read_csv(paths.ledger)) == 2
    assert not (compiler / "schema").exists()
    assert not (compiler / "pipeline").exists()
    assert not list(foreign.iterdir())
    after = tree(tmp_path)
    changed = {p for p in set(before) | set(after) if before.get(p) != after.get(p)}
    assert changed == {p.relative_to(tmp_path) for p in outputs(paths)}
