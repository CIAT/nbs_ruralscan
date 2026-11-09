"""T3/T6/T6E compilation from explicitly selected records and policies.

The CLI retains the existing checkout defaults. This adapter never selects code
from the input snapshot and does not promote a compiled candidate to a release.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

from .table_fields import T3_FIELDS, T6_FIELDS
from nbs_ruralscan.recipe import cell_synthesis as cs
from nbs_ruralscan.recipe import prose as P
from nbs_ruralscan.recipe.evidence import EvidenceUnit, load_units
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import staged_publish


def check_nbs_id(nbs_id: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", nbs_id):
        raise ValueError("Invalid NbS identifier")


@dataclass(frozen=True)
class T3T6BuildInputs:
    """Every file consumed by effect synthesis, independent of compiler location.

    Evidence is the maintained typed JSON, as in the existing effect pipeline.
    Run the existing CSV-to-JSON synchronization gate before selecting a snapshot.
    A missing prose sidecar means no authored prose; every other input is required.
    """

    evidence: Path
    sources: Path
    families: Path
    crosswalk: Path
    income_groups: Path
    confidence_matrix: Path
    comparator_policy: Path
    route_policy: Path
    family_policy: Path
    crop_policy: Path
    effect_locus: Path
    magnitude_bands: Path
    design_weights: Path
    prose: Path

    @classmethod
    def from_root(cls, root: Path, nbs_id: str) -> T3T6BuildInputs:
        check_nbs_id(nbs_id)
        schema = Path(root).resolve() / "schema"
        reg, look = schema / "registers", schema / "lookups"
        return cls(
            evidence=reg / "EV_evidence_register.json",
            sources=reg / "SRC_source_register.csv",
            families=reg / "FAM_family_registry.csv",
            crosswalk=reg / "XW_target_crosswalk.csv",
            income_groups=look / "wb_income_groups.csv",
            confidence_matrix=look / "ipcc_confidence_matrix.csv",
            comparator_policy=look / "comparator_policy.csv",
            route_policy=look / "xw_route_policy.csv",
            family_policy=look / "family_rollup_policy.csv",
            crop_policy=look / "crop_scope_policy.csv",
            effect_locus=look / "effect_locus.csv",
            magnitude_bands=reg / "BANDS_magnitude_bands.csv",
            design_weights=look / "design_weights.csv",
            prose=schema / "recipes" / nbs_id / "T3T6_prose.json",
        )

    def paths(self) -> tuple[Path, ...]:
        return tuple(getattr(self, field.name) for field in fields(self))

    def validate(self) -> None:
        for field in fields(self):
            path = getattr(self, field.name)
            if field.name == "prose" and not path.exists():
                continue
            if not path.is_file():
                raise ValueError(f"Missing T3/T6 input ({field.name}): {path}")


T3_HAZARDS = cs.T3_HAZARDS


def _rd(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _cell(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def crop_scope_policy(nbs_id: str, *, path: Path) -> bool | frozenset[str]:
    """`allow_crop_scope` for an NbS from `schema/lookups/crop_scope_policy.csv`.

    A row with an empty `suitability_family_id` sets the NbS-wide policy (returns True).
    Family rows re-include crop_specific units of THOSE families only (returns the set) —
    e.g. AF F5 shaded perennials, wetland peatland paludiculture. Until 2026-10-22 family
    rows were ignored here, so those ratified rulings never reached T3/T6.
    Default False = the species/crop lock (`claim_scope=crop_specific` routed out)."""
    if not path.exists():
        return False
    fams: set[str] = set()
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["nbs_id"] != nbs_id:
                continue
            if str(r.get("allow_crop_scope") or "").lower() != "true":
                continue
            fam = (r.get("suitability_family_id") or "").strip()
            if not fam:
                return True
            fams.add(fam)
    return frozenset(fams) if fams else False


def load_inputs(
    nbs_id: str, staging: list[Path], *, inputs: T3T6BuildInputs
) -> dict[str, Any]:
    check_nbs_id(nbs_id)
    inputs.validate()
    for path in staging:
        if not path.is_file():
            raise ValueError(f"Missing staging input: {path}")
    src = _rd(inputs.sources)
    tiers = {r["source_id"]: (r["benchmark_tier"] or "medium").lower() for r in src}
    categories = {r["source_id"]: r.get("source_category", "") for r in src}
    # SRC.study_country is free text ("Brazil; Colombia; Mexico", "Global"): normalise to
    # ISO3 here so the envelope never carries a raw name (riparian prose review 2026-10-01)
    name_to_iso3 = {r["country_name"]: r["iso3"] for r in _rd(inputs.income_groups)}
    src_contexts: dict[str, dict[str, Any]] = {}
    unresolved: dict[str, list[str]] = {}
    for r in src:
        codes, bad = cs.normalise_countries(r.get("study_country", ""), name_to_iso3)
        if bad:
            unresolved[r["source_id"]] = bad
        src_contexts[r["source_id"]] = {
            "country": codes,
            "aez": r.get("aez", ""),
            "farming_system": r.get("farming_system", ""),
            "income_group": r.get("study_income_group", ""),
        }
    xw = cs.load_xw(inputs.crosswalk)
    income = cs.load_income_lookup(inputs.income_groups)
    matrix = cs.load_confidence_matrix(inputs.confidence_matrix)
    # a `qualitative_only` family (FAM.spatial_product_type) is parked out of the scored
    # tables: its evidence stays in the register for Module 6 hand-off material but never
    # sets a T3/T6 class (Pete 2026-10-06: rooftop / household cisterns are a built domestic
    # supply technology, not a landscape NbS)
    parked = {
        r["suitability_family_id"]
        for r in _rd(inputs.families)
        if r["nbs_id"] == nbs_id
        and r.get("spatial_product_type") == "qualitative_only"
        # the cross-cutting envelope meta-tag is qualitative_only too, but it is a
        # tagging value for pooled evidence, not a parked practice
        and not r["subpractice_id"].startswith("cross_cutting_envelope")
    }
    units = [
        u
        for u in load_units(inputs.evidence)
        if u.nbs_id == nbs_id
        and u.use_role in cs.EFFECT_ROLES
        # soft-deleted rows stay in the register as records; the engine skips them per
        # cell, but the run report must not count them as pooled (2026-10-06)
        and getattr(u, "review_state", "") != "dropped"
        and u.suitability_family_id not in parked
    ]
    for p in staging:
        units += [
            u
            for u in load_units(p)
            if u.nbs_id == nbs_id and u.use_role in cs.EFFECT_ROLES
        ]
    return {
        "units": units,
        "parked_families": sorted(parked),
        "tiers": tiers,
        "categories": categories,
        "src_contexts": src_contexts,
        "src_country_unresolved": unresolved,
        "xw": xw,
        "income": income,
        "matrix": matrix,
        "comparator_policy": cs.load_comparator_policy(inputs.comparator_policy),
        "route_policy": cs.load_xw_route_policy(inputs.route_policy),
        "family_policy": cs.load_family_rollup_policy(inputs.family_policy),
        "crop_policy": crop_scope_policy(nbs_id, path=inputs.crop_policy),
        "effect_locus": cs.load_effect_locus(inputs.effect_locus),
        "bands": cs.load_bands(inputs.magnitude_bands),
        "design_weights": cs.load_design_weights(inputs.design_weights),
    }


def synthesise(nbs_id: str, inp: dict[str, Any]) -> dict[str, Any]:
    check_nbs_id(nbs_id)
    units: list[EvidenceUnit] = inp["units"]
    xw: list[cs.XWRow] = cs.filter_xw(inp["xw"], nbs_id, inp["route_policy"])
    common: dict[str, Any] = {
        "categories": inp["categories"],
        "src_contexts": inp["src_contexts"],
        "income_lookup": inp["income"],
        "matrix": inp["matrix"],
        "xw_rows": xw,
        # crop_specific re-inclusion is a per-NbS policy read from the schema, never
        # hardcoded (schema/lookups/crop_scope_policy.csv; Pete 2026-10-06 for WH)
        "allow_crop_scope": inp["crop_policy"],
        "bands": inp["bands"],
        "design_weights": inp["design_weights"],
    }
    t3_rows: list[dict[str, Any]] = []
    t6_rows: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "nbs_id": nbs_id,
        "n_units_pooled": len(units),
        "parked_families": inp.get("parked_families", []),
        "units_by_role": dict(Counter(u.use_role for u in units)),
        "cells": [],
        "dropped": [],
        "collapsed": [],
        "excluded_economics": [],
        "weights_incomplete": [],
        "notes": [],
    }
    live_vars = {u.variable for u in units if u.use_role == "nbs_effect"}
    routed_vars = {x.ev_variable for x in xw}
    report["unmapped_variables"] = sorted(
        {
            v: sum(1 for u in units if u.variable == v and u.use_role == "nbs_effect")
            for v in live_vars - routed_vars
        }.items()
    )

    def _collect(rows, rep, table, key):
        report["cells"].append(
            {
                "table": table,
                "cell": key,
                "rows": len(rows),
                "used": len(rep.used),
                "scope_rows": rep.scope_rows_emitted,
            }
        )
        report["dropped"] += [(table, key, *d) for d in rep.dropped]
        report["collapsed"] += [(table, key, *c) for c in rep.collapsed]
        report["excluded_economics"] += [
            (table, key, *e) for e in rep.excluded_economics
        ]
        report["notes"] += rep.notes

    # ── T6: every XW T6 target (priorities + economic indicators) ──
    for key in sorted({x.target_key for x in xw if x.target_table == "T6"}):
        rows, rep = cs.synthesise_cell_with_families(
            units,
            inp["tiers"],
            table="T6",
            nbs_id=nbs_id,
            comparator_policy=inp["comparator_policy"],
            family_rollup_policy=inp["family_policy"],
            target_key=key,
            **common,
        )
        if rows:
            t6_rows += rows
            _collect(rows, rep, "T6", key)

    # ── T3 mitigation: every XW T3 hazard × the farming systems present (+ all) ──
    fs_present = sorted(
        {str((u.context or {}).get("farming_system") or "all") for u in units} | {"all"}
    )
    for hz in sorted({x.target_key for x in xw if x.target_table == "T3"}):
        for fs in fs_present:
            rows, rep = cs.synthesise_cell_with_families(
                units,
                inp["tiers"],
                table="T3",
                nbs_id=nbs_id,
                comparator_policy=inp["comparator_policy"],
                family_rollup_policy=inp["family_policy"],
                target_key=hz,
                farming_system=fs,
                **common,
            )
            if rows:
                t3_rows += rows
                _collect(rows, rep, "T3", f"{hz}__{fs}")

    # ── T3 asset threat: per hazard (+ asset-only hazards), from asset_vulnerability units ──
    for hz in T3_HAZARDS + cs.ASSET_ONLY_HAZARDS:
        rows, rep = cs.synthesise_cell_with_families(
            units,
            inp["tiers"],
            table="T3",
            nbs_id=nbs_id,
            comparator_policy=inp["comparator_policy"],
            family_rollup_policy=inp["family_policy"],
            target_key=hz,
            role="asset_vulnerability",
            **common,
        )
        if rows:
            t3_rows += rows
            _collect(rows, rep, "T3", f"asset_threat__{hz}")
    cs.apply_effect_locus(t3_rows, inp["effect_locus"])
    weights = cs.asset_risk_weights(t3_rows, nbs_id)
    if weights is None:
        if any(r.get("risk_role") == "asset_threat" for r in t3_rows):
            report["weights_incomplete"].append(nbs_id)
    else:
        for r in t3_rows:
            if (
                r.get("risk_role") == "asset_threat"
                and not r.get("scope_type")
                and not r.get("suitability_family_id")
                and r["hazard_type"] in weights  # asset-only hazards carry no weight
            ):
                r["asset_risk_weight"] = weights[r["hazard_type"]]

    # Pete 2026-10-23 (row review D8): cost rows are not scorecard effects — they move to the
    # NbS economic profile (T6E, feeds the econometric / economic-archetype profiles), and
    # cost per tCO2e is a feasibility-level figure, not generated at scoping grade
    econ = [r for r in t6_rows if r.get("variable_type") == "economic_indicator"]
    report["dropped_economics"] = sorted(
        {
            r["record_id"]
            for r in econ
            if r.get("variable_id") in cs.FEASIBILITY_ONLY_ECON
        }
    )
    t6e_rows = [r for r in econ if r.get("variable_id") not in cs.FEASIBILITY_ONLY_ECON]
    t6_rows = [r for r in t6_rows if r.get("variable_type") != "economic_indicator"]
    report["t3_rows"] = len(t3_rows)
    report["t6_rows"] = len(t6_rows)
    report["t6e_rows"] = len(t6e_rows)
    return {"T3": t3_rows, "T6": t6_rows, "T6E": t6e_rows, "report": report}


def write_recipe(
    nbs_id: str,
    out: dict[str, Any],
    *,
    inputs: T3T6BuildInputs,
    output_dir: Path,
    dry_run: bool,
) -> list[Path]:
    """Publish three recipe CSVs and their report with caught-failure recovery.

    Prose comes from the selected input sidecar, never from the destination. The
    four declared outputs are the only mutable files. Existing source records,
    sidecars and unrelated output files survive unchanged.
    """
    check_nbs_id(nbs_id)
    inputs.validate()
    rdir = Path(output_dir).absolute()
    tables = (
        ("T3", T3_FIELDS, "T3_nbs_hazard_farming.csv"),
        ("T6", T6_FIELDS, "T6_nbs_scorecard.csv"),
        ("T6E", T6_FIELDS, "T6E_economic_profile.csv"),
    )
    destinations = [rdir / name for _, _, name in tables]
    destinations.append(rdir / "T3T6_synthesis_report.json")
    if {p.resolve() for p in destinations} & {p.resolve() for p in inputs.paths()}:
        raise ValueError("Recipe outputs overlap declared inputs")
    paths = SchemaBuildPaths(rdir / "schema")
    paths.preflight(destinations)
    sidecar = (
        json.loads(inputs.prose.read_text(encoding="utf-8"))
        if inputs.prose.exists()
        else {}
    )
    for table, _, name in tables:
        if sidecar:
            applied, stale = P.apply_prose(
                out[table], "T6" if table == "T6E" else table, sidecar
            )
            print(
                f"{table}: prose applied to {applied} row(s); {stale} stale (evidence changed → pending)"
            )
        if dry_run:
            print(f"[dry-run] {rdir / name}: {len(out[table])} row(s)")
    if dry_run:
        return []

    def render(staged: SchemaBuildPaths) -> list[Path]:
        assert staged.output_root is not None
        for table, columns, name in tables:
            with (staged.output_root / name).open(
                "w", newline="", encoding="utf-8"
            ) as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=columns,
                    lineterminator="\n",
                    extrasaction="ignore",
                )
                writer.writeheader()
                writer.writerows(
                    {c: _cell(row.get(c)) for c in columns} for row in out[table]
                )
        (staged.output_root / "T3T6_synthesis_report.json").write_text(
            json.dumps(out["report"], ensure_ascii=False, indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        return []

    staged_publish(paths, destinations, render)
    # Preserve the legacy return: all four published paths, even for an unchanged run.
    return destinations


def _summary(out: dict[str, Any]) -> str:
    lines = [
        "| table | record_id | class | evidence×agreement→confidence | n | transfer | strength |",
        "|---|---|---|---|---|---|---|",
    ]
    for table in ("T3", "T6", "T6E"):
        for r in out[table]:
            cls = (
                r.get("effect_direction")
                or r.get("mitigation_potential")
                or r.get("asset_sensitivity")
            )
            conf = r.get("confidence") or r.get("effect_confidence")
            app = r.get("applicability") or {}
            sb = (r.get("justification") or {}).get("strength_basis", "")
            lines.append(
                f"| {table} | {r['record_id']} | {cls} | {r['evidence_level']}×{r['agreement_level']}→{conf} | {r.get('n_sources')} | {app.get('transfer_class')} | {sb} |"
            )
    rep = out["report"]
    lines.append("")
    lines.append(
        f"pooled units {rep['n_units_pooled']} {rep['units_by_role']}; T3 rows {rep['t3_rows']}; T6 rows {rep['t6_rows']}"
    )
    if rep["unmapped_variables"]:
        lines.append(f"unmapped variables: {rep['unmapped_variables']}")
    if rep["excluded_economics"]:
        lines.append(f"excluded economics: {len(rep['excluded_economics'])}")
    if rep["weights_incomplete"]:
        lines.append(
            f"asset_risk_weight blank (incomplete hazard set): {rep['weights_incomplete']}"
        )
    return "\n".join(lines)
