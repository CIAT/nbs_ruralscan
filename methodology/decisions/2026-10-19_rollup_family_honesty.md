# Does the NbS-level row get to disagree with its own families?

**For:** Pete. **Raised:** 2026-10-19 (flagged when the Baker meta-analysis flipped two
agroforestry family rows to conflicting evidence; twinned then with the plantation question,
which you answered — this is the general half). **Also in here:** draft rules for your three
hold cards from tonight's review batch, each needing a yes/no/reword from you.

---

## 1. The roll-up honesty question (the main decision)

### What happens today

The NbS-level row pools **every unit from every family** into one big vote. The family rows
pool only their own units. Nothing connects the two — so a big agreeable pool at NbS level
can swamp conflicts that are plainly visible one line down.

### The live example (agroforestry, production gap)

| row | class | units |
|---|---|---|
| **agroforestry (NbS level)** | **strong_positive** | 121 |
| regeneration_farmland | strong_positive | 27 |
| cross_family | strong_positive | 19 |
| shaded_perennial | slight_positive | 3 |
| planted_silvoarable | **conflicting_evidence** | 33 |
| silvopastoral | **conflicting_evidence** | 24 |
| linear_boundary | **conflicting_evidence** | 15 |

Three of six families — carrying **72 of the 121 units** — read conflicting. The NbS row
reads *"agroforestry strongly closes the production gap, high confidence"*. It isn't lying
(the pooled majority is positive), but a TTL who never opens the family rows walks away with
a cleaner story than the evidence tells. This is the same instinct as your conflicting-
evidence ruling: positive and negative votes balancing must not read as a clean average —
here they must not read as a clean majority either, when the disagreement is structured by
sub-practice.

### Options

- **A — leave it.** The NbS row is an honest pooled vote; family rows carry the nuance; the
  scorecard UI shows both. Risk: the headline is what gets read.
- **B — the NbS class defers to its families.** When families whose rows carry at least a
  third of the evidence weight read conflicting (or oppose the pooled sign), the NbS row
  states **conflicting_evidence** too, and its narrative says *which families* gain and which
  conflict ("strong in regeneration-based systems; conflicting in silvoarable, silvopastoral
  and boundary planting"). Same 1/3 threshold as the unit-level conflict rule, applied one
  level up. The pooled class is still computed and reported inside the account.
- **C — keep the pooled class, stamp it.** The NbS row keeps strong_positive but carries a
  mandatory `families_divided` flag + a statement sentence naming the conflicted families.
  Cheapest; the headline class still reads clean.

### Recommendation

**B.** Your own words on conflicts: "there is a difference if we have positive and negative
votes making a neutral average vs neutral votes making a neutral average" — the same applies
to a positive headline built over divided families. B reuses the ratified 1/3 threshold, so
there's one conflict philosophy in the engine, not two. C is the fallback if you want the
headline class preserved for MCDA reasons.

**Answered (Pete, 2026-10-19):** "suggest the roll-up is not at the row level but the
sub-oractice level, with some weighting for units (but not simply n, maybe root n or log n or
someting?) - so B-ish."

**Implemented:** the NbS-level class is derived from a vote of the family rows, each weighted
sqrt(n_sources) (sources are the engine's independence currency; root-n is the damping Pete
asked for). Conflicting families plus the minority sign at >= 1/3 of the signed weight make
the roll-up state conflicting evidence — the same threshold as the unit-level rule, one
conflict philosophy at both levels. Guards: at least two classed family rows covering at least
half the roll-up's sources, otherwise the pooled class stands and the account says why. The
vote, its weights and the pooled class it replaced are recorded in every row's
`justification.family_vote`. 18 roll-up rows re-classed (4 to conflicting evidence —
agroforestry production and wind, water-harvesting waterlogging, forest-restoration fire;
most others tempered one step; two strengthened where the families agree on more than the
pool said). The first run weighted votes by each family's whole register slice — the WH
prose writer caught it ("in_situ = 38 sources where the flood cell held 7 units"); weights
now come from the family's row in the cell.

---

## 2. Hold card: santos25_8 — "what is the traditional system?"

The Brazilian soil-carbon quote gives stocks for four systems: natural vegetation 134.65,
silvopastoral 97.59, agrosilvopastoral 71.64, "sistema tradicional" 68.16 Mg/ha. The unit
votes positive (97.59 vs 68.16) — but the paper never says what the traditional system is,
and against the natural-vegetation baseline the silvopasture is a large LOSS.

**Draft rule:** a contrast against an **unnamed comparator** ("traditional", "conventional",
"typical practice" with no description) may vote on direction but its strength is capped at
moderate, and `practice_as_described` must carry the comparator's own words when the paper
gives any. Where the same quote offers a *named* baseline (here: natural vegetation), the
reviewer checks the sign against the counterfactual that matters for the cell.

**How to answer:** "santos: cap / leave / drop".

## 3. Hold card: batcheler24_6 — "turn the judgement down a notch"

Your note: grazing may reduce litter build-up, but a silvopasture still carries more
flammable material than the treeless comparator system. The cell currently pools six fuel
and fire units without asking *which comparator* each one votes against.

**Draft rule:** in hazard cells, a fuel/mechanism unit's sign is read **against the cell's
farming-system comparator** (for agro-pastoral: open pasture), not against an unmanaged
woodland. Units whose comparator is the unmanaged state (grazed vs ungrazed forest) inform
the account but don't set the class. This is a comparator question, not a weighting knob —
classes stay derived, nothing is hand-notched.

**How to answer:** "fire: rule / leave".

## 4. Hold card: ojan20_4 — net emissions unclear

No new rule needed, I think: your 16-Oct gas ruling already governs the class (net CO2e
decides; a single-gas unit never sets a carbon class), and this unit IS a net statement —
methane offsets "a major part" of the cooling in the first decades, which is exactly the
decadal-warming / century-cooling story the wetland carbon row now tells. It stays a voter.

**How to answer:** "ojan: ok" (or "drop" if you want it out).
