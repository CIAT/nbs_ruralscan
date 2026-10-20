"""Plain-language T4 review, generated from the current CSV and provenance."""

from __future__ import annotations
import html
import json

EXPLANATIONS = {
    "slope": "Ground steepness; affects cultivation and establishment.",
    "soil_ph": "Soil acidity or alkalinity; affects nutrient availability.",
    "annual_precipitation": "Rainfall received in a year; a water-availability indicator.",
    "mean_annual_temperature": "Average temperature over a year; a climate suitability indicator.",
    "soil_organic_carbon": "Organic carbon in soil; a soil-condition indicator.",
    "land_cover": "Whether the existing land use can host this agroforestry system.",
    "protected_area_status": "A retained legal exclusion; local legal applicability still needs checking.",
}
MASKS = {
    "managed_forage_without_grazing": "confirmed forage production without grazing",
    "farmland_context": "confirmed agricultural, fallow or former-farmland use",
    "grazing_system_present": "local confirmation of grazing",
    "field_boundary_zone": "mapped field boundaries with a locally justified placement width",
    "coffee_host_fraction": "coffee present (retain its share of pixel area)",
    "cocoa_host_fraction": "cocoa present (retain its share of pixel area)",
    "tea_host_fraction": "tea present (retain its share of pixel area)",
}


def pretty(value):
    return (
        str(value).replace("agroforestry__", "").replace("_", " ").strip().capitalize()
    )


def interval_text(band, unit):
    unit = {
        "pH_units": "pH",
        "degC": "°C",
        "g/kg": "g carbon/kg soil",
        "mm/year": "mm/year",
    }.get(unit, unit)
    low, high = band["lower"], band["upper"]
    if low is None:
        span = ("≤ " if band["upper_inclusive"] else "< ") + f"{high:g}"
    elif high is None:
        span = ("≥ " if band["lower_inclusive"] else "> ") + f"{low:g}"
    else:
        span = f"{low:g}–{high:g}"
    return f"{span} {unit}: {pretty(band['label']).lower()} (score {band['score']:.2g})"


def render(root, read_csv, table, bindings, coverage):
    live = read_csv(root / "schema/recipes/agroforestry/T4_suitability_mappings.csv")
    ontology = {
        r["canonical_variable_id"]: r
        for r in read_csv(root / "schema/registers/VONT_variable_ontology.csv")
    }
    sources = {
        r["source_id"]: r
        for r in read_csv(root / "schema/registers/SRC_source_register.csv")
    }
    datasets = {
        r["dataset_id"]: r for r in read_csv(root / "schema/T1_data_registry.csv")
    }
    evidence = {
        r["evidence_id"]: r
        for r in read_csv(root / "schema/registers/EV_evidence_register.csv")
    }
    rows = []
    for row in live:
        params = json.loads(row["relationship_params"] or "{}")
        scenario = row["is_scenario_candidate"] == "true"
        profiles = params.get("profiles", [])
        family = pretty(row["suitability_family_id"])
        shared = family == "Cross family"
        if shared:
            family = "Shared evidence — family not assigned"
        family = {
            "Planted silvoarable": "Planted trees with crops",
            "Regeneration farmland": "Natural tree regeneration on farmland",
            "Silvopastoral": "Trees with grazing livestock",
            "Linear boundary": "Boundary and linear plantings",
            "Shaded perennial": "Shade trees over perennial crops",
        }.get(family, family)
        crop = params.get("host_crop")
        variable = ontology.get(row["variable"], {}).get(
            "label", pretty(row["variable"])
        )
        if crop:
            variable = pretty(crop) + " host crop"
        explanation = EXPLANATIONS.get(
            row["variable"],
            row["scenario_description"] or pretty(row["suitability_dimension"]),
        )
        details = []
        if profiles:
            for profile in profiles:
                context = (
                    "; ".join(str(v) for v in profile["context"].values())
                    or "Regional context not fully encoded"
                )
                details.append(
                    {
                        "title": pretty(profile["source_id"])
                        + (
                            " · " + pretty(profile["source_group"])
                            if profile["source_group"] != "default"
                            else ""
                        ),
                        "text": context
                        + "\n"
                        + "\n".join(
                            interval_text(b, profile["unit"])
                            for b in profile["intervals"]
                        )
                        + "\n"
                        + profile["applicability_note"],
                        "citation": sources.get(profile["source_id"], {}).get(
                            "citation", ""
                        ),
                        "reference": profile["evidence_id"],
                    }
                )
            rule = (
                "; ".join(
                    interval_text(b, profiles[0]["unit"])
                    for b in profiles[0]["intervals"]
                )
                if len(profiles) == 1
                else f"{len(profiles)} regional responses retained. Open source rules below to compare bands."
            )
            status = "Ready to use after selecting the regional source response. Unreported ranges and conflicting class boundaries stay unknown."
            if shared:
                status += " Family applicability must be chosen explicitly."
            kind = "Numeric suitability"
        elif "class_map" in params:
            allowed = []
            excluded = []
            for code, score in params["class_map"].items():
                label = params.get("class_labels", {}).get(code, code)
                conditions = params.get("class_requirements", {}).get(code, [])
                if score == 1:
                    allowed.append(
                        label
                        + (
                            " with "
                            + " and ".join(MASKS.get(c, pretty(c)) for c in conditions)
                            if conditions
                            else ""
                        )
                    )
                elif score == 0:
                    excluded.append(label)
            rule = "; ".join(allowed) + ". Excludes: " + ", ".join(excluded) + "."
            status = "Host condition only; missing inputs and other land-cover classes stay unknown."
            if crop:
                status += " Combine suitable host crops using OR."
            if params.get("applicable_subpractices"):
                status += (
                    " Covers only "
                    + ", ".join(pretty(x) for x in params["applicable_subpractices"])
                    + "."
                )
            kind = "Existing host system"
        elif scenario:
            rule = row["scenario_label"] + " " + row["scenario_description"]
            status = (
                "Retained investment scenario, not a biophysical suitability score."
            )
            kind = "Investment scenario"
        elif isinstance(params.get("threshold"), (int, float)):
            unit = ontology.get(row["variable"], {}).get("canonical_unit", "")
            rule = (
                (
                    "Exclude above "
                    if not params["above_is_suitable"]
                    else "Exclude below "
                )
                + str(params["threshold"])
                + " "
                + unit
                + "."
            )
            status = "One regional model rule; transfer to other settings needs care."
            kind = "Numeric suitability"
        else:
            rule = "Retained protected-area exclusion for IUCN categories I–II."
            status = "Needs legal category-mask adapter and family-scope review before execution."
            kind = "Legal exclusion"
        for eid in json.loads(row["evidence_ids"] or "[]"):
            if profiles:
                continue
            unit = evidence.get(eid, {})
            details.append(
                {
                    "title": pretty(unit.get("source_id", eid)),
                    "text": "Source quote: "
                    + unit.get("quote", "")
                    + "\nPage: "
                    + unit.get("page", ""),
                    "citation": sources.get(unit.get("source_id"), {}).get(
                        "citation", ""
                    ),
                    "reference": eid,
                }
            )
        data = datasets.get(row["dataset_id"], {})
        details.append(
            {
                "title": "Input data",
                "text": data.get("dataset_name", row["dataset_id"])
                + "\n"
                + data.get("description", "")
                + "\n"
                + data.get("limitations", ""),
                "citation": "",
                "reference": row["mapping_id"],
            }
        )
        rows.append(
            {
                "Family": family,
                "Variable": variable,
                "What the rule says": rule,
                "Use and limits": status,
                "Rule category": kind,
                "explanation": explanation,
                "details": details,
            }
        )
    numeric = sum(r["Rule category"] == "Numeric suitability" for r in rows)
    payload = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Agroforestry · Suitability rules</title><style>
