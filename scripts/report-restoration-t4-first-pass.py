#!/usr/bin/env python3
"""Reproduce bounded restoration T4 counts, raw source profiles and input requirements.

No source ranking, human approval, score, weight or complete denominator is inferred.
"""

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    evidence = read("schema/registers/EV_evidence_register.csv")
    sources = {
        r["source_id"]: r for r in read("schema/registers/SRC_source_register.csv")
    }
    ontology = {
        r["canonical_variable_id"]: r
        for r in read("schema/registers/VONT_variable_ontology.csv")
    }
    bindings = read("schema/registers/BIND_dataset_binding.csv")
    for nbs in ("forest_restoration", "mangrove_restoration"):
        dest = ROOT / "pipeline/t4_audit" / nbs / "first_pass_2026-10-28"
        dest.mkdir(parents=True, exist_ok=True)
        units = [
            u
            for u in evidence
            if u["nbs_id"] == nbs
            and u["use_role"] in {"structural_suitability", "operational_risk"}
        ]
        active = [u for u in units if u["review_state"] != "dropped"]
        groups = defaultdict(list)
        for u in active:
            groups[
                (
                    u["suitability_family_id"],
                    u["use_role"],
                    u["claim_scope"],
                    u["variable"],
                )
            ].append(u)
        coverage, requirements, profiles = [], [], []
        for (family, role, scope, variable), members in sorted(groups.items()):

            def paper(u):
                source = sources[u["source_id"]]
                return source.get("doi", "").lower() or u["source_id"]

            uses = [
                u
                for u in members
                if json.loads(u["context"] or "{}").get("model_use", {}).get("used")
                is True
            ]
            directions = [
                u
                for u in members
                if json.loads(u["relationship"] or "{}").get("direction")
                in {"increasing", "decreasing", "optimum_range", "non_monotonic"}
            ]
            reviewed = [u for u in members if u["reviewer_ok"].lower() == "true"]
            coverage.append(
                dict(
                    family=family,
                    role=role,
                    claim_scope=scope,
                    variable=variable,
                    group=ontology.get(variable, {}).get("group_id", ""),
                    recorded_sources=len({paper(u) for u in members}),
                    explicit_variable_use_n=len({paper(u) for u in uses}),
                    direction_n=len({paper(u) for u in directions}),
                    approved_sources=len({paper(u) for u in reviewed}),
                    approved_calibrated_contributors=0,
                    screened_N="",
                    raw_support_pct="",
                    quality_weighted_support_pct="",
                    source_ids="|".join(sorted({u["source_id"] for u in members})),
                    evidence_ids="|".join(u["evidence_id"] for u in members),
                    basis="Recorded reporting-paper counts only; incomplete model-use capture and unresolved lineage/contexts prevent independent agreement claims",
                )
            )
            vont = ontology.get(variable, {})
            matches = [
                b
                for b in bindings
                if b.get("variable_id", b.get("variable", "")) == variable
            ]
            requirements.append(
                dict(
                    family=family,
                    role=role,
                    variable=variable,
                    canonical_unit=vont.get("canonical_unit", ""),
                    candidate_dataset_ids=vont.get("candidate_dataset_ids", ""),
                    min_meaningful_resolution_m=vont.get(
                        "min_meaningful_resolution_m", ""
                    ),
                    binding_candidates=json.dumps(matches, sort_keys=True),
                    status="Candidate inputs only; no response or dataset transfer selected",
                    special_requirement=(
                        "Local tidal vertical reference, flooding duration/frequency and spatial support must match; terrestrial elevation/forest proximity not equivalent"
                        if nbs == "mangrove_restoration"
                        and variable
                        in {
                            "elevation",
                            "tidal_inundation_duration",
                            "distance_to_forest",
                        }
                        else "Site history and native non-forest safeguards required before land eligibility"
                        if variable in {"land_cover", "tree_canopy_cover"}
                        else "Confirm quantity, units, period, scale and applicability before binding"
                    ),
                )
            )
        for u in units:
            profiles.append(
                {
                    k: u[k]
                    for k in (
                        "evidence_id",
                        "source_id",
                        "suitability_family_id",
                        "variable",
                        "use_role",
                        "claim_scope",
                        "reviewer_ok",
                        "review_state",
                        "relationship",
                        "context",
                        "page",
                        "lineage_of",
                    )
                }
            )
        # No approved numeric contributors currently: fail rather than publish a stale zero.
        recipe = read(f"schema/recipes/{nbs}/T4_suitability_mappings.csv")
        if recipe:
            raise ValueError(
                "First-pass zero-calibration report must be upgraded after recipe approval"
            )
        for filename, rows in [
            ("coverage.csv", coverage),
            ("dataset_requirements.csv", requirements),
            ("source_profiles.csv", profiles),
        ]:
            write(dest / filename, rows, list(rows[0]))
        summary = dict(
            nbs=nbs,
            records=len(units),
            active=len(active),
            approved=sum(u["reviewer_ok"].lower() == "true" for u in active),
            source_count=len({u["source_id"] for u in active}),
            calibrated_functions=0,
            screened_N=None,
            quality_weighted_support=None,
            aggregation=None,
            runtime_weights=None,
            snapshot_sha256=hashlib.sha256(
                json.dumps(units, sort_keys=True).encode()
            ).hexdigest(),
        )
        (dest / "current_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(nbs, summary)


if __name__ == "__main__":
    main()
