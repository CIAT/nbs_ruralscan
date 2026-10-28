# ruff: noqa: E402
from pathlib import Path
import csv
import json

ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)
OUT = ROOT / "pipeline/staging/forest_t4_20261028"
OUT.mkdir(parents=True, exist_ok=True)
src = list(csv.DictReader((ROOT / "schema/registers/SRC_source_register.csv").open()))
queue = list(csv.DictReader((ROOT / "pipeline/acquisition_queue.csv").open()))
stock = list(
    csv.DictReader((ROOT / "reference/stocktake/peer_reviewed_benchmarked.csv").open())
)
result = []
for r in stock:
    if r["NbS_Practice"] not in (
        "Reforestation and afforestation",
        "Forest conservation and restoration",
    ):
        continue
    if "mangrove" in (r["File"] + " " + r["NbS_Subpractice"]).lower():
        continue
    doi = r["doi_extracted"].lower().strip()
    s = [
        x["source_id"]
        for x in src
        if doi and doi != "na" and x["doi"].lower().strip() == doi
    ]
    q = [
        x["source_id"]
        for x in queue
        if doi and doi != "na" and x["doi"].lower().strip() == doi
    ]
    result.append(
        {
            "stocktake_file": r["File"],
            "stocktake_doi_unverified": doi,
            "stocktake_subpractice": r["NbS_Subpractice"],
            "stocktake_variables_not_evidence": r["Input_Variables"],
            "source_ids_exact_doi": ";".join(s),
            "queue_ids_exact_doi": ";".join(q),
            "status": "exact DOI candidate match; artifact identity checked separately"
            if s or q
            else "no exact DOI match; title/canonical identity reconciliation and source intake pending; not evidence source absence",
            "reported_benchmark_not_adopted": r["Final_Benchmark"],
        }
    )
with (OUT / "stocktake_reconciliation.csv").open("w") as f:
    w = csv.DictWriter(f, fieldnames=list(result[0]))
    w.writeheader()
    w.writerows(result)
z = "fr_zomer_cdm_afforestation_suit_2008"
o = "fr_semiarid_reforestation_spatial_planning_2026"
f = "optimizing_afforestation_reforestation_degraded_2024"
inv = []


def entry(s, p, item, status, ids=None, detail=""):
    inv.append(
        dict(
            source_id=s,
            pages=p,
            item=item,
            disposition=status,
            evidence_ids=ids or [],
            detail=detail,
        )
    )


for var, eid in [
    ("aridity_index", "ev_fr_aridity_index_zomer08_1"),
    ("elevation", "ev_fr_elevation_zomer08_1"),
    ("water bodies/urban/forested/recently deforested", "ev_fr_land_cover_zomer08_1"),
]:
    entry(
        z,
        [2, 3],
        var,
        "existing rule retained; CDM-specific transfer hold",
        [eid],
        "Source is 2007–2012 CDM economic/eligibility screen, not whole restoration family.",
    )
entry(
    z,
    [3],
    "tundra; irrigated/intensive agriculture; currently forested; recently deforested",
    "new continuation staged",
    ["ev_fr_land_cover_zomer08_continuation_20261028"],
    "Native non-forest safeguard unresolved. Agricultural food-security exclusion is source policy, not automatic project mask.",
)
entry(
    z,
    [3],
    "30% canopy forest definition",
    "existing numeric source profile; transfer hold",
    ["ev_fr_tree_canopy_cover_zomer08_1"],
    "Forest definition 500 m VCF; source comparison to 1991 landcover acknowledged rough estimate/error; enrichment planting excluded in p2 source scope.",
)
entry(
    z,
    [3],
    "growing-season mean temperature below 6.5°C",
    "ontology + glyph + transfer hold",
    detail="Distinct from MAT; no new canonical variable introduced.",
)
for item in [
    "VMAP country boundaries",
    "USGS GLCC v2 landcover",
    "MODIS VCF tree canopy",
    "SRTM topography",
    "WDPA protected areas",
    "WorldClim climate",
    "GPW population",
    "MOD17A3 NPP",
    "GLASOD degradation",
]:
    entry(
        z,
        [3],
        item,
        "dataset use inventoried; not a separate weighted suitability criterion",
        detail="500 m analysis grid; source inputs 500 m–1 km. No source weight vector reported.",
    )
entry(
    z,
    [3, 4],
    "NPP, population density, GLASOD erosion/degradation",
    "descriptors; no calibration extracted",
    detail="Source describes socio-ecological characteristics after eligibility mask; raw mapped values not siting limits.",
)
entry(
    z,
    [5],
    "protected areas; Fig 2 caption",
    "existing source exclusion; legal generalisation held",
    ["ev_fr_protected_area_status_zomer08_1"],
    "Caption does not establish universal legal prohibition on restoration in protected areas.",
)
entry(
    z,
    [5],
    "land/tree tenure",
    "new operational mention staged",
    ["ev_fr_tenure_zomer08_20261028"],
    "Not modelled, no weight or calibration. Markets/opportunity costs/national support retained in same source context, not extra model-use votes.",
)
entry(
    z,
    list(range(4, 13)),
    "Table 1 + Figs 1–8 (see caption inventory)",
    "output/descriptor tables and figures; no graphic threshold extraction",
    detail="Captions/table rows machine inventoried. No graphical precision or full figure visual review claimed.",
)
for item in [
    "Digital Model Elevation (DEM): Copernicus 30 m",
    "Soil Type: IBGE 1:250,000",
    "Land Use and Land Cover: MapBiomas 30 m",
    "Precipitation: Xavier 0.1° daily",
]:
    entry(
        o,
        [3],
        "Table 1: " + item,
        "input to erosion/priority optimizer; not establishment calibration",
    )
