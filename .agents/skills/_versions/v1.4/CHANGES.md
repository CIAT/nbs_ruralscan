# Ruleset v1.4 — 2026-07-20

Snapshot of the extract-evidence skill + command in force from v1.4. Pin: `SRCH.ruleset_version` / `EV.ruleset_version = v1.4`.

## Change vs v1.3

**Catalogue #17 — relationship shape params must use CANONICAL keys.**
The T4 synthesiser (`recipe.synthesis`) reads threshold params only under the canonical keys
`abs_min` · `opt_low` · `opt_high` · `abs_max` (+ `unit`). Free-form keys (`range_min`,
`abs_min_mm`, `precip_mm_low`, `optimum_low_mm`, `sahelian_zone_min`, `low_density_per_ha`…)
are **silently invisible** to synthesis — a variable with a real, multi-source range emits
**0 T4 rows**.

Surfaced by #114: F2 (regeneration_farmland) synthesis returned 0 rows even though 7 sources
agreed a Sahel rainfall envelope (~100–950 mm; reconciled 251 / 400–800 / 800). Every range
was encoded under a free-form key.

Rule:
- A range/optimum → `{"abs_min":…, "opt_low":…, "opt_high":…, "abs_max":…, "unit":"…"}`.
- A single floor/ceiling → just that bound.
- A categorical class is NOT a shape param — leave it descriptive.

Safety net (not a substitute): `recipe.synthesis.normalize_shape_keys` maps the recurring
numeric-range aliases → canonical at read time (explicit + conservative; no bare `min`/`max`).
The F2 register data was also normalized in place (lossless — values/quotes unchanged, alias
key renamed; `check_numbers` still passes).

## Trigger

#114 F2 T4 synthesis returning empty despite real range consensus — the free-form
relationship keys from the 2026-07 FMNR sweep were unreadable by the synthesiser.
