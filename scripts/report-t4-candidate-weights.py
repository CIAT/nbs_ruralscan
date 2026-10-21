#!/usr/bin/env python3
"""Diagnostic candidate scenarios; never writes runtime/schema weights."""

import csv
import html
import json
from pathlib import Path
from nbs_ruralscan.recipe.importance import candidate_weights

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "pipeline/t4_audit/agroforestry/importance_2026-10-21"


def main():
    models = {
        r["model_id"]: r for r in json.loads((AUDIT / "results.json").read_text())
    }
    output = []
    with (AUDIT / "candidate_scenarios.csv").open() as handle:
        for scenario in csv.DictReader(handle):
            rows = candidate_weights(
                [models[m] for m in scenario["models"].split("|")],
                scenario["variables"].split("|"),
            )
            output.append(dict(**scenario, results=rows))
    (AUDIT / "candidate_results.json").write_text(json.dumps(output, indent=2) + "\n")
    rows = []
    for scenario in output:
        cells = "".join(
            f"<td><b>{r['candidate_weight']:.1%}</b><br>median {r['median_ratio']:.2f}×<br>range {r['minimum']:.2f}–{r['maximum']:.2f}×</td>"
            for r in scenario["results"]
        )
        rows.append(
            f"<tr><th>{html.escape(scenario['scenario'])}<small>{html.escape(scenario['purpose'])}</small></th>{cells}<td>{scenario['results'][0]['source_count']}</td></tr>"
        )
    page = (
        """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>T4 candidate weight review</title>
<style>body{font:17px system-ui;color:#203e34;background:#f5f8f6;margin:36px;max-width:1250px}p{line-height:1.5}table{border-collapse:collapse;background:white;width:100%}th,td{padding:16px;border:1px solid #cfddd5;text-align:left;vertical-align:top}th{background:#e1ece6}small{display:block;font-weight:normal;margin-top:8px;max-width:500px}td b{font-size:24px}a{color:#14644b}</style>
<h1>T4 candidate weights: what changes?</h1>
<p><strong>Exploratory two-variable comparison—not a complete T4 recipe.</strong> Slope and annual rainfall are common inputs across these three regional agroforestry models. Equal baseline: 50% each. Candidate shares normalise median hierarchy-adjusted importance across this selected pair only. Neither weights nor regional response functions are approved for global transfer.</p>
<h2>Candidate matrix</h2><table><thead><tr><th>Comparison</th><th>Slope</th><th>Annual rainfall</th><th>Independent model lineages</th></tr></thead><tbody>"""
        + "".join(rows)
        + """</tbody></table>
<h2>What evidence agrees?</h2><p>In this bounded three-paper panel, slope and annual rainfall each appear in 3/3 models. Source tables favour lower slope (3/3) and higher annual rainfall within reported contexts (3/3). These are source-inspection counts, not new human approvals or full-corpus support percentages. Direction agreement does not prove matching cutoffs. Suitability calibration holds remain separate.</p>
<p>Mean annual temperature appears in Singh and Nath (2/3), both increasing within study context; Haile does not include it. It is retained in the source matrix but omitted from this common-input weight experiment. Soil pH, organic carbon and texture cannot yet be pooled across unspecified versus topsoil/subsoil depth definitions. Wetness, drainage and water proximity measure different things. Access inputs stay outside structural T4; they remain in each original model's importance denominator.</p>
<h2>Haile: what can be resolved?</h2><p>Section 3.2 explicitly describes Table 5 as AHP-derived weights. Recomputing its printed matrix by column normalisation and row means yields 34.55, 29.54, 18.95, 10.48 and 6.48%, closely matching printed 34.5, 29.5, 18.9, 10.5 and 6.5%. Table 3 gives 35, 30, 15, 12 and 8%. No explicit statement establishes that Table 3 was preliminary or superseded. Table 5 is therefore the provisional computed-weight representation; Table 3 stays an alternative. This does not establish which weights generated the published map.</p>
<p><a href="source-pages/haile_2024-p9.png">Haile Table 5 and methods</a> · <a href="source-pages/haile_2024-p4.png">Table 3</a> · <a href="source-pages/haile_2024-p5.png">Table 3 continued</a></p>
<h2>Review once, not row by row</h2><p><strong>Agreed by Pete, 21 October 2026:</strong> keep equal weights as this comparison’s baseline. Candidate results depend strongly on which study enters the pool. Review these as sensitivity scenarios before choosing a default. Family-specific applicability, full variable selection and AOI correlation checks are still required before a complete T4 weighting proposal.</p>
<p><a href="t4-importance-comparison.html">Full source-by-source importance matrix</a>. Nath: Table 2 p11. Singh: Tables 1–2 pp4,8, inherited Singh 2022 weights; variants never create extra votes. Haile: Tables 3–5 pp4–6,9. Regional models span Odisha, Eastern Indian Himalaya and Genale Ethiopia; pooled results are an explicit transfer experiment, not evidence of universal compatibility.</p></html>"""
    )
    (ROOT / "docs/review/t4-candidate-weights.html").write_text(page)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
