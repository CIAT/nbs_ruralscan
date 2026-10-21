"""Build a grouped, local-feedback T4 review surface; never writes review decisions."""

from pathlib import Path
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "pipeline/t4_audit/agroforestry/bounded_review_2026-10-21"
LABELS = {
    "annual_precipitation": "Annual rainfall",
    "mean_annual_temperature": "Temperature",
    "soil_ph": "Soil pH",
    "soil_ph_subsoil": "Subsoil pH",
    "ndvi": "Vegetation greenness (NDVI)",
    "evapotranspiration_ref": "Reference evapotranspiration",
    "soil_cation_exchange_capacity": "Soil nutrient-holding capacity (CEC)",
    "soil_available_water_capacity": "Plant-available soil water",
    "soil_organic_carbon_subsoil": "Subsoil organic carbon",
    "soil_depth": "Depth to bedrock",
}
PROPOSALS = {
    "slope": (
        "Keep each paper’s slope classes within its stated crop and region. Treat values outside the reported range as unknown.",
        "Nath stops at 44°; the existing extension above that needs correction. WOCAT slopes describe observed sites, not suitability limits.",
    ),
    "soil_ph": (
        "Keep topsoil and subsoil results distinct. Retain all reported classes; hold contradictory cutoffs and unresolved weight totals.",
        "Haile pH classes conflict. Nath repeats pH in nutrient and rooting branches. Species-selection criteria do not establish a universal pH range.",
    ),
    "ndvi": (
        "Replace the mistaken canopy-cover interpretation with vegetation greenness (NDVI).",
        "NDVI measures vegetation greenness; it is not percentage tree cover. Existing approved record needs a traceable correction.",
    ),
    "land_cover": (
        "Keep named land-use classes with their original study scope. Count Chuma’s use of land cover, but do not invent missing classes.",
        "Ahmad exclusions remain in the source inventory pending exact claim-specific provenance. Tea remains your explicit design choice, not evidence from the coffee/cocoa paper.",
    ),
    "elevation": (
        "Retain regional elevation classes. Show both Haile weight sets without choosing one.",
        "Haile Table 3 gives 8%; Table 5 gives 6.5%. Source data alone do not resolve which should govern.",
    ),
    "evapotranspiration_ref": (
        "Keep the reported direction and classes, but hold numeric application until units are resolved.",
        "Nath labels values mm/day, but their magnitude looks annual. We must not silently change units.",
    ),
    "soil_texture": (
        "Retain named textures and source codes; translate to dataset classes only after checking each codebook.",
        "Numbers such as 5, 7 and 9 are category codes, not increasing amounts of texture. Topsoil and subsoil remain separate.",
    ),
    "soil_cation_exchange_capacity": (
        "Retain the source classes as evidence; hold executable cutoffs.",
        "Nath’s classes overlap and its printed unit needs clarification.",
    ),
    "soil_organic_carbon_subsoil": (
        "Keep subsoil carbon separate from topsoil; hold the apparent source range typo.",
        "Nath prints a range “2 to 1.03”. Preserve the source rather than guessing its correction.",
    ),
}


def build_data(root=ROOT):
    audit = root / "pipeline/t4_audit/agroforestry/bounded_review_2026-10-21"
    manifest = json.loads((audit / "manifest.json").read_text())
    evidence = {
        r["evidence_id"]: r
        for r in csv.DictReader(
            (root / "schema/registers/EV_evidence_register.csv").open()
        )
    }
    groups = {}
    for eid in manifest["new_evidence_ids"]:
        r = evidence[eid]
        key = "soil_ph" if r["variable"] == "soil_ph_subsoil" else r["variable"]
        proposal, issue = PROPOSALS.get(
            key,
            (
                "Retain the paper’s evidence with its stated scope. Combine only compatible systems, units and contexts.",
                "A variable used to select tree species does not automatically define a general agroforestry limit. Source weights remain specific to each paper.",
            ),
        )
        group = groups.setdefault(
            key,
            {
                "id": key,
                "label": LABELS.get(key, key.replace("_", " ").capitalize()),
                "proposal": proposal,
                "issue": issue,
                "records": [],
            },
        )
        c = json.loads(r["context"] or "{}")
        group["records"].append(
            {
                "id": eid,
                "source": r["source_id"],
                "variable": r["variable"],
                "label": LABELS.get(
                    r["variable"], r["variable"].replace("_", " ").capitalize()
                ),
                "page": r["page"],
                "quote": r["quote"],
                "header": r.get("justification_quote", ""),
                "header_page": r.get("justification_page", ""),
                "relationship": json.loads(r["relationship"] or "{}"),
                "scope": c.get("t4_assessment", {}).get("scope", r["claim_scope"]),
                "branch": c.get("branch", ""),
                "issue": c.get("calibration_hold") or c.get("review_needed", ""),
                "weights": c.get("model_use", {}),
                "image": c.get("direction_provenance", {}).get("image", ""),
                "image_page": c.get("direction_provenance", {}).get("page"),
                "state": r["review_state"],
                "role": r["use_role"],
            }
        )
    order = [
        "slope",
        "soil_ph",
        "ndvi",
        "annual_precipitation",
        "mean_annual_temperature",
        "land_cover",
        "elevation",
    ]
    result = sorted(
        groups.values(),
        key=lambda g: (order.index(g["id"]) if g["id"] in order else 99, g["label"]),
    )
    for g in result:
        # Binding feedback to the exact shown evidence and proposal prevents silent reuse after regeneration.
        g["fingerprint"] = hashlib.sha256(
            json.dumps(g, sort_keys=True).encode()
        ).hexdigest()
    sources = {
        r["source_id"]: r
        for r in csv.DictReader(
            (root / "schema/registers/SRC_source_register.csv").open()
        )
    }
    # Display-only source images must not invalidate feedback on unchanged claims.
    for group in result:
        for record in group["records"]:
            raw = evidence[record["id"]]
            record["source_row"] = raw.get("raw_name") or record["label"]
            record["citation"] = sources[record["source"]].get(
                "citation", record["source"]
            )
            record["source_url"] = sources[record["source"]].get("url", "")
            pages = {}
            for value, purpose in [
                (record["page"], "Claim"),
                (record["header_page"], "Table heading"),
                (record["weights"].get("page"), "Weight / method"),
                (record["image_page"], "Direction table"),
            ]:
                for token in re.findall(r"\d+", str(value or "")):
                    number = int(token)
                    if number > 0:
                        pages.setdefault(number, []).append(purpose)
            record["source_pages"] = [
                {
                    "page": number,
                    "purpose": ", ".join(purposes),
                    "image": f"/review/source-pages/{record['source']}-p{number}.png",
                }
                for number, purposes in sorted(pages.items())
            ]
    return {
        "version": 1,
        "review_id": "agroforestry-t4-bounded-2026-10-21",
        "groups": result,
        "source_count": len(manifest["sources"]),
        "record_count": len(manifest["new_evidence_ids"]),
    }


def main():
    data = build_data()
    template = (ROOT / "scripts/templates/t4-feedback.html").read_text()
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    (ROOT / "docs/review/t4-bounded-review.html").write_text(
        template.replace("__REVIEW_DATA__", payload)
    )
    print(
        f"Built {len(data['groups'])} variable groups covering {data['record_count']} records"
    )


if __name__ == "__main__":
    main()
