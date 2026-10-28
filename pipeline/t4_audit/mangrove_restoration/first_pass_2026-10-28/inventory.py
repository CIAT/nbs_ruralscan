# ruff: noqa: E402
"""Build page-linked claim-row and honest incomplete-source accounting from cached indexes."""

import json
import csv
from pathlib import Path
from nbs_ruralscan.ingest.cache import load_index

ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)
P = ROOT / "pipeline/staging/mangrove_t4_20261028"
G = "gma_mangrove_restoration_guidelines_2023"
W = "wb_2025_mangroves_coastal_resilience_bangladesh"
rows = []


def row(s, p, item, raw, status, reason, ev="", values=None):
    rows.append(
        dict(
            source_id=s,
            page=p,
            item=item,
            raw_property=raw,
            status=status,
            reason=reason,
            evidence_ids=ev.split("|") if ev else [],
            reported_values=values,
            source_weight=None,
            runtime_weight=None,
            reviewer_ok=False,
        )
    )


row(
    G,
    25,
    "Section 2.2.4",
    "Historical natural mangrove occurrence",
    "staged",
    "Site-history prerequisite; no automatic global land-use mask",
    "ev_mgt4_20261028_historic_habitat",
)
row(
    G,
    25,
    "Figure 3 and text",
    "Intertidal elevation relative to local tidal planes",
    "staged",
    "Graph inspected. Tidal datums indicative and site-varying; no terrestrial elevation transfer",
    "ev_mgt4_20261028_tidal_elevation",
    {
        "lower": "mean sea level",
        "upper": "highest astronomical tide",
        "figure_label_upper": "Highest high tide",
        "printed_pages": "47–48",
    },
)
row(
    G,
    25,
    "Section 2.2.4",
    "Geomorphic setting",
    "held",
    "Deltaic, estuarine, open coast, lagoonal and carbonate types; speculative comparative feasibility, not quantified calibration",
    values=["deltaic", "estuarine", "open coast", "lagoonal", "carbonate"],
)
for name, reason in [
    (
        "Natural regeneration",
        "Low damage; remove degradation causes; intact soil and abundant propagules",
    ),
    (
        "Assisted regeneration",
        "Reinstate tidal flow; reshape aquaculture ponds; control invasive species",
    ),
    (
        "Direct intervention",
        "After suitable conditions established, replant if insufficient propagules",
    ),
]:
    row(
        G,
        26,
        "Restoration continuum / Figure 4",
        name,
        "staged" if name == "Direct intervention" else "held",
        reason,
        "ev_mgt4_20261028_propagule_method" if name == "Direct intervention" else "",
    )
row(
    G,
    26,
    "Section 2.2.5",
    "Stakeholder support and legal feasibility",
    "staged",
    "Operational module; specific legal exclusion classes not reported",
    "ev_mgt4_20261028_stakeholder_feasibility",
)
for name, reason in [
    ("Undegraded mangrove", "Conservation destination, not planting opportunity"),
    (
        "Degraded mangrove",
        "Address future decline and socioeconomic/biophysical stressors",
    ),
    (
        "No mangroves remaining",
        "Ask historical occurrence; then natural ecosystems at site",
    ),
    (
        "Existing natural ecosystems",
        "Mudflats/seagrass branch: consider new site; avoid damage, conditional on no historic mangroves",
    ),
    (
        "Peat/mineral soils",
        "Manage recovery differently; no thresholds or new families",
    ),
    (
        "Planting not usually needed",
        "Only when socioeconomic and biophysical stressors of natural expansion addressed",
    ),
]:
    row(
        G,
        27,
        "Figure 5 decision tree",
        name,
        "held",
        "Diagram visually inspected; decision-tree topology preserved here; safeguard/method policy approval needed. "
        + reason,
    )
