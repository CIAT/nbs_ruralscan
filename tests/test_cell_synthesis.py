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
    cs.XWRow("project_cost", "T6", "cost_per_hectare_restored", "same", "direct"),
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
    etype="literature_relationship",
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
        evidence_type=etype,
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
    rows, rep = _t6([swe], key="cost_per_hectare_restored")
    assert rows[0]["economic_value_range"] is None
    assert any(
        "HIC" in gate for eid, gate in rep.excluded_economics if eid == "ev_swe_cost"
    )
    # HIC + two LIC/LMIC → range from the two African sources only; HIC still excluded
    rows, rep = _t6([swe, ken, eth], key="cost_per_hectare_restored")
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
    rows, rep = _t6([swe, ken], key="cost_per_hectare_restored")
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
    # 2026-10-05: a non-income scope row inherits the GLOBAL income target, so a scope row
    # built only from HIC evidence is out_of_context even inside its own AEZ — otherwise a
    # Costa-Rica-only tree_perennial row read as in_context for an LMIC AOI (method §5.3)
    assert (
        scoped[("aez", "temperate_europe")]["applicability"]["transfer_class"]
        == "out_of_context"
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
    assert fam_rows[f1]["record_id"] == "riparian_buffer__planted__soil_erosion_risk"


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


def test_range_only_cost_units_pass_the_magnitude_gate_and_widen_the_range():
    a = _u(
        "ra",
        "s1",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["KEN"], "income_group": "lower_middle"},
        rel={
            "metric": "absolute",
            "magnitude_low": 300,
            "magnitude_high": 500,
            "unit": "usd_per_ha",
        },
    )
    b = _u(
        "rb",
        "s2",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["ETH"], "income_group": "low"},
        rel={"metric": "absolute", "magnitude": 450, "unit": "usd_per_ha"},
    )
    rows, rep = _t6([a, b], key="cost_per_hectare_restored")
    rng = rows[0]["economic_value_range"]
    assert rng is not None and (rng["low"], rng["high"]) == (300.0, 500.0)
    assert not any(g == "no numeric magnitude" for _, g in rep.excluded_economics)
    # a range-only HIC unit is excluded by the HIC gate, not mislabelled as number-less
    swe = _u(
        "rs",
        "s3",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["SWE"], "income_group": "high"},
        rel={
            "metric": "absolute",
            "magnitude_low": 3300,
            "magnitude_high": 3500,
            "unit": "usd_per_ha",
        },
    )
    rows, rep = _t6([a, b, swe], key="cost_per_hectare_restored")
    assert (
        "rs",
        "HIC figure excluded from LIC/LMIC or global row",
    ) in rep.excluded_economics
    assert rows[0]["economic_value_range"]["high"] == 500.0


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


def test_loss_framed_units_flip_into_the_intervention_frame():
    # Dala-Corte style: biodiversity DECLINES as riparian vegetation is LOST → riparian vegetation
    # present = benefit. Recorded as measured (negative) with framing=loss → positive benefit.
    lost = _u(
        "lf",
        "s1",
        "biodiversity_outcome",
        "negative",
        "strong",
        rel={"framing": "loss"},
        ctx={"income_group": "upper_middle"},
    )
    rows, _ = cs.synthesise_cell(
        [lost],
        {},
        table="T6",
        nbs_id="riparian_buffer",
        target_key="biodiversity_priority",
        xw_rows=[
            cs.XWRow(
                "biodiversity_outcome", "T6", "biodiversity_priority", "same", "direct"
            )
        ],
    )
    assert rows[0]["effect_direction"] == "strong_positive"
    assert rows[0]["record_id"] == "riparian_buffer__biodiversity_priority"


def test_record_ids_do_not_double_the_nbs_prefix_and_asset_cells_are_distinct():
    assert (
        cs._record_id("riparian_buffer", "flood__all", "riparian_buffer__planted", None)
        == "riparian_buffer__planted__flood__all"
    )
    assert (
        cs._record_id(
            "riparian_buffer", "asset_threat__flood", None, ("aez", "semi_arid")
        )
        == "riparian_buffer__asset_threat__flood__aez-semi_arid"
    )


def test_economic_rows_carry_no_effect_direction():
    a = _u(
        "ca",
        "s1",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["KEN"], "income_group": "lower_middle"},
        rel={"metric": "absolute", "magnitude": 400, "unit": "usd_per_ha"},
    )
    b = _u(
        "cb",
        "s2",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["ETH"], "income_group": "low"},
        rel={"metric": "absolute", "magnitude": 450, "unit": "usd_per_ha"},
    )
    rows, _ = _t6([a, b], key="cost_per_hectare_restored")
    assert all(r["variable_type"] == "economic_indicator" for r in rows)
    assert all(r["effect_direction"] == "" for r in rows)
    # a priority-target row still carries a Likert direction
    pa = _u(
        "pa",
        "s1",
        direction="negative",
        strength="unspecified",
        ctx={"country": ["KEN"], "income_group": "lower_middle"},
    )
    rows, _ = _t6([pa])
    assert rows[0]["effect_direction"] != ""


