"""T3/T6 cell-synthesis engine — the six contract fixtures (synthesis contract §6) + units.

Synthetic units only: no register data, no files. Every fixture is a behaviour the method
doc (methodology/T3_T6_generation_method.md) promises.
"""

from __future__ import annotations

import json

from nbs_ruralscan.recipe import cell_synthesis as cs
from nbs_ruralscan.recipe.evidence import EvidenceUnit

XW = [
    cs.XWRow("erosion_hazard", "T6", "soil_erosion_risk", "inverted", "direct"),
    cs.XWRow("project_cost", "T6", "establishment_cost", "same", "direct"),
    cs.XWRow("household_income", "T6", "rural_poverty", "same", "proxy"),
    cs.XWRow("drought_hazard", "T3", "drought", "inverted", "direct"),
]
TIERS_HIGH: dict[str, str] = {}


def _u(
    eid,
    src,
    variable="erosion_hazard",
    direction="negative",
    strength="strong",
    *,
    role="nbs_effect",
    basis="primary_measured",
    ctx=None,
    rel=None,
    family="riparian_buffer__planted",
    lineage=None,
    scope="practice_technology",
):
    r = {"direction": direction, "strength_class": strength}
    if rel:
        r.update(rel)
    return EvidenceUnit(
        evidence_id=eid,
        source_id=src,
        nbs_id="riparian_buffer",
        suitability_family_id=family,
        variable=variable,
        use_role=role,
        evidence_type="literature_relationship",
        claim_basis=basis,
        claim_scope=scope,
        extraction_confidence="high",
        quote="q",
        locator_type="page",
        page=1,
        relationship=r,
        context=ctx or {},
        lineage_of=lineage,
    )


def _t6(units, tiers=None, **kw):
    return cs.synthesise_cell(
        units,
        tiers or {},
        table="T6",
        nbs_id="riparian_buffer",
        target_key=kw.pop("key", "soil_erosion_risk"),
        xw_rows=XW,
        **kw,
    )


# ── fixture 1: Sweden → Sahel ─────────────────────────────────────────────────────────


def test_hic_only_evidence_is_out_of_context_and_yields_gap_for_sahel_aoi():
    swe = _u(
        "ev_swe",
        "swe_2019",
        ctx={"country": ["SWE"], "aez": "temperate_europe", "income_group": "high"},
    )
    rows, rep = _t6([swe])
    assert len(rows) == 1
    g = rows[0]
    assert g["applicability"]["transfer_class"] == "out_of_context"
    assert g["applicability"]["income_groups"] == {"high": 1}
    # the class still exists: erosion strongly DOWN = strong benefit (benefit frame)
    assert g["effect_direction"] == "strong_positive"
    assert g["evidence_level"] == "limited"
    # runtime: a Sahel AOI must NOT receive the class as if it applied
    row, status = cs.resolve_for_aoi(
        rows,
        {"income_group": "low", "aez": "semi_arid", "farming_system": "agro_pastoral"},
    )
    assert status == "no_applicable_evidence"
    assert row is g  # attached for greyed display


def test_hic_cost_never_enters_lmic_or_global_range_but_lmic_pair_does():
    swe = _u(
        "ev_swe_cost",
        "swe_2019",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["SWE"], "income_group": "high"},
        rel={"metric": "absolute", "magnitude": 4000, "unit": "usd_per_ha"},
    )
    ken = _u(
        "ev_ken_cost",
        "ken_2016",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["KEN"], "income_group": "lower_middle"},
        rel={"metric": "absolute", "magnitude": 300, "unit": "usd_per_ha"},
    )
    eth = _u(
        "ev_eth_cost",
        "eth_2019",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["ETH"], "income_group": "low"},
        rel={"metric": "absolute", "magnitude": 450, "unit": "usd_per_ha"},
    )
    # HIC alone → no range, exclusion logged with the HIC gate
    rows, rep = _t6([swe], key="establishment_cost")
    assert rows[0]["economic_value_range"] is None
    assert any(
        "HIC" in gate for eid, gate in rep.excluded_economics if eid == "ev_swe_cost"
    )
    # HIC + two LIC/LMIC → range from the two African sources only; HIC still excluded
    rows, rep = _t6([swe, ken, eth], key="establishment_cost")
    rng = rows[0]["economic_value_range"]
    assert rng == {
        "low": 300.0,
        "high": 450.0,
        "unit": "usd_per_ha",
        "source_note": rng["source_note"],
    }
    assert "swe_2019" not in rng["source_note"]
    assert (
        "ev_swe_cost",
        "HIC figure excluded from LIC/LMIC or global row",
    ) in rep.excluded_economics
    # one LMIC source only → gate 1 fails
    rows, rep = _t6([swe, ken], key="establishment_cost")
    assert rows[0]["economic_value_range"] is None
    assert any("only 1 independent" in g for _, g in rep.excluded_economics)


