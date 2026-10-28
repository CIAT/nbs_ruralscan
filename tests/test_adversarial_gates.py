"""Adversarial staging attacks use isolated registers; no production mutations."""

import hashlib
import json
from types import SimpleNamespace

import pytest

import test_pipeline_hardening as helpers
from test_pipeline_hardening import script, write_csv
from nbs_ruralscan.schema_tools import migrate_effects


@pytest.fixture(name="staging")
def staging_fixture(tmp_path, monkeypatch):
    return helpers.staging.__wrapped__(tmp_path, monkeypatch)


def errors(staging, **changes):
    module, unit, _ = staging
    return module.gate([{**unit, **changes}], {"structural_suitability"})


@pytest.mark.parametrize(
    "quote", ["(English: fabricated translated claim)", "x (English: fabricated claim)"]
)
def test_translation_cannot_replace_native_provenance(staging, quote):
    assert any("native quote" in e for e in errors(staging, quote=quote))


@pytest.mark.parametrize("number", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_nested_claims_refused(staging, number):
    assert any(
        "JSON" in e
        for e in errors(staging, relationship={"nested": {"threshold": number}})
    )


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("evidence_id", 10),
        ("evidence_id", []),
        ("reviewer_ok", 0),
        ("attribution", {"author": "someone"}),
    ],
)
def test_scalar_type_tricks_refused_without_crash(staging, key, value):
    assert any("invalid evidence unit" in e for e in errors(staging, **{key: value}))


@pytest.mark.parametrize(
    ("quote_key", "page_key"),
    [
        ("justification_quote", "justification_page"),
        ("selection_justification", "selection_justification_page"),
    ],
)
def test_supplementary_claim_must_match_its_own_page(staging, quote_key, page_key):
    assert any(
        "not verbatim" in e
        for e in errors(
            staging,
            **{
                quote_key: "Invented rationale absent from the real source.",
                page_key: 1,
            },
        )
    )
    assert any(
        "supplied together" in e
        for e in errors(staging, **{quote_key: staging[1]["quote"]})
    )
    assert errors(staging, **{quote_key: staging[1]["quote"], page_key: 1}) == []
    assert any(
        "unreadable" in e
        for e in errors(staging, **{quote_key: staging[1]["quote"], page_key: 2})
    )


def test_duplicate_json_keys_rejected_before_gate_or_append(
    staging, tmp_path, monkeypatch
):
    module, unit, _ = staging
    path = tmp_path / "staging.json"
    payload = json.dumps([unit]).replace(
        '"source_id": "paper"', '"source_id": "wrong", "source_id": "paper"'
    )
    path.write_text(payload)
    monkeypatch.setattr(
        module, "gate", lambda *args: pytest.fail("must fail before gate")
    )
    with pytest.raises(SystemExit):
        module.main([str(path), "--dry-run", "--allow-structural"])


def test_registered_wrong_pdf_cannot_pass_with_correct_hash(staging):
    module, unit, identity = staging
    fitz = pytest.importorskip("fitz")
    path = module.CORPUS / "paper.pdf"
    path.unlink()
    with fitz.open() as doc:
        doc.new_page().insert_text((50, 50), unit["quote"])
        doc.save(path)
    source = {
        **identity,
        "citation": "Author (2026). Coastal coral ecosystem conservation management.",
    }
    source["artifact_sha1"] = hashlib.sha1(path.read_bytes()).hexdigest()
    write_csv(module.REG / "SRC_source_register.csv", [source])
    write_csv(module.QUEUE, [source])
    assert any("source document identity hold" in e for e in errors(staging))


def test_append_bad_later_row_writes_nothing_even_in_dry_run(tmp_path):
    path = tmp_path / "EV.csv"
    write_csv(path, [], ["evidence_id", "relationship"])
    original = path.read_bytes()
    rows = [
        {"evidence_id": "good", "relationship": {"direction": "decreasing"}},
        {"evidence_id": "bad", "relationship": {"value": float("nan")}},
    ]
    for dry_run in (True, False):
        with pytest.raises(ValueError, match="JSON"):
            migrate_effects.append_to_register(rows, path, dry_run=dry_run)
        assert path.read_bytes() == original