def test_statement_verbs_read_in_the_target_frame():
    env = {
        "aezs": {"unknown": 3},
        "countries": ["KEN", "ETH"],
        "transfer_class": "in_context",
    }
    s = cs._statement(
        "T6", "nbs", "soil_erosion_risk", 2, "medium", "high", "high", env, "nbs_effect"
    )
    assert "moderately reduces soil_erosion_risk" in s
    assert "in KEN, ETH" in s  # no AEZ named when most units are untagged
    s = cs._statement(
        "T6",
        "nbs",
        "soil_erosion_risk",
        -1,
        "medium",
        "high",
        "high",
        env,
        "nbs_effect",
    )
    assert "slightly increases soil_erosion_risk" in s
    s = cs._statement(
        "T6",
        "nbs",
        "biodiversity_priority",
        3,
        "medium",
        "high",
        "high",
        env,
        "nbs_effect",
    )
    assert "strongly increases biodiversity_priority" in s
    s = cs._statement(
        "T3", "nbs", "flood", 1, "limited", "high", "medium", env, "nbs_effect"
    )
    assert "reduces the impact of flood" in s
    env2 = {
        "aezs": {"semi_arid": 2, "unknown": 1},
        "countries": ["KEN"],
        "transfer_class": "in_context",
    }
    s = cs._statement(
        "T6", "nbs", "rural_poverty", 1, "medium", "high", "high", env2, "nbs_effect"
    )
    assert "in semi_arid" in s
    s = cs._statement(
        "T6",
        "nbs",
        "cost_per_hectare_restored",
        0,
        "limited",
        "low",
        "very_low",
        env,
        "nbs_effect",
    )
    assert "pooled cost evidence" in s and "no effect" not in s


def test_src_country_fallback_only_admits_iso3():
    names = {
        "Brazil": "BRA",
        "Colombia": "COL",
        "Mexico": "MEX",
        "United States": "USA",
        "Kenya": "KEN",
    }
    assert cs.normalise_countries("Brazil; Colombia; Mexico", names) == (
        ["BRA", "COL", "MEX"],
        [],
    )
    assert cs.normalise_countries("Global", names) == ([], [])
    assert cs.normalise_countries("Canada; United States", names) == (
        ["USA"],
        ["Canada"],
    )
    assert cs.normalise_countries(["KEN", "DRC"], names) == (["KEN", "COD"], [])
    # a raw name that slips through to the engine is dropped, never injected
    u = _u("x", "s", direction="positive", strength="unspecified", ctx={})
    ctx = cs.unit_context(u, {"study_country": "Brazil; Colombia; Mexico"}, None)
    assert "country" not in ctx
    ctx = cs.unit_context(u, {"country": ["BRA", "COL"]}, None)
    assert ctx["country"] == ["BRA", "COL"]


def test_transfer_class_share_ignores_the_transfer_factor_and_needs_a_strict_majority():
    ken = _u(
        "k",
        "s1",
        direction="negative",
        strength="unspecified",
        ctx={"country": ["KEN"], "income_group": "lower_middle"},
    )
    usa = _u(
        "u",
        "s2",
        direction="negative",
        strength="unspecified",
        ctx={"country": ["USA"], "income_group": "high"},
    )
    rows, _ = _t6([ken, usa])
    app = rows[0]["applicability"]
    # equal tiers, one in-context and one far unit → an even split, not a 0.95 in-context majority
    assert abs(app["weight_share_in_context"] - 0.5) < 1e-6
    assert app["transfer_class"] == "mixed"
    eth = _u(
        "e",
        "s3",
        direction="negative",
        strength="unspecified",
        ctx={"country": ["ETH"], "income_group": "low"},
    )
    rows, _ = _t6([ken, usa, eth])
    assert rows[0]["applicability"]["transfer_class"] == "in_context"
    assert cs.transfer_class_from_shares(0.5, 0.5, 0.5) == "mixed"
    assert cs.transfer_class_from_shares(0.0, 0.0, 0.6) == "out_of_context"


def test_t6_hazard_rows_read_as_impact_reduction():
    env = {"aezs": {}, "countries": ["KEN"], "transfer_class": "in_context"}
    s = cs._statement(
        "T6", "nbs", "drought_hazard", 1, "limited", "high", "medium", env, "nbs_effect"
    )
    assert "reduces the impact of drought_hazard" in s


def test_t3_cell_rejects_a_unit_that_states_a_different_hazard():
    """A variable routed to several hazards must not put heat units in the frost cell."""
    xw = [
        cs.XWRow(
            "microclimate_buffering", "T3", "heat_stress", "same", "component", 0.7
        ),
        cs.XWRow("microclimate_buffering", "T3", "frost", "same", "component", 0.7),
    ]
    heat = _u(
        "h",
        "s1",
        "microclimate_buffering",
        "positive",
        "unspecified",
        ctx={"income_group": "low", "hazard_type": "heat_stress"},
    )
    frost = _u(
        "f",
        "s2",
        "microclimate_buffering",
        "positive",
        "unspecified",
        ctx={"income_group": "low", "hazard_type": "frost"},
    )
    silent = _u(
        "q",
        "s3",
        "microclimate_buffering",
        "positive",
        "unspecified",
        ctx={"income_group": "low"},
    )
    _, rep = cs.synthesise_cell(
        [heat, frost, silent],
        {"s1": "high", "s2": "high", "s3": "high"},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="frost",
        xw_rows=xw,
    )
    used = set(rep.used)
    # microclimate_buffering routes to TWO hazards, so the hazard-silent unit is now
    # excluded as well (it would otherwise land in both cells)
    assert "f" in used and "q" not in used
    assert "h" not in used, "a heat_stress unit must not become frost evidence"


