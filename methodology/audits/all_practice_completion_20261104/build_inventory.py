"""Read-only register inventory; writes snapshots, never stamps pipeline progress."""

import csv
import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / "current_inventory"
OUT.mkdir(exist_ok=True)
paths = [
    "pipeline/progress_ledger.csv",
    "pipeline/acquisition_queue.csv",
    "schema/registers/EV_evidence_register.csv",
    "schema/registers/SRC_source_register.csv",
    "schema/registers/FAM_family_registry.csv",
    "schema/registers/XW_target_crosswalk.csv",
    "schema/registers/SRCH_search_register.csv",
]


def read(p):
    return list(csv.DictReader((ROOT / p).open()))


L, Q, E, S, F, X, H = map(read, paths)
active = [e for e in E if e["review_state"] != "dropped"]
src = {s["source_id"]: s for s in S}
bysrc = defaultdict(list)
for e in E:
    bysrc[e["source_id"]].append(e)
route = defaultdict(set)
for x in X:
    route[x["ev_variable"]].add(x["target_table"])


def eligible(e, t):
    return (
        e["use_role"] == "structural_suitability"
        if t == "T4"
        else (e["use_role"] == "asset_vulnerability" and t == "T3")
        or (e["use_role"] == "nbs_effect" and t in route[e["variable"]])
    )


def write(name, rows):
    if not rows:
        return
    with (OUT / name).open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


fams = {(f["nbs_id"], f["suitability_family_id"]) for f in F} | {
    (e["nbs_id"], e["suitability_family_id"]) for e in E
}
rows = []
for n, f in sorted(fams):
    for t in ["T4", "T3", "T6"]:
        ev = [
            e
            for e in active
            if e["nbs_id"] == n and e["suitability_family_id"] == f and eligible(e, t)
        ]
        led = [
            x for x in L if x["nbs_id"] == n and x["family"] == f and x["table"] == t
        ]
        ff = [x for x in F if x["nbs_id"] == n and x["suitability_family_id"] == f]
        rows.append(
            dict(
                nbs_id=n,
                family=f,
                table=t,
                spatial_product_type="|".join(
                    sorted({x["spatial_product_type"] for x in ff})
                ),
                active_routed_units=len(ev),
                sources=len({x["source_id"] for x in ev}),
                reviewer_ok=sum(x["reviewer_ok"] == "true" for x in ev),
                awaiting_review_flag=sum(x["reviewer_ok"] != "true" for x in ev),
                practice_scope=sum(
                    x["claim_scope"] == "practice_technology" for x in ev
                ),
                crop_scope=sum(x["claim_scope"] == "crop_specific" for x in ev),
                species_scope=sum(x["claim_scope"] == "species_specific" for x in ev),
                ledger_categories="|".join(x["category"] for x in led),
                ledger_states=json.dumps(
                    [
                        {
                            k: x[k]
                            for k in [
                                "category",
                                "searched",
                                "screened",
                                "verified",
                                "last_run_id",
                            ]
                        }
                        for x in led
                    ]
                ),
                note="Candidate XW routes only; not synthesis eligibility or completion. Empty family is unassigned, never distributed.",
            )
        )
write("family_table_inventory.csv", rows)
summary = []
for n in sorted({f["nbs_id"] for f in F}):
    d = {"nbs_id": n}
    for t in ["T4", "T3", "T6"]:
        ev = [e for e in active if e["nbs_id"] == n and eligible(e, t)]
        d[t + "_active_routed"] = len(ev)
        d[t + "_reviewer_ok"] = sum(e["reviewer_ok"] == "true" for e in ev)
    summary.append(d)
write("nbs_table_counts.csv", summary)
queue = []
for q in Q:
    s = src.get(q["source_id"])
    ev = bysrc[q["source_id"]]
    if q["status"] not in ["acquired", "pending"] and (
        not s or s["extraction_status"] not in ["pending", "in_progress"]
    ):
        continue
    queue.append(
        dict(
            source_id=q["source_id"],
            nbs_id=q["nbs_id"],
            family=q["family"],
            tables=q["tables"],
            queue_status=q["status"],
            source_status=s["extraction_status"] if s else "unregistered",
            existing_units=len(ev),
            active_units=sum(e["review_state"] != "dropped" for e in ev),
            identity_flag=q["doi_verified"] if q["doi"] else q["title_verified"],
            cache_exists=any(
                (ROOT / ".cache/corpus" / f"{q['source_id']}{ext}").is_file()
                for ext in [".pdf", ".txt", ".md", ".html"]
            ),
            blocker=q["blocker"],
            note=q["note"],
        )
    )
write("source_work_inventory.csv", queue)
manifest = {
    "inputs": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
    "counts": {
        "EV_all": len(E),
        "EV_active": len(active),
        "EV_dropped": len(E) - len(active),
        "FAM_rows": len(F),
        "FAM_unique_families": len({f["suitability_family_id"] for f in F}),
        "SRC": len(S),
        "queue": len(Q),
        "ledger": len(L),
    },
    "SRC_status": dict(Counter(s["extraction_status"] for s in S)),
    "queue_status": dict(Counter(q["status"] for q in Q)),
    "family_table_inventory_rows": len(rows),
    "source_work_inventory_rows": len(queue),
    "limitations": [
        "T3/T6 counts use XW routing candidates, not full synthesis eligibility. Roles, species/crop exclusions, review and comparator gates remain separate.",
        "reviewer_ok is stored flag, not independent reconstruction of human consensus.",
        "Source status swept/complete does not prove whole-source claim accounting.",
        "No ledger stage inferred or updated.",
        "Queue source identity flags not reverified in this read-only inventory.",
    ],
}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
print(summary)
