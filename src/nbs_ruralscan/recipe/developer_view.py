"""Human-readable view of the generated T4 developer contract.

Presentation only: never select functions, interpolate intervals, or resolve blockers.
"""

from __future__ import annotations

import html
import json
import math


def _text(value: object) -> str:
    return html.escape(str(value if value is not None else "Not specified"))


def _label(value: object) -> str:
    """Readable display labels; identifiers remain unchanged in the contract."""
    raw = str(value if value is not None else "Not specified")
    aliases = {
        "agroforestry__cross_family": "Shared evidence — system not assigned",
        "agroforestry__planted_silvoarable": "Planted trees with annual crops",
        "agroforestry__regeneration_farmland": "Farmland tree regeneration (FMNR)",
        "agroforestry__silvopastoral": "Trees with pasture / livestock",
        "agroforestry__linear_boundary": "Boundary and linear plantings",
        "agroforestry__shaded_perennial": "Shade trees over perennial crops",
        "agroforestry__homegardens_proximity": "Homegardens",
        "ndvi": "Vegetation greenness (NDVI)",
        "soil_ph": "Soil pH",
        "mean_annual_temperature": "Mean annual temperature",
        "source_profile": "Single-study response",
        "harmonized_pool": "Combined compatible studies",
        "selection_required": "Response selection required",
        "suitability_score": "Suitability score",
        "biophysical": "Biophysical conditions",
        "land_cover_vegetation": "Land cover and vegetation",
    }
    return aliases.get(
        raw, raw.removeprefix("agroforestry__").replace("_", " ").capitalize()
    )


def _fields(values: list[tuple[str, object]]) -> str:
    return (
        "<dl>"
        + "".join(
            "<dt>" + _text(name) + "</dt><dd>" + _text(value) + "</dd>"
            for name, value in values
        )
        + "</dl>"
    )


def _dataset(dataset: dict) -> str:
    resolution = dataset.get("native_resolution_m")
    result = (
        "<strong>"
        + _text(dataset.get("dataset_id") or "No dataset selected")
        + "</strong>"
    )
    result += (
        '<p class="muted">'
        + _text(
            str(resolution) + " m"
            if resolution is not None
            else "Resolution not specified"
        )
        + " · "
        + _text(dataset.get("time_period") or "Time period not specified")
        + "</p>"
    )
    if dataset.get("needs_upload"):
        result += '<p class="badge">Local input required</p>'
    result += "<details><summary>Dataset, units and preparation</summary>"
    result += _fields(
        [
            ("Asset / location", dataset.get("asset")),
            ("Band", dataset.get("band")),
            ("Source units", dataset.get("source_unit")),
            ("Required function units", dataset.get("canonical_unit")),
            ("Scale / offset", dataset.get("scale_offset")),
            ("Time aggregation", dataset.get("temporal_reducer")),
            ("Binding", dataset.get("binding_id") or "Recipe fallback"),
        ]
    )
    result += _list(dataset.get("preparation") or [])
    for field in ("prompt", "limitations", "access_validation"):
        if dataset.get(field):
            result += "<p>" + _text(dataset[field]) + "</p>"
    result += "</details>"
    return result


def _host_inputs(branches: dict) -> str:
    if not branches:
        return ""
    result = "<details><summary>Host conditions and required inputs</summary>"
    for name, branch in branches.items():
        result += '<section class="host"><strong>' + _text(_label(name)) + "</strong>"
        spec = branch.get("spec", {})
        result += "<p>" + _text(_label(spec.get("operation", ""))) + "</p>"
        if spec.get("note"):
            result += "<p>" + _text(spec["note"]) + "</p>"
        for variable, dataset in branch.get("inputs", {}).items():
            result += (
                "<details><summary>"
                + _text(_label(variable))
                + (" — local input required" if dataset.get("needs_upload") else "")
                + "</summary>"
                + _dataset(dataset)
                + "</details>"
            )
        result += "</section>"
    return result + "</details>"


def _json(value: object) -> str:
    return "<pre>" + _text(json.dumps(value, indent=2, ensure_ascii=False)) + "</pre>"


