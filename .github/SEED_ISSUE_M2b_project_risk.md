# Seed issue — M2b Project Disaster Risk Screen

Copy the block below into a new issue at github.com/CIAT/nbs_ruralscan/issues/new (Module Spec template). It carries an embedded schema RFC, so it also satisfies the "new columns require an RFC issue" rule in `schema/README.md`.

---

**Template:** Module Spec
**Title:** `[Module Spec] M2b Project Disaster Risk Screen`
**Assignees:** @brayden @pete
**Labels:** `module-spec`, `M2-climate-risk`, `methodology`, `schema`, `priority-high`
**Milestone:** Phase 2 — Methodology Development

**Body:**

## Module

**ID:** M2b (addendum to M2)
**Name:** Project Disaster Risk Screen
**Owner(s):** @brayden (lead, climate methods) · @pete (oversight)
**Status:** todo — spec drafted (`methodology/modules/M2b_project_risk.md`), method to confirm

## Purpose

Add the **World Bank Climate & Disaster Risk Screening** lens called for in Stocktake §4.7–§4.8. M2b produces an indicative spatial surface of **risk to the NbS investment itself** (where disasters could damage or destroy the asset) — deliberately separate from M2, which is risk to rural *livelihoods* (the need lens). Spec: [`methodology/modules/M2b_project_risk.md`](../methodology/modules/M2b_project_risk.md).

The crux distinction (worth internalising before coding): the **same hazard can play opposite roles**. For wetland creation, flooding is a *need* driver in M2 (the wetland mitigates it for livelihoods) but a storm surge is an *asset threat* in M2b (it could destroy the wetland). M2 uses hazards the NbS *mitigates*; M2b uses hazards that *threaten the asset* and the NbS does *not* mitigate.

## Schema RFC (please review before authoring rows)

- **T3** (NbS × Hazard × Farming System): add
  - `risk_role` ∈ `{livelihood_mitigation | asset_threat | both | neutral}`
  - `asset_fragility` (0–1 / Likert) — how damageable this NbS is by the hazard
- **T2** (Climate Risk Formulation): add
  - `risk_lens` ∈ `{livelihood | project | shared}`
  - extend `risk_component` enum with `asset_exposure` (investment footprint + supporting infrastructure)
- No existing column meanings change. Legacy defaults: `risk_role = livelihood_mitigation`, `risk_lens = livelihood` (preserves current M2 behaviour).

## Combination stance (do not break this)

M2b is a **filter / scope**, never summed into the suitability or hotspot score. Therefore sharing a hazard variable with M2 or with the suitability recipe is **allowed** — it's a check-and-balance, not double-counting. The only prohibition: don't add the project-risk score as another additive MCDA term sharing those variables. See spec §7.

## Build order

1. Confirm method + schema RFC (this issue).
2. Standalone **Project Risk tab** in the wireframe (per the Claude Design dispatch).
3. Wire the rating in as a **third "Project-Risk scope"** on Priority Hotspots (alongside NbS Suitability Scope and Priority Scope) — exclude/flag High/Very-High areas.

## Decisions to settle (spec §11)

- [ ] Rating composition: multiplicative (`H × E × fragility`) vs additive/weighted?
- [ ] Asset-exposure proxy: opportunity-space mask (suitability-weighted) vs flat candidate-area mask?
- [ ] Source of `asset_fragility`: literature from T6/T3 vs small expert-elicited table?
- [ ] Institutional/social constraints (conflict, cohesion) — in v0 or deferred?
- [ ] On-by-default or opt-in?

## Acceptance criteria

- [ ] Reads all rules from schema (T1–T3, T7); nothing hardcoded.
- [ ] T3 `risk_role`/`asset_fragility` and T2 `risk_lens`/`asset_exposure` added via migration PR.
- [ ] Produces baseline + future project-risk rasters + overall rating + ranked-unit table for agroforestry Sierra Leone.
- [ ] "No screened asset hazards" NbS returns an explicit low-risk/empty state, not a blank raster.
- [ ] Double-count guard still passes (shared hazard across lenses is permitted; additive re-use is not).
- [ ] Outputs framed as *indicative screen*, with the full WB project-level screening pointed to in M6 / Next Steps.

## Definition of done

- [ ] Spec reviewed by Pete + Brayden
- [ ] Schema RFC accepted; migration PR merged
- [ ] Implementation issue linked (pipeline)
- [ ] Standalone Project Risk tab shipped in wireframe
