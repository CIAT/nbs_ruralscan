"""Deterministic CONTEXT-KEY check for effect claims (ruleset v1.6.0, contract §2.3).

The v1 T3/T6 extraction recorded study context under ~15 different key spellings
(`country`, `study_region`, `location`, `countries`, `study_country`…), so nothing could be
grouped by where it applied — the root cause of the applicability failure. The v1.6.0
contract fixes the vocabulary: `country` (ISO3) · `region` · `aez` (T7) · `farming_system`
(T7) · `income_group` (WB) · `climate_zone`, plus the hazard keys on hazard units.

Flags (advisory, never fatal), on ACTIVE `nbs_effect` / `asset_vulnerability` units only:

* `unknown_context_key`   — a key outside the fixed vocabulary (put it in `note`)
* `bad_vocab`             — `aez`/`farming_system` not in T7, `income_group`/`hazard_type`/
                            `timescale_of_effect` not in their enums, `country` not ISO3-shaped
* `missing_income_group`  — `country` known but no `income_group` (the WB lookup resolves it)
* `missing_hazard_type`   — a hazard-routed unit with no `context.hazard_type`
* `severity_without_hazard` — `hazard_severity` set on a unit with no `hazard_type` (v1.6.3)
* `missing_severity_cue`  — `hazard_severity` other than `unspecified` with no `severity_cue`
* `severity_cue_not_in_quote` — the cue is not a verbatim substring of quote / note / outcome_raw

`check_context.py [EV.csv]` prints a summary; `check()` returns the flags.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

EFFECT_ROLES = {"nbs_effect", "asset_vulnerability"}
ALLOWED_KEYS = {
    "country",
    "region",
    "aez",
    "farming_system",
    "income_group",
    "climate_zone",
    # hazard units (contract §2.2.7–8)
    "hazard_type",
    "hazard_severity",  # v1.6.3: author-stated intensity of the hazard event
    "severity_cue",  # v1.6.3: verbatim words that justify hazard_severity
    "landscape_scale_only",
    "timescale_of_effect",
    "note",
}
INCOME = {"low", "lower_middle", "upper_middle", "high", "lic_lmic"}
CLIMATE = {"tropical", "dryland", "temperate", "boreal"}
HAZARDS = {
    "drought",
    "flood",
    "heat_stress",
    "fire",
    "wind_cyclone",
    "waterlogging",
    "frost",
    # asset-threat-only hazards (Pete 2026-10-06): non-climatic / sub-hazard processes that
    # damage WH structures (siltation of dams and tanks; storm damage to terraces). Valid in
    # `asset_vulnerability` units and T3 asset_threat rows only — never a T3 livelihood cell
    # and never counted in `asset_risk_weight` completeness.
    "sedimentation",
    "extreme_rainfall",
}
SEVERITY = {"mild", "moderate", "severe", "extreme", "unspecified"}
TIMESCALE = {"immediate", "short_term_1_3yr", "medium_term_3_7yr", "long_term_7yr_plus"}
_ISO3 = re.compile(r"^[A-Z]{3}$")

_ROOT = Path(__file__).resolve().parents[3]
_EV = _ROOT / "schema" / "registers" / "EV_evidence_register.csv"
_T7 = _ROOT / "schema" / "T7_geographic_context.csv"


def _obj(v: str | None) -> dict:
    if not v:
        return {}
    try:
        o = json.loads(v)
    except Exception:
        return {}
    return o if isinstance(o, dict) else {}


def _ctx_of(row: dict) -> dict:
    c = row.get("context")
    return c if isinstance(c, dict) else _obj(c)


def _t7(path: Path = _T7) -> tuple[set[str], set[str]]:
    aez: set[str] = set()
    fs: set[str] = set()
    if not path.exists():
        return aez, fs
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("context_type") == "aez":
                aez.add(r["context_id"])
            elif r.get("context_type") == "farming_system":
                fs.add(r["context_id"])
    return aez, fs


def check_unit(row: dict, aez: set[str], fs: set[str]) -> list[dict]:
    ctx = _ctx_of(row)
    eid = row.get("evidence_id", "")
    flags: list[dict] = []

    def flag(sig: str, detail: str) -> None:
        flags.append({"signal": sig, "evidence_id": eid, "detail": detail})

    for k in ctx:
        if k not in ALLOWED_KEYS:
            flag("unknown_context_key", k)
    countries = ctx.get("country")
    if isinstance(countries, str):
        countries = [
            c.strip() for c in countries.replace("|", ",").split(",") if c.strip()
        ]
    for c in countries or []:
        if not _ISO3.match(str(c)):
            flag("bad_vocab", f"country='{c}' not ISO3")
    if ctx.get("aez") and aez and ctx["aez"] not in aez:
        flag("bad_vocab", f"aez='{ctx['aez']}' not in T7")
    if ctx.get("farming_system") and fs and ctx["farming_system"] not in fs | {"all"}:
        flag("bad_vocab", f"farming_system='{ctx['farming_system']}' not in T7")
    if ctx.get("income_group") and ctx["income_group"] not in INCOME:
        flag("bad_vocab", f"income_group='{ctx['income_group']}'")
    if ctx.get("climate_zone") and ctx["climate_zone"] not in CLIMATE:
        flag("bad_vocab", f"climate_zone='{ctx['climate_zone']}'")
    if ctx.get("hazard_type") and ctx["hazard_type"] not in HAZARDS:
        flag("bad_vocab", f"hazard_type='{ctx['hazard_type']}'")
    if ctx.get("timescale_of_effect") and ctx["timescale_of_effect"] not in TIMESCALE:
        flag("bad_vocab", f"timescale_of_effect='{ctx['timescale_of_effect']}'")
    if countries and not ctx.get("income_group"):
        flag("missing_income_group", ",".join(countries))
    if row.get("use_role") == "asset_vulnerability" and not ctx.get("hazard_type"):
        flag("missing_hazard_type", row.get("variable", ""))
    sev = ctx.get("hazard_severity")
    if sev is not None:
        if sev not in SEVERITY:
            flag("bad_vocab", f"hazard_severity='{sev}'")
        elif not ctx.get("hazard_type"):
            flag("severity_without_hazard", f"hazard_severity='{sev}'")
        elif sev != "unspecified":
            cue = str(ctx.get("severity_cue") or "")
            rel = row.get("relationship")
            if isinstance(rel, str):
                try:
                    rel = json.loads(rel) if rel else {}
                except json.JSONDecodeError:
                    rel = {}
            hay = " ".join(
                str(x or "")
                for x in (
                    row.get("quote"),
                    ctx.get("note"),
                    (rel or {}).get("outcome_raw"),
                )
            )
            if not cue:
                flag("missing_severity_cue", f"hazard_severity='{sev}'")
            elif cue not in hay:
                flag("severity_cue_not_in_quote", cue[:80])
    return flags


def check(
    ev_path: str | Path | None = None, t7_path: str | Path | None = None
) -> list[dict]:
    p = Path(ev_path) if ev_path else _EV
    if not p.exists():
        return []
    aez, fs = _t7(Path(t7_path) if t7_path else _T7)
    out: list[dict] = []
    with open(p, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("review_state") or "") == "dropped":
                continue
            if r.get("use_role") not in EFFECT_ROLES:
                continue
            out += check_unit(r, aez, fs)
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    flags = check(argv[0] if argv else None)
    if not flags:
        print("CONTEXT CHECK: no fixed-key violations in active effect units.")
        return 0
    by: dict[str, int] = {}
    for f in flags:
        by[f["signal"]] = by.get(f["signal"], 0) + 1
    print(f"CONTEXT CHECK: {len(flags)} flag(s) on active effect units:")
    for sig, n in sorted(by.items(), key=lambda kv: -kv[1]):
        print(f"  {n}  {sig}")
    for f in flags[:40]:
        print(f"  [{f['signal']}] {f['evidence_id']}: {f['detail']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
