"""discovery_sources — Lens adapter shape, AGRIS manual helpers (2026-10-07)."""

from __future__ import annotations

import pytest

from nbs_ruralscan.ingest import discovery_sources as ds

REC = {
    "lens_id": "012-345-678-901-234",
    "title": "Zaï pits and sorghum yield in drought years.",
    "year_published": 2021,
    "authors": [
        {"display_name": "A. Author"},
        {"first_name": "B.", "last_name": "Writer"},
    ],
    "external_ids": [
        {"type": "doi", "value": "10.1000/xyz"},
        {"type": "pmid", "value": "1"},
    ],
    "source": {"title": "Field Crops Research"},
    "abstract": "We measured sorghum yield under zaï in a drought year.",
    "open_access": {"is_oa": True, "colour": "green"},
    "languages": ["en"],
    "source_urls": [
        {"type": "html", "url": "https://x/html"},
        {"type": "pdf", "url": "https://x/p.pdf"},
    ],
    "publication_type": "journal article",
}


class _Resp:
    def __init__(self, status, payload):
        self.status_code = status
        self._p = payload
        self.text = str(payload)

    def json(self):
        return self._p


class _Session:
    def __init__(self, status=200, payload=None):
        self.status, self.payload, self.calls = status, payload or {"data": [REC]}, []

    def post(self, url, json=None, headers=None, timeout=None):
        self.calls.append((url, json, headers))
        return _Resp(self.status, self.payload)


def test_lens_record_becomes_a_registrar_candidate():
    c = ds.lens_to_candidate(REC, process="updated_lit", tables="T3")
    assert c["candidate_id"] == "lens_012345678901234"
    assert c["citation"].startswith(
        "A. Author, B. Writer (2021). Zaï pits and sorghum yield in drought years."
    )
    assert c["doi"] == "10.1000/xyz" and c["url"] == "https://x/p.pdf"  # pdf preferred
    assert c["oa_status"] == "oa" and c["language"] == "en" and c["tables"] == "T3"
    assert c["source_db"] == "lens" and c["process"] == "updated_lit"


def test_lens_search_posts_query_string_and_year_filter():
    s = _Session()
    out = ds.lens_search("zai drought", token="t", size=5, year_from=2015, session=s)
    assert len(out) == 1
    url, body, headers = s.calls[0]
    assert url == ds.LENS_API and headers["Authorization"] == "Bearer t"
    assert body["size"] == 5 and "bool" in body["query"]
    assert body["query"]["bool"]["filter"][0]["range"]["year_published"]["gte"] == 2015


def test_lens_search_refuses_without_token(monkeypatch):
    monkeypatch.delenv("LENS_TOKEN", raising=False)
    with pytest.raises(RuntimeError):
        ds.lens_search("x", session=_Session())


def test_lens_search_raises_on_http_error():
    with pytest.raises(RuntimeError):
        ds.lens_search("x", token="t", session=_Session(401, {"message": "no"}))


def test_agris_is_manual_url_and_template():
    url = ds.agris_search_url('"zaï" rendement sécheresse', lang="fr")
    assert url.startswith("https://agris.fao.org/search/fr?query=")
    assert ds.agris_search_url("x", lang="zz9").startswith(
        "https://agris.fao.org/search/en?"
    )
    t = ds.agris_candidate_template("zai drought", tables="T6")
    assert t["process"] == "grey" and t["tables"] == "T6" and t["source_db"] == "agris"
    assert "systematic review" in ds.review_type_block()
