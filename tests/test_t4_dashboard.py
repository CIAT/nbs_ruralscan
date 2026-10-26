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


def test_known_uncompiled_continuation_is_visible_and_not_selectable(result):
    row = next(r for r in result["contract"]["rows"] if r["rule_id"] == SOC)
    option = row["function_options"][0]
    assert len(option["intervals"]) == 2
    assert option["completeness"]["status"] == "partial"
    assert (
        option["completeness"]["missing_continuations"][0]["evidence_id"]
        == "ev_T4_soc_haile2024_continuation"
    )
    assert "Incomplete curve" in render_developer_view(result["contract"])
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
    assert "Incomplete curve" in studies
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
