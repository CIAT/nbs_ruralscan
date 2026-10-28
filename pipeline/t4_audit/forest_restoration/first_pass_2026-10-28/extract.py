# ruff: noqa: E402
"""Deterministic bounded recovery from three existing cached sources; staging only.
Run: uv run python pipeline/staging/forest_t4_20261028/extract.py
No registrations, approvals, schema edits, discovery or progress stamps.
"""

from pathlib import Path
import csv
import json
import sys
import hashlib

ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)
OUT = ROOT / "pipeline/staging/forest_t4_20261028"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.ingest.pdf import build_index
from nbs_ruralscan.ingest.integrity import identity_error, pdf_title_error
from nbs_ruralscan.recipe.evidence import (
    EvidenceUnit,
    package_for_extraction_multi,
    validate_units,
    save_units,
)

CACHE = ROOT / ".cache/corpus"
SIDS = [
    "fr_zomer_cdm_afforestation_suit_2008",
    "fr_semiarid_reforestation_spatial_planning_2026",
    "optimizing_afforestation_reforestation_degraded_2024",
]
queue = {
    r["source_id"]: r
    for r in csv.DictReader((ROOT / "pipeline/acquisition_queue.csv").open())
}
src = {
    r["source_id"]: r
    for r in csv.DictReader((ROOT / "schema/registers/SRC_source_register.csv").open())
}


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


indexes = {}
manifest = []
tables = []
captions = []
variables = [
    {"variable": v, "aliases": a}
    for v, a in [
        ("land_cover", ["land cover", "tundra", "agricultural", "non-vegetated"]),
        ("aridity_index", ["aridity"]),
        ("elevation", ["elevation", "timberline"]),
        ("slope", ["slope", "75%"]),
        ("tenure_security", ["tenure"]),
        ("tree_canopy_cover", ["canopy"]),
        ("mean_annual_temperature", ["temperature"]),
        ("soil_depth", ["soil", "depth"]),
        ("distance_to_road", ["road"]),
        ("market_value_chain", ["markets"]),
    ]
]
for sid in SIDS:
    p = CACHE / (sid + ".pdf")
    assert identity_error(queue[sid]) is None
    assert pdf_title_error(p, src[sid]["citation"]) is None
    assert src[sid]["library_path"]
    idx = build_index(p, source_id=sid, with_tables=True)
    indexes[sid] = idx
    bundle = package_for_extraction_multi(
        idx,
        variables,
        force=True,
        full_tables=True,
        max_passages_per_var=100,
        min_score=0,
    )
    dump(sid + "_passages.json", bundle)
    manifest.append(
        {
            "source_id": sid,
            "pdf_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "pdf_sha1": hashlib.sha1(p.read_bytes()).hexdigest(),
            "cache_path": str(p),
            "library_path": src[sid]["library_path"],
            "metadata_verified": True,
            "opening_title_match": True,
            "pages": idx.n_pages,
            "tables_extracted": idx.tables_extracted,
            "needs_ocr_pages": idx.needs_ocr_pages,
            "index_table_count": len(idx.tables),
        }
    )
    for tab in idx.tables:
        for n, row in enumerate(tab.rows):
            tables.append(
                {
                    "source_id": sid,
                    "page": tab.page,
                    "table_label": tab.label,
                    "caption": tab.caption,
                    "row_index": n,
                    "cells": row,
                    "status": "machine-inventoried; disposition in inspected_source_inventory.json; extraction text layout not presumed faithful",
                }
            )
    for c in idx.captions:
        captions.append(
            {
                "source_id": sid,
                **c.__dict__,
                "status": "caption detected; no numeric graphical calibration inferred",
            }
        )


def sl(sid, page, start, end):
    t = indexes[sid].pages[page - 1]
    i = t.index(start)
    j = t.index(end, i) + len(end)
    return t[i:j]


def unit(
    id, sid, page, start, end, var, relationship, context, role="structural_suitability"
):
    return EvidenceUnit(
        evidence_id=id,
        source_id=sid,
        nbs_id="forest_restoration",
        suitability_family_id="forest_restoration__active_planting",
        variable=var,
        use_role=role,
        evidence_type="literature_relationship",
        claim_basis="expert_assertion",
        claim_scope="practice_technology",
        extraction_confidence="medium",
        quote=sl(sid, page, start, end),
        page=page,
        relationship=relationship,
        context=context,
        ruleset_version="v1.8.0",
    )


