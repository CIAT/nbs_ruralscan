"""Descriptive paper-level direction counts; never suitability calibration."""

from collections import Counter, defaultdict
import json

from .variable_usage import _object, _paper_key, _study_context

# Display aliases only. No score, threshold or response function is inferred.
DIRECTIONS = {
    "positive": "increasing",
    "higher_is_better": "increasing",
    "increasing": "increasing",
    "negative": "decreasing",
    "lower_is_better": "decreasing",
    "decreasing": "decreasing",
    "optimum_range": "optimum_range",
    "optimum_band": "optimum_range",
    "non_monotonic": "non_monotonic",
}


def direction_usage(evidence, sources, nbs_id="agroforestry"):
    """Count papers once within variable/family/scope/unit/taxon, by review lane.

    Contexts and response reuse remain visible, not silently pooled. Missing or
    unsupported labels are not votes. Quarantine and observed presence cannot vote.
    Reviewed counts never inherit a pending direction from another record.
    """
    groups = defaultdict(lambda: defaultdict(list))
    for unit in evidence:
        if (
            unit.get("nbs_id") != nbs_id
            or unit.get("use_role") != "structural_suitability"
        ):
            continue
        family = unit.get("suitability_family_id", "")
        if family == "cross_family":
            family = nbs_id + "__cross_family"
        key = (
            unit["variable"],
            family,
            unit.get("claim_scope", ""),
            unit.get("unit")
            or _object(unit.get("relationship")).get("unit")
            or _object(unit.get("context")).get("reported_values", {}).get("unit", ""),
            unit.get("taxon", ""),
        )
        groups[key][_paper_key(unit["source_id"], sources)].append(unit)
    result = []
    for key, papers in sorted(groups.items()):
        cells = []
        counts = {lane: Counter() for lane in ("reviewed", "pending_only")}
        for paper, units in sorted(papers.items()):
            lanes = {lane: [] for lane in ("reviewed", "pending", "quarantined")}
            for unit in units:
                lane = (
                    "quarantined"
                    if unit.get("review_state") == "dropped"
                    else "reviewed"
                    if str(unit.get("reviewer_ok", "")).lower() == "true"
                    else "pending"
                )
                rel = _object(unit.get("relationship"))
                raw = rel.get("direction", "")
                observed = rel.get("type") == "observed_presence"
                lanes[lane].append(
                    {
                        "evidence_id": unit["evidence_id"],
                        "reported_direction": raw,
                        "direction": None if observed else DIRECTIONS.get(raw),
                        "exclusion": "Observed site condition" if observed else "",
                        "study_context": _study_context(unit),
                        "response_lineage": unit.get("lineage_of", ""),
                        "model_use_lineage": _object(unit.get("context"))
                        .get("model_use", {})
                        .get("lineage_of", ""),
                    }
                )
            labels = {}
            for lane, rows in lanes.items():
                values = {r["direction"] for r in rows if r["direction"]}
                labels[lane] = (
                    next(iter(values))
                    if len(values) == 1
                    else "conflicting_directions"
                    if values
                    else "not_classified"
                )
            # A reviewed direction takes precedence for counting, but pending
            # alternatives remain visible and never modify the reviewed vote.
            if labels["reviewed"] != "not_classified":
                counts["reviewed"][labels["reviewed"]] += 1
            elif labels["pending"] != "not_classified":
                counts["pending_only"][labels["pending"]] += 1
            cells.append(
                {
                    "paper_key": paper,
                    "source_ids": sorted({u["source_id"] for u in units}),
                    "directions": labels,
                    "records": lanes,
                }
            )
        result.append(
            dict(zip(("variable", "family", "claim_scope", "unit", "taxon"), key))
            | {
                "reviewed_counts": dict(counts["reviewed"]),
                "pending_only_counts": dict(counts["pending_only"]),
                "papers": cells,
            }
        )
    return result


