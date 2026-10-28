"""Regression cases from the October 2026 discovery/ingestion audit. No network."""

import csv
import hashlib
import importlib.util
import json
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from nbs_ruralscan.ingest import build, cache
from nbs_ruralscan.ingest.acquire import AcquireError, acquire
from nbs_ruralscan.ingest.models import DocIndex
from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.schema_tools import learnings, migrate_effects, search_log

ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), ROOT / "scripts" / f"{name}.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path, rows, columns=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=columns or list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


@pytest.mark.parametrize("sid", ["../escape", "/absolute", "", "a/b", "a\\b"])
def test_acquisition_rejects_paths_before_fetch(tmp_path, sid):
    with patch("nbs_ruralscan.ingest.acquire.requests.get") as get:
        with pytest.raises(ValueError, match="source_id"):
            acquire(sid, "https://example.org", kind="pdf", corpus_dir=tmp_path)
        get.assert_not_called()


def test_acquisition_rejects_html_with_pdf_mime(tmp_path):
    response = SimpleNamespace(
        status_code=200,
        headers={"Content-Type": "application/pdf"},
        content=b"<html>access denied</html>",
    )
    with patch("nbs_ruralscan.ingest.acquire.requests.get", return_value=response):
        with pytest.raises(AcquireError, match="signature"):
            acquire(
                "paper", "https://example.org/p.pdf", kind="pdf", corpus_dir=tmp_path
            )
    assert not (tmp_path / "paper.pdf").exists()


@pytest.mark.parametrize("change", ["body", "url", "sidecar", "pin"])
def test_cache_mismatch_refuses_without_overwrite(tmp_path, change):
    url = "https://example.org/p.pdf"
    response = SimpleNamespace(
        status_code=200,
        headers={"Content-Type": "application/pdf"},
        content=b"%PDF-1.4 test",
    )
    with patch(
        "nbs_ruralscan.ingest.acquire.requests.get", return_value=response
    ) as get:
        acquire("paper", url, kind="pdf", corpus_dir=tmp_path)
        if change == "body":
            (tmp_path / "paper.pdf").write_bytes(b"%PDF-1.4 different")
        if change == "sidecar":
            (tmp_path / "paper.meta.json").unlink()
        before = (tmp_path / "paper.pdf").read_bytes()
        with pytest.raises(AcquireError, match="Invalid cache"):
            acquire(
                "paper",
                url + ("?new" if change == "url" else ""),
                kind="pdf",
                corpus_dir=tmp_path,
                commit_sha="new" if change == "pin" else None,
            )
        assert get.call_count == 1
        assert (tmp_path / "paper.pdf").read_bytes() == before


def test_index_capability_upgrade_and_content_refresh(tmp_path, monkeypatch):
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    pdf = pdf_dir / "paper.pdf"
    pdf.write_bytes(b"first content")
    index_dir = tmp_path / "index"
    calls = []

    def extract(path, source_id, with_tables):
        calls.append(with_tables)
        return DocIndex(
            source_id, str(path), build._sha1(path), 1, tables_extracted=with_tables
        )

    monkeypatch.setattr(build, "build_index", extract)
    assert build.build_cache(pdf_dir, index_dir, with_tables=False) == ["paper"]
    assert build.build_cache(pdf_dir, index_dir, with_tables=False) == []
    assert build.build_cache(pdf_dir, index_dir, with_tables=True) == ["paper"]
    assert build.build_cache(pdf_dir, index_dir, with_tables=True) == []
    pdf.write_bytes(b"changed content")
    assert build.build_cache(pdf_dir, index_dir) == ["paper"]
    assert calls == [False, True, True]


def test_index_names_do_not_collide_and_bad_cache_is_not_used(tmp_path):
    assert cache.cache_path("a/b") != cache.cache_path("a?b")
    assert cache.cache_path("x" * 81) != cache.cache_path("x" * 80 + "y")
    p = cache.cache_path("paper", tmp_path)
    p.write_text("{broken")
    with pytest.warns(UserWarning, match="invalid index"):
        assert cache.load_index("paper", tmp_path) is None
    p.write_text(json.dumps(DocIndex("other", "", "", 0).to_dict()))
    with pytest.warns(UserWarning, match="source_id"):
        assert cache.load_index("paper", tmp_path) is None


