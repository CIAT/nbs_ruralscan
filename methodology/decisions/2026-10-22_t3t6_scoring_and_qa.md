# Before we move on: QA, how T3/T6 are generated, and how scores reach the dashboard

**For:** Pete. **Date:** 2026-10-22. **What you asked:** finish the human QA/QC on the agroforestry
evidence, evaluate how T6 and T3 are generated from it, and work out how variables nest into a
hierarchy and how evidence combines into indicator scores the dashboard can show.

**How to answer:** every decision at the bottom takes one letter. The full working is in
`2026-10-22_evidence/` (the generation evaluation, the hierarchy and scoring study, and the list of
high-leverage units).

---

## The short version

1. **Almost none of the agroforestry effect evidence has had a human look.** Of 589 effect units,
   9 are reviewer-approved (T4 is at 80%, because Codex has been reviewing it). Reviewing all 589 is
   not realistic. A risk-based sample is: the evaluation found **167 units that, on their own,
   change a class or delete a row**. That is where human eyes pay off.
2. **The generator works, but three bugs make some AF rows wrong today.** All three are
   implementation errors against rules you have already ratified, so none of them needs a new decision:
   - **Ratified crop-scope rulings are ignored in T3/T6.** The script reads only NbS-wide rows of
     `crop_scope_policy.csv`. Two of your rulings are family-level, so neither has ever applied:
     agroforestry F5 shaded perennials (95 cocoa and coffee units never vote) and the wetland
     paludiculture ruling of 16 October.
   - **Data-deficient asset rows tell M2b "no damage".** Nine asset-threat rows with too little
     evidence carry `asset_sensitivity = none` instead of blank. One of them has prose describing
     35–40% seedling mortality.
   - **Old prose still describes rows whose class has since changed.** Prose written before the
     class stamp existed (254 of 293 entries) still renders on rows that have since become data
     deficient, so some read as positive findings.
3. **The AF results are fragile.** In 119 of 187 rows, removing a single unit flips the class or
   deletes the row. production_gap goes back from conflicting to strong_positive if any one of 12
   units is dropped. Second-hand review sentences carry more than half the weight in 18 of 31
   classed roll-ups. This fragility is the case for the QA sample.
4. **Nothing combines evidence above the T6/T3 row today.** There is no theme roll-up, no NbS
   score, and no runtime scorecard: `runtime/outputs.py` and `schema_loader.py` are empty. **The
   wireframe does not ask for a single score either.** It shows one Likert chip and one
   confidence badge per outcome row. So the design question is how to fill the wireframe honestly,
   not how to invent an index.

## Done the same day (D1 and D2 implemented after Pete's "yes")

- **The three bugs are fixed.**
  - Family-level crop-scope rows now apply. AF F5 cocoa and coffee units vote, and so does the
    wetland paludiculture ruling.
  - Data-deficient asset rows state no sensitivity, and M2b treats a blank as not assessed.
  - Unstamped legacy prose is now stale on data-deficient and conflicting rows.
- **A fourth bug surfaced and is fixed.** The prose check stopped checking exactly those rows,
  because its trial entry had no class stamp.
- **179 rows across six NbS were re-prosed.** The full sweep of live prose shows 0 flags and 0
  rows pending.
- **Two orchestrator corrections:**
  - Dobhal 2024's second-hand reading of Philpott 2008 is superseded by the primary, which found no
    effect on coffee harvest. The shaded-perennial wind rows now read "none", and the NbS wind row
    reads conflicting.
  - A number-checker regex bug (ungrouped alternation that turned "twice" into 2.5) is fixed.
- **Review batches are live** (after the PR merges and Pages rebuilds):
  - Unit QA: `review.html?batch=af_qa_2026-10-22`. 166 high-leverage units, 2 flagged cards, and a
    random 40 (20 general, 20 newly voting F5).
  - Row review: `review.html?batch=af_rollups_2026-10-22`. The 46 agroforestry roll-up rows, each
    with its class, confidence, prose, family vote and evidence.

All decisions D1–D8 are now taken (see below).

## Revised 23 October, evening — the dashboard shows the mockup's rows (supersedes D3/D4/D7 below)

