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
- **Subpractices** — the variants: alley cropping, parkland/FMNR, silvopasture, windbreaks, homegardens, riparian buffers…
- **Suitability families** — **groups of subpractices that respond to the same suitability variables in the same way.**
  This is the unit T4 is authored against. Tree-on-cropland systems (alley cropping, parkland) likely share
  slope/rainfall/soil-depth drivers; silvopasture pulls in pasture/livestock context; riparian buffers are
  water-proximity-driven — a different family.

**T4 is keyed to `suitability_family_id`, not to the whole NbS.** The grouping must carry a documented rationale
with references (the same biophysical-logic check `CLAUDE.md` enforces at cluster level — "water harvesting ≠
wetland creation"). The grouping is mildly circular (group by shared drivers, discover drivers partly by
grouping), so treat it as a **first-pass hypothesis from the scoping report + a discovery pass, revisable** once
evidence is in — recorded so the revision is auditable.

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

---

## 3. Discovery (recall-first — proposes candidates)

Discovery's job is to find *what to look for and where*; it is allowed to be speculative because nothing it
proposes reaches a T4 parameter without passing through the evidence layer. Three feeds:

- **Scoping report** — first-class source: parse for the NbS definition, subpractices, named criteria, candidate variables.
- **Deep research** — targeted search beyond the stocktake (FAO land-evaluation frameworks, recent suitability studies) to widen the candidate set and surface missed sources.
- **ML variable-importance** — see §3.1.

Output: a **candidate-variable register** and a **candidate-source set**, both explicitly provisional.

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
`group_id` (→ Variable-Group vocab) · **`candidate_dataset_ids` → T1** (which datasets can supply it, at what resolution/tier).

