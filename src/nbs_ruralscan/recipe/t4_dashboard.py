"""Read-only T4 analysis panels inside the existing evidence dashboard.

All results come from the developer compiler; no analytical or review mutation.
"""

from collections import Counter, defaultdict
from pathlib import Path
import hashlib

from .developer_contract import (
    build_contract,
    obj,
    read_csv,
    stable_json,
    _package_inputs,
)
from .developer_view import (
    _text,
    _label,
    _list,
    _function,
    _dataset,
    _host_inputs,
)
from .synthesis import TIER_W, BASIS_W, GREY_DISCOUNT

PANELS = ("evidence", "studies", "global", "rules")
STATE_FIELDS = (
    "evidence_id",
    "source_id",
    "variable",
    "suitability_family_id",
    "relationship",
    "context",
    "reviewer_ok",
    "review_state",
    "use_role",
    "claim_scope",
    "quote",
    "page",
)


def evidence_state(units):
    """Comparable with the typed dashboard register, including dropped history."""
    result = {}
    for unit in units:
        row = {key: unit.get(key) or "" for key in STATE_FIELDS}
        for key in ("relationship", "context"):
            row[key] = obj(row[key], {})
        row["reviewer_ok"] = str(row["reviewer_ok"]).lower() == "true"
        result[unit["evidence_id"]] = row
    return result


def _value(value):
    if isinstance(value, dict):
        return (
            "<dl>"
            + "".join(
                "<dt>" + _text(_label(k)) + "</dt><dd>" + _value(v) + "</dd>"
                for k, v in value.items()
            )
            + "</dl>"
        )
    if isinstance(value, list):
        return "; ".join(_value(v) for v in value)
    return _text(value)