Checked against the mockup (Opportunity Space panels and NbS Comparison): it shows **one row per
problem** — the problem's spatial distribution (T5 need layer, runtime) beside how strongly the
NbS responds (the T6 evidence row) — and **no theme or group chips**. So:

- **D3 → (a) profile only:** no theme chips, no NbS number; one response chip per problem row.
- **D4:** no longer needed for themes; the same median / dissent rule is used only for a row
  that pools several T6 rows.
- **D7 → the mockup's rows** (`schema/lookups/scorecard_rows.csv`): *Risk to rural livelihoods
  (climate)* — erosion, drought, flood, heat; *What the NbS can address* — biodiversity loss,
  carbon, rural poverty, gender inequality (response chip here; still an unweighted flag in
  Priority Hotspots), food insecurity, and **water-table depletion (recharge)**, which pools water
  stress, catchment water yield and water quality.
- **Fire is a project risk** (M2b), not an opportunity-space row.
- **Production gap is an intermediate step** to rural poverty and food insecurity, not a row.
- **D6 revised (Pete: "moderate positive shows ++ HIGH?"):** the symbol now matches the evidence
  class one-to-one — + slight · ++ moderate · +++ strong (− −− −−− for harm) — and confidence is
  shown separately under the symbol (●●● high · ●●○ medium · ●○○ low), never inside the pill,
  so size and certainty can't be read as one thing.
- **Where and how (Pete 2026-10-24: "note if it is in-situ and direct or ex-situ indirect"):**
  every chip carries two small tags. *Where it lands* — on-farm · landscape / downstream ·
  both · public good — from the engine's `effect_locus.csv` (per NbS) with per-problem
  overrides in `schema/lookups/scorecard_locus.csv` (drafted for Pete's approval: water-table
  recharge and biodiversity = landscape, carbon = public good, water-harvesting flood =
  landscape, riparian erosion = both, mangrove flood = landscape …). *How direct* — direct
  when at least half the row's units measured the outcome itself, indirect when mostly a
  stand-in or mechanism (income for poverty, canopy cooling for heat, runoff for flood),
  counted from the units' crosswalk routes.
- D5 and D8 stand.

## Decided 23 October — scoring and dashboard (D3–D7, first build; superseded above)

- **D3 (b):** theme chips, no NbS-level number, plus a count strip.
- **D4 (a):** a theme chip is the TTL-weighted median of its priority rows at medium confidence or
  better; disagreement among them uses the cell rule (dissent ≥ 1/3 → ±); the theme's
  confidence is that of its weakest setting row.
- **D5 (d):** T6 and the hotspot map side by side by default; the TTL can switch on a filter that
  keeps only the priorities the NbS is evidenced to improve.
- **D6 (b):** five glyphs (++ + 0 − −−) and three badges (HIGH / MED / LOW), plus ± (studies
  disagree), ? (not enough evidence) and n/a (not assessed); CAUTION is the chip colour, set
  when a row lists measured harm for some adopters.
- **D7 — revised the same day (Pete):** the first build grouped the comparison chips by the T5
  themes. T5 is the *need* side (the hotspot layers), so the view drifted from the mockup and the
  TOR. Comparison rows are now **benefit rows** matching the mockup and the TOR benefit streams
  (`schema/lookups/scorecard_rows.csv`), in four groups: climate resilience (T3 hazards only, so
  nothing is counted twice) · land & water · nature & carbon · livelihoods; gender and IPLC lands
  are shown as context flags, never scored; agricultural dependency and the T6 hazard rows are
  not shown. **Food security is split from rural income**: a new T5 priority `food_insecurity`
  takes the food-security evidence that used to feed `rural_poverty`.

Built: `src/nbs_ruralscan/runtime/scorecard.py` → `docs/scorecard.json` (every schema build),
viewable at `docs/scorecard.html`. The scale, badges and TTL weights live in
`schema/lookups/scorecard_*.csv`. Glyph mapping: strong and moderate share ++ / −−, slight is
+ / −; T3 moderate and above is ++, low is +. Wiring the wireframe's NbS Comparison tab to this
JSON is a separate PR.

