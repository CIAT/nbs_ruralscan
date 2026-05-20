# Seed issues — initial backlog

Copy each block below into a new issue on github.com/CIAT/nbs_ruralscan/issues/new. Pick the right template (recipe / variable-card / module-spec / pilot-task) — the title and labels are pre-filled in each block. Open one at a time.

Open them in roughly this order so the backlog tells a coherent story when the team first sees it.

---

## 1 — Module specs to author with their owners (5 issues)

### Issue 1: M0 Setup spec

**Template:** Module Spec
**Title:** `[Module Spec] M0 Setup & Scope`
**Assignee:** @pete
**Labels:** `module-spec`, `M0-setup`, `methodology`, `priority-medium`
**Milestone:** Phase 2 — Methodology Development

**Body:**
> Draft `methodology/modules/M0_setup.md` following the structure of `M1_suitability.md`. M0 captures the user-facing setup flow — selecting NbS, geography, resolution, climate scenario, mode toggle — and produces the run configuration that downstream modules consume. Should also document the ingestion check (does every required dataset have access / hosting / upload status).
>
> Reference: the wireframe's Setup tab (`docs/wireframe.html`) is the design target.

---

### Issue 2: M3 Opportunity Space Characterisation spec

**Template:** Module Spec
**Title:** `[Module Spec] M3 Opportunity Space Characterisation`
**Assignee:** @namita
**Labels:** `module-spec`, `M3-characterisation`, `methodology`, `priority-medium`
**Milestone:** Phase 2 — Methodology Development

**Body:**
> Draft `methodology/modules/M3_characterisation.md` following the structure of `M1_suitability.md` and `M2_climate_risk.md`. M3 extracts characteristics within the opportunity space — poverty, biodiversity loss, GESI, agricultural production, rural population, farm size proxy. Schema tables consumed: T1, T5. Variables reduced per Ani's principles (Reduce / Source / Explain). Double-count guard ensures variables used here aren't also used in M2.

---

### Issue 3: M4 TTL Hotspots spec

**Template:** Module Spec
**Title:** `[Module Spec] M4 TTL Hotspots (MCDA)`
**Assignee:** @benson
**Labels:** `module-spec`, `M4-hotspots`, `methodology`, `priority-medium`
**Milestone:** Phase 2 — Methodology Development

**Body:**
> Draft `methodology/modules/M4_hotspots.md`. M4 runs a user-weighted MCDA on T5 priority variables within the opportunity space mask from M1. Re-uses the AHP+CRITIC+Entropy weighting engine from M1 with TTL-supplied weights replacing the recipe defaults. Output is a hotspot raster + top-N region list. Schema: T5.
>
> Wireframe's TTL Hotspots tab is the design target.

---

### Issue 4: M5 NbS Scorecard & Response spec

**Template:** Module Spec
**Title:** `[Module Spec] M5 NbS Scorecard & Response`
**Assignee:** @namita
**Labels:** `module-spec`, `M5-scorecard`, `methodology`, `priority-medium`
**Milestone:** Phase 2 — Methodology Development

**Body:**
> Draft `methodology/modules/M5_scorecard.md`. M5 renders the qualitative NbS scorecard (Likert effects from T6 + economic archetype) for the chosen NbS. Schema: T3 (mitigation potential matrix) + T6 (scorecard). Output is a structured table + indicative economic profile.
>
> Wireframe's right-panel scorecard + economic archetype card is the design target.

---

### Issue 5: M6 Implementation Hand-off spec

**Template:** Module Spec
**Title:** `[Module Spec] M6 Implementation Hand-off`
**Assignees:** @sarah-jones @chris-kettle @evert-thomas @hannes-gaisberger @pete
**Labels:** `module-spec`, `M6-handoff`, `methodology`, `priority-low`
**Milestone:** Phase 3 — Piloting