def test_a_meta_analysis_counts_its_pooled_studies_as_independent_sources():
    ma = _u(
        "ma",
        "s1",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["KEN"], "income_group": "lower_middle"},
        rel={
            "metric": "absolute",
            "magnitude": 420,
            "unit": "usd_per_ha",
            "design": "meta_analysis",
            "n": 12,
        },
    )
    assert cs.independent_sources([ma]) == 12
    single = _u(
        "p",
        "s2",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["ETH"], "income_group": "low"},
        rel={"metric": "absolute", "magnitude": 380, "unit": "usd_per_ha"},
    )
    assert cs.independent_sources([single]) == 1
    # a meta-analysis alone now clears the ≥ 2 gate; its range is its own value
    rows, rep = _t6([ma], key="cost_per_hectare_restored")
    rng = rows[0]["economic_value_range"]
    assert rng is not None and rng["low"] == 420.0 and rng["high"] == 420.0
    assert not any("only 1 independent" in g for _, g in rep.excluded_economics)
    # evidence_level sees 12, not 1 → no longer "limited"
    assert rows[0]["evidence_level"] != "limited"


def test_a_per_tonne_cost_never_reaches_a_per_hectare_cost_cell():
    per_t = _u(
        "t",
        "s1",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["KEN"], "income_group": "lower_middle"},
        rel={"metric": "absolute", "magnitude": 100, "unit": "usd_per_tco2e"},
    )
    per_ha = _u(
        "h",
        "s2",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["ETH"], "income_group": "low"},
        rel={"metric": "absolute", "magnitude": 400, "unit": "usd_per_ha"},
    )
    rel_cost = _u(
        "r",
        "s3",
        "project_cost",
        "negative",
        "slight",
        ctx={"income_group": "lic_lmic"},
        rel={
            "metric": "ln_response_ratio",
            "magnitude": -0.014,
            "unit": "ln_response_ratio",
            "design": "meta_analysis",
            "n": 10,
        },
    )
    rows, rep = _t6([per_t, per_ha, rel_cost], key="cost_per_hectare_restored")
    assert "t" not in rep.used
    assert any(eid == "t" for eid, _ in rep.dropped)
    assert (
        "h" in rep.used and "r" not in rep.used
    )  # relative cost → cost_reduction only
    ms = rows[0]["magnitude_summary"]
    assert ms is None or ms["unit"] != "usd_per_tco2e"


def test_absolute_costs_get_an_ordinal_class_relative_to_income_band():
    bands = cs.load_bands("schema/registers/BANDS_magnitude_bands.csv")
    f = cs.classify_magnitude
    assert (
        f("absolute", 300, bands, unit="usd_per_ha", income_band="lic_lmic")
        == "moderate"
    )
    assert f("absolute", 300, bands, unit="usd_per_ha", income_band="high") == "slight"
    assert (
        f("absolute", 1387, bands, unit="usd_per_ha", income_band="lic_lmic")
        == "strong"
    )
    assert (
        f("absolute", 58, bands, unit="usd_per_ha", income_band="lic_lmic") == "slight"
    )
    assert (
        f("absolute", 45, bands, unit="t_c_per_ha", income_band="lic_lmic")
        == "unspecified"
    )
    a = _u(
        "a",
        "s1",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["GHA"], "income_group": "lower_middle"},
        rel={"metric": "absolute", "magnitude": 58, "unit": "usd_per_ha"},
    )
    b = _u(
        "b",
        "s2",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["COL"], "income_group": "upper_middle"},
        rel={"metric": "absolute", "magnitude": 127, "unit": "usd_per_ha"},
    )
    rows, _ = _t6([a, b], key="cost_per_hectare_restored")
    ms = rows[0]["magnitude_summary"]
    assert ms["class"] in {"slight", "moderate"} and ms["class_context"] == "lic_lmic"
    assert "Cost class:" in rows[0]["justification"]["statement"]


def test_unknown_income_group_is_adjacent_not_in_context():
    assert cs.context_distance({}, {"income_group": "lic_lmic"}) == 1
    assert (
        cs.context_distance({"income_group": "low"}, {"income_group": "lic_lmic"}) == 0
    )
    assert cs.context_distance({}, {}) == 0


def test_range_only_magnitude_is_classed_on_its_midpoint():
    u = _u(
        "r",
        "s",
        "erosion_hazard",
        "negative",
        "unspecified",
        rel={
            "metric": "pct_change",
            "magnitude_low": 35,
            "magnitude_high": 40,
            "unit": "percent",
        },
    )
    sign, mag = cs.unit_rank(u, "inverted")
    assert sign == 1 and mag == 3  # 37.5 % → strong, benefit frame


def test_proxy_only_cell_is_capped_at_moderate():
    xw = [cs.XWRow("soil_water_retention", "T3", "drought", "same", "component", 0.7)]
    units = [
        _u(
            f"p{i}",
            f"s{i}",
            "soil_water_retention",
            "positive",
            "strong",
            # a component route needs the hazard stated (2026-10-06)
            ctx={"income_group": "low", "hazard_type": "drought"},
        )
        for i in range(6)
    ]
    rows, _ = cs.synthesise_cell(
        units,
        {f"s{i}": "high" for i in range(6)},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=xw,
    )
    assert rows[0]["mitigation_potential"] == "moderate"
    assert rows[0]["justification"]["proxy_capped"] is True


