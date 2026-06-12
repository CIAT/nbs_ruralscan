# M2b — Project Disaster Risk Screen

**Module spec addendum to M2 · v0.1 draft · June 2026**

| Field | Value |
|---|---|
| **ID** | M2b (addendum to M2) |
| **Module** | Project Disaster Risk Screen |
| **Owner(s)** | Brayden Youngberg (lead — hazard-index formulation + dataset download from T1) · Pete (oversight) |
| **Status** | Draft — RFC. Methodology to be confirmed before it becomes a wireframe surface. |
| **Schema tables consumed** | T1 · T2 · T3 · T7 |
| **Schema tables produced** | (none — outputs are rasters + tables) |
| **Position in pipeline** | M0 (Setup) → **M2b (Project Risk)** ‖ runs alongside M1 / M2; evaluated within the M1 opportunity space; later exposed as a third scope on M4 Priority Hotspots |

> This is an addendum to `M2_climate_risk.md`, not a replacement. M2 answers *risk to rural livelihoods* (the need lens). M2b answers *risk to the project/investment* (the WB Climate & Disaster Risk Screening lens). They are deliberately separate components, per Stocktake §4.7–§4.8.

---

## 1. Purpose

For a selected NbS and AOI, M2b produces an **indicative project disaster-risk surface**: where natural hazards could **damage or destroy the NbS investment itself**, under baseline and future scenarios. It is the spatial, scoping-grade expression of the **World Bank Climate & Disaster Risk Screening** framework (Stocktake §4.7.1, Figure 8 right), whose four-step structure — Exposure → Impacts → Adaptive Capacity → Overall Risk Rating — broadly aligns with IPCC AR6 `R = f(H, E, V)`.

The surface is:

- Continuous (0–1), classified Low → Very High, mirroring the WB "Overall Risk Rating".
- **NbS-specific** — asset fragility differs by NbS (a constructed wetland and a parkland agroforestry plot are vulnerable to different hazards).
- Evaluated primarily **within the opportunity space** (the candidate investment footprint), because asset risk only matters where you would actually invest.
- Scenario-aware — baseline + future, supporting "is this investment durable under climate change?".

## 2. The two-risk distinction (read this first)

| | **M2 — Risk to rural livelihoods** | **M2b — Risk to the project/investment** |
|---|---|---|
| Question | Where are people & production exposed to hazards this NbS can *mitigate*? | Where could disasters *damage or destroy* the NbS asset? |
| Hazards used | Hazards the NbS **mitigates** (T3 `risk_role = livelihood_mitigation`) | Hazards that **threaten the asset** but the NbS does **not** mitigate (T3 `risk_role = asset_threat`) |
| Exposure | Rural population, farms, production | The investment footprint + supporting infrastructure (roads, power — per Laurent [LF14]) |
| Role in tool | A *priority/need* layer → feeds M4 hotspots | A *feasibility check* → a scope filter on the opportunity space / hotspots |
| Example (wetland creation) | Wetland mitigates downstream flooding for livelihoods → flood is a *need* driver | Storm surge could destroy the wetland → surge is an *asset threat* |

The wetland example is the crux: the **same hazard family can be a need driver in M2 and an asset threat in M2b**, with opposite roles. This is why they are separate lenses, not one model.

## 3. Question answered

> *"If we invest in this NbS here, how exposed is that investment to disasters that could damage or destroy it — today and under mid-century climate change?"*

What M2b **does not** do:

- It is **not** the full project-level WB Climate & Disaster Risk Screening (which is qualitative, multi-criteria, and done at appraisal). M2b is an *indicative spatial screen*; the full screening happens downstream at pre-feasibility (see M6 / Next Steps).
- It does not model engineering failure modes or site-level design.
- It is not summed into the suitability or hotspot score — see §7.

## 4. Inputs

| Input | Source | Schema | Notes |
|---|---|---|---|
| Selected NbS | M0 Setup | `T0.nbs_id` | Resolves to T3 rows |
| Area of Interest | M0 Setup | `T7` | Same AOI as M1/M2 |
| Resolution, scenarios | M0 Setup | run config | Same as M2 |
| Asset-threat hazards | T3 | rows where `risk_role ∈ {asset_threat, both}` | Hazards that endanger the asset, NbS-specific |
| Asset fragility | T3 | `T3.asset_fragility` (new) | How damageable this NbS is by each hazard (0–1 / Likert) |
| Hazard variables | T2 + T1 | `T2.risk_component = hazard`, `risk_lens ∈ {project, shared}` | Intensity/frequency metrics (cyclone wind, storm-surge/flood depth, fire frequency, landslide) |
| Asset-exposure variables | T2 + T1 | `T2.risk_component = asset_exposure` (new) | Investment footprint proxy + supporting infrastructure |
| Geographic context | T7 | AEZ / admin | Context overrides if defined |