**Body:**
> Draft `methodology/modules/M6_handoff.md`. M6 is the narrative bridge from scoping to feasibility — points to MFL team tools and methods for next-step analysis (Evert's species-level methodology, Chris's biodiversity planning, Hannes's diversification work, Sarah's ecosystem service framing). Schema: T0 + T6.
>
> Output: implementation hand-off card per NbS — what tools to use, what consultations to run, what feasibility analyses to commission.

---

## 2 — Recipe authoring (3 issues)

### Issue 6: Agroforestry recipe (Phase 3 pilot)

**Template:** Recipe
**Title:** `[Recipe] Agroforestry`
**Assignees:** @benson @namita
**Labels:** `recipe`, `agroforestry`, `phase-3-pilot`, `priority-high`
**Milestone:** Phase 3 — Piloting

**Body:**
> Author `methodology/recipes/agroforestry.md` to full draft. Currently a skeleton; needs all 8 sections populated and the master variable table filled (target ~20 variables across 6 themes). Inherit the structure of `water_harvesting.md`.
>
> MFL reviewer: pick Evert (agroforestry / species lead) or Hannes (diversification).

---

### Issue 7: Forest Restoration / ANR recipe

**Template:** Recipe
**Title:** `[Recipe] Forest Restoration & ANR`
**Assignees:** @namita
**Labels:** `recipe`, `forest-restoration`, `phase-2-methodology`, `priority-medium`
**Milestone:** Phase 2 — Methodology Development

**Body:**
> Author `methodology/recipes/forest_restoration.md`. Second priority cluster per the stocktake ranking. Inherit structure from `water_harvesting.md`. Subpractices: assisted natural regeneration · reforestation · afforestation (subpractice family pattern).
>
> MFL reviewer: Sarah (ecosystem services) or Hannes.

---

### Issue 8: Riparian Buffers / Floodplain Management recipe

**Template:** Recipe
**Title:** `[Recipe] Riparian Buffers / Floodplain Management`
**Assignees:** @namita
**Labels:** `recipe`, `riparian-buffer`, `phase-2-methodology`, `priority-medium`
**Milestone:** Phase 2 — Methodology Development