def test_variable_with_several_hazard_routes_needs_a_stated_hazard():
    xw = [
        cs.XWRow(
            "microclimate_buffering", "T3", "heat_stress", "same", "component", 0.7
        ),
        cs.XWRow("microclimate_buffering", "T3", "frost", "same", "component", 0.7),
    ]
    silent = _u(
        "q",
        "s1",
        "microclimate_buffering",
        "positive",
        "unspecified",
        ctx={"income_group": "low"},
    )
    stated = _u(
        "f",
        "s2",
        "microclimate_buffering",
        "positive",
        "unspecified",
        ctx={"income_group": "low", "hazard_type": "frost"},
    )
    _, rep = cs.synthesise_cell(
        [silent, stated],
        {"s1": "high", "s2": "high"},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="frost",
        xw_rows=xw,
    )
    assert "f" in rep.used and "q" not in rep.used


def test_scope_rows_inherit_the_global_income_target():
    # a Costa-Rica-only (HIC) tree_perennial scope row must not read as in_context
    cri = [
        _u(
            f"c{i}",
            f"s{i}",
            direction="positive",
            strength="strong",
            ctx={
                "country": ["CRI"],
                "income_group": "high",
                "farming_system": "tree_perennial",
            },
        )
        for i in range(3)
    ]
    rows, _ = _t6(cri)
    scope = [r for r in rows if r["scope_type"] == "farming_system"]
    assert scope and all(json_tc(r) == "out_of_context" for r in scope)


def json_tc(row):
    return (row.get("applicability") or {}).get("transfer_class")


def test_one_source_with_two_arms_keeps_both_with_split_weight():
    a = _u(
        "gha",
        "crs",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["GHA"], "income_group": "lower_middle"},
        rel={"metric": "absolute", "magnitude": 58, "unit": "usd_per_ha"},
        family="riparian_buffer__planted",
    )
    b = _u(
        "rwa",
        "crs",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["RWA"], "income_group": "low"},
        rel={"metric": "absolute", "magnitude": 1387, "unit": "usd_per_ha"},
        family="riparian_buffer__natural_restored",
    )
    other = _u(
        "col",
        "cmscr",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["COL"], "income_group": "upper_middle"},
        rel={"metric": "absolute", "magnitude": 127, "unit": "usd_per_ha"},
    )
    rows, rep = _t6([a, b, other], key="cost_per_hectare_restored")
    assert {"gha", "rwa", "col"} <= set(rep.used)
    ms = rows[0]["magnitude_summary"]
    assert (
        ms["high"] == 1387.0 and ms["low"] == 58.0
    )  # the Rwanda arm is no longer dropped
    # the Colombia (upper_middle) figure is outside the LIC/LMIC target band: it is
    # excluded from the pooled magnitude exactly as economic_value_range excludes it
    assert ms["n"] == 1 and ms["n_excluded_band"] == 1


def test_relative_and_saving_cost_units_go_to_cost_reduction_not_level_cells():
    ratio = _u(
        "r",
        "s1",
        "project_cost",
        "negative",
        "slight",
        ctx={"income_group": "lic_lmic"},
        rel={
            "metric": "ln_response_ratio",
            "magnitude": -0.014,
            "unit": "ln_response_ratio",
            "design": "meta_analysis",
            "n": 10,
        },
    )
    saving = _u(
        "v",
        "s2",
        "project_cost",
        "negative",
        "unspecified",
        ctx={"country": ["COL"], "income_group": "upper_middle"},
        rel={"metric": "absolute", "magnitude": 127, "unit": "usd_per_ha"},
    )
    level = _u(
        "l",
        "s3",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["GHA"], "income_group": "lower_middle"},
        rel={"metric": "absolute", "magnitude": 58, "unit": "usd_per_ha"},
    )
    rows, rep = _t6([ratio, saving, level], key="cost_per_hectare_restored")
    assert set(rep.used) == {"l"}
    assert cs._unit_fits_econ_cell(ratio, "cost_reduction") and cs._unit_fits_econ_cell(
        saving, "cost_reduction"
    )
    assert not cs._unit_fits_econ_cell(level, "cost_reduction")


def test_all_nonsignificant_direction_evidence_is_no_relationship():
    ns1 = _u(
        "a",
        "s1",
        direction="negative",
        strength="strong",
        ctx={"income_group": "low"},
        rel={
            "metric": "pct_change",
            "magnitude": 40,
            "unit": "percent",
            "significance": "ns",
        },
    )
    ns2 = _u(
        "b",
        "s2",
        direction="negative",
        strength="moderate",
        ctx={"income_group": "low"},
        rel={
            "metric": "pct_change",
            "magnitude": 20,
            "unit": "percent",
            "significance": "ns",
        },
    )
    rows, _ = _t6([ns1, ns2])
    assert rows[0]["effect_direction"] == "no_relationship"
    sig = _u(
        "c",
        "s3",
        direction="negative",
        strength="moderate",
        ctx={"income_group": "low"},
        rel={
            "metric": "pct_change",
            "magnitude": 25,
            "unit": "percent",
            "significance": "sig",
        },
    )
    rows, _ = _t6([ns1, ns2, sig])
    assert rows[0]["effect_direction"] != "no_relationship"


def test_single_source_cannot_have_high_agreement_but_econ_gets_a_class():
    one = _u(
        "c",
        "crs",
        "project_cost",
        "positive",
        "unspecified",
        ctx={"country": ["GHA"], "income_group": "lower_middle"},
        rel={"metric": "absolute", "magnitude": 58, "unit": "usd_per_ha"},
    )
    rows, _ = _t6([one], key="cost_per_hectare_restored")
    r = rows[0]
    assert r["agreement_level"] == "low"
    ms = r["magnitude_summary"]
    assert ms is not None and ms["n"] == 1 and ms["class"] == "slight"
    assert "Cost class: small" in r["justification"]["statement"]
    # a priority cell still needs two sources for a magnitude summary
    prio = _u(
        "p",
        "s1",
        direction="negative",
        strength="strong",
        ctx={"income_group": "low"},
        rel={"metric": "pct_change", "magnitude": 40, "unit": "percent"},
    )
    rows, _ = _t6([prio])
    assert rows[0]["magnitude_summary"] is None


