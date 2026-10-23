#!/usr/bin/env python3
"""Rebuild the bounded importance audit; does not modify schema or approvals."""

import csv
import hashlib
import html
import json
from pathlib import Path

from nbs_ruralscan.recipe.importance import (
    compare_importance,
    consolidate_importance,
    load_weight_models,
)

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "pipeline/t4_audit/agroforestry/importance_2026-10-21"


def main():
    results = []
    flat = []
    for model in load_weight_models(AUDIT / "source_weight_trees.csv"):
        pdf = ROOT / ".cache/corpus" / (model["source_id"] + ".pdf")
        if (
            pdf.exists()
            and hashlib.sha256(pdf.read_bytes()).hexdigest()
            != model["provenance"]["artifact_sha256"]
        ):
            raise ValueError(f"Source artifact changed: {model['source_id']}")
        result = compare_importance(model)
        result.update({k: model[k] for k in ("model_id", "source_id", "provenance")})
        results.append(result)
        for item in result["variables"]:
            flat.append(
                dict(
                    model_id=model["model_id"],
                    source_id=model["source_id"],
                    label=model["labels"][item["variable"]],
                    **item,
                )
            )
    (AUDIT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    with (AUDIT / "comparison.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flat[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            {**row, "within_group_ratios": json.dumps(row["within_group_ratios"])}
            for row in flat
        )
    with (AUDIT / "nath_concept_mapping.csv").open() as handle:
        mapping = list(csv.DictReader(handle))
    nath = next(r for r in results if r["model_id"] == "nath_2021_table2")
    consolidated = consolidate_importance(nath, mapping)
    (AUDIT / "nath_consolidated.json").write_text(
        json.dumps(consolidated, indent=2) + "\n"
    )
    esc = html.escape
    summary_rows = "".join(
        f"<tr><td>{esc(r['theme'].title())}</td><td>{esc(r['variable'].replace('_', ' '))}</td>"
        f"<td>{r['whole_model_share']:.2%}</td><td>{r['theme_share']:.0%}</td>"
        f"<td>{r['flat_variable_ratio']:.2f}×</td></tr>"
        for r in consolidated
    )
    summary = (
        "<h2>Nath: theme → variable</h2><p>Repeated nutrient/rooting branches and topsoil/subsoil "
        "weights are added. Soil keeps 20% of the full model. Each variable counts once per paper. "
        "Depth-specific suitability classes remain separate; this does not average cutoffs or change runtime weights.</p>"
        "<p>Relative importance below compares each contribution with equal allocation across "
        f"all {len(consolidated)} consolidated variables. Original hierarchy ratios remain in the source matrix below.</p>"
        "<table><thead><tr><th>Theme</th><th>Variable</th><th>Whole-model weight</th>"
        "<th>Share within theme</th><th>Relative to average variable</th></tr></thead><tbody>"
        + summary_rows
        + "</tbody></table>"
    )
    cells = []
    for variable in sorted(
        {r["variable"] for r in flat},
        key=lambda v: (v not in ("soil_ph", "slope", "annual_precipitation"), v),
    ):
        values = [r for r in flat if r["variable"] == variable]
        row = [f"<th>{esc(variable.replace('_', ' '))}</th>"]
        for result in results:
            item = next(
                (r for r in values if r["model_id"] == result["model_id"]), None
            )
            if not item:
                row.append(
                    '<td class="muted">Not included under this variable name</td>'
                )
                continue
            paths = [
                p
                for p in result["paths"]
                if p["variable"] == variable and p["scope"] == item["scope"]
            ]
            details = "".join(
                "<li>"
                + esc(" → ".join(p["path"]))
                + f": printed weight {p['source_weight']:g}; local ratio {p['within_group_ratio']:.2f}×; contribution {p['whole_model_share']:.2%}</li>"
                for p in paths
            )
            row.append(
                f"<td><b>{item['hierarchy_adjusted_ratio']:.2f}×</b><br>Whole-model share: {item['whole_model_share']:.2%}<br>Flat comparison: {item['flat_variable_ratio']:.2f}×<br>Rank: {item['source_importance_rank']} / {result['distinct_variable_scope_count']}<details><summary>Original weights and branches</summary><ul>{details}</ul></details></td>"
            )
        cells.append("<tr>" + "".join(row) + "</tr>")
    headings = "".join(
        f"<th>{esc(r['model_id'].replace('_', ' '))}<br><small>{r['leaf_count']} input paths; {r['distinct_variable_scope_count']} distinct inputs<br><a href='source-pages/{r['source_id']}-p{r['provenance']['page'].split('-')[0]}.png'>Source table</a></small></th>"
        for r in results
    )
    page = (
        """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>T4 variable importance comparison</title>
<style>body{font:16px system-ui;color:#203e34;background:#f5f8f6;margin:32px}p{max-width:1100px;line-height:1.5}table{border-collapse:collapse;width:100%;background:white}th,td{padding:14px;border:1px solid #d6e2dc;text-align:left;vertical-align:top;min-width:210px}th{background:#e2eee8;position:sticky;top:0}td b{font-size:24px}small,.muted{font-size:13px;color:#536a61}details{margin-top:12px}ul{padding-left:18px;font-size:14px}input{padding:12px;width:360px;margin-bottom:16px}.scroll{overflow:auto;max-height:75vh}a{color:#14644b}</style>
<h1>How important was each variable within each study?</h1>
<p><strong>1× = equal-allocation benchmark. 2× = twice that emphasis. 0.5× = half.</strong> For flat models, benchmark is average input weight. For hierarchical models, benchmark splits weight equally at each branch. These ratios describe model emphasis; they do not establish universal ecological importance or change runtime weights.</p>
<p><strong>Read across each row to compare studies.</strong> All original model inputs remain in denominators, including access variables. In the original source matrix, topsoil and subsoil remain separate; the new Nath summary combines their importance. Missing cells mean no matching input in this inventory, not zero importance. Source input names are retained; this page does not approve ontology mappings.</p>
<p><strong>Source differences:</strong> Singh shows both printed relative weights and RF importance; its weight model is attributed to Singh 2022, so avoid an extra independent vote. The original Nath matrix combines repeated additive pH branches within each depth; the two-level summary also combines depths. Haile Tables 3 and 5 disagree: both alternatives shown, neither selected. Singh printed weights total 99%; Haile Table 5 totals 99.9%. Shares are normalised by their actual totals; printed values remain visible.</p>
<p><strong>Ahmad 2018:</strong> SOC receives 20% of a soil-fertility composite weighted at 45.8%: nominal allocation 9.16%. Intermediate reclassification means this is not final-map sensitivity. <a href="source-pages/ahmad_2018-p4.png">Table 1 and Figure 2</a> → <a href="source-pages/ahmad_2018-p8.png">Table 2 and Figure 8</a>.</p>
<p>Haile nutrient subweights: <a href="source-pages/haile_2024-p5.png">Tables 3–4, page 5</a> and <a href="source-pages/haile_2024-p6.png">Table 4 continued, page 6</a>. RF-column shares mean normalised importance, not a measured share of ecological effect.</p>
<p><strong>Still needs review:</strong> resolve Haile's preferred weight set before a settled summary. Agree which model contexts can be pooled before proposing T4 weights. No new extraction approvals are implied. Six columns represent four papers, not six votes. Ahmad 2018 is inventoried separately and is not automatically added to the existing three-paper candidate-weight panel.</p>
<input id="filter" aria-label="Filter variables" placeholder="Filter variables, e.g. slope or soil ph"><div class="scroll"><table><thead><tr><th>Variable</th>"""
        + headings
        + "</tr></thead><tbody>"
        + "".join(cells)
        + """</tbody></table></div>
<p>Flat comparison uses distinct variable/scope inputs after additive consolidation. Nath has 26 paths but 24 distinct inputs. Original paths remain visible; the hierarchy benchmark retains every branch. Rank uses whole-model contribution, with ties sharing rank.</p>
<script>document.querySelector('#filter').addEventListener('input',e=>{for(const row of document.querySelectorAll('tbody tr'))row.hidden=!row.firstElementChild.textContent.toLowerCase().includes(e.target.value.toLowerCase())})</script></html>"""
    )
    page = page.replace(
        '<input id="filter"',
        summary + '<h2>Original source comparison</h2><input id="filter"',
    )
    page = page.replace(
        "document.querySelectorAll('tbody tr')",
        "document.querySelectorAll('.scroll tbody tr')",
    )
    (ROOT / "docs/review/t4-importance-comparison.html").write_text(page)
    print(f"{len(results)} source variants; {len(flat)} variable comparisons")


if __name__ == "__main__":
    main()
