"""Derived implementation readiness, separate from spatial execution authorization."""

LABELS = {
    "defined": "Defined for implementation",
    "provisional": "Provisional input assumption",
    "blocked": "Decision needed",
    "reference_only": "Evidence reference only",
}


def assess(row):
    """Classify existing choices; never select a response or approve an input."""
    role = row["role"]
    actions = []

    def action(owner, detail):
        actions.append({"owner": owner, "action": detail})

    selected = next(
        (
            o
            for o in row["function_options"]
            if o["function_id"] == row.get("function_id")
        ),
        None,
    )
    policy = row.get("approved_policy") or {}
    policy_matches = policy.get("function_verified") and (
        selected is None or selected["function_id"] == policy["function_id"]
    )
    effective = selected
    if effective is None and policy_matches:
        effective = next(
            (
                o
                for o in row["function_options"]
                if o["function_id"] == policy["function_id"]
            ),
            None,
        )
    basis = (
        "recipe_host_design"
        if selected and row.get("applicability_status") == "recipe_host_design"
        else "explicit_response_selection"
        if selected
        else "approved_policy"
        if effective
        else "none"
    )
    relevant_reviews = [
        r
        for r in row.get("soil_input_reviews", [])
        if effective
        and r["evidence_id"] in effective["evidence_ids"]
        and r.get("remaining_limit")
    ]
    proposals = policy.get("input_proposals", []) if policy_matches else []
    state = "blocked"
    if role == "reference_only":
        state = "reference_only"
        reason = "Retained operational evidence; no executable response is claimed."
    elif role == "operational_scenario":
        reason = (
            "Scenario endpoints are placeholders, not calibrated operational responses."
        )
        action(
            "Method lead",
            "Define raw inputs, scale, direction and scenario logic before implementation; keep outside M1 scoring.",
        )
    elif role == "hard_exclusion":
        if row.get("gate_input_contract"):
            state, basis = "defined", "authored_mask_contract"
            reason = "Boolean exclusion interface defined; target restriction assessment is still required."
            action(
                "Target team",
                "Supply assessed exclusion mask with applicable rules, authority, date, coverage and unknown areas; raw protected-area categories are insufficient.",
            )
        else:
            reason = "Legal exclusion has no usable input contract."
            action(
                "Method lead",
                "Define mask semantics and system coverage before implementation.",
            )
    elif effective is None:
        reason = (
            "No response is selected or available through a verified approved policy."
        )
        action(
            "Method lead",
            "Select an available response and record target-system applicability; restore or revalidate missing approved functions first.",
        )
    elif effective["completeness"]["status"] == "partial":
        reason = "Selected response has a known unresolved source continuation."
        action(
            "Evidence team",
            "Resolve the missing source continuation before using this response.",
        )
    else:
        state = "provisional" if relevant_reviews or proposals else "defined"
        reason = (
            "Response defined, but soil preparation or measurement compatibility remains an explicit assumption."
            if state == "provisional"
            else "Response or host rule defined; input checks and target applicability remain separate."
        )
        if state == "provisional":
            action(
                "Method lead with implementation team",
                "Record acceptance or replacement of soil-input assumptions and their limitations; run specified depth sensitivity checks.",
            )
        if role == "suitability_score":
            action(
                "Method lead",
                "Confirm target applicability; retain the approved criterion set and weights unless explicitly revised."
                if policy_matches
                else "Confirm target applicability and record the criterion set and weights for this response selection.",
            )
        for name, dependency in row.get("host_inputs", {}).items():
            required = dependency["spec"].get("variables", [])
            missing = [
                v for v in required if dependency["inputs"][v]["dataset_id"] is None
            ]
            action(
                "Implementation team",
                f"Supply and verify {name}; required only by its configured host branch. Missing inputs remain unknown."
                + (f" Local input needed: {', '.join(missing)}." if missing else ""),
            )
    if state != "reference_only":
        if row["dataset"].get("binding_differs_from_recipe"):
            action(
                "Implementation team",
                "Reconcile BIND versus recipe dataset and verify an explicit unit/class crosswalk; do not substitute silently.",
            )
        action(
            "Implementation team",
            "Verify actual dataset access, bands, units, masks, spatial processing and run-manifest provenance; spatial validation has not been performed.",
        )
    return {
        "state": state,
        "label": LABELS[state],
        "reason": reason,
        "function_basis": basis,
        "effective_function_id": effective["function_id"] if effective else None,
        "effective_function_fingerprint": effective["fingerprint"]
        if effective
        else None,
        "source_input_limit_ids": [r["evidence_id"] for r in relevant_reviews],
        "proposal_ids": [p["proposal_id"] for p in proposals],
        "next_actions": actions,
        "execution_ready": False,
        "execution_status": "not_spatially_validated",
    }
