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
                    applicability_review=profile.get("applicability_review", {}),
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
        combined_responses=pools,
    )
    out = ROOT / "pipeline/t4_audit/agroforestry/final_audit/harmonization.json"
    out.write_text(json.dumps(report, indent=2) + "\n")

    def esc(x):
        return html.escape(str(x))

    def pretty(value):
        return (
            value.strip().replace("_", " ").capitalize().replace("Soil ph", "Soil pH")
        )

    def short_range(raw):
        left, right = raw[1:-1].split(", ")

        def number(value):
            return f"{float(value):.3f}".rstrip("0").rstrip(".")

        if left == "−∞":
            return ("≤ " if raw[-1] == "]" else "< ") + number(right)
        if right == "∞":
            return ("≥ " if raw[0] == "[" else "> ") + number(left)
        if left == right:
            return "Exactly " + number(left)
        return number(left) + "–" + number(right)

    variables = list(dict.fromkeys(r["variable"] for r in records))
    if "slope" in variables:
        variables.remove("slope")
        variables.insert(0, "slope")
    doc = [
        """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T4 · Studies side by side</title><style>
*{box-sizing:border-box}body{max-width:1500px;margin:26px auto;padding:0 18px;font:15px system-ui;color:#203c30;background:#f4f7f5}h1{font-size:27px;margin-bottom:8px}p{line-height:1.5}.intro{color:#52695d;margin-top:0}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}.tabs button{font:inherit;padding:9px 14px;border:1px solid #adc4b5;background:white;border-radius:6px;cursor:pointer}.tabs button[aria-pressed=true]{background:#1c6147;color:white;border-color:#1c6147}.matrix-wrap{overflow-x:auto;background:white;border:1px solid #cbdcd1;border-radius:7px}table{width:100%;border-collapse:collapse;table-layout:fixed;min-width:580px}th,td{padding:14px 12px;text-align:left;vertical-align:top;border-bottom:1px solid #dbe6df;border-right:1px solid #e3ebe6}thead th{background:#e8f1eb;font-weight:650}tbody th{background:#f0f5f2;width:130px}thead th:first-child{width:130px}small{display:block;font-size:12px;font-weight:400;color:#52695d;line-height:1.45;margin-top:6px}.range{font-size:19px;font-weight:650;display:block;line-height:1.5}.missing{color:#7a877f;font-size:13px}.previous{color:#855d18}.source-label{font-style:italic}details{font-size:13px;margin-top:8px}summary{cursor:pointer;color:#23634b}details p{font-weight:400;overflow-wrap:anywhere}.foot{color:#52695d;font-size:13px}.review{margin-top:22px;padding:12px 16px;background:#edf2ee;border-radius:6px}.review li{margin:7px 0}a{color:#176447}.unit{font-size:15px;color:#52695d;font-weight:400}h2{font-size:21px}.profile{margin-top:8px}.score{font-weight:400;color:#577063}button:focus-visible,summary:focus-visible{outline:3px solid #c49e39} [hidden]{display:none!important}
</style><h1>Agroforestry: compare studies side by side</h1><p class="intro">Choose a variable. Each column is a study or climate profile; each row aligns classes with the same common score.</p><div class="tabs" aria-label="Choose variable">"""
    ]
    for index, variable in enumerate(variables):
        doc.append(
            f'<button data-variable="{esc(variable)}" aria-pressed="{str(index == 0).lower()}" aria-controls="panel-{esc(variable)}">{esc(pretty(variable))}</button>'
        )
    doc.append("</div>")
    aliases = {
        "medium": "moderate",
        "marginal": "low",
        "good": "high",
        "very_good": "very_high",
    }
    for index, variable in enumerate(variables):
        profiles = [r for r in records if r["variable"] == variable]
        for pool in pools:
            if not pool["pool_id"].endswith("__" + variable):
                continue
            pooled_bands = []
            display_cells = []
            for original in pool["cells"]:
                cell = dict(original)
                previous = display_cells[-1] if display_cells else None
                same = previous and all(
                    previous.get(key) == cell.get(key)
                    for key in ("score", "n_sources", "flags")
                )
                touching = previous and previous["upper"] == cell["lower"] and (
                    previous["upper_inclusive"] or cell["lower_inclusive"]
                )
                if same and touching:
                    previous["upper"] = cell["upper"]
                    previous["upper_inclusive"] = cell["upper_inclusive"]
                else:
                    display_cells.append(cell)
            for cell in display_cells:
                if not cell["n_sources"]:
                    continue
                lo, hi = cell["lower"], cell["upper"]
                raw = (
                    ("[" if cell["lower_inclusive"] else "(")
                    + (f"{lo:g}" if lo is not None else "−∞")
                    + ", "
                    + (f"{hi:g}" if hi is not None else "∞")
                    + ("]" if cell["upper_inclusive"] else ")")
                )
                label = (
                    ("Unresolved: " + ", ".join(cell["flags"]))
                    if cell["score"] is None
                    else (
                        "Both studies contribute"
                        if cell["n_sources"] == 2
                        else "One study contributes"
                    )
                )
                pooled_bands.append(
                    dict(
                        range=raw,
                        label=label,
                        old_score=cell["score"],
                        new_score=cell["score"],
                    )
                )
            profiles.append(
                dict(
                    variable=variable,
                    system=pool["system_id"],
                    profile_id=pool["pool_id"],
                    source_id="Combined scoping response",
                    source_group="default",
                    citation="Conditional India-derived planted-tree/crop scoping prior. Original studies retained; not a validated global envelope. Exact endpoints and disagreement flags remain in T4.",
                    unit=profiles[0]["unit"],
                    scores=pooled_bands,
                    context={"region": "India-derived regional models"},
                    applicability_review={"status": "combined_scoping_prior"},
                )
            )
        levels = sorted(
            {
                b["new_score"]
                for r in profiles
                for b in r["scores"]
                if b["new_score"] is not None
            },
            reverse=True,
        )
        if any(b["new_score"] is None for r in profiles for b in r["scores"]):
            levels.append(None)
        unit = {
            "degrees": "degrees",
            "degC": "°C",
            "pH_units": "pH",
            "g/kg": "g carbon/kg soil",
        }.get(profiles[0]["unit"], profiles[0]["unit"])
        hidden = " hidden" if index else ""
        doc.append(
            f'<section class="panel" id="panel-{esc(variable)}"{hidden}><h2>{esc(pretty(variable))} <span class="unit">· {esc(unit)}</span></h2><div class="matrix-wrap"><table aria-label="{esc(pretty(variable))} study comparison"><thead><tr><th scope="col">Suitability<br><small>Common score</small></th>'
        )
        for r in profiles:
            context = r["context"]
            location = (
                context.get("study_area")
                or context.get("region")
                or context.get("study_country")
                or "Location not specified"
            )
            system = (
                "System unassigned"
                if r["system"].endswith("cross_family")
                else pretty(r["system"].replace("agroforestry__", ""))
            )
            assessment = r.get("applicability_review", {})
            if assessment.get("status") == "establishment_pathway_unresolved":
                system = "Parkland: planting or regeneration unclear"
            elif assessment.get("status") == "generic_secondary_context":
                system = "Generic statement; no shaded-crop assignment"
            elif assessment.get("status") == "conditional_scoping_transfer":
                system = "Planted trees with crops — scoping prior"
            group = (
                ""
                if r["source_group"] == "default"
                else pretty(r["source_group"].split("_", 1)[-1])
            )
            doc.append(
                '<th scope="col">'
                + esc(r["source_id"].replace("_", " ").title())
                + "<small>"
                + esc(location)
                + "</small>"
                + (('<div class="profile">' + esc(group) + "</div>") if group else "")
                + "<small>"
                + esc(system)
                + "</small><details><summary>Source</summary><p>"
                + esc(r["citation"])
                + "</p><p>"
                + esc(r["profile_id"])
                + "</p><p>"
                + esc(assessment.get("decision", ""))
                + "</p></details></th>"
            )
        doc.append("</tr></thead><tbody>")
        for score in levels:
            labels = list(
                dict.fromkeys(
                    aliases.get(
                        b["label"].strip().lower().replace(" ", "_"),
                        b["label"].strip().lower().replace(" ", "_"),
                    )
                    for r in profiles
                    if r["source_id"] != "Combined scoping response"
                    for b in r["scores"]
                    if b["new_score"] == score
                )
            )
            label = (
                "Score unresolved"
                if score is None
                else " / ".join(pretty(label) for label in labels)
            )
            score_text = "—" if score is None else f"{score:g}"
            doc.append(
                '<tr><th scope="row">'
                + esc(label)
                + '<small class="score">'
                + score_text
                + "</small></th>"
            )
            for r in profiles:
                bands = [b for b in r["scores"] if b["new_score"] == score]
                if not bands:
                    doc.append('<td class="missing">Not reported</td>')
                    continue
                doc.append("<td>")
                for band in bands:
                    doc.append(
                        '<div title="Original interval: '
                        + esc(band["range"])
                        + '"><span class="range">'
                        + esc(short_range(band["range"]))
                        + '</span><small class="source-label">'
                        + esc(pretty(band["label"]))
                        + "</small>"
                    )
                    doc.append("</div>")
                doc.append("</td>")
            doc.append("</tr>")
        doc.append(
            '</tbody></table></div><p class="foot">“Not reported” means this class is absent from that profile—not unsuitable. Cutoffs rounded for display; hover for original interval brackets. Shared ambiguous endpoints remain unknown. Original class names appear beneath each range.</p></section>'
        )
    doc.append(
        '<details class="review"><summary>What still needs review?</summary><ul><li>Three conditional planted-tree/crop pools are now compiled: slope (Ahmad + Nath), soil carbon (Ahmad + Nath), pH (Nath + Singh). Combined columns show available-source medians; one-source regions are identified. These India-derived model priors are not globally validated limits.</li><li>Haile: parkland is established, but planted versus regenerated origin is unspecified. Its profiles remain separate.</li><li>Yadav’s temperature groups describe tree species, not agroforestry systems; moved to the species lane.</li><li>Mushtaq’s “favourable above 1,200 mm” is generic secondary discussion, not shaded-perennial evidence, and has no class score.</li><li>FMNR rainfall study ranges describe observations, not a suitability function.</li>'
    )
    for hold in holds:
        doc.append(
            "<li>"
            + esc(hold["evidence_id"])
            + ": "
            + esc(hold["reason"].replace("_", " "))
            + "</li>"
        )
    doc.append(
        '</ul></details><p class="foot">Common scores align the papers’ class labels on one agreed scale; they are not probabilities. <a href="t4-categorical-tables.html">Live T4</a> · <a href="t4-harmonization-examples.html">Worked conventions</a></p>'
    )
    doc.append("""<script>
const buttons=[...document.querySelectorAll('[data-variable]')];
buttons.forEach(button=>button.addEventListener('click',()=>{
 buttons.forEach(other=>other.setAttribute('aria-pressed',String(other===button)));
 document.querySelectorAll('.panel').forEach(panel=>panel.hidden=panel.id!=='panel-'+button.dataset.variable);
}));
</script></html>""")
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