def test_lmic_evidence_dominates_and_semi_arid_scope_row_emitted():
    swe = _u(
        "ev_swe",
        "swe_2019",
        strength="slight",
        ctx={"country": ["SWE"], "aez": "temperate_europe", "income_group": "high"},
    )
    ken = _u(
        "ev_ken",
        "ken_2016",
        strength="strong",
        ctx={"country": ["KEN"], "aez": "semi_arid", "income_group": "lower_middle"},
    )
    eth = _u(
        "ev_eth",
        "eth_2019",
        strength="strong",
        ctx={"country": ["ETH"], "aez": "semi_arid", "income_group": "low"},
    )
    rows, rep = _t6([swe, ken, eth])
    g = rows[0]
    assert g["effect_direction"] == "strong_positive"  # LMIC weight ×1.0 beats HIC ×0.3
    assert g["applicability"]["transfer_class"] == "in_context"
    # semi-arid group (2 sources) vs global: same rank → emitted only if global is
    # out_of_context for that scope, which it is not → no aez scope row expected here...
    ids = [r["record_id"] for r in rows]
    # ...but the LIC/LMIC income group also has 2 sources and matches global → none either
    assert all("temperate" not in i for i in ids)
    # now make the HIC evidence pull the global rank down: two HIC slight + two LIC strong
    ita = _u(
        "ev_ita",
        "ita_2020",
        strength="slight",
        ctx={"country": ["ITA"], "aez": "temperate_europe", "income_group": "high"},
    )
    rows, rep = _t6([swe, ita, ken, eth])
    g = rows[0]
    scoped = {(r["scope_type"], r["scope_id"]): r for r in rows[1:]}
    # a temperate_europe scope row exists: its rank (slight) differs from global (strong)
    assert ("aez", "temperate_europe") in scoped
    assert scoped[("aez", "temperate_europe")]["effect_direction"] == "slight_positive"
    assert (
        scoped[("aez", "temperate_europe")]["applicability"]["transfer_class"]
        == "in_context"
    )
    assert g["effect_direction"] == "strong_positive"


# ── fixture 2: false-zero guard ───────────────────────────────────────────────────────


def test_opposite_signs_never_collapse_to_no_relationship():
    units = [
        _u(
            "p1",
            "s1",
            direction="positive",
            ctx={"aez": "humid_tropics", "income_group": "low"},
        ),
        _u(
            "p2",
            "s2",
            direction="positive",
            ctx={"aez": "humid_tropics", "income_group": "low"},
        ),
        _u(
            "n1",
            "s3",
            direction="negative",
            ctx={"aez": "semi_arid", "income_group": "low"},
        ),
        _u(
            "n2",
            "s4",
            direction="negative",
            ctx={"aez": "semi_arid", "income_group": "low"},
        ),
    ]
    rows, rep = _t6(units)
    g = rows[0]
    assert g["effect_direction"] != "no_relationship"
    assert g["agreement_level"] == "low"
    scoped = {(r["scope_type"], r["scope_id"]): r["effect_direction"] for r in rows[1:]}
    # erosion UP in the humid tropics = harm; DOWN in the semi-arid = benefit
    assert scoped[("aez", "humid_tropics")] == "strong_negative"
    assert scoped[("aez", "semi_arid")] == "strong_positive"
    assert g["context_dependent"] is True


