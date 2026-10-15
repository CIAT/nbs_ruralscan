# Four rows are telling a World Bank reader the opposite of what the evidence says

**For:** Pete. **From:** the orchestrator, 2026-10-15. **Needs:** three decisions (A, B, C below).
**Context:** the wetland effect round just took the tables from 27 rows on 75 evidence units to
75 rows on 341. Most of it works. These are the parts that do not.

## The problem in one example

One row now reads: *wetland restoration moderately DECREASES carbon sequestration.*

Ten units give it that negative sign. I checked every one:

| what the unit actually measures | count |
|---|---|
| methane or nitrous oxide rising, where the same sentence's carbon dioxide fall is a separate unit | 4 |
| a restored wetland still below an INTACT wetland, years later | 5 |
| anything that says rewetting releases more carbon than leaving peat drained | 0 |

Not one source in that pool concludes what the row says. The same two artefacts produce a
biodiversity row reading *moderately decreases biodiversity*, where again no unit says it.

A Task Team Leader comparing NbS options sees the class. The caveats are already written and they
are honest, but a wrong-signed class with correct prose underneath is still a wrong answer.

## Decision A — do we record which gas a number refers to?

We have no variable for an individual greenhouse gas. Rewetting peat lowers carbon dioxide and
raises methane; that is the finding, not a complication. Both halves currently land in one pool as
opposite signs, so a literature that agrees is read by the engine as internal disagreement, and
the "measured harm in 13 sources" clause on the global carbon row is largely counting methane
halves of sentences whose carbon halves sit beside them.

- **A1. Add a `gas` tag to the evidence** (`co2`, `ch4`, `n2o`, `net`). Cheap, no schema reshape.
  The engine can then group by gas before taking a sign, and prefer a net balance where a source
  gives one. **My recommendation.**
- **A2. Separate variables per gas**, routed to carbon with an inversion. Cleaner in principle,
  more plumbing, and it splits cells that are already thin.
- **A3. Leave it.** The classes stay contradictory and we rely on prose.

## Decision B — is "not yet as good as an intact wetland" a harm?

Several syntheses measure restored wetlands against intact reference wetlands and find them short:
biological structure about a quarter below, soil carbon about half, decades on. That is a real and
important finding. It is not evidence that restoring harms anything, but the engine counts it as a
negative, and in two rows those shortfalls outvote the gains measured against the degraded
baseline that restoration actually starts from.

- **B1. New comparator value `reference_wetland`**, kept out of the sign vote and reported as a
  recovery note instead, exactly as `existing_forest` is handled today. **My recommendation.**
- **B2. Keep them in the vote** and accept that incomplete recovery reads as harm.
- **B3. Drop them.** Worst option: it deletes the strongest finding in the recovery literature.

B1 alone fixes both the carbon row above and the biodiversity row.

## Decision C — can a benefit to society set a poverty class?

The wetland poverty row reads moderately positive. Underneath it: income people already earn from
wetlands drained decades ago, benefit-cost ratios whose beneficiary is society, and asserted
statements. **The only matched-counterfactual study of an actual restoration found household
income LOWER for participants**, with the only significant gain in transfer income, which is
compensation rather than production. The two scope rows that contain that study both read
moderately negative, so the table currently contradicts itself by geography.

- **C1. A poverty class may only be set by units whose beneficiary is the household**; society-level
  value is reported alongside, not summed into it. **My recommendation.**
- **C2. Weight society-level evidence down but keep it in.**
- **C3. Leave as is.**

Worth knowing while you decide: a coastal economics review in this round warns that valuing
protection by avoided damage values it by the income of the community protected, which it says has
"created a justification to over-invest in marshes in high-income areas and underinvest in
middle-low-income areas". That is an argument against C3 in our specific setting.

## What I will fix without a decision, once you have ruled

Plumbing, no methodology in it: a wetland entry in the crop-scope policy so paludiculture crop
evidence reaches its own cells (the same call you made for water harvesting); a coastal home
family in the comparator policy so coastal evidence stops landing in the rewetting row; a route
from water regulation to the flood cell; a cross-family id for wetland, which is the only NbS
without one; and renaming the cost rows that are labelled "cost reduction" but contain only cost
increases.

Still missing as ontology, flagged but not invented: peat subsidence rate, wave attenuation,
establishment survival, and a home for distributional equity. The first is the primary measured
outcome of our best tropical evidence, so it contributes nothing today.

## How to answer

Three letters, for example "A1 B1 C1". If you want the fuller argument on any of them the row
names and unit counts are in the pull request.
