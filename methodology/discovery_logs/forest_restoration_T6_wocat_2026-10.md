# Discovery log — Forest Restoration · all families · T6 · WOCAT sheets via the adapter (2026-10-06)

- Run `fr_wocat_adapter_2026-10-06` · ruleset v1.6.2 · by orchestrator
- **Source set:** the 23 WOCAT entries already in SRC for `forest_restoration` (T4 sweep); no new search — a structured re-read through `ingest/wocat.py` (questionnaire JSON → `.md` transcript → rule-based units).
- **Counts:** 23 → 23 screened → 23 with rated fields → 269 units (234 `nbs_effect` · 30 `asset_vulnerability` · 5 `operational_risk`), families from each sheet's T4 family (active_planting 80 · passive_regeneration 76 · protection_cbfm 45 · assisted_regeneration 42 · mangrove_coastal 26).
- **Rules applied:** impact ratings (QT 6.1/6.2) with carbon / biodiversity / emissions needing a compiler comment; QT 6.3 coping → asset vulnerability (drought / heatwave excluded as delivery shortfall, Pete D3); QT 4 costs only with a stated calculation base; long-term cost-benefit ratings only.
