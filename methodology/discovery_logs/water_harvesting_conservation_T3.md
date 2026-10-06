
## Grey — WOCAT technology sheets via the adapter (2026-10-06, run `wh_wocat_adapter_2026-10-06`, ruleset v1.6.2)

- **Source set:** the 52 WOCAT entries already in SRC for `water_harvesting_conservation` (T4 sweep `round2_grey_wocat_2026-09`); `wocat_wh_guidelines_2013` is a manual, not a sheet → excluded (52 → 51 screened → 50 with rated fields).
- **Method:** no search — a structured re-read. `python -m nbs_ruralscan.ingest.wocat acquire` cached the embedded questionnaire JSON + a deterministic `.md` transcript per sheet; `emit` produced rule-based units from `schema/lookups/wocat_impact_map.csv` (QT 6.1/6.2 impact ratings → `nbs_effect`, `ordinal_rating` / `wocat_impact`) and `wocat_hazard_map.csv` (QT 6.3 disaster coping → `asset_vulnerability`). No LLM, no inference from compiler comments.
- **Counts:** 690 units (538 effect · 126 asset-vulnerability · 26 operational-risk) through the staging gate with `--allow-operational`; family = each sheet's T4 family; all under `water_harvesting_conservation` (FAM-resolved).
- **Caveat:** practitioner ratings carry `claim_basis = expert_assertion` → they never raise `evidence_level` above `limited` on their own (`_LOW_BASIS`) and take the grey discount; they do add to agreement and to the asset-threat hazard coverage (now 7 + 2 asset-only hazards).
