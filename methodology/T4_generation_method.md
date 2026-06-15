# T4 Generation Method — evidence-first, defensible suitability mappings

**Status:** v0.1 draft for team discussion · June 2026
**Owners:** Namita (recipe content) · Pete (framework) · Brayden (ML / climate) · Benson (QA/QC sign-off)
**Produces:** rows of **T4 — Suitability Variable Mappings** (see [`../schema/spec.md`](../schema/spec.md))
**Scope:** scoping-grade suitability, per NbS *suitability family*. Not site feasibility, not ecosystem-service modelling.

---

## 0. Why this method exists

T4 is the table where "a model read some papers and chose numbers" is least defensible. Every response curve,
threshold and weight has to survive a World Bank reviewer asking *"why that value?"* — so the method is built
around one principle:

> **Never go from a PDF to a threshold in one step.** Extraction (what a source says) and synthesis
> (combining sources into a mapping) are separate stages, with a **traceable evidence layer** between them.

Every value in a finished T4 row traces a chain: **T4 row → evidence units → source (tier, page, quote)**.
That chain *is* the deliverable's defensibility, and it is what makes a run reproducible.

**Defensibility tenets (apply throughout):**

1. **Provenance on every value** — no parameter without linked evidence units.
2. **No silent inference** — extraction records only what a source states; missing values are `null`, not guessed.
3. **Separation of concerns** — discovery proposes, evidence substantiates, synthesis combines, a reviewer signs off.
4. **ML for *which*, literature for *what shape*** — machine learning ranks variable importance; it never sets a response curve.
5. **Auditable lumping** — variable harmonisation and subpractice grouping are recorded with rationale, never merged silently.
6. **Reproducibility** — prompts, skills and the evidence corpus are versioned; uncertainty is derived from evidence spread, not asserted.

---

## 1. The staged pipeline

```
DEFINE practice + targets + vocab   ─┐  (definition layer — gates everything)
DISCOVER candidate variables/sources ┘
        │   feeds: scoping report · deep research · ML variable-importance
        ▼
HARMONISE  surface names → canonical variable → T1 dataset, classified into a group
        ▼
INGEST     PDF → page-tagged text + structure index (sections · tables · figures w/ captions+pages)
        │   vectorless: retrieve by keyword/structure, not embeddings · cache once (gitignored)
        ▼
EXTRACT    one source → atomic evidence units (quote + page + context + tier)
        ▼
NORMALISE / QA   controlled vocab · context tags · human validation gate
        ▼
SYNTHESISE   evidence units → one T4 row per (suitability_family × variable)
        │   literature → shape & params · ML/discovery → selection only
        ▼
VALIDATE (FK / enum / schema)  →  HUMAN SIGN-OFF  →  write to T4
```

Two streams run in parallel and meet at synthesis: **selection** (which variables matter — discovery + ML)
and **shape** (what the relationship is — literature evidence). They are kept structurally distinct so an ML
importance score can never become a response curve.

---

## 2. Definition layer (do this first — it gates the rest)

If the practice and the variable groups aren't crisply defined, discovery wanders and evidence won't aggregate.

### 2.1 Practice definition → subpractices → suitability families

An NbS is not a monolith. Three levels:

- **NbS** — the T0 anchor (e.g. agroforestry), with a scoping-report-sourced definition and scope boundaries.
- **Subpractices** — the variants: alley cropping, tree intercropping, FMNR, parkland retention, silvopasture, windbreaks, vegetative/contour buffers, homegardens, woodlots, riparian buffers…
- **Suitability families** — the unit T4 is authored against.

**Grouping criterion — shared dominant limiting factor.** A family = practices that share the *dominant limiting
factor* that decides where they're suitable, because that factor determines the **leading variable and the whole
variable set**. (Establishment pathway matters only insofar as *regeneration potential* is one such limiting
factor.) Grouping by visual structure mis-merges: *scattered trees on cropland* can arise by **planting** (→
biophysical-envelope family) or by **retention/FMNR** (→ regeneration family) — same picture on the ground,
different limiting factor, different variable set.

Four limiting-factor archetypes:

| Archetype | Dominant limiting factor (leading variable) | Practices |
|---|---|---|
| **Biophysical-envelope, planted** | climate/soil/slope envelope + management | alley cropping, tree intercropping; planted silvopasture (+livestock vars); shaded perennial-crop systems (+understorey-crop envelope) |
| **Regeneration-potential** | remnant rootstock · seedbank · seed-source proximity · tenure | FMNR, parkland retention, ANR-on-farm |
| **Placement / geometry** | linear-feature logic — wind exposure *or* slope/flow lines | windbreaks & shelterbelts; contour/vegetative buffers |
| **Proximity / intensive** | settlement & water proximity (sub-pixel) | homegardens |

**Worked agroforestry families** (first-pass hypothesis from the Inception Report longlist, revisable):

| Family | Subpractices | Dominant limiting factor | `spatial_product_type` (§2.4) |
|---|---|---|---|
| **F1 Planted silvoarable** | alley cropping, tree intercropping, planted boundary on cropland | biophysical envelope + management | `area_suitability` |
| **F2 Regeneration-based on farmland** | FMNR, parkland retention (kin to ANR) | regeneration potential | `area_suitability` |
| **F3 Silvopastoral** | sylvo-/agrosilvopastoral | envelope + grazing context + livestock/forage vars | `area_suitability` |
| **F5 Shaded perennial-crop systems** | shade trees over coffee / cocoa / tea / cardamom (incl. cabruca, shaded coffee) | the **understorey crop's** bioclimatic envelope + shade benefit | `area_suitability` |
| **F4 Linear / boundary plantings** | windbreaks, shelterbelts, vegetative/contour buffers | wind exposure / slope-flow + boundary geometry | `applicability_zone` |
| *(Homegardens)* | multistrata homegardens | settlement & water proximity (sub-pixel) | `qualitative_only` |
| *Riparian buffers (own NbS)* | hydrology / water proximity | watercourse zone | `zonal_linear` |

Schema note: silvopasture can't be a cropland→grazing *context override* of F1 because it needs **additional**
variables (forage, grazing pressure, livestock) and overrides only re-parameterise existing variables — so it is
its own family. **F5 (shaded perennial crops)** is the same reasoning: its suitability is gated by the *understorey
crop's* envelope (coffee → cool highlands; cocoa → lowland humid tropics), a crop-specific variable set distinct
from generic silvoarable — so it is its own family (likely with crop sub-variants, modelled via the `ecocrop`
composite type). Note the distinctive logic: shade often **extends** suitability into the heat/drought-marginal
edges of the crop's range (shade as adaptation), so the surface is "where the crop grows *and* where shade adds
resilience," not the bare crop envelope.

**T4 is keyed to `suitability_family_id`, not to the whole NbS.** The grouping carries a documented rationale +
references (the biophysical-logic check `AGENTS.md` enforces — "water harvesting ≠ wetland creation"). It is a
**first-pass hypothesis, revisable** once evidence is in, recorded so the revision is auditable.

### 2.2 Target / scope spec (what we're looking for)