for item in [
    "rainfall erosivity R",
    "soil erodibility K",
    "cover-management C",
    "support practice P",
    "upslope contributing area U",
    "slope β",
    "m=1.6 and n=1.3 rill-erosion exponents",
    "drainage network",
]:
    entry(
        o,
        [3],
        item,
        "USPED model parameter/use; no T4 importance transfer",
        detail="Not an AHP suitability criterion weight. Exponents describe erosion transport model.",
    )
entry(
    o,
    [4],
    "agricultural and non-vegetated allocation classes",
    "new categorical scope staged",
    ["ev_fr_land_cover_oliveira26_scope_20261028"],
    "Socio-economic, legal and logistical constraints explicitly omitted, not demonstrated irrelevant.",
)
entry(
    o,
    [8],
    "slope >75% + Santos 2018 attribution",
    "existing numeric rule requires correction/hold",
    ["ev_fr_slope_oliveira26_1"],
    "Full paragraph includes >75% slopes in restoration allocation; cannot be universal exclusion.",
)
entry(
    o,
    [3, 4],
    "Supplementary sections 2/3 and Figs S1/S2/S3",
    "missing supplementary artifact hold",
    detail="Full source-table closure impossible without supplement; not searched anew.",
)
entry(
    o,
    list(range(3, 10)),
    "Main Figs 1–8",
    "source/output maps and landscape metrics; no graphical threshold extraction",
    detail="Caption inventory retained; numeric map extrema are not T4 limits. All figures still lack complete visual second-read.",
)
# Every Table 1 data row is accounted for; roles taken from methods pp2–5, not title.
groups = {
    "target_domain": ["Deforestation", "Impervious Surface", "Land Cover"],
    "ecosystem_service_priority": [
        "NDVI",
        "EVI",
        "GPP",
        "Lai–FPAR",
        "Water Content",
        "ET",
        "ABG",
        "BGB",
    ],
    "wildfire_model": [
        "Fire Hotspot",
        "Elevation",
        "Slope",
        "Aspect",
        "Precipitation",
        "Temperature",
        "Wind Speed",
        "Road Network",
        "Population Density",
    ],
    "environmental_pressure": ["AOD"],
    "planning_comparison": ["Land-Use Planning"],
}
for group, names in groups.items():
    for item in names:
        entry(
            f,
            [4],
            "Table 1: " + item,
            "retained source-use inventory; "
            + (
                "existing target-domain EV"
                if group == "target_domain"
                else "not establishment suitability"
            ),
            ["ev_fr_land_cover_fahrudin24_1"] if group == "target_domain" else [],
            "Source component: "
            + group
            + ". NDVI also wildfire predictor; temperature also environmental-pressure indicator. No weights automatically enter T4.",
        )
entry(
    f,
    [4],
    "ES weighting hierarchy",
    "equal weighting retained at source ES component; not T4 weights",
    detail="FWS: precipitation + average water content across six depths − ET; BMP: EVI/FPAR/GPP/LAI/NDVI; CS: BGB/AGB/global carbon; composite FWS/BMP/CS. Formula/table naming inconsistencies stay uncorrected; depths prose m versus cited source cm; table/prose data identity discrepancies.",
)
entry(
    f,
    [4, 5],
    "Wildfire predictor importance",
    "Gini importance, wildfire risk model; no T4 importance transfer",
    detail="Source says 70% sample points/30% training; retain wording, do not silently repair. Fig9 distributions are fire-hotspot training values, not suitability thresholds.",
)
entry(
    f,
    [7],
    "Table 2: all 12 subdistricts × afforestation/reforestation areas",
    "output area accounting excluded from T4 calibration",
    detail="Belitung subdistrict hectares are model outputs, not thresholds or study votes.",
)
entry(
    f,
    list(range(3, 14)),
    "Figs 1–13",
    "diagram, covariate maps, priority and model-evaluation outputs inventoried; no establishment curves derived",
    detail="Complete visual second-read pending. Map minima/maxima and priority class colors not establishment suitability.",
)
(OUT / "inspected_source_inventory.json").write_text(json.dumps(inv, indent=2) + "\n")
print(
    "stocktake rows",
    len(result),
    "no exact DOI match",
    sum(not x["source_ids_exact_doi"] and not x["queue_ids_exact_doi"] for x in result),
    "inspected items",
    len(inv),
)
