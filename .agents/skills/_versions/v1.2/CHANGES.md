# v1.2 (2026-07-14) — extract-evidence defect-catalogue additions (2026-07 sweep-retro)

New/changed extraction rules + deterministic guards from the 2026-07 QA retrospective
(triage of 165 unincorporated review decisions):

1. **#15 Species/crop-specific evidence → TAG + KEEP, never drop.** A per-taxon claim is
   *routed*, not deleted: set `claim_scope=species_specific|crop_specific` + `taxon`;
   `synthesis.py` filters it from the practice-level T4 surface but RETAINS it in the register
   for a future species-level layer. The defect is the **mis-tag** — a species claim left as
   `claim_scope=practice_technology` (12 of 29 July `species_envelope` drops). New guard:
   **`check_species.py`** (quote or SRC citation names a taxon but `claim_scope=practice_technology`).
2. **#13 `unusable_value`** (renamed from `uninterpretable_weight`) — broadened to cover a
   weight/score with no scale ("5 out of what?") **OR** land cover with no class list (which
   classes in/out). New `check_scope.py` signal **`land_cover_no_classes`**.
3. **`check_scope.py` `land_capability`** signal — AOI-constraining land-capability /
   land-use-capacity / residual-("marginal land") classifications (`constrained_aoi`, #14) are
   now deterministically flagged (regression guard).
4. **Reason-code cleanup** — merged `cross_row_stitch` → `table_error`; per-card **drop** now
   requires a coded reason (was reason-less → blank-reason drops).

Deterministic guards now: `validate_sources · check_numbers · check_scope · check_quote ·
check_picos · check_species · quarantine` + the adversarial relationship-verify.

Trigger: 2026-07 sweep-retro. Dominant new signals — `species_envelope` (29),
`constrained_aoi`/INAB residual-land (32), land_cover-no-classes (~10).