@pytest.fixture
def staging(tmp_path, monkeypatch):
    fitz = pytest.importorskip("fitz")
    module = script("ingest-effects-staging")
    reg = tmp_path / "registers"
    reg.mkdir()
    for name in [
        "BANDS_magnitude_bands.csv",
        "VONT_variable_ontology.csv",
        "FAM_family_registry.csv",
    ]:
        (reg / name).write_bytes((ROOT / "schema/registers" / name).read_bytes())
    write_csv(
        reg / "EV_evidence_register.csv", [], [f.name for f in fields(EvidenceUnit)]
    )
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    quote = "Lower slopes favour agroforestry establishment."
    with fitz.open() as doc:
        doc.new_page().insert_text((50, 50), "Paper\n" + quote)
        doc.save(corpus / "paper.pdf")
    source = {
        "source_id": "paper",
        "citation": "Author (2026). Paper.",
        "doi": "10.1234/paper",
        "artifact_sha1": hashlib.sha1((corpus / "paper.pdf").read_bytes()).hexdigest(),
    }
    write_csv(reg / "SRC_source_register.csv", [source])
    identity = {**source, "doi_verified": "true", "title_verified": ""}
    queue = tmp_path / "queue.csv"
    write_csv(queue, [identity])
    monkeypatch.setattr(module, "REG", reg)
    monkeypatch.setattr(module, "CORPUS", corpus)
    monkeypatch.setattr(module, "QUEUE", queue)
    unit = dict(
        evidence_id="ev_test",
        source_id="paper",
        nbs_id="agroforestry",
        suitability_family_id="agroforestry__planted_silvoarable",
        variable="slope",
        use_role="structural_suitability",
        evidence_type="literature_relationship",
        claim_basis="modelled",
        claim_scope="practice_technology",
        extraction_confidence="high",
        quote=quote,
        page=1,
        locator_type="page",
        relationship={"direction": "decreasing"},
        context={"practice_as_described": "agroforestry"},
        ruleset_version="v1.7.0",
    )
    return module, unit, identity


def test_staging_valid_source_passes_and_historical_t4_stamp_allowed(staging):
    module, unit, _ = staging
    assert module.gate([unit], {"structural_suitability"}) == []
    unit["ruleset_version"] = "v1.6.16"
    assert module.gate([unit], {"structural_suitability"}) == []


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("page", 0, "integer page"),
        ("page", True, "integer page"),
        ("page", -1, "integer page"),
        ("quote", "", "non-empty"),
        ("reviewer_ok", True, "approval"),
        ("nbs_id", "wetland_management", "family does not belong"),
        ("source_id", "../paper", "source_id"),
        ("unexpected", "value", "unknown evidence fields"),
    ],
)
def test_staging_refuses_invalid_units(staging, key, value, message):
    module, unit, _ = staging
    unit[key] = value
    assert any(message in e for e in module.gate([unit], {"structural_suitability"}))


def test_staging_refuses_unverified_identity_and_changed_artifact(staging):
    module, unit, identity = staging
    identity["doi_verified"] = "false"
    write_csv(module.QUEUE, [identity])
    assert any(
        "DOI is not verified" in e
        for e in module.gate([unit], {"structural_suitability"})
    )
    identity["doi_verified"] = "true"
    write_csv(module.QUEUE, [identity])
    with (module.CORPUS / "paper.pdf").open("ab") as f:
        f.write(b"\n% changed")
    assert any(
        "hash differs" in e for e in module.gate([unit], {"structural_suitability"})
    )


def test_staging_requires_role_opt_in_and_duplicate_free_batch(staging):
    module, unit, _ = staging
    assert any("not allowed" in e for e in module.gate([unit]))
    assert any(
        "duplicate evidence_id" in e
        for e in module.gate([unit, unit], {"structural_suitability"})
    )


