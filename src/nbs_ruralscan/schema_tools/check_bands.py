"""Deterministic MAGNITUDE-BAND check for effect claims (ruleset v1.6.0, contract §2.2.3).

A unit's `strength_class` must follow from its `metric` + `magnitude` via the BANDS register
(`schema/registers/BANDS_magnitude_bands.csv`), never from adjectives ("significantly",
"dramatically" — defect E3). Flags (advisory) on ACTIVE `nbs_effect` / `asset_vulnerability`
units:

* `band_mismatch`      — banded metric, numeric magnitude, but `strength_class` ≠ the band
* `adjective_strength` — `strength_class` ∈ {slight, moderate, strong} with no numeric
                         magnitude and a non-ordinal metric (narrative / absent)
* `unknown_metric`     — `metric` outside the enum
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from nbs_ruralscan.recipe.cell_synthesis import (
    classify_magnitude,
    load_bands,
    match_band,
)

EFFECT_ROLES = {"nbs_effect", "asset_vulnerability"}
METRICS = {
    "smd_hedges_g",
    "pct_change",
    "ln_response_ratio",
    "ordinal_rating",
    "absolute",
    "narrative",
    # v1.6.2 (2026-10-06): a WITH / WITHOUT (after / before) pair quoted as two values —
    # `value_with`, `value_without` — classed on their ratio against the response_ratio
    # bands; `value_without = 0` (nothing without the practice) is a complete contrast.
    "contrast",
    # v1.6.2: an all-or-nothing statement with no number ("only fields with pits produced
    # a harvest") — strength_class `strong` without a magnitude, by definition.
    "complete_contrast",
}


def contrast_class(rel: dict, bands: list[dict]) -> str:
    """Derived strength_class of a `contrast` / `complete_contrast` relationship."""
    metric = str(rel.get("metric") or "")
    if metric == "complete_contrast":
        return "strong"
    if metric != "contrast":
        return "unspecified"
    w, wo = rel.get("value_with"), rel.get("value_without")
    if not isinstance(w, (int, float)) or not isinstance(wo, (int, float)):
        return "unspecified"
    if wo == 0:
        return "strong" if w != 0 else "unspecified"
    return classify_magnitude(
        "absolute", float(w) / float(wo), bands, unit="response_ratio"
    )


_ROOT = Path(__file__).resolve().parents[3]
_EV = _ROOT / "schema" / "registers" / "EV_evidence_register.csv"
_BANDS = _ROOT / "schema" / "registers" / "BANDS_magnitude_bands.csv"


def _obj(v) -> dict:
    if isinstance(v, dict):
        return v
    if not v:
        return {}
    try:
        o = json.loads(v)
    except Exception:
        return {}
    return o if isinstance(o, dict) else {}


def check_unit(row: dict, bands: list[dict]) -> list[dict]:
    rel = _obj(row.get("relationship"))
    eid = row.get("evidence_id", "")
    metric = str(rel.get("metric") or "")
    cls = str(rel.get("strength_class") or "unspecified")
    mag = rel.get("magnitude")
    if mag is None:
        # a RANGE is a quantified claim: check its midpoint, as the engine ranks it
        lo, hi = rel.get("magnitude_low"), rel.get("magnitude_high")
        nums = [float(x) for x in (lo, hi) if isinstance(x, (int, float))]
        if nums:
            mag = sum(nums) / len(nums)
    flags: list[dict] = []
    if metric and metric not in METRICS:
        flags.append({"signal": "unknown_metric", "evidence_id": eid, "detail": metric})
        return flags
    banded = {b.get("metric") for b in bands}
    if metric in ("contrast", "complete_contrast"):
        expect = contrast_class(rel, bands)
        if expect == "unspecified" or expect != cls:
            flags.append(
                {
                    "signal": "band_mismatch",
                    "evidence_id": eid,
                    "detail": f"{metric} with={rel.get('value_with')} without={rel.get('value_without')} → {expect}, unit says {cls}",
                }
            )
        return flags
    if (
        metric in banded
        and metric != "ordinal_rating"
        and isinstance(mag, (int, float))
    ):
        ctx = _obj(row.get("context"))
        band = {
            "low": "lic_lmic",
            "lower_middle": "lic_lmic",
            "lic_lmic": "lic_lmic",
            "upper_middle": "upper_middle",
            "high": "high",
        }.get(str(ctx.get("income_group") or ""), "")
        expect = classify_magnitude(
            metric, float(mag), bands, unit=str(rel.get("unit") or ""), income_band=band
        )
        if expect != "unspecified" and expect != cls:
            flags.append(
                {
                    "signal": "band_mismatch",
                    "evidence_id": eid,
                    "detail": f"{metric}={mag} → {expect}, unit says {cls}",
                }
            )
    elif cls in {"slight", "moderate", "strong"} and not isinstance(mag, (int, float)):
        if metric != "ordinal_rating":
            flags.append(
                {
                    "signal": "adjective_strength",
                    "evidence_id": eid,
                    "detail": f"strength_class={cls} with no magnitude (metric={metric or 'none'})",
                }
            )
    return flags


def check(
    ev_path: str | Path | None = None, bands_path: str | Path | None = None
) -> list[dict]:
    p = Path(ev_path) if ev_path else _EV
    b = Path(bands_path) if bands_path else _BANDS
    if not p.exists() or not b.exists():
        return []
    bands = load_bands(b)
    out: list[dict] = []
    with open(p, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("review_state") or "") == "dropped" or r.get(
                "use_role"
            ) not in EFFECT_ROLES:
                continue
            out += check_unit(r, bands)
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    flags = check(argv[0] if argv else None)
    if not flags:
        print(
            "BANDS CHECK: strength classes agree with magnitudes on all active effect units."
        )
        return 0
    print(f"BANDS CHECK: {len(flags)} flag(s):")
    for f in flags[:40]:
        print(f"  [{f['signal']}] {f['evidence_id']}: {f['detail']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ── plain-words band rule for the review page (theme 4, Pete 2026-10-12) ──────────────
#: "5% to 2.2% loss — what is the logic by which you have inferred this is a large amount?
#: is there a rule?" There is one, in BANDS, and the review page never showed it. These
#: helpers turn the matched band row into a sentence a reviewer can check.

_METRIC_WORDS = {
    "pct_change": "a change of {v} %",
    "smd_hedges_g": "a standardised mean difference (Hedges' g) of {v}",
    "ln_response_ratio": "a log response ratio of {v}",
    "absolute": "an absolute value of {v}{u}",
    "ordinal_rating": "a compiler rating of {s} on the source's own scale",
}


def _fmt(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".")


#: a BANDS `note` is sometimes the rule in words ("|change| < 10 %") and sometimes a
#: changelog line; only the first kind helps a reviewer, so it is shown only when it reads
#: like a threshold
_RULEISH = ("<", ">", "≥", "≤", "|", "%")


def _rule_text(band: dict) -> str:
    """The band's own inequality, in words ('|value − 1| ≥ 0.30')."""
    note = (band.get("note") or "").strip()
    if not any(c in note for c in _RULEISH):
        note = ""
    centre = (band.get("centre") or "").strip()
    lo, hi = (band.get("abs_min") or "").strip(), (band.get("abs_max") or "").strip()
    if band.get("metric") == "ordinal_rating":
        return f"the register maps the rating '{band.get('source_scale_value')}' to {band.get('strength_class')}"
    lhs = "|value − " + centre + "|" if centre and centre != "0" else "|value|"
    if lo and hi:
        txt = f"{lo} ≤ {lhs} < {hi}"
    elif lo:
        txt = f"{lhs} ≥ {lo}"
    elif hi:
        txt = f"{lhs} < {hi}"
    else:
        txt = note or "no threshold recorded"
    return txt + (f" — {note}" if note and note not in txt else "")


