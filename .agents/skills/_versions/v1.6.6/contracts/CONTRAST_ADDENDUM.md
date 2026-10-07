# v1.6.2 addendum — contrast metrics (2026-10-06)

Applies on top of `T3_T6_extraction_contract.md` §4 (strength_class / BANDS). Units stamped `ruleset_version = v1.6.2`.

| metric | relationship fields | strength_class | when |
|---|---|---|---|
| `contrast` | `value_with` (with the practice / after), `value_without` (without / before) — BOTH verbatim in the quote; `direction` as usual; `unit` names the quantity (kg_per_ha, t_per_ha_yr …) | DERIVED: ratio `value_with / value_without` on the `response_ratio` bands (centre 1: \|r−1\| < 0.10 slight · < 0.30 moderate · else strong); `value_without = 0` → strong | the quote states both arms of a comparison as numbers ("0 kg/ha without zaï vs 300–400 with it", "54 → 2.6 t/ha/yr") |
| `complete_contrast` | no numbers; `direction` | `strong` by definition | the quote states an all-or-nothing outcome ("only fields treated with tassa produced a harvest"); "no millet gain in the driest year" is NOT this — that is `direction = none` |
| `absolute` + `unit = fold_change` | `magnitude` (or `magnitude_low` / `magnitude_high`) = the stated multiplier | BANDS `fold_change` rows (centre 1) | "two to three times", "divided by 150", "doubled" — spelled-out multipliers count as number provenance |

Never set a `contrast` class by adjective; `check_bands` recomputes it and flags any mismatch. Vote counts, perception shares and "cited n times" remain `unspecified`.
