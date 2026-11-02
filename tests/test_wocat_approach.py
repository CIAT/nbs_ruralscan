"""Approach/technology isolation, locator fidelity and immutable hydration."""

import copy
import hashlib
import json
from io import BytesIO

import pytest

from nbs_ruralscan.ingest import wocat_approach as a

SID = "wocat_anr_approach_1971"
PAYLOAD = {
    "id": 1971,
    "selected_version": {
        "id": 1972,
        "approach": 1971,
        "status": 4,
        "name": {"en": "ANR"},
        "description": {"en": "Existing wildlings.\r\n600-700 per hectare."},
        "technologies": [{"description": {"en": "UNRELATED"}}],
        "weaknesses_compiler": [{"weakness": {"en": "Research missing"}}],
    },
}


def page(payload=PAYLOAD, kind="approaches"):
    return (
        '<script type="application/json" data-sveltekit-fetched data-url="/api/database/'
        + kind
        + '/1971/">'
        + json.dumps({"body": json.dumps(payload)})
        + "</script>"
    )


def test_identity_and_technology_isolation():
    assert a.parse(page(), 1971) == PAYLOAD
    with pytest.raises(ValueError):
        a.parse(page(kind="technologies"), 1971)
    wrong = copy.deepcopy(PAYLOAD)
    wrong["selected_version"]["approach"] = 999
    with pytest.raises(ValueError):
        a.parse(page(wrong), 1971)
    with pytest.raises(ValueError):
        a.approach_id("wocat_1971_2017")


def test_missing_english_and_unpublished_rejected():
    for change in (
        {"description": {"fr": "texte"}},
        {"status": 1},
        {"is_deleted": True},
    ):
        p = copy.deepcopy(PAYLOAD)
        p["selected_version"].update(change)
        with pytest.raises(ValueError):
            a.parse(page(p), 1971)


def test_native_text_and_nested_narrative_remain_locatable():
    md = a.render(PAYLOAD, SID)
    assert "## description\n\nExisting wildlings. 600-700 per hectare." in md
    assert "[0].weakness: Research missing" in md
    assert "UNRELATED" not in md
    reordered = copy.deepcopy(PAYLOAD)
    reordered["selected_version"] = dict(
        reversed(list(reordered["selected_version"].items()))
    )
    assert a.render(reordered, SID) == md


def test_changed_snapshot_rejected_before_cache_write(tmp_path, monkeypatch):
    monkeypatch.setattr(
        a.urllib.request, "urlopen", lambda *args, **kw: BytesIO(page().encode())
    )
    with pytest.raises(ValueError, match="transcript changed"):
        a.acquire(SID, tmp_path, expected_sha1="0" * 40)
    assert not list(tmp_path.iterdir())
    expected = hashlib.sha1(a.render(PAYLOAD, SID).encode()).hexdigest()
    out = a.acquire(SID, tmp_path, expected_sha1=expected)
    assert hashlib.sha1(out.read_bytes()).hexdigest() == expected


def test_fresh_dashboard_hydration_uses_exact_archive_without_network(
    tmp_path, monkeypatch
):
    import csv
    import importlib.util
    from pathlib import Path

    script = Path(__file__).resolve().parents[1] / "scripts/hydrate-corpus.py"
    spec = importlib.util.spec_from_file_location("hydrate_approach_test", script)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    archive = tmp_path / "methodology/audits/batch"
    archive.mkdir(parents=True)
    md = a.render(PAYLOAD, SID)
    (archive / f"{SID}.md").write_text(md)
    src = tmp_path / "sources.csv"
    row = dict(
        source_id=SID,
        library_path="",
        source_kind="website",
        source_category="tool",
        url="https://wocat.net/en/database/approaches/1971/",
        artifact_sha1=hashlib.sha1(md.encode()).hexdigest(),
    )
    with src.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        w.writeheader()
        w.writerow(row)
    monkeypatch.setattr(h, "ROOT", tmp_path)
    monkeypatch.setattr(h, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(h, "SRC_CSV", src)
    monkeypatch.setattr(h, "library_root", lambda: None)

    def no_network(*args, **kwargs):
        raise AssertionError("Archived source must hydrate offline")

    monkeypatch.setattr(h, "_fetch", no_network)
    monkeypatch.setattr(a, "acquire", no_network)
    assert h.main([]) == 0
    assert (h.CACHE / f"{SID}.md").read_text() == md