def test_existing_duplicate_ids_block_append(tmp_path):
    path = tmp_path / "EV.csv"
    write_csv(path, [{"evidence_id": "one"}, {"evidence_id": "one"}])
    before = path.read_bytes()
    with pytest.raises(ValueError, match="existing register.*duplicate"):
        migrate_effects.append_to_register([{"evidence_id": "new"}], path)
    assert path.read_bytes() == before


def test_atomic_publication_failure_preserves_whole_register(tmp_path, monkeypatch):
    path = tmp_path / "EV.csv"
    write_csv(path, [{"evidence_id": "one"}])
    before = path.read_bytes()

    def failed_publication(*args):
        raise OSError("simulated replacement failure")

    monkeypatch.setattr(migrate_effects, "atomic_write", failed_publication)
    with pytest.raises(OSError, match="replacement"):
        migrate_effects.append_to_register([{"evidence_id": "new"}], path)
    assert path.read_bytes() == before


def test_promotion_wrong_readable_pdf_is_not_identity(staging):
    module, unit, identity = staging
    promotion = script("promote-queue-to-src")
    promotion.CORPUS = module.CORPUS
    q = {
        **identity,
        "nbs_id": "agroforestry",
        "citation": "Author (2026). Coastal coral ecosystem conservation management.",
        "target_library_path": "library/paper.pdf",
    }
    with pytest.raises(ValueError, match="source document identity hold"):
        promotion.build_row(q, {}, [], SimpleNamespace(nbs="agroforestry"))


@pytest.mark.parametrize("table", ["source", "queue"])
def test_duplicate_source_identity_cannot_shadow_other_row(staging, table):
    module, unit, identity = staging
    path = module.QUEUE if table == "queue" else module.REG / "SRC_source_register.csv"
    write_csv(path, [identity, identity])
    assert any("duplicate source_id" in e for e in errors(staging))


def test_cli_reports_invalid_ids_instead_of_crashing(staging, tmp_path):
    module, unit, _ = staging
    path = tmp_path / "staging.json"
    path.write_text(json.dumps([{**unit, "evidence_id": ["invalid"]}]))
    assert module.main([str(path), "--dry-run", "--allow-structural"]) == 1


def test_promotion_preserves_all_queue_scopes_and_checks_exact_membership(staging):
    module, _, identity = staging
    promotion = script("promote-queue-to-src")
    promotion.CORPUS = module.CORPUS
    q = {
        **identity,
        "nbs_id": "forest_restoration|agroforestry",
        "target_library_path": "library/paper.pdf",
        "note": "",
        "url": "https://example.org/paper",
    }
    meta = dict(
        benchmark_tier="medium",
        venue_type="peer_reviewed_journal",
        method_type="empirical",
    )
    args = SimpleNamespace(nbs="forest_restoration", date="2026-10-28")
    assert promotion.build_row(q, meta, [], args)["nbs_ids"] == q["nbs_id"]
    args.nbs = "agroforestry"
    assert promotion.build_row(q, meta, [], args)["nbs_ids"] == q["nbs_id"]
    args.nbs = "forest"
    with pytest.raises(ValueError, match="absent from queue-declared scopes"):
        promotion.build_row(q, meta, [], args)


@pytest.mark.parametrize(
    "existing_scopes", ["forest_restoration", "forest_restoration|agroforestry"]
)
def test_promotion_existing_source_cannot_hide_untracked_scope(
    staging, tmp_path, monkeypatch, existing_scopes
):
    module, _, identity = staging
    promotion = script("promote-queue-to-src")
    promotion.QUEUE = module.QUEUE
    promotion.SRC = module.REG / "SRC_source_register.csv"
    q = {**identity, "status": "acquired", "nbs_id": "forest_restoration|agroforestry"}
    write_csv(promotion.QUEUE, [q])
    write_csv(promotion.SRC, [{"source_id": "paper", "nbs_ids": existing_scopes}])
    before = promotion.SRC.read_bytes()
    ids, meta = tmp_path / "ids.txt", tmp_path / "meta.json"
    ids.write_text("paper\n")
    meta.write_text("{}")
    monkeypatch.setattr(
        "sys.argv",
        [
            "promote-queue-to-src",
            "--run-id",
            "test",
            "--nbs",
            "forest_restoration",
            "--sources",
            str(ids),
            "--meta",
            str(meta),
            "--dry-run",
        ],
    )
    assert promotion.main() == (0 if existing_scopes == q["nbs_id"] else 1)
    assert promotion.SRC.read_bytes() == before