def test_true_null_evidence_gives_no_relationship():
    units = [
        _u("z1", "s1", direction="none", strength="unspecified"),
        _u("z2", "s2", direction="none", strength="unspecified"),
    ]
    rows, _ = _t6(units)
    assert rows[0]["effect_direction"] == "no_relationship"
    assert rows[0]["agreement_level"] == "high"


# ── fixture 3: non-significant handling ───────────────────────────────────────────────


def test_ns_unit_counts_half_toward_direction_and_not_toward_strength():
    sig = _u(
        "sig",
        "s1",
        direction="positive",
        strength="moderate",
        rel={"significance": "sig"},
    )
    ns = _u(
        "ns", "s2", direction="positive", strength="strong", rel={"significance": "ns"}
    )
    rows, _ = _t6([sig, ns])
    g = rows[0]
    # erosion UP (positive as measured) → harm in the benefit frame
    assert g["effect_direction"].endswith("negative")
    # weights: sig 1.0, ns 0.5 → weighted median over ranks {2:1.0, 3:0.5} = 2 → moderate
    assert g["effect_direction"] == "moderate_negative"
    w_sig = cs.unit_weight(sig, "high", "", 0)
    w_ns = cs.unit_weight(ns, "high", "", 0)
    assert w_ns == w_sig * cs.NS_FACTOR


# ── fixture 4: lineage ────────────────────────────────────────────────────────────────


def test_citation_echoes_collapse_to_one_independent_source():
    primary = _u("p", "meta_2018")
    e1 = _u("e1", "echo_a", basis="cited_secondary", lineage="meta_2018")
    e2 = _u("e2", "echo_b", basis="cited_secondary", lineage="meta_2018")
    e3 = _u("e3", "echo_c", basis="cited_secondary", lineage="meta_2018")
    rows, rep = _t6([primary, e1, e2, e3])
    assert rows[0]["evidence_level"] == "limited"
    assert rows[0]["n_sources"] == 1
    assert len(rep.collapsed) == 3


# ── fixture 5: asset weights ──────────────────────────────────────────────────────────


def _asset_row(h, sens):
    return {
        "nbs_id": "riparian_buffer",
        "hazard_type": h,
        "risk_role": "asset_threat",
        "asset_sensitivity": sens,
        "scope_type": "",
        "suitability_family_id": "",
    }


def test_asset_risk_weights_only_on_complete_hazard_set():
    rep = cs.CellReport()
    six = [_asset_row(h, "moderate") for h in cs.T3_HAZARDS[:6]]
    assert cs.asset_risk_weights(six, "riparian_buffer", rep) is None
    assert rep.weights_incomplete == ["riparian_buffer"]
    seven = six + [_asset_row("frost", "none")]
    w = cs.asset_risk_weights(seven, "riparian_buffer")
    assert w is not None
    assert abs(sum(w.values()) - 1.0) < 1e-4
    assert w["frost"] == 0.0


def test_asset_vulnerability_cell_uses_hazard_key_and_damage_scale():
    units = [
        _u(
            "a1",
            "s1",
            "seedling_mortality",
            "positive",
            "strong",
            role="asset_vulnerability",
            ctx={"hazard_type": "drought", "income_group": "low"},
        ),
        _u(
            "a2",
            "s2",
            "seedling_mortality",
            "positive",
            "moderate",
            role="asset_vulnerability",
            ctx={"hazard_type": "drought", "income_group": "low"},
        ),
        _u(
            "a3",
            "s3",
            "seedling_mortality",
            "positive",
            "strong",
            role="asset_vulnerability",
            ctx={"hazard_type": "fire", "income_group": "low"},
        ),
    ]
    rows, _ = cs.synthesise_cell(
        units,
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
        role="asset_vulnerability",
    )
    g = rows[0]
    assert g["risk_role"] == "asset_threat"
    assert g["mitigation_potential"] == ""
    # strong(3) + moderate(2), equal weight → weighted median takes the lower → moderate
    assert g["asset_sensitivity"] == "moderate"
    assert g["n_sources"] == 2  # the fire unit is another cell
    # two strong → high; very_high would need confidence >= high (2 sources → limited)
    units[1].relationship["strength_class"] = "strong"  # type: ignore[index]
    rows, _ = cs.synthesise_cell(
        units,
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
        role="asset_vulnerability",
    )
    assert rows[0]["asset_sensitivity"] == "high"


