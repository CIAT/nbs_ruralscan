"""Acquisition bundles use synthetic content and mocked remote responses only."""

import base64
import copy
import hashlib
from io import BytesIO
import json
from pathlib import Path
import shutil

import pytest

from nbs_ruralscan.ingest import github, wocat, wocat_approach
from nbs_ruralscan.ingest.source_publication import SourceSnapshot
from nbs_ruralscan.schema_tools import publication


COMMIT = "a" * 40
CODE = b"// Synthetic code\nvar slopeThreshold = 17;\n"
TECH_ID = "wocat_999_2026"
APPROACH_ID = "wocat_fixture_approach_999"
PAYLOAD = {
    "id": 999,
    "selected_version": {
        "id": 42,
        "approach": 999,
        "name": {"en": "Synthetic restoration"},
        "description": {"en": "Synthetic adoption narrative."},
        "status": 4,
        "is_deleted": False,
        "country": "KE",
    },
}


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


def page(payload):
    outer = {"body": json.dumps(payload)}
    return (
        '<script type="application/json" data-sveltekit-fetched '
        'data-url="/api/database/approaches/999/">' + json.dumps(outer) + "</script>"
    ).encode()


@pytest.fixture(params=["technology", "approach"])
def adapter(request, tmp_path, monkeypatch):
    corpus = tmp_path / "corpus"
    payload = copy.deepcopy(PAYLOAD)
    if request.param == "technology":
        monkeypatch.setattr(wocat, "fetch_payload", lambda _: copy.deepcopy(payload))
        sid = TECH_ID

        def acquire():
            return wocat.acquire(sid, corpus)

    else:
        monkeypatch.setattr(
            wocat_approach.urllib.request,
            "urlopen",
            lambda *a, **kw: BytesIO(page(payload)),
        )
        sid = APPROACH_ID

        def acquire():
            return wocat_approach.acquire(sid, corpus)

    return acquire, corpus, sid, payload


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("position", [1, 2, 3])
@pytest.mark.parametrize("after", [False, True])
def test_wocat_failure_restores_entire_source_bundle(
    adapter, monkeypatch, existing, position, after
):
    acquire, corpus, _, payload = adapter
    if existing:
        acquire()
    before = inventory(corpus)
    payload["selected_version"]["name"]["en"] = "Updated synthetic restoration"
    replace = publication.os.replace
    attempts = 0

    def failing_replace(src, dest):
        nonlocal attempts
        if Path(dest).parent == corpus:
            attempts += 1
            if attempts == position:
                if after:
                    replace(src, dest)
                raise OSError("synthetic replacement failure")
        return replace(src, dest)

    monkeypatch.setattr(publication.os, "replace", failing_replace)
    with pytest.raises(OSError, match="synthetic replacement failure"):
        acquire()
    assert inventory(corpus) == before


def test_wocat_triplet_preserves_existing_serialization_and_rerenders(adapter):
    acquire, corpus, sid, payload = adapter
    out = acquire()
    source = corpus / f"{sid}.source.json"
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1).encode()
    assert source.read_bytes() == raw
    render = wocat.render if sid == TECH_ID else wocat_approach.render
    assert out.read_text(encoding="utf-8") == render(payload, sid)
    meta = json.loads((corpus / f"{sid}.meta.json").read_bytes())
    assert meta["source_id"] == sid
    assert meta["source_sha1"] == hashlib.sha1(raw).hexdigest()
    assert meta["render_sha1"] == hashlib.sha1(out.read_bytes()).hexdigest()
    payload["selected_version"]["name"]["en"] = "Refreshed"
    acquire()
    assert out.read_text(encoding="utf-8") == render(payload, sid)


def test_wocat_drift_before_publication_preserves_competing_file(adapter, monkeypatch):
    acquire, corpus, sid, _ = adapter
    original = SourceSnapshot.publish
    competitor = corpus / f"{sid}.md"

    def drift(snapshot, *args, **kwargs):
        corpus.mkdir()
        competitor.write_bytes(b"competing transcript")
        return original(snapshot, *args, **kwargs)

    monkeypatch.setattr(SourceSnapshot, "publish", drift)
    with pytest.raises(ValueError, match="changed during preparation"):
        acquire()
    assert [p.name for p in corpus.iterdir()] == [competitor.name]
    assert competitor.read_bytes() == b"competing transcript"


def test_wocat_staged_transcript_tamper_rejected_before_any_output(
    adapter, monkeypatch
):
    acquire, corpus, sid, _ = adapter
    manifest = publication._manifest

    def tamper(root, *args, **kwargs):
        (root / f"{sid}.md").write_text("unrelated transcript", encoding="utf-8")
        return manifest(root, *args, **kwargs)

    monkeypatch.setattr(publication, "_manifest", tamper)
    with pytest.raises(ValueError, match="artifact/provenance mismatch"):
        acquire()
    assert not corpus.exists()


def test_technology_id_mismatch_and_unsafe_source_id_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(wocat, "fetch_payload", lambda _: dict(PAYLOAD, id=888))
    with pytest.raises(ValueError, match="artifact/provenance mismatch"):
        wocat.acquire(TECH_ID, tmp_path / "corpus")
    with pytest.raises(ValueError):
        wocat.acquire("wocat_999_../../escape", tmp_path / "corpus")
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("position", [1, 2])
@pytest.mark.parametrize("after", [False, True])
def test_github_new_pair_rolls_back_exclusive_publication(
    tmp_path, monkeypatch, position, after
):
    corpus = tmp_path / "corpus"
    monkeypatch.setattr(github, "_gh", lambda _: base64.b64encode(CODE).decode())
    link = publication.os.link
    attempts = 0

    def failing_link(src, dest):
        nonlocal attempts
        attempts += 1
        if attempts == position:
            if after:
                link(src, dest)
            raise OSError("synthetic exclusive creation failure")
        return link(src, dest)

    monkeypatch.setattr(publication.os, "link", failing_link)
    with pytest.raises(OSError, match="synthetic exclusive creation failure"):
        github.acquire_file("fixture/repo", COMMIT, "rules.js", corpus, "fixture_code")
    assert not inventory(corpus)


