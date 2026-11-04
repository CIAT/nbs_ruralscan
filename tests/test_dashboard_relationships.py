from nbs_ruralscan.recipe.aggregate_evidence import aggregate
from nbs_ruralscan.schema_tools import dashboard_relationships


def test_live_catalogue_preserves_unapproved_and_uncompiled_claims(tmp_path):
    data = {
        "registers": {
            "EV_evidence_register": [
                {
                    "evidence_id": "active",
                    "nbs_id": "trees",
                    "source_id": "paper",
                    "variable": "slope",
                    "use_role": "structural_suitability",
                    "claim_scope": "practice_technology",
                    "reviewer_ok": False,
                    "relationship": {"direction": "decreasing"},
                },
                {
                    "evidence_id": "drop",
                    "nbs_id": "trees",
                    "source_id": "paper",
                    "use_role": "structural_suitability",
                    "review_state": "dropped",
                },
            ]
        },
        "recipes": {"trees": {}},
    }
    result = dashboard_relationships.build_relationships(data, tmp_path)["practices"][
        "trees"
    ]
    assert result["aggregate_status"] == "unavailable"
    assert result["aggregate"] is None
    assert [r["evidence_id"] for r in result["catalogue"]["records"]] == ["active"]
    claim = result["catalogue"]["records"][0]
    assert claim["has_stated_direction"] is True
    assert claim["reviewer_ok"] is False
    assert claim["linked_mapping_ids"] == []


def test_parity_failure_never_falls_back_to_old_published_aggregate(
    tmp_path, monkeypatch
):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/synthesise-recipe.py").touch()
    (tmp_path / "schema/recipes/trees").mkdir(parents=True)
    (tmp_path / "schema/recipes/trees/T4_suitability_mappings.csv").touch()

    def fail(*args, **kwargs):
        raise ValueError(
            "Reviewed corpus does not reproduce the audited live T4 recipe: test"
        )

    monkeypatch.setattr(dashboard_relationships, "build_contract", fail)
    data = {"recipes": {"trees": {"T4_suitability_mappings": [{"mapping_id": "rule"}]}}}
    result = dashboard_relationships.build_relationships(data, tmp_path)["practices"][
        "trees"
    ]
    assert result["aggregate"] is None
    assert "does not reproduce" in result["rebuild_detail"]


def test_current_aggregate_uses_canonical_contract_results(tmp_path, monkeypatch):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/synthesise-recipe.py").touch()
    (tmp_path / "schema/recipes/trees").mkdir(parents=True)
    (tmp_path / "schema/recipes/trees/T4_suitability_mappings.csv").touch()
    evidence = [
        {
            "evidence_id": "e",
            "source_id": "paper",
            "variable": "slope",
            "use_role": "structural_suitability",
            "claim_scope": "practice_technology",
            "suitability_family_id": "F1",
            "relationship": {"direction": "decreasing"},
        }
    ]
    monkeypatch.setattr(
        dashboard_relationships,
        "build_contract",
        lambda *args, **kwargs: {
            "evidence": evidence,
            "synthesis_report": {"evidence_dispositions": []},
            "inclusion": [],
            "importance": [],
            "contract": {"rows": []},
        },
    )
    data = {"recipes": {"trees": {"T4_suitability_mappings": [{"mapping_id": "rule"}]}}}
    result = dashboard_relationships.build_relationships(data, tmp_path)["practices"][
        "trees"
    ]
    assert result["aggregate_status"] == "current"
    assert result["aggregate"]["rows"][0]["evidence_ids"] == ["e"]


def model(mid, source, share, scope="regional_practice_model"):
    return dict(
        model_id=mid,
        source_id=source,
        status="calculated",
        provenance={},
        variables=[
            dict(
                variable="slope",
                scope=scope,
                whole_model_share=share,
                hierarchy_adjusted_ratio=share * 10,
            )
        ],
    )


def test_alternative_models_are_not_extra_source_votes_and_scopes_stay_separate():
    catalogue = {
        "records": [
            dict(
                evidence_id="a",
                source_id="s1",
                variable="slope",
                claim_scope="practice_technology",
                relationship='{"direction":"decreasing"}',
                compilation_disposition="selection_only",
                suitability_family_id="F1",
            )
        ]
    }
    models = [
        model("a", "s1", 0.1),
        model("b", "s1", 0.3),
        model("c", "s2", 0.4),
        model("d", "s3", 0.9, "fmnr_niger_practitioner_model"),
    ]
    out = aggregate(catalogue, [], models, [], {"slope": {"group_id": "topographic"}})
    assert len(out["rows"]) == 1
    summaries = out["rows"][0]["weight_summary"]
    assert summaries[0]["reporting_sources"] == 2
    assert abs(summaries[0]["median_source_share"] - 0.3) < 1e-10
    assert summaries[1]["median_source_share"] == 0.9
    assert out["rows"][0]["variable_use"] is None


def test_source_claim_repeats_and_function_options_do_not_inflate_support():
    base = dict(
        source_id="s1",
        variable="slope",
        claim_scope="practice_technology",
        relationship='{"direction":"decreasing"}',
        compilation_disposition="selection_only",
        suitability_family_id="F1",
    )
    c = {"records": [dict(base, evidence_id="a"), dict(base, evidence_id="b")]}
    m = [
        dict(
            role="suitability_score",
            variable="slope",
            system="F1",
            rule_id="rule",
            function_options=[dict(evidence_ids=["a"]), dict(evidence_ids=["b"])],
        )
    ]
    r = aggregate(c, [], [], m, {"slope": {"group_id": "topographic"}})["rows"][0]
    assert r["direction_by_family"][0]["sources"] == ["s1"]
    assert r["function_support"][0]["sources"] == ["s1"]


