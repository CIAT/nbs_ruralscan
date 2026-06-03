# M5 — NbS Scorecard & Response

**Module spec sheet · v0.1 draft · June 2026**

| Field | Value |
|---|---|
| **ID** | M5 |
| **Module** | NbS Scorecard & Response |
| **Owner(s)** | Namita Joshi (lit + content) · MFL team (Likert + economic input) · Pete (oversight) |
| **Status** | Draft — authored to match the v0.6 wireframe ("What this NbS can address" + Economic archetype + NbS Comparison response rows) |
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

```python
def load_scorecard(nbs_id, t3, t6) -> "pd.DataFrame":
    """§6.1 — Likert effects per outcome/hazard with confidence + source."""

def pair_with_problems(scorecard, characterisation) -> "pd.DataFrame":
    """§6.2 — join response strength to problem-present-in-opp-space distribution."""

def economic_profile(nbs_id, t6) -> dict:
    """§6.3 — establishment cost band, time-to-income, revenue streams, financing archetype."""

def comparison_rows(nbs_ids, t3, t6) -> "pd.DataFrame":
    """§6.4 — response + economic rows shaped for NbS Comparison."""
```

## 11. Open questions

1. Likert scale rendering — keep 5-point (++ · + · 0 · − · −−) or add an explicit "n/a / not assessed"?
2. Economic archetype granularity — fixed archetypes (Long/Medium/Short Horizon) vs per-NbS numeric bands? (Current: archetype label + indicative bands from T6.)
3. How prominently to surface confidence — per-cell flag vs an overall scorecard confidence?

---

## Version history

- **v0.1** (June 2026) — authored to match the v0.6 wireframe (scorecard + economic archetype + comparison rows). Qualitative; economic profile is indicative archetype, not CBA (downstream M6).
