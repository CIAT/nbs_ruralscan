# M6 — Implementation Hand-off

**Module spec sheet · v0.1 draft · June 2026**

| Field | Value |
|---|---|
| **ID** | M6 |
| **Module** | Implementation Hand-off |
| **Owner(s)** | MFL team (Sarah Jones · Chris Kettle · Evert Thomas · Hannes Gaisberger) · Pete · Namita |
| **Status** | Draft — authored to match the v0.6 wireframe (Next Steps tab) |
| **Schema tables consumed** | T0 · T6 (+ M4 ranked units, M5 economic archetype) |
| **Schema tables produced** | (none — narrative + guidance content) |
| **Position in pipeline** | terminal — reads `nbs_id` + M4/M5 outputs; renders the Next Steps tab |

> M6 is the **narrative bridge from scoping to feasibility**. It is *content*, not computation: short, targeted guidance notes that point to the tools, consultations and feasibility analyses a project team would commission next. It is the project's **scope boundary** — scoping stops here; feasibility starts downstream. Grounded in Stocktake §5 ("From Scoping to Feasibility") + Table 6.

---

## 1. Purpose

For a selected NbS (or a stacked NbS cluster), M6 renders the hand-off from this scoping tool to the feasibility stage: a four-stage pathway (Scoping → Pre-feasibility → Feasibility & design → Implementation), an indicative economic snapshot (from M5/T6), recommended next steps, the **feasibility methods & tools** to use, and country-/NbS-specific tailoring. The intent is to tell a TTL — and the MFL/sector team — *what to do next and which methods to reach for*, without pretending to be a feasibility assessment.

## 2. Question answered

> *"Scoping is done — what comes next for this NbS here: which validation, consultations, and feasibility analyses, using which methods and tools?"*

What M6 explicitly **does not** do (the scope boundary):

- It is **not** a feasibility assessment, ecosystem-service model, or cost-benefit analysis. It *points to* those (Stocktake Table 6) — they are downstream.
- It does not imply every scoped NbS proceeds to feasibility.
- The economic snapshot is an **indicative archetype** (M5/T6), not a CBA.

## 3. Inputs

| Input | Source | Schema | Notes |
|---|---|---|---|
| Selected NbS / cluster | M0 | `T0.nbs_id` | Per-NbS, or a stacked cluster where several overlap |
| Economic archetype | M5 | T6 | Indicative cost band, time-to-income, revenue, financing archetype |
| Ranked priority units | M4 | `tables/hotspots_ranked.csv` | Seeds "validate priority districts in the field" |
| MFL method/tool library | content | T6 / docs | Valuation methods (Table 6), right-tree-right-place, domain pointers |
| Context notes | content | T0 / docs | Country/NbS-specific guidance (e.g. Sierra Leone FSRP) |

## 4. Outputs

| Output | Format | Path / surface | Consumer |
|---|---|---|---|
| Stage pathway | UI | Next Steps tab | Sets the scoping → feasibility → implementation boundary |
| Indicative economic snapshot | from M5 | Next Steps card | Cost / benefit-cost / payback — planning-level, clearly caveated |
| Recommended next steps | content | Next Steps list | Tagged PRE-FEAS / FEASIBILITY, each tied to the tool layer it builds on |
| Feasibility methods & tools | content | Next Steps "methods" block | Valuation families (Table 6) + right-tree-right-place + proportionality note |
| Per-NbS hand-off card | content | Next Steps | Methods · consultations · feasibility analyses to commission · design step |
| Context tailoring | content | Next Steps panel | Country/NbS-specific guidance; links to the Opportunity Space what-if |

## 5. Dependencies

**Upstream:** M4 (ranked units), M5 (economic archetype). Content authored by the MFL/sector team.

**Downstream:** terminal. Hands off to the real feasibility stage (outside the tool).

## 6. Content structure (sub-steps)

