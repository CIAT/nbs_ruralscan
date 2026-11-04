"""Pure, conservative dashboard counts; no analytical or review state is changed.

Source records, search observations, excerpts and compiled relationships are different
units. Their totals must never be added together or treated as a single funnel.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any

from .ledger import tables_for


def _list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple, set)):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value or "").strip()
    if text.startswith("["):
        try:
            return _list(json.loads(text))
        except (ValueError, TypeError):
            return []
    return [v.strip() for v in re.split(r"[|;,]", text) if v.strip()]


def _integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    text = str(value).strip()
    return int(text) if re.fullmatch(r"[0-9]+", text) else None


def _approved(row: dict) -> bool:
    return str(row.get("reviewer_ok", "")).lower() == "true"


def _source_type(row: dict, is_tool: bool = False) -> str:
    if is_tool or row.get("source_category") == "tool":
        return "tools"
    venue = str(row.get("venue_type") or "").lower()
    if venue in {"journal", "peer_reviewed_journal"}:
        return "literature"
    if venue in {"report", "agency_report", "government_report", "grey_literature"}:
        return "grey"
    kind = str(row.get("source_kind") or "").lower()
    if kind in {"paper", "journal_article"}:
        return "literature"
    if kind in {"grey_lit", "report"}:
        return "grey"
    if row.get("source_category") == "updated_lit":
        return "literature"
    if row.get("source_category") == "grey":
        return "grey"
    return "unknown"


def _searches(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for index, row in enumerate(rows):
        run = row.get("run_id") or ""
        identity = tuple(
            str(row.get(k) or "")
            for k in (
                "nbs_id",
                "suitability_family_id",
                "category",
                "run_id",
                "search_date",
                "search_terms",
                "limits",
            )
        )
        # With no run provenance, even identical text is not proof of shared work.
        key = identity if run else (*identity, row.get("search_id") or index)
        groups[key].append(row)
    events = []
    for rows_in_group in groups.values():
        first = rows_in_group[0]
        raw_counts = [
            {k: r.get(k, "") for k in ("n_retrieved", "n_screened", "n_included")}
            for r in rows_in_group
        ]
        # Retrieval work may be shared across tables whose screening protocols differ.
        # Preserve that single retrieval, but never add incompatible screening cohorts.
        screening_variants = {
            (
                str(r.get("screening_steps") or ""),
                str(r.get("inclusion_criteria") or ""),
            )
            for r in rows_in_group
        }
        conflicts = []
        counts = {}
        for field in ("retrieved", "screened", "included"):
            raw_values = {str(r.get("n_" + field, "")).strip() for r in rows_in_group}
            if len(raw_values) > 1:
                conflicts.append(field)
            counts[field] = (
                _integer(first.get("n_" + field)) if len(raw_values) == 1 else None
            )
            if field != "retrieved" and len(screening_variants) > 1:
                counts[field] = None
        complete = all(v is not None for v in counts.values())
        retrieved, screened, included = (
            counts[k] for k in ("retrieved", "screened", "included")
        )
        valid = (
            retrieved is not None
            and screened is not None
            and included is not None
            and retrieved >= screened >= included
        )
        event = dict(first)
        event.update(
            search_ids=sorted(
                {r["search_id"] for r in rows_in_group if r.get("search_id")}
            ),
            tables=sorted({r["table"] for r in rows_in_group if r.get("table")}),
            raw_records=[dict(r) for r in rows_in_group],
            raw_counts=raw_counts,
            counts=counts,
            counts_conflict=bool(conflicts),
            count_conflict_fields=conflicts,
            screening_variants=len(screening_variants),
            complete_counts=bool(valid),
            invalid_order=bool(complete and not valid),
        )
        events.append(event)
    return events


def _search_metrics(events: list[dict]) -> dict:
    complete = [e for e in events if e["complete_counts"]]
    paired_retrieved = sum(e["counts"]["retrieved"] for e in complete)
    paired_screened = sum(e["counts"]["screened"] for e in complete)
    out = {
        "events": len(events),
        "complete_counts": len(complete),
        "screened_pct": (
            round(100 * paired_screened / paired_retrieved, 1)
            if paired_retrieved
            else None
        ),
        "paired_retrieved": paired_retrieved,
        "paired_screened": paired_screened,
        "paired_included": sum(e["counts"]["included"] for e in complete),
        "coverage": {},
        "screening_variant_events": sum(e["screening_variants"] > 1 for e in events),
        "definition": "Search observations, not unique publications; shared retrievals counted once, table-specific screening variants not aggregated. Searches may overlap.",
    }
    for field in ("retrieved", "screened", "included"):
        values = [
            e["counts"][field]
            for e in events
            if e["counts"][field] is not None and not e["invalid_order"]
        ]
        out[field] = sum(values) if values else None
        out["coverage"][field] = {"recorded": len(values), "total": len(events)}
    return out


def build_progress(data: dict, queue: list[dict]) -> dict:
    """Build presentation-only progress facts from supplied records, without I/O."""
    registers = data.get("registers", {})
    src = registers.get("SRC_source_register", [])
    ev = list(registers.get("EV_evidence_register", [])) + list(
        data.get("_evDropped", [])
    )
    # A repeated payload row must not count twice (e.g. _evDropped plus full EV).
    evidence = {r["evidence_id"]: r for r in ev if r.get("evidence_id")}
    # Count assessment work separately from current approval. Reopened or queried
    # claims have been assessed, but are not necessarily resolved. A flag alone can
    # be an automated detector output, so cannot establish a review took place.
    assessment_actions = {"ok", "keep", "drop", "query", "reclassify", "retag"}
    assessed_ids = {
        r.get("evidence_id")
        for r in data.get("review_log", [])
        if str(r.get("decision", "")).strip().lower() in assessment_actions
    } & evidence.keys()
    assessed_ids.update(eid for eid, row in evidence.items() if _approved(row))
    families = registers.get("FAM_family_registry", [])
    tools = registers.get("TOOL_tool_registry", [])
    searches = _searches(registers.get("SRCH_search_register", []))
    parent: dict[str, str] = {}
    targets: set[str] = set()
    outgoing: set[str] = set()

    def root(sid: str) -> str:
        parent.setdefault(sid, sid)
        while parent[sid] != sid:
            sid = parent[sid]
        return sid

    for row in [*src, *queue]:
        sid = str(row.get("source_id") or "").strip()
        if sid:
            root(sid)
    for row in queue:
        sid = str(row.get("source_id") or "").strip()
        target = str(row.get("duplicate_of") or "").strip()
        if sid and target:
            targets.add(target)
            outgoing.add(sid)
            left, right = root(sid), root(target)
            if left != right:
                parent[left] = right
    components: dict[str, set[str]] = defaultdict(set)
    for sid in parent:
        components[root(sid)].add(sid)
    canonical = {}
    for members in components.values():
        terminal = members & (targets - outgoing)
        key = sorted(terminal or members)[0]
        canonical.update({sid: key for sid in members})

    family_lookup: dict[str, dict] = {}
    for fam in families:
        fid = fam.get("suitability_family_id")
        if not fid:
            continue
        presentation = data.get("family_presentation", {}).get(fid, {})
        navigation_group = presentation.get("navigation_group") or (
            "evidence" if fid.endswith("__cross_family") else "practice"
        )
        group = family_lookup.setdefault(
            fid,
            {
                "family_id": fid,
                "nbs_id": fam.get("nbs_id", ""),
                "name": presentation.get("display_name")
                or fid.split("__")[-1].replace("_", " ").capitalize(),
                "navigation_group": navigation_group,
                "subpractices": [],
                "scope_kind": (
                    "all_families" if fid.endswith("__cross_family") else "family"
                ),
                "scope_definition": fam.get("definition", ""),
            },
        )
        entry = {
            "subpractice_id": fam.get("subpractice_id", ""),
            "name": fam.get("name", ""),
            "presentation_role": "evidence"
            if navigation_group == "evidence"
            else "umbrella"
            if fam.get("subpractice_id") == presentation.get("umbrella_subpractice_id")
            else "variant",
        }
        if entry not in group["subpractices"]:
            group["subpractices"].append(entry)

    def family_ids(row: dict) -> set[str]:
        values = _list(row.get("suitability_family_id") or row.get("family"))
        nbs = _list(row.get("nbs_ids") or row.get("nbs_id"))
        resolved = set()
        for value in values:
            if "__" in value:
                resolved.add(value)
            else:
                matches = {
                    f
                    for f, item in family_lookup.items()
                    if item["nbs_id"] in nbs and f.endswith("__" + value)
                }
                resolved.update(matches or {value})
        return resolved

    records: dict[str, dict] = {}
    type_sets: dict[str, set[str]] = defaultdict(set)
    for row in [*src, *queue]:
        sid = str(row.get("source_id") or "").strip()
        if not sid:
            continue
        key = canonical[sid]
        record = records.setdefault(
            key,
            {
                "key": key,
                "source_id": key,
                "aliases": [],
                "citation": "",
                "url": "",
                "doi": "",
                "type": "unknown",
                "origins": set(),
                "nbs_ids": set(),
                "family_ids": set(),
                "screening": "not_recorded",
                "search_ids": [],
                "extraction_status": set(),
                "queue_statuses": set(),
                "evidence_ids": set(),
                "dropped_evidence_ids": set(),
                "approved_evidence_ids": set(),
                "reviewed_evidence_ids": set(),
                "extraction_counts": {k: 0 for k in ("T4", "effects", "M2b", "other")},
                "contributions": {k: set() for k in ("T4", "T3", "T6", "M2b")},
            },
        )
        record["aliases"] = sorted(
            k for k, v in canonical.items() if v == key and k != key
        )
        for field in ("citation", "url", "doi"):
            if not record[field] and row.get(field):
                record[field] = row[field]
        record["nbs_ids"].update(_list(row.get("nbs_ids") or row.get("nbs_id")))
        record["family_ids"].update(family_ids(row))
        if row.get("source_category"):
            record["origins"].add(row["source_category"])
        if row.get("status"):
            record["queue_statuses"].add(row["status"])
        if row.get("extraction_status"):
            record["extraction_status"].add(row["extraction_status"])
        kind = _source_type(row)
        if kind != "unknown":
            type_sets[key].add(kind)
    for tool in tools:
        key = canonical.get(tool.get("source_id"))
        if key in records:
            records[key].setdefault("tools", []).append(dict(tool))
            type_sets[key] = {"tools"}
    for key, record in records.items():
        kinds = type_sets[key]
        record["type"] = next(iter(kinds)) if len(kinds) == 1 else "unknown"

    active = {
        eid: row
        for eid, row in evidence.items()
        if row.get("review_state") != "dropped"
    }
    for eid, row in evidence.items():
        key = canonical.get(row.get("source_id"))
        if key not in records:
            continue
        record = records[key]
        record["nbs_ids"].update(_list(row.get("nbs_id")))
        record["family_ids"].update(family_ids(row))
        field = "evidence_ids" if eid in active else "dropped_evidence_ids"
        record[field].add(eid)
        if eid in assessed_ids:
            record["reviewed_evidence_ids"].add(eid)
        if eid in active:
            role = row.get("use_role")
            bucket = {
                "structural_suitability": "T4",
                "nbs_effect": "effects",
                "operational_risk": "M2b",
                "asset_vulnerability": "M2b",
            }.get(role, "other")
            record["extraction_counts"][bucket] += 1
        if eid in active and _approved(row):
            record["approved_evidence_ids"].add(eid)
        if eid in active and row.get("use_role") in {
            "operational_risk",
            "asset_vulnerability",
        }:
            record["contributions"]["M2b"].add(eid)

    unresolved_compiled = set()
    dropped_compiled = set()
    table_specs = {
        "T2a": ("Climate risk", "risk indicators"),
        "T3": ("Hazard response", "hazard-response assessments"),
        "T4": ("Suitability", "suitability rules"),
        "T6": ("Benefits", "benefit assessments"),
    }
    output_rows: dict[str, dict[tuple, dict]] = {t: {} for t in table_specs}

    def add_output(table: str, nbs: str, row: dict, index: int) -> None:
        identity = str(
            row.get("mapping_id")
            or row.get("record_id")
            or (row.get("variable_id") if table == "T2a" else "")
            or f"unkeyed:{index}"
        )
        key = (nbs, identity)
        cited = set(_list(row.get("evidence_ids")))
        unresolved_compiled.update(cited - evidence.keys())
        dropped_compiled.update(cited & (evidence.keys() - active.keys()))
        label_parts = [
            str(row.get("variable_id") or row.get("hazard_type") or identity).replace(
                "_", " "
            )
        ]
        fids = family_ids(row)
        if fids:
            label_parts.append(
                ", ".join(
                    family_lookup.get(f, {}).get("name")
                    or f.split("__")[-1].replace("_", " ")
                    for f in sorted(fids)
                )
            )
        elif table in {"T3", "T6"}:
            label_parts.append("practice roll-up")
        if row.get("farming_system"):
            label_parts.append(
                "farming system: " + str(row["farming_system"]).replace("_", " ")
            )
        if row.get("scope_type") or row.get("scope_id"):
            label_parts.append(
                str(row.get("scope_type", "context")).replace("_", " ")
                + ": "
                + str(row.get("scope_id", "")).replace("_", " ")
            )
        if row.get("risk_role"):
            label_parts.append(str(row["risk_role"]).replace("_", " "))
        output = output_rows[table].setdefault(
            key,
            {
                "id": identity,
                "label": " · ".join(label_parts),
                "farming_system": row.get("farming_system", ""),
                "scope_type": row.get("scope_type", ""),
                "scope_id": row.get("scope_id", ""),
                "risk_role": row.get("risk_role", ""),
                "nbs_id": nbs,
                "family_ids": family_ids(row),
                "evidence_ids": set(),
                "cited_evidence_ids": set(),
            },
        )
        output["evidence_ids"].update(cited & active.keys())
        output["cited_evidence_ids"].update(cited & evidence.keys())
        output["family_ids"].update(family_ids(row))

    for index, row in enumerate(
        data.get("global_tables", {}).get("T2_climate_risk", [])
    ):
        add_output("T2a", "", row, index)

    mappings: list[dict] = []
    for nbs, recipe in data.get("recipes", {}).items():
        for table, filename in (
            ("T4", "T4_suitability_mappings"),
            ("T3", "T3_nbs_hazard_farming"),
            ("T6", "T6_nbs_scorecard"),
        ):
            for index, row in enumerate(recipe.get(filename, [])):
                cited = set(_list(row.get("evidence_ids")))
                retained = cited & active.keys()
                unresolved_compiled.update(cited - evidence.keys())
                dropped_compiled.update(cited & (evidence.keys() - active.keys()))
                if table == "T4":
                    mappings.append(
                        {
                            "key": (nbs, row.get("mapping_id") or f"unkeyed:{index}"),
                            "nbs_id": row.get("nbs_id") or nbs,
                            "family_ids": family_ids(row),
                            "evidence_ids": retained,
                            "operational": (
                                row.get("suitability_dimension")
                                == "operational_constraint"
                                and str(row.get("is_scenario_candidate", "")).lower()
                                == "true"
                            ),
                        }
                    )
                operational = (
                    table == "T4"
                    and row.get("suitability_dimension") == "operational_constraint"
                    and str(row.get("is_scenario_candidate", "")).lower() == "true"
                )
                if not operational:
                    add_output(table, nbs, row, index)
                for eid in retained:
                    key = canonical.get(active[eid].get("source_id"))
                    if key in records:
                        records[key]["contributions"][table].add(eid)

    routes: dict[str, set[str]] = defaultdict(set)
    priorities = {
        r.get("variable_id")
        for r in data.get("global_tables", {}).get("T5_opportunity_space", [])
        if r.get("mcda_role") == "priority"
    }
    for row in registers.get("XW_target_crosswalk", []):
        # The legacy XW also routes economic cells to T6; the compiler publishes
        # those separately as T6E. Benefits use the schema's T5 priority targets.
        if (
            priorities
            and row.get("target_table") == "T6"
            and row.get("target_key") not in priorities
        ):
            continue
        routes[row.get("ev_variable", "")].add(row.get("target_table", ""))
    routed = bool(registers.get("XW_target_crosswalk"))
    scope_ids = {
        table: set().union(*(r["cited_evidence_ids"] for r in rows.values()))
        for table, rows in output_rows.items()
    }
    for eid, row in evidence.items():
        role = row.get("use_role", "")
        targets = tables_for(role, row.get("variable", ""), routes)
        if role == "climate_risk":
            targets.add("T2a")
        if not routed and role == "nbs_effect":
            targets.update({"T3", "T6"})
        for table in targets & scope_ids.keys():
            scope_ids[table].add(eid)

    def output_summary(table: str, nbs: str = "") -> dict:
        rows = [r for r in output_rows[table].values() if not nbs or r["nbs_id"] == nbs]
        ids = set().union(*(r["evidence_ids"] for r in rows))
        source_keys = {canonical.get(active[eid].get("source_id")) for eid in ids}
        source_keys.discard(None)
        return {
            "table_id": table,
            "label": table_specs[table][0],
            "unit": table_specs[table][1],
            "count_definition": "Distinct configured/compiled record IDs, including family, practice roll-up and context variants; not unique hazard or benefit dimensions. Counts do not certify review completion.",
            "output_count": len(rows),
            "evidence_backed_outputs": sum(bool(r["evidence_ids"]) for r in rows),
            "contributing_excerpts": len(ids),
            "contributing_sources": len(source_keys),
            "evidence_ids": sorted(ids),
            "source_keys": sorted(source_keys),
            "rows": [
                {
                    "id": r["id"],
                    "label": r["label"],
                    "nbs_id": r["nbs_id"],
                    "family_ids": sorted(r["family_ids"]),
                    "farming_system": r["farming_system"],
                    "scope_type": r["scope_type"],
                    "scope_id": r["scope_id"],
                    "risk_role": r["risk_role"],
                    "evidence_ids": sorted(r["evidence_ids"]),
                    "source_keys": sorted(
                        {
                            canonical[active[eid]["source_id"]]
                            for eid in r["evidence_ids"]
                            if active[eid].get("source_id") in canonical
                        }
                    ),
                }
                for r in rows
            ],
        }

    def metrics(nbs: str = "", fid: str = "", table: str = "") -> dict:
        def family_matches(ids: set[str]) -> bool:
            if fid == "__unassigned":
                return not any(
                    family_lookup.get(f, {}).get("nbs_id") == nbs for f in ids
                )
            return not fid or fid in ids

        def in_scope(row: dict) -> bool:
            return (not nbs or nbs in _list(row.get("nbs_id"))) and family_matches(
                family_ids(row)
            )

        selected_outputs = [
            r
            for t, rows in output_rows.items()
            if not table or t == table
            for r in rows.values()
            if not nbs or r["nbs_id"] == nbs
        ]
        cited_in_scope = set().union(
            *(r["cited_evidence_ids"] for r in selected_outputs)
        )
        selected_ev = {
            eid: row
            for eid, row in evidence.items()
            if (not table or eid in scope_ids[table])
            and (in_scope(row) or (bool(table) and not fid and eid in cited_in_scope))
        }

        selected = [
            r
            for r in records.values()
            if (not nbs or nbs in r["nbs_ids"])
            and (
                family_matches(r["family_ids"])
                or (
                    fid == "__unassigned"
                    and bool(
                        (r["evidence_ids"] | r["dropped_evidence_ids"])
                        & selected_ev.keys()
                    )
                )
            )
        ]
        if table:
            source_keys = {
                canonical.get(r.get("source_id")) for r in selected_ev.values()
            }
            selected = [r for r in records.values() if r["key"] in source_keys]
        live_ids = selected_ev.keys() & active.keys()
        approved_ids = {eid for eid in live_ids if _approved(active[eid])}
        reviewed_ids = selected_ev.keys() & assessed_ids
        dropped_ids = selected_ev.keys() - active.keys()
        reviewed_dropped_ids = reviewed_ids & dropped_ids
        sources_with_review = {
            r["key"] for r in selected if r["reviewed_evidence_ids"] & reviewed_ids
        }
        extracted, reviewed, fully_reviewed = set(), set(), set()
        for record in selected:
            ids = record["evidence_ids"] & live_ids
            if ids:
                extracted.add(record["key"])
                if ids & approved_ids:
                    reviewed.add(record["key"])
                if ids <= approved_ids:
                    fully_reviewed.add(record["key"])
        t4 = [
            r
            for r in mappings
            if (not nbs or r["nbs_id"] == nbs) and family_matches(r["family_ids"])
        ]
        if table:
            t4 = [r for r in t4 if table == "T4" and not r["operational"]]
        contribution_ids = (
            set().union(*(r["evidence_ids"] for r in selected_outputs)) & live_ids
        )
        contribution_sources = {
            canonical.get(active[eid].get("source_id")) for eid in contribution_ids
        }
        contribution_sources.discard(None)
        t4_ids = set().union(*(r["evidence_ids"] for r in t4))
        t4_sources = {canonical.get(active[eid].get("source_id")) for eid in t4_ids}
        t4_sources.discard(None)
        scoped_searches = [
            e
            for e in (
                _searches(
                    [
                        r
                        for r in registers.get("SRCH_search_register", [])
                        if r.get("table")
                        in ({"T2", "T2a"} if table == "T2a" else {table})
                    ]
                )
                if table
                else searches
            )
            if (not nbs or e.get("nbs_id") == nbs) and family_matches(family_ids(e))
        ]
        return {
            "compiled_outputs": sum(
                family_matches(r["family_ids"]) for r in selected_outputs
            ),
            "evidence_ids": sorted(selected_ev),
            "contributing_excerpts": len(contribution_ids),
            "contributing_sources": len(contribution_sources),
            "known_sources": len(selected),
            "source_keys": sorted(r["key"] for r in selected),
            "extracted_sources": len(extracted),
            "reviewed_sources": len(reviewed),
            "fully_reviewed_sources": len(fully_reviewed),
            "sources_with_reviewed_excerpts": len(sources_with_review),
            "sources_with_approved_excerpts": len(reviewed),
            "active_excerpts": len(live_ids),
            "retained_excerpts": len(live_ids),
            "all_excerpts": len(selected_ev),
            "reviewed_excerpts": len(reviewed_ids),
            "unreviewed_excerpts": len(selected_ev.keys() - reviewed_ids),
            "reviewed_pct": (
                round(100 * len(reviewed_ids) / len(selected_ev), 1)
                if selected_ev
                else None
            ),
            "approved_excerpts": len(approved_ids),
            "approved_pct": (
                round(100 * len(approved_ids) / len(reviewed_ids), 1)
                if reviewed_ids
                else None
            ),
            "reviewed_active_excerpts": len(reviewed_ids & live_ids),
            "reviewed_dropped_excerpts": len(reviewed_dropped_ids),
            "reviewed_unresolved_excerpts": len(
                reviewed_ids - approved_ids - dropped_ids
            ),
            "dropped_excerpts": len(dropped_ids),
            "t4_relationships": len({r["key"] for r in t4}),
            "t4_operational_relationships": len(
                {r["key"] for r in t4 if r["operational"]}
            ),
            "t4_structural_relationships": len(
                {r["key"] for r in t4 if not r["operational"]}
            ),
            "t4_evidence_backed_relationships": len(
                {r["key"] for r in t4 if r["evidence_ids"]}
            ),
            "t4_contributing_sources": len(t4_sources),
            "source_mix": {
                kind: sum(r["type"] == kind for r in selected)
                for kind in ("literature", "grey", "tools", "unknown")
            },
            "search_metrics": _search_metrics(scoped_searches),
        }

    nbs_ids = set(data.get("recipes", {}))
    for record in records.values():
        nbs_ids.update(record["nbs_ids"])
    nbs_ids.update(f["nbs_id"] for f in family_lookup.values())
    nbs_ids.update(e.get("nbs_id", "") for e in searches)
    # Evidence routing tags absent from FAM remain inspectable, not silently dropped.
    for row in evidence.values():
        for fid in family_ids(row):
            family_lookup.setdefault(
                fid,
                {
                    "family_id": fid,
                    "nbs_id": row.get("nbs_id", ""),
                    "name": fid.split("__")[-1].replace("_", " ").capitalize(),
                    "navigation_group": "evidence",
                    "subpractices": [],
                    "scope_kind": "unmapped",
                    "scope_definition": "Recorded evidence routing tag absent from the family registry.",
                },
            )
    practices: list[dict] = []
    for nbs in sorted(nbs_ids - {""}):
        practice = {
            "nbs_id": nbs,
            "name": nbs.replace("_", " ").capitalize(),
            "metrics": metrics(nbs),
            "families": [],
            "outputs": [output_summary(t, nbs) for t in table_specs if t != "T2a"],
        }
        for fid, family in sorted(family_lookup.items()):
            if family["nbs_id"] == nbs:
                practice["families"].append({**family, "metrics": metrics(nbs, fid)})
        practice["families"].append(
            {
                "family_id": "__unassigned",
                "nbs_id": nbs,
                "name": "Family not recorded",
                "navigation_group": "evidence",
                "subpractices": [],
                "scope_kind": "unassigned",
                "scope_definition": "No matching family association is recorded for these source or evidence records; this does not mean applicable to all families.",
                "metrics": metrics(nbs, "__unassigned"),
            }
        )
        practices.append(practice)

    table_views = {}
    for table, (label, _unit) in table_specs.items():
        note = {
            "T2a": "Shared T2 climate-risk configuration, displayed as T2a; not M2b investment-risk screening. Evidence includes explicit climate-risk roles and configuration citations. Other upstream allocation is not recorded; zero tracked extracts does not mean no research was done.",
            "T3": (
                "Evidence relevant to hazard response, plus claims already cited by T3 outputs. Relevance does not establish suitability for use. T3 and T6 can share extracts; totals must not be added."
                if routed
                else "Shared T3/T6 effect-evidence pool, plus T3 asset-vulnerability evidence and explicit T3 citations. Upstream allocation is unavailable; this is not a T3-only extraction count."
            ),
            "T4": "Structural-suitability evidence plus explicit citations in core T4 rules. Soft operational scenario rows are excluded; hard legal masks remain included.",
            "T6": (
                "Evidence relevant to benefits, plus claims already cited by T6 outputs. Relevance does not establish suitability for use. T3 and T6 can share extracts; totals must not be added. Output counts exclude economic profiles (T6E)."
                if routed
                else "Shared T3/T6 effect-evidence pool plus explicit T6 citations. Upstream allocation is unavailable; this is not a T6-only extraction count. Output counts exclude economic profiles (T6E)."
            ),
        }[table]
        scoped_practices = []
        if table != "T2a":
            for practice in practices:
                nbs = practice["nbs_id"]
                scoped_practices.append(
                    {
                        **practice,
                        "metrics": metrics(nbs, table=table),
                        "families": [
                            {**f, "metrics": metrics(nbs, f["family_id"], table)}
                            for f in practice["families"]
                        ],
                        "outputs": [output_summary(table, nbs)],
                    }
                )
        table_views[table] = {
            "table_id": table,
            "label": label,
            "scope_note": note,
            "project_level": table == "T2a",
            "evidence_tracking": "role_and_citations"
            if table == "T2a"
            else ("routed" if routed or table == "T4" else "shared_effect_pool"),
            "totals": metrics(table=table),
            "practices": scoped_practices,
            "outputs": [output_summary(table)],
        }

    def serial(value: Any) -> Any:
        if isinstance(value, set):
            return sorted(value)
        if isinstance(value, dict):
            return {k: serial(v) for k, v in value.items()}
        if isinstance(value, list):
            return [serial(v) for v in value]
        return value

    return {
        "sources": serial([records[k] for k in sorted(records)]),
        "searches": searches,
        "totals": metrics(),
        "practices": practices,
        "table_views": table_views,
        "outputs": [output_summary(t) for t in table_specs],
        "diagnostics": {
            "compiled_missing_evidence_ids": sorted(unresolved_compiled),
            "compiled_dropped_evidence_ids": sorted(dropped_compiled),
            "uncatalogued_evidence_sources": sorted(
                {
                    r.get("source_id", "")
                    for r in evidence.values()
                    if r.get("source_id") not in canonical
                }
            ),
        },
        "definitions": {
            "known_sources": "Known source records; explicit duplicate aliases merged. Unmarked publication duplicates may remain. Legacy unmatched resources excluded.",
            "searches": "Shared retrieval identity uses run, practice, family, category, date, query and limits. Shared retrievals counted once; table-specific screening variants not aggregated. Search observations overlap and are not unique publications. Conflicts exclude only the affected count field.",
            "screened_pct": "Screened / retrieved observations for matched complete, ordered numeric search records only; not unique-source screening coverage.",
            "screening": "Per-source screening decisions and discovery-parent links are not recorded; no source-level screening percentage is inferred.",
            "reviewed_excerpts": "Distinct claims with a recorded Keep/OK, Drop, Query, Reclassify or Retag decision, or an explicit reviewer_ok approval. Includes human and automated decisions, quarantined claims and previously reviewed claims reopened for another decision. Mere flags and reopen events do not establish an assessment. This measures recorded review work, not completed review.",
            "reviewed_pct": "Reviewed claims divided by all extracted claims, including quarantined claims. Missing review history is not inferred from a quarantine status.",
            "approved_pct": "Currently approved retained claims divided by claims with a recorded review decision or explicit approval; not the percentage reviewed.",
            "reviewed_unresolved_excerpts": "Previously assessed retained claims without current approval, including queries and reopened claims. They may still need a decision.",
            "sources_with_reviewed_excerpts": "Sources with at least one claim with a recorded assessment or explicit approval in the displayed scope, including quarantined claims; not whole-paper reviews.",
            "sources_with_approved_excerpts": "Sources with at least one retained excerpt currently approved; not whole-paper reviews.",
            "reviewed_sources": "Legacy compatibility field: sources with at least one retained excerpt currently approved; use sources_with_reviewed_excerpts for recorded assessment work.",
            "fully_reviewed_sources": "Sources with a nonempty retained excerpt set, all approved in the displayed scope.",
            "extraction_counts": "Mutually exclusive retained excerpt role buckets: T4 structural suitability; effects nbs_effect; M2b operational_risk/asset_vulnerability; other remaining roles. These do not claim compilation into T3/T6.",
            "t4_operational_relationships": "Soft operational rows marked operational_constraint and is_scenario_candidate=true. Hard operational masks remain core suitability relationships.",
            "compiled_outputs": "Distinct configured or compiled output records in the displayed table, practice and explicit family scope, keyed by table, practice and record ID. Includes records without retained citations and family/roll-up/context variants; not unique analytical dimensions or evidence-backed outputs. Shared T2a configuration is project-level; T4 soft operational rows and T6E economics are excluded.",
            "contributing_excerpts": "Distinct retained excerpts explicitly cited in displayed compiled/configured outputs, intersected with the displayed evidence scope; not inferred from extraction roles. T4 excludes soft operational scenario rows. T6 excludes T6E economics.",
            "contributions": "T4/T3/T6 cite retained excerpts in compiled rows. M2b counts role-based operational-risk or asset-vulnerability excerpts, not compiled outputs. Categories overlap. T6 excludes T6E economics.",
            "families": "Direct source/evidence family associations only. Generic evidence is not copied into every family; family sums need not equal grand totals.",
            "t4_relationships": "Distinct mapping records, not necessarily approved or evidence-backed. Evidence-backed records cite at least one retained excerpt.",
        },
    }
