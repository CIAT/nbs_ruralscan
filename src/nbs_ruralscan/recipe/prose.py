"""Prose sidecar for generated T3/T6 rows (T3/T6 synthesis contract §5 — the one AI step).

The cell-synthesis engine writes every level, class, id list and the calibrated ``statement``
deterministically; the only text an AI may write is the *mechanism*, the *conditionality /
caveats*, and optionally a re-worded ``evidence_summary`` / ``agreement_note``. That prose is
kept OUT of the engine run, in a per-recipe sidecar ``schema/recipes/<nbs_id>/T3T6_prose.json``::

    {
      "<record_id>": {
        "evidence_ids": [...sorted ids the prose was written against...],
        "mechanism": "...", "conditionality": "...",
        "evidence_summary": [...] | null, "agreement_note": "..." | null,
        "written": "YYYY-MM-DD", "writer": "opus|human"
      }
    }

Re-running the synthesis re-applies a sidecar entry only while the row's ``evidence_ids`` are
exactly the set the prose was written against; otherwise the row goes back to
``[prose pending]`` (the prose may now be wrong). Every merge is gated by
``schema_tools.check_account`` (no number or id in the prose that is not in a used unit).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from nbs_ruralscan.schema_tools import check_account

PENDING = "[prose pending] "
PROSE_FIELDS = ("mechanism", "conditionality", "evidence_summary", "agreement_note")


def sidecar_path(recipe_dir: Path) -> Path:
    return recipe_dir / "T3T6_prose.json"


def load_sidecar(recipe_dir: Path) -> dict[str, dict[str, Any]]:
    p = sidecar_path(recipe_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def save_sidecar(recipe_dir: Path, sidecar: dict[str, dict[str, Any]]) -> Path:
    p = sidecar_path(recipe_dir)
    p.write_text(
        json.dumps(dict(sorted(sidecar.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return p


def _ids(row: dict[str, Any]) -> list[str]:
    ids = row.get("evidence_ids") or []
    if isinstance(ids, str):
        ids = json.loads(ids)
    return sorted(ids)


def mechanism_field(table: str) -> str:
    return "mitigation_mechanism" if table == "T3" else "effect_mechanism"


def conditionality_field(table: str) -> str:
    return "caveats" if table == "T3" else "conditionality"


def apply_prose(
    rows: list[dict[str, Any]], table: str, sidecar: dict[str, dict[str, Any]]
) -> tuple[int, int]:
    """Write sidecar prose onto engine rows in place. Returns (applied, stale)."""
    applied = stale = 0
    for r in rows:
        entry = sidecar.get(r["record_id"])
        if not entry:
            continue
        if sorted(entry.get("evidence_ids") or []) != _ids(r):
            stale += 1
            continue
        acc = r.get("justification")
        if isinstance(acc, str):
            acc = json.loads(acc) if acc else {}
        acc = dict(acc or {})
        r[mechanism_field(table)] = entry["mechanism"]
        r[conditionality_field(table)] = entry.get("conditionality") or ""
        acc["mechanism"] = entry["mechanism"]
        acc["conditionality"] = entry.get("conditionality") or ""
        if entry.get("evidence_summary"):
            acc["evidence_summary"] = entry["evidence_summary"]
        if entry.get("agreement_note"):
            acc["agreement_note"] = entry["agreement_note"]
        acc["prose_pending"] = False
        acc["prose_written"] = entry.get("written", "")
        r["justification"] = acc
        applied += 1
    return applied, stale


def check_prose(
    rows: list[dict[str, Any]],
    table: str,
    prose: dict[str, dict[str, Any]],
    ev: dict[str, dict] | None = None,
) -> list[dict[str, Any]]:
    """Validate a prose payload against the rows it targets WITHOUT writing anything.

    Flags: ``unknown_record`` · ``missing_mechanism`` · ``level_language`` (prose restating a
    confidence/evidence level — the engine owns those words) · everything
    ``check_account.check_row`` raises on the would-be merged row.
    """
    by_id = {r["record_id"]: r for r in rows}
    ev = ev if ev is not None else check_account._load_ev(check_account._EV)
    flags: list[dict[str, Any]] = []
    for rid, entry in prose.items():
        row = by_id.get(rid)
        if row is None:
            flags.append({"signal": "unknown_record", "record_id": rid, "detail": ""})
            continue
        if not (entry.get("mechanism") or "").strip():
            flags.append(
                {"signal": "missing_mechanism", "record_id": rid, "detail": ""}
            )
            continue
        for fld in ("mechanism", "conditionality"):
            txt = (entry.get(fld) or "").lower()
            for word in (
                "very_high confidence",
                "high confidence",
                "medium confidence",
                "low confidence",
                "robust evidence",
                "limited evidence",
            ):
                if word in txt:
                    flags.append(
                        {
                            "signal": "level_language",
                            "record_id": rid,
                            "detail": f"{fld}: '{word}' — levels are engine-owned",
                        }
                    )
        trial = json.loads(json.dumps(row, default=str))
        trial["evidence_ids"] = _ids(row)
        acc = trial.get("justification")
        if isinstance(acc, str):
            acc = json.loads(acc) if acc else {}
        trial["justification"] = dict(acc or {})
        apply_prose(
            [trial],
            table,
            {rid: {**entry, "evidence_ids": _ids(row)}},
        )
        flags += check_account.check_row(trial, ev)
    return flags


def merge_prose(
    recipe_dir: Path,
    rows: list[dict[str, Any]],
    table: str,
    prose: dict[str, dict[str, Any]],
    *,
    writer: str,
    ev: dict[str, dict] | None = None,
) -> tuple[int, list[dict[str, Any]]]:
    """Check, then record the prose in the sidecar (keyed to the rows' current evidence_ids)
    and apply it to ``rows``. Refuses (writes nothing) on any flag."""
    flags = check_prose(rows, table, prose, ev)
    if flags:
        return 0, flags
    by_id = {r["record_id"]: r for r in rows}
    sidecar = load_sidecar(recipe_dir)
    today = date.today().isoformat()
    for rid, entry in prose.items():
        sidecar[rid] = {
            "evidence_ids": _ids(by_id[rid]),
            "mechanism": entry["mechanism"].strip(),
            "conditionality": (entry.get("conditionality") or "").strip(),
            "evidence_summary": entry.get("evidence_summary") or None,
            "agreement_note": entry.get("agreement_note") or None,
            "written": today,
            "writer": writer,
        }
    save_sidecar(recipe_dir, sidecar)
    applied, _ = apply_prose(rows, table, sidecar)
    return applied, []