def _table(headers, rows):
    head = "".join(
        f'<th><button type="button" data-t4-sort="{i}">{_text(h)} ↕</button></th>'
        for i, h in enumerate(headers)
    )
    return (
        '<div class="t4-scroll"><table><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def _row(cells, system="", **attrs):
    data = {"system": system, **attrs}
    return (
        "<tr data-t4-row "
        + " ".join(f'data-{k}="{_text(v)}"' for k, v in data.items())
        + ">"
        + "".join("<td>" + c + "</td>" for c in cells)
        + "</tr>"
    )


def _claim(unit):
    relationship = obj(unit.get("relationship"), {})
    context = obj(unit.get("context"), {})
    return (
        _value(relationship)
        if relationship
        else '<p class="muted">No encoded response. Read the claim and its scope.</p>'
    ) + (
        "<details><summary>Additional reported values</summary>"
        + _value(context["reported_values"])
        + "</details>"
        if context.get("reported_values")
        else ""
    )


def _source(unit):
    return (
        "<details><summary>Source claim · page "
        + _text(unit.get("page") or "not specified")
        + "</summary><p>"
        + _text(unit.get("citation"))
        + "</p><blockquote>"
        + _text(unit.get("quote"))
        + "</blockquote><p>"
        + _text(unit.get("attribution"))
        + "</p><code>"
        + _text(unit["evidence_id"])
        + "</code></details>"
    )


def _review(unit):
    return (
        "Dropped"
        if unit.get("review_state") == "dropped"
        else "Approved extraction"
        if str(unit.get("reviewer_ok")).lower() == "true"
        else "Unresolved / not approved"
    )


def _evidence(result):
    dispositions = {
        u["evidence_id"]: u["disposition"]
        for u in result["synthesis_report"]["evidence_dispositions"]
    }
    rows, counts = [], Counter()
    for unit in result["evidence"]:
        dropped = unit.get("review_state") == "dropped"
        linked = bool(unit["linked_mapping_ids"])
        lane = "dropped" if dropped else "linked" if linked else "uncompiled"
        counts[lane] += 1
        destination = (
            "Response function"
            if unit["function_ids"]
            else "T4 mapping / operational reference"
            if linked
            else "Not in a compiled mapping"
        )
        rows.append(
            _row(
                [
                    "<strong>"
                    + _text(_label(unit["variable"]))
                    + "</strong><p>"
                    + _text(_label(unit["suitability_family_id"]))
                    + "</p>",
                    _text(_label(unit["source_id"])),
                    "<strong>"
                    + destination
                    + "</strong><p>"
                    + _text(
                        _label(
                            dispositions.get(unit["evidence_id"], "authored_reference")
                        )
                    )
                    + "</p>"
                    + _list(unit["linked_mapping_ids"]),
                    _review(unit)
                    + "<p>"
                    + _text(_label(unit.get("claim_scope")))
                    + "</p>",
                    _claim(unit) + _source(unit),
                ],
                unit["suitability_family_id"],
                lane=lane,
                variable=unit["variable"],
            )
        )
    intro = "<p>Trace every record into a response, mapping or documented hold. Linked references are not necessarily numeric-rule contributors. Approval confirms an extraction; it does not approve geographic transfer.</p>"
    intro += (
        '<label>Show <select data-t4-evidence-lane><option value="linked">Linked to T4 / operational output ('
        + str(counts["linked"])
        + ')</option><option value="uncompiled">Not compiled ('
        + str(counts["uncompiled"])
        + ')</option><option value="dropped">Dropped history ('
        + str(counts["dropped"])
        + ')</option><option value="all">All evidence ('
        + str(len(rows))
        + ")</option></select></label>"
    )
    return intro + _table(
        [
            "Variable / system",
            "Study",
            "Where it went",
            "Review / scope",
            "What the evidence says",
        ],
        rows,
    )


def _study_weights(units):
    seen, out = set(), []
    for unit in units:
        weight = obj(unit.get("context"), {}).get("model_use", {})
        if not weight or stable_json(weight) in seen:
            continue
        seen.add(stable_json(weight))
        info = {
            k: weight[k]
            for k in (
                "method",
                "weight_path_pct",
                "weight_alternatives_pct",
                "weight_conflict_note",
                "weight_pct",
                "page",
                "note",
            )
            if weight.get(k) is not None
        }
        out.append(_value(info))
    return (
        "".join(out)
        or '<p class="muted">No source weighting method recorded for this variable.</p>'
    )


def _studies(result):
    units = [u for u in result["evidence"] if u.get("review_state") != "dropped"]
    groups = defaultdict(list)
    for u in units:
        groups[
            (
                u["variable"],
                u["source_id"],
                u["suitability_family_id"],
                u["claim_scope"],
            )
        ].append(u)
    options = defaultdict(list)
    for row in result["contract"]["rows"]:
        for option in row["function_options"]:
            if option["kind"] == "source_profile":
                for sid in option["source_ids"]:
                    options[(row["variable"], sid)].append(option)
    variables = sorted({u["variable"] for u in units})
    out = [
        "<p>Compare studies side by side. Curves use common suitability scores; raw claims, direction, source weights and methods remain visible. A direction without calibrated cutoffs stays qualitative.</p><label>Variable <select data-t4-study-variable>"
    ]
    out.extend(
        '<option value="' + _text(v) + '">' + _text(_label(v)) + "</option>"
        for v in variables
    )
    out.append('</select></label><div class="t4-study-grid">')
    for (variable, sid, system, scope), members in sorted(groups.items()):
        out.append(
            '<article class="t4-study" data-t4-study data-variable="'
            + _text(variable)
            + '" data-system="'
            + _text(system)
            + '"><h4>'
            + _text(_label(sid))
            + "</h4><p>"
            + _text(_label(system))
            + " · "
            + _text(_label(scope))
            + "</p>"
        )
        matched = [
            o
            for o in options[(variable, sid)]
            if set(o["evidence_ids"]) & {u["evidence_id"] for u in members}
        ]
        out.extend(_function(o, False) for o in matched)
        out.append(
            "<details"
            + ("" if matched else " open")
            + "><summary>Extracted claims and review state ("
            + str(len(members))
            + ")</summary>"
        )
        for unit in members:
            out.append(
                "<section><strong>"
                + _review(unit)
                + "</strong>"
                + _claim(unit)
                + _source(unit)
                + "</section>"
            )
        out.append(
            "</details><details><summary>Weights and method reported in this study</summary>"
            + _study_weights(members)
            + "</details></article>"
        )
    out.append(
        "</div><h4>Relative importance within source models</h4><p>Whole-model share follows the source’s weighting tree. Ratio 1× means equal-share benchmark; 2× means twice that benchmark. Hierarchy-adjusted comparison preserves source groups. These are diagnostics, not runtime weights. Multiple models from the same paper are alternatives, not independent studies. Original source variable names are retained where canonical mapping is unresolved.</p>"
    )
    weight_rows = []
    for model in result["importance"]:
        if model.get("holds"):
            weight_rows.append(
                _row(
                    [
                        _text(_label(model["source_id"])),
                        _text(_label(model["model_id"])),
                        "Held",
                        _list(model["holds"]),
                        "",
                        "",
                        "",
                    ],
                    importance="true",
                )
            )
        for item in model["variables"]:
            weight_rows.append(
                _row(
                    [
                        _text(_label(model["source_id"])),
                        _text(_label(model["model_id"])),
                        _text(_label(item["variable"])),
                        f"{item['whole_model_share']:.1%}",
                        f"{item['flat_variable_ratio']:.2f}×",
                        f"{item['hierarchy_adjusted_ratio']:.2f}×",
                        "Rank "
                        + str(item["source_importance_rank"])
                        + "<details><summary>Source and branch details</summary>"
                        + _value(model["provenance"])
                        + _value(
                            [
                                p
                                for p in model["paths"]
                                if p["variable"] == item["variable"]
                                and p["scope"] == item["scope"]
                            ]
                        )
                        + "</details>",
                    ],
                    importance="true",
                    variable=item["variable"],
                )
            )
    out.append(
        '<p class="muted">Weight-model table spans all systems in the source model; the system selector does not reinterpret those models.</p>'
    )
    out.append(
        "<details><summary>Compare full source weighting models (all variables)</summary>"
    )
    out.append(
        _table(
            [
                "Study",
                "Source model / method",
                "Source variable",
                "Whole-model share",
                "Versus flat equal share",
                "Versus hierarchy equal share",
                "Rank / provenance",
            ],
            weight_rows,
        )
    )
    out.append("</details>")
    return "".join(out)


def _inclusion(row):
    lines = []
    for level, title in (("group", "Group"), ("variable", "Variable")):
        entries = [e for e in row["study_use"] if e["level"] == level]
        for item in entries:
            lane = {
                "reviewed": "with reviewed use evidence",
                "all_recorded": "including pending use evidence",
            }.get(item["review_lane"], _label(item["review_lane"]))
            lines.append(
                f"{title}, {lane}: {item['n']}/{item['N']} studies ({item['percent']}%)"
            )
    return (
        _list(lines)
        + '<p class="muted">Denominator: model-use studies in this module and scope, across systems; not the whole literature corpus or a confidence score.</p>'
    )


def _approved_policy(result):
    out = []
    for policy in result["contract"]["run_contract"].get("approved_policies", []):
        out.append(
            "<h4>Approved first pass: " + _text(policy["output_label"]) + "</h4>"
        )
        out.append(
            "<p>Planted silvoarable only. Weighted average baseline; minimum-factor sensitivity. Land-use eligibility and legal exclusions stay separate, with no score weight. Eligible fraction is retained separately. Missing required scores remain unknown. Regional transfer and dataset checks still required.</p>"
        )
        out.append(
            _table(
                ["Criterion", "Group", "Approved weight", "Function status"],
                [
                    _row(
                        [
                            _text(_label(c["rule_id"].split("__")[-1])),
                            _text(_label(c["variable_group"])),
                            f"{c['weight']:.0%}",
                            "Verified"
                            if c["function_verified"]
                            else "Changed or unavailable — held",
                        ]
                    )
                    for c in policy["criteria"]
                ],
            )
        )
        proposals = [
            _row(
                [
                    _text(_label(c["rule_id"].split("__")[-1])),
                    _text(f"{p['depth_cm'][0]}–{p['depth_cm'][1]} cm"),
                    _text(_label(p["aggregation"])),
                    _text(p["interpretation"]),
                    _text(p["sensitivity"]),
                ]
            )
            for c in policy["criteria"]
            for p in c.get("input_proposals", [])
        ]
        if proposals:
            out.append(
                "<details><summary>Proposed soil inputs — not activated</summary>"
                "<p>Design assumptions, not findings from the papers. Explicit run-manifest selection and input checks are required. Scale each layer, summarize depth, then apply the response. Missing layers remain unknown.</p>"
                + _table(
                    [
                        "Criterion",
                        "Depth",
                        "Summary",
                        "Meaning and limits",
                        "Sensitivity check",
                    ],
                    proposals,
                )
                + "</details>"
            )
        out.append(_list(policy["holds"]))
    return "".join(out)


def _global(result):
    rows = []
    for row in result["contract"]["rows"]:
        pools = [o for o in row["function_options"] if o["kind"] == "harmonized_pool"]
        typed = [o for o in row["function_options"] if o["kind"] == "numeric_threshold"]
        gates = [o for o in row["function_options"] if o["kind"] == "categorical_gate"]
        function = "".join(_function(o, False) for o in pools + typed)
        if gates:
            function = (
                "<strong>Authored host eligibility rule</strong>"
                + _host_inputs(row.get("host_inputs", {}))
                + "<details><summary>Class rules</summary>"
                + _value(gates[0]["parameters"].get("class_map", {}))
                + "</details>"
            )
        if not function:
            function = (
                "<strong>No approved combined response</strong><p>Individual evidence remains available; no universal curve inferred.</p>"
                if row["role"] == "suitability_score"
                else "<strong>"
                + _text(_label(row["role"]))
                + "</strong><p>"
                + _text(_label(row["function_type"]))
                + "</p>"
            )
        function += (
            '<button type="button" data-t4-jump="studies" data-variable="'
            + _text(row["variable"])
            + '">Compare source studies</button>'
        )
        reviews = row.get("soil_input_reviews", [])
        if reviews:
            function += (
                "<details><summary>Soil depth and measurement compatibility</summary>"
                + _table(
                    ["Study", "Source input", "Depth", "Finding", "Still unresolved"],
                    [
                        _row(
                            [
                                _text(_label(r["source_id"])),
                                _text(r["source_dataset"]),
                                _text(
                                    f"{r['depth_cm'][0]}–{r['depth_cm'][1]} cm"
                                    if r["depth_cm"]
                                    else "Not established"
                                ),
                                _text(r["finding"]),
                                _text(r["remaining_limit"]),
                            ]
                        )
                        for r in reviews
                    ],
                )
                + "</details>"
            )
        weight = row["weight"]
        rows.append(
            _row(
                [
                    _text(_label(row["system"])),
                    _text(_label(row["theme"])),
                    _text(_label(row["variable_group"])),
                    "<strong>"
                    + _text(_label(row["variable"]))
                    + "</strong><p>"
                    + _text(row["module"])
                    + " · "
                    + _text(_label(row["role"]))
                    + "</p>",
                    function,
                    _inclusion(row),
                    "Runtime: "
                    + _text(
                        weight.get("runtime_weight")
                        if weight.get("runtime_weight") is not None
                        else (
                            f"Approved first-pass weight: {row['approved_policy']['weight']:.0%}; target transfer pending"
                            if row.get("approved_policy")
                            else "Not assigned"
                        )
                    )
                    + "<p>Configured default: "
                    + _text(weight.get("configured_default"))
                    + "</p><details><summary>Weight basis</summary>"
                    + _text(weight.get("basis"))
                    + "</details>",
                    _dataset(row["dataset"])
                    + (
                        "<details><summary>Verified provider input details and remaining checks</summary>"
                        + _value(row["dataset"]["documented_input"])
                        + "</details>"
                        if row["dataset"].get("documented_input")
                        else ""
                    ),
                    '<span class="badge">'
                    + _text(_label(row["status"]))
                    + "</span>"
                    + _list(row["blockers"])
                    + _list(row["notes"]),
                ],
                row["system"],
                variable=row["variable"],
                module=row["module"],
            )
        )
    return (
        "<p><strong>Full-corpus synthesis — work in progress.</strong> “Global” means no study-country filter. It does not mean every regional response applies worldwide. Only explicitly compatible studies are combined; source options are never silently averaged. Operational feasibility stays separate from M1 suitability.</p><p>Common score: 0–1 relative suitability, not probability. Gaps, unresolved boundaries and absent inputs remain unknown.</p>"
        + _approved_policy(result)
        + _table(
            [
                "System",
                "Theme",
                "Group",
                "Variable / module",
                "Combined rule",
                "Study inclusion",
                "Runtime weighting",
                "Dataset",
                "Readiness",
            ],
            rows,
        )
    )


def _rules(root, result):
    policies = read_csv(root / "schema/lookups/t4_numeric_compilation_policy.csv")
    scores = {}
    for p in policies:
        if p.get("nbs_id") != result["contract"]["nbs"]:
            continue
        for value in p.values():
            if value.startswith("{"):
                policy = obj(value, {})
                if policy.get("class_scores"):
                    scores[stable_json(policy["class_scores"])] = policy["class_scores"]
    out = [
        "<h4>Evidence → responses → compatible synthesis → developer table</h4><ol><li>Read authoritative source and evidence registers. Keep dropped and unresolved records visible in evidence accounting; only eligible reviewed evidence sets compiled responses.</li><li>Separate model use, suitability direction and numeric calibration. Species/crop scope, observed site conditions and operational feasibility keep their recorded roles.</li><li>Convert units and standardize suitability classes using the versioned policy below. Preserve source ranks, gaps, overlaps and explicit unsuitable classes. Low suitability is not exclusion.</li><li>Combine only profiles with approved matching pool, system, context, units and scoring policy. Deduplicate independent origins before weighting. At each interval, take the quality-weighted median; tied median bounds, within-origin conflicts and exclusion disagreements remain unknown.</li><li>Rebuild from the full corpus and compare with audited T4. Dataset binding and target transfer are separate decisions. Publish function options and provenance, never an implicit universal choice.</li></ol>"
    ]
    out.append(
        "<h4>Common class scores loaded from compilation policy</h4>"
        + "".join(_value(s) for s in scores.values())
    )
    out.append(
        "<h4>Weights used to combine evidence</h4><p>Source-quality weight = tier × claim basis × applicable grey-literature discount. These weights reconcile evidence; they are distinct from a variable’s importance in its source model.</p>"
        + _value(
            {
                "Source tier": TIER_W,
                "Claim basis": BASIS_W,
                "Grey-literature structural suitability multiplier": GREY_DISCOUNT[
                    "structural_suitability"
                ],
            }
        )
    )
    out.append(
        "<h4>Variable importance and spatial MCDA</h4><p>Source weights are normalized within each complete sibling group, then multiplied along the source hierarchy to obtain whole-model shares. Additive repeat branches are consolidated by variable and scope. Flat ratio = whole-model share × number of distinct variable/scope inputs. Hierarchy-adjusted ratio = whole-model share ÷ equal-share contribution through the same tree. Missing or conflicting models retain holds; these diagnostics do not set runtime weights.</p><p>Choose one representative per thematic/correlation group before final weights. Current numerical baseline is weighted linear combination with separate gates. Final selected weights sum to one; missing inputs remain unknown, without per-pixel renormalization. Aggregation choice remains explicit because the original minimum-factor design differs.</p>"
    )
    out.append(
        "<h4>Repairing incomplete curves</h4><p>Verified continuations of reviewed source tables can be restored under an explicit, content-pinned correction policy. Source pages and agent verification remain visible; human approval flags and reviewed-study counts do not change. This does not create an independent study vote. A highest reported class below 1 is not automatically a missing class: high maps to 0.75 and very high to 0.9 under the common convention. Unknown thresholds and contradictory classes remain explicit.</p>"
    )
    out.append(
        "<h4>Country and version rules</h4><p>Target country selects dataset bindings. An optional exact study-country filter narrows evidence and recomputes compatible pools; neither approves transfer. This view uses the full corpus. Published developer bundles are pinned snapshots; this dashboard is the single inspection surface. Review decisions stay in QA/QC.</p>"
    )
    base = "https://github.com/CIAT/nbs_ruralscan/blob/main/"
    for label, path in [
        ("Full methodology", "methodology/T4_developer_contract.md"),
        ("Variable importance convention", "methodology/T4_variable_importance.md"),
        (
            "Numeric compilation policy",
            "schema/lookups/t4_numeric_compilation_policy.csv",
        ),
        ("Harmonization logic", "src/nbs_ruralscan/recipe/harmonization.py"),
        ("Developer integration guide", "handoff/agroforestry-t4/IMPLEMENTATION.md"),
    ]:
        out.append(
            '<p><a target="_blank" rel="noopener" href="'
            + base
            + path
            + '">'
            + label
            + "</a></p>"
        )
    return _approved_policy(result) + "".join(out)


def build_dashboard(root):
    root = Path(root)
    result = build_contract(root)
    inputs = _package_inputs(root, "agroforestry") | {"scripts/build-t4-dashboard.py"}
    hashes = {
        p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sorted(inputs)
    }
    return {
        "version": "1",
        "nbs": "agroforestry",
        "work_in_progress": True,
        "snapshot": hashlib.sha256(stable_json(hashes).encode()).hexdigest(),
        "input_hashes": hashes,
        "compiler_version": result["contract"]["version"],
        "summary": result["contract"]["summary"],
        "evidence_state": evidence_state(result["evidence"]),
        "panels": {
            "evidence": _evidence(result),
            "studies": _studies(result),
            "global": _global(result),
            "rules": _rules(root, result),
        },
    }
