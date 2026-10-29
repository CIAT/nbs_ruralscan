"""DOI <-> citation verification gate for the acquisition queue.

Why: discovery agents assembled `doi` + `citation` from search snippets. Some DOIs
resolve to a DIFFERENT paper than the citation (wrong-paper), are dead, or carry the
wrong author. A wrong DOI would fetch the wrong PDF -> contamination at extraction.
This is the deterministic gate that makes that class impossible to ship silently.

Two commands:
* `verify` (online, manual/pre-handover) -- round-trips each DOI through Crossref,
  asserts the resolved title matches the citation (token overlap >= THRESH), stamps
  the `doi_verified` column (true/false), and rebuilds verified citations to the
  authoritative Crossref record. Writes a report to pipeline/metrics/doi_audit.json.
* `check` (offline, CI + generate) -- NO network. Asserts every pending queue row with
  a non-empty `doi` has `doi_verified=true`. Any `doi` present but not verified is a
  build-flagged defect (acquire by title or run `verify`). Extraction must refuse
  `doi_verified != true` rows (title-only acquisition).

The trust anchor is the TITLE, never the DOI, until the DOI is round-trip verified.

DOI-less sources (grey literature, agency manuals, WOCAT technology sheets; ruleset v1.6.0):
* `verify-titles` (offline) -- for every acquired queue row with NO doi and a cached
  artifact in `.cache/corpus/`, asserts the citation's TITLE appears in the opening pages
  of the cached file itself (token coverage >= TITLE_THRESH) and stamps `title_verified`
  (true/false). This guards the failure the DOI lock exists for -- the wrong document in
  the cache (cf. Nyamadzawo 2013, a different paper filed under its name). The acquire
  URL must also be the publisher's own domain (fao.org, wocat.net, iucn.org, ...), which
  is recorded in `url` and checked at review, not here.
* `check` additionally FAILS if a source registered in SRC failed its title check.
Extraction may proceed on a source only if `doi_verified=true`, or it has no DOI and
`title_verified=true`.
"""

from __future__ import annotations

import csv
import json
import time
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"
REPORT = ROOT / "pipeline" / "metrics" / "doi_audit.json"
CORPUS = ROOT / ".cache" / "corpus"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"
TITLE_THRESH = 0.8
MAILTO = "p.steward@cgiar.org"
THRESH = 0.5
_UA = {"User-Agent": f"nbs-ruralscan/1.0 (mailto:{MAILTO})"}
_STOP = set(
    "the and for with from into their which under across between within based using "
    "study effects impact assessment analysis review journal international climate change".split()
)


def _toks(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if len(w) > 3} - _STOP


def _overlap(crossref_title: str, citation: str) -> float:
    ct = _toks(crossref_title)
    return len(ct & _toks(citation)) / max(1, len(ct)) if ct else 0.0


def _crossref(doi: str) -> tuple[dict | None, str]:
    """(record, outcome) where outcome is `ok` · `not_found` · `unreachable`.

    The distinction is load-bearing and was added after a 2026-10-16 run blanked 113 VALID
    DOIs: every transport failure (rate limit, timeout, reset) looked identical to "this DOI
    does not resolve", and the caller blanks on failure. Crossref rate-limits a parallel
    sweep readily, so an unreachable DOI must leave the row untouched; only a definitive
    404 may blank one.
    """
    doi = doi.replace("https://doi.org/", "").strip()
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto={MAILTO}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=_UA), timeout=20
            ) as r:
                return json.load(r)["message"], "ok"
        except urllib.error.HTTPError as e:  # noqa: PERF203
            if e.code == 404:
                return None, "not_found"
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 * (attempt + 1))
                continue
            return None, "unreachable"
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None, "unreachable"


def _authoritative_citation(m: dict) -> str:
    fams = [a.get("family", "") for a in (m.get("author") or []) if a.get("family")]
    au = (fams[0] if fams else "") + (" et al." if len(fams) > 1 else "")
    try:
        yr = str((m.get("issued", {}).get("date-parts") or [[None]])[0][0] or "")
    except Exception:
        yr = ""
    title = (m.get("title") or [""])[0]
    cont = m.get("container-title") or [""]
    cont = cont[0] if cont else ""
    return f"{au} ({yr}). {title}. {cont}.".strip()


def _rows() -> tuple[list[dict], list[str]]:
    with QUEUE.open(encoding="utf-8") as f:
        rd = csv.DictReader(f)
        rows = list(rd)
        cols = list(rd.fieldnames or [])
    for c in ("doi_verified", "title_verified"):
        if c not in cols:
            cols.append(c)
            for r in rows:
                r.setdefault(c, "")
    return rows, cols