## 5. Outputs

| Output | Format | Path | Consumer |
|---|---|---|---|
| Project-risk raster — baseline | COG, 0–1 | `…/maps/project_risk_baseline.tif` | Project Risk tab; later M4 scope |
| Project-risk raster — future | COG, 0–1 per scenario | `…/maps/project_risk_<scenario>.tif` | Durability view |
| Per-hazard asset-threat surfaces | COGs | `…/maps/project_hazards/<hazard>_<scenario>.tif` | Drilldown |
| Overall project-risk rating + ranked units | CSV | `…/tables/project_risk_summary.csv` | Rating card + ranked list |
| Meta (hazards, fragility, weights used) | JSON | `…/project_risk_meta.json` | Audit trail |

## 6. Sub-steps

1. **Asset-threat hazard scoping** — from T3, take hazards with `risk_role ∈ {asset_threat, both}` for this NbS. The complement of the M2 mitigation set. If none are flagged, M2b returns an explicit "no screened asset hazards" result rather than an empty raster.
2. **Asset-threat hazard assembly** — build hazard stack (one band per hazard × scenario), same datasets/harmonisation as M2 §6.2.
3. **Asset-exposure assembly** — investment-footprint proxy (default: the M1 opportunity-space mask, optionally weighted by suitability) + supporting infrastructure layers.
4. **Asset fragility** — per-hazard NbS fragility weights from `T3.asset_fragility`.
5. **Rating composition** — `ProjectRisk = combine(Hazard_threat × Asset_exposure × Asset_fragility)`, weighted across hazards, normalised 0–1, classified Low → Very High. Composition function (multiplicative vs additive) is Brayden's call, logged in meta. Mirrors the WB "Overall Risk Rating".
6. **Future scenario run** — re-run step 2 with future hazard datasets; keep exposure/fragility constant; re-compose.
7. **Summary extraction** — per admin unit: mean rating, share in High/Very-High, dominant asset-threat hazard, Δ vs baseline.

## 7. Combination & double-count stance (important)

M2b is applied as an **independent screen / scope filter** — it masks or flags areas. It is **never summed** into the suitability index or the hotspot MCDA score.

Consequence: **sharing a hazard variable between M2 and M2b is allowed and intentional.** The double-count problem only arises when correlated variables are summed into the *same additive composite*; here the same hazard enters two *different lenses* in two *different roles* (mitigation vs threat), and neither inflates a single score. This is the "additional check and balance" framing — the project-risk screen cross-checks the opportunity space without distorting it.

The one rule the guard must preserve: **do not also add the project-risk score as another additive term into the final MCDA sum.** Keep it a *filter*. Overlap with the NbS suitability scope is therefore fine; overlap inside one additive index is not.

## 8. Integration as a Priority Hotspots scope (forward)

Once the method is agreed, M2b's rating becomes a **third scope on M4 Priority Hotspots — a "Project-Risk scope"** alongside the existing NbS Suitability Scope and Priority Scope. The TTL dials it to **exclude or flag** High / Very-High project-risk areas from the hotspot intersection. Because it acts as a filter (§7), this introduces no double-counting even where it shares hazard layers with suitability.

Build order: standalone **Project Risk tab first** (validate the method and outputs), then wire in as the hotspot scope.

## 9. Schema changes (RFC — needs a migration PR)

Per `schema/README.md`, new columns require an RFC issue. Proposed:

- **T3 (NbS × Hazard × Farming System):**
  - `risk_role` ∈ `{livelihood_mitigation | asset_threat | both | neutral}` — which lens each NbS×hazard pairing feeds.
  - `asset_fragility` (0–1 or Likert) — how vulnerable this NbS's investment is to this hazard. Null where `risk_role` excludes asset threat.
- **T2 (Climate Risk Formulation):**
  - `risk_lens` ∈ `{livelihood | project | shared}` — which screen a variable feeds.
  - extend `risk_component` enum with `asset_exposure` (investment footprint + supporting infrastructure).

No existing column meanings change. Default for legacy rows: `risk_role = livelihood_mitigation`, `risk_lens = livelihood`, preserving current M2 behaviour.

## 10. Scope guardrails (for Laurent / Dinara)