For each suitability family, capture from the scoping report — this is the brief handed to the discovery and
extraction agents so they pull the *right* evidence (the precision counterweight to discovery's recall):

- the **suitability question** and what "suitable" means — establishment vs productivity vs persistence (each implies different variables);
- **inclusion / exclusion boundaries** (e.g. excludes irrigated; includes rainfed parkland);
- the **decision context** — scoping-grade, which keeps thresholds coarse and honest.

### 2.3 Controlled vocabularies

Extraction is only aggregatable if everyone records the same way. Lock these registries up front:

- **Variable-Group vocab** (shared across T4 and T5): `group_id`, label, definition, `applies_to` (suitability | opportunity | both).
  - *Suitability (T4):* Topographic · Climatic · Soil · Land cover/vegetation · Socio-economic/infrastructure · Hazard — cross-cut by `suitability_dimension` (biophysical / system / operational constraint).
  - *Opportunity (T5):* Climate hazard · NbS-response · People & production · Infrastructure.
- **Canonical variable names + units** (the Variable Ontology, §4).
- **`relationship_type`** — the canonical membership-function set (see `spec.md`): trapezoidal · gaussian · linear↑/↓ · sigmoid · inverted_sigmoid · threshold · ranked_classes · piecewise.
- **AEZ ids & farming-system ids** — must match **T7**.
- **method_type · confidence · benchmark_tier** enums.

Anything that can't be mapped to a vocab is flagged for a human, never guessed.

### 2.4 Spatial product type & the resolution trap

T4's MCDA machinery (variables → response → weighted composite → 0–1) is shared by every family, but **what the
output *means* and how footprint is accounted differ by family.** Each family carries a `spatial_product_type`:

| `spatial_product_type` | Meaning | Footprint accounting | Families |
|---|---|---|---|
| `area_suitability` | pixel can host the practice | area (km²) | envelope-limited (F1, planted silvopasture); regeneration-limited (F2); silvopastoral (F3) |
| `applicability_zone` | area would *benefit* / is a candidate; the intervention is a line within it | candidate length / density — **not** pixel area | F4 windbreaks, contour/vegetative buffers |
| `zonal_linear` | suitability defined along a feature (streams) | zone length / riparian area | riparian buffers (own NbS) |
| `qualitative_only` | sub-pixel; a raster misleads → flag, don't map | none — scorecard + M6 note | homegardens |

This is a labelling/interpretation layer plus one schema field — **not** a second pipeline.

**The resolution trap (critical for honesty of footprint).** A linear or point practice occupies a tiny fraction
of a pixel, so reporting a "suitable" pixel as suitable *area* **over-estimates footprint, and the over-estimate
grows with pixel size** — a 5 km cell flagged suitable for windbreaks implies 25 km² of plantable extent when the
real figure is a few line-km. Consequences baked into the method:

- For `applicability_zone` / `zonal_linear` / `qualitative_only`, **never report pixel area as footprint.** Report
  candidate **length or density** (e.g. erodible field-boundary km per km²), or qualitative extent.
- Apply a **realisable-fraction**: footprint ≈ candidate-zone × a density factor (boundary length, settlement
  density), not the zone area itself.
- The **resolution audit** must flag any non-`area_suitability` product, and coarsening the grid should widen its
  stated uncertainty, not just blur the map. `area_suitability` families are comparatively resolution-robust in
  interpretation (a suitable pixel ≈ suitable land); the others are not.
- **NbS Comparison** compares within product type, or caveats explicitly — never ranks an `area_suitability` km²
  against an `applicability_zone` surface.

### Per-variable resolution validity (a *second*, independent coarseness limit)

The trap above is about *footprint*. There is a separate limit about *variable validity*: **some variables stop
being meaningful above a certain resolution.** Slope is the textbook case — it's a **derivative of elevation**, and
slope magnitude is strongly scale-dependent: as grid size grows, computed slope **flattens**, which biases
suitability *optimistic* (under-reads steepness → over-reads suitable area). Derivatives (slope, TWI, drainage
density, roughness) lose signal faster than smooth primary fields (rainfall, poverty). *(Real example: Nath 2021
derived slope from ~1 km GTOPO30 — questionable — while most agroforestry papers used 30–90 m SRTM.)*

Rules:

- Each variable carries **`min_meaningful_resolution_m`** (coarsest grid at which it stays valid — slope ≈ 30–90 m)
  and a **`resolution_sensitivity`** level (slope = high; rainfall/poverty = low). See the Variable Ontology (§4).
- **The run's maximum coarseness is set by the most resolution-sensitive *selected* variable** (the binding
  variable). The resolution audit flags any variable run coarser than its `min_meaningful_resolution_m` → exclude,
  down-weight (widen uncertainty), or fetch finer data.
- **Derive-then-aggregate, never resample-then-derive.** Compute scale-dependent derivatives at the native fine
  resolution, then aggregate the *derived* metric to the analysis grid — carrying a **within-pixel distribution**
  (e.g. mean slope + *fraction of the cell below the slope threshold*). The suitability function can then use the
  sub-grid fraction ("30 % of this 1 km cell is gentle enough") instead of one flattened value — which also gives
  the honest realisable fraction for slope-limited families, echoing the footprint logic above.

So coarseness is bounded by **two** things at once: product type (footprint honesty) *and* the binding variable
(signal validity).

### 2.5 Constrain by observed distribution, not a modelled niche, where data exist

When a family's applicability is gated by an **existing host system** (a land use, a crop, a grazing system),
prefer the host's **observed distribution / production** as the gating layer over a model of its potential niche.
This is a general rule, not an F5 special case:

- It is already the logic behind **land-cover eligibility** in F1/F2 (observed land use gates the planting/
  regeneration envelope). F5 extends it from "cropland" to "this specific crop"; F3 would use pasture/grazing
  distribution.
- It is **more correct for "improve the existing system" interventions** (shading existing coffee/cocoa,
  thinning canopy): the intervention happens where the system already is, so a potential-niche surface
  over-claims into land the system never occupies. Observed distribution also already integrates the real
  climate · soil · market · tenure reasons the system sits where it does — things a bioclimatic envelope misses.
- Use a **graded** constraint (fractional area / production intensity: MapSPAM, GAEZ harvested-area, EO commodity
  maps, national ag-stats) rather than binary presence where the data support it.
- **Resolution honesty applies** (§2.4): a coarse distribution layer constrains coarsely; carry that into the
  uncertainty, don't pretend to fine detail.
- **Niche / envelope modelling is the fallback**, used only where distribution data are absent or too coarse —
  and flagged as potential, not realised, extent.
- Where the family is also about **adaptation** (e.g. shade), reframe the benefit as *prioritising the
  climate-stressed edge within the observed distribution*, not extending beyond it.

Record the choice (distribution-constrained vs niche-modelled) per family in the target/scope spec (§2.2) so the
provenance is auditable.

**Mechanism — the BIND registry (schema v0.2.1).** Which dataset supplies a variable is **context-resolved**, not
fixed globally: the global recipe carries a `global` binding, and a country / AEZ / region can override it with a
better local dataset (most-specific-context-wins). When a better local dataset is known but not catalogued, the
binding is `requires_upload` — the runtime uses the global default and **flags the user to supply it**. So "select
Sierra Leone → use the national cocoa map if present, else prompt for it" is a schema lookup, not a code change.
See `schema/spec.md` → BIND. Relationship *parameters* are refined in parallel via `T4.context_overrides`.

### 2.6 Variable generalisability & data sovereignty — flag, don't resolve

Variables differ in how freely a global dataset transfers and how politically charged the numbers are. Carry this
as `VONT.context_sensitivity`:

- **`low`** — generalisable physical variables (slope, climate, terrain). A global dataset transfers across
  countries; uncontroversial. Set the global binding and move on.
