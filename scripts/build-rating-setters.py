#!/usr/bin/env python3
"""List the findings a person must review for the T3/T6 "reviewed" stage (Pete 2026-11-11).

    uv run python scripts/build-rating-setters.py [nbs ...] [--sample-share 0.1]

A finding is a *rating setter* when dropping it alone changes a headline row (NbS roll-up,
all farming systems, no breakdown) of that table: its class, its confidence, or whether the
row exists. Every setter plus a fixed random sample of the other findings feeding that table
are the review targets. `schema_tools/table_progress.py` marks "reviewed" done when every
target has a human decision. Writes `pipeline/metrics/rating_setters.json` (deterministic:
the sample uses a fixed seed and sorted ids). Re-run after the evidence changes.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

NBS = [
    "agroforestry",
    "forest_restoration",
    "mangrove_restoration",
    "riparian_buffer",
    "water_harvesting_conservation",
    "wetland_management",
]
SEED = 20261111
OUT = ROOT / "pipeline" / "metrics" / "rating_setters.json"


def _load_synth():
    spec = importlib.util.spec_from_file_location(
        "synth", ROOT / "scripts" / "synthesise-t3t6.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError("cannot load scripts/synthesise-t3t6.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _label(r: dict) -> str:
    if r.get("hazard_type"):
        return f"{r['hazard_type']} | {r.get('risk_role', '')}"
    return str(r.get("variable_id") or r.get("record_id"))


def _headline(out: dict, table: str) -> dict[str, tuple[str, str, str]]:
    rows = {}
    for r in out.get(table, []):
        if r.get("scope_type") or r.get("suitability_family_id"):
            continue
        if r.get("farming_system") not in (None, "", "all"):
            continue
        cls = (
            r.get("mitigation_potential")
            or r.get("asset_sensitivity")
            or r.get("effect_direction")
            or ""
        )
        conf = r.get("confidence") or r.get("effect_confidence") or ""
        rows[r["record_id"]] = (cls, conf, _label(r))
    return rows


def _ids(out: dict, table: str) -> set[str]:
    ids: set[str] = set()
    for r in out.get(table, []):
        ev = r.get("evidence_ids") or []
        if isinstance(ev, str):
            ev = json.loads(ev or "[]")
        ids.update(ev)
    return ids


def build(nbs_list: list[str], share: float) -> dict:
    s = _load_synth()
    cells: dict[str, dict] = {}
    for nbs in nbs_list:
        inp = s.load_inputs(nbs, [])
        units = inp["units"]

        def run(drop: str | None = None) -> dict:
            i = dict(inp)
            i["units"] = [u for u in units if u.evidence_id != drop]
            with contextlib.redirect_stdout(io.StringIO()):
                return s.synthesise(nbs, i)

        base = run()
        cells[nbs] = {}
        heads = {t: _headline(base, t) for t in ("T3", "T6")}
        pools = {t: _ids(base, t) for t in ("T3", "T6")}
        candidates = sorted(pools["T3"] | pools["T6"])
        setters: dict[str, set[str]] = {"T3": set(), "T6": set()}
        effects: dict[str, list[dict]] = {}
        for eid in candidates:
            out = run(eid)
            for t in ("T3", "T6"):
                after = _headline(out, t)
                if eid in pools[t] and after != heads[t]:
                    setters[t].add(eid)
                    for rid in sorted(set(after) | set(heads[t])):
                        b, a = heads[t].get(rid), after.get(rid)
                        ref = b or a
                        if b != a and ref is not None:
                            effects.setdefault(eid, []).append(
                                {
                                    "table": t,
                                    "row": ref[2],
                                    "before": list(b[:2]) if b else None,
                                    "after": list(a[:2]) if a else None,
                                }
                            )
        for t in ("T3", "T6"):
            rest = sorted(pools[t] - setters[t])
            k = min(len(rest), max(10, min(25, round(share * len(rest)))))
            sample = sorted(random.Random(f"{SEED}-{nbs}-{t}").sample(rest, k))
            cells[nbs][t] = {
                "setters": sorted(setters[t]),
                "sample": sample,
                "targets": sorted(setters[t] | set(sample)),
                "n_pool": len(pools[t]),
            }
        cells[nbs]["effects"] = {k: effects[k] for k in sorted(effects)}
        print(
            nbs,
            {t: (len(setters[t]), len(cells[nbs][t]["sample"])) for t in ("T3", "T6")},
            flush=True,
        )
    return {
        "meta": {
            "rule": "setter = dropping this finding alone changes a headline row's class, "
            "confidence or existence in that table; targets = setters + fixed random sample "
            "(10% of the rest, 10-25 per table)",
            "seed": SEED,
            "decided_by": "Pete 2026-11-11 (review rule: rating-setting findings)",
        },
        "cells": cells,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("nbs", nargs="*")
    ap.add_argument("--sample-share", type=float, default=0.1)
    a = ap.parse_args(argv)
    nbs_list = a.nbs or NBS
    data = build(nbs_list, a.sample_share)
    if a.nbs and OUT.exists():  # partial rebuild: keep the other practices
        old = json.loads(OUT.read_text(encoding="utf-8"))
        old.setdefault("cells", {}).update(data["cells"])
        old["meta"] = data["meta"]
        data = old
    data["cells"] = dict(sorted(data["cells"].items()))
    OUT.write_text(json.dumps(data, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
