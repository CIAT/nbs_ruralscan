---
description: Generate an NbS recipe's T3 (hazard) and T6 (scorecard) tables by cell synthesis over pooled effect-claim evidence (T3/T6 method section 7)
---

Run T3/T6 cell synthesis for one NbS (methodology/T3_T6_generation_method.md sections 2, 5, 7, 8;
engine contract `.agents/skills/_versions/v1.6.0/contracts/T3_T6_synthesis_contract.md`). Ask for
the `nbs_id` if missing. Evidence must already be in the register (`use_role = nbs_effect` /
`asset_vulnerability`, ruleset v1.6.0) — run the effect-claim extraction (contract
`T3_T6_extraction_contract.md`) and the central gates first.

Workflow:
1. Gates on the pooled units BEFORE synthesising: `validate_sources` (verbatim), `check_numbers`,
   `check_context`, `check_bands`, `check_xw`. Anything flagged is fixed at the unit, never in the row.
2. Run the engine (never re-judge a class by hand):
     python3 scripts/synthesise-t3t6.py <nbs_id> --dry-run     # preview table
     python3 scripts/synthesise-t3t6.py <nbs_id>               # writes the recipe CSVs + report
     python3 src/nbs_ruralscan/schema_tools/generate.py schema  # regenerate JSON
     python3 -m nbs_ruralscan.schema_tools.check_account schema/recipes/<nbs_id>/T6_nbs_scorecard.json
   The script reads tiers / categories / study context from SRC, routes from XW, income groups and
   the IPCC matrix from `schema/lookups/`; it pools every effect unit of the NbS and emits, per cell,
   a global row + scope rows + family rows (+ the NbS roll-up with `family_spread`).
3. Report (paste the script's summary table): per row the class, `evidence_level × agreement_level →
   confidence`, `n_sources`, `transfer_class`, `strength_basis`; then the run report — unmapped
   variables (catalogued, feed no cell — a T5/XW decision, not an extraction defect), excluded
   economics with their failed gate, incomplete asset-weight sets, dropped/collapsed units.
4. Acceptance (method section 14): every row's `evidence_ids` resolve to live units; a re-run is
   byte-identical; global rows built only from out-of-context evidence carry
   `transfer_class = out_of_context` (the consumer shows a gap, not the class).

Rules: the class, levels and confidence are engine outputs — fix the evidence unit and re-run;
`no_relationship` only from real nulls; economics only under the section 7.7 gates (HIC never in an
LMIC/global row); prose (`mechanism`, `conditionality`, `caveats`) stays empty until the gated
prose writer runs — the traceable account carries the evidence summary meanwhile. Frozen seed rows
(agroforestry, water harvesting) are a benchmark: never overwrite them with generated rows
without recording the comparison (method section 14).
