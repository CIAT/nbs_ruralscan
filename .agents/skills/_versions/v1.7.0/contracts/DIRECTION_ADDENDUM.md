# Direction addendum (ruleset v1.6.17, 2026-10-23)

Applies on top of `T3_T6_extraction_contract.md` §2.2 rule 1. Units stamped `ruleset_version = v1.6.17` or later.

## The rule (unchanged, restated)

`relationship.direction` is the movement of the **outcome variable as named**, as the quote states it.
It is never "good" or "bad".

| variable | quote | direction | why |
|---|---|---|---|
| `erosion_hazard` | "reduced erosion" | `negative` | erosion went down (a benefit) |
| `flood_hazard` | "downstream flooding was reduced" | `negative` | flooding went down |
| `project_cost` | "costs US$ 400/ha" | `positive` | a cost exists / is higher |
| `runoff_reduction` | "runoff fell 40%" | `positive` | the variable is NAMED as the reduction |
| `windbreak_protection` | "wind speed reduced behind the belt" | `positive` | more shelter |
| `crop_yield` | "yield fell under shade" | `negative` | yield went down (a harm) |

What `positive` and `negative` mean for every variable is in
`schema/lookups/variable_direction_sense.csv` (`positive_means`, `negative_means`, `high_is`). Read the row
for your variable before coding. A new effect variable needs a row there; the build fails without it.

## New required key: `relationship.direction_cue`

The shortest **verbatim** phrase from the quote that carries the direction ("reduced erosion",
"yields were 30% higher", "no significant difference"). Slice it from the quote; never retype it.

- Required on every unit with a `direction` (`positive`, `negative` or `none`).
- `check_direction.py` flags a cue that is not in the quote (`cue_not_verbatim`), a missing cue
  (`missing_cue`), and a cue whose only movement word points the other way from the coded direction on a
  plainly-named quantity (`cue_word_conflict`, e.g. cue "reduced erosion" with `direction = positive` on
  `erosion_hazard`).
- Loss-framed units (`framing = loss`): the cue describes the loss ("if mangroves were lost, 28% more
  people"); code the direction as measured and let the engine flip it.

## Self-check before emitting (say it in words)

Write, for yourself: "<variable> went <up/down/no change> according to '<cue>'". Then map up → `positive`,
down → `negative`. If you find yourself thinking "this is good, so positive", stop: that is defect E8.
