#!/usr/bin/env python3
"""Rebuild a plain-language comparison from live T4 and its schema policies."""

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with (ROOT / path).open() as f:
        return list(csv.DictReader(f))


def build():
    rows = read("schema/recipes/agroforestry/T4_suitability_mappings.csv")
    sources = {
        r["source_id"]: r for r in read("schema/registers/SRC_source_register.csv")
    }
    policies = read("schema/lookups/t4_numeric_compilation_policy.csv")
    records, review, pools = [], [], []
    for row in rows:
        params = json.loads(row["relationship_params"])
        for profile in params.get("profiles", []):
            scores = []
            for band in profile["intervals"]:
                lo, hi = band["lower"], band["upper"]
                span = (
                    ("[" if band["lower_inclusive"] else "(")
                    + (f"{lo:.6g}" if lo is not None else "−∞")
                    + ", "
                    + (f"{hi:.6g}" if hi is not None else "∞")
                    + ("]" if band["upper_inclusive"] else ")")
                )
                scores.append(
                    dict(
                        range=span,
                        label=band["label"],
                        old_score=band.get("legacy_score"),
                        new_score=band["score"],
                    )
                )
            records.append(
                dict(
                    variable=row["variable"],
                    system=row["suitability_family_id"],
                    profile_id=profile["profile_id"],
                    source_group=profile.get("source_group", "default"),
                    source_id=profile["source_id"],
                    citation=sources.get(profile["source_id"], {}).get(
                        "citation", profile["source_id"]
                    ),
                    unit=profile["unit"],
                    scores=scores,
                    context=profile["context"],
                    pool_status=profile.get("pool_review", ""),
                    source_weight=profile["source_weight"],
                )
            )
        for item in params.get("harmonization", {}).get("review", []):
            review.append(
                dict(
                    variable=row["variable"],
                    system=row["suitability_family_id"],
                    **item,
                )
            )
        pools.extend(params.get("harmonization", {}).get("pools", []))
    holds = [
        dict(evidence_id=p["evidence_id"], reason=p["reason"])
        for p in policies
        if p["action"] == "hold"
    ]
    changed = sum(
        s["old_score"] != s["new_score"] for r in records for s in r["scores"]
    )
    unknown = sum(s["new_score"] is None for r in records for s in r["scores"])
    report = dict(
        profiles=len(records),
        publications=len({r["source_id"] for r in records}),
        bands=sum(len(r["scores"]) for r in records),
        changed_bands=changed,
        unresolved_score_bands=unknown,
        approved_pools=len(pools),
        records=records,
        review=review,
        held_numeric_policies=holds,
    )
    out = ROOT / "pipeline/t4_audit/agroforestry/final_audit/harmonization.json"
    out.write_text(json.dumps(report, indent=2) + "\n")

    def esc(x):
        return html.escape(str(x))

    doc = [
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T4 harmonization — actual evidence</title><style>body{max-width:1050px;margin:30px auto;padding:0 20px;font:16px system-ui;color:#203c30;background:#f4f7f5}p,li{line-height:1.6}details,section{padding:18px;background:white;border:1px solid #d4e0d8;border-radius:8px;margin:14px 0}summary{cursor:pointer;font-weight:650}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:9px;text-align:left;border-bottom:1px solid #dbe6df}a{color:#176447}.scroll{overflow:auto}.note{border-left:4px solid #a87926;padding-left:15px}</style><h1>Agroforestry: what harmonization changes</h1>',
        f"<p><strong>{len(records)} source profiles · {report['bands']} class bands · {changed} scores changed · {unknown} unresolved score band · {len(pools)} approved combined pools</strong></p>",
        "<p>Scores now follow the approved common class convention. Below, “previous score” means the previous compiler’s rank ÷ full-scale maximum—not necessarily a score reported by the paper. Source ranks and cutoffs remain traceable. Slope conversions now retain full precision.</p>",
        '<section><h2>What still needs review?</h2><ul><li><strong>System and context applicability:</strong> no compatible cross-paper pools have yet been assigned in schema. Most multi-paper records are regional, unassigned agroforestry evidence. Their cutoffs are comparable for inspection, but not yet authorized as one universal system response.</li><li><strong>Favourable rainfall above 1,200 mm:</strong> Mushtaq’s retained statement does not identify an ordinal class or calibrated score. The range remains recorded, but its previous score of 1 is now unknown.</li><li><strong>FMNR rainfall:</strong> observed study ranges and spread remain evidence, not an establishment response curve. Harmonization cannot turn those descriptions into cutoffs.</li><li><strong>Class meanings:</strong> marginal→low, good→high and very good→very high use the approved semantic convention. They remain design crosswalks, not measured calibration.</li></ul><p class="note">Engine can combine explicitly approved compatible pools. No automatic pool was invented for these records. Ties and conflicting exclusion claims stay unknown when evaluated.</p></section>',
        "<h2>Actual source profiles</h2><p>Open each profile for every before/after score and its source context. Parentheses exclude endpoints; brackets include them. Shared ambiguous boundaries remain unknown.</p>",
    ]
    for r in records:
        system = (
            "Agroforestry — system applicability unresolved"
            if r["system"].endswith("cross_family")
            else r["system"].replace("agroforestry__", "").replace("_", " ")
        )
        doc.append(
            "<details><summary>"
            + esc(r["variable"].replace("_", " "))
            + " · "
            + esc(
                r["source_id"]
                + (
                    " · " + r["source_group"].replace("_", " ")
                    if r["source_group"] != "default"
                    else ""
                )
            )
            + " · "
            + esc(system)
            + "</summary><p>"
            + esc(r["citation"])
            + "</p><p>Context: "
            + esc(json.dumps(r["context"], ensure_ascii=False))
            + '</p><div class="scroll"><table><tr><th>Range ('
            + esc(r["unit"])
            + ")</th><th>Source class</th><th>Previous score</th><th>Common score</th></tr>"
        )
        for s in r["scores"]:

            def fmt(v):
                return "Unknown — class meaning unresolved" if v is None else f"{v:.4g}"

            doc.append(
                "<tr>"
                + "".join(
                    "<td>" + esc(v) + "</td>"
                    for v in [
                        s["range"],
                        s["label"],
                        fmt(s["old_score"]),
                        fmt(s["new_score"]),
                    ]
                )
                + "</tr>"
            )
        doc.append(
            "</table></div><p>Profile: "
            + esc(r["profile_id"])
            + ". Pooling: system/context compatibility requires review.</p></details>"
        )
    doc.append(
        "<details><summary>Existing source defects still held ("
        + str(len(holds))
        + ")</summary><ul>"
    )
    for h in holds:
        doc.append(
            "<li>"
            + esc(h["evidence_id"])
            + ": "
            + esc(h["reason"].replace("_", " "))
            + "</li>"
        )
    doc.append(
        '</ul><p>See the live T4 review for additional categorical crosswalks and mapping holds; this page reports numeric harmonization.</p></details><p><a href="t4-categorical-tables.html">Open live T4</a> · <a href="t4-harmonization-examples.html">Worked conventions</a></p></html>'
    )
    (ROOT / "docs/review/t4-harmonization-results.html").write_text(
        "\n".join(doc) + "\n"
    )
    print(
        json.dumps(
            {k: v for k, v in report.items() if not isinstance(v, list)}, indent=2
        )
    )


if __name__ == "__main__":
    build()
