"""Relationship-first presentation. Never infers curves from source class values."""
import html
import json
from collections import defaultdict


def obj(value):
    return value if isinstance(value, dict) else json.loads(value or "{}")


def label(value):
    return str(value or "Not stated").replace("agroforestry__", "").replace("_", " ").capitalize()


def reading(row):
    """A conservative reading of recorded direction; source context stays attached."""
    rel = obj(row.get("relationship"))
    direction = rel.get("direction", "")
    variable = label(row.get("variable")).lower()
    excluded = {"observed_presence", "observed_site_description_not_response",
                "mapped_area_statistic_not_response", "importance_weight_not_response",
                "implementation_duration_not_response"}
    if row.get("compilation_disposition") in excluded or rel.get("type") in {
        "accounting_convention", "expert_target_summary", "source_land_capability_context"
    }:
        return "context", "Context only", "Does not establish a suitability response."
    if row.get("variable") == "rootstock_presence":
        return "enabling", "Regeneration material must be present", "Implementation prerequisite; outside core T4 under current project routing."
    if row.get("variable") == "production_gap":
        return "context", "Economic targeting criterion", "Marginal cropland targeting is not an ecological establishment response."
    if row.get("variable") in {"land_cover", "soil_quality_class", "protected_area_status", "built_up_areas"}:
        return "classes", "Eligibility depends on land class or local rules", "A class code is not a continuous suitability scale. Preserve source definitions and legal context."
    if direction in {"increasing", "positive"}:
        return "up", f"Higher {variable} → higher suitability", "Direction reported for the source context."
    if direction in {"decreasing", "negative", "inverse"}:
        return "down", f"Higher {variable} → lower suitability", "Direction reported for the source context."
    if direction == "optimum_range":
        return "optimum", "An intermediate range is preferred", "Keep the source range and its units; no universal optimum inferred."
    if direction == "non_monotonic":
        return "mixed", "Suitability does not change in one direction", "Retain the source's ranked ranges; do not fit a monotonic curve."
    if direction == "better_drained_more_suitable":
        return "classes", "Better-drained soils rank higher", "Source soil classes need compatible dataset definitions."
    if direction == "finer_more_suitable":
        return "classes", "Finer soil textures rank higher", "Source categories are not continuous texture thresholds."
    if rel.get("required_cover"):
        return "classes", f"Requires {rel['required_cover']}", "A host condition, not a graded numeric response."
    if row.get("has_source_classes"):
        return "classes", "Suitability differs between source classes", "Compare the reported classes below; no extra direction or score inferred."
    if direction and direction not in {"unclear", "not_reported", "unknown"}:
        return "conditional", str(direction).replace("_", " "), "Source wording retained; check purpose and context before treating it as suitability."
    return "unknown", "No clear suitability direction recorded", "Variable use alone does not establish a response."


def comparison(rows):
    """Report disagreement, never majority-vote across regional/source contexts."""
    kinds = {reading(r)[0] for r in rows}
    if "up" in kinds and "down" in kinds:
        return "Opposite directions recorded — compare study contexts; do not average."
    directional = kinds & {"up", "down", "optimum", "mixed"}
    if len(directional) > 1:
        return "Different response forms recorded — compare ranges and study contexts."
    if len(directional) == 1:
        return "One direction/form among explicitly directional records; other records may be unresolved. This is not proof of transferable agreement."
    return "Class-based or conditional evidence; no common numeric relationship established."