def _bound(value: object) -> float | None:
    if not isinstance(value, (int, float, str)):
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _interval_plot(option: dict) -> str:
    intervals = option.get("intervals") or []
    finite = [
        n
        for row in intervals
        for key in ("lower", "upper")
        if (n := _bound(row.get(key))) is not None
    ]
    if not finite:
        return '<p class="muted">No bounded numeric interval available to plot. Read exact parameters below.</p>'
    low, high = min(finite), max(finite)
    span = high - low or max(abs(low) * 0.2, 1)
    left_tail = any(_bound(row.get("lower")) is None for row in intervals)
    right_tail = any(_bound(row.get("upper")) is None for row in intervals)
    low -= span * (0.15 if left_tail else 0.04)
    high += span * (0.15 if right_tail else 0.04)
    if low == high:
        high = low + 1

    def x(value: float) -> float:
        return 34 + (value - low) / (high - low) * 244

    parts = [
        '<svg viewBox="0 0 300 140" role="img" aria-label="Reported suitability intervals; gaps remain unknown">',
        '<path d="M34 12V108H280" fill="none" stroke="#9baeb0"/>',
        '<text x="5" y="18">1</text><text x="5" y="111">0</text>',
    ]
    for row in intervals:
        score = _bound(row.get("score"))
        if score is None or not 0 <= score <= 1:
            continue
        a, b = _bound(row.get("lower")), _bound(row.get("upper"))
        xa, xb, yy = (
            x(a if a is not None else low),
            x(b if b is not None else high),
            108 - score * 94,
        )
        parts.append(
            f'<path d="M{xa:.2f} {yy:.2f}H{xb:.2f}" stroke="#087d72" stroke-width="3" fill="none"/>'
        )
        for pos, bound, closed, direction in (
            (xa, a, row.get("lower_inclusive", False), -1),
            (xb, b, row.get("upper_inclusive", False), 1),
        ):
            if bound is None:
                parts.append(
                    f'<path d="M{pos - direction * 5:.2f} {yy - 4:.2f}L{pos:.2f} {yy:.2f}L{pos - direction * 5:.2f} {yy + 4:.2f}" fill="none" stroke="#087d72"/>'
                )
            else:
                fill = "#087d72" if closed else "white"
                parts.append(
                    f'<circle cx="{pos:.2f}" cy="{yy:.2f}" r="3" stroke="#087d72" fill="{fill}"/>'
                )
    parts += [
        f'<text x="{x(min(finite)):.2f}" y="125" text-anchor="middle">{min(finite):.4g}</text><text x="{x(max(finite)):.2f}" y="125" text-anchor="middle">{max(finite):.4g}</text>',
        f'<text x="150" y="139" text-anchor="middle">{_text(option.get("unit", ""))}</text>',
        "</svg>",
    ]
    return "".join(parts)


def _function(option: dict, selected: bool) -> str:
    intervals = option.get("intervals") or []
    body = (
        '<article class="option"><strong>'
        + _text(_label(option.get("label") or option.get("function_id")))
        + "</strong>"
    )
    body += (
        '<p class="muted">'
        + ("Selected function" if selected else "Available option — not selected")
        + " · "
        + _text(_label(option.get("kind")))
        + "</p>"
    )
    if intervals:
        body += _interval_plot(option)
        body += '<details><summary>Exact intervals and source context</summary><table class="intervals"><thead><tr><th>Input range</th><th>Suitability</th></tr></thead><tbody>'
        for row in intervals:
            a, b = row.get("lower"), row.get("upper")
            start = "[" if row.get("lower_inclusive") and _bound(a) is not None else "("
            end = "]" if row.get("upper_inclusive") and _bound(b) is not None else ")"
            range_text = f"{start}{a if _bound(a) is not None else '−∞'}, {b if _bound(b) is not None else '+∞'}{end}"
            body += (
                "<tr><td>"
                + _text(range_text)
                + "</td><td>"
                + _text(row.get("score") if row.get("score") is not None else "Unknown")
                + "</td></tr>"
            )
        body += "</tbody></table>"
    else:
        body += "<details><summary>Exact function parameters and context</summary>"
    body += (
        _json(
            {
                "function_id": option.get("function_id"),
                "parameters": option.get("parameters", {}),
                "context": option.get("context", {}),
                "evidence_ids": option.get("evidence_ids", []),
            }
        )
        + "</details></article>"
    )
    return body


