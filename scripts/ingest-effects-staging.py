#!/usr/bin/env python3
"""Ingest gated effect-claim staging files into the live EV register (T3/T6 pilot).

Staging → register is the ONE place extraction output becomes evidence, so it re-runs the
central gates first and refuses on any failure: verbatim page containment against the cached
PDF, number provenance (`check_numbers`), fixed context keys (`check_context`), magnitude
bands (`check_bands`), source identity, VONT id, family/NbS agreement. XW coverage remains advisory
(`check_xw`): an unmapped outcome is retained, not silently dropped. Units
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
import hashlib
from contextlib import ExitStack
from dataclasses import fields
from collections import Counter
from pathlib import Path

import fitz


from nbs_ruralscan.ingest.integrity import (
    identity_error,
    pdf_title_error,
    source_identity_differs,
    validate_source_id,
)
from nbs_ruralscan.recipe.evidence import EvidenceUnit, validate
from nbs_ruralscan.recipe.cell_synthesis import load_bands
from nbs_ruralscan.schema_tools import check_bands, check_context, check_direction
from nbs_ruralscan.schema_tools.check_numbers import _floats, _nums, _rel_nums
from nbs_ruralscan.schema_tools.validate_sources import _native_part
from nbs_ruralscan.schema_tools.migrate_effects import (
    append_to_register,
    resync_vars_extracted,
)

#: accepted extraction rulesets (methodology/RULESET_VERSIONS.md; v1.6.3–v1.6.6 are search /
#: tagging / note-rule patches — the extraction contract is unchanged since v1.6.2, apart from
#: v1.6.9's `context.practice_as_described`, which `check_context` polices)
_RULESETS = {
    "v1.6.0",
    "v1.6.1",
    "v1.6.2",
    "v1.6.3",
    "v1.6.4",
    "v1.6.5",
    "v1.6.6",
    "v1.6.7",
    "v1.6.8",
    "v1.6.9",
    "v1.6.10",
    "v1.6.11",
    "v1.6.12",
    "v1.6.13",
    "v1.6.14",
    "v1.6.15",
    "v1.6.16",
    "v1.7.0",
    "v1.8.0",
    # Historical stamps remain valid; --allow-structural controls T4 scope.
    "v1.6.17",
}

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "schema" / "registers"
CORPUS = ROOT / ".cache" / "corpus"
QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"


def _col(path: Path, col: str) -> set[str]:
    with path.open(newline="", encoding="utf-8") as f:
        return {r[col] for r in csv.DictReader(f) if r.get(col)}


def _indexed_csv(path: Path, key: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            value = row.get(key) or ""
            if not value or value in rows:
                raise ValueError(f"{path.name}: blank/duplicate {key}: {value!r}")
            rows[value] = row
    return rows


def _validate_payload_shape(u: dict) -> None:
    """Reject JSON/type tricks before permissive dataclass construction or checks."""
    # json.loads accepts NaN/Infinity by default. Neither is evidence or portable JSON.
    json.dumps(u, allow_nan=False)
    objects = {"relationship", "context"}
    pages = {"page", "justification_page", "selection_justification_page"}
    for key, value in u.items():
        if key in objects:
            if value is not None and not isinstance(value, dict):
                raise ValueError(f"{key} must be an object or null")
        elif key in pages:
            if value is not None and not (key == "page" and value == ""):
                if type(value) is not int or value < 1:
                    raise ValueError(f"{key} requires an integer page >= 1")
        elif key == "reviewer_ok":
            if value is not None and type(value) is not bool:
                raise ValueError("reviewer_ok must be a boolean or null")
        elif value is not None and not isinstance(value, str):
            raise ValueError(f"{key} must be a string or null")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    out: dict = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def gate(units: list[dict], allowed_roles: set[str] | None = None) -> list[str]:
    if allowed_roles is None:
        allowed_roles = {"nbs_effect", "asset_vulnerability"}
    errs: list[str] = []
    bands = load_bands(REG / "BANDS_magnitude_bands.csv")
    vont = _col(REG / "VONT_variable_ontology.csv", "canonical_variable_id")
    fams = _col(REG / "FAM_family_registry.csv", "suitability_family_id")
    aez, fs = check_context._t7()
    try:
        sources = _indexed_csv(REG / "SRC_source_register.csv", "source_id")
        identities = _indexed_csv(QUEUE, "source_id")
    except ValueError as exc:
        return [f"source identity register invalid: {exc}"]
    with (REG / "FAM_family_registry.csv").open(newline="", encoding="utf-8") as f:
        family_nbs = {
            (r["suitability_family_id"], r["nbs_id"]) for r in csv.DictReader(f)
        }
    unit_fields = {f.name for f in fields(EvidenceUnit)}
    with (REG / "EV_evidence_register.csv").open(newline="", encoding="utf-8") as f:
        ev_fields = set(csv.DictReader(f).fieldnames or [])
    docs: dict[str, fitz.Document | None] = {}
    seen: set[str] = set()
    with ExitStack() as stack:
        for u in units:
            eid = (
                u.get("evidence_id", "<missing>")
                if isinstance(u, dict)
                else "<invalid>"
            )
            try:
                if not isinstance(u, dict):
                    raise ValueError("staged unit must be an object")
                unknown = set(u) - ev_fields
                if unknown:
                    raise ValueError(f"unknown evidence fields: {sorted(unknown)}")
                _validate_payload_shape(u)
                unit = EvidenceUnit(**{k: v for k, v in u.items() if k in unit_fields})
                problems = validate(unit)
                if (
                    len("".join(c for c in _native_part(unit.quote) if c.isalnum()))
                    < 12
                ):
                    problems.append(
                        "native quote must contain at least 12 alphanumeric characters"
                    )
                validate_source_id(unit.source_id)
                if u.get("reviewer_ok") not in (None, False):
                    problems.append("new extraction cannot grant reviewer approval")
                if u.get("review_state"):
                    problems.append(
                        "new extraction cannot set review_state; use review workflow"
                    )
                if unit.taxon and unit.claim_scope == "practice_technology":
                    problems.append(
                        "practice_technology must not carry a taxon; retain species/crop scope"
                    )
                if unit.relationship is not None and not isinstance(
                    unit.relationship, dict
                ):
                    problems.append("relationship must be an object or null")
                if unit.context is not None and not isinstance(unit.context, dict):
                    problems.append("context must be an object or null")
                if problems:
                    raise ValueError("; ".join(problems))
            except (TypeError, ValueError, AttributeError) as exc:
                errs.append(f"{eid}: invalid evidence unit: {exc}")
                continue
            sid = u["source_id"]
            if eid in seen:
                errs.append(f"{eid}: duplicate evidence_id in staging")
            seen.add(eid)
            source = sources.get(sid)
            identity = identities.get(sid)
            if source is None:
                errs.append(f"{eid}: source {sid} is not registered in SRC")
            identity_problem = identity_error(identity)
            if identity_problem:
                errs.append(f"{eid}: {identity_problem}")
            elif source and identity and source_identity_differs(source, identity):
                errs.append(
                    f"{eid}: SRC identity differs from verified acquisition queue; reconcile first"
                )
            if (u["suitability_family_id"], u["nbs_id"]) not in family_nbs:
                errs.append(f"{eid}: family does not belong to nbs_id {u['nbs_id']}")
            if unit.locator_type not in {"page", "section"}:
                errs.append(
                    f"{eid}: locator {unit.locator_type} needs its dedicated adapter; not supported by this gate"
                )
                continue
            if unit.locator_type == "page" and sid not in docs:
                pdf = CORPUS / f"{sid}.pdf"
                try:
                    if pdf.exists() and source:
                        problem = pdf_title_error(pdf, source.get("citation") or "")
                        if problem:
                            errs.append(
                                f"{eid}: source document identity hold: {problem}"
                            )
                    docs[sid] = (
                        stack.enter_context(fitz.open(pdf)) if pdf.exists() else None
                    )
                except Exception as exc:
                    errs.append(f"{eid}: unreadable cached PDF ({exc})")
                    docs[sid] = None
            d = docs.get(sid)
            if (u.get("locator_type") or "page") == "section":
                # section locator → the rendered snapshot (.md/.txt/.html) is the artefact,
                # exactly as validate_sources resolves it (WOCAT adapter, 2026-10-06)
                snap = next(
                    (
                        CORPUS / f"{sid}{ext}"
                        for ext in (".md", ".txt", ".html")
                        if (CORPUS / f"{sid}{ext}").exists()
                    ),
                    None,
                )
                if snap is None:
                    errs.append(
                        f"{eid}: no cached snapshot for section locator ({sid})"
                    )
                else:
                    text = " ".join(
                        snap.read_text(encoding="utf-8", errors="replace").split()
                    )
                    if " ".join(_native_part(u["quote"]).split()) not in text:
                        errs.append(
                            f"{eid}: quote not verbatim in snapshot {snap.name}"
                        )
                    if not (u.get("locator") or "").strip():
                        errs.append(f"{eid}: section locator missing")
            elif d is None:
                errs.append(f"{eid}: no cached PDF for {sid}")
            else:
                try:
                    if source and source.get("artifact_sha1"):
                        digest = hashlib.sha1(
                            (CORPUS / f"{sid}.pdf").read_bytes()
                        ).hexdigest()
                        expected = source["artifact_sha1"]
                        if (
                            len(expected) not in (16, 40)
                            or digest[: len(expected)] != expected
                        ):
                            errs.append(
                                f"{eid}: cached PDF hash differs from SRC; reverify source identity"
                            )
                    text = " ".join(d[u["page"] - 1].get_text().split())
                    # a non-English quote is stored "<native> (English: <translation>)" per
                    # the AGENTS.md lock; only the native part is in the PDF, so verify that
                    # - the central guardrail (validate_sources) already does exactly this
                    if " ".join(_native_part(u["quote"]).split()) not in text:
                        errs.append(f"{eid}: quote not verbatim on page {u['page']}")
                except Exception as e:  # noqa: BLE001
                    errs.append(f"{eid}: page {u.get('page')} unreadable ({e})")
            for quote_key, page_key in (
                ("justification_quote", "justification_page"),
                ("selection_justification", "selection_justification_page"),
            ):
                supplementary = u.get(quote_key)
                supplementary_page = u.get(page_key)
                if not supplementary and supplementary_page is None:
                    continue
                if not supplementary or supplementary_page is None:
                    errs.append(
                        f"{eid}: {quote_key} and {page_key} must be supplied together"
                    )
                    continue
                native = " ".join(_native_part(supplementary).split())
                if len("".join(c for c in native if c.isalnum())) < 12:
                    errs.append(f"{eid}: {quote_key} lacks a substantive native quote")
                    continue
                if d is None:
                    errs.append(
                        f"{eid}: {quote_key} needs cached PDF for its page locator"
                    )
                    continue
                try:
                    supplementary_text = " ".join(
                        d[supplementary_page - 1].get_text().split()
                    )
                    if native not in supplementary_text:
                        errs.append(
                            f"{eid}: {quote_key} not verbatim on page {supplementary_page}"
                        )
                except (IndexError, ValueError) as exc:
                    errs.append(f"{eid}: {page_key} unreadable ({exc})")
            rel = u.get("relationship") or {}
            # the WHOLE relationship, exactly the surface `check_numbers.check` walks — not
            # only the numeric fields. The 2026-10-13 retrospective found the gate passing
            # lanes that the next build then flagged at 23%: every miss was a study descriptor
            # (buffer width, exceedance probability, project geometry) written into
            # `outcome_raw`, where a mis-stitched value would hide just as well. Descriptors
            # belong in `context.note`, which is not a claim surface (catalogue #22).
            rn = _rel_nums(json.dumps(rel, ensure_ascii=False))
            # compare as FLOATS, like check_numbers.check: otherwise an integral float
            # magnitude (41.0) never matches a quote that prints "41"
            q = _nums(_native_part(u["quote"]))
            missing = sorted(
                n for n in rn if n not in q and not (_floats({n}) & _floats(q))
            )
            if missing:
                errs.append(
                    f"{eid}: numbers not in quote {missing} — if these are study descriptors, "
                    "move them to context.note; relationship carries claims only"
                )
            row = {
                "evidence_id": eid,
                "use_role": u["use_role"],
                "variable": u["variable"],
                # the QUOTE has to travel with the row: check_context verifies a `severity_cue`
                # verbatim against quote / note / outcome_raw, and without it a cue that lives
                # only in the quote (the normal case) failed here while passing the central
                # guardrail — so lanes were pushing cues into `note` to satisfy a false flag
                "quote": u.get("quote") or "",
                "ruleset_version": u.get("ruleset_version") or "",
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
            errs += [
                f"{eid}: direction {f['signal']} {f['detail']}"
                for f in check_direction.check_unit(
                    {
                        **row,
                        "variable": u.get("variable", ""),
                        "use_role": u.get("use_role", ""),
                        "source_id": sid,
                        "relationship": json.dumps(rel),
                    }
                )
            ]
            if u["variable"] not in vont:
                errs.append(f"{eid}: variable '{u['variable']}' has no VONT id")
            if u.get("suitability_family_id") not in fams:
                errs.append(
                    f"{eid}: family '{u.get('suitability_family_id')}' not in FAM"
                )
            if u.get("use_role") not in allowed_roles:
                errs.append(
                    f"{eid}: use_role '{u.get('use_role')}' is not allowed here "
                    f"(allowed: {sorted(allowed_roles)})"
                )
            if u.get("ruleset_version") not in _RULESETS:
                errs.append(
                    f"{eid}: ruleset_version '{u.get('ruleset_version')}' not in {sorted(_RULESETS)}"
                )
    return errs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("files", nargs="+")
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
    args = ap.parse_args(argv)
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
    errs = gate(units, roles)
    print(
        f"{len(units)} staged unit(s) from {len(args.files)} file(s); roles {dict(Counter(str(u.get('use_role', '<missing>')) for u in units))}"
    )
    if errs:
        print(f"GATE FAILED: {len(errs)} problem(s) — nothing written")
        for e in errs[:40]:
            print("  -", e)
        return 1
    print(
        "gates clean: verbatim · numbers · context · bands · VONT · FAM · role · ruleset"
    )
    try:
        n = append_to_register(units, dry_run=args.dry_run)
    except ValueError as exc:
        print(f"APPEND FAILED — nothing written: {exc}")
        return 1
    if args.dry_run:
        print(f"append validation clean: {n} new unit(s); nothing written")
        return 0
    touched = {u["source_id"] for u in units}
    changed = resync_vars_extracted(touched)
    print(
        f"appended {n} new unit(s) to EV; vars_extracted resynced for {len(changed)} source(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