def write_direction_report(root, evidence, sources):
    """Generate review matrix plus complete machine-readable provenance."""
    import html

    rows = direction_usage(evidence, sources)
    destination = (
        root / "pipeline/t4_audit/agroforestry/final_audit/direction_agreement.json"
    )
    destination.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    labels = {
        "increasing": "Higher favoured",
        "decreasing": "Lower favoured",
        "optimum_range": "Middle range favoured",
        "non_monotonic": "Changes direction",
        "conflicting_directions": "Directions differ",
        "not_classified": "No classified direction",
    }
    esc = html.escape
    papers = {p["paper_key"]: p["source_ids"] for row in rows for p in row["papers"]}
    names = sorted(papers, key=lambda p: papers[p][0])
    page = """<!doctype html><meta charset="utf-8"><title>T4: directions across papers</title>
<style>body{font:16px system-ui;color:#243e35;margin:24px}table{border-collapse:collapse}td,th{padding:12px;border:1px solid #ccd9d2;min-width:180px;vertical-align:top}th{background:#e6eee9;position:sticky;top:0}td:first-child,th:first-child{position:sticky;left:0;background:#edf4ef;min-width:240px}small{display:block}details{margin-top:10px}input{padding:10px;width:400px}.scroll{overflow:auto;max-height:75vh}summary{cursor:pointer}</style>
<h1>T4: directions across papers</h1>
<p>Each column is one paper; DOI aliases count once. Each row keeps variable, agroforestry system, claim scope, unit and taxon separate. Starts with slope. Change filter to compare another variable or system; empty paper columns hide automatically. Clear filter to show all.</p>
<p><b>Counts describe reported directions, not independent evidence or pooled suitability.</b> Study settings may differ. Missing units stay unspecified; no conversion is inferred. Reused models and response citations remain visible in record details. Matching directions do not establish matching thresholds. No percentage agreement or runtime weights are inferred.</p>
<p>Reviewed means record-level human approval; later metadata corrections may still need review. Pending-only counts include papers without a classified reviewed direction. Dropped and observed-presence records never vote. Unrecognised labels stay visible for interpretation; missing direction does not mean no relationship.</p>
<input id="filter" value="slope" placeholder="Filter variable, system or scope" aria-label="Filter direction comparison"><div class="scroll"><table><thead><tr><th>Variable / system / scope</th><th>Paper counts</th>"""
    page += "".join(
        "<th>" + esc(", ".join(papers[p]).replace("_", " ")) + "</th>" for p in names
    )
    page += "</tr></thead><tbody>"

    def count_text(counts):
        return (
            "; ".join(f"{labels[k]}: {v}" for k, v in sorted(counts.items()))
            or "None classified"
        )

    for row in rows:
        system = row["family"].removeprefix("agroforestry__").replace("_", " ")
        if system == "cross family":
            system = "System not specified"
        scope = {
            "practice_technology": "Practice-level",
            "crop_specific": "Crop-specific",
            "species_specific": "Species-specific",
        }.get(row["claim_scope"], row["claim_scope"].replace("_", " "))
        heading = " · ".join(
            str(v)
            for v in (
                row["variable"].replace("_", " "),
                system,
                scope,
                row["unit"] or "Unit not recorded",
                row["taxon"],
            )
            if v
        )
        page += (
            '<tr data-search="'
            + esc(heading.lower(), quote=True)
            + '"><td>'
            + esc(heading)
            + "</td><td>Reviewed: "
            + esc(count_text(row["reviewed_counts"]))
            + "<p>Pending only: "
            + esc(count_text(row["pending_only_counts"]))
            + "</p></td>"
        )
        cells = {p["paper_key"]: p for p in row["papers"]}
        for name in names:
            cell = cells.get(name)
            if not cell:
                page += "<td>—</td>"
                continue
            page += '<td data-present="true">'
            for lane in ("reviewed", "pending", "quarantined"):
                records = cell["records"][lane]
                if not records:
                    continue
                page += (
                    "<b>"
                    + esc(lane.capitalize() + ": " + labels[cell["directions"][lane]])
                    + "</b><details><summary>Records and study setting</summary>"
                )
                for record in records:
                    context = "; ".join(
                        f"{k.replace('_', ' ')}: {v}"
                        for k, v in record["study_context"].items()
                    )
                    page += (
                        "<p>"
                        + esc(record["evidence_id"])
                        + "<br>Reported: "
                        + esc(str(record["reported_direction"]) or "not stated")
                        + "<br>"
                        + esc(context)
                        + "<br>"
                        + esc(record["exclusion"])
                    )
                    for field, label in [
                        ("response_lineage", "Response cites"),
                        ("model_use_lineage", "Model reuses"),
                    ]:
                        if record[field]:
                            page += "<br>" + esc(label + ": " + str(record[field]))
                    page += "</p>"
                page += "</details><br>"
            page += "</td>"
        page += "</tr>"
    page += """</tbody></table></div><script>function filter(){
const q=document.querySelector('#filter').value.toLowerCase();
const rows=[...document.querySelectorAll('tbody tr')];
rows.forEach(r=>r.hidden=!r.dataset.search.includes(q));
const headers=[...document.querySelectorAll('thead th')];
headers.forEach((h,i)=>{if(i<2)return;const visible=rows.some(r=>!r.hidden&&r.cells[i].dataset.present==='true');h.hidden=!visible;rows.forEach(r=>r.cells[i].hidden=!visible);});
}document.querySelector('#filter').addEventListener('input',filter);filter();</script>"""
    (root / "docs/review/t4-direction-agreement.html").write_text(
        page, encoding="utf-8"
    )
    return rows
