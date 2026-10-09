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


VONT = ROOT / "schema" / "registers" / "VONT_variable_ontology.csv"
_STRENGTH = {
    "slight": "by a small amount",
    "moderate": "by a moderate amount",
    "strong": "by a large amount",
}
_DESIGN = {
    "meta_analysis": "a pooled result across many studies (meta-analysis)",
    "systematic_review": "a systematic review of other studies",
    "review": "a review citing other studies",
    "rct": "a randomised trial",
    "quasi_experimental": "a controlled comparison (not randomised)",
    "observational": "an observational study (measured, no experimental control)",
    "case_study": "a single case study",
    "model": "a modelled (simulated) result",
    "expert": "an expert statement",
    "practitioner_rating": "a practitioner's rating on a fixed scale (WOCAT compiler)",
}
_SIG = {
    "sig": "statistically significant",
    "ns": "NOT statistically significant",
    "not_reported": "significance not reported",
}
_BASIS = {
    "primary_measured": "measured by the authors themselves",
    "primary_measurement": "measured by the authors themselves",
    "table": "read from a table in the paper",
    "figure_read": "read off a figure",
    "cited_secondary": "cited by the authors from another study (not their own measurement)",
    "expert_assertion": "asserted by the authors without a measurement",
    "modelled": "produced by a model, not measured",
}
_SCOPE = {
    "practice_technology": "about the practice in general",
    "species_specific": "about one species only",
    "crop_specific": "about one crop only",
}
_ROLE = {
    "nbs_effect": "an EFFECT of the practice on people or land (feeds the hazard and scorecard tables)",
    "asset_vulnerability": "DAMAGE to the works themselves by a hazard (asset threat)",
    "operational_risk": "an enabling / implementation factor (next-steps guidance, not an effect)",
    "structural_suitability": "a condition for where the practice can be established (suitability table)",
}
_INCOME = {
    "low": "low-income",
    "lower_middle": "lower-middle-income",
    "upper_middle": "upper-middle-income",
    "high": "high-income",
    "lic_lmic": "low / lower-middle-income",
    "mixed": "mixed-income",
}


FAM = ROOT / "schema" / "registers" / "FAM_family_registry.csv"


def _families() -> dict[str, str]:
    """family id → 'name; name' of its sub-practices (what the practice actually is)."""
    out: dict[str, list[str]] = {}
    try:
        for r in csv.DictReader(FAM.open(encoding="utf-8")):
            fid = (r.get("suitability_family_id") or "").strip()
            if fid and r.get("name"):
                out.setdefault(fid, []).append(r["name"].strip())
    except OSError:
        pass
    return {k: "; ".join(v) for k, v in out.items()}


def _labels() -> dict[str, str]:
    try:
        return {
            r["canonical_variable_id"]: r["label"]
            for r in csv.DictReader(VONT.open(encoding="utf-8"))
        }
    except OSError:
        return {}


def _num(rel: dict) -> str:
    unit = str(rel.get("unit") or "").replace("_per_", " per ").replace("_", " ")
    m = rel.get("magnitude")
    lo, hi = rel.get("magnitude_low"), rel.get("magnitude_high")
    met = str(rel.get("metric") or "")
    if met == "contrast" and rel.get("value_with") is not None:
        return f"{rel.get('value_with')} with the practice vs {rel.get('value_without')} without ({unit})".strip()
    if met == "complete_contrast":
        return "an all-or-nothing contrast (e.g. a harvest only with the practice)"
    if met == "ordinal_rating":
        v = rel.get("source_scale_value")
        return (
            f"rated {v} on the compiler's −3…+3 scale"
            if v is not None
            else "a compiler rating"
        )
    if met == "pct_change" and m is not None:
        return f"a change of {m} %"
    if m is not None:
        return f"{m} {unit}".strip()
    if lo is not None or hi is not None:
        return f"{lo}–{hi} {unit}".strip()
    if met == "narrative":
        return "stated in words only, no number"
    return ""


def practice_line(r: dict, fams: dict[str, str]) -> str:
    nbs = r["nbs_id"].replace("_", " ")
    fid = r.get("suitability_family_id") or ""
    if not fid or fid.endswith("__cross_family"):
        return f"Practice: {nbs} (no sub-practice stated in the source — pooled across the whole NbS)."
    short = fid.split("__", 1)[-1].replace("_", " ")
    names = fams.get(fid)
    return f"Practice: {nbs} → {short}" + (f" ({names})" if names else "") + "."


