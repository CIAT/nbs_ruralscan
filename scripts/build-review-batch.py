#!/usr/bin/env python3
"""Build a review batch for the simple review page (docs/review.html).

    python3 scripts/build-review-batch.py <batch_id> --title "..." --items items.csv [--notes "..."]

`items.csv` columns: evidence_id, question (why this unit needs a human look). Writes
`docs/review/<batch_id>.json` (the units with their fields + the quote), renders a page crop
per unit to `docs/review/img/<evidence_id>.png` (quote highlighted; whole page at low DPI
when the quote cannot be located), and updates `docs/review/index.json`. Reads only the
register + the cached PDF; never edits evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.review import REASON_CODES  # noqa: E402

EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"
CORPUS = ROOT / ".cache" / "corpus"
OUT = ROOT / "docs" / "review"
IMG = OUT / "img"
DPI = 110
#: same base the dashboard uses (vfSharePointUrl) — team-openable link built from SRC.library_path
SP_BASE = (
    "https://cgiar.sharepoint.com/sites/Alliance-ClimateActionNetZero/Shared%20Documents/"
    "ClimateActionNetZero/1_Projects/"
)


def sharepoint_url(library_path: str, page: int | None = None) -> str | None:
    from urllib.parse import quote

    if not library_path:
        return None
    url = SP_BASE + "/".join(quote(part) for part in library_path.split("/"))
    return f"{url}#page={page}" if page else url


MARGIN = 28  # pt around the quote block


def _j(s: str) -> dict:
    try:
        return json.loads(s) if s else {}
    except json.JSONDecodeError:
        return {}


def render_crop(pdf: Path, page_no: int, quote: str, dest: Path) -> str:
    """Crop the cited page around the quote (highlighted); fall back to the whole page."""
    doc = fitz.open(pdf)
    if page_no < 1 or page_no > len(doc):
        return "page out of range"
    page = doc[page_no - 1]
    # locate by the first and last ~50 chars of the quote (page text layers wrap lines)
    q = re.sub(r"\s+", " ", quote).strip()
    rects = []
    for probe in (q[:50], q[-50:], q[:30]):
        if len(probe) < 12:
            continue
        hits = page.search_for(probe)
        if hits:
            rects += hits
            if len(rects) >= 2 or probe == q[:30]:
                break
    note = "quote highlighted"
    if rects:
        r = rects[0]
        for x in rects[1:]:
            r |= x
        clip = fitz.Rect(
            max(page.rect.x0, r.x0 - MARGIN),
            max(page.rect.y0, r.y0 - MARGIN * 3),
            min(page.rect.x1, r.x1 + MARGIN),
            min(page.rect.y1, r.y1 + MARGIN * 3),
        )
        # widen to the full text width so the sentence context stays readable
        clip.x0, clip.x1 = page.rect.x0 + 20, page.rect.x1 - 20
        for h in rects:
            page.add_highlight_annot(h)
        pix = page.get_pixmap(dpi=DPI, clip=clip)
    else:
        note = "quote not located in the text layer — whole page shown"
        pix = page.get_pixmap(dpi=72)
    dest.parent.mkdir(parents=True, exist_ok=True)
    pix.save(dest)
    return note


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("batch_id")
    ap.add_argument("--title", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--notes", default="")
    a = ap.parse_args(argv)
    items = {
        r["evidence_id"]: (r.get("question") or "")
        for r in csv.DictReader(open(a.items, encoding="utf-8"))
    }
    src = {r["source_id"]: r for r in csv.DictReader(SRC.open(encoding="utf-8"))}
    units = []
    missing = []
    with EV.open(newline="", encoding="utf-8") as f:
        ev = {r["evidence_id"]: r for r in csv.DictReader(f)}
    for eid, question in items.items():
        r = ev.get(eid)
        if not r:
            missing.append(eid)
            continue
        rel, ctx = _j(r.get("relationship", "")), _j(r.get("context", ""))
        s = src.get(r["source_id"], {})
        crop, crop_note = None, "no cached PDF"
        pdf = CORPUS / f"{r['source_id']}.pdf"
        page = int(r["page"]) if (r.get("page") or "").isdigit() else 0
        if pdf.exists() and page:
            dest = IMG / f"{eid}.png"
            crop_note = render_crop(pdf, page, r.get("quote", ""), dest)
            crop = f"review/img/{eid}.png"
        elif (r.get("locator_type") or "") == "section":
            crop_note = f"transcript section {r.get('locator')} (no page image)"
        units.append(
            {
                "evidence_id": eid,
                "source_id": r["source_id"],
                "citation": s.get("citation", ""),
                "benchmark_tier": s.get("benchmark_tier", ""),
                "nbs_id": r["nbs_id"],
                "use_role": r["use_role"],
                "variable": r["variable"],
                "suitability_family_id": r.get("suitability_family_id", ""),
                "claim_scope": r.get("claim_scope", ""),
                "claim_basis": r.get("claim_basis", ""),
                "page": page or r.get("page"),
                "locator": r.get("locator", ""),
                "quote": r.get("quote", ""),
                "relationship": {
                    k: rel.get(k)
                    for k in (
                        "direction",
                        "strength_class",
                        "metric",
                        "magnitude",
                        "magnitude_low",
                        "magnitude_high",
                        "value_with",
                        "value_without",
                        "unit",
                        "design",
                        "significance",
                        "outcome_raw",
                    )
                    if rel.get(k) not in (None, "")
                },
                "context": {
                    k: ctx.get(k)
                    for k in (
                        "hazard_type",
                        "hazard_severity",
                        "severity_cue",
                        "country",
                        "income_group",
                        "farming_system",
                        "comparator",
                        "note",
                    )
                    if ctx.get(k) not in (None, "")
                },
                "question": question,
                "crop": crop,
                "crop_note": crop_note,
                "pdf_url": sharepoint_url(s.get("library_path", ""), page or None),
                "library_path": s.get("library_path", ""),
            }
        )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{a.batch_id}.json").write_text(
        json.dumps(
            {
                "batch": {
                    "id": a.batch_id,
                    "title": a.title,
                    "date": date.today().isoformat(),
                    "notes": a.notes,
                    "n": len(units),
                },
                "reasons": REASON_CODES,
                "units": units,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    idx_p = OUT / "index.json"
    idx = (
        json.loads(idx_p.read_text(encoding="utf-8"))
        if idx_p.exists()
        else {"batches": []}
    )
    idx["batches"] = [b for b in idx["batches"] if b["id"] != a.batch_id] + [
        {
            "id": a.batch_id,
            "title": a.title,
            "date": date.today().isoformat(),
            "n": len(units),
            "file": f"review/{a.batch_id}.json",
        }
    ]
    idx_p.write_text(
        json.dumps(idx, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(
        f"{len(units)} unit(s) → docs/review/{a.batch_id}.json; missing ids: {missing}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
