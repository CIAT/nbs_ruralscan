#!/usr/bin/env python3
"""Rank T3/T6 review targets by value of information (Pete 2026-11-12).

    uv run python scripts/rank-review-targets.py [--top 60]

Reads `pipeline/metrics/rating_setters.json` (targets + what each setter moves when dropped),
the EV register, the BANDS register and `pipeline/metrics/review_flags.csv` (doubts raised by
extraction lanes or prose writers). Score = (1 + impact) x (1 + doubt):

* impact (setters only): class steps moved on each headline row it sets (x3; a row appearing or
  disappearing, or moving to/from "conflicting"/"no rating", counts 2 steps), plus confidence
  steps (x1), summed over rows, capped at 15. Sample units have impact 0.
* doubt: how likely the unit is wrong - second-hand, assertion or model basis; low extraction
  confidence; coded size disagrees with the band rule; strong/moderate with no number;
  figure-read, OCR, unreplicated; loss framing or a comparator; bundled; flagged in review_flags.

Setters always rank before the random sample (a sample unit cannot move a rating). Writes
`pipeline/metrics/review_ranking.csv` and ranked item lists for scripts/build-review-batch.py
under `pipeline/staging/review_ranked/` (a cross-practice "top" list + one per practice for the
rest). Deterministic; never edits evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nbs_ruralscan.recipe.cell_synthesis import load_bands  # noqa: E402
from nbs_ruralscan.schema_tools import check_bands  # noqa: E402

SETTERS = ROOT / "pipeline/metrics/rating_setters.json"
FLAGS = ROOT / "pipeline/metrics/review_flags.csv"
OUT = ROOT / "pipeline/metrics/review_ranking.csv"
ITEMS = ROOT / "pipeline/staging/review_ranked"

T6_ORD = {
    "strong_negative": -3,
    "moderate_negative": -2,
    "slight_negative": -1,
    "no_relationship": 0,
    "slight_positive": 1,
    "moderate_positive": 2,
    "strong_positive": 3,
}
T3_ORD = {"negative": -1, "none": 0, "low": 1, "moderate": 2, "high": 3, "very_high": 4}
CONF = {"very_low": 0, "low": 1, "medium": 2, "high": 3, "very_high": 4}
NBS_LABEL = {
    "agroforestry": "Agroforestry",
    "forest_restoration": "Forest restoration",
    "mangrove_restoration": "Mangroves",
    "riparian_buffer": "Riverside buffers",
    "water_harvesting_conservation": "Water harvesting",
    "wetland_management": "Wetlands",
}
CLASS_WORDS = {
    "strong_positive": "strong gain",
    "moderate_positive": "moderate gain",
    "slight_positive": "slight gain",
    "no_relationship": "no effect",
    "slight_negative": "slight harm",
    "moderate_negative": "moderate harm",
    "strong_negative": "strong harm",
    "conflicting_evidence": "conflicting",
    "negative": "harm",
    "very_high": "very high",
}
ROLE_WORDS = {
    "livelihood_mitigation": "protecting livelihoods",
    "asset_threat": "damage to the practice",
}


def _obj(v) -> dict:
    if isinstance(v, dict):
        return v
    try:
        o = json.loads(v or "{}")
    except (TypeError, ValueError):
        return {}
    return o if isinstance(o, dict) else {}


def _row_words(table: str, row: str) -> str:
    if "|" in row:
        hz, role = (x.strip() for x in row.split("|", 1))
        return (
            f"{hz.replace('_', ' ')} ({ROLE_WORDS.get(role, role.replace('_', ' '))})"
        )
    words = row
    for suf in ("_priority", "_risk", "_hazard", "_potential"):
        words = words.removesuffix(suf)
    return words.replace("_", " ") + (" (scorecard)" if table == "T6" else "")


def _cls_words(c: str | None) -> str:
    if not c:
        return "no rating"
    return CLASS_WORDS.get(c, c.replace("_", " "))


def _steps(table: str, b: list | None, a: list | None) -> tuple[float, float]:
    """(class steps, confidence steps) between before and after."""
    if b is None or a is None:
        return 2.0, 0.0
    ordm = T6_ORD if table == "T6" else T3_ORD
    cb, ca = b[0] or "", a[0] or ""
    if cb == ca:
        cls = 0.0
    elif cb in ordm and ca in ordm:
        cls = float(abs(ordm[cb] - ordm[ca]))
    else:  # to/from conflicting or no rating
        cls = 2.0
    conf = float(abs(CONF.get(b[1] or "", 0) - CONF.get(a[1] or "", 0)))
    return cls, conf


def impact_of(effects: list[dict]) -> tuple[float, list[str]]:
    score, why = 0.0, []
    for e in effects:
        cls, conf = _steps(e["table"], e["before"], e["after"])
        score += 3 * cls + conf
        b, a = e["before"], e["after"]
        what = _row_words(e["table"], e["row"])
        if b is None:
            why.append(f"{what} would disappear without it" if a else what)
            continue
        if a is None:
            why.append(f"{what} ({_cls_words(b[0])}) would disappear without it")
            continue
        if b[0] != a[0]:
            why.append(
                f"{what} would move from {_cls_words(b[0])} to {_cls_words(a[0])}"
            )
        else:
            why.append(
                f"{what} confidence would move from {_cls_words(b[1])} to {_cls_words(a[1])}"
            )
    return min(score, 15.0), why


def doubt_of(u: dict, bands: list[dict], flag: str) -> tuple[float, list[str]]:
    rel, ctx = _obj(u.get("relationship")), _obj(u.get("context"))
    d, why = 0.0, []
    basis = u.get("claim_basis") or ""
    if basis == "cited_secondary":
        d, why = d + 2, why + ["second-hand (cited from another paper)"]
    elif basis == "expert_assertion":
        d, why = d + 2, why + ["an author's or tool's assertion, not a measurement"]
    elif basis == "modelled":
        d, why = d + 1.5, why + ["a model result"]
    conf = u.get("extraction_confidence") or ""
    if conf == "low":
        d, why = d + 2, why + ["extractor was unsure"]
    elif conf == "medium":
        d += 0.5
    band = check_bands.explain_unit(u, bands)
    strength = str(rel.get("strength_class") or "unspecified")
    has_number = any(
        rel.get(k) not in (None, "")
        for k in ("magnitude", "magnitude_low", "magnitude_high", "value_with")
    )
    if band.get("verdict") == "mismatch":
        d, why = d + 3, why + ["coded size disagrees with the size rule"]
    elif strength in ("strong", "moderate") and not has_number:
        d, why = d + 1.5, why + [f"coded {strength} but no number in the finding"]
    note = (str(rel.get("note") or "") + " " + str(ctx.get("note") or "")).lower()
    if "figure" in note and ("read" in note or "estimated from" in note):
        d, why = d + 1.5, why + ["value read off a figure"]
    if ctx.get("ocr_text"):
        d, why = d + 1.5, why + ["scanned page (text from OCR)"]
    if ctx.get("unreplicated"):
        d, why = d + 1, why + ["single unreplicated site"]
    if rel.get("framing") == "loss" or ctx.get("comparator"):
        d, why = d + 1, why + ["direction depends on how the comparison is framed"]
    if (ctx.get("attribution") or u.get("attribution")) == "bundled":
        d, why = d + 1, why + ["practice bundled with other measures"]
    if flag:
        d, why = d + 3, why + [flag]
    return d, why


def _flags() -> dict[str, str]:
    if not FLAGS.exists():
        return {}
    with FLAGS.open(newline="", encoding="utf-8") as f:
        return {r["evidence_id"]: r["doubt"] for r in csv.DictReader(f)}


def rank(top: int) -> list[dict]:
    data = json.loads(SETTERS.read_text(encoding="utf-8"))["cells"]
    with (ROOT / "schema/registers/EV_evidence_register.csv").open(
        newline="", encoding="utf-8"
    ) as f:
        ev = {r["evidence_id"]: r for r in csv.DictReader(f)}
    bands = load_bands(ROOT / "schema/registers/BANDS_magnitude_bands.csv")
    flags = _flags()
    rows: dict[str, dict] = {}
    for nbs, cell in data.items():
        effects = cell.get("effects", {})
        for t in ("T3", "T6"):
            for eid in cell[t]["targets"]:
                u = ev.get(eid)
                if (
                    not u
                    or u.get("review_state") == "dropped"
                    or (u.get("reviewer_ok") or "").lower() == "true"
                ):
                    continue
                if eid in rows:
                    continue
                setter = eid in cell["T3"]["setters"] or eid in cell["T6"]["setters"]
                imp, imp_why = impact_of(effects.get(eid, [])) if setter else (0.0, [])
                dbt, dbt_why = doubt_of(u, bands, flags.get(eid, ""))
                score = (1 + imp) * (1 + dbt) if setter else dbt
                rows[eid] = {
                    "evidence_id": eid,
                    "nbs": nbs,
                    "setter": setter,
                    "impact": round(imp, 2),
                    "doubt": round(dbt, 2),
                    "score": round(score, 2),
                    "if_wrong": "; ".join(imp_why),
                    "doubts": "; ".join(dbt_why),
                }
    ranked = sorted(
        rows.values(), key=lambda r: (not r["setter"], -r["score"], r["evidence_id"])
    )
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    return ranked


def _question(r: dict) -> str:
    lead = (
        f"If this finding is wrong: {r['if_wrong']}."
        if r["if_wrong"]
        else "Random quality check (cannot move a rating on its own)."
    )
    tail = f" Why check it: {r['doubts']}." if r["doubts"] else ""
    return f"Rank {r['rank']} · {NBS_LABEL.get(r['nbs'], r['nbs'])}. {lead}{tail}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument(
        "--top", type=int, default=60, help="size of the cross-practice top batch"
    )
    a = ap.parse_args(argv)
    ranked = rank(a.top)
    cols = [
        "rank",
        "evidence_id",
        "nbs",
        "setter",
        "score",
        "impact",
        "doubt",
        "if_wrong",
        "doubts",
    ]
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows({k: r[k] for k in cols} for r in ranked)
    ITEMS.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[dict]] = {"top": ranked[: a.top]}
    for r in ranked[a.top :]:
        groups.setdefault(r["nbs"], []).append(r)
    for name, rs in groups.items():
        with (ITEMS / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["evidence_id", "question"])
            w.writerows([r["evidence_id"], _question(r)] for r in rs)
    print(
        f"ranked {len(ranked)} ({sum(r['setter'] for r in ranked)} setters); "
        f"top {min(a.top, len(ranked))} -> {ITEMS.relative_to(ROOT)}/top.csv; "
        f"wrote {OUT.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
