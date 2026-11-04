"""Expose source claims independently of numeric compilation eligibility.

This view reports stored evidence, not inferred directions or executable rules.
"""
import html
import json
from collections import Counter, defaultdict


def _obj(value):
    if isinstance(value, dict):
        return value
    return json.loads(value) if value else {}


def relationship_signals(row):
    rel = _obj(row.get("relationship"))
    direction = rel.get("direction", "")
    stated_direction = bool(direction and direction not in {"unclear", "not_reported", "unknown"})
    # Detect stored source classes without interpreting their numeric/categorical meaning.
    classes = any(
        value not in (None, "", [], {})
        and ("class" in key or key in {"thresholds", "very_high", "high", "moderate",
                                     "very_good_code", "good_codes", "required_cover", "gate"})
        for key, value in rel.items()
    )
    return {"source_direction": direction, "has_stated_direction": stated_direction,
            "has_source_classes": classes,
            "source_shape": rel.get("source_shape", rel.get("shape", ""))}


def build_catalogue(evidence, dispositions, mappings):
    """Account for every non-dropped structural claim, including species/crop lanes."""
    dispositions = {r["evidence_id"]: r for r in dispositions}
    links = defaultdict(list)
    for row in mappings:
        ids = row.get("evidence_ids") or []
        if isinstance(ids, str):
            ids = json.loads(ids)
        for eid in ids:
            links[eid].append(row.get("mapping_id", row.get("rule_id")))
    records = []
    for row in evidence:
        if row.get("use_role") != "structural_suitability" or row.get("review_state") == "dropped":
            continue
        eid = row["evidence_id"]
        disposition = dispositions.get(eid, {}).get("disposition", "not_accounted")
        signal = relationship_signals(row)
        linked = links[eid]
        focus = not linked and disposition in {
            "selection_only", "qualitative_relationship", "class_or_gate_requires_mapping"
        }
        record = {key: row.get(key, "") for key in (
            "evidence_id", "source_id", "citation", "variable", "suitability_family_id",
            "claim_scope", "evidence_type", "reviewer_ok", "relationship", "context",
            "quote", "page", "locator_type", "locator", "lineage_of",
            "justification_quote", "justification_page",
        )}
        record.update(signal)
        record.update({"compilation_disposition": disposition, "linked_mapping_ids": linked,
                       "focus_review": focus,
                       "visibility_flag": disposition == "selection_only" and bool(
                           signal["has_stated_direction"] or signal["has_source_classes"] or signal["source_shape"]),
                       "runtime_authorization": "None granted by this catalogue"})
        records.append(record)
    assert len({r["evidence_id"] for r in records}) == len(records), "Duplicate evidence IDs"
    return {"summary": {"structural_claims": len(records),
                        "explicitly_linked_claims": sum(bool(r["linked_mapping_ids"]) for r in records),
                        "focus_claims": sum(r["focus_review"] for r in records),
                        "selection_only_with_relationship_content": sum(r["visibility_flag"] for r in records),
                        "scopes": dict(Counter(r["claim_scope"] for r in records))},
            "records": records}


def render_catalogue(catalogue):
    def esc(value):
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False, indent=2)
        return html.escape(value)

    out = ['<!doctype html><html lang="en"><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           '<title>T4 source relationships</title><style>body{font:16px/1.5 system-ui;max-width:1200px;margin:24px auto;padding:0 20px;color:#183c36}article{border:1px solid #ccd9d3;padding:16px;margin:12px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f6f4;padding:12px}summary{cursor:pointer}input{padding:10px;width:65%}.flag{color:#824500}small{overflow-wrap:anywhere}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #ccc;text-align:left}</style>',
           '<h1>T4 source relationships</h1><p><a href="index.html">Developer rules and plots</a> · <a href="relationship_catalogue.json">Download full catalogue</a></p>',
           '<p>Source evidence and compiled rules are separate. This page retains directions, classes and context even when no numeric function can be compiled. Source wording may describe occurrence, adoption or priority rather than suitability: inspect context. No score, cutoff, weight, approval or target transfer is granted here.</p>',
           '<p>Counts are evidence records, not independent-study votes. Species/crop lanes remain separate. Linked means explicit mapping evidence ID, not validated execution. This is a pinned package snapshot.</p>',
           '<table><tr><th>Measure</th><th>Count</th></tr>']
    for key, label in [("structural_claims", "Non-dropped structural claims"),
                       ("explicitly_linked_claims", "Explicitly linked to mappings"),
                       ("focus_claims", "Unlinked selection / qualitative / categorical review"),
                       ("selection_only_with_relationship_content", "Selection-only records with direction, shape or classes")]:
        out.append(f'<tr><td>{label}</td><td>{catalogue["summary"][key]}</td></tr>')
    out += ['</table><p><input id="search" placeholder="Search variable, source, family, direction or evidence ID" aria-label="Search claims"> <label><input type="checkbox" id="focus" style="width:auto"> Focus review only</label></p><p id="count"></p>']
    for r in sorted(catalogue["records"], key=lambda r: (r["variable"], r["source_id"], r["evidence_id"])):
        out.append(f'<article data-focus="{str(r["focus_review"]).lower()}"><h2>{esc(r["variable"])} — {esc(r["source_id"])}</h2>')
        out.append(f'<p>{esc(r["suitability_family_id"])} · {esc(r["claim_scope"])} · Human approval flag: {esc(r["reviewer_ok"])}</p>')
        out.append(f'<p>Compiler: {esc(r["compilation_disposition"])} · Linked mappings: {esc(r["linked_mapping_ids"] or "None")}</p>')
        if r["visibility_flag"]:
            out.append('<p class="flag">Relationship content exists despite selection-only compiler status. Retain for review; do not automatically compile.</p>')
        out.append(f'<p>Source direction wording: <strong>{esc(r["source_direction"] or "Not encoded")}</strong> · Shape: {esc(r["source_shape"] or "Not encoded")}</p>')
        out.append(f'<details><summary>Reported relationship / classes</summary><pre>{esc(_obj(r["relationship"]))}</pre></details>')
        out.append(f'<details><summary>Context, source quote and provenance</summary><p>{esc(r["citation"])}</p><p>Page: {esc(r["page"])} · {esc(r["locator_type"])}: {esc(r["locator"])}</p><pre>{esc(r["quote"])}</pre><pre>{esc(_obj(r["context"]))}</pre><p>Supporting page: {esc(r["justification_page"])}</p><pre>{esc(r["justification_quote"])}</pre><p>Lineage: {esc(r["lineage_of"])}</p></details><small>{esc(r["evidence_id"])}</small></article>')
    out.append('''<script>const cards=[...document.querySelectorAll('article')];function filter(){const q=document.getElementById('search').value.toLowerCase();const focus=document.getElementById('focus').checked;let n=0;for(const c of cards){c.hidden=!(c.textContent.toLowerCase().includes(q)&&(!focus||c.dataset.focus==='true'));if(!c.hidden)n++;}document.getElementById('count').textContent=n+' claims shown';}document.getElementById('search').addEventListener('input',filter);document.getElementById('focus').addEventListener('change',filter);filter();</script></html>''')
    return "\n".join(out)
