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

---

## Board hygiene — reassignments & closes (apply on the live board)

Not new issues — edits to existing cards, reflecting the ownership shift:

- **#3 M4 spec** — reassign **@benson → @pete** (Pete now owns Priority Hotspots).
- **M6 hand-off** — set **@pete** as lead (MFL team + Namita remain contributors).
- **#9 M1 port** — drop @benson as owner (Benson → QA/QC); implementation is Python via Claude Code (Brayden / Anastasia / Pete). Reword per issue F.
- **#13 GEE App spec** — **close / park** (GEE App dropped).
- Tag **@benson** as **QA/QC reviewer** across modules rather than a module owner.

---

## G — Dedup methodology sign-off (post draft-0)

**Title:** `[Decision] T2/T5 reconciliation after shared-layer dedup`
**Assignees:** @brayden @pete
**Labels:** `methodology`, `schema`, `M2-climate-risk`, `priority-high`
**Milestone:** Phase 2

> The draft-0 dedup collapsed the `_wh` clones into single shared rows (see `schema/DEDUP_NOTES.md`). Three items need methodology sign-off before the pilot review: (1) **T2 baseline risk weights are provisional** — after removing duplicates the merged set was renormalised proportionally to 1.0 (gives agroforestry-origin variables ~64% of weight purely by count); decide the correct combined weighting. (2) **Two flood-hazard methods coexist** in T2 (`flood_exposure_baseline` CHELSA-precip vs `flood_hazard_runoff_depth` SCS-CN) — pick a canonical one or justify both. (3) **`soil_erosion_risk` vs `soil_degradation_risk`** (T5) — confirm distinct or merge.

---

## H — Develop T0–T7 population methods

**Title:** `[Methodology] Reproducible methods to populate the schema tables`
**Assignees:** @namita @brayden @pete @benson
**Labels:** `methodology`, `schema`, `priority-high`
**Milestone:** Phase 2

> The draft-0 tables are placeholders that illustrate the data model; the deliverable is the **methods that populate them** reproducibly per NbS/AOI. Highest-leverage piece: a repeatable, quality-scored **evidence-extraction protocol** feeding T3/T4/T6 (papers → schema-valid rows with justification, references, confidence). Plus a **dataset-curation protocol** for T1/T7 (fitness-for-purpose, 3-tier sourcing, resolution audit — Benson QA/QC) and **operationalising the weighting/clustering** for T2/T4/T5 (already half-specified in the framework primitives). T7 contexts and T0 are largely adopt/template.

---

## Schema status (informational)

> Schema is now **v0.2** (committed). Added since v0.1: `T3.risk_role` + `asset_risk_weight` (M2 / M2b two-risk split), `T5.theme` + `weight_default` (hotspot grouping/weighting), canonical `T4.relationship_type` set, the shared-layer dedup, **and the evidence & configuration layer** (Source / Evidence / Variable-Ontology / Subpractice-Family registers; T4 keyed to `suitability_family_id`). This **defines** the fields issues **A** (T5 priority-variable fields) and **B** (`risk_role` for M2b) called for — design-complete at the schema level; **populating** with real values is part of issue **H**.

---

## T4 build stream (June 2026 — method = `methodology/T4_generation_method.md`)

**I — Family scheme review (blocks the build).**
**Assignees:** @namita (+ consult MFL: @sarah-jones @chris-kettle @evert-thomas @hannes-gaisberger)
**Labels:** `methodology`, `priority-high`
> Review and sign off the agroforestry suitability families (F1 planted silvoarable · F2 regeneration-based · F3 silvopastoral · F4 linear/boundary · F5 shaded perennial-crop · homegardens `qualitative_only` · riparian split to its own NbS). Grouping criterion = shared dominant limiting factor. Confirm or revise before extraction is built on it.

**J — Build `doc-ingestion` pipeline (vectorless, structure-aware).**
**Assignees:** @brayden @anastasia @pete (Claude Code)
**Labels:** `pipeline`, `priority-high`
> `src/nbs_ruralscan/ingest`: PDF → page-tagged text + structure index (sections/tables/figures w/ captions+pages) + parsed tables; OCR fallback; keyword/structure (vectorless) retrieval; targeted figure-vision. Cache **gitignored** (copyright). Recovers table-bound thresholds (e.g. Ahmad 2018, Haile 2024).