## Decided 23 October (Pete's row review)

- **D8 — economics rows:** cost rows leave the T6 scorecard for a separate **T6E economic
  profile** (same columns), which feeds the economic / econometric profiles. Cost per tCO2e is
  feasibility-level and is no longer generated. Cost reduction is used only as a farm-level
  production-cost saving (the route to profit and so to poverty).
- **Frost is out of T3 for every NbS.** Frost-tagged units stay in the register and feed T6.
- **Asset threat × drought** now says it is an establishment-phase risk first (the phase a
  project funds), while noting that mature cocoa and shade trees also died in the El Niño drought.
- **Catchment water yield** now says its evidence is from drylands only.
- **Asset threat × heat stress** is data-deficient: the evidence is too thin to say.

## Part 1 — Human QA/QC for agroforestry

**What exists:** the review page (one card at a time, approve / hold / reject, PICOS panel), the
review log, and soft-drop. **What's missing:** coverage. The 167 high-leverage units are the
ones that set or flip a class: sole voters, swing votes in a family vote, and strength-setters.
99 of them touch an NbS-level row. Suggested order:

1. The production_gap swing units, plus `watts22_10`. Each of these, on its own, flips the headline row.
2. The 5 silvopastoral practitioner ratings that lift drought × pastoral rangeland from low to
   moderate. That family row is 100% ratings.
3. The asset-drought units (`gateau18_2`, `cmscr20_4/_5`, Watts 2022) behind the M2b rows.
4. Rows that rest on a single unit.

Plus **a random sample of about 40 of the rest**, so we can state an error rate for the
evidence we did *not* review. That's the number a reviewer will ask for.

**Sequencing matters.** If the crop-scope bug is fixed first, 95 cocoa/coffee units start
voting and the high-leverage list changes. So: **fix the bugs, then recompute the list, then
review.** Otherwise you review against rows that are about to move.

## Part 2 — How T3/T6 are generated (the evaluation)

The pipeline as it runs, per cell:

1. **Units in.** Agroforestry pools 614 units. Crop- and species-specific units are excluded
   (130, of which the 95 F5 units are the bug above), leaving 488 practice units from 74 sources.
2. **Routing.** The crosswalk sends each unit to its T3 hazard or T6 priority; proxies count at 0.7.
3. **Eligibility.** Comparators, gas, existing-use, envelope-misfit and the evidence floor decide
   which units may vote.
4. **Weighting and vote.** Units are weighted by source tier × design weight × bundle share. A
   sign vote follows: if the minority sign holds at least 1/3 of the weight, the cell states
   conflicting evidence.
5. **Strength and confidence.** Strength is the median over the units that state a size.
   Confidence comes from the IPCC two-axis matrix.
6. **Family vote.** The family rows vote on the NbS class, weighted √n.

Output: 187 rows, of which 39 are data-deficient and 16 conflicting.

**Where the code has drifted from the method doc.** The doc (v0.1, 29 Sept) predates the
evidence floor, the conflicting class, the family vote and the design weights. It needs a refresh
so a reviewer can audit the engine against it. Three smaller code issues:
- Family rows are gated on sources counted across the whole register, not per cell, so 13 classed
  family rows rest on one source.
- A meta-analysis can reach very_high confidence from two sources.
- The code uses three different definitions of "measured".

**What a TTL would trip on:**
- 25 rows pair a weak class with high or very_high confidence. Readers take that as "strongly true"
  when it means "confidently small".
- 12 roll-ups get more than 40% of their weight from one source.
- 43 of 74 sources have no income group.

These are mostly display fixes, covered in Part 3.

## Part 3 — The hierarchy, and how scores reach the dashboard

**The hierarchy today:**

```
evidence unit
  └─ EV variable (e.g. crop_yield, soil_moisture)
       └─ crosswalk (direct / proxy 0.7 / component 0.7)
            ├─ T3 cell: NbS × hazard × farming system   (livelihood mitigation; asset threat → M2b)
            └─ T6 cell: NbS × T5 priority               (one row per priority, + family / scope rows)
                 └─ T5 theme  (climate_hazard · nbs_response · people_production · equity_inclusion · context)
                      └─ NbS     ← NOTHING aggregates at this level or the theme level today
```