def test_append_refuses_changed_id_before_any_write(tmp_path):
    p = tmp_path / "EV.csv"
    row = {
        "evidence_id": "one",
        "quote": "original",
        "relationship": '{"a": 1, "b": 2}',
        "reviewer_ok": "true",
        "review_state": "",
    }
    write_csv(p, [row])
    before = p.read_bytes()
    assert (
        migrate_effects.append_to_register(
            [{**row, "relationship": {"b": 2, "a": 1}, "reviewer_ok": False}], p
        )
        == 0
    )
    assert p.read_bytes() == before
    with pytest.raises(ValueError, match="existing evidence differs"):
        migrate_effects.append_to_register(
            [{**row, "evidence_id": "two"}, {**row, "quote": "different"}], p
        )
    assert p.read_bytes() == before
    with pytest.raises(ValueError, match="duplicate evidence_id"):
        migrate_effects.append_to_register([{**row, "evidence_id": "two"}] * 2, p)
    assert p.read_bytes() == before


def test_promotion_is_pending_preserves_access_and_refuses_unverified(
    tmp_path, monkeypatch
):
    module = script("promote-queue-to-src")
    monkeypatch.setattr(module, "CORPUS", tmp_path)
    fitz = pytest.importorskip("fitz")
    with fitz.open() as doc:
        doc.new_page().insert_text((50, 50), "Paper")
        doc.save(tmp_path / "paper.pdf")
    q = dict(
        source_id="paper",
        nbs_id="agroforestry",
        citation="Paper",
        doi="10.1234/paper",
        doi_verified="true",
        note="",
        target_library_path="library/paper.pdf",
        access_status="paywalled",
        url="https://example.org",
    )
    args = SimpleNamespace(
        nbs="agroforestry", date="2026-10-28", run_id="test", extractor="test"
    )
    meta = dict(
        benchmark_tier="medium",
        venue_type="peer_reviewed_journal",
        method_type="empirical",
    )
    row = module.build_row(q, meta, [], args)
    assert row["extraction_status"] == "pending"
    assert row["vars_extracted"] == row["extraction_date"] == row["extractor"] == ""
    assert row["doi"] == q["doi"] and row["access_status"] == "paywalled"
    with pytest.raises(ValueError, match="not verified"):
        module.build_row({**q, "doi_verified": "false"}, {}, [], args)
    with pytest.raises(ValueError, match="title is not verified"):
        module.build_row({**q, "doi": ""}, {}, [], args)


def test_discovery_preserves_long_titles_unicode_and_exact_queries(tmp_path):
    module = script("register-discovery")
    prefix = "Authors and shared title prefix " * 5
    assert module._norm_title(prefix + "one") != module._norm_title(prefix + "two")
    assert module._norm_title("森林恢复") != module._norm_title("农林系统")
    query = "a  AND  b " * 1000
    assert (
        module._sections(
            "## Verbatim queries\n" + query + "\n## Results\nnone",
            r"^## Verbatim queries$",
        )
        == query.strip()
    )
    p = tmp_path / "bad.json"
    p.write_text('{"unexpected": []}')
    with pytest.raises(ValueError, match="expected a candidate list"):
        module._load_candidates(p)


def test_search_log_keeps_same_day_runs_and_actual_date(tmp_path):
    p = tmp_path / "SRCH.csv"
    params = dict(
        nbs="agroforestry",
        table="T4",
        category="grey",
        search_terms="query",
        ruleset_version="v1.7.0",
        search_date="2026-10-20",
        path=p,
    )
    a = search_log.log_search(**params, run_id="one")
    b = search_log.log_search(**params, run_id="two")
    assert a["search_id"] != b["search_id"]
    assert a["search_date"] == "2026-10-20"
    assert len(search_log.rows(p)) == 2
    search_log.log_search(**params, run_id="two")
    assert len(search_log.rows(p)) == 2