- **`medium`** — context-dependent but apolitical (soils, land cover, infrastructure). Local data is better where
  available, via a BIND override.
- **`high`** — **nationally-derived / sovereignty-sensitive** (population, poverty, crop production). Official
  figures carry political weight, and a global model (WorldPop, MapSPAM, PIP) can diverge from — or appear to
  contradict — the country's own numbers. For these, the scoping output should **recommend a country-endorsed
  source** and treat a global default as provisional.

**The scope line (important).** This is a **flag, not a resolution.** The scoping tool *marks* a variable as
sensitive and *recommends* the source be confirmed/validated with the country in the **feasibility phase**
(surfaced in the data-gap prompt and the M6 hand-off). It does **not** negotiate, validate or endorse national
data itself — that is feasibility work, downstream, and outside this project's rapid-scoping mandate. Naming the
sensitive variables precisely is exactly the kind of hand-off guidance scoping *should* produce ("confirm these,
don't trust the global default blindly"); doing the confirmation is not ours to do. Keep it a labelling layer —
no change to the suitability analysis.

### 2.7 Hard vs soft operational constraints (resolves the schema ↔ Fig 9 tension)

The stocktake's **Figure 9** framing routed social/institutional factors into a separate **Project
Operational Risk** stream, which doesn't, on its face, sit cleanly inside the T4
`operational_constraint` dimension. The reconciliation (v0.2.6) is the *hard-vs-soft* split:

- **Hard exclusions** belong inside the opportunity space as T4 constraints. Examples: legal
  protected areas, water bodies, urban/built-up footprints, formally-designated reserves.
  Tag: `suitability_dimension = operational_constraint`, `is_scenario_candidate = false`.
  These aren't investment-addressable on a scoping timescale.
- **Soft, investment-addressable** access/institutional factors are **not** baked into the core
  biophysical opportunity space. They appear as:
  - **scenario levers** (T4 rows, `is_scenario_candidate = true`) — toggle on/off in the wireframe
    to surface what investment would unlock;
  - **inputs to a separate operational-risk / feasibility filter** on the M2b side (project-disaster
    + project-feasibility lens).

  Examples: road access, market access, extension coverage, tenure security.

The practical test: if turning the variable off in a what-if scenario is a *reasonable* policy
question, the variable is soft → scenario lever + operational-risk filter. If it isn't (you can't
legislate away a water body), it's hard → exclusion in T4.

Reconciliation with Fig 9: biophysical + system + hard-operational dimensions ≈ the opportunity-
space surface; soft-operational ≈ scenario levers + the project-operational-risk stream (M2b
family). Two streams, one consistent framework. The earlier inconsistency (e.g. `road_access`
tagged `system_constraint` in draft-0) is fixed in v0.2.6.

See `schema/spec.md` → T4 → "Hard vs soft operational decision" for the schema-side
implementation.

---

## 3. Discovery (recall-first — proposes candidates)

**Process order (Pete, 2026-06-05) — paper-first, not variable-first.** Earlier passes extracted
one canonical variable at a time across the corpus (slope, precip, MAT…) against an unaudited
draft-0 variable list. This is inverted: traverse the corpus *one paper at a time*, capturing every
variable across all relevant tables (T3 hazard mitigation, T4 suitability, T5 priority targets, and T6 economics/scorecard) in a single pass, then harmonise across
papers, then weight by tier, then synthesise. Concretely:

1. **Per-paper variable scan + relationship capture.** For each paper in the corpus, enumerate every
   suitability variable it uses and extract any quantified threshold/class table at the same visit —
   *one trip through the PDF per paper, not one per variable.* Records both the variable's surface name
   and any in-paper relationship (EvidenceUnits with quote + page) in a single pass. Append the
   variable list to the paper's row in `schema/registers/SRC_source_register` (`vars_extracted[]`).
2. **Harmonisation.** Map surface names → canonical Variable Ontology ids, keeping the surface name
   in EV (`raw_name`) for audit. New variables not in VONT are queued for ontology review (Namita +
   Pete) before they enter T4.
3. **Tier-weighted prevalence + variable combining.** Prevalence of a variable across the corpus is not a raw paper count or percentage of instances. Instead, we calculate a **weighted prevalence ratio** where each paper's vote is scaled by its authority and pedigree (its `benchmark_tier` weight: High=1.0, Med=0.6, Low=0.35). This ensures that a variable supported by highly authoritative, seminal syntheses is prioritized over one found in multiple low-tier primary studies. Variables that fail a soft floor on weighted prevalence are reviewed (not auto-dropped) and may be combined (e.g. soil N/P/K → a nutrient-availability composite when the underlying papers themselves do so).
4. **Synthesis → global aggregate / composite response functions.** Only after steps 1-3 does each
   surviving (family × canonical variable) get its T4 row synthesised — same weighted-median logic as
   today (§6).

The four feeds below still produce the *initial* candidate-source set, but the per-paper scan is the
operative discovery loop for T4 extraction itself.

### Bounded, authority-weighted seed-set rule (v0.2.6, expanded v0.2.7)

Discovery does not sweep 100k abstracts. Per **NbS × table**, assemble a **capped seed set
(~10-20 sources)** of authoritative material, then expand only when the seed set leaves
obvious gaps. Categories to hit, in roughly this order of authority:

**Tier-1 authority (project-relevant, evidence-grade):**

- **World Bank rural-NbS catalogue** (in-house operational reports + adoption studies)
- **WB project evidence** — Project Appraisal Documents (PADs), Implementation Completion Reports
  (ICRs), Independent Evaluation Group (IEG) reviews. Operational reality + outcomes that
  literature alone misses.