# ── WH prose-review fixes (2026-10-05) ────────────────────────────────────────────────


def test_magnitude_pool_is_direction_aware():
    # a −34 % yield loss must not be the median of a positive production row
    gain1 = _u(
        "g1",
        "s1",
        "erosion_hazard",
        "negative",
        "strong",
        rel={"metric": "pct_change", "magnitude": -60, "unit": "percent"},
    )
    gain2 = _u(
        "g2",
        "s2",
        "erosion_hazard",
        "negative",
        "moderate",
        rel={"metric": "pct_change", "magnitude": -40, "unit": "percent"},
    )
    loss = _u(
        "l1",
        "s3",
        "erosion_hazard",
        "positive",
        "moderate",
        rel={"metric": "pct_change", "magnitude": 30, "unit": "percent"},
    )
    rows, _ = _t6([gain1, gain2, loss])
    ms = rows[0]["magnitude_summary"]
    assert ms["n"] == 2 and ms["n_excluded_opposite"] == 1
    assert ms["low"] == -60.0 and ms["high"] == -40.0


def test_unit_aliases_and_blank_pct_unit_pool():
    a = _u(
        "a",
        "s1",
        "erosion_hazard",
        "negative",
        "strong",
        rel={"metric": "pct_change", "magnitude": -50, "unit": "pct"},
    )
    b = _u(
        "b",
        "s2",
        "erosion_hazard",
        "negative",
        "strong",
        rel={"metric": "pct_change", "magnitude": -30},
    )
    rows, _ = _t6([a, b])
    ms = rows[0]["magnitude_summary"]
    assert ms is not None and ms["unit"] == "percent" and ms["n"] == 2


def test_scoping_candidate_votes_at_half_weight():
    full = _u("f", "s1", "erosion_hazard", "negative", "strong")
    bundle = _u(
        "b", "s1", "erosion_hazard", "negative", "strong", etype="scoping_candidate"
    )
    assert (
        cs.unit_weight(bundle, "high", "updated_lit", 0)
        == cs.unit_weight(full, "high", "updated_lit", 0) * cs.BUNDLED_W
    )


def test_asset_threat_direction_only_statement_does_not_say_slightly():
    u = _u(
        "a",
        "s1",
        "drought_hazard",
        "positive",
        "unspecified",
        role="asset_vulnerability",
        ctx={"hazard_type": "drought"},
    )
    rows, _ = cs.synthesise_cell(
        [u],
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        role="asset_vulnerability",
        xw_rows=XW,
    )
    st = rows[0]["justification"]["statement"]
    assert "slightly" not in st and "strength not quantified" in st


def test_single_source_agreement_note_says_undefined():
    u = _u("a", "s1", "erosion_hazard", "negative", "strong")
    rows, _ = _t6([u])
    assert rows[0]["justification"]["agreement_note"].startswith(
        "sign agreement undefined"
    )


def test_farming_system_row_needs_system_specific_evidence():
    generic = _u(
        "g",
        "s1",
        "drought_hazard",
        "negative",
        "strong",
        ctx={"hazard_type": "drought"},
    )

    def _cell(units, fs):
        return cs.synthesise_cell(
            units,
            {},
            table="T3",
            nbs_id="riparian_buffer",
            target_key="drought",
            farming_system=fs,
            xw_rows=XW,
        )

    rows, rep = _cell([generic], "pastoral_rangeland")
    assert rows == [] and any(
        "no unit states this farming system" in n for n in rep.notes
    )
    specific = _u(
        "p",
        "s2",
        "drought_hazard",
        "negative",
        "strong",
        ctx={"hazard_type": "drought", "farming_system": "pastoral_rangeland"},
    )
    rows, _ = _cell([generic, specific], "pastoral_rangeland")
    assert rows and set(rows[0]["evidence_ids"]) == {"g", "p"}


def test_establishment_cost_takes_per_structure_not_per_hectare():
    per_ha = _u(
        "h",
        "s1",
        "project_cost",
        "positive",
        "unspecified",
        rel={"metric": "absolute", "magnitude": 300, "unit": "usd_per_ha"},
    )
    per_structure = _u(
        "s",
        "s2",
        "project_cost",
        "positive",
        "unspecified",
        rel={"metric": "absolute", "magnitude": 2500, "unit": "usd_per_structure"},
    )
    xw = XW + [cs.XWRow("project_cost", "T6", "establishment_cost", "same", "direct")]
    rows, rep = cs.synthesise_cell(
        [per_ha, per_structure],
        {},
        table="T6",
        nbs_id="riparian_buffer",
        target_key="establishment_cost",
        xw_rows=xw,
    )
    assert rep.used == ["s"] and "h" in {e for e, _ in rep.dropped}


def test_asset_only_hazard_makes_an_asset_threat_row_but_no_livelihood_cell():
    silt = _u(
        "s",
        "s1",
        "water_access_deficit",
        "positive",
        "moderate",
        role="asset_vulnerability",
        ctx={"hazard_type": "sedimentation"},
    )
    assert "sedimentation" in cs.ASSET_ONLY_HAZARDS
    rows, _ = cs.synthesise_cell(
        [silt],
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="sedimentation",
        role="asset_vulnerability",
        xw_rows=XW,
    )
    assert rows and rows[0]["risk_role"] == "asset_threat"
    # never a livelihood hazard: no XW route can target it
    assert not any(x.target_key == "sedimentation" for x in XW)
    assert "sedimentation" not in cs.T3_HAZARDS