def _list(values: list) -> str:
    return (
        "<ul>" + "".join("<li>" + _text(v) + "</li>" for v in values) + "</ul>"
        if values
        else ""
    )


def render_developer_view(contract: dict) -> str:
    """Render a self-contained HTML table without modifying the contract."""
    rows = contract.get("rows", [])
    out = [
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T4 developer handoff</title><style>',
        "body{font:16px/1.45 system-ui,sans-serif;color:#183c36;background:#f5f8f7;margin:24px}h1{margin-bottom:4px}p{margin:8px 0}.muted{color:#586b67;font-size:13px}.toolbar{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}input,select{padding:10px;border:1px solid #aabdb7;border-radius:5px;background:white;font:inherit}input{min-width:300px}.scroll{overflow:auto;background:white;border:1px solid #ccdad5}table{border-collapse:collapse;width:100%}dl{font-size:13px;margin:8px 0}dt{font-weight:650}dd{margin:0 0 7px;overflow-wrap:anywhere}.host{border-top:1px solid #ddd;padding:8px 0}th,td{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid #d9e3df}thead th{background:#e2eee8;position:sticky;top:0}th button{font:inherit;font-weight:700;border:0;background:transparent;color:inherit;cursor:pointer;padding:0;text-align:left}td{min-width:110px}.response{min-width:300px;max-width:650px}.options{display:flex;gap:12px;overflow:auto;max-width:650px}.option{min-width:280px;flex:1;border:1px solid #d8e3df;padding:10px;border-radius:5px}.option svg{width:280px;max-width:100%;font:11px system-ui}.option p{margin:4px 0}details{margin:8px 0}summary{cursor:pointer;color:#076c61}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.5 ui-monospace,monospace;max-width:450px}.intervals td,.intervals th{font-size:12px;padding:5px;min-width:0}.badge{display:inline-block;padding:3px 8px;background:#fff0d4;border-radius:4px;font-size:13px}.status{min-width:220px}ul{padding-left:19px;margin:6px 0}code{overflow-wrap:anywhere}.links a{margin-right:18px}footer{margin-top:18px}</style>",
        "<h1>T4 developer handoff</h1><p>"
        + _text(contract.get("version"))
        + " · "
        + _text(_label(contract.get("nbs")))
        + " · Target country: "
        + _text(contract.get("target_country") or "Not selected")
        + "</p>",
        "<p>Choose system, response and dataset before execution. Blocked rows need the listed decisions; conditional rows still need consumer checks. Evidence review does not establish transfer to the target country.</p>",
        '<p class="muted">Plots show exact scored intervals, not fitted curves. Open circles exclude boundaries; filled circles include them. Arrows show unbounded tails truncated for display. Gaps and unscored intervals remain unknown.</p>',
        '<div class="links"><a href="developer_table.csv">Developer CSV</a><a href="developer_contract.json">Full contract JSON</a><a href="inclusion.csv">Study inclusion</a><a href="source_importance.json">Within-study importance</a><a href="IMPLEMENTATION.md">Implementation guide</a></div>',
        "<details><summary>Package summary and evidence filter</summary>"
        + _json(
            {
                "summary": contract.get("summary", {}),
                "evidence_countries": contract.get("evidence_countries", []),
            }
        )
        + "</details>",
        '<div class="toolbar"><label>Find <input id="find" placeholder="Variable, system, dataset or blocker"></label><label>Module <select id="module"><option value="">All</option>',
        "".join(
            "<option>" + _text(m) + "</option>"
            for m in sorted({str(r.get("module", "")) for r in rows})
        ),
        '</select></label><label>Readiness <select id="status"><option value="">All</option>',
        "".join(
            '<option value="'
            + _text(s)
            + '">'
            + _text(s.replace("_", " "))
            + "</option>"
            for s in sorted({r.get("status", "") for r in rows})
        ),
        '</select></label><span id="count" aria-live="polite"></span></div><div class="scroll"><table id="rules"><thead><tr>',
        "".join(
            f'<th><button type="button" data-column="{i}" title="Sort by {label}">{label} ↕</button></th>'
            for i, label in enumerate(
                [
                    "System",
                    "Theme",
                    "Variable group",
                    "Variable / role",
                    "Relationship function",
                    "Dataset",
                    "MCDA weight",
                    "Readiness",
                ]
            )
        ),
        "</tr></thead><tbody>",
    ]
    for row in rows:
        dataset, weight = row.get("dataset", {}), row.get("weight", {})
        options = row.get("function_options") or []
        chosen = row.get("function_id")
        selected = (
            [o for o in options if o.get("function_id") == chosen] if chosen else []
        )
        alternatives = [o for o in options if o not in selected]
        response = "".join(_function(o, True) for o in selected)
        if not selected:
            response = "<strong>No selected function</strong>"
            if alternatives:
                response += (
                    '<p class="muted">Preview only: first available option, not a recommendation.</p>'
                    + _function(alternatives[0], False)
                )
        if len(alternatives) > (0 if selected else 1):
            response += (
                "<details><summary>Compare all "
                + str(len(options))
                + ' options side by side</summary><div class="options">'
                + "".join(_function(o, o in selected) for o in options)
                + "</div></details>"
            )
        response += (
            '<p class="muted">' + _text(_label(row.get("function_type"))) + "</p>"
        )
        data_summary = _dataset(dataset) + _host_inputs(row.get("host_inputs") or {})
        runtime_weight = weight.get("runtime_weight")
        weight_summary = "Runtime: " + _text(
            runtime_weight if runtime_weight is not None else "Not assigned"
        )
        weight_summary += (
            '<p class="muted">Configured default: '
            + _text(weight.get("configured_default"))
            + "</p><details><summary>Weight basis</summary>"
            + _text(weight.get("basis"))
            + "</details>"
        )
        status = row.get("status", "")
        out.append(
            '<tr data-module="'
            + _text(row.get("module", ""))
            + '" data-status="'
            + _text(status)
            + '">'
        )
        cells = [
            _text(_label(row.get("system"))),
            _text(_label(row.get("theme"))),
            _text(_label(row.get("variable_group"))),
            "<strong>"
            + _text(_label(row.get("variable")))
            + "</strong><p>"
            + _text(row.get("unit"))
            + '</p><p class="muted">'
            + _text(row.get("module"))
            + " · "
            + _text(_label(row.get("role")))
            + "</p>",
            response,
            data_summary,
            weight_summary,
            '<span class="badge">'
            + _text(status.replace("_", " "))
            + "</span>"
            + _list(row.get("blockers", []))
            + "<details><summary>Notes and provenance</summary>"
            + _list(row.get("notes", []))
            + _json(
                {
                    "rule_id": row.get("rule_id"),
                    "evidence_ids": row.get("evidence_ids", []),
                }
            )
            + "</details>",
        ]
        for index, cell in enumerate(cells):
            cls = "response" if index == 4 else "status" if index == 7 else ""
            out.append('<td class="' + cls + '">' + cell + "</td>")
        out.append("</tr>")
    out.append("""</tbody></table></div><footer class="muted">Generated from the same developer contract as the machine-readable tables. Source registers remain authoritative. No review decisions are recorded here.</footer><script>
const table=document.querySelector('#rules'), body=table.tBodies[0];
function filter(){const q=document.querySelector('#find').value.toLowerCase(), m=document.querySelector('#module').value, s=document.querySelector('#status').value;let count=0;for(const row of body.rows){row.hidden=Boolean((m&&row.dataset.module!==m)||(s&&row.dataset.status!==s)||!row.textContent.toLowerCase().includes(q));if(!row.hidden)count++;}document.querySelector('#count').textContent=count+' of '+body.rows.length+' rows';}
for(const id of ['find','module','status'])document.getElementById(id).addEventListener(id==='find'?'input':'change',filter);
for(const button of table.querySelectorAll('th button'))button.addEventListener('click',()=>{const i=Number(button.dataset.column),ascending=button.dataset.direction!=='asc';for(const b of table.querySelectorAll('th button')){delete b.dataset.direction;b.parentElement.removeAttribute('aria-sort');}button.dataset.direction=ascending?'asc':'desc';button.parentElement.setAttribute('aria-sort',ascending?'ascending':'descending');[...body.rows].sort((a,b)=>a.cells[i].textContent.localeCompare(b.cells[i].textContent,undefined,{numeric:true})*(ascending?1:-1)).forEach(row=>body.appendChild(row));});filter();
</script></html>""")
    return "".join(out)
