#!/usr/bin/env python3
"""Ingest gated effect-claim staging files into the live EV register (T3/T6 pilot).

Staging → register is the ONE place extraction output becomes evidence, so it re-runs the
central gates first and refuses on any failure: verbatim page containment against the cached
PDF, number provenance (`check_numbers`), fixed context keys (`check_context`), magnitude
bands (`check_bands`), VONT id + XW route (`check_xw` semantics), family ids in FAM. Units
already in the register are skipped (idempotent). Then `SRC.vars_extracted` is resynced for
the touched sources. No ledger / SRCH changes here (those are stamped by the orchestrator).

Usage:
    python3 scripts/ingest-effects-staging.py pipeline/staging/riparian_effects_A.json ... [--dry-run]
        [--fix-family EVIDENCE_ID=FAMILY ...]   # recorded human family decisions applied on ingest
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import fitz

from nbs_ruralscan.recipe.cell_synthesis import load_bands
from nbs_ruralscan.schema_tools import check_bands, check_context
from nbs_ruralscan.schema_tools.check_numbers import _nums
from nbs_ruralscan.schema_tools.migrate_effects import (
    append_to_register,
    resync_vars_extracted,
)

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "schema" / "registers"
CORPUS = ROOT / ".cache" / "corpus"


def _col(path: Path, col: str) -> set[str]:
    with path.open(newline="", encoding="utf-8") as f:
        return {r[col] for r in csv.DictReader(f) if r.get(col)}


def gate(units: list[dict]) -> list[str]:
    errs: list[str] = []
    bands = load_bands(REG / "BANDS_magnitude_bands.csv")
    vont = _col(REG / "VONT_variable_ontology.csv", "canonical_variable_id")
    fams = _col(REG / "FAM_family_registry.csv", "suitability_family_id")
    aez, fs = check_context._t7()
    docs: dict[str, fitz.Document | None] = {}
    for u in units:
        eid = u["evidence_id"]
        sid = u["source_id"]
        if sid not in docs:
            pdf = CORPUS / f"{sid}.pdf"
            docs[sid] = fitz.open(pdf) if pdf.exists() else None
        d = docs[sid]
        if d is None:
            errs.append(f"{eid}: no cached PDF for {sid}")
        else:
            try:
                text = " ".join(d[int(u["page"]) - 1].get_text().split())
                if " ".join(u["quote"].split()) not in text:
                    errs.append(f"{eid}: quote not verbatim on page {u['page']}")
            except Exception as e:  # noqa: BLE001
                errs.append(f"{eid}: page {u.get('page')} unreadable ({e})")
        rel = u.get("relationship") or {}
        rn: set[str] = set()
        for k in ("magnitude", "magnitude_low", "magnitude_high", "n"):
            v = rel.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                rn |= _nums(str(v))
        missing = rn - _nums(u["quote"])
        if missing:
            errs.append(f"{eid}: numbers not in quote {sorted(missing)}")
        row = {
            "evidence_id": eid,
            "use_role": u["use_role"],
            "variable": u["variable"],
            "context": u.get("context") or {},
            "relationship": rel,
        }
        errs += [
            f"{eid}: context {f['signal']} {f['detail']}"
            for f in check_context.check_unit(row, aez, fs)
        ]
        errs += [
            f"{eid}: bands {f['signal']} {f['detail']}"
            for f in check_bands.check_unit(row, bands)
        ]
        if u["variable"] not in vont:
            errs.append(f"{eid}: variable '{u['variable']}' has no VONT id")
        if u.get("suitability_family_id") not in fams:
            errs.append(f"{eid}: family '{u.get('suitability_family_id')}' not in FAM")
        if u.get("use_role") not in {"nbs_effect", "asset_vulnerability"}:
            errs.append(f"{eid}: use_role '{u.get('use_role')}' is not an effect role")
        if u.get("ruleset_version") != "v1.6.0":
            errs.append(f"{eid}: ruleset_version '{u.get('ruleset_version')}' ≠ v1.6.0")
    return errs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--fix-family", action="append", default=[], metavar="EVIDENCE_ID=FAMILY"
    )
    args = ap.parse_args(argv)
    fixes = dict(kv.split("=", 1) for kv in args.fix_family)
    units: list[dict] = []
    for f in args.files:
        units += json.loads(Path(f).read_text(encoding="utf-8"))
    for u in units:
        if u["evidence_id"] in fixes:
            u["suitability_family_id"] = fixes[u["evidence_id"]]
            u.setdefault("context", {})
            u["context"]["note"] = (
                u["context"].get("note", "")
                + f"; family set to {fixes[u['evidence_id']]} at ingest (human decision)"
            ).strip("; ")
    ids = Counter(u["evidence_id"] for u in units)
    dups = [k for k, n in ids.items() if n > 1]
    errs = gate(units) + [f"duplicate evidence_id in staging: {d}" for d in dups]
    print(
        f"{len(units)} staged unit(s) from {len(args.files)} file(s); roles {dict(Counter(u['use_role'] for u in units))}"
    )
    if errs:
        print(f"GATE FAILED: {len(errs)} problem(s) — nothing written")
        for e in errs[:40]:
            print("  -", e)
        return 1
    print(
        "gates clean: verbatim · numbers · context · bands · VONT · FAM · role · ruleset"
    )
    if args.dry_run:
        return 0
    n = append_to_register(units)
    touched = {u["source_id"] for u in units}
    changed = resync_vars_extracted(touched)
    print(
        f"appended {n} new unit(s) to EV; vars_extracted resynced for {len(changed)} source(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