**K — Depth-first F1 (alley-cropping first) → first full agroforestry recipe.**
**Assignees:** @namita @pete (Claude)
**Labels:** `methodology`, `recipe`
> After the slope slice, complete all F1 variables starting with alley-cropping-type silvoarable; produce the first complete per-family T4 recipe with full provenance.

**L — Per-table extraction contracts (enables extract-once).**
**Assignees:** @namita @brayden @pete
**Labels:** `methodology`, `schema`
> Author the T3 (mitigation matrix), T5 (priority-layer) and T6 (effects) extraction sub-instructions/skills so one paper read populates multiple tables correctly. T4 leads; others follow once contracts exist.

**M — Water-harvesting taxonomy.**
**Assignees:** @pete @brayden
**Labels:** `methodology`
> Build the WH subpractice → suitability-family taxonomy (second NbS), reusing existing standards (FAO land eval, WOCAT/SLM, GAEZ, Dixon farming systems) rather than inventing. Use the prior WH methodological plan (`Methodology/Claude/Spatial_Methodological_Plan_Water_Harvesting_NbS_v1.docx`) as a **`scoping_candidate` reference only** — it proposes candidate variables + subpractice structure but carries **no decision history** to justify variable selection, so every variable must be substantiated through the evidence layer (the 85 WH stocktake PDFs). Reference, not justification.

**Done this session:** corrected the draft-0 agroforestry slope row (abs_max 45°→30°, unit-conflation fix) — see the slope worked example.

---

## v0.2.6 sharpenings backlog (June 2026 — corpus + adoption-evidence sequencing)

**N — T6 bounded-corpus discovery pass (effectiveness + conditionality).**
**Assignees:** @namita @pete (Claude support)
**Labels:** `methodology`, `discovery`, `t6`
> Assemble the **T6 bounded seed-set** per the v0.2.6 rule (`methodology/T4_generation_method.md` §3): WB rural-NbS catalogue · GEF / NBS Invest · IPCC · FAO · WRI · major meta-analyses · **MEL/MELIA reports** · CSA adoption & barriers dataset. Tier each entry against `SRC.benchmark_tier`. Don't sweep 100k abstracts. **Sequenced after T4** — start scoping once F1 (agroforestry, planted silvoarable) is complete. Output: a `schema/registers/CV_t6_seed_agroforestry.csv` (or per-NbS) mirroring the structure of the v0.6 T4 candidate-variable register.

**O — T3 bounded-corpus discovery pass (hazard mitigation + vulnerability).**
**Assignees:** @brayden @pete
**Labels:** `methodology`, `discovery`, `t3`
> Same as N but for T3: hazard-resilience + vulnerability literature; IPCC AR6 WGII Ch.2/3; CGIAR-CCAFS climate-resilience reviews. Brayden's M2 lit is the spine. Sequenced after T4. Output: per-NbS T3 seed-set CSV.

**P — Ingest the CSA adoption & barriers dataset (Aggarwal et al. + successors).**
**Assignees:** @namita @pete (Claude Code)
**Labels:** `data`, `methodology`, `discovery`
> Pull the CSA adoption & barriers synthesised dataset into the SRC + EV registers as **observed-reality evidence** (`SRC.method_type = adoption_study`). Per v0.2.6 method §3 evidence-source principle, this feeds T4 **system_constraint** / **operational_constraint** variables and T6 conditionality directly. Keep PDFs/full text **off-repo**; only short fair-use quotes + structured EV rows commit. Goal: cover the agroforestry & water-harvesting practices for the pilot.

**Q — MEL / MELIA seed-set per NbS (large-project synthesis material).**
**Assignees:** @namita (with MFL team: @sarah-jones @chris-kettle @evert-thomas @hannes-gaisberger)
**Labels:** `methodology`, `discovery`, `data`
> Assemble per-NbS the MEL/MELIA reports and synthesis pieces from large CGIAR/donor projects (Kuria, Sida-NbS, Restoration Initiative MEL packs, AFR100, ICRAF MELIA outputs, GEF NBS Invest portfolios). Same ingest path as N/P (`SRC.method_type = mel_report`, observed-reality evidence). Feeds T4 system/operational dimensions + T6 conditionality. Sequence after T4 unless a specific MEL paper is already known to fill a T4 gap.