Harmonisation runs on **discovered** variables (dedupe candidate list to canonical terms) and on **extracted**
variables (attach every evidence unit to a canonical variable). Method: embedding/fuzzy match → **human-confirmed**
mapping, logged (auditable lumping — the `_wh` dedup lesson). Payoff: all "slope" claims collapse to one
canonical variable for synthesis, and the canonical variable resolves straight to a T1 `dataset_id` (and is what
the wireframe's dataset replace/upload validation checks against).

Subpractice names harmonise the same way (alley cropping vs hedgerow intercropping → same family?).

---

## 5. Extraction → the evidence layer

Two provenance registries sit **upstream of T4** and are reused by T3 and T6 (all evidence-based tables). They
formalise what is today free-text in `justification`/`references`.

**Source Register** (one row per publication — this *is* the stocktake CSV, formalised):
`source_id` · citation · DOI · **benchmark_tier** (High/Med/Low — already scored) · impact factor · cites/yr ·
**study_country / region / coords** · **AEZ · farming_system** · method_type · spatial_scale · NbS(s) addressed.

**Evidence Register** (one row per atomic claim):
`evidence_id` · `source_id` (FK) · `nbs_id` · `suitability_family_id` · canonical `variable` · the extracted
relationship (e.g. *optimal 0–15°, unsuitable >35°*) · implied direction/shape · **context it applies to**
(AEZ/farming system) · `evidence_type` · `extraction_confidence` · **verbatim quote + page** · `reviewer_ok`.

`evidence_type ∈ { literature_relationship · ml_importance · scoping_candidate · expert }`.
**Only `literature_relationship` / `expert` may carry shape-bearing params**; `ml_importance` and
`scoping_candidate` feed selection only.

Extraction is **per source, atomic, quote-mandatory, no inference.** Run extractors in parallel across the corpus.

---

## 6. Synthesis → T4 rows

One variable (within one suitability family) at a time: combine its evidence units into a single T4 row.

- **Ranking / weighting** — an evidence unit's weight ≈ `f(benchmark_tier, context_match, recency, method_credibility)`. A High-tier study in your AEZ/farming system outweighs a Low-tier one from a different biome.
- **Thresholds / optima** → tier-weighted reconciliation (e.g. weighted median for `opt_low/opt_high/abs_max`); the **spread sets `uncertainty_pct`** (real disagreement, not a guess).
- **Context-specific values** → where High-tier sources in a specific AEZ disagree with the global picture, that becomes a **`context_override`** keyed to T7, not averaged away.
- **Conflicts** → recorded explicitly in `justification` with the `evidence_id`s ("3 High-tier sources support 0–15°; Nath 2021 (Himalayan, High) extends to 20° → captured as a humid-tropics override"), never silently resolved.
- **Variable selection (2-stage)** → thematic grouping (does this variable belong, per the group vocab + scoping target) then **per-AOI correlation clustering** (one representative enters MCDA). ML importance informs grouping/priority; clustering prunes at runtime.
- **Output** → a T4 row with `relationship_type` + `relationship_params`, `uncertainty_pct`, `context_overrides`, `weight_default`, `justification` (citing `evidence_id`s), `references`, and `dataset_id` resolved via the ontology.

---

## 7. Validation & sign-off

- **Schema validation** — FK integrity (incl. `context_overrides → T7`, `dataset_id → T1`), enum/vocab validity, required-field coverage.
- **Adversarial review pass** — does every parameter trace to evidence units? Any threshold without a source? Any inference beyond the quotes? Are conflicts recorded? Reject-and-explain.
- **Human gates** — extraction validated (full review for High-tier, spot-check for Low?), and a final family-level sign-off. This is where Benson's QA/QC role lands (dataset fitness, output validation, resolution audit).

---

## 8. Schema additions (proposed)

Beyond the existing T0–T7. These feed T3 and T6 too, not just T4.

| New registry | Purpose | Key fields |
|---|---|---|
| **Source Register** | Publications + ranking (formalised stocktake) | `source_id` · tier · DOI · study context (country/AEZ/farming_system) · method_type |
| **Evidence Register** | Atomic claims with provenance | `evidence_id` · `source_id` · `suitability_family_id` · canonical `variable` · extracted relationship · context · `evidence_type` · quote + page · confidence |
| **Variable Ontology** | Canonical variables, harmonisation, catalog link | `canonical_variable_id` · aliases[] · unit + conversions · `group_id` · `candidate_dataset_ids → T1` |
| **Variable-Group vocab** | Thematic grouping (T4 + T5) | `group_id` · label · definition · `applies_to` |
| **Subpractice / Suitability-Family registry** | NbS decomposition + grouping | `subpractice_id` · `nbs_id` · name · definition · `suitability_family_id` · grouping rationale + refs |

**T4 change:** key rows to `suitability_family_id` (subpractices roll up to NbS for display). Target/scope
definitions attach per family (recipe header + structured fields).

---

## 9. Claude operationalisation — agents, skills, prompts

**Subagents** (each a tight contract; parallelise where possible):

- **Discovery agent** — given NbS + scoping report, emit the subpractice→family taxonomy, per-family target specs, and the candidate-variable/source sets. Reuses the deep-research skill.
- **Practice-taxonomy** step — decompose NbS → subpractices → suitability families with rationale.
- **ML-importance** step — runs in `src/nbs_ruralscan/`; Claude orchestrates, interprets, and writes typed `ml_importance` evidence units.
- **Harmoniser** — surface name → canonical variable (+ unit) → T1 dataset; classify into the group vocab; flag misses for a human.
- **Extractor** — one source → evidence units, strict JSON schema, quotes mandatory, no inference.
- **Synthesiser** — one (family × variable) → one T4 row, applying the §6 rules, citing `evidence_id`s, uncertainty from spread.
- **Adversarial reviewer** — the §7 defensibility check.

**Skills** (versioned in-repo, the reusable protocol):

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

Don't extract the whole corpus first. Take **agroforestry × slope** end-to-end through every stage to produce one
gold-standard example, then build the extraction skill to reproduce it by machine (the gold standard is itself
part of the defensibility story):

1. **Define** — from the scoping report, pull the agroforestry definition + subpractices; propose 2–3 suitability families with rationale; write the target spec for one family (tree-on-cropland).
2. **Vocab** — classify `slope` into the Topographic group; register canonical `slope` (aliases: terrain slope, gradient; unit ° with %↔° conversion) linked to the SRTM dataset in T1.
3. **Discover** (+ optional toy ML importance unit for slope).
4. **Extract** 3–4 evidence units from stocktake papers (quote + page + context + tier).
5. **Synthesise** the T4 row for that family; check the provenance chain holds end to end.

This single slice exercises practice definition, variable grouping, target spec, discovery, ML, harmonisation,
the evidence types, and synthesis.

## Open questions to settle early

- Do the Source / Evidence / Ontology / Family registers become **formal schema tables** (recommended — they feed T3/T6) or live as working files first?
- Is the **scoping report** rich enough to seed the family grouping, or do we need a discovery pass to propose it? *(Point me at the report and I'll sanity-check.)*
- How much **human review per tier** (full High, spot-check Low)?
- How do we **version the corpus** so a T4 row is reproducible against a frozen evidence set?
