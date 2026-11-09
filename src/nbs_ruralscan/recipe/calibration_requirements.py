"""Mapping-level numerical holds are separate from source and input review."""

from .binding_requirements import params


def calibration_requirement(row):
    """Return the declared hold, failing closed on malformed review metadata."""
    relationship = params(row)
    if not isinstance(relationship, dict):
        raise ValueError("Invalid T4 relationship parameters")
    adaptation = relationship.get("reviewed_adaptation")
    if adaptation is None:
        return None
    if not isinstance(adaptation, dict):
        raise ValueError("Invalid reviewed adaptation")
    if "numerical_calibration" not in adaptation:
        return None
    requirement = adaptation["numerical_calibration"]
    if (
        not isinstance(requirement, dict)
        or requirement.get("status") != "held"
        or not isinstance(requirement.get("reason"), str)
        or not requirement["reason"].strip()
    ):
        raise ValueError("Invalid reviewed numerical calibration hold")
    return requirement
