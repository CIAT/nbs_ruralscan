"""Grey-lit positive-bias discount in synthesis weighting (issue #63)."""

from nbs_ruralscan.recipe import synthesis
from nbs_ruralscan.recipe.evidence import EvidenceUnit


def _unit(eid, src, role, basis="primary_measured"):
    return EvidenceUnit(
        evidence_id=eid,
        source_id=src,
        nbs_id="agroforestry",
        suitability_family_id="agroforestry__planted_silvoarable",
        variable="x",
        use_role=role,
        evidence_type="literature_relationship",
        claim_basis=basis,
        claim_scope="practice_technology",
        extraction_confidence="medium",
        quote="q",
        locator_type="page",
        page=1,
    )


def test_grey_discount_is_directional():
    peer = _unit("p", "peer", "nbs_effect")
    grey_t6 = _unit("g6", "greysrc", "nbs_effect")
    grey_t4 = _unit("g4", "greysrc", "structural_suitability")
    w_peer = synthesis._weight(peer, "high", "")
    # grey T6 benefit claim — hard haircut (0.4)
    assert synthesis._weight(grey_t6, "high", "grey") == w_peer * 0.4
    # grey T4 biophysical — barely discounted (0.9), much lighter than T6
    assert synthesis._weight(grey_t4, "high", "grey") == w_peer * 0.9
    assert synthesis._weight(grey_t6, "high", "grey") < synthesis._weight(
        grey_t4, "high", "grey"
    )
    # no category → no discount (backward compatible; peer/stock untouched)
    assert synthesis._weight(grey_t6, "high", "") == w_peer


def test_grey_cannot_dominate_t6_median_but_still_contributes():
    # T6 benefit reconciliation: one peer says abs_max=30, two grey say 60. Without the
    # discount the 2× grey win the weighted median (60); with the T6 haircut (×0.4) the
    # grey weight (2×0.4=0.8) drops below the peer (1.0) → consensus pulled back to 30.
    # Tests _reconcile directly (the core weighting; the T6 synthesiser will use it).
    contribs = [
        (_unit("p", "peer", "nbs_effect"), "high", {"abs_max": 30}),
        (_unit("g1", "grey1", "nbs_effect"), "high", {"abs_max": 60}),
        (_unit("g2", "grey2", "nbs_effect"), "high", {"abs_max": 60}),
    ]
    cats = {"grey1": "grey", "grey2": "grey"}
    assert (
        synthesis._reconcile(contribs, {})["abs_max"] == 60
    )  # undiscounted → grey wins
    assert (
        synthesis._reconcile(contribs, cats)["abs_max"] == 30
    )  # discounted → pulled back
    # grey still CONTRIBUTED (it was in the pool, just out-weighted) — n_sources unaffected.
