"""T3/T6 backlog round-1 rules (Pete 2026-11-06): A1 severity logging, A4 implied counterfactual."""

from nbs_ruralscan.recipe import cell_synthesis as cs
from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.schema_tools import check_context


def _row(
    version, ctx, quote="yields rose 40% in a season with 14 to 23 day dry spells"
):
    return {
        "evidence_id": "ev_x",
        "use_role": "nbs_effect",
        "variable": "crop_yield",
        "quote": quote,
        "ruleset_version": version,
        "context": ctx,
        "relationship": {"direction": "positive"},
    }


def _signals(row):
    return {f["signal"] for f in check_context.check_unit(row, set(), set())}


def test_severity_unlogged_only_from_v197():
    ctx = {"hazard_type": "drought", "hazard_severity": "unspecified"}
    assert "severity_unlogged" in _signals(_row("v1.9.7", dict(ctx)))
    assert "severity_unlogged" not in _signals(_row("v1.9.6", dict(ctx)))


def test_severity_unlogged_answered_by_magnitude_or_not_stated():
    for extra in (
        {"hazard_magnitude": "14 to 23 day dry spells"},
        {"hazard_magnitude": "not_stated"},
    ):
        ctx = {"hazard_type": "drought", **extra}
        assert "severity_unlogged" not in _signals(_row("v1.9.7", ctx))


def test_counterfactual_vocab():
    ctx = {
        "hazard_type": "drought",
        "hazard_magnitude": "not_stated",
        "counterfactual": "guessed",
    }
    assert "bad_vocab" in _signals(_row("v1.9.7", ctx))


def test_implied_counterfactual_discounts_weight():
    def unit(ctx):
        return EvidenceUnit(
            evidence_id="ev_x",
            source_id="s",
            nbs_id="water_harvesting_conservation",
            suitability_family_id="",
            variable="groundwater_recharge_potential",
            use_role="nbs_effect",
            evidence_type="literature_relationship",
            claim_basis="measured",
            claim_scope="practice_technology",
            extraction_confidence="low",
            quote="q",
            page=1,
            relationship={"direction": "positive"},
            context=ctx,
        )

    base = cs.unit_weight(unit({}), "high", "updated_lit", 0)
    implied = cs.unit_weight(
        unit({"counterfactual": "implied"}), "high", "updated_lit", 0
    )
    assert abs(implied - base * cs.IMPLIED_COUNTERFACTUAL_W) < 1e-9


def test_range_classed_by_weaker_end():
    assert cs.range_floor([4.0, 56.0]) == 4.0
    assert cs.range_floor([-58.0, -9.0]) == -9.0
    assert cs.range_floor([-0.35, 2.67]) == 0.0
    assert cs.range_floor([12.0]) == 12.0


def test_unreplicated_caps_contrast_class_at_moderate():
    def unit(ctx):
        return EvidenceUnit(
            evidence_id="ev_x",
            source_id="s",
            nbs_id="agroforestry",
            suitability_family_id="",
            variable="crop_yield",
            use_role="nbs_effect",
            evidence_type="literature_relationship",
            claim_basis="measured",
            claim_scope="practice_technology",
            extraction_confidence="medium",
            quote="q",
            page=1,
            relationship={"direction": "positive", "strength_class": "strong"},
            context=ctx,
        )

    assert cs.unit_rank(unit({}))[1] == cs.STRENGTH_RANK["strong"]
    assert cs.unit_rank(unit({"unreplicated": True}))[1] == cs.STRENGTH_RANK["moderate"]
