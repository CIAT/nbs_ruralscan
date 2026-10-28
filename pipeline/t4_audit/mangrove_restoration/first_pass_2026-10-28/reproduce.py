# ruff: noqa: E402
"""Reproduce bounded mangrove source reconciliation and deterministic staged extraction.
Run: PYTHONPATH=src .venv/bin/python pipeline/staging/mangrove_t4_20261028/reproduce.py --corpus PATH
No register, review, policy, or progress mutation. Requires existing verified artifacts.
"""

import argparse
import csv
import json
import hashlib
import re
from pathlib import Path
from collections import Counter
from dataclasses import asdict
from nbs_ruralscan.ingest.pdf import build_index
from nbs_ruralscan.ingest.cache import load_index, save_index
from nbs_ruralscan.ingest.integrity import (
    identity_error,
    pdf_title_error,
    source_identity_differs,
)
from nbs_ruralscan.recipe.evidence import (
    EvidenceUnit,
    package_for_extraction_multi,
    validate_units,
    save_units,
)

ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)
OUT = ROOT / "pipeline/staging/mangrove_t4_20261028"
OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    with (ROOT / path).open() as f:
        return list(csv.DictReader(f))


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    args = ap.parse_args()
    ev = read("schema/registers/EV_evidence_register.csv")
    src = read("schema/registers/SRC_source_register.csv")
    queue = read("pipeline/acquisition_queue.csv")
    srch = read("schema/registers/SRCH_search_register.csv")
    hist = read("pipeline/metrics/review_log.csv")
    scoped = [r for r in ev if r["nbs_id"] == "mangrove_restoration"]
    active = [r for r in scoped if r["review_state"] != "dropped"]
    lane = [
        r
        for r in active
        if r["use_role"] in ("structural_suitability", "operational_risk")
    ]
    ids = {r["evidence_id"] for r in scoped}
    sids = {r["source_id"] for r in scoped}
    sources = [
        r
        for r in src
        if r["source_id"] in sids or "mangrove_restoration" in r["nbs_ids"].split("|")
    ]
    decisions = json.loads((ROOT / "docs/review/decisions.json").read_text())
    hits = []

    def walk(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ids:
                    hits.append({"path": path + "/" + k, "record": v})
                walk(v, path + "/" + k)
        elif isinstance(obj, list):
            for n, v in enumerate(obj):
                walk(v, path + "/" + str(n))

    walk(decisions)
    dump(
        "reconciliation.json",
        {
            "nbs_id": "mangrove_restoration",
            "family": "mangrove_restoration__tidal_coastal",
            "ruleset": "v1.8.0",
            "total_ev": len(scoped),
            "active_ev": len(active),
            "active_lane": len(lane),
            "active_lane_roles": dict(Counter(r["use_role"] for r in lane)),
            "active_lane_true_approval": sum(r["reviewer_ok"] == "true" for r in lane),
            "source_count": len(sources),
            "baseline_T4_csv": {
                "commit": "f18ff32",
                "present": False,
                "observation": "Agent inspected before central orchestration generated header-only CSV",
            },
            "current_T4_csv_present": (
                ROOT / "schema/recipes/mangrove_restoration/T4_suitability_mappings.csv"
            ).exists(),
            "review_log_scope": [r for r in hist if r["evidence_id"] in ids],
            "review_log_lane": [
                r for r in hist if r["evidence_id"] in {x["evidence_id"] for x in lane}
            ],
            "dashboard_decision_matches": hits,
            "local_pending_decisions_present": (
                ROOT / "pipeline/review/decisions.json"
            ).exists(),
            "sources": sources,
            "queue": [r for r in queue if "mangrove" in str(r).lower()],
            "search_records": [r for r in srch if "mangrove" in str(r).lower()],
            "existing_lane": lane,
            "source_cache_status": [
                {
                    "source_id": s["source_id"],
                    "cached_pdf": (args.corpus / (s["source_id"] + ".pdf")).exists(),
                }
                for s in sources
            ],
            "screened_corpus_n": None,
            "quality_weighted_support": None,
        },
    )
    targets = [
        "gma_mangrove_restoration_guidelines_2023",
        "wb_2025_mangroves_coastal_resilience_bangladesh",
    ]
    indexes = {}
    identities = []
    specs = [
        {
            "variable": "land_cover",
            "aliases": [
                "history",
                "natural ecosystems",
                "aquaculture",
                "agriculture",
                "residential",
            ],
        },
        {"variable": "elevation", "aliases": ["tidal", "datum", "intertidal"]},
        {
            "variable": "tidal_inundation_duration",
            "aliases": ["hydrology", "hydroperiod", "flooding"],
        },
        {"variable": "distance_to_forest", "aliases": ["propagules", "seed", "10 km"]},
        {
            "variable": "regeneration_potential",
            "aliases": ["propagule", "recolonization"],
        },
        {
            "variable": "soil_ph",
            "aliases": ["pH", "salinity", "redox", "sulfides", "nutrients", "texture"],
        },
        {"variable": "tenure_security", "aliases": ["tenure", "ownership", "legal"]},
        {"variable": "extension_governance", "aliases": ["stakeholder", "support"]},
    ]
    for sid in targets:
        s = next(r for r in src if r["source_id"] == sid)
        q = next(r for r in queue if r["source_id"] == sid)
        pdf = args.corpus / (sid + ".pdf")
        err = identity_error(q) or pdf_title_error(pdf, s["citation"])
        assert not err, (sid, err)
        assert not source_identity_differs(s, q)
        assert s["library_path"]
        digest = hashlib.sha1(pdf.read_bytes()).hexdigest()
        identities.append(
            {
                "source_id": sid,
                "sha1": digest,
                "registered_sha1": s["artifact_sha1"],
                "library_path": s["library_path"],
                "opening_title_match": True,
                "queue_title_verified": q["title_verified"],
                "canonical_source_reused": True,
                "new_scope": "mangrove_restoration__tidal_coastal / T4",
                "prior_queue_tables": q["tables"],
                "prior_queue_family": q["family"],
                "source_quality_tier": s["benchmark_tier"],
            }
        )
        idx = load_index(sid, OUT / "indexes")
        if not idx or idx.sha1 != digest[:16] or not idx.tables_extracted:
            idx = build_index(pdf, source_id=sid, with_tables=True)
            save_index(idx, OUT / "indexes")
        indexes[sid] = idx
        bundle = package_for_extraction_multi(
            idx,
            specs,
            force=True,
            full_tables=True,
            max_passages_per_var=150,
            min_score=0,
            ev_register=ROOT / "schema/registers/EV_evidence_register.csv",
        )
        dump(sid + "_retrieval.json", bundle)
        dump(
            sid + "_structure.json",
            {
                "pages": idx.n_pages,
                "needs_ocr": idx.needs_ocr_pages,
                "captions": [asdict(c) for c in idx.captions],
                "tables": [asdict(t) for t in idx.tables],
                "sections": [asdict(s) for s in idx.sections],
                "supplement_mentions": [
                    {"page": i + 1, "text": p}
                    for i, p in enumerate(idx.pages)
                    if re.search(r"supplement|appendix|appendices", p, re.I)
                ],
                "coverage_status": "partial: enumerated structure does not establish completed claim coverage",
            },
        )
    dump("artifact_identity.json", identities)
    units = []

    def add(
        sid,
        suffix,
        page,
        variable,
        start,
        end,
        direction,
        raw,
        context,
        basis="expert_assertion",
        role="structural_suitability",
        attribution=None,
    ):
        txt = indexes[sid].pages[page - 1]
        a = txt.index(start)
        b = txt.index(end, a) + len(end)
        quote = txt[a:b]
        assert quote in txt
        u = EvidenceUnit(
            evidence_id="ev_mgt4_20261028_" + suffix,
            source_id=sid,
            nbs_id="mangrove_restoration",
            suitability_family_id="mangrove_restoration__tidal_coastal",
            variable=variable,
            use_role=role,
            evidence_type="literature_relationship",
            claim_basis=basis,
            claim_scope="practice_technology",
            extraction_confidence="high",
            quote=quote,
            page=page,
            raw_name=raw,
            relationship={"type": "qualitative", "direction": direction},
            context=context,
            attribution=attribution,
            ruleset_version="v1.8.0",
        )
        units.append(u)

    g = targets[0]
    w = targets[1]
    common = {
        "practice_as_described": "Mangrove planting and ecological mangrove restoration; establishment method is a project choice, not a new family",
        "calibration_hold": "No numeric response scores or transferable global cutoffs; human review pending",
        "runtime_weight": None,
        "source_weight": None,
    }
    add(
        g,
        "historic_habitat",
        25,
        "land_cover",
        "The most important question",
        "successful mangrove restoration.",
        "unclear",
        "Historical occurrence of naturally growing mangroves",
        {
            **common,
            "reported_values": {
                "requirement": "Investigate prior natural mangrove occurrence, cause of loss, and failure of natural recovery"
            },
            "intended_use": "Categorical habitat-history prerequisite for site assessment; no automatic mask approved",
            "remaining_decision": "Approve source reading and decide how site history is represented in opportunity-space safeguards",
        },
    )
    add(
        g,
        "tidal_elevation",
        25,
        "elevation",
        "Mangrove distribution can potentially",
        "(Figure 3, bottom panel).",
        "optimum_range",
        "Elevation relative to local tidal planes",
        {
            **common,
            "vertical_reference": ["mean sea level", "highest astronomical tide"],
            "spatial_support": "site-specific tidal planes; Figure 3 caption says tidal datums indicative and may vary across sites",
            "reported_values": {
                "lower_reference": "mean sea level",
                "upper_reference": "highest astronomical tide",
                "endpoint_meaning": "potential natural habitat envelope; sites that have always been below mean sea level or above high tide limit have little chance of success",
            },
            "intended_use": "Retain local-datum habitat envelope; do not convert to absolute metres or pool with terrestrial DEM elevation",
            "remaining_decision": "Local tidal datum and hydroperiod binding required before any executable rule",
        },
        basis="cited_secondary",
        attribution="GMA guideline references 17 and 18; Figure 3 adapted from Primavera (2012), reference 20",
    )
    add(
        g,
        "propagule_method",
        26,
        "regeneration_potential",
        "Direct intervention –",
        "natural recolonization.",
        "unclear",
        "Insufficient mangrove propagules for natural recolonization",
        {
            **common,
            "practice_as_described": "Direct replanting only after suitable conditions established where propagules insufficient",
            "model_use": {"used": False, "scope": "restoration-method guidance"},
            "intended_use": "Method selection: planting versus natural recruitment, not generic suitability weight",
            "remaining_decision": "Keep method prerequisite separate from shared tidal-coastal envelope",
        },
    )
    add(
        g,
        "stakeholder_feasibility",
        26,
        "extension_governance",
        "The highest priority factors",
        "no legal barrier to project implementation.",
        "unclear",
        "Stakeholder support and legal feasibility",
        {
            **common,
            "practice_as_described": "Mangrove restoration project planning",
            "intended_use": "M2b operational module / M6; no core suitability score",
            "remaining_decision": "Local stakeholder and legal feasibility assessment; sentence gives no mapped legal exclusion classes",
        },
        role="operational_risk",
    )
    add(
        w,
        "proximity_source_choice",
        6,
        "distance_to_forest",
        "Existing presence of mangroves",
        "existing mangrove patches.",
        "decreasing",
        "Distance to existing mangroves on the foreshore",
        {
            **common,
            "practice_as_described": "Bangladesh coastal mangrove afforestation for embankment protection",
            "country": "BGD",
            "income_group": "lower_middle",
            "model_use": {
                "used": True,
                "scope": "benefit-oriented potential location screening",
                "source_lineage": "Method follows Gijón Mancheño et al. 2021 and World Bank 2024 (same PDF page); independent lineage unresolved, not an extra vote",
                "method": "10 km proximity screen; other joint criteria retained in source-row inventory",
                "weight": None,
            },
            "reported_values": {
                "threshold": 10,
                "unit": "km",
                "operator": "within",
                "meaning": "authors consider potentially suitable for colonization; not measured establishment boundary",
            },
            "observed_dataset": "Global Forest Watch mangrove patches",
            "intended_use": "Regional source profile only; constrained-AOI design choice, no global cutoff",
            "calibration_hold": "Source Boolean proximity screen preserved; no source scores, excluded tail or global ecological transfer approved",
            "remaining_decision": "Whether this regional proximity design belongs in scenario screening; mangrove-specific mask required",
        },
        basis="cited_secondary",
        attribution="Potential-location methodology follows Gijón Mancheño et al. (2021) and World Bank (2024), introduced on PDF page 6; do not count as independent of those sources",
    )
    u = units[-1]
    t = indexes[w].pages[5]
    a = t.index("The identiﬁcation of potential mangrove sites")
    b = t.index("In particular,", a)
    u.justification_quote = t[a:b].strip()
    u.justification_page = 6
    errors = validate_units(units)
    dump("validation.json", errors)
    assert not errors, errors
    save_units(units, OUT / "units.json")
    print(
        json.dumps(
            {
                "units": len(units),
                "source_identities": len(identities),
                "active_lane": len(lane),
                "review_log_lane": sum(
                    r["evidence_id"] in {x["evidence_id"] for x in lane} for r in hist
                ),
                "decision_hits": len(hits),
            }
        )
    )


if __name__ == "__main__":
    main()