- M2b is an **indicative spatial screen**, not a feasibility-grade WB Disaster Risk Screening. State this on the tab.
- The full, project-level WB screening is a **downstream** step, pointed to in M6 / Next Steps.
- Keep it country-agnostic: hazards, fragility and exposure read from schema, never hardcoded.

## 11. Open questions for Brayden

1. Composition function for the rating — multiplicative (`H × E × fragility`) vs additive/weighted? Default suggestion: multiplicative per hazard, weighted sum across hazards.
2. Asset-exposure proxy — use the M1 opportunity-space mask as the footprint, suitability-weighted, or a flat candidate-area mask?
3. Source of `asset_fragility` — author from T6/T3 literature, or a small expert-elicited table per NbS?
4. Default treatment of "no screened asset hazards" NbS (e.g. some soil-and-water practices) — show an explicit low-risk/empty state.
5. Institutional/social constraints (conflict, cohesion) — in-scope for v0 or deferred? (Data availability and country-agnosticism are the constraints.)
6. On-by-default or optional? Suggest optional tab for v0, opt-in scope on hotspots.

## 12. Two streams — Stream A (asset hazard) + Stream B (operational/enabling) — v0.3.0

Sections 1-11 above describe **Stream A — asset hazard exposure**: T2 hazards × T3
`asset_threat` / `asset_risk_weight`, baseline + future, modulated by T0
`establishment_period_years` (a 30-year tree-crop investment is more exposed to slow-onset
climate change than a 3-year annual cropping intervention).

**Stream B — operational / enabling environment** is added at v0.3.0 to cover the
investment-readiness levers TTLs need to surface. **Soft / investment-addressable**: each
variable is a scenario lever ("what if road access improved?"), **not** baked into the
opportunity-space surface; **filter / flag, never summed** into hotspots. Hard exclusions
(legal protected areas, water bodies, urban) remain T4 masks per the v0.2.6 hard-vs-soft
decision.

| Stream-B lever | Variable family | Datasets / sources | T4 row |
|---|---|---|---|
| Accessibility | travel time to market / town | Nelson accessibility, Weiss et al. | `accessibility_travel_time` |
| Electrification | grid coverage, night-lights | World Bank Energy / VIIRS night-lights | `electrification_index` |
| Tenure (incl. IPLC) | land tenure security, customary/IPLC lands | **LandMark** + **WWF/ICCA** + Prindex; carries **FPIC / ESS7 safeguard flag** | `tenure_security` |
| Conflict / fragility | sub-national conflict events + WB FCV list | **ACLED** + WB FCV list | `conflict_fragility_index` |
| Governance / extension | extension-service coverage, governance quality | WB WGI, country-team uploads | `extension_governance` |
| Finance / credit | rural credit / micro-finance / project portfolio | WB project-funding density, FinScope | `finance_credit_access` |
| Market / value-chain | output-market depth + processing capacity | FAOSTAT + country-team uploads | `market_value_chain` |
| Labour | seasonal labour availability + cost | ILO + LSMS-ISA / country uploads | `labour_availability` |

### WOCAT QM Alignment & GCA 2022 Enabler Evidence

To ensure methodological traceability and alignment with global Sustainable Land Management (SLM) standards, the 8 operational enabling-environment scenario levers in Stream B are explicitly modeled after and aligned with the **WOCAT QM (Questionnaire on SLM Technologies/Approaches)** indirect drivers of land degradation and SLM adoption:

1. **Accessibility (`accessibility_travel_time`)** maps directly to WOCAT QM indirect driver **`m`** (market access, including roads and transport infrastructure).
2. **Electrification (`electrification_index`)** maps to WOCAT QM indirect driver **`i`** (infrastructure, including energy, communication, and basic utilities).
3. **Tenure (`tenure_security`)** maps to WOCAT QM indirect driver **`t`** (land tenure, including formal and customary rights). Secure land tenure is documented by the **Global Center on Adaptation (GCA 2022, p. 85)** as a critical prerequisite for long-term agroforestry investment, as smallholders require long-term land security to justify upfront tree-planting labor and deferred returns.
4. **Conflict / Fragility (`conflict_fragility_index`)** maps to WOCAT QM indirect driver **`p`** (political stability, security, and conflict).
5. **Governance / Extension (`extension_governance`)** maps to WOCAT QM indirect drivers **`e`** (extension/education) and **`g`** (governance, policy, and institutional support).
6. **Finance / Credit (`finance_credit_access`)** maps to WOCAT QM indirect driver **`f`** (financial access and credit availability). **GCA (2022, p. 86)** emphasizes that bridging the agricultural credit and finance gap is critical to buffer the establishment phase of NbS investments.
7. **Market / Value-chain (`market_value_chain`)** maps to WOCAT QM indirect driver **`m`** (market depth, processing infrastructure, and value chain development).
8. **Labour (`labour_availability`)** maps to WOCAT QM indirect driver **`l`** (labor availability, including seasonal labor supply and age/gender structures).

