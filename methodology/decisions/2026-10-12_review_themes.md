# What your review of the 8 October batch tells us — and what I propose doing

**From:** the orchestrator. **For:** Pete (and Namita for the QA items).
**Input:** all 48 units reviewed — 13 approved, 9 rejected, 26 held with notes (`docs/review/exports/review_recovered_2026-10-08_Peter_2026-10-12.csv`, applied to the register).

Your notes repeat seven patterns. Each one below says what you found, what it costs us, and what I would do. The ones marked **decide** need your call before I build.

## 1. Bundles are being credited to one practice — **decide**

You flagged it five times: conservation agriculture (Steward, Knapp, Mazvimavi, Boillat) and the Indian farm pond "+ crop + tree + livestock" (Palsaniya). Your words: *"If a bundle contains more than 1 NbS it must be mapped as such"* and *"what is the water harvesting component in the bundle?"*

Today an evidence unit names one NbS and one family. A bundled intervention therefore credits the whole effect to whichever NbS the lane picked, and conservation agriculture is the worst case: in Boillat's Malawi table fewer than half the farmers used ridging or planting basins at all.

Options:
- **A.** Add a `bundle_components` field (list of practices named in the source) plus `attribution = isolated | bundled`. Bundled units keep their evidence but are weighted down and never set a class alone. Mechanical, honest, ~half a day.
- **B.** As A, and additionally require that a bundled unit be emitted once per NbS it contains, so the same finding appears under each practice with a note.
- **C.** Treat conservation agriculture as its own NbS rather than a water-harvesting sub-practice, and stop borrowing its evidence.

My recommendation is **A**, with **C** raised separately: much of the water-harvesting drought evidence is really conservation agriculture.

## 2. The practice must be the NbS — not something next to it

Rejections and holds of the same kind: supplemental irrigation counted as water harvesting (*"BAD ERROR"*), plantations counted as forest restoration (Bradshaw), protected areas counted as restoration (Naidoo, Robertson, Snilstveit), a farm pond used for irrigation (*"is water harvesting + irrigation still the NbS?"*).

You also asked for the fix directly: *"it would be good if the extract could capture the description of the NbS in question from the evidence."* I will add a required `practice_as_described` field — the source's own words for what was done — so the practice test is visible on the review page instead of being inferred. No decision needed; I will do it.

## 3. Hazard-year gains need a normal-year comparator — **decide**

*"Is the same absolute gain also seen in normal years and therefore this is just a production benefit?"* (Mazvimavi). This is the difference between resilience and ordinary yield gain, and we currently cannot tell them apart: a drought-year contrast with no normal-year reference is read as hazard mitigation.

Options: **A** record a `normal_year_reference` (present / absent / value) and down-weight hazard units without one; **B** exclude hazard-year units that have no normal-year comparison. I recommend **A** — **B** would empty several cells.

## 4. Strength bands are invisible to the reviewer

*"5% to 2.2% loss — what is the logic by which you have inferred this is a large amount? is there a rule?"* There is: `schema/registers/BANDS_magnitude_bands.csv` maps a metric and unit to slight / moderate / strong. The page never showed it. I will print the band rule applied to each unit ("response ratio 0.44 → strong, band: |r−1| ≥ 0.30"). No decision needed.

## 5. Several units, one paper

Twice flagged (Bayala, Adimassu): *"multiple data points from same paper will require dealing with when compiling the evidence."* The engine does weight by source rather than by unit, but the page does not say so. I will show "this cell draws on N units from M sources" on every row, and the same line in the generated tables' account.

## 6. Second-hand citations

Montagnini reporting other people's milk figures: *"use the publications referenced not a secondary interpretation."* Agreed. Cited-secondary units already carry a lower weight; I will also log the primary reference as a discovery candidate so we can replace them rather than keep a second-hand reading.

## 7. Economic value — to whom? — **decide**

Mangrove protection value mapped to rural poverty (Das, Marois): *"economic value to whom? we are primarily interested in direct beneficiaries of the WB investment, societal benefits are good too, but should be kept separate"*, and *"is protection to houses a rural poverty indicator? surely this maps more to hazard reduction."*

Options: **A** add a `beneficiary = farm_household | community | society` tag and keep societal values out of the poverty priority (they stay visible, in their own line); **B** re-route avoided-damage values to the flood-hazard priority instead of poverty; **C** both. I recommend **C**.

## Also noted
- One quote was the whole of a table (*"the coded field contains a huge amount of text"*). I will add a quote-width check: a quote must be the row plus its header, not the table.
- Forest-restoration units should state the restoration type; I will add it to the practice description in item 2.
- T4: the three suitability units are out of the queue and opportunistic T4 extraction is paused. **Medland 2020 (Ontario wetland suitability) looks highly relevant to the T4 analysis** — flagged for Namita to include there.

## To answer
Reply with the numbers: e.g. "1A, 3A, 7C". Items 2, 4, 5, 6 and the quote-width check need no decision; I will build them next.
