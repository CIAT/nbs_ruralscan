# Expert-Opinion Elicitation & Integration Protocol

**Status:** v0.1 draft for team review · June 2026  
**Owner:** Namita (Task H Lead) · Pete (Oversight & Framework Integration)  
**Applies to:** Turning expert interviews, surveys, and focus group inputs into structured database entries in `schema/registers/EV_evidence_register.json` (`evidence_type = "expert"`).

---

## 1. Objectives & Framing

While peer-reviewed literature forms the baseline for the Rural NbS Scan, expert opinion is critical for:
* Filling gaps where local literature is absent (especially for emerging practices).
* Identifying **soft operational constraints** and **adoption barriers**.
* Resolving **context-specificity** (the "it depends" factor).
* Aligning qualitative views on hazard resilience and scorecard impact.

Because expert feedback is inherently unstructured, this protocol provides a repeatable workflow to **elicit, structure, and translate** expert assertions into the machine-readable T0–T7 schema without breaking schema validation rules.

```
                  ┌──────────────────────────────────────────────┐
                  │          EXPERT ELICITATION STAGE            │
                  │  Query: Suitability · Vulnerability · M5/M6   │
                  └──────────────────────┬───────────────────────┘
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │            CONTEXT & SCALE FILTER            │
                  │  Identify scale limits and context-drivers  │
                  └──────────────────────┬───────────────────────┘
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │          SCHEMA TRANSLATION STAGE            │
                  │  Structure to EV: evidence_type = expert     │
                  └──────────────────────────────────────────────┘
```

---

## 2. Elicitation Guidelines & Question Templates

Interviews should be semi-structured but target these specific axes to align with the framework's primitives:

### 2.1 Separating Species-Specific vs. Practice-Technology Envelope
Experts frequently cite biophysical limits (e.g., rainfall, temperature) based on a single crop or tree species they are familiar with. We must isolate practice-level constraints.
* **Core Question:** *"You mentioned a minimum rainfall of 1,200 mm. Is that a requirement for the practice/technology to function (e.g., to prevent erosion on contour strips), or is it specific to a particular tree/crop species (e.g., a specific cocoa variety)?"*
* **Translation:** 
  * If **species-specific**, tag `claim_scope = "species_specific"` (or `"crop_specific"`) and populate `taxon`. These must **not** set practice-level T4 envelopes.
  * If **practice-specific**, tag `claim_scope = "practice_technology"`. These populate the core T4 row.

### 2.2 Disaster Vulnerability, Establishment Windows & Economic Archetypes (M2b / T0)
Disaster screening (M2b) needs to understand when the NbS asset is most vulnerable and how that affects the economic viability of the investment.
* **Core Questions:** 
  * *"How many years does this practice take to establish (reach maturity or soil-binding capacity)?"*
  * *"During this establishment window, what climate hazards (drought, flood, fire) could destroy the investment?"*
  * *"How does this early vulnerability impact the economic archetype (e.g., does it create high upfront risk with delayed returns)?"*
* **Translation:** 
  * Establishes `T0.establishment_period_years`.
  * Dictates risk weights in `T3` (`asset_risk_weight`) for Stream A exposure screening.
  * Informs the economic value ranges in `T6` (`economic_value_range`).

### 2.3 Livelihood Risks, Response, & Maladaptation (M2 / M5 / T6)
We need to capture not just where the NbS works, but also where it fails or makes things worse.
* **Core Questions:** 
  * *"Under what circumstances could this solution lead to unintended negative consequences (maladaptation) for local livelihoods?"*
  * *"How does the solution's effectiveness change under severe climate stress (e.g., does it continue to provide soil moisture during a multi-month drought)?"*
* **Translation:** 
  * Feeds `T3` hazard mitigation rows.
  * Populates `T6` scorecard effects and conditionality notes (mapping where benefits drop or turn negative).

### 2.4 Scale Limits & Grid Resolution Limits
Experts understand at what scale physical parameters matter.
* **Core Question:** *"At what geographic scale does this constraint lose its meaning? (e.g., can we evaluate slope suitability using a 10km grid, or do we lose the micro-topographical signals needed for infiltration pits?)"*
* **Translation:** 
  * Sets `VONT.min_meaningful_resolution_m` (e.g., 90m for slope, 1km for rainfall).
  * Informs the resolution audit warnings in M0/M1.

---

## 3. Capturing Context-Specificity & Next Steps

When experts state that a relationship "depends on the context," the interviewer must drill down on the drivers of that dependency.

### 3.1 Identifying Context Drivers
Ask: *"What specific factors drive that variation? Is it soil texture, agro-ecological zone (AEZ), farm size, or land tenure?"*
* **If driven by geographic context (AEZ, farming system, admin unit):** 
  * Translate to a **context override** in `T4.context_overrides` using the standard T7 IDs.
* **If driven by data availability or local knowledge:**
  * Translate to a **dataset override** in `BIND` (e.g., flagging that a local custom map `requires_upload` to replace the global default in that country).

### 3.2 Capturing Adoption Barriers for Next Steps (M6)
Adoption barriers (labor constraints, gender inequalities in tenure, credit access) are not hard biophysical exclusions, but they are vital for project implementation.
* **Core Question:** *"What are the most common reasons farmers stop practicing this solution after a project ends? What enabling environment (credit, extension, tenure) is missing?"*
* **Translation:** 
  * Feeds the soft operational risk levers in M2b (Stream B).
  * Directs the implementation guidance, tool references (e.g., CBA, InVEST), and safeguard flags (ESS7/FPIC) in the **Next Steps (M6)** module.

---

## 4. Translating Expert Claims to the Schema

Expert assertions must be formatted to fit the existing [Evidence Register (EV)](file:///Users/pstewarda/Documents/rprojects/nbs_ruralscan/schema/registers/EV_evidence_register.json) structure without exception.

### 4.1 Schema Mapping Rules
For every expert assertion, compile an EV row:

| EV Field | Mapping Rule for Expert Opinion | Example |
|---|---|---|
| `evidence_id` | `exp__<expert_initials>__<variable>__<date>` | `exp__nj__slope__20260609` |
| `source_id` | Key to a source register entry representing the interview/consultation. | `source_expert_interview_2026` |
| `evidence_type` | Must be **`expert`**. | `expert` |
| `claim_basis` | Must be **`expert_assertion`**. | `expert_assertion` |
| `quote` | Verbatim transcription of the expert's statement (provenance). | `"Slope exceeding 20 degrees is too steep for manual terracing without heavy machinery, leading to high labor dis-adoption."` |
| `page` | Set to `1` (or corresponding transcript line/section number). | `1` |
| `relationship` | Parsed relationship parameters (if numeric thresholds were given). | `{"abs_max": 20.0, "unit": "degrees"}` |
| `context` | Geographic or systemic context (AEZ, farming system). | `{"aez": "humid_tropics", "farming_system": "cropping_rainfed"}` |

### 4.2 Source Register Entry
The interview transcript or focus group metadata must have an entry in the **Source Register (SRC)**:
* `source_id`: `source_expert_interview_2026`
* `citation`: *"Expert consultation on Agroforestry suitability and risk, Nairobi, June 2026"*
* `benchmark_tier`: Typically **`medium`** (expert opinion is structured below peer-reviewed empirical data, but above unreferenced grey literature).
* `method_type`: **`expert_elicitation`**
