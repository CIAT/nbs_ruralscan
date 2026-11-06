#!/usr/bin/env python3
"""Ingest gated effect-claim staging files into the live EV register (T3/T6 pilot).

Staging → register is the ONE place extraction output becomes evidence, so it re-runs the
central gates first and refuses on any failure: verbatim page containment against the cached
PDF, number provenance (`check_numbers`), fixed context keys (`check_context`), magnitude
bands (`check_bands`), source identity, VONT id, family/NbS agreement. XW coverage remains advisory
(`check_xw`): an unmapped outcome is retained, not silently dropped. Units
already in the register are skipped (idempotent). Then `SRC.vars_extracted` is resynced for
the touched sources and those still `pending` are marked `swept` with `--run-id` (promotion
leaves them pending). No ledger / SRCH changes here (those are stamped by the orchestrator).

Usage:
    python3 scripts/ingest-effects-staging.py pipeline/staging/riparian_effects_A.json ... --run-id <id> [--dry-run]
        [--fix-family EVIDENCE_ID=FAMILY ...]   # recorded human family decisions applied on ingest
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path

from nbs_ruralscan.schema_tools import evidence_intake as intake

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "schema/registers"
CORPUS = ROOT / ".cache/corpus"
QUEUE = ROOT / "pipeline/acquisition_queue.csv"
_validate_payload_shape = intake._validate_payload_shape
_unique_object = intake._unique_object


def _paths(
    *, root: Path | None = None, corpus: Path | None = None
) -> intake.EvidenceIntakePaths:
    if root is not None:
        return intake.EvidenceIntakePaths.from_root(root, corpus=corpus)
    return replace(
        intake.EvidenceIntakePaths.from_root(
            ROOT, corpus=corpus if corpus is not None else CORPUS
        ),
        evidence=REG / "EV_evidence_register.csv",
        sources=REG / "SRC_source_register.csv",
        families=REG / "FAM_family_registry.csv",
        variables=REG / "VONT_variable_ontology.csv",
        bands=REG / "BANDS_magnitude_bands.csv",
        queue=QUEUE,
    )


def gate(units, allowed_roles=None, *, paths=None):
    """Compatibility entrypoint; explicit contexts never use checkout defaults."""
    return intake.gate(
        units, allowed_roles, paths=paths if paths is not None else _paths()
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument(
        "--root",
        type=Path,
        help="Data root to validate and update (default: this checkout)",
    )
    ap.add_argument(
        "--corpus-dir",
        type=Path,
        help="Cached source artifacts (default: selected root/.cache/corpus)",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--fix-family", action="append", default=[], metavar="EVIDENCE_ID=FAMILY"
    )
    ap.add_argument(
        "--family-decision",
        help="Decision reference/rationale required with --fix-family",
    )
    ap.add_argument(
        "--allow-operational",
        action="store_true",
        help=(
            "also accept use_role=operational_risk units (enabling-environment / adoption "
            "claims from the same single-pass read; 2026-06-23 lock routes them to M2b and "
            "Module 6). Every other gate still applies; they carry no effect relationship, "
            "so the BANDS check skips them by role."
        ),
    )
    ap.add_argument(
        "--allow-structural",
        action="store_true",
        help="also accept structural_suitability (T4) units — same gates (verbatim, numbers, VONT, FAM)",
    )
    ap.add_argument(
        "--run-id",
        help="extraction run id stamped on the touched sources (required unless --dry-run)",
    )
    ap.add_argument("--extractor", default="claude (gated pipeline)")
    args = ap.parse_args(argv)
    if not args.dry_run and not (args.run_id or "").strip():
        ap.error("--run-id is required to write (it marks the touched sources swept)")
    if args.fix_family and not (args.family_decision or "").strip():
        ap.error(
            "--fix-family requires --family-decision (decision reference/rationale)"
        )
    fixes: dict[str, str] = {}
    for assignment in args.fix_family:
        parts = assignment.split("=", 1)
        if len(parts) != 2 or not all(parts) or parts[0] in fixes:
            ap.error(
                "--fix-family needs unique non-empty EVIDENCE_ID=FAMILY assignments"
            )
        fixes[parts[0]] = parts[1]
    units: list[dict] = []
    for f in args.files:
        try:
            payload = json.loads(
                Path(f).read_text(encoding="utf-8"), object_pairs_hook=_unique_object
            )
        except (ValueError, OSError) as exc:
            ap.error(f"{f}: invalid staging JSON: {exc}")
        if not isinstance(payload, list) or any(
            not isinstance(u, dict) for u in payload
        ):
            ap.error(f"{f}: expected a list of evidence objects")
        units += payload
    for u in units:
        if isinstance(u.get("evidence_id"), str) and u["evidence_id"] in fixes:
            try:
                _validate_payload_shape(u)
            except (TypeError, ValueError) as exc:
                ap.error(f"{u['evidence_id']}: invalid family-fix input: {exc}")
            u["suitability_family_id"] = fixes[u["evidence_id"]]
            u["context"] = u.get("context") or {}
            u["context"]["note"] = (
                u["context"].get("note", "")
                + f"; family set to {fixes[u['evidence_id']]} at ingest: {args.family_decision}"
            ).strip("; ")
    roles = {"nbs_effect", "asset_vulnerability"} | (
        ({"operational_risk"} if args.allow_operational else set())
        | ({"structural_suitability"} if args.allow_structural else set())
    )
    paths = _paths(root=args.root, corpus=args.corpus_dir)
    print(
        f"{len(units)} staged unit(s) from {len(args.files)} file(s); roles {dict(Counter(str(u.get('use_role', '<missing>')) for u in units))}"
    )
    try:
        result = intake.ingest(
            units,
            paths=paths,
            allowed_roles=roles,
            run_id=args.run_id or "",
            extractor=args.extractor,
            dry_run=args.dry_run,
        )
    except intake.IntakeGateError as exc:
        print(f"GATE FAILED: {len(exc.problems)} problem(s) — nothing written")
        for problem in exc.problems[:40]:
            print("  -", problem)
        return 1
    except (ValueError, OSError) as exc:
        print(f"INTAKE FAILED: {exc}")
        return 1
    print(
        "gates clean: verbatim · numbers · context · bands · VONT · FAM · role · ruleset"
    )
    if args.dry_run:
        print(
            f"append validation clean: {result.appended} new unit(s); nothing written"
        )
        return 0
    print(
        f"appended {result.appended} new unit(s) to EV; vars_extracted resynced for {len(result.variables_changed)} "
        f"source(s); {len(result.stamped)} source(s) marked swept ({args.run_id})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
