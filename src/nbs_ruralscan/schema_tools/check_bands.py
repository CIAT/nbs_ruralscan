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

from nbs_ruralscan.recipe.cell_synthesis import classify_magnitude, load_bands

EFFECT_ROLES = {"nbs_effect", "asset_vulnerability"}
METRICS = {
    "smd_hedges_g",
    "pct_change",
    "ln_response_ratio",
    "ordinal_rating",
    "absolute",
    "narrative",
}
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
    flags: list[dict] = []
    if metric and metric not in METRICS:
        flags.append({"signal": "unknown_metric", "evidence_id": eid, "detail": metric})
        return flags
    banded = {b.get("metric") for b in bands}
    if (
        metric in banded
        and metric != "ordinal_rating"
        and isinstance(mag, (int, float))
    ):
        expect = classify_magnitude(
            metric, float(mag), bands, unit=str(rel.get("unit") or "")
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
