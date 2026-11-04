"""Readiness is artifact presence, not source validation or review approval."""

import csv
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from nbs_ruralscan.schema_tools import review_server as server

ROOT = Path(__file__).resolve().parents[1]


def test_readiness_counts_unique_sources_and_skips_dataset_only(tmp_path, monkeypatch):
    ev = tmp_path / "schema/registers/EV_evidence_register.csv"
    ev.parent.mkdir(parents=True)
    ev.write_text(
        "source_id,use_role,review_state\na,nbs_effect,\na,nbs_effect,\nb,nbs_effect,dropped\nc,dataset,\nd,nbs_effect,\n"
    )
    cache = tmp_path / ".cache/corpus"
    cache.mkdir(parents=True)
    (cache / "a.md").write_text("snapshot")
    (cache / "d.pdf").touch()  # empty files do not pass
    monkeypatch.setattr(server, "ROOT", tmp_path)
    monkeypatch.setattr(server, "CACHE", cache)
    result = server._corpus_readiness()
    assert result == dict(
        known=True, total=3, cached=1, missing=["b", "d"], ready=False
    )
    ev.unlink()
    assert server._corpus_readiness()["known"] is False


def test_scope_status_overrides_counts_and_preserves_routing():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node required")
    html = (ROOT / "docs/dashboard.html").read_text()
    function = html[
        html.index("  function auditFamilyStatus(") : html.index(
            "  // Jump to the Evidence Query"
        )
    ]
    with (ROOT / "docs/dashboard-family-status.csv").open() as stream:
        annotations = {r["suitability_family_id"]: r for r in csv.DictReader(stream)}
    # Plantation comes from the analytical policy, not a duplicate presentation rule.
    with (ROOT / "schema/lookups/family_rollup_policy.csv").open() as stream:
        for row in csv.DictReader(stream):
            if row["rollup_included"] == "false":
                annotations[row["suitability_family_id"]] = dict(
                    status="separate_comparison",
                    label="Separate comparison",
                    reason=row["rationale"],
                )
    script = (
        "const dashboardData = "
        + json.dumps(dict(family_display_status=annotations))
        + ";\n"
        + function
        + """
const assert=require('assert');
assert.equal(auditFamilyStatus('water_harvesting__rooftop','qualitative_only',999,999).key,'out_of_scope');
assert.equal(auditFamilyStatus('agroforestry__homegardens_proximity','qualitative_only').key,'out_of_scope');
assert.equal(auditFamilyStatus('forest_restoration__plantation','area_suitability').key,'separate_comparison');
assert.equal(auditFamilyStatus('forest_restoration__cross_family','qualitative_only').key,'routing');
assert.equal(auditFamilyStatus('wetland_management__constructed','qualitative_only').key,'qualitative');
assert.equal(auditFamilyStatus('agroforestry__planted_silvoarable','area_suitability').key,'target');
"""
    )
    result = subprocess.run([node, "-e", script], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
