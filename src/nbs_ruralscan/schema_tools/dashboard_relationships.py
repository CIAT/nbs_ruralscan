"""Live dashboard relationships, derived read-only from the canonical T4 builders.

The aggregate is the developer-v0.1.7 presentation. Historical packages are not
inputs: every build uses current registers and independently verifies recipe parity.
"""

from pathlib import Path

from nbs_ruralscan.recipe.aggregate_evidence import aggregate
from nbs_ruralscan.recipe.developer_contract import build_contract
from nbs_ruralscan.recipe.relationship_catalogue import build_catalogue


def build_relationships(data: dict, root: Path) -> dict:
    registers = data.get("registers", {})
    evidence = registers.get("EV_evidence_register", [])
    ontology = {
        row["canonical_variable_id"]: row
        for row in registers.get("VONT_variable_ontology", [])
    }
    practices = {}
    for nbs, recipe in sorted(data.get("recipes", {}).items()):
        mappings = recipe.get("T4_suitability_mappings", [])
        members = [row for row in evidence if row.get("nbs_id") == nbs]
        if not mappings and not any(
            row.get("use_role") == "structural_suitability" for row in members
        ):
            continue
        catalogue = build_catalogue(members, [], mappings)
        entry = {
            "catalogue": catalogue,
            "aggregate": None,
            "aggregate_status": "unavailable",
            "aggregate_note": "Source claims remain available. The current recipe has not passed the aggregate rebuild check.",
        }
        if (root / "schema/recipes" / nbs / "T4_suitability_mappings.csv").exists():
            try:
                result = build_contract(root, nbs=nbs)
            except ValueError as error:
                # A stale audited recipe must never acquire an apparently current
                # aggregate by silently reusing an old handoff snapshot.
                entry["rebuild_detail"] = str(error)
            else:
                catalogue = build_catalogue(
                    result["evidence"],
                    result["synthesis_report"]["evidence_dispositions"],
                    mappings,
                )
                entry.update(
                    catalogue=catalogue,
                    aggregate=aggregate(
                        catalogue,
                        result["inclusion"],
                        result["importance"],
                        result["contract"]["rows"],
                        ontology,
                    ),
                    aggregate_status="current",
                    aggregate_note="Rebuilt from current registers; the audited T4 recipe matches the canonical compiler.",
                )
        practices[nbs] = entry
    return {"presentation_version": "developer-v0.1.7", "practices": practices}