**Done in v0.2.6:** sharpened `T4.suitability_dimension` (3 ordered definitions); fixed draft-0 mislabels (`land_cover` → system; `distance_to_road` → operational; `permanent_water` → operational); added enum_values policing for `suitability_dimension` + `relationship_type`; extended `SRC.method_type` with `adoption_study` + `mel_report`; method-doc §3 bounded seed-set + §2.7 hard-vs-soft reconcile (resolves the stocktake Fig 9 tension); CLAUDE.md + READMEs + docs cascade.

---

## v0.2.7 discovery-and-evidence-sourcing SOP backlog (June 2026)

**R — WOCAT seed-set per NbS (SLM technologies database).**
**Assignees:** @namita @pete (Claude Code)
**Labels:** `methodology`, `discovery`, `data`
> Assemble per-NbS the WOCAT (World Overview of Conservation Approaches and Technologies) SLM-technology entries that match the family scheme. **LMIC-grounded**, per-practice fact sheets cover **T4 requirements** (climate/soil/topography/land-use) AND **T6 benefits/costs** (impacts, adoption costs, success factors). The highest-yield single class in the seed-set rule (v0.2.7 method §3 diamond classes). Ingest via per-paper sweep; assign `SRC.venue_type = institutional_report`; assess each entry against the six-axis rubric. Goal: cover agroforestry + water harvesting for the pilot.

**S — Evidence Gap Maps ingest (3ie / Campbell / CEE).**
**Assignees:** @namita @pete
**Labels:** `methodology`, `discovery`, `t6`
> Pull pre-mapped intervention × outcome evidence from 3ie / Campbell Collaboration / CEE (Collaboration for Environmental Evidence) for the pilot NbS. EGMs are a shortcut + **honest gaps** — where evidence is missing they say so, which is exactly the input T6 conditionality needs. Map each EGM cell to T6 effect rows via `SRC.method_type = empirical`/`mel_report` (depending on study designs underneath) and `venue_type = institutional_report`. Sequenced after T4.

**T — WB project evidence (PADs / ICRs / IEG reviews).**
**Assignees:** @pete @namita
**Labels:** `methodology`, `discovery`, `data`
> Pull NbS-relevant WB Project Appraisal Documents, Implementation Completion Reports, and Independent Evaluation Group reviews into the SRC + EV registers as **operational-reality evidence** — what the Bank actually funded, what worked, what didn't. Feeds T4 `operational_constraint` + T6 conditionality. `SRC.venue_type = institutional_report`; `SRC.method_type = mel_report` or `adoption_study` depending on doc. Coordinate with the TORs-named tools (D4R, AAAA, MapAWD) and the WB rural-NbS catalogue.

**U — Discovery-log SOP rollout (PRISMA-lite).**
**Assignees:** @pete (Claude support)
**Labels:** `methodology`, `documentation`
> Author the first per-NbS × table discovery logs under `methodology/discovery_logs/`. Start with `agroforestry_T4.md` (retrospective — capture what was done on the 23-paper Stocktake + the F1 sweep) and `water_harvesting_T4.md` (forward-looking — feeds the WH discovery pass when the second NbS comes into scope). Template lives at `methodology/discovery_logs/README.md`. Records search strings, sources queried, dates, PRISMA-lite counts (returned → screened → included). **Markdown, not a schema register** — narrative audit trail at this phase.

**Done in v0.2.7:** added SRC fields `study_income_group` (enum), `is_seminal` (bool), `venue_type` (enum) to make the six-axis credibility rubric auditable; reconciled the C/I/D rubric with the six-axis rubric in spec.md + method doc (one scheme, two views); expanded method §3 with the diamond source classes (WOCAT, EGMs, WB project evidence + TORs tools, ICRAF/Ecocrop/TECA), five-step screening funnel, LMIC tie-break, independence/COI discount, source-type register (economic valuation / gender / maladaptation / BIND-T1 datasets); created `methodology/discovery_logs/` with PRISMA-lite template; CLAUDE.md + READMEs + docs cascade. **Not in scope this batch:** T5 opportunity-space ratification — still waiting on Pete (equity/gender = own theme vs folded into people_production).
