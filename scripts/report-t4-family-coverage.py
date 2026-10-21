#!/usr/bin/env python3
"""Generate a family-local matrix from current CSV registers and T4."""

import csv
import html
import json
from pathlib import Path
from nbs_ruralscan.recipe.family_coverage import family_coverage

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with (ROOT / path).open() as handle:
        return list(csv.DictReader(handle))


def main():
    sources = {
        s["source_id"]: s for s in read("schema/registers/SRC_source_register.csv")
    }
    rows = family_coverage(
        read("schema/registers/EV_evidence_register.csv"),
        read("schema/recipes/agroforestry/T4_suitability_mappings.csv"),
        sources,
        "agroforestry",
    )
    out = (
        ROOT
        / "pipeline/t4_audit/agroforestry/importance_2026-10-21/family_coverage.json"
    )
    out.write_text(json.dumps(rows, indent=2) + "\n")
    families = sorted({r["family"] for r in rows})
    labels = {
        "cross_family": "System not assigned",
        "planted_silvoarable": "Planted trees with crops",
        "regeneration_farmland": "Regeneration on farmland",
        "silvopastoral": "Trees with grazing",
        "linear_boundary": "Boundary plantings",
        "shaded_perennial": "Shade over perennial crops",
        "homegardens_proximity": "Homegardens",
    }
    esc = html.escape
    body = []
    for variable in sorted({r["variable"] for r in rows}):
        selected = [r for r in rows if r["variable"] == variable]
        visible = any(
            r["mapping_ids"]
            or r["verified_model_use_papers"]
            or r["required_input_for"]
            for r in selected
        )
        cells = []
        for family in families:
            r = next((r for r in selected if r["family"] == family), None)
            if not r:
                cells.append("<td>—</td>")
                continue
            if (
                r["required_input_for"]
                and not r["mapping_ids"]
                and not r["evidence_ids"]
            ):
                details = "".join(
                    "<p>"
                    + esc(
                        d["note"]
                        or "Required input for "
                        + d["parent_variable"].replace("_", " ")
                    )
                    + "</p><small>Used by: "
                    + esc(d["mapping_id"])
                    + "</small>"
                    for d in r["required_input_for"]
                )
                cells.append(
                    "<td><b>Separate required input</b>"
                    + details
                    + "<p>Linked to parent rule; no additional paper vote or suitability weight.</p></td>"
                )
                continue
            rules = "; ".join(r["relationship_types"]) or "No configured rule"
            directions = (
                "; ".join(
                    f"{k.replace('_', ' ')}: {v}"
                    for k, v in r["direction_counts"].items()
                )
                or "Direction not explicitly encoded"
            )
            cells.append(
                f"<td><b>{esc(rules)}</b><br>Evidence papers: {r['evidence_papers']}<br>Human-reviewed: {r['reviewed_papers']}<br>Verified model use: {r['verified_model_use_papers']}<br>Observed-presence papers: {r['observed_presence_papers']}<br>{esc(directions)}<details><summary>Sources and mappings</summary>{esc('; '.join(r['source_ids']))}<p>{esc('; '.join(r['mapping_ids']))}</p><p>Configured weights: {esc(str(r['configured_weights']))}</p></details></td>"
            )
        body.append(
            f'<tr data-core="{str(visible).lower()}"><th>{esc(variable.replace("_", " "))}</th>'
            + "".join(cells)
            + "</tr>"
        )
    headings = "".join(
        "<th>" + esc(labels.get(f.split("__")[-1], f)) + "</th>" for f in families
    )
    page = (
        """<!doctype html><html lang="en"><meta charset="utf-8"><title>T4 family evidence matrix</title><style>body{font:16px system-ui;color:#203e34;background:#f5f8f6;margin:28px}p{max-width:1150px;line-height:1.5}.scroll{overflow:auto;max-height:75vh}table{border-collapse:collapse;background:white}th,td{min-width:220px;padding:14px;vertical-align:top;border:1px solid #d5dfda}th{background:#e1ece6;position:sticky;top:0}input{padding:10px;margin:10px}details{margin-top:10px}</style><h1>T4: evidence by agroforestry system</h1>
<p>Read across to compare systems. Counts stay within assigned system; shared regional evidence is not automatically inherited. “System not assigned” means source applicability still needs a system/context decision. No percentage support shown: this is an evidence inventory, not a complete screened-paper denominator. Counts deduplicate DOI/source identity; secondary-source lineage still requires checking before independent agreement is claimed.</p>
<p>Evidence papers count active general-practice structural records; human-reviewed means at least one retained record for that paper and cell was approved, not that every claim is settled. Verified model use is separate source-checked metadata. Direction counts require explicit encoding and do not create numeric curves. Dropped, crop/species and soft scenario evidence stay outside these general-practice counts. Configured crop-host rules remain visible independently.</p>
<p>Boundary plantings require two distinct inputs: <strong>land cover</strong> describes the host land use; <strong>field-boundary zone</strong> identifies placement geometry and a locally justified buffer. Boundary geometry is not a land-cover class. Other required inputs are likewise shown separately, without duplicating evidence votes.</p>
<p><strong>Configured does not mean ready everywhere:</strong> piecewise rules can require explicit regional profile selection; categorical rules require their dataset inputs. No new weight or applicability approval follows from this matrix.</p>
<p><a href="t4-importance-comparison.html">Study importance matrix</a> · <a href="t4-candidate-weights.html">Approved comparison baseline and sensitivity</a>. These importance comparisons remain regional; they have not been assigned as weights to each system.</p>
<input id="search" aria-label="Filter variables" placeholder="Filter variable"><label><input id="all" type="checkbox">Include evidence-only variables without configured rules or verified model use</label><div class="scroll"><table><thead><tr><th>Variable</th>"""
        + headings
        + "</tr></thead><tbody>"
        + "".join(body)
        + """</tbody></table></div><script>function filter(){for(const r of document.querySelectorAll('tbody tr'))r.hidden=(!document.querySelector('#all').checked&&r.dataset.core!=='true')||!r.firstElementChild.textContent.toLowerCase().includes(document.querySelector('#search').value.toLowerCase())}document.querySelector('#search').oninput=filter;document.querySelector('#all').onchange=filter;filter();</script></html>"""
    )
    (ROOT / "docs/review/t4-family-coverage.html").write_text(page)
    print(f"{len(rows)} family-variable cells; {len(families)} system columns")


if __name__ == "__main__":
    main()