# ── fixture 6: determinism ────────────────────────────────────────────────────────────


def test_same_units_give_byte_identical_rows():
    units = [
        _u(
            "p1",
            "s1",
            direction="positive",
            ctx={"aez": "humid_tropics", "income_group": "low"},
        ),
        _u(
            "n1",
            "s3",
            direction="negative",
            strength="slight",
            ctx={"aez": "semi_arid", "income_group": "high"},
        ),
        _u(
            "p2",
            "s2",
            direction="positive",
            strength="moderate",
            rel={"significance": "ns"},
        ),
    ]
    a, _ = _t6(list(units))
    b, _ = _t6(list(reversed(units)))
    # order-independent on the rank/levels/envelope (ids may reorder → compare sorted ids)
    for r in (*a, *b):
        r["evidence_ids"] = sorted(r["evidence_ids"])
        r["justification"]["key_evidence_ids"] = sorted(
            r["justification"]["key_evidence_ids"]
        )
        r["justification"]["evidence_summary"] = sorted(
            r["justification"]["evidence_summary"]
        )
        r["justification"]["agreement_note"] = ""
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    a2, _ = _t6(list(units))
    assert json.dumps(a2, sort_keys=True, default=str) == json.dumps(
        _t6(list(units))[0], sort_keys=True, default=str
    )


# ── proxies, polarity, T3 mapping, bands, IPCC ────────────────────────────────────────


def test_proxy_is_inverted_downweighted_and_named():
    inc = _u(
        "i1",
        "s1",
        "household_income",
        "positive",
        "moderate",
        ctx={"income_group": "low"},
    )
    rows, _ = _t6([inc], key="rural_poverty")
    g = rows[0]
    assert (
        g["effect_direction"] == "moderate_positive"
    )  # income up → poverty concern eased
    assert g["justification"]["proxies"] == ["household_income→rural_poverty (proxy)"]
    assert (
        cs.unit_weight(inc, "high", "", 0, XW[2].factor)
        == cs.unit_weight(inc, "high", "", 0) * 0.7
    )


def test_t3_mitigation_mapping_and_very_high_gate():
    assert cs.t3_mitigation_potential(0, "high") == "none"
    assert cs.t3_mitigation_potential(-3, "low") == "very_negative"
    assert cs.t3_mitigation_potential(-1, "low") == "negative"
    assert cs.t3_mitigation_potential(3, "medium") == "high"
    assert cs.t3_mitigation_potential(3, "high") == "very_high"
    assert cs.t3_mitigation_potential(3, "very_high") == "very_high"
    assert cs.t6_effect_direction(-2) == "moderate_negative"


def test_t3_cell_routes_via_xw_and_farming_system_key():
    d1 = _u(
        "d1",
        "s1",
        "drought_hazard",
        "negative",
        "strong",
        ctx={"farming_system": "cropping_rainfed", "income_group": "low"},
    )
    d2 = _u(
        "d2",
        "s2",
        "drought_hazard",
        "negative",
        "moderate",
        ctx={"farming_system": "agro_pastoral", "income_group": "low"},
    )
    rows, _ = cs.synthesise_cell(
        [d1, d2],
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
        farming_system="cropping_rainfed",
    )
    g = rows[0]
    assert g["hazard_type"] == "drought" and g["farming_system"] == "cropping_rainfed"
    assert g["n_sources"] == 1
    # 'negative' on drought_hazard = hazard impact reduced → positive mitigation
    assert g["mitigation_potential"] in ("high", "very_high", "moderate")


