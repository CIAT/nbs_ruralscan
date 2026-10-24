"""NbS scorecard: generated T6 rows → the dashboard's problem/response chips (D3–D7).

Pete, 2026-10-23 (`methodology/decisions/2026-10-22_t3t6_scoring_and_qa.md`): the dashboard
shows, per NbS, **one row per problem** exactly as the mockup's Opportunity Space panels do —
the problem's spatial distribution (T5 need layer, computed at runtime) beside **how strongly
this NbS responds** (the T6 evidence row for that problem) — and the NbS Comparison tab shows
the same rows across NbS. No theme or group chips, no NbS-level number (D3 = profile).

* Rows come from `schema/lookups/scorecard_rows.csv` (mockup order and wording). A row can pool
  several T6 rows (water-table depletion = water stress + catchment water yield + water
  quality); its chip is the median of those rows at medium confidence or better, and any
  dissent ≥ 1/3 shows ± — the cell rule, one level up.
* Fire is a project risk (M2b), not an opportunity-space row; production gap is an
  intermediate step to rural poverty and food insecurity, not a row of its own.
* D6 (revised 2026-10-23, Pete: "moderate positive shows ++ HIGH?"): the symbol matches the
  evidence class 1:1 (+ slight · ++ moderate · +++ strong; − −− −−− for harm), and confidence
  is shown SEPARATELY from the symbol (●●● high · ●●○ medium · ●○○ low), never inside the
  pill; plus ± (studies disagree), ? (too little evidence) and n/a (not assessed); CAUTION is
  the chip outline (measured harm for some adopters). Scale/badges: `schema/lookups/scorecard_*.csv`.
* D5: `evidenced_priorities` (T5 need layers the NbS is evidenced to improve) is the optional
  hotspot-map filter; T6 never alters the hotspot weights.

Only NbS-level, global rows are used (no family, no scope).
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CONF_ORDER = ["very_low", "low", "medium", "high", "very_high"]
MIN_THEME_CONF = "medium"
DISSENT_SHARE = 1 / 3
GLYPH_OF_RANK = {3: "+++", 2: "++", 1: "+", 0: "0", -1: "−", -2: "−−", -3: "−−−"}


def _rd(p: Path) -> list[dict[str, str]]:
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _j(v: str | None, default: Any) -> Any:
    try:
        return json.loads(v) if v else default
    except json.JSONDecodeError:
        return default


def load_scale(schema_root: Path) -> dict[str, Any]:
    lk = schema_root / "lookups"
    scale = {(r["field"], r["class"]): r for r in _rd(lk / "scorecard_chip_scale.csv")}
    badges = {
        r["confidence"]: r["badge"] for r in _rd(lk / "scorecard_confidence_badge.csv")
    }
    dots = {
        r["confidence"]: r.get("dots", "")
        for r in _rd(lk / "scorecard_confidence_badge.csv")
    }
    return {"scale": scale, "badges": badges, "dots": dots}


def _special(scale: dict, cls: str) -> dict[str, Any]:
    r = scale.get(("any", cls), {})
    return {
        "glyph": r.get("glyph", "?"),
        "rank": None,
        "label": r.get("label", cls),
        "dots": "",
    }


def chip(
    row: dict[str, Any] | None, field: str, conf_col: str, sc: dict
) -> dict[str, Any]:
    """One row → {glyph, rank, label, class, confidence, badge, caution, record_id}."""
    scale, badges = sc["scale"], sc["badges"]
    if row is None:
        return {
            **_special(scale, "not_assessed"),
            "class": "not_assessed",
            "confidence": "",
            "badge": "",
            "caution": False,
            "record_id": "",
        }
    j = row.get("justification")
    j = j if isinstance(j, dict) else _j(j, {})
    cls = str(row.get(field) or "")
    if j.get("data_deficient"):
        base = _special(scale, "data_deficient")
        cls = "data_deficient"
    elif cls == "conflicting_evidence" or j.get("conflicting") in (True, "True"):
        base = _special(scale, "conflicting_evidence")
        cls = "conflicting_evidence"
    else:
        r = scale.get((field, cls))
        if r is None:
            base = _special(scale, "data_deficient")
        else:
            base = {"glyph": r["glyph"], "rank": int(r["rank"]), "label": r["label"]}
    conf = str(row.get(conf_col) or "")
    mal = j.get("maladaptation") or {}
    caution = bool(
        isinstance(mal, dict)
        and (mal.get("n_units") or mal.get("ids") or mal.get("units"))
    )
    return {
        **base,
        "class": cls,
        "confidence": conf,
        "badge": "" if cls == "data_deficient" else badges.get(conf, ""),
        "dots": "" if cls == "data_deficient" else sc.get("dots", {}).get(conf, ""),
        "caution": caution,
        "record_id": row.get("record_id", ""),
    }


def _conf_ok(conf: str, floor: str = MIN_THEME_CONF) -> bool:
    return conf in CONF_ORDER and CONF_ORDER.index(conf) >= CONF_ORDER.index(floor)


def _wmedian(pairs: list[tuple[int, float]]) -> int:
    pairs = sorted(pairs)
    half = sum(w for _, w in pairs) / 2
    run = 0.0
    for r, w in pairs:
        run += w
        if run >= half:
            return r
    return pairs[-1][0]


def theme_chip(
    chips: list[dict[str, Any]], weights: list[float], sc: dict
) -> dict[str, Any]:
    """D4: TTL-weighted median of the theme's rows at medium confidence or better."""
    scale = sc["scale"]
    assessed = [(c, w) for c, w in zip(chips, weights) if c["class"] != "not_assessed"]
    setting = [
        (c, w)
        for c, w in assessed
        if c["class"] != "data_deficient" and _conf_ok(c["confidence"])
    ]
    if not assessed:
        return {
            **_special(scale, "not_assessed"),
            "class": "not_assessed",
            "confidence": "",
            "badge": "",
            "caution": False,
            "setting_rows": [],
            "why": "no priority in this theme has an evidence row",
        }
    if not setting:
        return {
            **_special(scale, "data_deficient"),
            "class": "data_deficient",
            "confidence": "",
            "badge": "",
            "caution": False,
            "setting_rows": [],
            "why": "rows exist but none reaches medium confidence",
        }
    pos = sum(w for c, w in setting if (c["rank"] or 0) > 0)
    neg = sum(w for c, w in setting if (c["rank"] or 0) < 0)
    conf_w = sum(w for c, w in setting if c["class"] == "conflicting_evidence")
    base = pos + neg + conf_w
    weakest = min((c["confidence"] for c, _ in setting), key=CONF_ORDER.index)
    common = {
        "confidence": weakest,
        "badge": sc["badges"].get(weakest, ""),
        "dots": sc.get("dots", {}).get(weakest, ""),
        "caution": any(c["caution"] for c, _ in setting),
        "setting_rows": [c["record_id"] for c, _ in setting],
    }
    if base and (conf_w + min(pos, neg)) / base >= DISSENT_SHARE:
        return {
            **_special(scale, "conflicting_evidence"),
            "class": "conflicting_evidence",
            **common,
            "why": "rows in this theme point in different directions (dissent ≥ 1/3)",
        }
    rank = (
        _wmedian([(c["rank"], w) for c, w in setting if c["rank"] is not None])
        if any(c["rank"] is not None for c, _ in setting)
        else 0
    )
    return {
        "glyph": GLYPH_OF_RANK[rank],
        "rank": rank,
        "label": "",
        "class": "",
        **common,
        "why": "TTL-weighted median of the setting rows",
    }


