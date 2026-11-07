"""Reviewed input requirements; these never approve a numerical relationship."""

import json


def params(row):
    value = row.get("relationship_params") or {}
    return json.loads(value) if isinstance(value, str) else value


def validate_matching_input(requirement):
    if (
        not isinstance(requirement, dict)
        or requirement.get("status") != "requires_matching_input"
        or not isinstance(requirement.get("reason"), str)
        or not requirement["reason"].strip()
    ):
        raise ValueError("Invalid reviewed dataset binding requirement")
    return requirement


def row_binding_requirement(row):
    """The persistent mapping requirement, distinct from numerical profile review."""
    adaptation = params(row).get("reviewed_adaptation")
    if adaptation is None:
        return None
    if not isinstance(adaptation, dict):
        raise ValueError("Invalid reviewed adaptation")
    if "dataset_binding" in adaptation:
        return validate_matching_input(adaptation["dataset_binding"])
    return None


def matching_input_requirement(row):
    """Combine row/profile holds without permitting a dataset fallback."""
    relationship = params(row)
    reasons = []
    for carrier in [row, relationship, *relationship.get("profiles", [])]:
        adaptation = carrier.get("reviewed_adaptation")
        if adaptation is None:
            continue
        if not isinstance(adaptation, dict):
            raise ValueError("Invalid reviewed adaptation")
        if "dataset_binding" in adaptation:
            requirement = validate_matching_input(adaptation["dataset_binding"])
            reasons.append(requirement["reason"].strip())
    return (
        {
            "status": "requires_matching_input",
            "reason": " ".join(dict.fromkeys(reasons)),
        }
        if reasons
        else None
    )