def test_github_cache_keeps_original_provenance_and_returned_relative_path(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(github, "_gh", lambda _: base64.b64encode(CODE).decode())
    result = github.acquire_file("fixture/repo", COMMIT, "rules.js", "corpus")
    assert result.cached.startswith("corpus/")
    before = inventory(tmp_path / "corpus")
    github.acquire_file("fixture/repo", COMMIT, "rules.js", "corpus")
    assert inventory(tmp_path / "corpus") == before
    assert Path(result.cached).read_bytes() == CODE


def test_github_content_fetch_drift_is_not_adopted(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus"

    def fetching(_):
        corpus.mkdir()
        (corpus / "fixture_code.txt").write_bytes(b"competing code")
        return base64.b64encode(CODE).decode()

    monkeypatch.setattr(github, "_gh", fetching)
    with pytest.raises(ValueError, match="changed during preparation"):
        github.acquire_file("fixture/repo", COMMIT, "rules.js", corpus, "fixture_code")
    assert (corpus / "fixture_code.txt").read_bytes() == b"competing code"
    assert not (corpus / "fixture_code.meta.json").exists()


@pytest.mark.parametrize("alias", ["symlink", "hardlink"])
def test_adapter_destinations_reject_aliases_before_content_fetch(
    tmp_path, monkeypatch, alias
):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    external = tmp_path / "external"
    external.write_bytes(CODE)
    target = corpus / "fixture_code.txt"
    if alias == "symlink":
        target.symlink_to(external)
    else:
        target.hardlink_to(external)
    calls = []
    monkeypatch.setattr(github, "_gh", lambda args: calls.append(args))
    with pytest.raises(ValueError):
        github.acquire_file("fixture/repo", COMMIT, "rules.js", corpus, "fixture_code")
    assert not calls and external.read_bytes() == CODE


def test_source_bundle_dry_run_validates_without_creating_outputs(tmp_path):
    artifact = tmp_path / "corpus/source.txt"
    snapshot = SourceSnapshot.capture([artifact])
    checked = []

    def validate(stage):
        checked.append((stage / artifact.name).read_bytes())

    assert snapshot.publish({artifact: CODE}, validate, create_only=True, dry_run=True)
    assert checked == [CODE] and not artifact.exists()


def test_github_cli_selects_corpus(tmp_path, monkeypatch):
    calls = []

    def interrogate(*args):
        calls.append(args)
        return {"acquired": [], "candidates": []}

    monkeypatch.setattr(github, "interrogate", interrogate)
    assert github.main(["fixture/repo", COMMIT, "--corpus-dir", str(tmp_path)]) == 0
    assert calls[0][-1] == tmp_path


def test_wocat_acquire_cli_stops_on_incomplete_recovery(tmp_path, monkeypatch):
    calls = []

    def acquire(sid, corpus):
        calls.append((sid, corpus))
        raise publication.PublicationRecoveryError(
            tmp_path, ["synthetic rollback failure"]
        )

    monkeypatch.setattr(wocat, "acquire", acquire)
    with pytest.raises(publication.PublicationRecoveryError):
        wocat.main(
            ["acquire", TECH_ID, "wocat_998_2026", "--corpus-dir", str(tmp_path)]
        )
    assert calls == [(TECH_ID, tmp_path)]


def test_wocat_emit_uses_selected_input_tree_without_compiler_data(
    tmp_path, monkeypatch
):
    # Real empty maps/registers exercise file routing without changing scientific rules.
    from nbs_ruralscan.recipe.cell_synthesis import load_bands

    selected = tmp_path / "selected"
    schema = selected / "schema"
    (schema / "lookups").mkdir(parents=True)
    (schema / "registers").mkdir()
    source_schema = wocat.ROOT / "schema"
    for name in (
        "wocat_impact_map.csv",
        "wocat_hazard_map.csv",
        "wb_income_groups.csv",
    ):
        shutil.copy2(source_schema / "lookups" / name, schema / "lookups" / name)
    for name in (
        "BANDS_magnitude_bands.csv",
        "FAM_family_registry.csv",
        "EV_evidence_register.csv",
    ):
        original = source_schema / "registers" / name
        if name == "BANDS_magnitude_bands.csv":
            shutil.copy2(original, schema / "registers" / name)
        else:
            (schema / "registers" / name).write_text(
                original.read_text().splitlines()[0] + "\n"
            )
    corpus = tmp_path / "external-corpus"
    corpus.mkdir()
    (corpus / f"{TECH_ID}.source.json").write_text(json.dumps(PAYLOAD))
    (corpus / f"{TECH_ID}.md").write_text(wocat.render(PAYLOAD, TECH_ID))
    output = tmp_path / "staging.json"
    for name in ("ROOT", "CORPUS", "LOOKUPS", "EV_CSV"):
        monkeypatch.setattr(wocat, name, tmp_path / "poison")
    assert load_bands(schema / "registers/BANDS_magnitude_bands.csv")
    assert (
        wocat.main(
            [
                "emit",
                TECH_ID,
                "--nbs",
                "fixture",
                "--root",
                str(selected),
                "--corpus-dir",
                str(corpus),
                "--out",
                str(output),
            ]
        )
        == 0
    )
    assert json.loads(output.read_text()) == []
