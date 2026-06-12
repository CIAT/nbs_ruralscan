# M5 — NbS Scorecard & Response

**Module spec sheet · v1.0 · June 2026**

| Field | Value |
|---|---|
| **ID** | M5 |
| **Module** | NbS Scorecard & Response |
| **Owner(s)** | Namita Joshi (lit + content) · MFL team (Likert + economic input) · Pete (oversight) |
| **Status** | Ratified — v1.0 |
| **Schema tables consumed** | T3 · T6 (+ M3 problem-variable distributions) |
| **Schema tables produced** | (none — renders schema rows) |
| **Position in pipeline** | reads `nbs_id`; renders alongside M3 in Opportunity Space; feeds NbS Comparison and Next Steps |

> M5 is **qualitative**. It renders how strongly an NbS responds to development outcomes (Likert, from T6) and its indicative **economic archetype** (T6). It is *not* ecosystem-service modelling or cost-benefit analysis — those are downstream (M6). The economic profile is an indicative archetype an economist can relate to, not a CBA.

---

## 1. Purpose

For a selected NbS, M5 renders the **NbS response scorecard** — a qualitative rating (Likert: ++ · + · 0 · − · −−) of how strongly the NbS addresses each development outcome (erosion, drought resilience, biodiversity, carbon, rural income, food security, fire-risk caution) — together with an **indicative economic archetype** (establishment cost band, time-to-first-income, revenue streams, financing implication). It powers the "What this NbS can address" panel, the economic-archetype card, and the response/economic rows in NbS Comparison.

## 2. Question answered

> *"What can this NbS plausibly do for development outcomes here, how strongly, and what is its basic economic shape?"*

What M5 explicitly **does not** do:

- Quantify benefits or returns (no ES valuation, no CBA — M6 points to those).
- Decide where the NbS works (M1) or prioritise locations (M4).
- Assess investment risk (M2b).

## 3. Inputs

| Input | Source | Schema | Notes |
|---|---|---|---|
| Selected NbS | M0 Setup | `T0.nbs_id` | |
| Mitigation potential matrix | T3 | `T3` rows for `nbs_id` | NbS × outcome/hazard qualitative response (Likert), with confidence |
| Scorecard + economic archetype | T6 | `T6` rows for `nbs_id` | Likert effects per outcome; establishment cost band; recurring cost; time-to-first-income; revenue streams; financing archetype |
| Problem-variable distribution | M3 | `tables/characterisation.csv` | To pair "problem present in opp space" × "response strength" |

## 4. Outputs

| Output | Format | Path | Consumer |
|---|---|---|---|
| Scorecard table | CSV | `…/tables/scorecard.csv` | "What this NbS can address" panel; NbS Comparison response rows |
| Economic profile | JSON | `…/tables/economic_profile.json` | Economic archetype card; Next Steps indicative cost-benefit; NbS Comparison economic rows |
| Scorecard metadata | JSON | `…/scorecard_meta.json` | T3/T6 row versions, confidence flags, provenance |

## 5. Dependencies

**Upstream:** M3 (problem-variable distributions, to contextualise response against present problems).

**Downstream:** Opportunity Space tab ("What this NbS can address"); NbS Comparison (response + economic rows); Next Steps / M6 (indicative cost-benefit is sourced from this archetype, clearly marked planning-level).

## 6. Sub-steps

1. **Load response matrix** — read T3 Likert effects for `nbs_id` per outcome/hazard, with confidence.
2. **Pair with problem severity** — join M3's problem-variable distribution so each outcome shows *problem present in the opp space* (bar) × *response strength* (Likert chip). This is the "what this NbS can address, where the problem is" read.
3. **Render economic archetype** — read T6 economic fields: establishment-cost band, recurring cost, time-to-first-income, revenue streams, financing archetype (e.g. "Long Horizon — patient/blended capital").
4. **Assemble comparison rows** — emit the scorecard + economic profile in the shape NbS Comparison consumes (one column per NbS).
5. **Flag cautions** — surface negative/caution Likert entries (e.g. fire risk during establishment) explicitly, not buried.

## 7. Variable / content sourcing

T3 and T6 content is literature- and expert-derived (Namita + MFL team). Each Likert entry carries a confidence flag and source; the economic archetype cites its basis. Qualitative ratings are the deliverable — precision beyond Likert is out of scope for scoping.

## 8. Tests / acceptance criteria

- [ ] Reads T3/T6 for `nbs_id`; nothing hardcoded.
- [ ] Every rendered outcome has a Likert value + confidence + source.
- [ ] Economic archetype card populated (cost band, time-to-income, revenue, financing).
- [ ] Caution entries (negative Likert) are surfaced explicitly.
- [ ] Comparison rows render for ≥ 2 NbS consistently.
- [ ] Indicative cost-benefit in Next Steps is traceable to the T6 archetype and labelled planning-level.

## 9. Definition of done

- [ ] T3 + T6 rows populated and reviewed for the NbS
- [ ] Likert entries carry confidence + provenance
- [ ] Economic archetype agreed with MFL/economist input
- [ ] Panels render for agroforestry Sierra Leone and at least one comparison NbS

## 10. Implementation notes (Python)