def _title_of(citation: str) -> str:
    """The title segment of an 'Author (Year). Title. Publisher.' citation."""
    c = citation or ""
    i = c.find("). ")
    body = c[i + 3 :] if i >= 0 else c
    j = body.find(". ")
    return body[:j] if j > 0 else body


def _head_text(source_id: str, pages: int = 3) -> str | None:
    """Text of the opening pages of the cached artifact, or None if not cached."""
    for ext in (".pdf", ".txt", ".html", ".md"):
        f = CORPUS / f"{source_id}{ext}"
        if not f.exists():
            continue
        if ext != ".pdf":
            return f.read_text(encoding="utf-8", errors="ignore")[:20000]
        import fitz  # PyMuPDF

        with fitz.open(f) as doc:
            return " ".join(doc[i].get_text() for i in range(min(pages, len(doc))))
    return None


def _squash(s: str) -> str:
    """NFKC, lower, alnum only, no spaces — survives letter-spaced / ligature titles
    ("F o r e s t s a n d ﬂ o o d s", caught 2026-10-08 on a CIFOR cover page)."""
    import re
    import unicodedata

    return re.sub(r"[^a-z0-9]+", "", unicodedata.normalize("NFKC", s or "").lower())


def _title_coverage(title: str, text: str) -> float:
    tt = _toks(title)
    cov = len(tt & _toks(text)) / len(tt) if tt else 0.0
    if cov < TITLE_THRESH:
        st = _squash(title)
        if len(st) >= 20 and st in _squash(text):
            return 1.0
    return cov


def _title_page_in_body(source_id: str, title: str) -> int | None:
    """PDF page (1-indexed) whose text covers the citation title, or None.

    A chapter inside a larger cached artefact is legitimate — the team decided on
    2026-10-16 that the SharePoint library edition wins even when it is a whole book
    (Jacobson: book page = chapter page + 206). The head-pages check then fails on the
    book's front matter although the cited document is right there, so on failure the
    title is sought across the body. A WRONG book still fails: it has no page covering
    the chapter title.
    """
    f = CORPUS / f"{source_id}.pdf"
    if not f.exists():
        return None
    import fitz  # PyMuPDF

    with fitz.open(f) as doc:
        prev = ""
        for i in range(min(len(doc), 500)):
            page = doc[i].get_text()
            # a title may straddle a page turn; score the 2-page window
            # in the BODY the title must appear contiguously: scattered title words across
            # two pages are not an identity (Donato 2012 cached for Bock 1978 scored 0.8)
            window = prev + " " + page
            key = _squash(title)[:40]
            if (
                len(key) >= 20
                and key in _squash(window)
                and not _cited_not_titled(title, window)
            ):
                return i + 1
            prev = page
    return None


_REF_HEAD = None


def _cited_not_titled(title: str, text: str) -> bool:
    """True when the title appears only as a CITATION on the page: inside a reference list
    (after a References / Literature cited / Bibliography heading) or as a reference entry
    (a publication year just before it). Caught 2026-10-29: Donato et al. 2012 was cached
    for Bock et al. 1978 and passed because Bock's title sits in Donato's reference list."""
    import re

    global _REF_HEAD
    if _REF_HEAD is None:
        _REF_HEAD = re.compile(
            r"(references|literature cited|bibliography|références|referencias|"
            r"bibliografía|referências)",
        )
    st, sx = _squash(title), _squash(text)
    key = st[:40]
    pos = sx.find(key) if len(key) >= 20 else -1
    if pos < 0:
        return False  # token-coverage match without a contiguous title: leave as is
    head = _REF_HEAD.search(sx[:pos])
    if head:
        return True
    before = sx[max(0, pos - 60) : pos]
    return bool(
        re.search(r"(19|20)\d{2}[a-z]?$", before[-12:])
        or re.search(r"(19|20)\d{2}", before[-20:])
    )


#: note marker for an identity a person confirmed by eye (garbled cover text layer, a
#: chapter in a book with an author-less citation); verify-titles never downgrades it
HAND_CONFIRMED = "[title: confirmed by hand]"


def verify_titles() -> int:
    rows, cols = _rows()
    passed = failed = uncached = 0
    for r in rows:
        if (r.get("doi") or "").strip() or r.get("status") not in (
            "acquired",
            "extracted",
        ):
            continue
        if (r.get("url") or "").strip() and not (
            r.get("target_library_path") or ""
        ).strip():
            continue  # code / web snapshot: pinned by URL + commit, no title page to check
        if (
            HAND_CONFIRMED in (r.get("note") or "")
            and r.get("title_verified") == "true"
        ):
            passed += 1
            continue  # a person confirmed identity where the text layer cannot show it
        text = _head_text(r["source_id"])
        if text is None:
            uncached += 1
            continue
        title = _title_of(r.get("citation", ""))
        cov = _title_coverage(title, text)
        ok = cov >= TITLE_THRESH
        body_page = None
        if not ok:
            body_page = _title_page_in_body(r["source_id"], title)
        r["title_verified"] = "true" if ok else "false"
        if ok:
            passed += 1
        else:
            failed += 1
            note = (r.get("note") or "").strip()
            flag = f"TITLE CHECK FAILED (coverage {cov:.2f}): cached file may be the wrong document."
            if body_page is not None:
                flag += f" Body-only match at PDF page {body_page} may be a reference; verify chapter identity manually."
            if flag not in note:
                r["note"] = (note + " | " if note else "") + flag
    with QUEUE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"verify-titles: passed={passed} failed={failed} not_cached={uncached}")
    return 0