1. **Stage pathway** — Scoping (you are here) → Pre-feasibility → Feasibility & design → Implementation; each stage states what it adds.
2. **Indicative economic snapshot** — render M5/T6 archetype (cost band, benefit-cost, payback) with an explicit "planning-level, full CBA at feasibility" caveat.
3. **Recommended next steps** — validate priority units in the field (from M4 ranks); stakeholder & tenure mapping; full cost-benefit & financing scan; safeguards/ESG screening — each traced to the tool layer it builds on. **Confirm country-endorsed data sources** for any variable flagged `context_sensitivity = high` in VONT (population, poverty, production stats): scoping used a global default; feasibility should validate/replace it with a source the country accepts. Scoping *flags* this; it does not negotiate or validate the figures.
4. **Feasibility methods & tools (guidance notes)** — signpost the valuation toolbox from Stocktake Table 6, grouped: nature-based (IPCC Tier 1–3 carbon, RUSLE erosion, InVEST/ARIES/Co$tingNature), and integrated (CBA, MCDA). Tool names are quiet references, not endorsements. Include the **proportionality principle**: simple methods (benefit transfer, proxy indicators) suffice early; reserve detailed spatial modelling for high-priority sites.
5. **Design step (tree-based NbS)** — "right-tree-right-place": species/mixture selection, establishment feasibility, future-climate resilience — authored with the MFL sector team (Evert species, Chris biodiversity, Hannes diversification, Sarah ES).
6. **Context tailoring** — country/NbS-specific guidance; cross-link to the Opportunity Space what-if (e.g. enabling-environment / road investment relaxing a constraint — Laurent's [LF15] point).
7. **Scope-boundary statement** — explicit line: the tool stops at scoping; next steps are indicative; not all scoped NbS proceed.

## 7. Content sourcing

Authored by the MFL/sector team + Pete + Namita as **short, targeted guidance notes** (Stocktake §5 wording), not a prescriptive analytical methodology. Each next-step / method entry cites its basis (Table 6 / domain method). Placeholders are honest where content is still to be authored; each authored slot has a labelled structure (methods · consultations · feasibility analyses · design step).

## 8. Tests / acceptance criteria

- [ ] Stage pathway renders with the scoping boundary explicit.
- [ ] Economic snapshot traces to the T6 archetype and is labelled planning-level (not a CBA).
- [ ] Methods block signposts feasibility tools (not just activities) with the proportionality caveat.
- [ ] Right-tree-right-place design step present for tree-based NbS; MFL signposting included.
- [ ] Each recommended next step is tied to a specific tool output (e.g. "validate Kenema/Kailahun/Bo = VH suit ∩ hotspot").
- [ ] `context_sensitivity = high` variables are listed for country-endorsed source confirmation (flag, not validation).
- [ ] Per-NbS / stacked-cluster tailoring supported.

## 9. Definition of done

- [ ] T6 economic archetype + MFL method library populated for the NbS
- [ ] Guidance notes authored + reviewed by the MFL team
- [ ] Scope-boundary statement agreed (defensible to WB — Laurent/Dinara)
- [ ] Next Steps tab renders for agroforestry Sierra Leone and one comparison NbS

## 10. Implementation notes

M6 is primarily content (markdown/T6 + UI), not a compute module. Minimal logic:

```python
def handoff_card(nbs_id, t0, t6, ranked_units, economic_profile) -> dict:
    """Assemble the per-NbS hand-off card: economic snapshot, next steps (tied to
    tool layers), feasibility methods (Table 6), design step, context tailoring."""

def stacked_cluster_card(nbs_ids, ...) -> dict:
    """Hand-off for a stacked NbS cluster where several NbS overlap spatially."""
```

## 11. Open questions

1. Method library home — a T-table (structured) vs markdown guidance notes (flexible)? (Current: notes + T6 economic fields.)
2. How prescriptive to be on tool choice — list options (current) vs recommend per NbS/context.
3. Stacked-cluster hand-off — how to combine per-NbS guidance when several overlap (e.g. the south-east 4-NbS overlap).

---

## Version history

- **v0.1** (June 2026) — authored to match the v0.6 wireframe Next Steps tab and Stocktake §5 + Table 6. Content/guidance module (no heavy compute); the project's scope boundary. Closes the M0–M6 spec set.