def _global(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        r
        for r in rows
        if not r.get("suitability_family_id") and not r.get("scope_type")
    ]


def load_rows(schema_root: Path) -> list[dict[str, str]]:
    rows = _rd(schema_root / "lookups" / "scorecard_rows.csv")
    return sorted(rows, key=lambda r: int(r.get("order") or 0))


def _source_chip(src: str, t6: dict, t3: dict, sc: dict) -> dict[str, Any]:
    table, key = src.split(":", 1)
    if table == "T3":
        return chip(t3.get(key), "mitigation_potential", "confidence", sc)
    return chip(t6.get(key), "effect_direction", "effect_confidence", sc)


def build_nbs(
    schema_root: Path,
    nbs_id: str,
    sc: dict,
    t5: list[dict[str, str]],
    display_rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    rdir = schema_root / "recipes" / nbs_id
    t6 = {r["variable_id"]: r for r in _global(_rd(rdir / "T6_nbs_scorecard.csv"))}
    t3 = {
        r["hazard_type"]: r
        for r in _global(_rd(rdir / "T3_nbs_hazard_farming.csv"))
        if r.get("risk_role") != "asset_threat"
        and (r.get("farming_system") or "all") == "all"
    }
    display_rows = display_rows if display_rows is not None else load_rows(schema_root)
    rows_out = []
    for d in display_rows:
        srcs = [x for x in (d.get("sources") or "").split("|") if x]
        parts = [(x, _source_chip(x, t6, t3, sc)) for x in srcs]
        if len(parts) == 1:
            c = parts[0][1]
        else:
            c = theme_chip([p for _, p in parts], [1.0] * len(parts), sc)
            c.setdefault("record_id", "")
        rows_out.append(
            {
                **c,
                "class_label": c.get("label", ""),
                "row_id": d["row_id"],
                "panel": d["panel"],
                "panel_label": d["panel_label"],
                "label": d["label"],
                "sources": [
                    {
                        "source": x,
                        "glyph": p["glyph"],
                        "badge": p["badge"],
                        "class": p["class"],
                        "record_id": p["record_id"],
                    }
                    for x, p in parts
                ],
            }
        )
    counts: dict[str, int] = {}
    for r in rows_out:
        k = (
            r["class"] or "pooled"
            if r["rank"] is None
            else "benefit"
            if r["rank"] > 0
            else "harm"
            if r["rank"] < 0
            else "no_effect"
        )
        counts[k] = counts.get(k, 0) + 1
    pri = [
        r["variable_id"]
        for r in t5
        if r.get("mcda_role") == "priority" and r.get("is_active", "true") != "false"
    ]
    evidenced = []
    for v in pri:
        c = chip(t6.get(v), "effect_direction", "effect_confidence", sc)
        if (c["rank"] or 0) > 0 and c["badge"] in ("MED", "HIGH"):
            evidenced.append(v)
    return {"rows": rows_out, "counts": counts, "evidenced_priorities": evidenced}


def build(schema_root: str | Path) -> dict[str, Any]:
    schema_root = Path(schema_root)
    sc = load_scale(schema_root)
    t5 = _rd(next(iter(sorted(schema_root.glob("T5_*.csv"))), schema_root / "T5.csv"))
    display_rows = load_rows(schema_root)
    nbs = {}
    for d in sorted((schema_root / "recipes").iterdir()):
        if (d / "T6_nbs_scorecard.csv").exists():
            nbs[d.name] = build_nbs(
                schema_root, d.name, sc, t5, display_rows=display_rows
            )
    return {
        "meta": {
            "decisions": "methodology/decisions/2026-10-22_t3t6_scoring_and_qa.md",
            "rows": "schema/lookups/scorecard_rows.csv (mockup rows: problem + NbS response)",
            "scale": [
                {k: r[k] for k in ("field", "class", "glyph", "label")}
                for r in sc["scale"].values()
            ],
            "badges": sc["badges"],
            "pooled_row_rule": (
                f"a row built from several T6 rows shows their median at {MIN_THEME_CONF} "
                f"confidence or better; dissent ≥ {DISSENT_SHARE:.2f} → ±; confidence = "
                "weakest setting row"
            ),
            "caution": "chip outline when the row lists measured harm for some adopters",
        },
        "nbs": nbs,
    }


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        ).stdout.strip()
    except Exception:
        return ""


def write(
    schema_root: str | Path, check: bool = False, dest: Path | None = None
) -> list[Path]:
    """(Re)write `docs/scorecard.json`; the stamp only moves when the content does."""
    schema_root = Path(schema_root)
    dest = Path(dest) if dest else schema_root.parent / "docs" / "scorecard.json"
    payload = build(schema_root)
    cur = _j(dest.read_text(encoding="utf-8"), None) if dest.exists() else None
    if (
        isinstance(cur, dict)
        and cur.get("meta") == payload["meta"]
        and cur.get("nbs") == payload["nbs"]
    ):
        return []
    if not check:
        out = {
            "build": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "git_commit": _git_commit(),
            },
            **payload,
        }
        dest.write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return [dest]
