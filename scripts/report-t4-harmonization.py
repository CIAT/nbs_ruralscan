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
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T4 harmonization — actual evidence</title><style>body{max-width:1600px;margin:30px auto;padding:0 20px;font:16px system-ui;color:#203c30;background:#f4f7f5}p,li{line-height:1.6}details,section{padding:18px;background:white;border:1px solid #d4e0d8;border-radius:8px;margin:14px 0}summary{cursor:pointer;font-weight:650}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:9px;text-align:left;border-bottom:1px solid #dbe6df}a{color:#176447}.scroll{overflow:auto}.note{border-left:4px solid #a87926;padding-left:15px}#comparison th{background:#e6efe9;vertical-align:top}#comparison td{vertical-align:top}#comparison th button{border:0;background:none;font:inherit;font-weight:650;cursor:pointer;text-align:left;padding:0}#comparison input{display:block;width:100%;box-sizing:border-box;margin-top:8px;padding:6px;border:1px solid #a9beb0;border-radius:4px}#comparison td details{padding:0;border:0;margin:5px 0;font-size:12px}#comparison td details p{max-width:320px}#comparison td small{display:block;color:#51695c;margin-top:5px}#comparison .changed{background:#fff4d8;font-weight:650}.toolbar{display:flex;gap:18px;align-items:center;margin:14px 0}.toolbar button{padding:7px 12px;font:inherit}#comparison{min-width:1150px}#comparison th:nth-child(1){width:11%}#comparison th:nth-child(2){width:12%}#comparison th:nth-child(3){width:17%}#comparison th:nth-child(4){width:14%}#comparison th:nth-child(8){width:16%}</style><h1>Agroforestry: what harmonization changes</h1>',
        f"<p><strong>{len(records)} source profiles · {report['bands']} class bands · {changed} scores changed · {unknown} unresolved score band · {len(pools)} approved combined pools</strong></p>",
        "<p>Scores now follow the approved common class convention. Below, “previous score” means the previous compiler’s rank ÷ full-scale maximum—not necessarily a score reported by the paper. Source ranks and cutoffs remain traceable. Slope conversions now retain full precision.</p>",
        '<details><summary>What still needs review?</summary><ul><li><strong>System and context applicability:</strong> no compatible cross-paper pools have yet been assigned in schema. Most multi-paper records are regional, unassigned agroforestry evidence. Their cutoffs are comparable for inspection, but not yet authorized as one universal system response.</li><li><strong>Favourable rainfall above 1,200 mm:</strong> Mushtaq’s retained statement does not identify an ordinal class or calibrated score. The range remains recorded, but its previous score of 1 is now unknown.</li><li><strong>FMNR rainfall:</strong> observed study ranges and spread remain evidence, not an establishment response curve. Harmonization cannot turn those descriptions into cutoffs.</li><li><strong>Class meanings:</strong> marginal→low, good→high and very good→very high use the approved semantic convention. They remain design crosswalks, not measured calibration.</li></ul><p class="note">Engine can combine explicitly approved compatible pools. No automatic pool was invented for these records. Ties and conflicting exclusion claims stay unknown when evaluated.</p></details>',
        "<h2>Compare all source bands</h2><p>One row per source class. Filter a variable to compare papers together. Click any heading to sort; use its box to filter. Yellow marks a changed score. Parentheses exclude endpoints; brackets include them. Ambiguous shared boundaries stay unknown.</p>",
        '<div class="toolbar"><button id="clear">Clear filters</button><span id="visible-count" role="status"></span></div><div class="scroll"><table id="comparison"><thead><tr>',
    ]
    headings = [
        "Variable",
        "Paper",
        "System / study context",
        "Range (unit)",
        "Source class",
        "Previous score",
        "Common score",
        "Review needed",
    ]
    for index, heading in enumerate(headings):
        doc.append(
            f'<th scope="col" aria-sort="none"><button data-column="{index}" aria-label="Sort by {esc(heading)}">{esc(heading)}</button><input data-column="{index}" aria-label="Filter {esc(heading)}" placeholder="Filter"></th>'
        )
    doc.append("</tr></thead><tbody>")
    for r in sorted(
        records,
        key=lambda item: (item["variable"], item["source_id"], item["source_group"]),
    ):
        system = (
            "System unassigned"
            if r["system"].endswith("cross_family")
            else r["system"]
            .replace("agroforestry__", "")
            .replace("_", " ")
            .capitalize()
        )
        context = r["context"]
        geography = list(
            dict.fromkeys(
                str(context[k])
                for k in ("study_area", "region", "study_country", "aez")
                if context.get(k)
            )
        )
        if r["source_group"] != "default":
            geography.append(r["source_group"].replace("_", " "))
        context_text = "; ".join(geography) or "Study context not specified"
        source_label = r["source_id"].replace("_", " ").title()
        unit = {
            "degrees": "°",
            "degC": "°C",
            "pH_units": "pH",
            "g/kg": "g/kg",
            "mm/year": "mm/year",
        }.get(r["unit"], r["unit"])
        for band in r["scores"]:

            def fmt(value):
                return "Unknown" if value is None else f"{value:.4g}"

            old, current = band["old_score"], band["new_score"]
            review_note = "System/context compatibility"
            if current is None:
                review_note = "Class meaning + context compatibility"
            cells = [
                esc(
                    r["variable"]
                    .replace("_", " ")
                    .capitalize()
                    .replace("Soil ph", "Soil pH")
                ),
                esc(source_label)
                + "<details><summary>Citation</summary><p>"
                + esc(r["citation"])
                + "</p><p>"
                + esc(r["profile_id"])
                + "</p></details>",
                esc(system) + "<small>" + esc(context_text) + "</small>",
                esc(band["range"] + " " + unit),
                esc(band["label"].replace("_", " ").capitalize()),
                esc(fmt(old)),
                esc(fmt(current)),
                esc(review_note),
            ]
            doc.append("<tr>")
            for index, cell in enumerate(cells):
                attr = ' class="changed"' if index == 6 and old != current else ""
                sort = ""
                if index in (5, 6):
                    value = old if index == 5 else current
                    sort = f' data-value="{value if value is not None else ""}"'
                doc.append(f"<td{attr}{sort}>{cell}</td>")
            doc.append("</tr>")
    doc.append("</tbody></table></div>")
    doc.append("""<script>
const table=document.getElementById('comparison'), body=table.tBodies[0];
const filters=[...table.querySelectorAll('thead input')];
let sortColumn=-1, direction=1;
function filterRows(){
 let visible=0;
 for(const row of body.rows){
  row.hidden=!filters.every((input,i)=>row.cells[i].textContent.toLowerCase().includes(input.value.trim().toLowerCase()));
  if(!row.hidden)visible++;
 }
 document.getElementById('visible-count').textContent=visible+' of '+body.rows.length+' source bands';
}
filters.forEach(input=>input.addEventListener('input',filterRows));
table.querySelectorAll('thead button').forEach(button=>button.addEventListener('click',()=>{
 const index=Number(button.dataset.column);
 direction=sortColumn===index?-direction:1;sortColumn=index;
 const rows=[...body.rows];
 rows.sort((a,b)=>{
  const x=a.cells[index],y=b.cells[index];
  if(index===5||index===6){
   if(x.dataset.value==='')return y.dataset.value===''?0:1;
   if(y.dataset.value==='')return -1;
   return direction*(Number(x.dataset.value)-Number(y.dataset.value));
  }
  return direction*x.textContent.localeCompare(y.textContent,undefined,{numeric:true,sensitivity:'base'});
 });
 rows.forEach(row=>body.append(row));
 table.querySelectorAll('th').forEach((th,i)=>th.setAttribute('aria-sort',i===index?(direction===1?'ascending':'descending'):'none'));
}));
document.getElementById('clear').addEventListener('click',()=>{filters.forEach(input=>input.value='');filterRows()});
filterRows();
</script>""")
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