def test_learning_cursor_detects_changed_feedback_without_inflated_replays(
    tmp_path, monkeypatch
):
    review = tmp_path / "reviews.csv"
    log = tmp_path / "learnings.csv"
    monkeypatch.setattr(learnings, "REVIEW_LOG", review)
    monkeypatch.setattr(learnings, "LEARNINGS_LOG", log)
    row = dict(
        evidence_id="one",
        reviewer="person",
        decision="ok",
        reason="",
        note="reviewed",
        date="2026-10-20",
    )
    write_csv(review, [row])
    learnings.record("Verified adjustment after reading feedback")
    assert learnings.status()["unprocessed"] == 0
    write_csv(review, [row, {**row, "date": "2026-10-21"}])
    assert learnings.status()["unprocessed"] == 0
    write_csv(review, [row, {**row, "decision": "query", "note": "Missing units"}])
    assert learnings.status()["unprocessed"] == 1
    assert learnings.status()["distinct_reviews"] == 1
    assert learnings.status()["tracking_basis"] == "review_content_fingerprints"


def test_learning_legacy_cursor_uses_last_correction_and_drop_denominator(
    tmp_path, monkeypatch
):
    review, log = tmp_path / "reviews.csv", tmp_path / "learnings.csv"
    monkeypatch.setattr(learnings, "REVIEW_LOG", review)
    monkeypatch.setattr(learnings, "LEARNINGS_LOG", log)
    write_csv(
        review,
        [
            dict(
                evidence_id=str(i),
                reviewer="p",
                decision="drop" if i == 0 else "query",
                reason="off_scope",
            )
            for i in range(3)
        ],
    )
    write_csv(log, [{"reviewed_through": "10"}, {"reviewed_through": "2"}])
    status = learnings.status()
    assert status["unprocessed"] == 1
    assert status["off_scope_rate_pct_of_drops"] == 100
    assert status["tracking_basis"] == "legacy_count_estimate"


def test_discovery_table_counts_use_exact_tags_even_for_known_sources(
    tmp_path, monkeypatch
):
    module = script("register-discovery")
    columns = next(csv.reader((ROOT / "pipeline/acquisition_queue.csv").open()))
    queue = tmp_path / "queue.csv"
    write_csv(
        queue,
        [
            {
                c: (
                    "known"
                    if c == "source_id"
                    else "Known paper"
                    if c == "citation"
                    else "agroforestry"
                    if c == "nbs_id"
                    else "T3"
                    if c == "tables"
                    else ""
                )
                for c in columns
            }
        ],
    )
    src = tmp_path / "SRC.csv"
    write_csv(src, [], ["source_id", "citation", "doi"])
    monkeypatch.setattr(module, "QUEUE", queue)
    monkeypatch.setattr(module, "SRC", src)
    monkeypatch.setattr(module, "LOGS", tmp_path / "logs")
    candidates = tmp_path / "candidates.json"
    candidates.write_text(
        json.dumps(
            [
                dict(
                    candidate_id="known",
                    citation="Known paper",
                    tables="T3",
                    process="updated_lit",
                )
            ]
        )
    )
    report = tmp_path / "report.md"
    report.write_text(
        '# Report\n## Verbatim queries\n"agroforestry" AND drought\n## Results\nOne candidate\n'
    )
    calls = []
    monkeypatch.setattr(module.search_log, "log_search", lambda **kw: calls.append(kw))
    assert (
        module.main(
            [
                "agroforestry",
                "--date",
                "2026-10-20",
                "--ruleset",
                "v1.7.0",
                "--candidates",
                f"lit={candidates}",
                "--reports",
                f"lit={report}",
                "--log-names",
                "lit=report.md",
            ]
        )
        == 0
    )
    assert len(calls) == 1
    assert calls[0]["table"] == "T3" and calls[0]["n_included"] == "1"
    assert calls[0]["search_date"] == "2026-10-20"
    assert len(list(csv.DictReader(queue.open()))) == 1