def explain_unit(row: dict, bands: list[dict]) -> dict:
    """Why this unit carries its `strength_class`: the value, the band rule, the verdict.

    Returns ``{value, class_claimed, class_by_rule, rule, band_id, basis, verdict}``.
    ``verdict`` is ``rule`` (the class follows the register), ``mismatch`` (it does not —
    the same finding `check_bands.check_unit` flags) or ``no_rule`` (nothing in BANDS
    covers this metric and unit, so the class is the extractor's judgement, unchecked).
    """
    rel = _obj(row.get("relationship"))
    ctx = _obj(row.get("context"))
    metric = str(rel.get("metric") or "")
    claimed = str(rel.get("strength_class") or "unspecified")
    out = {
        "value": "",
        "class_claimed": claimed,
        "class_by_rule": "",
        "rule": "",
        "band_id": "",
        "basis": "",
        "verdict": "no_rule",
    }
    if metric == "complete_contrast":
        out.update(
            value="an all-or-nothing result (something happened only with the practice)",
            class_by_rule="strong",
            rule="an all-or-nothing contrast is strong by definition — no number is needed",
            verdict="rule" if claimed == "strong" else "mismatch",
        )
        return out
    band = None
    unit = str(rel.get("unit") or "")
    if metric == "contrast":
        w, wo = rel.get("value_with"), rel.get("value_without")
        if isinstance(w, (int, float)) and isinstance(wo, (int, float)) and wo:
            ratio = float(w) / float(wo)
            out["value"] = (
                f"{w} with the practice against {wo} without "
                f"({unit.replace('_per_', ' per ').replace('_', ' ')}) → a ratio of {_fmt(ratio)}"
            )
            band = match_band("absolute", ratio, bands, unit="response_ratio")
        elif isinstance(w, (int, float)) and wo == 0:
            out.update(
                value=f"{w} with the practice against nothing without it",
                class_by_rule="strong",
                rule="a with/without pair whose 'without' value is zero is a complete contrast → strong",
                verdict="rule" if claimed == "strong" else "mismatch",
            )
            return out
    else:
        mag = rel.get("magnitude")
        if mag is None:
            lo, hi = rel.get("magnitude_low"), rel.get("magnitude_high")
            nums = [float(x) for x in (lo, hi) if isinstance(x, (int, float))]
            if nums:
                mag = sum(nums) / len(nums)
                out["value"] = (
                    f"a range of {lo} to {hi}, taken at its midpoint {_fmt(mag)}"
                )
        if isinstance(mag, (int, float)) and not out["value"]:
            out["value"] = _METRIC_WORDS.get(metric, "a value of {v}{u}").format(
                v=_fmt(float(mag)),
                u=f" {unit.replace('_', ' ')}" if unit else "",
                s=rel.get("source_scale_value"),
            )
        income = {
            "low": "lic_lmic",
            "lower_middle": "lic_lmic",
            "lic_lmic": "lic_lmic",
            "upper_middle": "upper_middle",
            "high": "high",
        }.get(str(ctx.get("income_group") or ""), "")
        band = match_band(
            metric,
            float(mag) if isinstance(mag, (int, float)) else None,
            bands,
            source_scale_value=(
                str(rel["source_scale_value"])
                if rel.get("source_scale_value") is not None
                else None
            ),
            unit=unit,
            income_band=income,
        )
        if metric == "ordinal_rating" and not out["value"]:
            out["value"] = _METRIC_WORDS["ordinal_rating"].format(
                v="", u="", s=rel.get("source_scale_value")
            )
    if band:
        out.update(
            class_by_rule=band.get("strength_class") or "",
            rule=_rule_text(band),
            band_id=band.get("band_id") or "",
            basis=(band.get("basis") or "").strip(),
            verdict="rule" if band.get("strength_class") == claimed else "mismatch",
        )
    elif claimed == "unspecified":
        out["verdict"] = "no_size"
        out["value"] = out["value"] or "no size recorded"
        out["rule"] = (
            "the unit records a direction but no size, so no band applies and the row's "
            "strength rests on the other units in the cell"
        )
    else:
        out["rule"] = (
            "no rule in the band register covers this metric and unit, so the strength is "
            "the extractor's judgement and is not checked — say if you disagree with it"
        )
    return out
