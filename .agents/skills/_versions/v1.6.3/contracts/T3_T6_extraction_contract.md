# Extraction Contract — effect claims for T3 / T6 (ruleset v1.6.0)

Governs how an extractor emits `EvidenceUnit`s with `use_role = nbs_effect` or `asset_vulnerability`.
Replaces the archived v1.4.2 `T3_contract.md` / `T6_contract.md` (which asked for finished table rows per
paper — the failed design). Method: `methodology/T3_T6_generation_method.md` §3 (atom), §4 (crosswalk),
§6 (sources), §10 (migration). Schema: `schema/spec.md` v0.4.0.

**Everything in the T4 extract-evidence skill still applies** (verbatim sliced quotes, page stamps, cached
artefact only, defect catalogue #1–#18, staging-only, never git). This contract adds the effect-claim shape.

---

## 0. What you are NOT doing

- You are **not** writing a T3 or T6 row. You are recording **what one source says about one outcome**.
  Direction, strength, confidence and applicability are computed later, over the pool.
- You are **not** mapping the outcome to a T5 priority or a T3 hazard. Record the outcome the paper measured
  (VONT canonical id). The `XW` register does the routing.
- You are **not** deciding whether the finding transfers to LMICs. Record the context; the engine weights it.
- You are **not** emitting `use_role = climate_risk` or `priority_need` (reserved, unused).

## 1. Roles

| `use_role` | Emit when the source says… | Examples |
|---|---|---|
| `nbs_effect` | the NbS **changes an outcome** (yield, erosion, carbon, income, biodiversity, a hazard's impact on livelihoods) | "alley cropping raised maize yield by 23 %"; "riparian buffers removed 60–90 % of sediment"; "silvopasture reduced fuel loads" |
| `asset_vulnerability` | a hazard **damages or kills the NbS asset** | "seedling mortality reached 70 % in the 2015 drought"; "windthrow losses in shelterbelts"; WOCAT: "technology tolerates drought moderately" |
| `structural_suitability` / `operational_risk` / `dataset` | unchanged T4 rules | |

**PICOS still applies:** the NbS practice must be explicit in the source. A generic land-use effect study is not
an NbS effect claim.

**Single pass.** Read the paper once for every live role. If a sweep is T4-only (contract not yet active for that
NbS), do not extract effects — instead emit a **deferred-effect pointer** per claim in the sweep report:
`{source_id, page, claim_kind: nbs_effect|asset_vulnerability, outcome_raw, note}`.

## 2. Required fields on an effect unit

Everything the T4 skill requires (`evidence_id`, `source_id`, `nbs_id`, `suitability_family_id`, `variable`,
`use_role`, `evidence_type`, `claim_basis`, `claim_scope`, `quote`, `page`/`locator`, `extraction_confidence`,
`ruleset_version = v1.6.0`) **plus**:

### 2.1 `variable`
The **VONT canonical outcome variable the paper measured** (`crop_yield`, `erosion_hazard`, `carbon_sequestration`,
`household_income`, `fire_hazard`…). Keep `raw_name` = the paper's own wording. If no VONT id exists, **stop and
raise an ontology-triage note**; do not invent an id or borrow the nearest T5 id.

### 2.2 `relationship` — the effect-claim object

```json
{
  "direction": "positive | negative | none",
  "strength_class": "slight | moderate | strong | unspecified",
  "metric": "smd_hedges_g | pct_change | ln_response_ratio | absolute | ordinal_rating | narrative",
  "magnitude": 23.0,
  "magnitude_low": 11.0,
  "magnitude_high": 35.0,
  "unit": "percent",
  "framing": "presence | loss",
  "significance": "sig | ns | not_reported",
  "n": 14,
  "design": "meta_analysis | rct | quasi_experimental | observational | model | case_study | expert | practitioner_rating",
  "outcome_raw": "maize grain yield, alley cropping vs sole crop"
}
```

Rules:

1. **`direction` is relative to the outcome variable as named.** `erosion_hazard` + `negative` = erosion went
   *down*. Never translate to "good/bad for people".
   **`framing`** (added 2026-09-30, riparian pilot): `presence` (default — the source measured the effect of the
   buffer / practice being present or added) or **`loss`** — the source measured what happens when the
   vegetation / practice is LOST or absent (dose-response to native-vegetation loss, deforestation → floods).
   Record the direction exactly as measured and set `framing = "loss"`; the engine flips the sign into the
   intervention-present frame. Never pre-flip the direction yourself.
2. **Every number in `magnitude*` and `n` must appear verbatim in `quote`** (`check_numbers`). No number in the
   quote → no `magnitude`, `metric = narrative`.
3. **`strength_class` comes from BANDS** (`schema/registers/BANDS_magnitude_bands.csv`) when `metric` has a band;
   otherwise `unspecified`. Never assign `strong` from adjectives ("substantially", "dramatically").
4. **`significance = ns`** when the CI spans zero or p > 0.05 is reported. Keep the unit; do not drop null or
   non-significant findings — they are the unsuitable tail (T4 method §6.1).
5. **`metric = absolute`** for raw values with a physical unit (t/ha/yr, mm, USD/ha). `unit` required.
6. **Economics**: `magnitude` only with a **per-unit denominator** (`usd_per_ha`, `usd_per_ha_yr`,
   `usd_per_beneficiary`, `usd_per_tco2e`, `usd_per_farmer`). A project total ("US$873.6 million") is **not** an
   economic effect claim — record it as `metric = absolute`, `unit = usd_total`, and it will fail the gate by design.
   Record currency year in `note`.
7. **Hazard-mitigation units** (`nbs_effect` whose outcome is a hazard) also carry in `context`:
   `hazard_type` (T3 enum), `farming_system` (T7 id or `all`), `landscape_scale_only` (bool),
   `timescale_of_effect` (T3 enum) — each **only if the source states it**; blank otherwise.
8. **Asset-vulnerability units** carry `context.hazard_type` and, if stated, `context.timescale_of_effect` as the
   vulnerability window (e.g. `short_term_1_3yr` for establishment losses). `direction = positive` means the hazard
   damages the asset more; `strength_class` from BANDS `ordinal_rating` rows for WOCAT-style scales.

### 2.3 `context` — fixed keys only

| Key | Vocab | Fill from |
|---|---|---|
| `country` | ISO3 list | paper's study area; default `SRC.study_country` |
| `region` | free text (informational) | |
| `aez` | T7 `aez` id | paper or SRC |
| `farming_system` | T7 `farming_system` id | paper or SRC |
| `income_group` | `low · lower_middle · upper_middle · high` | `schema/lookups/wb_income_groups.csv` from `country` |
| `climate_zone` | `tropical · dryland · temperate · boreal` | from `aez` or `country` when `aez` blank |
| + the hazard keys in 2.2.7–8 | | |

Anything else (site name, altitude, commodity) goes in `note`, not `context`. `check_context.py` fails unknown keys,
out-of-vocab values, and a blank `income_group` where `country` is known. Multi-site papers: one unit per site
context if the paper reports them separately; otherwise the modal context.

### 2.4 `claim_scope`
Unchanged: a per-species mortality or yield figure is `species_specific` / `crop_specific` + `taxon`; kept, routed
out of practice cells. A practice-level meta-analysis is `practice_technology`.

## 3. Defects specific to effect claims (add to the catalogue)

| # | Defect | Rule |
|---|---|---|
| E1 | **Row-authoring** — emitting `effect_direction`, `mitigation_potential`, `confidence` or `variable_id` on a unit | Those are engine outputs. Emit `direction` + `strength_class` + outcome variable only. |
| E2 | **Silent proxy** — labelling an income result as `rural_poverty`, a runoff result as `erosion_hazard` | Record what was measured; XW routes. |
| E3 | **Adjective strength** — `strong` from "significantly", "greatly" | BANDS or `unspecified`. |
| E4 | **Denominator-less economics** — a project budget line as an establishment cost | `unit = usd_total`, will fail the gate; or skip. |
| E5 | **Context key sprawl** — `study_region`, `location`, `countries`… | §2.3 keys only. |
| E6 | **Dropping nulls** — omitting a non-significant or negative finding because it "doesn't fit" | Extract it, `significance = ns` / `direction = negative`. |
| E7 | **Inferred hazard** — tagging `hazard_type = drought` because the region is dry | Only when the source names the hazard. |
| E8 | **Sign in the wrong frame** — `direction = positive` on `erosion_hazard` to mean "good" | Direction is on the outcome as named. |

## 4. Deliverable per source

Staging file `pipeline/staging/<source_id>__effects.json` (units) + report block: units emitted per role, deferred
pointers, ontology-triage notes, economics recorded without denominator, blockers (two-column PDFs, unquotable
tables). Never write to registers; never run git.
