# ruff: noqa: E402
"""Read-only register/corpus audit. Writes exclusively beside this script."""

from pathlib import Path
import csv
import json
import collections
import hashlib
import sys

ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)
OUT = ROOT / "pipeline/staging/forest_t4_20261028"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.ingest.integrity import identity_error, pdf_title_error

CACHES = [ROOT / ".cache/corpus"]


def rows(p):
    return list(csv.DictReader((ROOT / p).open()))


def dump(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def writecsv(name, data):
    if not data:
        return
    fields = list(dict.fromkeys(k for r in data for k in r))
    with (OUT / name).open("w") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(data)


ev = rows("schema/registers/EV_evidence_register.csv")
fr = [
    r
    for r in ev
    if r["nbs_id"] == "forest_restoration"
    and r["use_role"] in ("structural_suitability", "operational_risk")
]
src = {r["source_id"]: r for r in rows("schema/registers/SRC_source_register.csv")}
queue = rows("pipeline/acquisition_queue.csv")
review = rows("pipeline/metrics/review_log.csv")
q = {r["source_id"]: r for r in queue}
ids = {r["evidence_id"] for r in fr}
hist = [r for r in review if r["evidence_id"] in ids]
# Decisions remain separate from applied review history. Search all known workspaces read-only.
# Historical external review locations are recorded in review_decisions.json.
# Reruns inspect this checkout; external pending decisions must be supplied separately.
decision_paths = [
    ROOT / "pipeline/review/decisions.json",
    ROOT / "docs/review/decisions.json",
]
decisions = []
for p in decision_paths:
    if p.exists():
        obj = json.loads(p.read_text())
        decisions.append(
            {
                "path": str(p),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "matching_entries": {
                    k: v
                    for k, v in obj.items()
                    if any(e in k or e in json.dumps(v) for e in ids)
                },
            }
        )
records = []
for r in fr:
    h = [x for x in hist if x["evidence_id"] == r["evidence_id"]]
    records.append(
        {
            **r,
            "history_count": len(h),
            "history": json.dumps(h),
            "decision_files_checked": json.dumps([str(p) for p in decision_paths]),
            "pending_decision_match": any(
                r["evidence_id"] in json.dumps(x["matching_entries"]) for x in decisions
            ),
        }
    )
writecsv("evidence_accounting.csv", records)
dump("review_decisions.json", decisions)
writecsv("review_history.csv", hist)
sids = sorted(
    {r["source_id"] for r in fr}
    | {
        r["source_id"]
        for r in queue
        if "forest_restoration" in r["nbs_id"].split("|")
        and "T4" in r["tables"].split("|")
    }
)
inv = []
for sid in sids:
    s = src.get(sid, {})
    qq = q.get(sid)
    files = [p for c in CACHES for p in c.glob(sid + ".*") if p.is_file()]
    pdf = next((p for p in files if p.suffix == ".pdf"), None)
    ee = [r for r in fr if r["source_id"] == sid]
    inv.append(
        {
            "source_id": sid,
            "citation": s.get("citation", (qq or {}).get("citation", "")),
            "source_registered": bool(s),
            "queue_present": bool(qq),
            "queue_status": (qq or {}).get("status", ""),
            "duplicate_of": (qq or {}).get("duplicate_of", ""),
            "metadata_hold": identity_error(qq) or "",
            "artifact_identity_hold": pdf_title_error(
                pdf, s.get("citation", (qq or {}).get("citation", ""))
            )
            if pdf
            else "PDF not cached; inspect non-PDF adapter if applicable",
            "cached_artifacts": json.dumps([str(p) for p in files]),
            "library_path": s.get("library_path", ""),
            "url": s.get("url", ""),
            "benchmark_tier": s.get("benchmark_tier", ""),
            "active_ev": sum(r["review_state"] != "dropped" for r in ee),
            "active_planting_ev": sum(
                r["review_state"] != "dropped"
                and r["suitability_family_id"] == "forest_restoration__active_planting"
                for r in ee
            ),
            "families": json.dumps(sorted({r["suitability_family_id"] for r in ee})),
            "human_history_records": sum(x["source_id"] == sid for x in hist),
            "inspection_status": "existing records reconciled; full source inventory pending unless covered in inspected_source_inventory.json",
        }
    )
for item in inv:
    canonical = item["duplicate_of"] or item["source_id"]
    item["canonical_source_id"] = canonical
    item["canonical_cached_artifacts"] = json.dumps(
        [str(p) for c in CACHES for p in c.glob(canonical + ".*") if p.is_file()]
    )
    if item["duplicate_of"]:
        item["artifact_identity_hold"] = (
            "duplicate source identity; reuse canonical artifact, do not count additional vote"
        )
writecsv("source_inventory.csv", inv)
writecsv(
    "search_protocol_existing.csv",
    [
        r
        for r in rows("schema/registers/SRCH_search_register.csv")
        if r["nbs_id"] == "forest_restoration" and r["table"] == "T4"
    ],
)
writecsv(
    "queue_existing.csv",
    [
        r
        for r in queue
        if "forest_restoration" in r["nbs_id"].split("|")
        and "T4" in r["tables"].split("|")
    ],
)
active = [r for r in fr if r["review_state"] != "dropped"]
dump(
    "summary.json",
    {
        "all_ev": len(fr),
        "active_ev": len(active),
        "active_by_family": dict(
            collections.Counter(r["suitability_family_id"] for r in active)
        ),
        "active_by_role": dict(collections.Counter(r["use_role"] for r in active)),
        "active_reviewer_ok_true": sum(
            r["reviewer_ok"].lower() == "true" for r in active
        ),
        "review_history_records": len(hist),
        "review_history_unique_ev": len({r["evidence_id"] for r in hist}),
        "decision_paths_existing": [str(p) for p in decision_paths if p.exists()],
        "source_inventory_count": len(inv),
        "source_inventory_metadata_holds": sum(bool(r["metadata_hold"]) for r in inv),
        "source_inventory_nonduplicate_artifact_holds": sum(
            bool(r["artifact_identity_hold"]) and not r["duplicate_of"] for r in inv
        ),
        "duplicate_alias_rows_reuse_canonical": sum(
            bool(r["duplicate_of"]) for r in inv
        ),
        "complete_screened_corpus_denominator": None,
        "quality_weighted_support": None,
        "ruleset": "v1.8.0",
        "scope": "forest_restoration structural_suitability and operational_risk; sibling families retained separately; no approvals or progress stages changed",
    },
)
print(json.dumps(json.loads((OUT / "summary.json").read_text()), indent=2))
