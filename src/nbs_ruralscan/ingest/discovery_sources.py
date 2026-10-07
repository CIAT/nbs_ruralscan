"""Bibliographic discovery sources beyond OpenAlex (search_protocol.md §Bibliographic sources).

Added 2026-10-07 after the ILRI "climate change × agri-food systems" umbrella-review protocol
(Mukherji, Haddaway, Eales) named sources our seed set lacked. Two were taken on:

* **Lens.org** — scriptable (free token for non-commercial use; env ``LENS_TOKEN``). Scholarly
  index with preprints and theses that OpenAlex misses. ``lens_search`` returns candidates in
  the shape ``scripts/register-discovery.py`` consumes (``candidate_id`` · ``citation`` · ``doi``
  · ``url`` · ``oa_status`` · ``language`` · ``process`` · ``tables`` · ``relevance_note``).
* **AGRIS** (FAO) — LMIC-heavy, multilingual agricultural grey literature. Its search sits
  behind a browser challenge (Cloudflare "Just a moment…" on any ``query=`` request, 2026-10-07)
  and it has no OAI-PMH or JSON endpoint, so it is a **manual, browser-run source**:
  ``agris_search_url`` builds the query URL; the human screens the result list and fills the
  candidate template (``agris_candidate_template``); the registrar logs it with
  ``searched_by=<handle>``. No scraping — a format with no handling rule is paused, not improvised.

Skipped on purpose (institutional / manual, low marginal yield for narrow NbS × hazard
questions): Web of Science, Scopus, CAB Abstracts, ProQuest theses, AGRICOLA, Google Scholar.

``REVIEW_TYPE_TERMS`` is the protocol's "study type" block (systematic review synonyms), reused
verbatim in our synthesis-first lanes.
"""

from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import quote_plus

import requests

LENS_API = "https://api.lens.org/scholarly/search"
AGRIS_SEARCH = "https://agris.fao.org/search/{lang}"
_TIMEOUT = 60

#: ILRI umbrella-review protocol Table 1, string #1 (study type), kept verbatim as a reusable
#: block for synthesis-first discovery (OR-joined; Lens/OpenAlex accept the quoted phrases).
REVIEW_TYPE_TERMS: tuple[str, ...] = (
    "systematic review",
    "systematically review*",
    "systematic evidence map*",
    "systematic literature review",
    "systematic map",
    "systematically map*",
    "scoping review",
    "evidence and gap map*",
    "evidence synthesis",
    "umbrella review",
    "review of review*",
    "overview of review*",
)

LENS_FIELDS = [
    "lens_id",
    "title",
    "year_published",
    "authors",
    "external_ids",
    "source",
    "abstract",
    "open_access",
    "languages",
    "source_urls",
    "publication_type",
]


def review_type_block() -> str:
    """The protocol's study-type string as one OR-joined block."""
    return " OR ".join(f'"{t}"' for t in REVIEW_TYPE_TERMS)


# ── Lens.org ──────────────────────────────────────────────────────────────────────────


def _lens_citation(rec: dict[str, Any]) -> str:
    authors = rec.get("authors") or []
    names = []
    for a in authors[:3]:
        n = a.get("display_name") or " ".join(
            x for x in (a.get("first_name"), a.get("last_name")) if x
        )
        if n:
            names.append(n)
    who = ", ".join(names) + (" et al." if len(authors) > 3 else "")
    year = rec.get("year_published") or "n.d."
    title = (rec.get("title") or "").strip().rstrip(".")
    src = (rec.get("source") or {}).get("title") or ""
    return f"{who} ({year}). {title}." + (f" {src}." if src else "")


def _lens_doi(rec: dict[str, Any]) -> str:
    for x in rec.get("external_ids") or []:
        if str(x.get("type") or "").lower() == "doi":
            return str(x.get("value") or "").strip()
    return ""


