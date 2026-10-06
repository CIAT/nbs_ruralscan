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