*{box-sizing:border-box}body{font:15px system-ui;color:#1c3a30;background:#f6f8f7;margin:24px}h1{margin-bottom:8px}p{line-height:1.5;max-width:1100px}.muted{color:#54685e}.intro{background:#e9f2ed;padding:12px 18px;border-radius:8px}.toolbar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin:20px 0}button,select,input{font:inherit;padding:7px}button,summary{cursor:pointer}table{width:100%;border-collapse:collapse;background:white}td,th{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #d9e3dc}th{background:#e5eee8}th button{border:0;background:none;font-weight:650;text-align:left;padding:0}th input{display:block;width:100%;min-width:80px;margin-top:8px;border:1px solid #afc3b5;border-radius:4px}td{overflow-wrap:anywhere}td:first-child{width:15%}td:nth-child(2){width:18%}td:nth-child(3){width:37%}td:nth-child(4){width:30%}.help{font-size:13px;color:#52685b;display:block;margin-top:7px}.tag{display:block;font-size:12px;color:#577062;margin-top:6px}details{margin:12px 0}summary{color:#146445;font-weight:600}pre{white-space:pre-wrap;font:14px system-ui;line-height:1.5}.table-wrap{overflow:auto}a{color:#146445}.ref{font:12px monospace;color:#68766d}section{margin:18px 0;padding:14px;border:1px solid #dce5df;border-radius:6px}
</style></head><body><h1>Agroforestry: suitability rules (T4)</h1>
<div class="intro"><p><strong>How to read this:</strong> agroforestry is the overall solution. A <strong>family</strong> groups practices with similar establishment needs (for example, planted silvoarable includes alley cropping and tree intercropping). Each row below describes one variable and how it affects that family.</p><p><strong>Numeric rules</strong> describe rainfall, temperature, soils or slope. <strong>Host conditions</strong> check that suitable existing farmland, pasture or crops are present. A passed host condition does not establish overall suitability. Scores express relative source ranks: 1 is the highest rank, 0 means explicitly unsuitable. They are not probabilities; unknown means the evidence or input does not determine an answer.</p></div>
"""
    page += f"<p><strong>{numeric} numeric suitability rows</strong> · 7 host conditions · 1 retained legal exclusion · 8 investment scenarios. Shared evidence remains separate until family applicability is assigned.</p>"
    page += """<div class="toolbar"><label>Show <select id="category"><option value="core">Suitability, host conditions and exclusions</option><option value="all">All T4 rows</option><option>Numeric suitability</option><option>Existing host system</option><option>Investment scenario</option></select></label><button id="reset">Reset filters</button><span id="count" aria-live="polite"></span></div><p class="muted">Click headings to sort. Type under headings to filter. Open “Source rules and explanation” within a row for numeric bands, source context and input data.</p><div class="table-wrap"><table id="main"><thead></thead><tbody></tbody></table></div>
<details><summary>Still needs resolution — source ambiguities and missing mappings</summary><p>These are retained as evidence, not silently converted into suitability scores.</p>"""
    holds = read_csv(
        root / "pipeline/t4_audit/agroforestry/final_audit/parked_mappings.csv"
    )
    policies = read_csv(root / "schema/lookups/t4_numeric_compilation_policy.csv")
    for p in policies:
        if p["action"] == "hold" and p["evidence_id"] not in {
            h["evidence_id"] for h in holds
        }:
            holds.append(
                {"evidence_id": p["evidence_id"], "reason": pretty(p["reason"])}
            )
    for hold in holds:
        unit = evidence.get(hold["evidence_id"], {})
        page += (
            "<p><strong>"
            + html.escape(
                pretty(unit.get("source_id", ""))
                + " · "
                + ontology.get(unit.get("variable"), {}).get(
                    "label", pretty(unit.get("variable", ""))
                )
            )
            + "</strong>: "
            + html.escape(hold["reason"])
            + "</p>"
        )
    page += """<p>Scenario parameter grids still need a parameter choice. Site observations, study weights and mapped-area percentages are retained in the audit; they cannot define numeric suitability responses.</p><a href="t4-pipeline-audit.html">Every-record audit and unresolved reviews</a></details><details><summary>Developer detail — data bindings and synthetic missing-input check</summary><p>Bindings identify datasets supplying additional host inputs. The synthetic check tests missing-data handling; it is not a pilot run or suitability result.</p>"""
    page += table(
        bindings, ["family", "mask", "variable", "dataset_id", "band", "note"]
    )
    page += (
        "<details><summary>Missing-input diagnostic</summary>"
        + table(coverage, ["family", "dataset_id", "dataset_code", "runtime_status"])
        + "</details></details>"
    )
    page += '<script id="rows" type="application/json">' + payload + "</script>"
    page += """<script>
const rows=JSON.parse(document.getElementById('rows').textContent),keys=['Family','Variable','What the rule says','Use and limits'],filters={};let sortKey='',direction=1;
const head=document.querySelector('#main thead'),body=document.querySelector('#main tbody'),tr=document.createElement('tr');
keys.forEach(key=>{const th=document.createElement('th'),button=document.createElement('button'),input=document.createElement('input');button.textContent=key+' ↕';button.onclick=()=>{direction=sortKey===key?-direction:1;sortKey=key;head.querySelectorAll('th').forEach(t=>t.removeAttribute('aria-sort'));th.setAttribute('aria-sort',direction===1?'ascending':'descending');render()};input.placeholder='Filter…';input.setAttribute('aria-label','Filter '+key);input.oninput=()=>{filters[key]=input.value.toLowerCase();render()};th.append(button,input);tr.append(th)});head.append(tr);
function render(){const category=document.getElementById('category').value;let visible=rows.filter(r=>(category==='all'||(category==='core'?r['Rule category']!=='Investment scenario':r['Rule category']===category))&&keys.every(k=>!filters[k]||r[k].toLowerCase().includes(filters[k])));if(sortKey)visible.sort((a,b)=>direction*a[sortKey].localeCompare(b[sortKey],undefined,{numeric:true}));body.replaceChildren();visible.forEach(r=>{const tr=document.createElement('tr');keys.forEach(k=>{const td=document.createElement('td');td.textContent=r[k];if(k==='Variable'){const help=document.createElement('span');help.className='help';help.textContent=r.explanation;td.append(help)}if(k==='Use and limits'){const tag=document.createElement('span');tag.className='tag';tag.textContent=r['Rule category'];td.append(tag)}if(k==='What the rule says'){const d=document.createElement('details'),s=document.createElement('summary');s.textContent='Source rules and explanation';d.append(s);r.details.forEach(item=>{const h=document.createElement('strong'),p=document.createElement('pre'),cite=document.createElement('p'),ref=document.createElement('span');h.textContent=item.title;p.textContent=item.text;cite.textContent=item.citation;ref.className='ref';ref.textContent=item.reference;const section=document.createElement('section');section.append(h,p,cite,ref);d.append(section)});td.append(d)}tr.append(td)});body.append(tr)});document.getElementById('count').textContent=visible.length+' of '+rows.length+' rows'}
document.getElementById('category').onchange=render;document.getElementById('reset').onclick=()=>{keys.forEach(k=>delete filters[k]);head.querySelectorAll('input').forEach(i=>i.value='');document.getElementById('category').value='core';sortKey='';head.querySelectorAll('th').forEach(t=>t.removeAttribute('aria-sort'));render()};render();
</script></body></html>"""
    return page
