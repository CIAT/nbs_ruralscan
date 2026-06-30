"""Consensus reduction for the headless review-submit path (scripts/submit-review.sh)."""

from nbs_ruralscan.schema_tools.submit_review import consensus_decisions


def test_agreeing_reviewers_apply_with_merged_reason_and_reviewers():
    store = {
        "e1": {
            "alice": {"decision": "drop", "reason": "off_scope"},
            "bob": {"decision": "drop", "reason": "wrong_table"},
        }
    }
    decisions, conflicts = consensus_decisions(store)
    assert conflicts == []
    assert decisions["e1"]["decision"] == "drop"
    assert decisions["e1"]["reviewer"] == "alice,bob"
    assert decisions["e1"]["reason"] == "off_scope;wrong_table"


def test_disagreement_is_a_conflict_not_applied():
    store = {"e1": {"alice": {"decision": "ok"}, "bob": {"decision": "drop"}}}
    decisions, conflicts = consensus_decisions(store)
    assert decisions == {}
    assert conflicts == ["e1"]


def test_single_reviewer_applies():
    store = {"e1": {"alice": {"decision": "ok", "reason": "confirmed_pass"}}}
    decisions, conflicts = consensus_decisions(store)
    assert list(decisions) == ["e1"]
    assert conflicts == []


def test_empty_decision_ignored():
    store = {"e1": {"alice": {"decision": ""}}, "e2": {"bob": {}}}
    decisions, conflicts = consensus_decisions(store)
    assert decisions == {} and conflicts == []
