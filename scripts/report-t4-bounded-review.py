from nbs_ruralscan.recipe.evidence_assessment import assessments
from pathlib import Path
import csv
import json
import html

R = Path(__file__).resolve().parents[1]
A = R / "pipeline/t4_audit/agroforestry/bounded_review_2026-10-21"
m = json.loads((A / "manifest.json").read_text())
E = {
    r["evidence_id"]: r
    for r in csv.DictReader((R / "schema/registers/EV_evidence_register.csv").open())
}

src = {
    r["source_id"]: r
    for r in csv.DictReader((R / "schema/registers/SRC_source_register.csv").open())
}
(A / "direction_assessment.json").write_text(
    json.dumps(assessments(list(E.values()), src), indent=2) + "\n"
)
esc = html.escape
rows = []
for eid in m["new_evidence_ids"]:
    r = E[eid]
    c = json.loads(r["context"])
    rel = json.loads(r["relationship"])
    use = c.get("model_use", {})
    detail = {
        "relationship": rel,
        "source_weights": use,
        "source_context": c,
        "quote": r["quote"],
    }
    rows.append(
        "<tr><td>"
        + esc(r["source_id"])
        + "</td><td>"
        + esc(
            r["variable"].replace("_", " ")
            + (
                " [quarantined: model-use only]"
                if r["review_state"] == "dropped"
                else ""
            )
        )
        + "</td><td>"
        + esc(c["t4_assessment"]["scope"].replace("_", " "))
        + "</td><td>"
        + esc(rel.get("direction", "No single numeric direction"))
        + "</td><td>"
        + esc(str(c.get("calibration_hold") or c["review_needed"]))
        + "<details><summary>Source claim, weights and review details · p"
        + esc(r["page"])
        + "</summary><pre>"
        + esc(json.dumps(detail, indent=2, ensure_ascii=False))
        + "</pre><small>"
        + esc(eid)
        + "</small></details></td></tr>"
    )
summary = "".join(
    "<tr><td>"
    + esc(sid)
    + "</td><td>"
    + str(len(d["new_evidence_ids"]))
    + "</td><td><details><summary>Reviewed tables and remaining issues</summary><pre>"
    + esc(json.dumps(d["review"], indent=2, ensure_ascii=False))
    + "</pre></details></td></tr>"
    for sid, d in sorted(m["sources"].items())
)
page = (
    """<!doctype html><meta charset="utf-8"><title>T4 bounded evidence review</title><style>body{font:16px system-ui;margin:35px;color:#18372e;background:#f6faf8}table{border-collapse:collapse;width:100%;background:white}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #cddbd5;padding:12px}th{position:sticky;top:0;background:#dfeee6}pre{white-space:pre-wrap;font:13px system-ui;max-width:850px}input{padding:12px;width:65%;margin:15px 0}summary{cursor:pointer;color:#075e45}li{margin:8px 0}</style><h1>T4: bounded evidence re-review</h1><p>16 sources reviewed · 53 staged records (52 active pending; 1 quarantined) · no new literature search. Existing approval states preserved. New records do not authorize executable suitability curves.</p><h2>Decisions still needed</h2><ul><li>Ahmad 2018: existing canopy-cover record describes NDVI. Review replacement and retire incorrect mapping.</li><li>Haile: Table 3 and Table 5 weights disagree. No settled importance weight emitted. pH classes still conflict.</li><li>Nath: source slope stops at 44°; existing unbounded extension needs correction. Other class gaps/overlaps remain explicit.</li><li>Castle / Wotłolan / Mushtaq: species-selection or crop envelopes cannot automatically become general agroforestry rules.</li><li>WOCAT: observed slopes are context, not cutoffs; rootstock routing needs correction.</li><li>Ahmad 2020: six soil properties retain directions and nested weights in inventory, but lack safe canonical mappings. Categorical exclusions remain inventory-only pending exact claim-specific provenance.</li><li>Tea host mask remains Pete’s design decision; coffee/cocoa paper does not establish tea suitability.</li></ul><h2>New records: one review table</h2><p>Direction tells how suitability changes. It does not establish numeric cutoffs. Source weights are reported importance within each paper, not default runtime weights.</p><input id="search" placeholder="Filter by paper, variable, scope or issue"><table id="records"><thead><tr><th>Paper</th><th>Variable</th><th>Applies to</th><th>Direction</th><th>What needs review / source details</th></tr></thead><tbody>"""
    + "".join(rows)
    + """</tbody></table><h2>Coverage: all 16 sources</h2><table><tr><th>Source</th><th>New pending records</th><th>Source inventory</th></tr>"""
    + summary
    + """</table><script>document.getElementById('search').oninput=function(){const q=this.value.toLowerCase();document.querySelectorAll('#records tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))}</script>"""
)
(R / "docs/review/t4-bounded-review.html").write_text(page)
