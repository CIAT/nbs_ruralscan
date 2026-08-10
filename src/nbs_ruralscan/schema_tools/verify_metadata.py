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
"""

from __future__ import annotations

import csv
import json
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"
REPORT = ROOT / "pipeline" / "metrics" / "doi_audit.json"
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


def _crossref(doi: str) -> dict | None:
    doi = doi.replace("https://doi.org/", "").strip()
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto={MAILTO}"
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers=_UA), timeout=12
        ) as r:
            return json.load(r)["message"]
    except Exception:
        return None


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
    if "doi_verified" not in cols:
        cols.append("doi_verified")
        for r in rows:
            r.setdefault("doi_verified", "")
    return rows, cols


def verify() -> int:
    rows, cols = _rows()
    pending = [r for r in rows if (r.get("status") or "pending") == "pending"]
    with_doi = [r for r in pending if (r.get("doi") or "").strip()]

    def work(r: dict) -> dict:
        m = _crossref(r["doi"])
        cite = r.get("citation", "")
        if not m:
            return {
                "source_id": r["source_id"],
                "doi": r["doi"],
                "verified": False,
                "reason": "doi_unresolved",
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

    with ThreadPoolExecutor(max_workers=6) as ex:
        results = {res["source_id"]: res for res in ex.map(work, with_doi)}

    verified = mismatched = 0
    for r in rows:
        res = results.get(r["source_id"])
        if not res:
            continue
        if res["verified"]:
            r["doi_verified"] = "true"
            r["citation"] = res["authoritative_citation"]  # authoritative rebuild
            verified += 1
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
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        {
            "checked": len(with_doi),
            "verified": verified,
            "failed": mismatched,
            "results": list(results.values()),
        },
        REPORT.open("w", encoding="utf-8"),
        indent=1,
    )
    print(
        f"verify: checked={len(with_doi)} verified={verified} failed(blanked)={mismatched}"
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
    print("usage: verify_metadata.py [verify|check]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