- **WB TORs-named tools** — **D4R** (Data for Resilience), **Africa Agriculture Adaptation Atlas
  (AAAA)**, **MapAWD** (Mapping Agriculture's Water Demand). Pre-curated decision-support
  surfaces; mine them for variables, datasets, and operational thresholds.
- **GEF / NBS Invest** materials (project portfolios, lessons-learnt)
- **IPCC** (AR6 WGII, SRCCL chapters relevant to the NbS)
- **FAO** (land-evaluation framework, GAEZ, **Ecocrop** (restricted to F5 shaded systems understorey crop envelope modeling; explicitly excluded for general practice suitability models), **TECA** = Technologies and Practices
  for Small Agricultural Producers, AgrEd, EX-ACT)
- **WRI** (Global Restoration Initiative, Restoration Diagnostic, AFR100/Atlantic Forest)
- **CGIAR** systems-level reviews + science-quality outputs (ICRAF, ILRI, IWMI…)

**Tier-1 "diamond classes" — pre-mapped evidence + practice databases (high-leverage):**

- **WOCAT** (World Overview of Conservation Approaches and Technologies) — SLM technologies
  database; **LMIC-grounded**, structured per-practice fact sheets covering **T4 requirements**
  (climate/soil/topography/land-use), **T6 benefits/costs** (impacts, adoption costs, success
  factors), and dis-adoption notes. The single highest-yield single source for SLM/NbS
  characterisation.
- **Evidence Gap Maps (EGMs)** (e.g., **3ie**, **Campbell Collaboration**, **CEE**) — these pre-map the landscape of intervention-outcome pairs, acting as a **discovery shortcut** to immediately locate high-quality, relevant synthesis papers and primary evidence. Crucially, they also identify true 'evidence gaps', letting us know where empirical support is absent so we can avoid over-claiming or asserting spurious precision in T4/T6.
- **NbS-specialist research organisation assets & databases** — databases and tools developed by international research centers specializing in specific NbS classes (e.g., **ICRAF / World Agroforestry Treefinder**, **CIAT MyFarmTrees**, Vegetation Map for Africa, or GTPK Genetic Resources Information System). These offer species lists, traits, growth requirements, suitability profiles, and propagation guidelines that complement general databases like Ecocrop with practice-specific species recommendations.
- **IPLC tenure / rights layers** (v0.3.0) — **LandMark Global Platform of Indigenous &
  Community Lands** + **WWF / ICCA Consortium State of IPLC Lands**. Authoritative spatial
  layers for indigenous and community customary lands. Feed the **M2b tenure stream** + the
  T5 `equity_inclusion` theme (the future `marginalisation` / `iplc_lands` priority row when
  ratified). Carry the FPIC / ESS7 safeguard flag downstream.
- **CSA adoption & barriers dataset** (Aggarwal et al. and successors — the synthesised
  adoption/dis-adoption evidence base)

**Tier-2 (peer-reviewed / synthesis):**

- **Global-scale suitability models & MCDAs** (e.g. Zomer et al. 2014, GAEZ crop suitability models, or global-scale spatial methods). These are highly valuable for establishing baseline global biophysical envelopes, default threshold shapes, and candidate variable lists.
  - *Heritage & Pedigree:* These global-scale methods represent a crucial link to the **Stocktake Report** (which screened 220 peer-reviewed papers for spatial suitability/MCDA to build our initial variable inventory). They inherit the Stocktake's rigorous benchmark scoring (`High`/`Medium`/`Low`) and provide the initial global defaults in T4.
  - *Context Constraints:* To mitigate their coarse resolution and absence of local socio-economic inputs, their global thresholds act only as provisional defaults, subject to **context overrides** (`T4.context_overrides`) and **local dataset bindings** (`BIND`).
- **Major meta-analyses / reviews** in the peer-reviewed literature for the NbS
- **MEL / MELIA reports** + synthesis pieces from large CGIAR/donor projects (Kuria, Sida-NbS,
  Restoration Initiative MEL packs)

**Tier-3 (admitted only when seed-set above is thin):** primary peer-reviewed studies.

**Tie to `SRC.benchmark_tier`:** prefer `high` and `medium`; admit `low` only when the seed set
above is genuinely thin for the variable. `external` tier is used for citation-cascade pointers
(Mushtaq → Ahmad 2019), not for primary discovery.

**Corpus differs per table — sequence T6/T3 after T4.** The 220-paper stocktake was scoped to
**suitability (T4)** — *that* corpus is in hand. The other tables need their own bounded
discovery passes against different literature:

- **T6** (NbS effects, conditionality, economic profile): effectiveness / impact / adoption +
  **MEL / MELIA** reports + CSA adoption & barriers. Effectiveness lit is different from
  spatial-suitability lit.
- **T3** (NbS × hazard mitigation matrix): hazard-resilience + vulnerability literature; IPCC
  AR6 WGII Chapter 2/3; CGIAR-CCAFS climate-resilience reviews. Brayden's M2 lit is the spine.
- **T1** (data registry): GEE / STAC catalogues; data provider documentation. Not literature.
- **T7** (AEZ + farming systems): GAEZ + Dixon farming-systems standards. Not literature.

Sequence: **complete T4 first**, then T6/T3 use the same paper-first machinery against their
own bounded seed sets.

### Screening funnel (v0.2.7) — the repeatable SOP

A reproducible five-step screening pipeline, applied per NbS × table:

1. **Frame the claim precisely + search for syntheses first.** Define the specific claim being
   sourced (e.g. "for F1 silvoarable, what slope above which erosion risk dominates?"). Search
   for **syntheses** (systematic reviews, EGMs, meta-analyses, WOCAT entries, IPCC chapters)
   before primary studies — a good synthesis saves N primary-paper extractions.
2. **Source-type triage.** Authority order: **synthesis > primary > grey**. Within types, prefer
   the diamond classes (WOCAT, EGM, WB-project, ICRAF DBs) over generic peer-reviewed primary
   studies *for breadth*; admit primaries for *depth* on a specific threshold.
3. **Relevance screen** on three dimensions: **practice** (does it cover this NbS/family?) ·
   **outcome/hazard** (does it cover the variable/effect/exposure of interest?) · **system**
   (is the agro-ecological / income-group context relevant — LMIC preference applied as a
   tie-break, not a veto on global syntheses).
4. **Credibility scoring** → `SRC.benchmark_tier` on **six orthogonal axes** (replaces narrative
   tiering, reconciles the prior C/I/D rubric):
   - **(i) Evidence strength** — RCT/quasi-experimental/observational/correlational/expert; upweight papers that include empirical validation or performance metrics (such as ROC/AUC of maps, yield measurements, or cost-benefit verification)
   - **(ii) Methodological transparency** — pre-registration, data availability, reproducible code
   - **(iii) Authority & venue reputation** — `SRC.venue_type` (peer-reviewed > institutional report > preprint > grey); landmark institutions weigh more
   - **(iv) Context relevance / transferability** — `SRC.study_income_group`, AEZ, farming system;
     **LMIC preference** (`low`/`lower_middle`/`upper_middle`) for WB-investable contexts as a
     tie-break (not a veto)
   - **(v) Recency** — newer evidence preferred *unless* the source is `SRC.is_seminal = true`
     (foundational sources never penalised for age)
   - **(vi) Seminality / influence** — `is_seminal` flag; citation count + landmark status
   - **Independence / conflict-of-interest discount** — advocacy sources (industry-funded,
     promotional grey lit, single-perspective NGO output) take a tier-down adjustment.

   The **C/I/D rubric** (Content · Impact · Data quality) used historically is **one summary
   view** of these six axes — both produce the same `benchmark_tier`. Don't store the six axes
   separately on every row; use the SRC fields `study_income_group`, `is_seminal`, `venue_type`,
   `method_type` to capture what's audit-relevant and let the tier represent the summary.
5. **Saturation stop-rule + cap.** Stop adding sources when (a) new sources add no new
   variables/thresholds *and* (b) tier coverage looks robust (at least 1 High + 2 Medium for
   shape-bearing claims; ML or scoping-candidate okay for selection-only). Hard cap ~20 sources
   per NbS × table; lift only with a recorded justification.

**Search & Translation Logic:**
- **Title-Only Filtering**: Programmatic queries target title-only fields (e.g., `display_name.search` in OpenAlex) rather than full-text searches to avoid high-citation noise and non-specific results.
- **Multilingual AGROVOC Integration**: Query terms incorporate synonyms, sub-practice names, and translations derived from the FAO AGROVOC thesaurus across four languages (English, Spanish, French, Portuguese) to ensure LDC context relevance.
- **Organization-Neutral Queries**: Web and database search strings must remain organization-neutral and focus on functional keywords (e.g., `agroforestry hazard mitigation guidelines manual` or `agroforestry climate adaptation manual`) to avoid over-constraining search results. Evaluation of institutional authority (e.g., prioritizing WOCAT, FAO, or World Bank publications) is performed during the relevance and credibility screening stages, not within the query strings themselves.
- **Human-in-the-Loop Triage**: Borderline papers are flagged and reviewed collaboratively (e.g., rejecting urban forestry and pure physiology, accepting mechanical wind models or temperate baselines) to establish clear task boundaries.

After screening: register in the Source Register (SRC), extract paper-first (§3 above), dedupe lineage cascades via `lineage_of`, and record disagreement (don't silently average). For non-English studies, the extraction logs verbatim quotes in their native language followed by a bracketed English translation: `"[Native Text] (English: [Translated Text])"`.

### Reproducible discovery log (PRISMA-lite, v0.2.7)

**Per NbS × table**, log:

- date of search
- search strings / queries
- sources & databases queried
- **counts** at each funnel stage: `returned → relevance_screened → included` (PRISMA-like)
- exclusions with reason

**Decision (v0.2.7):** store as **markdown** under `methodology/discovery_logs/<nbs>_<table>.md`
rather than a formal schema register. Rationale: at this phase the log is a *narrative audit
trail* for a handful of NbS × table combinations, not a structured query target — a register
would be over-engineered. Promote to a register if the audit pattern stabilises and downstream
code needs to query it (e.g. to surface "how was this T4 row's evidence set assembled?" in the
wireframe).

Each log mirrors a single bounded seed-set run; commits to it land alongside the per-paper
sweep commits so the audit trail tracks the EV register growth.

### Source-type register (v0.2.7) — classes documented but not yet machine-readable

Beyond the diamond classes above, the following source classes are **named here** so they're
not lost — machinery (registers, ingest paths, dedicated bounded seed-sets) is **deferred
until that table or analysis is in scope**:

- **Economic valuation** — ELD (Economics of Land Degradation), TEEB (The Economics of
  Ecosystems and Biodiversity), social-cost-of-carbon literature, voluntary-carbon-market price
  series. Feeds **T0 economic archetypes**, **T6 economic profile**, and the M5 scorecard's
  benefit-cost framing. Phase 2.
- **Gender-disaggregated / distributional evidence** — CGIAR GENDER Platform, FAO gender-and-land
  series, IFPRI WEAI (Women's Empowerment in Agriculture Index). Feeds T5
  `priority_need` (equity/GESI theme) and is the dataset side of the T5 equity-theme ratification
  question Pete still owes. Phase 2.
- **Deliberate maladaptation / failure / trade-off stream** — Eriksen et al., Schipper, the
  "negative cases" literature. Captures *where NbS made things worse* — counter-stories to the
  optimistic-corpus bias documented in §6.1. Feeds T6 conditionality (negative cases) and the
  publication-bias humility rule.
- **Dataset-discovery list for BIND / T1** — **STAC** index, **Awesome-GEE-Community-Catalog**,
  **HDX** (Humanitarian Data Exchange), **WB Data Catalog**, **AWS Open Data**. Server-side
  preferred per AGENTS.md dataset-sourcing rule (v0.2.6+). These feed Brayden's T1 download
  layer + BIND resolution; documented here so the discovery work isn't reinvented.

Each class becomes a candidate bounded seed-set when its target table moves into scope.

### Evidence-source principle — observed-reality signals (v0.2.6)

**Adoption / dis-adoption studies and MEL/MELIA evidence are observed-reality signals**, not
parallel to literature thresholds. They extend the **"constrain by observed distribution, not
modelled niche"** rule (§2.5) to the human-system side:

- Where an adoption study shows that practice X is *not* taken up in context Y despite a
  favourable bioclimatic envelope, that's evidence the **system_constraint** or
  **operational_constraint** dimension is binding — and the binding variable belongs in T4 with
  that dimension tag, not in T2/M2b.
- MEL reports show which conditions *actually* deliver the effect at scale, which feeds T6
  (effects + conditionality + economic profile) directly.
- Operationally: ingest these sources via the per-paper sweep (§3 above) with
  `SRC.method_type = adoption_study` or `mel_report` (added in v0.2.6). Tier them via the
  Source Register the same way as suitability papers — they are not a separate evidence stream.

This sharpens the corpus-selection rule for T4 system/operational variables (currently we
under-source them because the stocktake was scoped to spatial-suitability lit) and for T6
conditionality (currently empty `evidence_ids`).

Discovery's job is to find *what to look for and where*; it is allowed to be speculative because nothing it
proposes reaches a T4 parameter without passing through the evidence layer. Three feeds:

- **Scoping report** — first-class source: parse for the NbS definition, subpractices, named criteria, candidate variables.
- **Deep research** — targeted search beyond the stocktake (FAO land-evaluation frameworks, recent suitability studies) to widen the candidate set and surface missed sources.
- **Tools & code repositories** — search GitHub/Zenodo/OSF and tool registries for relevant implementations (suitability/MCDA packages, published model code, data pipelines). Repos often reveal the *operational* variable lists, thresholds and datasets that papers gloss — frequently more informative than the text.
- **ML variable-importance** — see §3.1.

Output: a **candidate-variable register** and a **candidate-source set**, both explicitly provisional.

**Discovery as an active, iterative process.** Do not treat candidate lists or the initial 220-paper stocktake as static, pre-completed databases. Discovery is an ongoing activity designed to determine whether we have everything we need, specifically targeting:
- **Gaps in the Stocktake Report**: The stocktake report is the foundational core of this work, but it must be actively audited and supplemented. Discovery searches for missed peer-reviewed studies, key local grey literature, and newer project reviews to add to the corpus.
- **Triage of Suggestions**: Many variables and datasets in initial registers are provisional suggestions. Active discovery queries these suggestions to confirm if they are supported by empirical literature or if they should be refined/combined.

Phasing: **Phase 1 works from the existing corpus** (already discovered, screened, tiered — see §11) to establish the baseline recipes; **Phase 2 executes bounded re-discovery passes** (incl. the repo/tool search above) to fill identified gaps and expand the stocktake foundation once the method is proven on the existing set.

**Discovery is per-table — the existing corpus was scoped to *suitability* (T4).** The 220-paper stocktake targeted spatial-suitability/MCDA methods, so it is a strong source for **T4** and decent for **T1/T3/T5/T6-effects** (extract-once, §5/§6), but a **weak** source for several tables that will need their own dedicated discovery passes against different literature: **T2** climate-risk formulation (climate-risk/AR6 lit + Brayden's M2), **T6 economics** (economic/CBA lit + CrossBoundary archetypes), **T0** economic archetypes/costs, and **T7** AEZ/farming-system vocabularies (GAEZ/Dixon standards, not papers). Plan a discovery pass per table, not one corpus for all.

### 3.1 ML as the variable-importance stream

**ML tells you *which* variables matter; it does not give defensible response shapes.**

- Methods: random forest / gradient boosting / SHAP on observed or proxy suitability → ranked **variable importance**, per AOI/region; can flag interactions and variables the literature overlooked.
- Partial-dependence can hint at shape but overfits and is AOI-specific — **shape is out of scope for ML by design.**
- Feeds the **variable-selection / thematic-grouping** step as a prioritisation signal and a two-way completeness check (literature has a variable ML finds irrelevant here → flag; ML finds a predictor literature missed → trigger a discovery/extraction pass).
- Stored as `evidence_type = ml_importance` (§5), carrying importance score + model/method + AOI + the explicit caveat that no shape is implied. The synthesiser may use it for *selection* but is structurally barred from using it for *params*.
- Caveat recorded on every ML unit: correlational, AOI-specific, sensitive to training data and reference frame — corroboration/prioritisation only.

---

## 4. Harmonisation + the Variable Ontology

The layer that makes evidence aggregatable and connects it to the data catalog. Surface names diverge —
"slope / terrain slope / gradient / % slope", "soil depth / effective depth / rooting depth", "SOC / organic
carbon / OM". A **Variable Ontology** registry lumps them:

`canonical_variable_id` · label · **aliases[]** · `canonical_unit` + **unit conversions** (e.g. slope % ↔ degrees) ·
`group_id` (→ Variable-Group vocab) · **`candidate_dataset_ids` → T1** (which datasets can supply it, at what resolution/tier) ·
**`min_meaningful_resolution_m`** (coarsest grid at which the variable stays valid — slope ≈ 30–90 m) ·
**`resolution_sensitivity`** (`low` \| `medium` \| `high`; derivatives like slope/TWI = high) · `derive_then_aggregate` (bool — scale-dependent derivatives computed native then summarised to grid).

Harmonisation runs on **discovered** variables (dedupe candidate list to canonical terms) and on **extracted**
variables (attach every evidence unit to a canonical variable). Method: embedding/fuzzy match → **human-confirmed**
mapping, logged (auditable lumping — the `_wh` dedup lesson). Payoff: all "slope" claims collapse to one
canonical variable for synthesis, and the canonical variable resolves straight to a T1 `dataset_id` (and is what
the wireframe's dataset replace/upload validation checks against).

Subpractice names harmonise the same way (alley cropping vs hedgerow intercropping → same family?).

---

## 5. Ingestion & extraction → the evidence layer

### 5.1 Document ingestion (vectorless, structure-aware)

Extraction reads from a **pre-processed structure index**, never a raw PDF. Process each source **once** with code
(no model tokens) into:

- **Page-tagged text** — every passage keeps its page number, so provenance (quote + page) is exact.
- **A structure index** — sections, plus **tables and figures as first-class nodes with captions + page numbers**.
  This is what makes figure/table content findable ("Table 3: Slope suitability classes, p.7"; "Fig 2: membership
  curve, p.9") instead of relying on a text chunk to have caught it.
- **Extracted tables** parsed to rows (caption + page retained) — suitability-class matrices are the richest
  threshold source. **Figures** keep their caption; when a threshold/curve lives *only* in a figure, do a small
  **targeted vision pass on that one page image**, not the whole PDF.

**Retrieval is vectorless** — keyword + structure navigation over the index, not embedding similarity. We borrow
from PageIndex-style "reason over a table-of-contents tree," BM25/keyword, and agentic `get_section`/`get_table`
navigation. This fits the method better than vector RAG because:

- **Deterministic & auditable** — "retrieved Table 3, p.7" is reproducible; a vector store is opaque and
  non-deterministic (a defensibility liability, not just a cost one).
- **High precision on known targets** — we already know what we're looking for (canonical variable + aliases +
  units), which is exactly where keyword/structure beats semantic search.
- **Tables/figures survive** — structure-aware indexing keeps them intact; naive chunk-and-embed shreds a table.
- **Cheap** — no embedding step, no vector DB, no re-embedding; send a few hundred tokens of relevant passages,
  not a 20k-token PDF. The cache is reusable across every variable, NbS and re-run.

*(Embeddings have at most an optional one-off role in alias discovery — "gradient" ≈ slope — which the
harmonisation ontology already covers; they are not the retrieval backbone.)*

**Storage & copyright.** The page-tagged text cache and extracted tables are a **local, gitignored** artifact
(the PDFs are copyrighted and the repo is public). What is committed: the ingestion **code**, the register
**schemas**, and the **structured evidence units** (short fair-use quotes + page refs) — never full-text
reproductions or the PDFs.

### 5.2 Source & Evidence registers

Two provenance registries sit **upstream of T4** and are reused by T3 and T6 (all evidence-based tables). They
formalise what is today free-text in `justification`/`references`.

**Source Register** (one row per publication — this *is* the stocktake CSV, formalised):
`source_id` · citation · DOI · **benchmark_tier** (High/Med/Low — already scored) · impact factor · cites/yr ·
**study_country / region / coords** · **AEZ · farming_system** · method_type · spatial_scale · NbS(s) addressed.

**Evidence Register** (one row per atomic claim):
`evidence_id` · `source_id` (FK) · `nbs_id` · `suitability_family_id` · canonical `variable` · the extracted
relationship (e.g. *optimal 0–15°, unsuitable >35°*) · implied direction/shape · **context it applies to**
(AEZ/farming system) · `evidence_type` · `claim_basis` · `claim_scope` · `taxon` · `extraction_confidence` · **verbatim quote + page** · `reviewer_ok`.

**Source tier is not stored here** — `benchmark_tier` is a property of the *paper*, so it lives once on the
Source Register and is reached by the `source_id` join (re-score in one place; views may show it). Four
*orthogonal* per-claim axes live on the Evidence Register:

- `evidence_type ∈ { literature_relationship · ml_importance · scoping_candidate · expert }` — the **kind** of evidence. Only `literature_relationship` / `expert` may carry shape-bearing params; `ml_importance` / `scoping_candidate` feed selection only.
- `claim_basis ∈ { primary_measured · modelled · cited_secondary · expert_assertion · table · figure_read }` — how **strongly** *this* claim is supported *within* its source. Distinct from the paper's tier: a Low-tier paper can carry a `primary_measured` threshold while a High-tier paper offers only a `cited_secondary` ranking (we saw exactly this on slope).
- `claim_scope ∈ { practice_technology · species_specific · crop_specific }` (+ `taxon` when not practice-level) — **what the claim is about.** See the callout below.
- `extraction_confidence` — how **faithfully** we transcribed it.

> **Species vs technology (`claim_scope`) — read this.** Many "agroforestry suitability" papers actually model a
> **single tree/crop species** (e.g. mulberry in Mushtaq, sengon in Haris). Their climatic/edaphic optima are the
> *species'* bioclimatic envelope — that is **species suitability modelling, not agroforestry-practice modelling.**
> Tag every claim:
> - `practice_technology` — the constraint comes from the *practice* (slope/erosion/mechanisation, soil depth, land
>   cover, tenure, road access). Safe to use for the practice-level T4 row.
> - `species_specific` / `crop_specific` (+ `taxon`) — the constraint is a particular taxon's envelope
>   (temperature/rainfall/altitude optima of mulberry, coffee, etc.). **Do not let these define a practice-level
>   row.** They are routed to a *species/crop suitability* product, or used only where the species is an explicit
>   exemplar of the family and flagged as such.
>
> Variable-level heuristic: slope, soil depth, erosion, mechanisation, road/market access are usually
> **technology-driven**; temperature/rainfall/altitude optima are usually **species-driven**. The exception is
> **F5 (shaded perennial crops)**, where `crop_specific` *is* the model by design — the understorey crop's envelope
> is the point — handled per-crop via the `ecocrop` composite. The stocktake already half-recognised this: it
> excluded "suitability of 1 tree" papers (e.g. *Lansium domesticum*) at screening.

Extraction is **per source, atomic, quote-mandatory, no inference.** Run extractors in parallel across the corpus.

---

## 6. Synthesis → T4 rows

One variable (within one suitability family) at a time: combine its evidence units into a single T4 row.

- **Scope filter first** — drop/route `species_specific` & `crop_specific` claims before weighting a *practice-level* row (except F5, where `crop_specific` is the model). A species' rainfall optimum must not set the practice's rainfall envelope.
- **Ranking / weighting** — an evidence unit's weight ≈ `f(source_tier [joined], claim_basis, context_match, recency)`. A High-tier study in your AEZ/farming system outweighs a Low-tier one from a different biome — but a Low-tier `primary_measured` threshold can outweigh a High-tier `cited_secondary` ranking (`claim_basis` does that work).
- **Thresholds / optima** → tier-weighted reconciliation (e.g. weighted median for `opt_low/opt_high/abs_max`); the **spread sets `uncertainty_pct`** (real disagreement, not a guess).
- **Context-specific values** → where High-tier sources in a specific AEZ disagree with the global picture, that becomes a **`context_override`** keyed to T7, not averaged away.
- **Variable selection (now 3 signals)** → (1) **literature prevalence** `paper_support_pct` — weighted prevalence ratio of the family's screened corpus with ≥1 evidence unit for the variable (scaled by each paper's benchmark tier authority weight, as the provenanced successor to the stocktake variable-frequency heatmap), rolled up the hierarchy to group level by **set-union** over members; (2) **ML importance**; (3) **thematic fit** (group vocab + scoping target). These feed thematic grouping; **per-AOI correlation clustering** then prunes to one representative per cluster at runtime.
- **Filter before T4? Soft floor, not a hard cut.** Carry every candidate variable into T4 *with* its `paper_support_pct`, `n_sources` and ML flag. A variable below a prevalence floor (default 20 %) is **flagged `review_low_support` for a recorded inclusion decision**, not auto-dropped — because prevalence is as much *convention* (citation echo, publication bias) as importance, and a rarely-published variable can be locally decisive (ML can rescue it → `include_ml_override`). Hard, statistical pruning is left to correlation clustering; inclusion/exclusion is an auditable, admin-gated decision (mirrors the wireframe's "edit included variables").
- **Output** → a T4 row with `relationship_type` + `relationship_params`, `uncertainty_pct`, `context_overrides`, `weight_default`, **`paper_support_pct` + `n_sources` + `corpus_n`**, `justification` (citing `evidence_id`s), `references`, and `dataset_id` resolved via the ontology.

### 6.1 Publication bias & uncertainty (pragmatic)

The evidence base skews **optimistic** — papers map where an NbS *works*, rarely where it fails — so it
systematically **over-states suitable area and generous thresholds.** The bias is *directional*, which is what
makes it tractable without meta-analysis machinery. Handle it with what we already have:

- **Dedupe by source *lineage*, not paper count.** Ten papers echoing one original "slope <15°" is one claim, not
  ten. Collapse `cited_secondary` echoes to their origin and weight **independent** evidence only — pseudo-consensus
  is the main trap.
- **Capture the *unsuitable* tail.** The extraction prompt explicitly grabs exclusion/failure/maladaptation
  thresholds and caveats (most papers state them even while emphasising the positive) — this directly recovers the
  missing-negative that bias suppresses.
- **A tight consensus *widens* uncertainty, it doesn't narrow it.** Bias compresses the *reported* spread, so true
  uncertainty exceeds observed. Never let a suspiciously tight (citation-driven) cluster shrink `uncertainty_pct`;
  default to **conservative reconciliation** (tighter optimal, lower abs_max) where the bias is directional —
  under-promise at scoping grade.
- **Triangulate against bias-independent anchors** — first-principles agronomic limits (FAO land evaluation /
  EcoCrop physiological thresholds) as a prior, and the **ML presence/absence** stream (observational data includes
  where the practice *isn't*). Flag where literature thresholds disagree with the mechanistic limit.
- **Reward validation, down-weight assertion** — `claim_basis` (`primary_measured`/validated > `cited_secondary`/`expert_assertion`) already does this.
- **Make the optimism visible** — run the ±sensitivity pass as conservative-vs-optimistic scenarios, with a
  standing caveat that the evidence skews positive.

*Not used:* funnel plots / Egger / trim-and-fill — they need effect sizes + standard errors we don't have
(thresholds, not effects). This is honest direction and humility, not a statistical correction.

---

## 7. Validation & sign-off

- **Schema validation** — FK integrity (incl. `context_overrides → T7`, `dataset_id → T1`), enum/vocab validity, required-field coverage.
- **Adversarial review pass** — does every parameter trace to evidence units? Any threshold without a source? Any inference beyond the quotes? Are conflicts recorded? Reject-and-explain.
- **Human gates (roles).** *Intermediate* QA/QC — extraction fidelity, harmonisation, the adversarial review pass — is owned by the **extraction team + Claude** (the adversarial-reviewer agent). **Benson reviews later-stage outputs** (dataset fitness sign-off, output validation, resolution audit), not every intermediate evidence unit. **Namita reviews the family scheme and recipe content, consulting the MFL team.** This keeps the human bottleneck at the points that matter.

---

## 8. Schema additions (proposed)

Beyond the existing T0–T7. These feed T3 and T6 too, not just T4.

| New registry | Purpose | Key fields |
|---|---|---|
| **Source Register** | Publications + ranking (formalised stocktake) | `source_id` · tier · DOI · study context (country/AEZ/farming_system) · method_type |
| **Evidence Register** | Atomic claims with provenance | `evidence_id` · `source_id` · `suitability_family_id` · canonical `variable` · extracted relationship · context · `evidence_type` · **`claim_basis`** · **`claim_scope` + `taxon`** · `extraction_confidence` · quote + page (tier via `source_id` join) |
| **Variable Ontology** | Canonical variables, harmonisation, catalog link | `canonical_variable_id` · aliases[] · unit + conversions · `group_id` · `candidate_dataset_ids → T1` · **`min_meaningful_resolution_m`** · **`resolution_sensitivity`** · `derive_then_aggregate` |
| **Variable-Group vocab** | Thematic grouping (T4 + T5) | `group_id` · label · definition · `applies_to` |
| **Subpractice / Suitability-Family registry** | NbS decomposition + grouping | `subpractice_id` · `nbs_id` · name · definition · `suitability_family_id` · **`dominant_limiting_factor`** · **`spatial_product_type`** (`area_suitability` \| `applicability_zone` \| `zonal_linear` \| `qualitative_only`) · grouping rationale + refs |

**T4 change:** key rows to `suitability_family_id` (subpractices roll up to NbS for display). Target/scope
definitions attach per family (recipe header + structured fields).

---

## 9. Claude operationalisation — agents, skills, prompts

**Subagents** (each a tight contract; parallelise where possible):

- **Discovery agent** — given NbS + scoping report, emit the subpractice→family taxonomy, per-family target specs, and the candidate-variable/source sets. Reuses the deep-research skill.
- **Practice-taxonomy** step — decompose NbS → subpractices → suitability families with rationale.
- **ML-importance** step — runs in `src/nbs_ruralscan/`; Claude orchestrates, interprets, and writes typed `ml_importance` evidence units.
- **Harmoniser** — surface name → canonical variable (+ unit) → T1 dataset; classify into the group vocab; flag misses for a human.
- **Ingestor** (code, *no model tokens*) — runs in `src/nbs_ruralscan/`: PDF → page-tagged text + structure index (sections/tables/figures w/ captions+pages) + parsed tables; OCR fallback for scanned PDFs. Builds the gitignored cache the extractor reads from.
- **Retriever** — vectorless: keyword + structure navigation (`get_section`/`get_table`, BM25, PageIndex-style tree reasoning) returns the relevant passages/tables/figure-pages for a target variable. A targeted **vision** call reads a figure only when a threshold/curve is figure-only.
- **Extractor** — one source → evidence units from the retrieved passages, strict JSON schema, quotes mandatory, no inference.
- **Synthesiser** — one (family × variable) → one T4 row, applying the §6 rules, citing `evidence_id`s, uncertainty from spread.
- **Adversarial reviewer** — the §7 defensibility check.

**Skills** (versioned in-repo, the reusable protocol):

- `doc-ingestion` — PDF → page-tagged text + structure index + parsed tables (vectorless retrieval contract); the cache the extractor reads.
- `t4-discovery` — scoping-report parse + deep-research scope + candidate registers.
- `practice-taxonomy` — NbS → subpractice → suitability-family decomposition + grouping rationale.
- `variable-harmonisation` — the Variable Ontology + group vocab + alias/unit resolution rules.
- `t4-evidence-extraction` — the Source/Evidence schemas, controlled vocab, few-shot good-vs-bad examples, hard rules.
- `t4-synthesis` — aggregation/weighting rules, uncertainty-from-spread, context-override logic, justification template.

**Prompt principles** (more important than exact wording): extraction forbids inference, requires a quote + page
per claim and explicit "not stated" for missing params; synthesis must cite `evidence_id`s and surface
disagreement; everything is pinned to vocab lists passed in-context so outputs are enumerable; discovery is
labelled candidate-generating and never writes params.

---

## 10. Start here — the vertical slice

Don't extract the whole corpus first. Take **agroforestry × slope** (family **F1 Planted silvoarable**) end-to-end
to produce one gold-standard example, then build the extraction skill to reproduce it by machine (the gold
standard is itself part of the defensibility story):

1. **Define** — *done* (§2.1): agroforestry families F1–F4 + homegardens + riparian, from the Inception Report longlist; F1 target spec = where planted silvoarable can establish.
2. **Vocab** — classify `slope` into the Topographic group; register canonical `slope` (aliases: terrain slope, gradient; unit ° with %↔° conversion) linked to SRTM in T1.
3. **Ingest** — build the page-tagged + table-aware cache (§5.1) for the 23 agroforestry PDFs in `Stocktake Review/.../Agroforestry/` (gitignored).
4. **Retrieve + extract** — pull slope claims (text *and* suitability-class tables; targeted figure-vision only if needed) → evidence units with quote + page + tier (from the benchmarked CSV) + study context.
5. **Synthesise** the F1 slope T4 row; check the provenance chain holds end to end — and test the tier tension (the crisp slope thresholds are in Low-tier papers; the High-tier ones are MCDA-framing).

This single slice exercises practice definition, variable grouping, target spec, ingestion, harmonisation, the
evidence types, and synthesis.

### Sequencing (team decisions, June 2026)

- **Pilot = agroforestry, depth-first.** After the slope slice, complete **all F1 variables** → the first full
  recipe, rather than one variable across many families.
- **Start with alley-cropping-type silvoarable** within F1 (the best-evidenced, clearest subpractice) to get moving.
- **Family scheme is a draft pending review** — Namita reviews and consults the MFL team before it's locked.
- **Also build the water-harvesting taxonomy** (the second NbS). When building any taxonomy, **reference and reuse
  existing classifications** (FAO/ICRAF agroforestry typologies, FAO land evaluation, Dixon farming systems, GAEZ)
  rather than inventing — adopt where a credible standard exists.
- **Extract-once is the goal, but earn it per table.** Before populating T3/T5/T6 from the same pass, develop the
  **per-table extraction sub-instructions/skills** (T3 mitigation-matrix, T5 priority-layer, T6 effects) so each is
  extracted the right way; T4 leads, the others follow once their contracts exist.

## Open questions still open

- ~~Registers as formal schema tables?~~ **Resolved — promoted to `spec.md` (evidence & configuration layer).**
- ~~Scoping report rich enough?~~ **Resolved** (§11).
- ~~Human review per tier?~~ **Resolved** — intermediate QA = extraction team + Claude; Benson reviews later-stage outputs; Namita + MFL review families/recipes (§7).
- How do we **version the corpus** so a T4 row is reproducible against a frozen evidence set? *(Proposal: freeze the ingested cache + Source/Evidence registers per run, hash-stamped.)*
- T3/T5/T6 **per-table extraction contracts** — to be authored before extract-once.
- **Climate variables in F1 — load-bearing or redundant?** Open for team review (Pete, 2026-06-04 while reviewing annual_precipitation). Hypothesis: once a pixel is not rocky / frozen / desert (gated by land cover, ecosystem layer, AEZ mask), trees can grow → agroforestry biophysically possible. The crisp climate thresholds in the corpus are nearly all **species** envelopes routed out by `claim_scope`; the surviving *practice-level* claims (Haile, Nath on precip) bottom out at "not desert / not freezing," which other layers already exclude. Tension with §2.5's distribution-over-niche rule. If climate is redundant in F1, replace per-variable envelopes with a single non-extreme-environment composite (or let correlation clustering prune it per AOI). Decide once F1 climate variables are extracted end to end; ML-importance on the pilot AOI is the natural decider.

---

## 11. Prior assets to reuse (existing corpus)

Learned from `2_Technical_&_Data/Stocktake Review` and `…/Methodology`. The prior project already did discovery,
screening, ranking and context capture well — **reuse, don't rebuild** — but it left variable × suitability
relationships unstructured, which is exactly this method's job.

| Asset (path under `2_Technical_&_Data/`) | Reuse as | Notes |
|---|---|---|
| `Stocktake Review/data/NbS_peer_reviewed_benchmarked.csv` | **Source Register** seed | 220 papers, tiered High/Med/Low; Agroforestry = 23 (5 High). Carries DOI, IF, geo scope, study context. |
| Extraction template C1–C4 / I1–I4 / D1–D4 rubric | **tier weighting** in synthesis | Drop IF/CPY weighting (optional). |
| `Stocktake Review/Open Alex search/` (`OpenAlex_run.R`, `search_string.xlsx`) + GPT grey-lit | **Discovery** machinery (Phase 2) | Already run for agroforestry; reuse for new NbS. |
| `Stocktake Review/figures/fig02_nbs_x_input_heatmap` + `Methodology/.../Input Catalog.docx` + input-variables xlsx (Agroforestry sheet) | **candidate-variable + literature-frequency** prior | Complements the ML-importance stream. |
| `Stocktake Review/Manual Screening/.../Agroforestry/` (23 PDFs) | **ingestion corpus** for the slice | 1:1 with the benchmarked tiers. |
| `Methodology/Spatial_Methodological_Plan_NbS Scoping_v2.docx` + `spatMCDA.R` | framework primitives (already in design) | Confirms 5 fuzzy MFs + structural/climate/feasibility split; note its MF naming differs from the wireframe → our canonical `relationship_type` reconciliation was needed. |
| `Methodology/Claude/Spatial_Methodological_Plan_Water_Harvesting_NbS_v1.docx` (+ `Water Harvesting.xlsx`) | **`scoping_candidate` reference** for the WH taxonomy (issue M) — candidate variables + subpractice structure | **Reference only.** How it was created is unknown and it carries **no decision history** to explain / reference / justify its variable selection. Feeds discovery (what to look for); every variable must then be substantiated through the evidence layer before entering WH T4. Do **not** cite it as justification. Same rule as the agroforestry draft-0 tables. |

**The gap (= our contribution):** the old extraction stored thresholds in free-text `Narrative` + semicolon
`Input_Variables`, with no atomic claims, no per-claim quote/page provenance, no harmonised names, no family
keying, no uncertainty from spread. The Evidence Register + harmonisation + family-keyed synthesis is that
missing layer. **Skip:** re-running discovery/screening for agroforestry, IF/CPY weighting, and the free-text
Narrative as the carrier.