def render(catalogue):
    esc = lambda x: html.escape(str(x if x is not None else ""))
    groups = defaultdict(list)
    for r in catalogue["records"]:
        groups[(r["variable"], r["suitability_family_id"], r["claim_scope"], r.get("taxon", ""))].append(r)
    out = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
           '<title>T4 — what affects suitability?</title><style>body{font:16px/1.55 system-ui;color:#183c36;background:#f5f8f7;max-width:1200px;margin:32px auto;padding:0 20px}h1{font-size:32px}h2{margin:0;font-size:25px}h3{margin:0 0 6px;font-size:20px}.group{background:white;padding:24px;margin:22px 0;border:1px solid #ccd9d3;border-radius:10px}.relationship{border-top:1px solid #d8e1dc;padding:18px 0}.lead{font-size:21px;font-weight:650}.muted{color:#566b63}.note{background:#eef4f0;padding:12px}.warning{background:#fff2d6;padding:12px}summary{cursor:pointer;color:#076c61}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}table{border-collapse:collapse;width:100%;margin:10px 0}td,th{border:1px solid #d4dfd9;padding:8px;text-align:left}input,select{padding:10px;font:inherit}nav{margin-bottom:24px}small{overflow-wrap:anywhere}.toolbar{position:sticky;top:0;background:#f5f8f7;padding:12px 0;display:flex;gap:12px;flex-wrap:wrap}</style>',
           '<nav><a href="index.html">Numeric rules and plots</a> · <a href="relationship_catalogue.json">Evidence download</a></nav>',
           '<h1>What affects agroforestry suitability?</h1>',
           '<p class="lead">Read the relationship first. Then check where it applies and whether it is ready to use.</p>',
           '<p>Each section keeps one variable, farming system and evidence scope together. Arrows show direction only—not a calibrated curve. Studies may concern different places, measurements or designs.</p>',
           '<div class="toolbar"><input id="search" aria-label="Find a relationship" placeholder="Find slope, rainfall, soil…"><select id="scope" aria-label="Evidence scope"><option value="practice_technology">General practices</option><option value="species_specific">Species evidence</option><option value="crop_specific">Crop evidence</option><option value="">All scopes</option></select><label><input type="checkbox" id="focus"> Unlinked review items only</label></div><p id="count"></p>']
    for (variable, family, scope, taxon), rows in sorted(groups.items()):
        focus = any(r["focus_review"] for r in rows)
        out.append(f'<section class="group" data-scope="{esc(scope)}" data-focus="{str(focus).lower()}"><h2>{esc(label(variable))}</h2><p class="muted">{esc(label(family))} · {esc(label(scope))}{" · " + esc(taxon) if taxon else ""}</p>')
        out.append(f'<p class="note">{esc(comparison(rows))}</p>')
        ordered = sorted(rows, key=lambda r: (reading(r)[0] in {"context", "unknown"}, r["source_id"], r["evidence_id"]))
        # Repeated readings remain one display group, not additional study votes.
        readings = defaultdict(list)
        for r in ordered:
            readings[reading(r)].append(r)
        for (kind, headline, caveat), claims in readings.items():
            unresolved = kind in {"unknown", "context"}
            out.append('<div class="relationship">')
            if unresolved:
                out.append(f'<details><summary>{esc(headline)} — {len(claims)} records</summary>')
            else:
                out.append(f'<h3>{esc(headline)}</h3><p>{esc(caveat)}</p>')
            for r in claims:
                rel = obj(r.get("relationship"))
                context = obj(r.get("context"))
                location = context.get("country") or context.get("region") or context.get("study_context") or "Location not stated here"
                citation = r.get("citation") or r["source_id"]
                out.append(f'<p><strong>{esc(citation)}</strong><br><span class="muted">{esc(location)} · page {esc(r["page"] or "not stated")}</span></p>')
                if r["linked_mapping_ids"]:
                    status = "Linked to an existing mapping. Inspect its numeric option, inputs and target applicability in the rules table."
                elif kind in {"up", "down", "optimum", "mixed"}:
                    status = "Useful for directional interpretation. No executable mapping linked; calibration and applicability need a decision."
                elif kind == "classes":
                    status = "Useful source classes. Dataset/codebook and applicability need checking before a gate or scored rule."
                else:
                    status = "Context or conditional guidance only; no executable relationship established here."
                if r.get("reviewer_ok") not in {True, "true"}:
                    status = "Human review pending. " + status
                if scope != "practice_technology":
                    status += " Applies only to the specified species/crop context; no automatic general-practice transfer."
                out.append(f'<p class="warning"><strong>Use now / next decision:</strong> {esc(status)}</p>')
                classes = rel.get("classes") or rel.get("thresholds")
                if classes:
                    out.append(f'<p class="muted">Units: {esc(rel.get("unit") or "not stated in the relationship field; check source context")}</p>')
                if isinstance(classes, list) and all(isinstance(c, dict) for c in classes):
                    out.append('<table><caption>Source-reported classes — original values, not new scores</caption><thead><tr><th>Class</th><th>Reported value / category</th></tr></thead><tbody>')
                    for c in classes:
                        rest = {k: v for k, v in c.items() if k != "label"}
                        value = "; ".join(f"{label(k)}: {v}" for k, v in rest.items())
                        out.append(f'<tr><td>{esc(c.get("label", "Not labelled"))}</td><td>{esc(value)}</td></tr>')
                    out.append('</tbody></table>')
                elif isinstance(classes, dict):
                    out.append('<table><caption>Source-reported classes</caption>')
                    for k, v in classes.items():
                        out.append(f'<tr><th>{esc(label(k))}</th><td>{esc(v)}</td></tr>')
                    out.append('</table>')
                else:
                    class_keys = [k for k in rel if "class" in k or k in {"required_cover", "gate", "very_high", "high", "moderate", "very_good_code", "good_codes"}]
                    if class_keys:
                        out.append('<ul>')
                        for k in class_keys:
                            out.append(f'<li><strong>{esc(label(k))}:</strong> {esc(rel[k])}</li>')
                        out.append('</ul>')
                out.append(f'<details><summary>Evidence, limits and traceability</summary><p>{esc(r["quote"])}</p><p>{esc(r["justification_quote"])}</p><pre>{esc(json.dumps(context, ensure_ascii=False, indent=2))}</pre><pre>{esc(json.dumps(rel, ensure_ascii=False, indent=2))}</pre><small>{esc(r["evidence_id"])} · Compiler: {esc(r["compilation_disposition"])} · Review flag: {esc(r["reviewer_ok"])} · Lineage: {esc(r["lineage_of"])} · Locator: {esc(r["locator"])} · Mapping: {esc(r["linked_mapping_ids"])}</small></details>')
            if unresolved:
                out.append('</details>')
            out.append('</div>')
        out.append('</section>')
    out.append('''<script>const cards=[...document.querySelectorAll('.group')];function filter(){let n=0;const q=document.getElementById('search').value.toLowerCase(),s=document.getElementById('scope').value,f=document.getElementById('focus').checked;for(const c of cards){c.hidden=!(c.textContent.toLowerCase().includes(q)&&(!s||c.dataset.scope===s)&&(!f||c.dataset.focus==='true'));if(!c.hidden)n++;}document.getElementById('count').textContent=n+' variable × system sections shown. Repeated records are not independent study votes.';}for(const id of ['search','scope','focus'])document.getElementById(id).addEventListener('input',filter);filter();</script></html>''')
    return "\n".join(out)
