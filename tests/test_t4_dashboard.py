"""Dashboard integration preserves analytical and review boundaries."""

import json
import shutil
import subprocess
from pathlib import Path
import pytest
from nbs_ruralscan.recipe import developer_contract as dc
from nbs_ruralscan.recipe import t4_dashboard as view
from nbs_ruralscan.recipe.developer_view import render_developer_view

ROOT = Path(__file__).resolve().parents[1]
SOC = "agroforestry__cross_family__soil_organic_carbon"


@pytest.fixture(scope="module")
def result():
    return dc.build_contract(ROOT)


def test_completed_source_preserves_human_status(result):
    row = next(r for r in result["contract"]["rows"] if r["rule_id"] == SOC)
    option = row["function_options"][0]
    assert len(option["intervals"]) == 4
    assert not option["completeness"]["missing_continuations"]
    assert option["source_completions"][0]["kind"] == "verified_table_continuation"
    assert "Source table completed" in render_developer_view(result["contract"])
    record = next(
        u
        for u in result["evidence"]
        if u["evidence_id"] == "ev_T4_soc_haile2024_continuation"
    )
    assert record["reviewer_ok"] == "false"


def test_unresolved_partial_option_cannot_be_selected(result, monkeypatch):
    original = dc._options

    def partial(*args, **kwargs):
        options = original(*args, **kwargs)
        for option in options:
            option["completeness"]["status"] = "partial"
        return options

    monkeypatch.setattr(dc, "_options", partial)
    result = dc.build_contract(ROOT)
    row = next(r for r in result["contract"]["rows"] if r["rule_id"] == SOC)
    option = row["function_options"][0]
    pick = {
        "contract_version": dc.VERSION,
        "selections": {
            SOC: {
                "function_id": option["function_id"],
                "function_fingerprint": option["fingerprint"],
                "target_system": "agroforestry__planted_silvoarable",
                "applicability_country": None,
                "applicability_note": "Test",
                "decision_reference": "test",
            }
        },
    }
    with pytest.raises(ValueError, match="Incomplete source function"):
        dc.build_contract(ROOT, selection=pick)


def test_evidence_accounting_keeps_linked_uncompiled_and_dropped_distinct(result):
    page = view._evidence(result)
    assert page.count("<tr data-t4-row ") == len(result["evidence"])
    for lane in ("linked", "uncompiled", "dropped"):
        assert f'data-lane="{lane}"' in page
    assert "ev_T4_soc_haile2024_continuation" in page
    assert "Response function" in page
    assert "Not in a compiled mapping" in page


def test_study_and_global_panels_do_not_promote_partial_or_unpooled_curves(result):
    studies = view._studies(result)
    combined = view._global(result)
    assert "Source table completed" in studies
    assert "high:0.7-0.75" in studies
    assert "Whole-model share" in studies
    assert "Versus hierarchy equal share" in studies
    assert "No approved combined response" in combined
    assert combined.count("Combined compatible studies") == 3
    assert "profile:ev_T4_soc_haile2024_1" not in combined
    assert "not the whole literature corpus" in combined


def test_rules_read_class_policy_and_escape_claim_text(result):
    rules = view._rules(ROOT, result)
    assert "0.75" in rules and "0.9" in rules
    assert "quality-weighted median" in rules
    assert "flat" in rules.lower()
    bad = dict(
        result["evidence"][0],
        quote="<img src=x onerror=bad>",
        relationship='{"direction":"<script>bad</script>"}',
    )
    html = view._claim(bad) + view._source(bad)
    assert "<script>" not in html and "<img " not in html
    assert "&lt;script&gt;" in html and "&lt;img " in html


def test_client_scope_and_stale_snapshot_detection():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node not installed")
    subprocess.run([node, "tests/js/t4_analysis.test.cjs"], cwd=ROOT, check=True)


def test_published_panels_use_existing_dashboard_and_no_review_controls():
    data = json.loads((ROOT / "docs/t4_analysis.json").read_text(encoding="utf-8"))
    assert set(data["panels"]) == set(view.PANELS)
    for panel in data["panels"].values():
        assert "<script" not in panel
        assert "Accept answer" not in panel
    html = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
    assert 'id="t4-analysis"' in html
    assert (
        html.index('id="tab-interrogator"')
        < html.index('id="t4-analysis"')
        < html.index('id="tab-variables"')
    )


def test_soil_compatibility_shows_resolved_depth_and_remaining_limits(result):
    html = view._global(result)
    assert "Soil depth and measurement compatibility" in html
    assert "0–30 cm" in html
    assert "Not established" in html
    assert "Still unresolved" in html


def test_soil_proposal_is_visible_without_becoming_approved(result):
    html = view._global(result)
    assert "Proposed soil inputs — not activated" in html
    assert "Design assumptions, not findings from the papers" in html
    assert "Thickness weighted arithmetic mean" in html


def test_gates_explain_classes_and_legal_unknowns(result):
    html = view._global(result)
    assert "Legal exclusion — local assessment required" in html
    assert "Required legal-mask provenance" in html
    assert "Eligible host" in html
    assert "Mangroves" in html
    assert "No exclusion identified in assessed scope" in html


def test_readiness_display_uses_policy_reference_without_target_selection(result):
    page = view._global(result)
    assert "First-pass implementation scope (criteria plus gates)" in page
    assert "Defined for implementation" in page
    assert "Provisional input assumption" in page
    assert "Next actions and owners" in page
    exported = render_developer_view(result["contract"])
    assert "Approved policy response — target applicability pending" in exported
    assert 'value="Defined for implementation"' in exported


@pytest.mark.parametrize("nbs", ["forest_restoration", "mangrove_restoration"])
def test_pending_recipe_is_inspectable_without_borrowing_agroforestry(nbs):
    result = dc.build_contract(ROOT, nbs=nbs)
    contract = result["contract"]
    assert not contract["run_contract"]["approved_policies"]
    assert "No aggregation selected" in contract["run_contract"]["baseline"]
    assert not contract["run_contract"]["execution_ready"]
    assert result["evidence"]
    dashboard = view.build_dashboard(ROOT, nbs=nbs)
    assert dashboard["nbs"] == nbs
    assert "agroforestry-t4/IMPLEMENTATION" not in dashboard["panels"]["rules"]
    assert "No class-score policy approved" in dashboard["panels"]["rules"]
    assert all(not u["function_ids"] for u in result["evidence"])


def test_empty_core_defaults_to_structural_holds_despite_operational_links():
    result = dc.build_contract(ROOT, nbs="mangrove_restoration")
    assert any(u["linked_mapping_ids"] for u in result["evidence"])
    assert 'value="uncompiled" selected' in view._evidence(result)
    rules = view._rules(ROOT, result)
    assert "Current numerical baseline is weighted linear combination" not in rules
    assert "high maps to 0.75" not in rules


def test_standalone_mangrove_selectable_without_fabricating_t0():
    import json

    dashboard = json.loads((ROOT / "docs/dashboard_data.json").read_text())
    assert "mangrove_restoration" in dashboard["recipes"]
    assert "T4_suitability_mappings" in dashboard["recipes"]["mangrove_restoration"]
    assert "T0_nbs_registry" not in dashboard["recipes"]["mangrove_restoration"]
