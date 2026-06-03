# M0 — Setup & Scope

**Module spec sheet · v0.1 draft · June 2026**

| Field | Value |
|---|---|
| **ID** | M0 |
| **Module** | Setup & Scope |
| **Owner(s)** | Pete Steward (lead) · implemented in Python via Claude Code |
| **Status** | Draft — authored to match the v0.6 wireframe (Setup tab: Scope & climate + Variable config) |
| **Schema tables consumed** | T0 · T1 · T7 (+ T4/T5 for the variable-config surfaces) |
| **Schema tables produced** | run configuration (JSON, not a schema table) |
| **Position in pipeline** | **M0 (Setup)** → M1 · M2 · M2b · M3 · M4 · M5 |

> M0 is the front door. It captures the user's choices, validates that every required dataset is reachable, and emits the **run configuration** every downstream module consumes. Computed in **Python**; datasets pulled via the Earth Engine API or direct source — no native server-side GEE pipeline.

---

## 1. Purpose

For the TTL, M0 turns a set of choices — which NbS, where, at what resolution, under which climate lens — into a validated, reproducible **run configuration**. It also surfaces the recipe (variables + rules) behind those choices and runs the **ingestion check** (does every required dataset have access / hosting / upload status) before any analysis runs.

## 2. Question answered

> *"What are we scanning — which NbS, over what geography, at what detail, under which climate scenario and risk lens — and is everything needed to run it actually available?"*

What M0 explicitly **does not** do:

- Any analysis (M1–M5) — M0 only configures and validates.
- Author recipe content (Namita, via T0/T4/T5/T6) — M0 *reads* it.

## 3. Inputs

| Input | Source | Schema | Notes |
|---|---|---|---|
| NbS selection (one or more) | UI | `T0.nbs_id` | Each selected NbS gets its own opportunity space; subpractice variant per NbS |
| Geographic scope | UI | `T7` | Country/region + sub-national focus + admin level (neutral ADM codes — ADM0/1/2) |
| Resolution | UI | run config | 5 km (default, fast) · 1 km · 500 m |
| Climate risk mode | UI | run config | Mode A (H×E, default) · Mode B (H×E×V) |
| Scenarios to compare | UI | run config | `baseline` + one or more `future_*` (e.g. SSP2-4.5 / 2050) |
| Recipe + datasets | T0/T1/T4/T5 | schema rows | For the recipe summary + data-readiness check |

## 4. Outputs

| Output | Format | Path | Consumer |
|---|---|---|---|
| Run configuration | JSON | `…/run_config.json` | All downstream modules |
| Data-readiness report | JSON/CSV | `…/tables/data_readiness.csv` | Setup "Variables & recipe" readiness badges (GEE catalog / community / pending upload) |
| Resolution-audit seed | CSV | `…/tables/resolution_audit.csv` | Seeded here, appended by M1–M4 |
| Ingestion status | JSON | `…/ingestion_status.json` | Blocks the run if a required dataset is unreachable and not uploadable |

## 5. Dependencies

**Upstream:** none — M0 is the entry point.

**Downstream:** every analytical module reads `run_config.json`. M1/M3 read the variable lists; M2/M2b read the mode + scenarios; the wireframe Setup tab reads the recipe summary + readiness.

## 6. Sub-steps

1. **Scope capture** — record NbS (+ subpractice), AOI (T7), admin level (neutral ADM code), resolution, climate mode, scenarios.
2. **Recipe resolution** — for each NbS, resolve the recipe (T0 → T4 suitability vars, T5 priority vars) and compute the variable counts (e.g. 23 vars → ~16 after clustering).
3. **Data-readiness check** — for every required dataset (T1), report hosting status: GEE catalog / community-hosted / pending upload. Flag the resolution honesty (coarsest required input vs chosen resolution).
4. **Ingestion validation** — confirm each dataset is reachable (or has an upload path). Hard-block the run on any unreachable required dataset.
5. **Variable-config surfaces** — expose the two config surfaces (Suitability variables → M1/M4 recipe; Priority/hotspot variables → M3/M4) for inspection/editing. Technical-mode controls (cluster reps, response curves, weights) flagged for technical users.
6. **Emit run configuration** — write `run_config.json` (NbS, AOI, resolution, scenarios, mode, recipe + schema versions, dataset versions, date) for reproducibility.

## 7. Variable Cards consumed

All Variable Cards for the selected NbS (suitability T4 + priority T5) are surfaced read-only in the Setup → Variable config sub-tab, across the two surfaces. Editing them is a technical action (Technical mode).

## 8. Tests / acceptance criteria

- [ ] Emits a valid `run_config.json` capturing all choices + schema/dataset versions.
- [ ] Data-readiness report classifies every required dataset (catalog / community / upload).
- [ ] Run is blocked when a required dataset is unreachable and has no upload path.
- [ ] Neutral ADM terminology throughout (ADM0/1/2 + local name annotation); no hardcoded "district/county".
- [ ] Resolution-honesty flag fires when chosen resolution is finer than the coarsest required input.
- [ ] Reads recipe + datasets from schema; nothing hardcoded.

## 9. Definition of done

- [ ] T0/T1/T4/T5/T7 rows resolvable for the selected NbS + AOI
- [ ] Ingestion check passes (or upload paths confirmed)
- [ ] `run_config.json` consumed cleanly by M1 in an end-to-end agroforestry Sierra Leone run
- [ ] Setup tab renders recipe summary + readiness from the report

## 10. Implementation notes (Python)

```python
def capture_scope(ui_inputs) -> dict:
    """§6.1 — normalise NbS/AOI/resolution/mode/scenarios into a scope dict."""

def resolve_recipe(nbs_id, t0, t4, t5) -> dict:
    """§6.2 — variable lists + counts (raw, post-cluster) for the NbS."""

def check_data_readiness(t1_rows) -> "pd.DataFrame":
    """§6.3 — hosting status per dataset; resolution-honesty flags."""

def validate_ingestion(readiness) -> dict:
    """§6.4 — reachable? upload path? hard-block on failure."""

def emit_run_config(scope, recipe, versions) -> dict:
    """§6.6 — reproducible run configuration."""
```

## 11. Open questions

1. Multi-NbS runs — one `run_config` per NbS, or one config with an NbS list? (Wireframe implies several NbS in one session.)
2. Upload path for "pending upload" datasets — manual (user supplies a raster) vs a guided ingestion sub-pipeline.
3. ADM level default per country — ADM2 (current) vs let the recipe/AOI decide.

---

## Version history

- **v0.1** (June 2026) — authored to match the v0.6 wireframe Setup tab. Captures scope, recipe summary, data-readiness/ingestion, and the two variable-config surfaces; emits the run configuration. Computed in Python (post native-GEE).