def plain_words(
    r: dict,
    rel: dict,
    ctx: dict,
    labels: dict[str, str],
    fams: dict[str, str] | None = None,
) -> dict:
    """Plain-English sentences for a reviewer: what the unit claims, how it was
    established, and in what context. The codes stay in the JSON for the record."""
    var = labels.get(r["variable"], r["variable"].replace("_", " "))
    practice = r["nbs_id"].replace("_", " ")
    d = str(rel.get("direction") or "")
    hazard_var = r["variable"].endswith("_hazard")
    if r["use_role"] == "asset_vulnerability":
        hz = (ctx.get("hazard_type") or "the hazard").replace("_", " ")
        verb = {
            "positive": f"is damaged by {hz}",
            "negative": f"withstands {hz}",
            "none": f"is not clearly affected by {hz}",
        }.get(d, f"— {d}")
        claim = f"The works of {practice} {verb}"
    elif d in ("positive", "negative", "none"):
        if hazard_var:
            verb = {
                "negative": "REDUCES the impact of",
                "positive": "WORSENS the impact of",
                "none": "has NO clear effect on",
            }[d]
            obj = var.replace(" hazard", "").replace(" risk", "")
        else:
            verb = {
                "positive": "INCREASES",
                "negative": "DECREASES",
                "none": "has NO clear effect on",
            }[d]
            obj = var
        claim = f"{practice.capitalize()} {verb} {obj}"
    else:
        claim = d or "(no direction coded)"
    bits = []
    if d in ("positive", "negative") and rel.get("strength_class") in _STRENGTH:
        bits.append(_STRENGTH[rel["strength_class"]])
    elif d in ("positive", "negative"):
        bits.append("size not stated")
    n = _num(rel)
    if n:
        bits.append(n)
    if rel.get("significance") in _SIG:
        bits.append(_SIG[rel["significance"]])
    claim_sentence = claim + (" — " + "; ".join(bits) if bits else "") + "."
    how = []
    if rel.get("design") in _DESIGN:
        how.append(_DESIGN[rel["design"]])
    if r.get("claim_basis") in _BASIS:
        how.append(_BASIS[r["claim_basis"]])
    if r.get("claim_scope") in _SCOPE:
        how.append(
            _SCOPE[r["claim_scope"]]
            + (f" ({r.get('taxon')})" if r.get("taxon") else "")
        )
    how_sentence = ("This is " + "; ".join(how) + ".") if how else ""
    where = []
    if ctx.get("hazard_type"):
        hz = str(ctx["hazard_type"]).replace("_", " ")
        sev = ctx.get("hazard_severity")
        if sev and sev != "unspecified":
            where.append(
                f"under a {hz} the authors call {sev}"
                + (
                    f" (their words: “{ctx.get('severity_cue')}”)"
                    if ctx.get("severity_cue")
                    else ""
                )
            )
        else:
            where.append(f"under {hz} (intensity not characterised by the authors)")
    if ctx.get("country"):
        c = ctx["country"]
        where.append("in " + (", ".join(c) if isinstance(c, list) else str(c)))
    if ctx.get("income_group") in _INCOME:
        where.append(f"a {_INCOME[ctx['income_group']]} setting")
    if ctx.get("farming_system"):
        where.append(f"farming system: {str(ctx['farming_system']).replace('_', ' ')}")
    if ctx.get("comparator") == "existing_forest":
        where.append(
            "measured on EXISTING forest (or forest loss), not on a restoration"
        )
    if ctx.get("comparator") == "existing_wetland":
        where.append("measured on EXISTING wetlands, not on a restoration")
    where_sentence = ("Context: " + "; ".join(where) + ".") if where else ""
    compared = str(rel.get("outcome_raw") or "").strip()
    return {
        "practice": practice_line(r, fams or {}),
        "compared": ("What the paper compared: " + compared + ".") if compared else "",
        "role": _ROLE.get(r["use_role"], r["use_role"]),
        "claim": claim_sentence,
        "how": how_sentence,
        "where": where_sentence,
    }


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
    labels = _labels()
    fams = _families()
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
                "plain": plain_words(r, rel, ctx, labels, fams),
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