> **Schema state when this spec is picked up (v0.3.0+, June 2026):** several T6 and T5 fields the v0.1 draft assumed-pending have since landed. **Read this before implementing.**
>
> | Draft assumption | Current state |
> |---|---|
> | Module path `pipeline/scorecard.py` | **Updated** → `src/nbs_ruralscan/runtime/scorecard.py` per the v0.2 GEE-App-dropped runtime. Mostly table assembly; no heavy compute. |
> | T6 effect rows | **Constrained** at v0.3.0: T6 effect rows link **only** to T5 rows where `mcda_role == 'priority'`. The scorecard MUST filter T5 to priorities before pairing — descriptors don't carry effect strengths. |
> | T6 economic profile | **Generalised** at v0.3.0: `economic_indicator_type` extended with `cost_per_beneficiary` · `cost_per_hectare_restored` · `cost_per_tco2e_avoided` · `cost_per_farmer_reached` (indicative, scoping-grade, **not CBA**). `economic_value_range` is now an object `{low, high, unit, source_note}` with `unit` enum-policed. Render whatever denominators the recipe populated; never compute new ones. |
> | T6 orphans | 2 orphan T5 refs rerouted at v0.3.0-E (`food_security_risk` → `production_gap`; `groundwater_recharge_potential` → `water_stress`). No outstanding orphans. |
> | T3 risk-component fields | **Live**: `risk_role` (mitigates vs causes), `asset_threat`, `asset_risk_weight` shipped at v0.3.0. M5 reads `risk_role` to distinguish hazard-mitigation rows from hazard-causing rows when rendering the scorecard. |
> | iplc_lands flag | If the run had IPLC overlap (M3 `iplc_overlap_flag`), the scorecard's comparison block surfaces the **FPIC/ESS7 caveat** alongside any NbS-vs-NbS comparison — don't hide it inside M6 only. |
> | Likert confidence | T6 carries `confidence` (`high` · `medium` · `low`) plus `evidence_ids` linking back to EV rows. Surface confidence per cell; per #32, cost-effectiveness denominators arrive **scoping-grade** and should default to `confidence = low` until evidence-gathering lands. |

Suggested Python function signatures for `src/nbs_ruralscan/runtime/scorecard.py`:

```python
def load_scorecard(
    nbs_id: str,
    t3: "pd.DataFrame",
    t6: "pd.DataFrame",
    t5_priorities: "pd.DataFrame",  # T5 filtered to mcda_role == 'priority'
) -> "pd.DataFrame":
    """§6.1 — Likert effects per priority/hazard row with confidence + source.
    Filters T6 to rows whose variable_id ∈ t5_priorities (or T3 hazard for
    risk_role='mitigates' rows). Descriptor rows excluded."""

def pair_with_problems(
    scorecard: "pd.DataFrame",
    characterisation: "pd.DataFrame",
) -> "pd.DataFrame":
    """§6.2 — join response strength to M3's problem-present-in-opp-space
    distribution."""

def economic_profile(
    nbs_id: str,
    t6: "pd.DataFrame",
) -> dict:
    """§6.3 — establishment cost band, time-to-income, revenue streams,
    financing archetype + cost-effectiveness denominators
    (cost_per_beneficiary / _ha / _tco2e / _farmer where populated). Renders
    `economic_value_range = {low, high, unit, source_note}` as-is. Labels
    scoping-grade — never CBA."""

def comparison_rows(
    nbs_ids: list[str],
    t3: "pd.DataFrame",
    t6: "pd.DataFrame",
    t5_priorities: "pd.DataFrame",
    iplc_overlap: bool = False,
) -> "pd.DataFrame":
    """§6.4 — response + economic rows shaped for NbS Comparison. Adds
    FPIC/ESS7 caveat column when `iplc_overlap` is True."""
```

## 11. Open questions & decisions

1. **Likert Scale Range:** Maintain the 5-point Likert scale (`++` · `+` · `0` · `−` · `−−`) for qualitative response. If evidence is absent, indicate as "Not Assessed" (`n/a`) in the UI rather than implying neutral (`0`) effect.
2. **Economic Archetype Granularity:** Combine qualitative archetypes (e.g. "Long Horizon") with quantitative cost ranges (`low`, `high`, `unit`, `source_note` via T6 `economic_value_range` object) to represent establishment and recurring costs.
3. **Confidence Level Visibility:** Confidence levels (`high` · `medium` · `low`) are shown per outcome cell to maintain transparency. Cost-effectiveness denominators default to `low` confidence until systematically populated from literature.

---

## Version history

- **v0.1** (June 2026) — authored to match the v0.6 wireframe (scorecard + economic archetype + comparison rows). Qualitative; economic profile is indicative archetype, not CBA (downstream M6).
- **v0.1.1** (June 2026) — annotated §10 with v0.3.0 schema state: T6 effects gated to T5 mcda_role=priority; T6 economic-profile generalisation + cost-effectiveness denominators; T3 risk_role / asset_threat / asset_risk_weight live; T6 orphan reroutes done; iplc_lands FPIC/ESS7 caveat surfaced in comparison rows. Module path → `src/nbs_ruralscan/runtime/scorecard.py`. Function signatures widened. No methodology change.
- **v1.0** (June 2026) — Finalised and ratified module specification. Open questions resolved and aligned with the v0.3.0 schema tables.
