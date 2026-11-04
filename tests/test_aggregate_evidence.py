from nbs_ruralscan.recipe.aggregate_evidence import aggregate


def model(mid, source, share, scope="regional_practice_model"):
    return dict(model_id=mid, source_id=source, status="calculated", provenance={},
                variables=[dict(variable="slope", scope=scope, whole_model_share=share,
                                hierarchy_adjusted_ratio=share*10)])


def test_alternative_models_are_not_extra_source_votes_and_scopes_stay_separate():
    catalogue = {"records": [dict(evidence_id="a",source_id="s1",variable="slope",
        claim_scope="practice_technology",relationship='{"direction":"decreasing"}',
        compilation_disposition="selection_only",suitability_family_id="F1")]}
    models=[model("a","s1",.1),model("b","s1",.3),model("c","s2",.4),
            model("d","s3",.9,"fmnr_niger_practitioner_model")]
    out=aggregate(catalogue,[],models,[],{"slope":{"group_id":"topographic"}})
    assert len(out['rows'])==1
    summaries=out['rows'][0]['weight_summary']
    assert summaries[0]['reporting_sources']==2
    assert abs(summaries[0]['median_source_share']-.3)<1e-10
    assert summaries[1]['median_source_share']==.9
    assert out['rows'][0]['variable_use'] is None


def test_source_claim_repeats_and_function_options_do_not_inflate_support():
    base=dict(source_id="s1",variable="slope",claim_scope="practice_technology",
              relationship='{"direction":"decreasing"}',compilation_disposition="selection_only",
              suitability_family_id="F1")
    c={"records":[dict(base,evidence_id="a"),dict(base,evidence_id="b")]}
    m=[dict(role="suitability_score",variable="slope",system="F1",rule_id="rule",
            function_options=[dict(evidence_ids=["a"]),dict(evidence_ids=["b"])])]
    r=aggregate(c,[],[],m,{"slope":{"group_id":"topographic"}})['rows'][0]
    assert r['direction_by_family'][0]['sources']==['s1']
    assert r['function_support'][0]['sources']==['s1']


def test_unmapped_weight_mass_is_not_redistributed():
    c={"records":[dict(evidence_id="a",source_id="s1",variable="slope",claim_scope="practice_technology",
                        relationship="{}",compilation_disposition="selection_only",suitability_family_id="F1")]}
    m=model("a","s1",.2)
    m['variables'].append(dict(variable="unmapped",scope="regional_practice_model",whole_model_share=.8,hierarchy_adjusted_ratio=1))
    r=aggregate(c,[],[m],[],{"slope":{"group_id":"topographic"}})
    g=r['rows'][0]['mapped_group_weights'][0]
    assert g['share']==.2 and g['unmapped_model_variables']==['unmapped']
