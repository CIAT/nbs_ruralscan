"""Read-only scope-review inventory; does not modify registers or claim review progress."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NBS = "water_harvesting_conservation"


def rows(path):
    with (ROOT / path).open(newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    paths = {
        "fam": "schema/registers/FAM_family_registry.csv",
        "ev": "schema/registers/EV_evidence_register.csv",
        "t4": f"schema/recipes/{NBS}/T4_suitability_mappings.csv",
        "inventory": "methodology/audits/wh_five_extraction_20261104/criterion_inventory.json",
    }
    fam = [r for r in rows(paths["fam"]) if r["nbs_id"] == NBS]
    ev = [r for r in rows(paths["ev"]) if r["nbs_id"] == NBS]
    t4 = rows(paths["t4"])
    crosswalk = rows(str((OUT / "subpractice_crosswalk.csv").relative_to(ROOT)))
    assert Counter(r["subpractice_id"] for r in fam) == Counter(r["subpractice_id"] for r in crosswalk)
    family_ids = {r["suitability_family_id"] for r in fam}
    assert {r["suitability_family_id"] for r in ev} <= family_ids
    assert {r["suitability_family_id"] for r in t4} <= family_ids
    by_id = {r["subpractice_id"]: r for r in fam}
    for r in crosswalk:
        assert r["current_family"] == by_id[r["subpractice_id"]]["suitability_family_id"]
        assert r["current_spatial_product"] == by_id[r["subpractice_id"]]["spatial_product_type"]
    summary = []
    for family in sorted(family_ids):
        all_units = [r for r in ev if r["suitability_family_id"] == family]
        active = [r for r in all_units if r["review_state"] != "dropped"]
        structural = [r for r in active if r["use_role"] == "structural_suitability"]
        summary.append({
            "family": family,
            "subpractice_records": sum(r["suitability_family_id"] == family for r in fam),
            "all_ev": len(all_units), "dropped_ev": len(all_units) - len(active),
            "non_dropped_ev": len(active),
            "non_dropped_roles": dict(sorted(Counter(r["use_role"] for r in active).items())),
            "non_dropped_t4_ev": len(structural),
            "reviewer_ok_t4_ev": sum(r["reviewer_ok"].lower() == "true" for r in structural),
            "existing_t4_mapping_rows": sum(r["suitability_family_id"] == family for r in t4),
        })
    inventory = json.loads((ROOT / paths["inventory"]).read_text())
    held = [r for r in inventory if r["disposition"] == "held_or_deferred"]
    assert len(held) == 15
    batch = [r for r in ev if r["evidence_id"].startswith("ev_wh5_")]
    assert len(batch) == 53
    assert all(r["reviewer_ok"].lower() == "false" for r in batch)
    assert all(r["review_state"] != "dropped" for r in batch)
    data = {
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "input_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths.values()},
        "definitions": {
            "non_dropped": "review_state != dropped; does not mean approved or project-in-scope",
            "t4_ev": "use_role = structural_suitability; includes all claim scopes",
            "existing_t4_mapping_rows": "CSV row count, not approved/executable functions or independent studies",
            "subpractice_records": "Includes broad macrocatchment umbrella and cross-family metadata tag; not a target-practice count",
        },
        "families": summary,
        "five_source_batch": {"units": len(batch), "unapproved": len(batch), "held_criterion_groups": len(held)},
        "checks": {"all_fam_rows_covered_once": True, "current_family_and_footprint_match": True,
                   "all_evidence_and_mapping_families_accounted_for": True, "no_registers_modified": True},
    }
    (OUT / "snapshot.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({"families": len(summary), "crosswalk_rows": len(crosswalk), "batch_units": len(batch), "holds": len(held)}))


if __name__ == "__main__":
    main()