def verify() -> int:
    rows, cols = _rows()
    pending = [r for r in rows if (r.get("status") or "pending") == "pending"]
    with_doi = [r for r in pending if (r.get("doi") or "").strip()]

    def work(r: dict) -> dict:
        m, outcome = _crossref(r["doi"])
        cite = r.get("citation", "")
        if not m:
            return {
                "source_id": r["source_id"],
                "doi": r["doi"],
                "verified": False,
                # `unreachable` means we never got an answer — it must NOT blank a DOI
                "reason": "doi_unresolved" if outcome == "not_found" else "unreachable",
            }
        ov = _overlap((m.get("title") or [""])[0], cite)
        return {
            "source_id": r["source_id"],
            "doi": r["doi"],
            "verified": ov >= THRESH,
            "overlap": round(ov, 2),
            "crossref_title": (m.get("title") or [""])[0][:120],
            "authoritative_citation": _authoritative_citation(m),
            "reason": "ok" if ov >= THRESH else "title_mismatch",
        }

    # 6 parallel workers rate-limited Crossref hard enough on 2026-10-16 that 117 of 152
    # lookups failed at once; the polite pool is small and the retry in `_crossref` carries
    # the rest.
    with ThreadPoolExecutor(max_workers=2) as ex:
        results = {res["source_id"]: res for res in ex.map(work, with_doi)}

    verified = mismatched = unreachable = 0
    for r in rows:
        res = results.get(r["source_id"])
        if not res:
            continue
        if res["verified"]:
            r["doi_verified"] = "true"
            r["citation"] = res["authoritative_citation"]  # authoritative rebuild
            verified += 1
        elif res["reason"] == "unreachable":
            # Crossref never answered: leave the row exactly as it was and report it
            unreachable += 1
        else:
            # DOI is wrong/dead: blank it, keep the (title-bearing) citation, flag.
            note = (r.get("note") or "").strip()
            r["doi_verified"] = "false"
            r["note"] = (note + " | " if note else "") + (
                f"DOI FAILED verification ({res['reason']}); original DOI blanked — acquire by TITLE."
            )
            r["doi"] = ""
            mismatched += 1

    with QUEUE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        {
            "checked": len(with_doi),
            "verified": verified,
            "failed": mismatched,
            "unreachable": unreachable,
            "results": list(results.values()),
        },
        REPORT.open("w", encoding="utf-8"),
        indent=1,
    )
    print(
        f"verify: checked={len(with_doi)} verified={verified} failed(blanked)={mismatched} "
        f"unreachable(left alone)={unreachable}"
    )
    return 0


def check() -> int:
    """Offline gate: any pending row with a DOI must be doi_verified=true."""
    rows, _ = _rows()
    bad = [
        r["source_id"]
        for r in rows
        if (r.get("status") or "pending") == "pending"
        and (r.get("doi") or "").strip()
        and (r.get("doi_verified") or "") != "true"
    ]
    registered = set()
    if SRC.exists():
        with SRC.open(encoding="utf-8") as f:
            registered = {r["source_id"] for r in csv.DictReader(f)}
    bad_title = [
        r["source_id"]
        for r in rows
        if not (r.get("doi") or "").strip()
        and (r.get("title_verified") or "") == "false"
        and r["source_id"] in registered
    ]
    if bad_title:
        print(
            f"METADATA CHECK FAILED: {len(bad_title)} registered DOI-less source(s) FAILED the "
            "title check (the cached file may be the wrong document):"
        )
        for s in bad_title[:20]:
            print(f"   - {s}")
        return 1
    if bad:
        print(
            f"METADATA CHECK FAILED: {len(bad)} queue row(s) carry an unverified DOI "
            f"(run verify_metadata.py verify, or blank the DOI + acquire by title):"
        )
        for s in bad[:20]:
            print(f"   - {s}")
        return 1
    print(
        "METADATA CHECK OK: every pending queue DOI is verified against its citation."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "check"
    if cmd == "verify":
        return verify()
    if cmd == "check":
        return check()
    if cmd == "verify-titles":
        return verify_titles()
    print("usage: verify_metadata.py [verify|verify-titles|check]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