**What the dashboard expects:**
- **NbS Comparison** has one Likert chip (`++ + 0 − −−`) and a HIGH / MED / LOW / CAUTION badge
  per outcome row, plus economics as $ ranges, archetype, time to first income and revenue streams.
- **Priority Hotspots** is the M4 spatial map.

**The gaps:**
- Our scale (7 classes + conflicting + data deficient) doesn't fit the 5-glyph chip.
- There's nowhere to show "studies disagree", "not enough evidence" or "not assessed".
- Our 5 confidence levels don't fit 3 badges, and CAUTION, which is about direction, sits in the
  confidence slot.
- The wireframe's outcome rows don't match the T5 priority ids.
- Three economics rows have no schema field.

**The options:**
- **A — No single score; a profile.** One chip and badge per priority, ordered by the TTL's
  High/Medium/Low priority weights, plus a count strip per NbS: "6 positive · 1 conflicting ·
  1 caution · 2 not assessed".
- **B — Theme chips.** One chip per theme per NbS: the TTL-weighted median of that theme's cells,
  using only cells at medium confidence or above. Harm and conflict are never averaged away (the
  same 1/3 rule as the cells), and the chip shows how many priorities stand behind it.
- **C — A numeric score.** Rank/3 × confidence × TTL weight. It bends the ordinal-first rule and
  mixes "how big" with "how sure", so at most it would be a sort key in Technical mode.
- **D — T6 and the hotspot map.**
  - D1 multiplies the hotspot weights by the effect.
  - D2 keeps only the priorities the NbS is evidenced to improve.
  - D3 shows need and response side by side.

**Recommendation: A + B, D3 by default with D2 as a toggle, and no headline NbS number.** This
fits the wireframe's existing shape and carries the cell-level conflict rule up one level, so the
logic is the same from evidence unit to theme. It also never pretends ordinal classes are
equally spaced. A scoping tool shouldn't rank NbS on a false-precision number.

## Proposed order of work

1. Fix the three bugs (one PR), re-synthesise, and re-prose.
2. Recompute the high-leverage list; you review the QA batch (high-leverage plus random sample).
3. Refresh the method doc to match the engine.
4. Build the scorecard layer you choose below, plus the wireframe and spec housekeeping.

## Decisions (one letter each)

**D1. Fix the three bugs now?** They implement rules you have already ratified, and classes will move.
- (a) yes, before QA **← recommended**
- (b) QA first on today's output

**D2. QA sample.**
- (a) all 167 high-leverage units plus a random 40 **← recommended**
- (b) only the units that touch NbS-level rows (99) plus a random 40
- (c) top 30 only

**D3. Is there an NbS-level number?**
- (a) profile only (A)
- (b) theme chips, no NbS number (A+B) **← recommended**
- (c) theme chips plus a Technical-mode sort score
- (d) a headline score

**D4. Theme-chip rule (if B).**
- (a) TTL-weighted median of cells at medium confidence or above, with theme confidence set by the
  weakest setting cell **← recommended**
- (b) modal class
- (c) best-supported cell

**D5. Should T6 change the hotspot map?**
- (a) side by side only
- (b) filter only
- (c) multiplier
- (d) side by side by default, with the filter as a TTL toggle **← recommended**

**D6. Chip scale.**
- (a) widen the wireframe to our 7 classes and 5 confidence words
- (b) keep 5 glyphs and 3 badges, add `±` (conflicting), `?` (data deficient) and `n/a`, and move
  CAUTION to the chip colour **← recommended**

**D7. Comparison rows.**
- (a) generate them from T5 priorities grouped by theme, plus a T3 hazard block **← recommended**
- (b) keep the wireframe's outcome rows and map them to T5/T3

**D8. Economics rows the schema can't fill** (archetype, time to first income, revenue streams).
- (a) add schema fields (a structure change)
- (b) drop them for now and show only the cost and return denominators T6 carries, with
  "insufficient evidence" where the gates fail **← recommended**
- (c) hand-authored text
