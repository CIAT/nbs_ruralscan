"""Reproduce the bounded 83-claim inventory from the v0.1.6 package."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PACKAGE = ROOT / "handoff/agroforestry-t4/developer-v0.1.6"

# Review cautions from the stored quote/context; not new source extraction or decisions.
CAUTIONS = {
    "ev_t4_mat_yadav24_7": "Species-distribution importance discussion; not practice-level temperature direction. Scope/attribution review before any promotion.",
    "EV_ijbcs_rna_mali_2020_007": "Fertilizer use predicts adoption; not soil-fertility suitability. Route review to operational/adoption lane; do not make T4 response.",
    "EV_weston_2015_002": "950 mm is the Ghana study site's rainfall, not an FMNR envelope.",
    "EV_fao_anr_2019_002": "Fertilizer response of seedlings; context says forest restoration. Practice/role check, not a general AF soil-fertility gate.",
    "ev_production_gap_saraheb3_tool": "Tool economic-viability design criterion; separate opportunity priority from ecological establishment.",
    "ev_tree_canopy_cover_sprenkle24_1": "25% is an accounting convention; no biological eligibility threshold.",
    "ev_tree_canopy_cover_sprenkle24_2": "Expert target canopy, not baseline canopy eligibility. Preserve uncertainty and system context.",
    "ev_T4_slope_haris2021_3": "Land-capability description, explicitly not an agroforestry numeric rule.",
    "ev_t4_pa_mucida23_1": "Local legal exclusion; require target legal rules and coverage. No global protected-area mask inferred.",
    "ev_operational_risk_built_up_areas_baldwin_2022_full": "Project-specific buffers and parcel exclusions; no universal legal mask or numeric transfer.",
    "ev_T4_land_cover_chuma21_1": "Model input retained; class scores explicitly not extracted. No class/gate inferred.",
    "EV_chomba_2020_003": "Observed occurrence on nutrient-poor soils; not a calibrated fertility response.",
    "ev_t4_mat_castle2025_1": "Stored definition uses days under temperature variable; verify measurement identity before mapping.",
    "ev_T4_rereview_nath_2021_soil_cation_exchange_capacity_3": "Source class ranges overlap; direction explicitly unclear. Retain classes without repairing them.",
    "ev_T4_rereview_nath_2021_soil_available_water_capacity_10": "Source ranks/codes are not physical water-capacity units; direction unclear; codebook required.",
    "ev_T4_rereview_nath_2021_soil_texture_6": "Numeric texture codes require source codebook; do not interpret them as continuous texture values.",
    "ev_T4_rereview_chuma_2021_aspect_1": "Retain source label Dish; categorical aspect requires interpretation/codebook, not continuous ordering.",
}


def main():
    catalogue = json.loads((PACKAGE / "relationship_catalogue.json").read_text())
    records = catalogue["records"]
    selected = [r for r in records if r["focus_review"]]
    assert len(records) == 184 and len(selected) == 83
    assert catalogue["summary"]["explicitly_linked_claims"] == 21
    rows = []
    for r in selected:
        peers = [x["evidence_id"] for x in records if x["evidence_id"] != r["evidence_id"]
                 and x["source_id"] == r["source_id"] and x["variable"] == r["variable"]]
        caution = CAUTIONS.get(r["evidence_id"], "")
        if r["variable"] == "rootstock_presence":
            caution = "Preserve regeneration prerequisite; locked routing places rootstock enabling evidence outside core T4. Flag role for human review; no silent retag."
        if not caution:
            caution = ("Retain stated relationship/classes; confirm units, source context, codebook and endpoint semantics before any compilation."
                       if r["has_stated_direction"] or r["has_source_classes"] or r["source_shape"]
                       else "Retain stored evidence; inspect quote/context for model use versus observed context. Missing encoded direction stays unknown.")
        rows.append({"evidence_id": r["evidence_id"], "source_id": r["source_id"],
                     "variable": r["variable"], "family": r["suitability_family_id"],
                     "compiler_disposition": r["compilation_disposition"],
                     "source_direction": r["source_direction"], "source_shape": r["source_shape"],
                     "relationship": r["relationship"], "reviewer_ok": r["reviewer_ok"],
                     "source_page": r["page"], "same_source_variable_records": json.dumps(peers),
                     "review_caution": caution,
                     "action_taken": "Visible in source relationship catalogue; no register/rule/approval change"})
    with (HERE / "83_claim_inventory.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (HERE / "summary.json").write_text(json.dumps(catalogue["summary"], indent=2) + "\n")
    print(catalogue["summary"])


if __name__ == "__main__":
    main()
