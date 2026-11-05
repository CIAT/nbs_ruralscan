"""T3/T6 row selection for an AOI, plus a flat filterable view of every generated effect row.

The runtime side of T3/T6 scope rows (`methodology/T3_T6_generation_method.md` §2.3, §5.5;
developer guide `methodology/T3_T6_developer_handover.md`). A cell (T3 = nbs × hazard ×
farming system · T6/T6E = nbs × variable) can hold several rows: one global row plus scope rows
(`scope_type` / `scope_id`) and, optionally, one row per suitability family. Given an AOI's
contexts, `resolve` picks the **most-specific** matching row:

    admin_region > admin_country > hydrobasin > farming_system > aez > income_group > global

T3 also keys on `farming_system`: an AOI farming system with its own row wins over `all`.

The picked row's `transfer_class` says whether its evidence comes from the AOI's context. A
scope row was reconciled against its own scope, so its stored class stands. A global row was
reconciled against the WB-investable target (`income_group = lic_lmic`); for an LIC/LMIC AOI the
stored class stands, otherwise it is re-derived from the row's `applicability.income_groups`
source counts (an approximation: the generator's per-unit weights are not on the row — flagged
`transfer_basis = source_counts`). A global row that is `out_of_context` for the AOI returns
status `no_applicable_evidence`: show the gap, never the class as if it applied.

`write_flat` emits `docs/effect_rows_flat.csv` (every NbS, T3 + T6 + T6E, `applicability`
split into columns) from `generate.py schema`; never hand-edit it.

Stdlib only; reads the generated recipe JSON.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nbs_ruralscan.recipe.cell_synthesis import (
    INCOME_BAND,
    transfer_class_from_shares,
)

TABLES = {
    "T3": "T3_nbs_hazard_farming.json",
    "T6": "T6_nbs_scorecard.json",
    "T6E": "T6E_economic_profile.json",
}

# Most-specific-wins (method §2.3): BIND's order with income_group below aez.
SCOPE_PRECEDENCE: dict[str, int] = {
    "": 0,
    "income_group": 1,
    "aez": 2,
    "farming_system": 3,
    "hydrobasin": 4,
    "admin_country": 5,
    "admin_region": 6,
}
GENERATION_TARGET_BAND = "lic_lmic"


@dataclass
class EffectResolution:
    """Outcome of resolving one T3/T6 cell for an AOI."""

    status: str  # ok | no_applicable_evidence | no_row
    row: (
        dict[str, Any] | None
    )  # the picked row (attached greyed when no_applicable_evidence)
    scope_matched: str  # "global" or "<scope_type>-<scope_id>"
    transfer_class: str  # against the AOI ("" when no_row)
    transfer_basis: str  # stored | source_counts | ""
    note: str = ""


def load_rows(schema_root: str | Path, table: str) -> list[dict[str, Any]]:
    """Every generated row of `table` (T3 · T6 · T6E) across all NbS recipes."""
    out: list[dict[str, Any]] = []
    for p in sorted((Path(schema_root) / "recipes").glob(f"*/{TABLES[table]}")):
        out.extend(json.loads(p.read_text(encoding="utf-8")))
    return out


def _band(group: str) -> str:
    g = (group or "").strip().lower()
    return INCOME_BAND.get(g, g)


def _scope_matches(row: dict[str, Any], aoi: dict[str, str]) -> bool:
    st, sid = row.get("scope_type") or "", str(row.get("scope_id") or "")
    if not st:
        return True
    if st == "income_group":
        return bool(aoi.get("income_group")) and _band(sid) == _band(
            aoi["income_group"]
        )
    return bool(sid) and sid == aoi.get(st)


def _income_distance(a: str, b: str) -> int:
    ba, bb = _band(a), _band(b)
    if ba == bb:
        return 0
    return 2 if "high" in (ba, bb) else 1


def transfer_class_for_aoi(row: dict[str, Any], aoi: dict[str, str]) -> tuple[str, str]:
    """(transfer_class, basis) of a picked row against the AOI — see module docstring."""
    app = row.get("applicability") or {}
    stored = str(app.get("transfer_class") or "")
    aoi_band = _band(aoi.get("income_group", ""))
    if row.get("scope_type") or not aoi_band or aoi_band == GENERATION_TARGET_BAND:
        return stored, "stored"
    counts = app.get("income_groups") or {}
    total = sum(counts.values()) or 0
    if not total:
        return stored, "stored"
    # unknown / mixed income is at best adjacent (cell_synthesis.context_distance rule)
    ds = [
        (
            _income_distance(g, aoi_band)
            if _band(g) in ("lic_lmic", "upper_middle", "high")
            else 1,
            n,
        )
        for g, n in counts.items()
    ]
    s0 = sum(n for d, n in ds if d == 0) / total
    s1 = sum(n for d, n in ds if d <= 1) / total
    s2 = sum(n for d, n in ds if d == 2) / total
    return transfer_class_from_shares(s0, s1, s2), "source_counts"


def resolve(
    rows: list[dict[str, Any]],
    nbs_id: str,
    aoi: dict[str, str],
    *,
    hazard_type: str = "",
    variable_id: str = "",
    family: str = "",
    risk_role: str = "",
) -> EffectResolution:
    """Pick the row for one cell over an AOI.

    `aoi` maps context type → id, e.g. ``{"income_group": "low", "farming_system":
    "agro_pastoral", "admin_country": "NER"}``. Pass `hazard_type` for a T3 cell (optionally
    `risk_role` = livelihood_mitigation | asset_threat), `variable_id` for a T6/T6E cell.
    `family` = a `suitability_family_id`; blank = the NbS roll-up row.
    """

    def in_cell(r: dict[str, Any]) -> bool:
        if (
            r.get("nbs_id") != nbs_id
            or (r.get("suitability_family_id") or "") != family
        ):
            return False
        if hazard_type:
            if r.get("hazard_type") != hazard_type:
                return False
            if risk_role and r.get("risk_role") != risk_role:
                return False
        elif r.get("variable_id") != variable_id:
            return False
        return True

    cell = [r for r in rows if in_cell(r)]
    if hazard_type:  # T3 keys on farming_system: the AOI's own system wins over "all"
        fs = aoi.get("farming_system", "")
        own = [r for r in cell if r.get("farming_system") == fs] if fs else []
        cell = own or [r for r in cell if r.get("farming_system") == "all"]
    cands = [r for r in cell if _scope_matches(r, aoi)]
    if not cands:
        return EffectResolution(
            "no_row", None, "", "", "", "no generated row for this cell"
        )
    best = max(cands, key=lambda r: SCOPE_PRECEDENCE.get(r.get("scope_type") or "", 0))
    st = best.get("scope_type") or ""
    scope = f"{st}-{best.get('scope_id')}" if st else "global"
    tc, basis = transfer_class_for_aoi(best, aoi)
    if not st and tc == "out_of_context":
        app = best.get("applicability") or {}
        groups = ", ".join(
            f"{g} {n}" for g, n in (app.get("income_groups") or {}).items()
        )
        return EffectResolution(
            "no_applicable_evidence",
            best,
            scope,
            tc,
            basis,
            f"evidence from other contexts only ({groups}; n = {app.get('n_sources_in_scope', 0)})",
        )
    return EffectResolution("ok", best, scope, tc, basis)


# ── flat view ─────────────────────────────────────────────────────────────────────────

FLAT_COLUMNS = [
    "table",
    "record_id",
    "nbs_id",
    "suitability_family_id",
    "cell",
    "hazard_type",
    "farming_system",
    "risk_role",
    "variable_id",
    "variable_type",
    "scope_type",
    "scope_id",
    "class",
    "confidence",
    "evidence_level",
    "agreement_level",
    "transfer_class",
    "weight_share_in_context",
    "n_sources_in_scope",
    "countries",
    "income_groups",
    "farming_systems_evidence",
    "aezs",
    "context_dependent",
    "family_spread",
    "landscape_scale_only",
    "data_deficient",
    "economic_indicator_type",
    "statement",
    "n_evidence_ids",
]


def _counts(d: dict[str, int] | None) -> str:
    return "; ".join(f"{k}:{v}" for k, v in (d or {}).items())


def flatten(table: str, r: dict[str, Any]) -> dict[str, Any]:
    app = r.get("applicability") or {}
    just = r.get("justification")
    j: dict[str, Any] = just if isinstance(just, dict) else {}
    t3 = table == "T3"
    return {
        "table": table,
        "record_id": r.get("record_id", ""),
        "nbs_id": r.get("nbs_id", ""),
        "suitability_family_id": r.get("suitability_family_id", ""),
        "cell": f"{r.get('hazard_type')}|{r.get('farming_system')}"
        if t3
        else r.get("variable_id", ""),
        "hazard_type": r.get("hazard_type", ""),
        "farming_system": r.get("farming_system", ""),
        "risk_role": r.get("risk_role", ""),
        "variable_id": r.get("variable_id", ""),
        "variable_type": r.get("variable_type", ""),
        "scope_type": r.get("scope_type", ""),
        "scope_id": r.get("scope_id", ""),
        "class": r.get("mitigation_potential" if t3 else "effect_direction", "")
        or r.get("asset_sensitivity", ""),
        "confidence": r.get("confidence" if t3 else "effect_confidence", ""),
        "evidence_level": r.get("evidence_level", ""),
        "agreement_level": r.get("agreement_level", ""),
        "transfer_class": app.get("transfer_class", ""),
        "weight_share_in_context": app.get("weight_share_in_context", ""),
        "n_sources_in_scope": app.get("n_sources_in_scope", ""),
        "countries": "; ".join(app.get("countries") or []),
        "income_groups": _counts(app.get("income_groups")),
        "farming_systems_evidence": _counts(app.get("farming_systems")),
        "aezs": _counts(app.get("aezs")),
        "context_dependent": r.get("context_dependent", ""),
        "family_spread": r.get("family_spread", ""),
        "landscape_scale_only": r.get("landscape_scale_only", ""),
        "data_deficient": j.get("data_deficient", ""),
        "economic_indicator_type": r.get("economic_indicator_type", ""),
        "statement": j.get("statement", ""),
        "n_evidence_ids": len(r.get("evidence_ids") or []),
    }


def build_flat(schema_root: str | Path, *, from_csv: bool = False) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FLAT_COLUMNS, lineterminator="\n")
    w.writeheader()
    for table in TABLES:
        if from_csv:
            from nbs_ruralscan.schema_tools.generate import _csv_to_rows

            rows = [
                row
                for path in sorted(
                    (Path(schema_root) / "recipes").glob(
                        f"*/{Path(TABLES[table]).with_suffix('.csv')}"
                    )
                )
                for row in _csv_to_rows(path)
            ]
        else:
            rows = load_rows(schema_root, table)
        for r in rows:
            w.writerow(flatten(table, r))
    return buf.getvalue()


def write_flat(
    schema_root: str | Path,
    check: bool = False,
    dest: Path | None = None,
    *,
    from_csv: bool = False,
) -> list[Path]:
    """(Re)write `docs/effect_rows_flat.csv`; returns [dest] when it changed (or would)."""
    schema_root = Path(schema_root)
    dest = Path(dest) if dest else schema_root.parent / "docs" / "effect_rows_flat.csv"
    text = build_flat(schema_root, from_csv=from_csv)
    if dest.exists() and dest.read_text(encoding="utf-8") == text:
        return []
    if not check:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    return [dest]