**Stream-B principle (filter, never summed):**

- Each lever becomes a T4 row with `suitability_dimension = operational_constraint` and
  `is_scenario_candidate = true`. Together they constitute the *enabling-environment scope*
  in the wireframe — a third hotspot scope (`Project-Risk + Operational-Readiness` is the
  full M2b lens; Sections 1-11 cover the hazard-exposure half).
- **Hard exclusions** remain T4 masks (`is_scenario_candidate = false`): legal protected
  areas, urban/built-up, water bodies, formally-designated reserves. Soft levers don't get
  promoted to hard exclusions on the scoping timescale.
- **Scoping flags; feasibility validates.** M2b surfaces *where the investment is fragile or
  the enabling environment is thin*; the project team handles validation, FPIC, ESS7
  procedural compliance downstream.
- **IPLC tenure** carries an explicit safeguard flag: a hotspot that overlaps IPLC customary
  land triggers `FPIC_REQUIRED = true` in the M6 hand-off + a scorecard note. LandMark + WWF/
  ICCA layers are the spatial input; ESS7 is the WB Operational Policy hook.

**Discovery sources for Stream B** (T4 method §3 seed-set rule applies):

- **Accessibility / electrification**: WorldPop, Nelson accessibility, VIIRS, WB Energy.
- **Tenure / IPLC**: LandMark + WWF/ICCA + Prindex.
- **Conflict / fragility**: ACLED, WB FCV list, ND-GAIN.
- **Governance / extension**: WB WGI + project-level evidence (WB PADs / ICRs).
- **Finance**: WB FAR (Financial Access Report), FinScope, project-portfolio density.
- **Labour**: ILO statistics, LSMS-ISA, country-team uploads.

### ICRAF & PRAGA/SRM Methodological Refinements for M2/M2b (June 2026)

Based on the open-source audit of CIFOR-ICRAF tools and the Participatory Rangeland and Grassland Assessment (PRAGA) / VGGT guidelines, we propose the following specific additions for the M2/M2b modules:

1. **Livestock Grazing Pressure Bottleneck (F3 Silvopasture / Agrosilvopasture)**:
   * **The Hazard/Risk**: Planting trees/shrubs in active pastures (F3) faces high seedling mortality from livestock grazing and trampling during the `establishment_period_years`.
   * **Variables to Ingest**: Cross-reference grazing land classification maps (ESA WorldCover/Copernicus class 30) with livestock density statistics (FAO GLW - Gridded Livestock of the World) to estimate stocking density / grazing pressure.
   * **Scoping Lever**: High grazing density acts as an operational-constraint flag in M2b. In the user interface, it triggers a scenario lever: "Establishment exclusion fencing / rotational grazing plan" which, if active, overrides the high-risk flag to represent managed protection.

2. **Common-Property Rangeland Governance**:
   * **The Risk**: Dryland pastoral landscapes are typically managed under collective or customary tenure rather than private title. Fenced tree plots can trigger user conflicts over restricted common pasture access.
   * **Variables to Ingest**: Customary land boundary datasets (LandMark and WWF/ICCA database).
   * **Scoping Flag**: Any overlap with customary lands triggers an explicit `FPIC_REQUIRED = true` safeguard flag in the Module 6 hand-off (aligning with WB ESS7 safeguard policies).

## 13. Version history

- **v0.1** (June 2026) — addendum drafted to pin down the project-disaster-risk method ahead of the standalone Project Risk tab and its later use as a hotspot scope. Structure mirrors `M2_climate_risk.md`. Schema additions raised as an RFC; combination stance (filter-not-sum) specified to keep the double-count guard intact.
- **v0.2** (June 2026 — v0.3.0 schema batch) — added §12 **Stream-B operational/enabling
  levers**: accessibility, electrification, tenure (with FPIC/ESS7 flag for IPLC overlap),
  conflict/fragility, governance, finance, market, labour. Each lands as a T4
  `operational_constraint` row with `is_scenario_candidate = true`. Filter / flag, never
  summed.
- **v0.2.1** (June 2026) — Integrated ICRAF & PRAGA/SRM recommendations for F3 silvopastural/agrosilvopastural grazing pressure limits and customary rangeland tenure flags (livestock mobility corridors variable removed due to data limitations).

