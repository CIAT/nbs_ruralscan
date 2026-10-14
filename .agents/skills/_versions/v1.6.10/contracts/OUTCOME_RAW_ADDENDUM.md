# v1.6.10 addendum — `relationship.outcome_raw` carries no number the quote does not

**Source:** the 2026-10-13 retrospective on the riparian + wetland effect round.
**Applies to:** every unit extracted under v1.6.10 or later. Earlier units stay valid.

## What went wrong

The round passed its own staging gate and the next build flagged 37 of its 159 units — 23%,
against a register average of 8% — for number provenance. Every one was a **study descriptor**
written into `relationship.outcome_raw`:

- "share of sediment trapped by a **7.1-m-wide** switchgrass buffer"
- "water-surface elevation for a steady-state **10%** annual exceedance flood"
- "peak flow under the base-case restoration (**1006 m**, **20%** of the domain, **15 cm** bank height)"
- "nitrate reductions may be much less than the **80-99%** reported for established buffers"

None was a smuggled magnitude. But the check cannot tell the difference, and that is the
problem: at a 23% flag rate a genuinely mis-stitched value is invisible.

## The rule

`relationship` is a **claim surface**: every number in it, anywhere in the dict, must appear in
the unit's quote. `outcome_raw` states WHAT was measured and against what, in words.

Study descriptors — treatment geometry, event return period, site dimensions, a comparator
figure taken from elsewhere in the paper — go in **`context.note`**, which is not a claim
surface. This is the same split as catalogue #22, which sent process metadata the same way.

**Number words count.** `check_numbers` reads "ten", "twice", "double" as numerals, so writing
the descriptor out in words does not satisfy the rule. Move it, do not reword it.

## Enforcement

`scripts/ingest-effects-staging.py` now runs `check_numbers._rel_nums` over the whole
relationship, the same surface the build walks, instead of only the six numeric fields. A lane
can no longer pass a file that the next build will flag.