def test_unmapped_weight_mass_is_not_redistributed():
    c = {
        "records": [
            dict(
                evidence_id="a",
                source_id="s1",
                variable="slope",
                claim_scope="practice_technology",
                relationship="{}",
                compilation_disposition="selection_only",
                suitability_family_id="F1",
            )
        ]
    }
    m = model("a", "s1", 0.2)
    m["variables"].append(
        dict(
            variable="unmapped",
            scope="regional_practice_model",
            whole_model_share=0.8,
            hierarchy_adjusted_ratio=1,
        )
    )
    r = aggregate(c, [], [m], [], {"slope": {"group_id": "topographic"}})
    g = r["rows"][0]["mapped_group_weights"][0]
    assert g["share"] == 0.2 and g["unmapped_model_variables"] == ["unmapped"]


def test_relationship_ui_filters_traceability_and_safe_source_text():
    import shutil
    import subprocess
    from pathlib import Path

    import pytest

    if not shutil.which("node"):
        pytest.skip("Node unavailable")
    script = Path(__file__).resolve().parents[1] / "docs/dashboard-relationships.js"
    harness = r"""
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const nodes=new Map();
class Node {
  constructor(id){this.id=id;this.listeners={};this.value='';nodes.set(id,this);}
  set innerHTML(html){this.html=html;for(const m of html.matchAll(/\bid="([^"]+)"/g))new Node(m[1]);}
  get innerHTML(){return this.html;}
  addEventListener(name,handler){this.listeners[name]=handler;}
  focus(){this.focused=true;} scrollIntoView(){} querySelector(){return null;}
}
const root=new Node('relationship-review-root');let opened=[];
const window={DashboardProgress:{openSource:(...args)=>opened.push(args)}};
const document={getElementById:id=>nodes.get(id)};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window,document,Event:class {constructor(type){this.type=type;}}});
const base={source_id:'paper',variable:'slope',suitability_family_id:'F1',claim_scope:'practice_technology',source_direction:'decreasing',quote:'<img src=x onerror=bad()>',relationship:{direction:'decreasing'},linked_mapping_ids:[],compilation_disposition:'selection_only',has_stated_direction:true};
const fixture={relationships:{practices:{agroforestry:{catalogue:{records:[
  {...base,evidence_id:'approved',reviewer_ok:true},
  {...base,evidence_id:'waiting',reviewer_ok:false},
  {...base,evidence_id:'species',claim_scope:'species_specific',reviewer_ok:true}
]},aggregate:null,aggregate_note:'Aggregate unavailable'}}}};
window.DashboardRelationships.init(fixture);
assert(root.innerHTML.includes('does not certify human assessment'));
assert(!root.innerHTML.includes('Human approval'));
assert(nodes.get('dr-count').textContent.includes('2 source claims match'));
assert(nodes.get('dr-claims').innerHTML.includes('&lt;img'));
assert(!nodes.get('dr-claims').innerHTML.includes('<img'));
const change=(id,value)=>root.listeners.change({target:{id,value}});
nodes.get('dr-rule-detail').innerHTML='Previously selected numeric rule';
change('dr-review','approved');
assert.equal(nodes.get('dr-rule-detail').innerHTML,'');
assert(nodes.get('dr-count').textContent.includes('1 source claims match'));
assert(!nodes.get('dr-claims').innerHTML.includes('dr-claim-waiting'));
change('dr-scope','species_specific');
assert(nodes.get('dr-claims').innerHTML.includes('dr-claim-species'));
const button={dataset:{drSource:'paper'}};
root.listeners.click({target:{closest:()=>button}});
assert.deepEqual(opened,[['paper']]);
root.listeners.click({target:{closest:()=>({id:'dr-reset',dataset:{}})}});
assert(nodes.get('dr-count').textContent.includes('2 source claims match'));
fixture.recipes={agroforestry:{T4_suitability_mappings:[{mapping_id:'rule',variable:'slope',suitability_family_id:'F1',relationship_type:'piecewise',relationship_params:{profiles:[{source_id:'paper',unit:'degrees',intervals:[{lower:0,upper:5,lower_inclusive:true,upper_inclusive:false,label:'high',score:0.75,score_basis:'schema_class_convention'}]}]}}]}};
window.DashboardRelationships.refresh(fixture);
root.listeners.click({target:{closest:()=>({dataset:{drRule:'rule'}})}});
assert(nodes.get('dr-rule-detail').innerHTML.includes('Recorded intervals'));
assert(nodes.get('dr-rule-detail').innerHTML.includes('Compare source plots'));
assert(nodes.get('dr-rule-detail').innerHTML.includes('0.75'));
const host=new Node('t4-analysis'), practice=new Node('select-nbs'), family=new Node('select-family'), variable=new Node('study-variable'), find=new Node('t4-find'), tab=new Node('t4-tab-studies');
practice.dispatchEvent=()=>{};family.dispatchEvent=()=>{};variable.dispatchEvent=()=>{};
family.options=[{value:'F1'}];variable.options=[{value:'slope'}];host.querySelector=()=>variable;host.hidden=false;
let openedExplorer=false,updated;
window.DashboardShell={showExplorer(){openedExplorer=true;}};
window.T4Analysis={update(...args){updated=args;}};
tab.click=()=>{tab.clicked=true;};
root.listeners.click({target:{closest:()=>({dataset:{drPlots:'rule'}})}});
assert(openedExplorer);assert.equal(practice.value,'agroforestry');assert.equal(family.value,'F1');
assert.equal(variable.value,'slope');assert(tab.clicked);assert.equal(updated[0],'agroforestry');assert.equal(updated[1],'F1');
"""
    subprocess.run(
        ["node", "-e", harness, str(script)], check=True, capture_output=True, text=True
    )