for group, props in [
    ("Hydroperiod", ["duration", "frequency", "level of flooding"]),
    (
        "Physicochemical characteristics",
        ["salinity", "pH", "redox potential", "sulfides", "nutrients"],
    ),
    ("Soil characteristics", ["nutrient content", "organic matter", "texture"]),
    ("Topography", ["low/high elevations"]),
    ("Vegetation", ["planned vegetation type"]),
]:
    for prop in props:
        row(
            G,
            37,
            "Figure 8: " + group,
            prop,
            "held",
            "Figure visually inspected: assessment recommendation, not fitted model use or numeric direction; keep parent/siblings. Missing precise ontology stays held, never soil-carbon or salinity proxy.",
        )
for name, reason in [
    (
        "Deforested",
        "Natural recovery possible; native planting if propagule supply lacking",
    ),
    (
        "Drained",
        "Severe subsidence may require elevation restoration, may not be practical",
    ),
    ("Eroded", "Wave-exposed erosion may need engineered intervention"),
    (
        "Organic soil",
        "Up to 80% organic matter is descriptive, not suitability cutoff; retain SOM distinct from SOC",
    ),
    (
        "Mineral soil",
        "Appropriate hydroperiod required; broad tidal ranges not quantified",
    ),
]:
    row(G, 38, "Site-history and soil-type text", name, "held", reason)
row(
    G,
    39,
    "Problem 1",
    "Salinity and hydrological connectivity",
    "held",
    "Loss of flushing can cause either freshening or hypersalinity; no single monotonic global response and no salinity VONT match",
)
row(
    G,
    39,
    "Problem 1",
    "Tidal inundation duration",
    "existing_needs_review",
    "Existing abs_max=50 loses most-species qualifier; neither shared habitat cutoff nor arbitrary tail approved",
    "ev_fr_inundation_gma23_1",
    {
        "value": 50,
        "unit": "percent time inundated",
        "qualifier": "Most species cannot establish above this; no universal cutoff",
    },
)
for side in ["Landward", "Seaward"]:
    row(
        G,
        39,
        "Figure 9 and text",
        side,
        "held",
        "Different connectivity/propagule versus wave/erosion constraints. Figure intervention schematic is not numerical calibration.",
    )
row(
    G,
    40,
    "Problem 1 continuation",
    "Inundation extremes",
    "ontology_hold",
    "Frequency extremes and salinity explicitly retained; tidal_inundation_duration is NOT matching variable; staged candidate withdrawn after adversarial review",
)
for name, cost, scale in [
    ("Consultation", "Low", "Source has incomplete phrase a scale"),
    ("Elevation/inundation", "Low", "Small scale; low accuracy/resolution possible"),
    (
        "Model – Lidar/Digital Elevation Model",
        "High",
        "Can be large scale; moderate/high resolution without numeric grain",
    ),
    ("Mini buoys", "Low/Mid", "Small scale; local reference comparison"),
]:
    row(
        G,
        40,
        "Table 1 (all four methods)",
        name,
        "requirements_only",
        "Visually inspected full table. Cost category describes measurement method, not suitability or MCDA weight",
        values={"cost_category": cost, "spatial_support": scale},
    )
row(
    G,
    40,
    "Problem 2",
    "Wave/current exposure",
    "held",
    "Calm establishment window; current, wave and tidal dynamics. No thresholds; no wave/current VONT match. Do not substitute wind hazard.",
)
row(
    G,
    41,
    "Problem 3",
    "Propagule supply and transport",
    "held",
    "EMR requires propagules; tide/river transport and anchoring matter. Nearby forest Euclidean distance alone does not calibrate recruitment.",
)
row(
    G,
    41,
    "Problem 4",
    "Sedimentation rate",
    "held",
    "Too high buries roots; too low limits nutrient/elevation maintenance. No native rate unit or endpoints. sediment_retention is an effect variable, not interchangeable.",
)
row(
    G,
    109,
    "Appendix A chapter 2 key messages",
    "Prolonged inundation",
    "existing",
    "Repeated guideline summary, not independent vote",
    "ev_fr_inundation_gma23_2",
)
for p in [43, 69, 70, 71, 85, 92, 93, 103, 104]:
    row(
        G,
        p,
        "Other tables and continuations",
        "Costs/monitoring/blue carbon",
        "pending_scope_sweep",
        "Structure enumerated; detailed row-by-row claim relevance not yet resolved. Do not mark source swept.",
    )