def test_code_acquisition_pins_branch_and_refuses_custom_id_collision(
    tmp_path, monkeypatch
):
    import base64
    from nbs_ruralscan.ingest import github

    commit = "a" * 40
    body = base64.b64encode(b"weight = 1\n").decode()
    calls = []

    def api(args):
        calls.append(args)
        return json.dumps({"sha": commit}) if "/commits/" in args[0] else body

    monkeypatch.setattr(github, "_gh", api)
    first = github.acquire_file("team/repo", "main", "a/rules.py", tmp_path)
    second = github.acquire_file("team/repo", commit, "b/rules.py", tmp_path)
    assert first.commit == commit and first.source_id != second.source_id
    assert calls[1][0].endswith(f"?ref={commit}")
    github.acquire_file("team/repo", commit, "a/rules.py", tmp_path, source_id="fixed")
    before = (tmp_path / "fixed.txt").read_bytes()
    with pytest.raises(github.GithubIngestError, match="Refusing to replace"):
        github.acquire_file(
            "team/other", commit, "a/rules.py", tmp_path, source_id="fixed"
        )
    assert (tmp_path / "fixed.txt").read_bytes() == before


def test_download_intake_does_not_verify_a_bibliography_match(tmp_path):
    fitz = pytest.importorskip("fitz")
    intake = script("intake-downloads")
    pdf = tmp_path / "wrong.pdf"
    with fitz.open() as doc:
        for i in range(4):
            doc.new_page().insert_text(
                (50, 50),
                "Unrelated coastal fisheries study"
                if i < 3
                else "References: Smith. Contour ridges raise maize yields in semi-arid Zimbabwe.",
            )
        doc.save(pdf)
    ok, message = intake.title_check(
        pdf,
        "Smith (2020). Contour ridges raise maize yields in semi-arid Zimbabwe. Journal.",
    )
    assert not ok and "reference" in message


def test_acquisition_retry_keeps_existing_artifact_on_failure(tmp_path, monkeypatch):
    pytest.importorskip("fitz")
    module = script("acquire-queue")
    dest = tmp_path / "paper.pdf"
    dest.write_bytes(b"original bytes")

    def fail(*args, **kw):
        raise AcquireError("network unavailable")

    monkeypatch.setattr(module, "acquire", fail)
    assert not module._acquire("paper", "https://example.org/p.pdf", dest)
    assert dest.read_bytes() == b"original bytes"


def test_active_rules_have_complete_matching_snapshot():
    active = ROOT / ".agents/skills/source-command-extract-evidence"
    snapshot = ROOT / ".agents/skills/_versions/v1.8.0"
    for relative in ["SKILL.md", "references/defects.md"]:
        assert (active / relative).read_bytes() == (snapshot / relative).read_bytes()
    for name in [
        "T4_review_contract.md",
        "T3_T6_extraction_contract.md",
        "DIRECTION_ADDENDUM.md",
    ]:
        assert (ROOT / ".agents/skills/extraction_contracts" / name).read_bytes() == (
            snapshot / "contracts" / name
        ).read_bytes()
    assert (ROOT / ".claude/commands/extract-evidence.md").read_bytes() == (
        snapshot / "extract-evidence_command.md"
    ).read_bytes()


