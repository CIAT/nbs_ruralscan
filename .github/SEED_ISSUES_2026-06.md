# Backlog update — June 2026

New issues to open, reflecting the v0.6 mockup, the project disaster-risk lens (M2b), the move off native GEE, and the doc reconciliation. Copy each block into a new issue. M2b itself has its own block in [`SEED_ISSUE_M2b_project_risk.md`](./SEED_ISSUE_M2b_project_risk.md) — open that one too.

Milestones: Phase 2 — Methodology Development · Phase 3 — Piloting.

---

## A — Priority-variable normalization decision (blocks Priority Hotspots)

**Title:** `[Decision] Priority-variable normalization + reference frame (M4 / T5)`
**Assignees:** @brayden @pete @benson
**Labels:** `methodology`, `M4-hotspots`, `schema`, `priority-high`
**Milestone:** Phase 2

> Lock how priority variables are standardised to 0–1, since this defines what a hotspot *means*. Decide per-variable in T5: method (`fixed-threshold | min-max | percentile/quantile | z-score`), direction, and — for statistical methods — the **reference frame** (AOI / regional / global / fixed baseline). Recommendation: default to **percentile within the AOI**, use fixed thresholds where a credible standard exists (IPC, SPEI classes), and always surface the reference frame in the UI + map caption. Output: a short M4 spec section + T5 fields. See the Variable Config "Priority / hotspot variables" surface in the wireframe.

---

## B — Integrate Project Risk as a Hotspots scope (depends on M2b)

**Title:** `[Feature] Project-Risk scope on Priority Hotspots`
**Assignees:** @brayden @pete
**Labels:** `M4-hotspots`, `methodology`, `wireframe`, `priority-medium`
**Milestone:** Phase 2

> Wire the M2b project-risk rating into Priority Hotspots as a **third scope** (filter), alongside NbS Suitability Scope and Priority Scope — exclude/flag high-risk areas. Applied as a *filter, never summed* (preserves the double-count guard; see M2b spec §7–§8). Blocked on the M2b schema RFC (`risk_role`/`asset_fragility`/`risk_lens`). Add the matching comparison dimension on NbS Comparison.

---

## C — Author Next Steps (M6) content

**Title:** `[Module Spec] M6 Implementation Hand-off — author content`
**Assignees:** @sarah-jones @evert-thomas @chris-kettle @hannes-gaisberger @pete @namita
**Labels:** `module-spec`, `M6-handoff`, `methodology`, `priority-medium`
**Milestone:** Phase 3

> The Next Steps tab exists but lacks the doc-mandated content. Add, per Stocktake §5 + Table 6: feasibility **methods & tools** (IPCC carbon, RUSLE, InVEST/ARIES, CBA) as guidance notes; the **proportionality** principle; the **right-tree-right-place** design step; MFL signposting; an explicit scoping-boundary line; and traceability from each next step to the tool layer it builds on. Short guidance notes, not a prescriptive methodology.

---

## D — Author the lagging module specs (UI is ahead of methodology)

**Title:** `[Module Spec] Author M3, M4, M5 specs to match the built UI`
**Assignees:** @namita @benson @brayden @pete
**Labels:** `module-spec`, `methodology`, `priority-high`
**Milestone:** Phase 2

> M3 (Characterisation), M4 (Priority Hotspots), M5 (Scorecard / "What this NbS can address") are implemented in the v0.6 mockup but their specs are still TBD. Author each (inherit M1/M2 structure; I/O contract; schema tables). Fold the normalization decision (issue A) into M4. This closes the gap where the tool is ahead of the written method.

---

## E — Ratify the v0.6 tab structure

**Title:** `[Governance] Ratify v0.6 wireframe tab structure`
**Assignees:** @pete
**Labels:** `documentation`, `wireframe`, `priority-low`
**Milestone:** Phase 2

> The mockup now has Setup · Opportunity Space · Project Risk · Priority Hotspots · NbS Comparison · Next Steps + Danger Zone + Dev Notes — beyond the originally "locked" set. Confirm with the team and update CLAUDE.md / docs/README.md "what is locked" (already drafted in the June reconciliation commit) so the governance docs are canonical.

---

## F — Finish the GEE → Python cleanup

**Title:** `[Chore] Remove residual native-GEE framing from code & recipes`
**Assignees:** @brayden @pete
**Labels:** `documentation`, `chore`, `priority-low`
**Milestone:** Phase 2

> Docs reconciled in June (README, CLAUDE.md, pipeline.html). Remaining: reword Issue 9 (#9) to "implement MCDA in Python pulling GEE data"; close/park the GEE App spec (#13); sweep recipe/pipeline READMEs for "native GEE pipeline" language; confirm the wireframe's "Runs in Python" wording (Dev Notes item).