row(
    W,
    6,
    "2.1 bullet 1",
    "Distance to existing mangrove",
    "staged",
    "Source design screen; not measured establishment cutoff",
    "ev_mgt4_20261028_proximity_source_choice",
    {"value": 10, "unit": "km", "qualifier": "potential colonization within distance"},
)
row(
    W,
    6,
    "2.1 bullet 2",
    "Water side of coastal embankments",
    "held",
    "Flood-risk benefit-oriented constrained AOI, not general ecological suitability or exclusion",
)
row(
    W,
    6,
    "2.1 bullet 3",
    "Intertidal extent and tidal range",
    "held",
    "Existing model use; Murray2019 and Bricheno2016 cited. No numeric datum/tidal-range boundary given; no mapping to duration percent",
)
row(
    W,
    6,
    "2.1 bullet 3",
    "Sheltered low wave and freshwater input",
    "held",
    "Secondary Alongi2002 support; no numeric response and no exact VONT wave/freshwater-input fit",
)
row(
    W,
    6,
    "2.1 bullet 4",
    "Accreting versus eroding foreshore",
    "held",
    "Local dynamics change technique; Luijendijk2018 cited. Not sediment retention or generic soil erosion hazard",
)
row(
    W,
    7,
    "2.1 continuation bullet 5",
    "Active agriculture/aquaculture/residential",
    "operational_hold",
    "All classes retained; authors avoid land acquisition, not ecological unsuitability. No global legal mask approved",
    values=["active agriculture", "aquaculture", "residential settlements"],
)
row(
    W,
    7,
    "Table 1",
    "Hydrodynamic design conditions",
    "excluded_from_T4",
    "25-year return period, plus 1 m sea-level rise by 2050: embankment-protection model inputs, not mangrove establishment thresholds",
)
for p in [8, 9, 10, 11, 13, 14, 19]:
    row(
        W,
        p,
        "Remaining tables/continuations",
        "Vegetation geometry, economics and protection outcomes",
        "pending_scope_sweep",
        "Effect/design tables not establishment calibration; complete row-level effect inventory outside this bounded T4 pass",
    )
for p in range(28, 53):
    row(
        W,
        p,
        "Appendix",
        "Model equations/data supplements",
        "pending_scope_sweep",
        "Do not infer thresholds from model Appendix. Remaining source-level completion held until exact subsection/table contents accounted for.",
    )
(P / "source_row_inventory.json").write_text(
    json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
)
with (P / "source_row_inventory.csv").open("w") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(
        {
            k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
            for k, v in r.items()
        }
        for r in rows
    )
page_inventory = []
for sid, reviewed in [
    (G, {25, 26, 27, 36, 37, 38, 39, 40, 41, 109}),
    (W, {1, 5, 6, 7}),
]:
    idx = load_index(sid, P / "indexes")
    for n in range(1, idx.n_pages + 1):
        page_inventory.append(
            {
                "source_id": sid,
                "page": n,
                "status": "targeted_read" if n in reviewed else "not_claim_swept",
                "table_blocks": sum(t.page == n for t in idx.tables),
                "caption_blocks": sum(c.page == n for c in idx.captions),
                "supplement_coverage": "unresolved referenced material unless explicitly inventoried",
            }
        )
(P / "page_inventory.json").write_text(json.dumps(page_inventory, indent=2) + "\n")
print("Claim rows", len(rows), "page records", len(page_inventory))
