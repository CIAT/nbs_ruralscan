# ruff: noqa: E402
"""Locate existing stocktake PDFs and inventory Aduana; no metadata verification or intake."""

import argparse
import csv
import json
import hashlib
import unicodedata
from pathlib import Path
from dataclasses import asdict
from nbs_ruralscan.ingest.pdf import build_index
from nbs_ruralscan.ingest.cache import save_index

ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)
P = ROOT / "pipeline/staging/mangrove_t4_20261028"
P.mkdir(parents=True, exist_ok=True)
ap = argparse.ArgumentParser()
ap.add_argument("--stocktake-root", type=Path, required=True)
args = ap.parse_args()
with (ROOT / "reference/stocktake/peer_reviewed_benchmarked.csv").open() as f:
    seeds = [r for r in csv.DictReader(f) if "mangrove" in r["File"].lower()]
files = {
    unicodedata.normalize("NFC", p.name): p for p in args.stocktake_root.rglob("*.pdf")
}
found = []
for s in seeds:
    path = files.get(unicodedata.normalize("NFC", s["File"]))
    row = {
        "stocktake_file": s["File"],
        "local_path": str(path) if path else None,
        "metadata_verified": False,
        "intake_status": "held_pending_central_metadata_identity_and_team_library_registration",
        "stocktake_row": s,
    }
    if path:
        row["artifact_sha1"] = hashlib.sha1(path.read_bytes()).hexdigest()
        row["team_relative_path"] = (
            "D591_Rural-Scan_NBS/" + str(path).split("/D591_Rural-Scan_NBS/", 1)[1]
        )
    found.append(row)
(P / "stocktake_located.json").write_text(
    json.dumps(found, indent=2, ensure_ascii=False) + "\n"
)
p = next(
    Path(r["local_path"]) for r in found if r["stocktake_file"].startswith("Aduana")
)
idx = build_index(p, source_id="UNREGISTERED_aduana_2023", with_tables=True)
save_index(idx, P / "indexes")
rows = []


def add(page, item, status, reason, start=None, end=None, values=None):
    text = idx.pages[page - 1]
    quote = None
    if start:
        a = text.index(start)
        b = text.index(end, a) + len(end) if end else len(text)
        quote = text[a:b]
    rows.append(
        {
            "file": p.name,
            "pdf_page": page,
            "printed_page": 82 + page,
            "item": item,
            "status": status,
            "reason": reason,
            "quote": quote,
            "reported_values": values,
            "reviewer_ok": False,
            "metadata_verified": False,
        }
    )


for v in ["elevation", "slope", "precipitation", "air temperature"]:
    add(
        3,
        v,
        "variable_use_supported_intake_hold",
        "Model actually uses this member of complete four-variable criterion set. No native curve extracted without missing Table2.",
        "To determine land suitability for mangroves",
        "seconds.",
        {
            "parent": "WLC land suitability",
            "siblings": ["elevation", "slope", "precipitation", "air temperature"],
            "resolution": "30-arc seconds",
            "data": {
                "elevation": "ASTER Global Digital Elevation Map",
                "slope": "ASTER Global Digital Elevation Map",
                "air temperature": "Global Solar Atlas average air temperature",
                "precipitation": "WorldClim average precipitation",
            },
            "depth": None,
            "time_period": None,
        },
    )
add(
    4,
    "Suitability class scores",
    "reported_ordinal_scale",
    "Class labels and scores are explicit; criterion cutpoints missing. Do not infer normalized scores or all-variable thresholds.",
    "Four classes for land suitability",
    "where in the final score of the",
    {
        "unsuitable": 1,
        "marginally_suitable": 2,
        "moderately_suitable": 3,
        "highly_suitable": 4,
    },
)
add(
    4,
    "WLC equation and weights",
    "reported_assumption",
    "Equal weights assumed for complete four-member set; normalized 1/4 is a derivation, not explicitly printed. No runtime adoption.",
    "Where S is the final score",
    "mapped according to this equation and given values.",
    {
        "method": "WLC",
        "weight_policy": "assumed equal",
        "n_siblings": 4,
        "printed_numeric_weights": None,
        "parent_set": ["elevation", "slope", "precipitation", "air temperature"],
    },
)
add(
    5,
    "No AHP applied",
    "reported_method_limit",
    "Do not assign expert elicitation quality or AHP weights.",
    "However,",
    "respondents to AHP questionnaires.",
)
add(
    4,
    "Short-duration temperature tolerance",
    "secondary_scope_hold",
    "8 to42°C short-period tolerance cited Monsef2013, not annual mean function. Temperature time scale differs from average-air-temperature model input.",
    "Mangroves",
    "(Monsef et al., 2013).",
    {
        "low": 8,
        "high": 42,
        "unit": "°C",
        "time_support": "short periods",
        "attribution": "Monsef et al.2013",
    },
)
add(
    5,
    "Hydrology omitted and elevation proxy",
    "proxy_hold",
    "Elevation stated as inundation replacement. Cannot transfer native elevation to local tidal hydroperiod without vertical reference and mapping.",
    "Also, parameters in this study",
    "2007).",
    {"tidal_datum": None, "vertical_reference": None, "hydroperiod_measure": None},
)
add(
    5,
    "Excluded physicochemical variables",
    "not_model_use",
    "Do not count soil/water pH, salinity or nutrients as used in this model. They are proposed field followup.",
    "Given that this is a baseline study",
    "specificity of species to be planted.",
    {"not_included": ["water pH", "salinity", "nutrient availability"]},
)
add(
    4,
    "Table 2",
    "missing_source_component",
    "Text explicitly refers to parameter table, but it is absent from this artifact in text and rendered page. No numeric-class recovery can be claimed.",
    "Table 2 presents",
    "literature.",
)
add(
    2,
    "Table 1",
    "missing_source_component",
    "Referenced coastal municipal population table is absent; descriptive context, not suitability calibration.",
)
add(3, "Figure 1", "context_only", "Administrative map; no calibration or exclusions.")
add(
    4,
    "Figure 3",
    "output_map",
    "Output suitability colours only; no per-input direction/cutpoints. Image inspected. Do not reverse-engineer thresholds from final map.",
)
add(
    4,
    "Figure 2",
    "missing_or_numbering_gap",
    "Numbering jumps Figure1 to Figure3; no Figure2 found. Contents unknown, explicit hold.",
)
for n in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
    add(
        n,
        "Page accounting",
        "read",
        "Read page text; PDF3–5 visually inspected. References begin PDF6 and continue through PDF9; no standalone supplement or table appears at document end.",
    )
(P / "aduana_inventory.json").write_text(
    json.dumps(
        {
            "metadata_status": "unverified; not a registered source or EV",
            "artifact_sha1": hashlib.sha1(p.read_bytes()).hexdigest(),
            "opening_title": idx.pages[0][:650],
            "page_count": idx.n_pages,
            "claim_rows": rows,
            "tables_detected": [asdict(t) for t in idx.tables],
            "figures_detected": [asdict(c) for c in idx.captions],
            "source_weight_quality": None,
            "runtime_weight": None,
        },
        indent=2,
        ensure_ascii=False,
    )
    + "\n"
)
print(
    "Located",
    sum(bool(x["local_path"]) for x in found),
    "of",
    len(found),
    "stocktake files; Aduana rows",
    len(rows),
)