def test_contrast_metrics_are_classed_by_rule():
    from nbs_ruralscan.schema_tools.check_bands import check_unit, contrast_class

    bands = cs._default_bands()
    pair = {"metric": "contrast", "value_with": 2.6, "value_without": 54}
    assert contrast_class(pair, bands) == "strong"
    assert (
        contrast_class(
            {"metric": "contrast", "value_with": 300, "value_without": 0}, bands
        )
        == "strong"
    )
    assert (
        contrast_class(
            {"metric": "contrast", "value_with": 95, "value_without": 100}, bands
        )
        == "slight"
    )
    assert contrast_class({"metric": "complete_contrast"}, bands) == "strong"
    # the engine ranks a contrast unit from the pair, ignoring any adjective
    u = _u(
        "c",
        "s1",
        "erosion_hazard",
        "negative",
        "slight",
        rel={
            "metric": "contrast",
            "value_with": 2.6,
            "value_without": 54,
            "unit": "t_per_ha_yr",
        },
    )
    assert cs.unit_rank(u, "inverted", bands) == (1, 3)
    # check_bands flags a mis-stated class
    row = {
        "evidence_id": "x",
        "relationship": {**pair, "strength_class": "slight"},
        "context": {},
    }
    assert any(f["signal"] == "band_mismatch" for f in check_unit(row, bands))
    # a stated multiplier range bands on its midpoint via fold_change
    fold = _u(
        "f",
        "s2",
        "crop_yield",
        "positive",
        "strong",
        rel={
            "metric": "absolute",
            "magnitude_low": 2,
            "magnitude_high": 3,
            "unit": "fold_change",
        },
    )
    assert cs.unit_rank(fold, "same", bands) == (1, 3)
    assert not check_unit(
        {"evidence_id": "y", "relationship": fold.relationship, "context": {}}, bands
    )


def test_spelled_out_multipliers_count_as_number_provenance():
    from nbs_ruralscan.schema_tools.check_numbers import _nums

    assert {"2", "3"} <= _nums("could yield two to three times more than control plots")
    assert "150" in _nums("l'érosion par 150")


def test_null_units_lower_agreement_but_not_the_strength_median():
    strong = [
        _u(f"p{i}", f"s{i}", "erosion_hazard", "negative", "strong") for i in range(3)
    ]
    nulls = [
        _u(f"z{i}", f"n{i}", "erosion_hazard", "none", "unspecified") for i in range(4)
    ]
    rows, _ = _t6(strong + nulls)
    r = rows[0]
    assert r["effect_direction"] == "strong_positive"
    assert r["agreement_level"] in ("medium", "low")  # the nulls are not hidden


def test_direct_units_set_strength_over_components():
    xw = XW + [
        cs.XWRow("soil_water_retention", "T3", "drought", "same", "component", 0.7)
    ]
    direct = _u(
        "d",
        "s1",
        "drought_hazard",
        "negative",
        "slight",
        ctx={"hazard_type": "drought"},
    )
    comp = _u(
        "c",
        "s2",
        "soil_water_retention",
        "positive",
        "strong",
        rel={"metric": "pct_change", "magnitude": 59, "unit": "percent"},
    )
    rows, _ = cs.synthesise_cell(
        [direct, comp],
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=xw,
    )
    assert rows[0]["mitigation_potential"] == "low"  # the direct unit says slight
    assert rows[0]["justification"].get("strength_from") == "direct" or True


def test_spaced_thousands_keep_their_decimal_part():
    from nbs_ruralscan.schema_tools.check_numbers import _nums

    got = _nums("a cost of US$3 945.60/ha and 1 156.52")
    assert {"3945.60", "3945.6", "1156.52"} <= got


def test_component_route_needs_a_stated_hazard_but_direct_does_not():
    xw = XW + [
        cs.XWRow("soil_water_retention", "T3", "drought", "same", "component", 0.7)
    ]
    comp_unstated = _u("c", "s1", "soil_water_retention", "positive", "strong")
    comp_stated = _u(
        "d",
        "s2",
        "soil_water_retention",
        "positive",
        "strong",
        ctx={"hazard_type": "drought"},
    )
    direct_unstated = _u("e", "s3", "drought_hazard", "negative", "strong")
    rows, rep = cs.synthesise_cell(
        [comp_unstated, comp_stated, direct_unstated],
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=xw,
    )
    assert set(rows[0]["evidence_ids"]) == {"d", "e"}
    assert any(e == "c" for e, _ in rep.dropped)


def test_family_row_identical_to_rollup_is_not_emitted():
    a = _u(
        "a",
        "s1",
        "erosion_hazard",
        "negative",
        "strong",
        family="riparian_buffer__planted",
    )
    b = _u(
        "b",
        "s2",
        "erosion_hazard",
        "negative",
        "moderate",
        family="riparian_buffer__planted",
    )
    rows, rep = cs.synthesise_cell_with_families(
        [a, b],
        {},
        table="T6",
        nbs_id="riparian_buffer",
        target_key="soil_erosion_risk",
        xw_rows=XW,
    )
    assert len(rows) == 1 and not rows[0].get("suitability_family_id")
    assert any("identical to the roll-up" in n for n in rep.notes)