z, o, f = SIDS
units = [
    unit(
        "ev_fr_land_cover_zomer08_continuation_20261028",
        z,
        3,
        "! areas classiﬁed as various types of tundra;",
        "UNFCCC rules.",
        "land_cover",
        {
            "excluded_classes": [
                "various types of tundra",
                "irrigated or under other intensive agricultural production",
                "currently forested areas",
                "recently deforested areas",
            ]
        },
        {
            "model_use": {
                "used": True,
                "method": "Boolean CDM-AR eligibility screen",
                "source_specific_weight": None,
            },
            "applicability_hold": "Historical 2007–2012 CDM-AR source profile only; source includes plantation, agroforestry and ANR alongside reforestation. Active-planting transfer and safeguard decision pending. Enrichment excluded by source, not entire project family.",
            "continuation_of": "ev_fr_land_cover_zomer08_1",
            "continuation_page": 2,
            "numeric_calibration": "categorical source classes retained; no dataset class crosswalk or runtime mask approved",
            "reported_values": "Intensive production exclusion is justified by high-value production/food security, not universal natural tree-establishment limitation.",
        },
    ),
    unit(
        "ev_fr_land_cover_oliveira26_scope_20261028",
        o,
        4,
        "The basin includes six LULC classes,",
        "repro­\nducible conditions.",
        "land_cover",
        {"allowed_classes": ["agricultural", "non-vegetated"]},
        {
            "model_use": {
                "used": True,
                "method": "USPED erosion-reduction spatial optimization target domain",
                "source_specific_weight": None,
            },
            "applicability_hold": "Regional Caatinga allocation scope, not universal biological suitability. Non-vegetated does not authorize conversion of native non-forest ecosystems.",
            "scope": "Serido River Basin, Brazil",
            "numeric_calibration": "source-category selection only; dataset class mapping and transfer unapproved",
            "constraints_not_modelled": ["socio-economic", "legal", "logistical"],
        },
    ),
    unit(
        "ev_fr_tenure_zomer08_20261028",
        z,
        5,
        "Areas that might be available for CDM-AR, in reality,",
        "national level infrastructure and support.",
        "tenure_security",
        None,
        {
            "model_use": {
                "used": False,
                "method": "omitted enabling conditions discussed after biophysical/CDM screen",
                "source_specific_weight": None,
            },
            "intended_use": "M2b Stream B / Module 6; no T4 score",
            "calibration_hold": "No numeric tenure threshold or weight reported; land and tree tenure named as viability condition.",
        },
        "operational_risk",
    ),
]
for u in units:
    u.context["practice_as_described"] = (
        "afforestation or reforestation" if u.source_id == z else "reforestation"
    )
    if u.source_id == z:
        u.context["source_check"] = (
            "CDM first commitment period 2007–2012; p2 requires land not forested at beginning of 1990. p3 raster proxy uses 1991 GLCC. Source excludes enrichment planting; project active-planting family includes it. No transfer approved."
        )
for u in units:
    extras = {
        k: u.context.pop(k)
        for k in ["scope", "constraints_not_modelled"]
        if k in u.context
    }
    if extras:
        u.context["source_check"] = extras
errors = validate_units(units)
assert not errors, errors
for u in units:
    assert u.quote in indexes[u.source_id].pages[u.page - 1]
    assert not u.reviewer_ok
save_units(units, OUT / "evidence_staging.json")
dump(
    "validation.json",
    {
        "validate_units": errors,
        "quote_exact_page_match": True,
        "new_units": len(units),
        "central_gate_status": "not run by extraction agent; orchestrator must run dry-run with explicit authorised roles",
        "approved": False,
    },
)
dump("artifact_manifest.json", manifest)
dump("machine_table_row_inventory.json", tables)
dump("caption_inventory.json", captions)
# Explicit held evidence; these are NOT EvidenceUnits or numerical rules.
dump(
    "held_claims.json",
    [
        {
            "source_id": z,
            "page": 3,
            "raw_variable": "average growing-season temperature",
            "reported_values": "below 6.5 8C in text layer; growing-season mean, not MAT",
            "quote": sl(
                z, 3, "Areas above or approaching timberline", "DEM) was excluded."
            ),
            "hold": "Ontology mismatch: growing-season temperature distinct from mean_annual_temperature; verify printed degree glyph from image. CDM economic viability scope, no global forest boundary.",
            "existing_related_ids": ["ev_fr_elevation_zomer08_1"],
        },
        {
            "source_id": o,
            "page": 8,
            "variable": "slope",
            "quote": sl(
                o,
                8,
                "Areas with slopes greater than 75%",
                "5% of the total reforested area.",
            ),
            "hold": "Existing abs_max=75 falsely presents unconditional ceiling: source explicitly includes these areas. Keep cited planting difficulty (Santos et al. 2018) separate from optimization allocation. No automated overwrite.",
            "existing_related_ids": ["ev_fr_slope_oliveira26_1"],
        },
        {
            "source_id": z,
            "pages": [2, 3, 5],
            "hold": "All five existing numeric/categorical rules are historical CDM scope. No approved whole-active-planting transfer; 30% canopy excludes existing forest and therefore conflicts with enrichment planting family member. AI<0.65 and AI>0.65 wording leaves equality unspecified. Protected-area exclusion is model choice, not evidence all protected-area restoration is legally barred.",
        },
        {
            "source_id": o,
            "pages": [3, 4],
            "hold": "Supplementary Sections 2/3 and Figs S1/S2/S3 cited; supplementary artifact not inspected or established acquired. Full source sweep remains incomplete.",
        },
        {
            "source_id": f,
            "page": 4,
            "hold": "Equal weighting applies ES priority indicators, not establishment suitability. Water-content depths prose says m; reference names cm; Table 1 says MODIS 500 m while prose says OpenLandMap. No substitution or numeric transfer.",
        },
        {
            "source_id": "tool_afforestation_tracker_gee",
            "hold": "Historical SRCH/discovery log claims code inspection; no current SRC/acquisition identity/cached pinned code found. Reacquire via github adapter before using any reported threshold. No source vote inferred.",
        },
    ],
)
print(
    f"{len(units)} staged; {len(tables)} table rows machine-inventoried; no approvals"
)