def _lens_url(rec: dict[str, Any]) -> str:
    urls = rec.get("source_urls") or []
    for pref in ("pdf", "html", "unknown"):
        for u in urls:
            if str(u.get("type") or "unknown").lower() == pref and u.get("url"):
                return str(u["url"])
    doi = _lens_doi(rec)
    return f"https://doi.org/{doi}" if doi else ""


def lens_to_candidate(
    rec: dict[str, Any], *, process: str = "updated_lit", tables: str = "T3|T6"
) -> dict[str, Any]:
    """One Lens scholarly record → registrar candidate (never a DOI we trust: the
    registrar runs ``verify_metadata.py verify``; title is the anchor)."""
    oa = rec.get("open_access") or {}
    colour = str(oa.get("colour") or "").lower()
    oa_status = (
        "oa"
        if oa.get("is_oa") or colour in {"gold", "green", "hybrid", "bronze"}
        else "unknown"
    )
    langs = rec.get("languages") or []
    return {
        "candidate_id": f"lens_{rec.get('lens_id', '').replace('-', '')}",
        "citation": _lens_citation(rec),
        "doi": _lens_doi(rec),
        "url": _lens_url(rec),
        "oa_status": oa_status,
        "language": langs[0] if langs else "",
        "process": process,
        "tables": tables,
        "method_subtype": str(rec.get("publication_type") or ""),
        "report_number_or_handle": f"lens:{rec.get('lens_id', '')}",
        "relevance_note": (rec.get("abstract") or "")[:220],
        "source_db": "lens",
    }


def lens_search(
    query: str,
    *,
    token: str | None = None,
    size: int = 50,
    year_from: int | None = None,
    process: str = "updated_lit",
    tables: str = "T3|T6",
    session: Any | None = None,
) -> list[dict[str, Any]]:
    """Run one Lens scholarly query (query-string syntax) → candidate dicts.

    ``token`` defaults to ``LENS_TOKEN``; raises ``RuntimeError`` when absent so a lane
    never silently returns nothing."""
    token = token or os.environ.get("LENS_TOKEN")
    if not token:
        raise RuntimeError("Lens token missing: set LENS_TOKEN (free, non-commercial)")
    q: dict[str, Any] = {"query_string": {"query": query, "default_operator": "AND"}}
    if year_from:
        q = {
            "bool": {
                "must": [q],
                "filter": [{"range": {"year_published": {"gte": int(year_from)}}}],
            }
        }
    body = {"query": q, "size": int(size), "include": LENS_FIELDS}
    http = session or requests
    resp = http.post(
        LENS_API,
        json=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=_TIMEOUT,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Lens {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    return [
        lens_to_candidate(r, process=process, tables=tables)
        for r in data.get("data") or []
    ]


# ── AGRIS (manual) ────────────────────────────────────────────────────────────────────


def agris_search_url(query: str, *, lang: str = "en") -> str:
    """The browser URL for an AGRIS query (``query`` is the form field; ``q`` is ignored)."""
    lang = lang if re.fullmatch(r"[a-z]{2}", lang or "") else "en"
    return AGRIS_SEARCH.format(lang=lang) + "?query=" + quote_plus(query)


def agris_candidate_template(
    query: str, *, lang: str = "en", tables: str = "T3|T6"
) -> dict[str, Any]:
    """What the human fills per screened AGRIS record (one dict per record); the registrar
    consumes the list as any other candidate file."""
    return {
        "candidate_id": "agris_<record id from the URL /search/<lang>/records/<id>>",
        "citation": "<Authors (year). Title. Source.> — copy from the record page",
        "doi": "<DOI from the record's Links block, else blank>",
        "url": "<handle / full-text link from the record's Links block>",
        "oa_status": "oa | unknown",
        "language": "<Language field on the record page>",
        "process": "grey",
        "tables": tables,
        "report_number_or_handle": "agris:<record id>",
        "relevance_note": "<one line: why it fits the lane>",
        "source_db": "agris",
        "_query": query,
        "_search_url": agris_search_url(query, lang=lang),
        "_searched_by": "<handle>",
        "_searched_on": "<YYYY-MM-DD>",
    }