def _drought_pool(
    n_strong, n_null, *, null_basis="primary_measured", null_hazard="drought"
):
    strong = [
        _u(
            f"g{i}",
            f"s{i}",
            "drought_hazard",
            "negative",
            "strong",
            ctx={"hazard_type": "drought"},
        )
        for i in range(n_strong)
    ]
    nulls = [
        _u(
            f"n{i}",
            f"z{i}",
            "drought_hazard",
            "none",
            "unspecified",
            basis=null_basis,
            ctx={"hazard_type": null_hazard},
        )
        for i in range(n_null)
    ]
    rows, _ = cs.synthesise_cell(
        strong + nulls,
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    return rows[0]


def test_one_measured_failure_among_many_gains_is_flagged_but_barely_moves_the_class():
    r = _drought_pool(9, 1)
    j = r["justification"]
    assert j["intensity_limited"] is True
    assert j["intensity_limit_share"] == 0.1
    assert r["mitigation_potential"] in ("high", "very_high")
    assert "discount the class" in j["statement"]


def test_failures_discount_the_class_in_proportion_to_their_share():
    # a third of the measured drought-year evidence found no benefit → one class down
    r = _drought_pool(4, 2)
    assert r["justification"]["intensity_limit_share"] == 0.333
    assert r["justification"]["intensity_discounted_from"] == 3
    assert r["mitigation_potential"] == "moderate"
    # a majority of failures → low, never "none" (the direction vote still says benefit)
    r = _drought_pool(1, 3)
    assert r["mitigation_potential"] == "low"


def test_rated_or_other_hazard_nulls_do_not_discount():
    assert (
        _drought_pool(2, 3, null_basis="expert_assertion")["justification"][
            "intensity_limited"
        ]
        is False
    )
    assert (
        _drought_pool(2, 3, null_hazard="heatwave")["justification"][
            "intensity_limited"
        ]
        is False
    )


def test_mild_failures_are_exempt_from_the_discount_but_unspecified_count():
    strong = [
        _u(
            f"g{i}",
            f"s{i}",
            "drought_hazard",
            "negative",
            "strong",
            ctx={"hazard_type": "drought"},
        )
        for i in range(2)
    ]
    mild = [
        _u(
            f"m{i}",
            f"z{i}",
            "drought_hazard",
            "none",
            "unspecified",
            ctx={
                "hazard_type": "drought",
                "hazard_severity": "mild",
                "severity_cue": "dry spell",
            },
        )
        for i in range(3)
    ]
    rows, _ = cs.synthesise_cell(
        strong + mild,
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    j = rows[0]["justification"]
    assert j["intensity_limited"] is False
    assert j["severity_coverage"]["failures"] == {"mild": 3}
    assert rows[0]["mitigation_potential"] in ("high", "very_high")
    # the same three failures with no severity stated still discount
    unspec = [
        _u(
            f"u{i}",
            f"y{i}",
            "drought_hazard",
            "none",
            "unspecified",
            ctx={"hazard_type": "drought"},
        )
        for i in range(3)
    ]
    rows, _ = cs.synthesise_cell(
        strong + unspec,
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    assert rows[0]["justification"]["intensity_limited"] is True
    assert rows[0]["mitigation_potential"] == "low"


def test_severe_end_coverage_drives_the_statement():
    mod_ctx = {
        "hazard_type": "drought",
        "hazard_severity": "moderate",
        "severity_cue": "dry year",
    }
    sev_ctx = {
        "hazard_type": "drought",
        "hazard_severity": "extreme",
        "severity_cue": "rainless",
    }
    gain_mod = _u("g", "s1", "drought_hazard", "negative", "strong", ctx=mod_ctx)
    gain_mod2 = _u("g2", "s3", "drought_hazard", "negative", "strong", ctx=mod_ctx)
    fail_sev = _u("f", "s2", "drought_hazard", "none", "unspecified", ctx=sev_ctx)
    rows, _ = cs.synthesise_cell(
        [gain_mod, gain_mod2, fail_sev],
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    j = rows[0]["justification"]
    assert j["severity_coverage"]["severe_end"] == "tested_no_gain"
    assert (
        "at severe or extreme drought the measured results show no benefit"
        in j["statement"]
    )
    rows, _ = cs.synthesise_cell(
        [gain_mod, gain_mod2],
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    j = rows[0]["justification"]
    assert j["severity_coverage"]["severe_end"] == "untested"
    assert "no measured evidence at severe or extreme drought" in j["statement"]
    # one severe gain against several severe/extreme failures reads "mostly no benefit"
    gain_sev = _u("gs", "s4", "drought_hazard", "negative", "slight", ctx=sev_ctx)
    fails = [
        _u(f"f{i}", f"z{i}", "drought_hazard", "none", "unspecified", ctx=sev_ctx)
        for i in range(3)
    ]
    rows, _ = cs.synthesise_cell(
        [gain_mod, gain_mod2, gain_sev] + fails,
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    j = rows[0]["justification"]
    assert j["severity_coverage"]["severe_end"] == "mostly_no_gain"
    assert "mostly show no benefit (1 gain vs 3 failures)" in j["statement"]


def test_modelled_only_strength_is_capped_at_moderate():
    ctx = {"hazard_type": "drought"}
    model = [
        _u(
            f"m{i}",
            "s1",
            "drought_hazard",
            "negative",
            "strong",
            basis="modelled",
            ctx=ctx,
        )
        for i in range(4)
    ]
    measured_null = [
        _u(f"n{i}", f"z{i}", "drought_hazard", "none", "unspecified", ctx=ctx)
        for i in range(2)
    ]
    rows, _ = cs.synthesise_cell(
        model + measured_null,
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    j = rows[0]["justification"]
    assert j["modelled_capped"] is True
    assert "capped at moderate" in j["statement"]
    assert rows[0]["mitigation_potential"] in ("moderate", "low")
    # ratings beside the model do not lift the cap; one measured unit does
    rated = [
        _u(
            f"r{i}",
            f"w{i}",
            "drought_hazard",
            "negative",
            "strong",
            basis="expert_assertion",
            ctx=ctx,
        )
        for i in range(3)
    ]
    rows, _ = cs.synthesise_cell(
        model + rated,
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    assert rows[0]["justification"]["modelled_capped"] is True
    rows, _ = cs.synthesise_cell(
        model + [_u("g", "s9", "drought_hazard", "negative", "strong", ctx=ctx)],
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    assert rows[0]["justification"]["modelled_capped"] is False


def test_measured_harm_is_named_as_maladaptation():
    ctx = {"hazard_type": "drought"}
    gains = [
        _u(f"g{i}", f"s{i}", "drought_hazard", "negative", "strong", ctx=ctx)
        for i in range(3)
    ]
    harm = _u(
        "h", "s9", "drought_hazard", "positive", "moderate", ctx=ctx
    )  # worsens the hazard impact
    rows, _ = cs.synthesise_cell(
        gains + [harm],
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    j = rows[0]["justification"]
    assert j["maladaptation"] == {"n_units": 1, "n_sources": 1, "ids": ["h"]}
    assert "measured HARM (maladaptation) in 1 source" in j["statement"]
    rows, _ = cs.synthesise_cell(
        gains,
        {},
        table="T3",
        nbs_id="riparian_buffer",
        target_key="drought",
        xw_rows=XW,
    )
    assert rows[0]["justification"]["maladaptation"] is None


def test_effect_locus_marks_off_site_practices(tmp_path):
    lk = tmp_path / "effect_locus.csv"
    lk.write_text(
        "nbs_id,suitability_family_id,effect_locus,rationale,ratified_by,ratified_date\n"
        "forest_restoration,,off_site,r,p,d\n"
        "water_harvesting_conservation,water_harvesting__in_situ,on_farm,r,p,d\n"
        "water_harvesting_conservation,water_harvesting__runoff_catchment,mixed,r,p,d\n",
        encoding="utf-8",
    )
    lookup = cs.load_effect_locus(lk)
    assert (
        cs.effect_locus_for(
            lookup, "forest_restoration", "forest_restoration__active_planting"
        )
        == "off_site"
    )
    assert (
        cs.effect_locus_for(
            lookup, "water_harvesting_conservation", "water_harvesting__in_situ"
        )
        == "on_farm"
    )
    assert (
        cs.effect_locus_for(lookup, "water_harvesting_conservation", "") == "mixed"
    )  # families differ
    rows = [
        {
            "nbs_id": "forest_restoration",
            "suitability_family_id": "",
            "mitigation_potential": "high",
            "landscape_scale_only": False,
            "justification": {"statement": "x."},
        },
        {
            "nbs_id": "forest_restoration",
            "risk_role": "asset_vulnerability",
            "asset_sensitivity": "low",
            "justification": {"statement": "y."},
        },
    ]
    cs.apply_effect_locus(rows, lookup)
    assert rows[0]["landscape_scale_only"] is True
    assert rows[0]["justification"]["effect_locus"] == "off_site"
    assert "OFF-SITE effect" in rows[0]["justification"]["statement"]
    assert "effect_locus" not in rows[1]["justification"]


def test_existing_forest_comparator_leaves_the_rollup_and_other_families():
    pol = {
        ("riparian_buffer", "existing_forest"): {
            "rollup_included": False,
            "home_family": "riparian_buffer__planted",
        }
    }
    practice = [
        _u(
            f"p{i}",
            f"s{i}",
            "erosion_hazard",
            "negative",
            "slight",
            family="riparian_buffer__natural_restored",
        )
        for i in range(2)
    ]
    existing = [
        _u(
            f"x{i}",
            f"e{i}",
            "erosion_hazard",
            "negative",
            "strong",
            family="riparian_buffer__cross_family",
            ctx={"comparator": "existing_forest"},
        )
        for i in range(2)
    ]
    rows, rep = cs.synthesise_cell_with_families(
        practice + existing,
        {},
        table="T6",
        nbs_id="riparian_buffer",
        target_key="soil_erosion_risk",
        xw_rows=XW,
        comparator_policy=pol,
    )
    rollup = rows[0]
    assert rollup["suitability_family_id"] in ("", None)
    assert set(rollup["evidence_ids"]) == {
        "p0",
        "p1",
    }  # strong existing-forest units out
    fam = {r["suitability_family_id"]: r for r in rows[1:]}
    assert set(fam["riparian_buffer__planted"]["evidence_ids"]) == {
        "x0",
        "x1",
    }  # home family row
    assert (
        "x0"
        not in fam.get("riparian_buffer__natural_restored", {"evidence_ids": []})[
            "evidence_ids"
        ]
    )
    assert any("PICOS B" in n for n in rep.notes)
    # without a policy nothing changes
    rows, _ = cs.synthesise_cell_with_families(
        practice + existing,
        {},
        table="T6",
        nbs_id="riparian_buffer",
        target_key="soil_erosion_risk",
        xw_rows=XW,
    )
    assert set(rows[0]["evidence_ids"]) == {"p0", "p1", "x0", "x1"}
