# Forest restoration: does evidence about *existing* forest count as evidence for *restoring* forest?

2026-10-06 · for Pete Steward · one decision, five minutes

## What is at stake

The forest-restoration tables pool two kinds of study. Some measure what a restoration practice did (planting, assisted or natural regeneration, mangrove restoration, community forestry). Others measure what existing forest does or what its loss costs: children's diets near forest in Africa (Rasolofoson 2018), flood protection by the world's existing mangroves (Menéndez 2020, Gijsman 2021, McIvor 2012), local cooling after observed forest-cover gain (Prevedello 2019), and erosion or flood contrasts between forested and cleared land. The second kind is currently filed under the **protection / community-forestry family** or the cross-family tag, with a note saying what it is.

The PICOS rule says the practice must be evidenced in the source. Protecting forest keeps existing forest standing, so "what existing forest does" is arguably exactly the effect of protection. But it is not evidence that planting or regenerating forest will deliver the same service within a project horizon, and a reader of the roll-up row cannot tell the difference.

## Example

The forest-restoration flood roll-up reads **moderate, very high confidence** on 20 sources. Its strongest units are existing-mangrove protection models and forest-loss contrasts. The restoration-practice units in the same cell are weaker and fewer. The cyclone cell reads **very high** almost entirely on existing-mangrove evidence.

## Options

- **A — Keep, as protection-family evidence with a transfer note (current state).** Honest for the protection / community-forestry family; over-states the roll-up for planting and regeneration families. Nothing to change.
- **B — Keep, but out of the roll-up (recommended).** Existing-forest studies stay in the protection family rows (where they belong) and are excluded from the NbS roll-up and from the planting / regeneration families. Implementation: a `comparator = existing_forest` tag on the unit, which the engine keeps out of roll-up pooling. Half a day; re-synthesis; prose refresh on the affected rows.
- **C — Demote to forest-cover evidence only.** Re-tag these units to `landscape_forest_cover` (no practice). They leave every scored cell and inform only the opportunity-space context. Cleanest reading of PICOS, but it throws away the only quantified flood and cyclone evidence the mangrove family has.

## Recommendation

**B.** It keeps the evidence where it is defensible (protection keeps the forest that does these things), stops it from colouring the planting and regeneration rows, and the roll-up then reads what restoration practices have measurably delivered. Reply "PICOS B" (or A / C).

Technical record: `methodology/effect_evidence_followups.md` §1f; the affected units are listed in the FR lane C / D reports.

## Decision (Pete, 2026-10-07): B — applied

37 forest-restoration units now carry `comparator = existing_forest` (Rasolofoson 2018 diets near forest; McIvor 2012 storm-surge and wave attenuation by mangroves; Gijsman 2021; Menéndez 2020 "if current mangroves were lost"; the World Bank Bangladesh mangrove design study; Prevedello 2019 warming after deforestation; IUFRO 2018 flood risk after forest conversion / harvest and the forest-vs-non-forest water balance; Forbes & Broadhead 2011 landslides after clearance). They stay in the register and in the protection / community-forestry and mangrove family rows, and are out of every NbS roll-up row and every planting / regeneration row (`schema/lookups/comparator_policy.csv`; ruleset v1.6.4 addendum).

**What moved.** Protection-family flood: high → moderate (the strongest existing-mangrove units now sit in the mangrove family row instead). A cross-family soil-erosion row that rested on forest-loss landslide studies no longer exists; the landslide evidence now reads under protection. The roll-up flood, cyclone, erosion, heat-stress, water-stress and poverty rows were re-pooled from restoration-practice evidence only and their prose rewritten (21 rows). Planted-mangrove wind measurements (McIvor's Sonneratia plantation) are practice evidence and were NOT tagged.