**Body:**
> Author `methodology/recipes/riparian_buffer.md`. Strong stocktake performance (Rank #4 in inception report). Inherit structure from `water_harvesting.md`. Distinct biophysical logic from water harvesting — hydrology / flow accumulation / proximity to streams dominant; soil retention via root systems primary.
>
> MFL reviewer: Sarah.

---

## 3 — Pipeline implementation (2 issues)

### Issue 9: Port spatMCDA.R to mcda_pipeline.py

**Template:** Module Spec (re-purposed; or open a generic issue)
**Title:** `Port spatMCDA.R to GEE Python (mcda_pipeline.py)`
**Assignee:** @benson
**Labels:** `M1-suitability`, `phase-2-methodology`, `priority-high`
**Milestone:** Phase 2 — Methodology Development

**Body:**
> Port `reference/R/spatMCDA.R` to GEE Python at `pipeline/mcda_pipeline.py`. Follow the function signatures listed in `methodology/modules/M1_suitability.md` §13. Each sub-step (§6.1–§6.8) is a separately callable function. Reads recipe + schema rows; runs on GEE assets. Preserve CRITIC + Entropy + AHP weighting logic exactly.
>
> Suggested starting prompt for Claude Code is in the Delivery Architecture & Claude Code Uplift note.

---

### Issue 10: Climate risk implementation (climate_risk.py)

**Template:** Module Spec (re-purposed)
**Title:** `Implement climate_risk.py per M2 spec`
**Assignee:** @brayden
**Labels:** `M2-climate-risk`, `phase-2-methodology`, `priority-high`
**Milestone:** Phase 2 — Methodology Development

**Body:**
> Implement `pipeline/climate_risk.py` per the spec in `methodology/modules/M2_climate_risk.md`. Mode A first; Mode B opt-in. Function signatures in spec §14. Resolves Brayden's six open methodology questions listed at the spec bottom.
>
> Pair-program with Claude Code; the suggested first prompt is in the spec.

---

## 4 — Pilots (2 issues)

### Issue 11: Agroforestry pilot in Sierra Leone

**Template:** Pilot Task
**Title:** `[Pilot] Agroforestry in Sierra Leone`
**Assignees:** @benson @pete
**Labels:** `pilot`, `agroforestry`, `phase-3-pilot`, `priority-high`
**Milestone:** Phase 3 — Piloting

**Body:**
> Apply the methodology to agroforestry in Sierra Leone (FSRP pilot context per Dinara's suggestion). Phase 3 deliverable. Inputs: completed agroforestry recipe; M1 + M2 pipeline implementations. Outputs: Colab notebook + maps + summary tables + fingerprint.
>
> Blocked on: Issue 6 (recipe), Issue 9 (M1 implementation), Issue 10 (M2 implementation).

---

### Issue 12: Second LDC pilot (TBD)

**Template:** Pilot Task
**Title:** `[Pilot] Second LDC pilot — country + NbS TBD`
**Assignees:** @pete @benson
**Labels:** `pilot`, `phase-3-pilot`, `priority-medium`
**Milestone:** Phase 3 — Piloting

**Body:**
> Per proposal: two LDC pilots required. First is agroforestry in Sierra Leone (Issue 11). Second: discuss with WB team (Dinara + Laurent). Candidates from earlier conversation: Lobito Corridor (DRC/Angola — transport corridor + restoration), Haiti (LDCF/GEF preparation). Proposal also suggested "humid forest-agriculture mosaic in Asia" — Indonesia? Vietnam?
>
> Open as a placeholder; refine NbS + country once WB confirms.

---

## 5 — GEE App (1 issue)

### Issue 13: GEE App design spec

**Template:** Module Spec (re-purposed for App)
**Title:** `[App Spec] GEE App v0 design`
**Assignee:** @benson
**Labels:** `app`, `phase-3-pilot`, `priority-medium`
**Milestone:** Phase 3 — Piloting

**Body:**
> Author `pipeline/gee_app/spec.md` per the design brief in `pipeline/gee_app/README.md`. Scope what's buildable in GEE Apps against the HTML wireframe. Document the six open questions (multi-pilot vs per-pilot, hosting, costs, sharing/auth, live vs precomputed, tab simulation).
>
> Once spec is reviewed by Pete, second issue follows for the App implementation.

---

## 6 — Documentation / repo polish (2 issues)

### Issue 14: Set up GitHub Pages

**Template:** documentation
**Title:** `Set up GitHub Pages serving from /docs`
**Assignee:** @pete
**Labels:** `documentation`, `priority-medium`

**Body:**
> Enable Pages via Settings → Pages → Source: Deploy from a branch → main / `/docs` → Save. Verify the three URLs render:
> - https://ciat.github.io/nbs_ruralscan/
> - https://ciat.github.io/nbs_ruralscan/wireframe.html
> - https://ciat.github.io/nbs_ruralscan/pipeline.html
>
> Close when confirmed live.

---

### Issue 15: Wireframe polish via Claude Design

**Template:** documentation
**Title:** `Polish docs/wireframe.html via Claude Design`
**Assignee:** @pete
**Labels:** `documentation`, `app`, `priority-low`

**Body:**
> Use the Claude Design Brief (in project working folder — `Claude_Design_Brief_Wireframe.md`) to send the v0 wireframe for visual polish. Review against the checklist before integrating. Commit the polished version back to `docs/wireframe.html`.
>
> Output: a wireframe that holds up at the WB final presentation.

---

## Optional — pulling these into a script

If you'd rather batch-create these via `gh` CLI rather than the web UI, the gist of each one is:

```bash
gh issue create \
  --title "[Recipe] Agroforestry" \
  --body-file <(echo "Author methodology/recipes/agroforestry.md to full draft...") \
  --label recipe,agroforestry,phase-3-pilot,priority-high \
  --milestone "Phase 3 — Piloting" \
  --assignee benson,namita
```

But honestly, opening 15 issues through the web UI is ~20 minutes and gets you familiar with the templates. Either works.