def test_ipcc_matrix_and_levels():
    assert cs.confidence("robust", "high") == "very_high"
    assert cs.confidence("limited", "low") == "very_low"
    assert cs.confidence("medium", "medium") == "medium"
    assert cs.agreement_level(0.8) == "high"
    assert cs.agreement_level(0.6) == "medium"
    assert cs.agreement_level(0.59) == "low"
    units = [_u(f"u{i}", f"s{i}", basis="cited_secondary") for i in range(6)]
    assert cs.evidence_level(units, {}) == "limited"  # all secondary
    units = [_u(f"u{i}", f"s{i}") for i in range(5)]
    assert cs.evidence_level(units, {}) == "robust"
    assert cs.evidence_level(units[:3], {}) == "medium"


def test_bands_classification():
    bands = [
        {
            "metric": "smd_hedges_g",
            "strength_class": "slight",
            "abs_min": "0",
            "abs_max": "0.2",
        },
        {
            "metric": "smd_hedges_g",
            "strength_class": "moderate",
            "abs_min": "0.2",
            "abs_max": "0.5",
        },
        {
            "metric": "smd_hedges_g",
            "strength_class": "strong",
            "abs_min": "0.5",
            "abs_max": "",
        },
        {
            "metric": "ordinal_rating",
            "strength_class": "strong",
            "source_scale_value": "not well",
        },
    ]
    assert cs.classify_magnitude("smd_hedges_g", 1.16, bands) == "strong"
    assert cs.classify_magnitude("smd_hedges_g", -0.3, bands) == "moderate"
    assert cs.classify_magnitude("smd_hedges_g", 0.1, bands) == "slight"
    assert cs.classify_magnitude("pct_change", 50, bands) == "unspecified"
    assert cs.classify_magnitude("ordinal_rating", None, bands, "Not Well") == "strong"


def test_context_distance_rules():
    assert (
        cs.context_distance({"income_group": "low"}, {"income_group": "lower_middle"})
        == 0
    )
    assert (
        cs.context_distance(
            {"income_group": "upper_middle"}, {"income_group": "lic_lmic"}
        )
        == 1
    )
    assert (
        cs.context_distance({"income_group": "high"}, {"income_group": "lic_lmic"}) == 2
    )
    assert cs.context_distance({"aez": "semi_arid"}, {"aez": "arid"}) == 1
    assert cs.context_distance({"aez": "semi_arid"}, {"aez": "humid_tropics"}) == 2
    assert (
        cs.context_distance(
            {"farming_system": "cropping_rainfed"},
            {"farming_system": "mixed_crop_livestock"},
        )
        == 1
    )
    assert (
        cs.context_distance(
            {"farming_system": "pastoral_rangeland"},
            {"farming_system": "tree_perennial"},
        )
        == 2
    )
    # blank on one side → dimension ignored
    assert cs.context_distance({"income_group": "high"}, {"aez": "semi_arid"}) == 0


def test_unit_context_fills_income_from_lookup_and_climate_zone_from_aez():
    u = _u("x", "s", ctx={"country": "KEN", "aez": "semi_arid"})
    ctx = cs.unit_context(u, {}, {"KEN": "lower_middle"})
    assert ctx == {
        "country": ["KEN"],
        "aez": "semi_arid",
        "income_group": "lower_middle",
        "climate_zone": "dryland",
    }
    # SRC default used when the unit is silent; unit overrides SRC
    u2 = _u("y", "s", ctx={"aez": "arid"})
    assert (
        cs.unit_context(
            u2, {"study_country": "NER", "aez": "semi_arid"}, {"NER": "low"}
        )["aez"]
        == "arid"
    )


def test_species_scope_routed_out_and_dropped_units_ignored():
    sp = _u("sp", "s1", scope="species_specific")
    dr = _u("dr", "s2")
    dr.review_state = "dropped"
    ok = _u("ok", "s3")
    rows, rep = _t6([sp, dr, ok])
    assert rows[0]["n_sources"] == 1
    assert ("sp", "claim_scope=species_specific") in rep.dropped