def test_followup_projection_preserves_answers_but_detects_changed_weight():
    from nbs_ruralscan.schema_tools.t4_coverage import (
        check_review_followups,
        followup_key,
    )

    context = {
        "model_use": {"weight_path_pct": [25, 20, 20]},
        "later_annotation": "new",
    }
    item: dict = dict(
        evidence_id="e",
        reviewer="p",
        note="weight query",
        status="resolved",
        resolution="Answered",
        resolution_evidence_ids=["e"],
    )
    item["resolution_checks"] = [
        dict(
            evidence_id="e",
            field="context",
            json_keys=["model_use"],
            sha256=hashlib.sha256(
                json.dumps(
                    {"model_use": context["model_use"]},
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest(),
        )
    ]
    followups = {followup_key(item): item}
    evidence = {"e": {"context": json.dumps(context)}}
    assert check_review_followups([], evidence, followups) == []
    context["model_use"]["weight_path_pct"][0] = 50
    evidence["e"]["context"] = json.dumps(context)
    assert any(
        "corrective field changed" in e
        for e in check_review_followups([], evidence, followups)
    )
    evidence["e"]["context"] = "{}"
    assert any(
        "corrective field changed" in e
        for e in check_review_followups([], evidence, followups)
    )


def test_identity_comparison_ignores_author_abbreviations_but_not_title_or_doi():
    from nbs_ruralscan.ingest.integrity import source_identity_differs

    source = {
        "doi": "10.1234/p",
        "citation": "A, B; C, D (2020). Original title. Journal.",
    }
    verified = {
        "doi": "10.1234/p",
        "citation": "A et al. (2020). Original title. Journal.",
    }
    assert not source_identity_differs(source, verified)
    assert source_identity_differs(
        source, {**verified, "citation": "A (2020). Different paper. Journal."}
    )
    assert source_identity_differs(source, {**verified, "doi": "10.1234/other"})


def test_ingestion_audit_is_read_only_and_distinguishes_holds(tmp_path):
    from nbs_ruralscan.schema_tools.ingestion_audit import audit

    write_csv(
        tmp_path / "pipeline/acquisition_queue.csv",
        [dict(source_id="new", status="acquired", doi="", title_verified="true")],
    )
    write_csv(
        tmp_path / "schema/registers/SRC_source_register.csv",
        [
            dict(
                source_id="legacy",
                extraction_status="swept",
                source_kind="paper",
                library_path="library/legacy.pdf",
            )
        ],
    )
    write_csv(
        tmp_path / "schema/registers/EV_evidence_register.csv",
        [dict(evidence_id="orphan", source_id="absent")],
    )
    before = {p: p.read_bytes() for p in tmp_path.rglob("*.csv")}
    result = audit(tmp_path)
    assert result["findings_by_kind"] == {
        "acquired_not_registered": 1,
        "completion_needs_inventory": 1,
        "evidence_without_source": 1,
        "source_identity_hold": 1,
    }
    assert all(p.read_bytes() == data for p, data in before.items())


def test_discovery_does_not_claim_unsearched_process_table_pairs(tmp_path, monkeypatch):
    module = script("register-discovery")
    cols = next(csv.reader((ROOT / "pipeline/acquisition_queue.csv").open()))
    queue, src = tmp_path / "queue.csv", tmp_path / "SRC.csv"
    write_csv(queue, [{c: ("old" if c == "source_id" else "") for c in cols}])
    write_csv(src, [], ["source_id", "citation", "doi"])
    monkeypatch.setattr(module, "QUEUE", queue)
    monkeypatch.setattr(module, "SRC", src)
    monkeypatch.setattr(module, "LOGS", tmp_path / "logs")
    report = tmp_path / "report.md"
    report.write_text("# Report\n## Verbatim queries\nquery\n")
    paths = []
    for lane, table, process in [("lit", "T3", "updated_lit"), ("grey", "T6", "grey")]:
        p = tmp_path / f"{lane}.json"
        p.write_text(
            json.dumps(
                [
                    dict(
                        candidate_id=lane,
                        citation=f"{lane} paper",
                        tables=table,
                        process=process,
                    )
                ]
            )
        )
        paths.append(f"{lane}={p}")
    marks = []
    monkeypatch.setattr(module.search_log, "log_search", lambda **kw: None)
    monkeypatch.setattr(module.ledger, "mark", lambda *args, **kw: marks.append(args))
    assert (
        module.main(
            [
                "agroforestry",
                "--date",
                "2026-10-20",
                "--ruleset",
                "v1.7.0",
                "--candidates",
                *paths,
                "--reports",
                f"lit={report}",
                f"grey={report}",
                "--log-names",
                "lit=lit.md",
                "grey=grey.md",
                "--ledger",
                "updated_lit=done",
                "grey=done",
            ]
        )
        == 0
    )
    assert {(m[1], m[2]) for m in marks} == {("T3", "updated_lit"), ("T6", "grey")}


def test_append_dry_run_checks_collision_without_writing(tmp_path):
    path = tmp_path / "EV.csv"
    write_csv(path, [dict(evidence_id="one", quote="original")])
    before = path.read_bytes()
    assert (
        migrate_effects.append_to_register(
            [dict(evidence_id="two", quote="new")], path, dry_run=True
        )
        == 1
    )
    with pytest.raises(ValueError, match="existing evidence differs"):
        migrate_effects.append_to_register(
            [dict(evidence_id="one", quote="changed")], path, dry_run=True
        )
    assert path.read_bytes() == before