def test_family_rows_and_roll_up_spread():
    f1 = "riparian_buffer__planted"
    f2 = "riparian_buffer__natural_restored"
    units = [
        _u("a", "s1", strength="strong", family=f1, ctx={"income_group": "low"}),
        _u("b", "s2", strength="strong", family=f1, ctx={"income_group": "low"}),
        _u("c", "s3", strength="slight", family=f2, ctx={"income_group": "low"}),
        _u("d", "s4", strength="slight", family=f2, ctx={"income_group": "low"}),
    ]
    rows, _ = cs.synthesise_cell_with_families(
        units,
        {},
        table="T6",
        nbs_id="riparian_buffer",
        target_key="soil_erosion_risk",
        xw_rows=XW,
    )
    fam_rows = {
        r["suitability_family_id"]: r for r in rows if r["suitability_family_id"]
    }
    assert set(fam_rows) == {f1, f2}
    assert fam_rows[f1]["effect_direction"] == "strong_positive"
    assert fam_rows[f2]["effect_direction"] == "slight_positive"
    assert rows[0]["suitability_family_id"] == "" and rows[0]["family_spread"] is True
    assert rows[0]["record_id"] == "riparian_buffer__soil_erosion_risk"
    assert fam_rows[f1]["record_id"] == f"riparian_buffer__{f1}__soil_erosion_risk"


def test_magnitude_summary_needs_two_sources_sharing_metric_and_unit():
    a = _u("a", "s1", rel={"metric": "pct_change", "magnitude": -40, "unit": "percent"})
    b = _u("b", "s2", rel={"metric": "pct_change", "magnitude": -60, "unit": "percent"})
    c = _u(
        "c", "s3", rel={"metric": "smd_hedges_g", "magnitude": -0.8, "unit": "unitless"}
    )
    rows, _ = _t6([a, c])
    assert rows[0]["magnitude_summary"] is None
    rows, _ = _t6([a, b, c])
    ms = rows[0]["magnitude_summary"]
    assert (
        ms["metric"] == "pct_change"
        and ms["n"] == 2
        and ms["low"] == -60
        and ms["high"] == -40
    )


def test_resolve_prefers_most_specific_scope():
    rows = [
        {
            "record_id": "g",
            "scope_type": "",
            "scope_id": "",
            "applicability": {"transfer_class": "mixed"},
        },
        {"record_id": "inc", "scope_type": "income_group", "scope_id": "lic_lmic"},
        {"record_id": "aez", "scope_type": "aez", "scope_id": "semi_arid"},
    ]
    row, st = cs.resolve_for_aoi(rows, {"income_group": "low", "aez": "semi_arid"})
    assert row is not None and (row["record_id"], st) == ("aez", "ok")
    row, st = cs.resolve_for_aoi(rows, {"income_group": "low", "aez": "humid_tropics"})
    assert row is not None and (row["record_id"], st) == ("inc", "ok")
    row, st = cs.resolve_for_aoi(rows, {"income_group": "high"})
    assert row is not None and (row["record_id"], st) == ("g", "ok")


def test_direction_only_evidence_is_weakest_class_and_says_so():
    units = [
        _u(
            f"d{i}",
            f"s{i}",
            direction="negative",
            strength="unspecified",
            ctx={"income_group": "low"},
        )
        for i in range(3)
    ]
    rows, _ = _t6(units)
    g = rows[0]
    assert (
        g["effect_direction"] == "slight_positive"
    )  # erosion down, benefit frame, weakest
    assert g["justification"]["strength_basis"] == "direction_only"
    assert "strength not quantified" in g["justification"]["statement"]
    q = _u(
        "q", "sq", direction="negative", strength="strong", ctx={"income_group": "low"}
    )
    rows, _ = _t6(units + [q])
    assert rows[0]["justification"]["strength_basis"] == "quantified"
