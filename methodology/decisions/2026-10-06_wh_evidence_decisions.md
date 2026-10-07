# Water-harvesting evidence: decisions for Pete

2026-10-06 · for Pete Steward

## How to read this

Five decisions, each with a recommendation; about 20 minutes. You decide the *rule*, not the implementation. Every rule here is already coded and tested, so the cost of changing your mind later is a re-run, not a rebuild.

Background in two sentences. The water-harvesting T3/T6 tables are now generated from 962 evidence units: 276 measured results from papers and project evaluations, and 686 **compiler ratings** from WOCAT technology sheets (a compiler ticks "soil loss: decreased, +2" on a −3…+3 scale). The questions below are all about how those two kinds of evidence should be allowed to interact.

For each decision: what is at stake, a concrete example from the current tables, the options, my recommendation. Reply with the decision numbers and the option letters (e.g. "1B, 2A, 3A, 4 all, 5A").

## Decision 1 — can compiler ratings move a result that measured studies have set?

**At stake.** Whether a large pile of practitioner opinions can change the headline strength of an effect when real measurements exist.

**Example.** Water harvesting × flood. Before the WOCAT sheets came in, the measured evidence (runoff cut by half in Tunisian catchments, soil-loss reductions of 50–90 % on terraces) put flood mitigation at **very high**. Forty-six compiler ratings then arrived, most ticking "flood impacts: decreased, +1 or +2" — i.e. "moderately". The headline is now **moderate**. Nothing in the measured evidence changed; the opinions outvoted it.

**What already protects you.** Ratings are discounted (grey source, assertion not measurement) so one rating counts for about a quarter of one measured result. Ratings alone can never push the *confidence* above "limited". But in the *strength* vote, forty discounted opinions still outweigh ten measurements.

**Options.**

- **A — Leave it.** Strength = weighted vote of everything. Honest to the full pool; practitioner experience is real evidence. Downside: in any cell with many sheets, the compilers' habit of ticking +1/+2 becomes the answer.
- **B — Measured sets strength when it exists (recommended).** If a cell has at least one measured result with a stated strength, the strength class comes from the measured results only; ratings still count toward agreement and confidence and still fill cells with no measurements. Flood would read very high again, with the ratings visible in the agreement note. This mirrors a rule you have already accepted for proxies (direct measurements beat proxies).
- **C — Separate columns.** Report a measured strength and a practitioner strength side by side. Most honest, but T3/T6 have one strength field; it needs a structure change and the consumers (M2b, M5) would have to pick one anyway.

**Recommendation: B.** It is one rule, already proven for the direct-vs-proxy case, and it keeps the WOCAT material where it is strongest: coverage of hazards and practices the literature never measured.

## Decision 2 — "copes not well" on a field practice: damage to the investment, or exposure of the field?

**At stake.** What the M2b "risk to the investment" screen will say about field-level water harvesting (pits, bunds, ripper tillage) in flood- and storm-prone places.

**Context.** Every WOCAT sheet asks "how does the Technology cope with… river flood / rainstorm / drought?" on a four-step scale. For built works (check dams, sand dams, cisterns) a "not well" answer is a statement about damage to the structure — exactly what the asset-threat rows are for. For field practices the same answer usually means the *field* floods, not that the pits are destroyed; often the pits are what survive.

**Example.** The in-situ family's flood and rainstorm asset-threat rows now read **high** on the strength of Niger and Zambia sheets that say pits and bunds cope "not well" with river floods. Read as investment risk, that would warn a TTL off zaï in floodplains — the opposite of the field evidence.

**Options.**

- **A — Asset-threat rows only for built structures (recommended).** Coping ratings feed asset rows for runoff-catchment, rooftop, spate and terracing families; for in-situ and micro-catchment they are recorded but stay out of the asset rows. One line in the hazard lookup; the units remain in the register.
- **B — Keep them, label them.** Leave the rows, add a flag that the family is field-level so M2b can discount. Puts the judgement on the consumer.
- **C — Drop field-practice coping units entirely.** Loses the information that these fields are exposed, which is still useful for the livelihood lens.

**Recommendation: A.** The question the sheet asks is about the technology; the answer we need for M2b is about the asset. Where there is no asset, there is no asset threat.

## Decision 3 — a cistern that runs dry in a drought: asset damage, or not?

**At stake.** Whether the drought asset-threat rows describe structures breaking, or structures failing to deliver. They currently mix both.

**Context.** Four Brazilian units (household cisterns and subsurface dams running dry in multi-year droughts) and one Tunisian unit (benefits limited by drought) were tagged as asset vulnerability. Their own notes say "not structural damage". They now help set the rooftop and runoff-catchment drought asset rows, next to real damage such as check dams breached by peak flows.

**Why it matters.** M2b Stream A multiplies hazard exposure by asset sensitivity to say "your investment could be lost". A dry cistern is not a lost cistern; it is a benefit shortfall — which is what the T3 *livelihood* row and the T6 water-stress row already capture.

**Options.**

- **A — Damage only (recommended).** Asset threat = physical loss, breakage, siltation, erosion of the works. Storage running dry is re-tagged as an effect unit (the practice's benefit in a drought year), where it lowers the drought-mitigation class honestly instead of inflating investment risk.
- **B — Keep functional failure as asset threat.** Treat "did not deliver" as a threat to the investment case. Broader, but it double-counts with the livelihood row and blurs what M2b is screening.

**Recommendation: A.** The retag is five units, done through the review tooling with a reason code, fully reversible.

## Decision 4 — four WOCAT field-to-variable mappings to confirm

**At stake.** Which WOCAT questionnaire items are allowed to speak for which of our variables. Twenty-seven items are mapped; twenty-three are plain synonyms (crop production → crop yield, soil loss → erosion). These four involve a judgement. Each is one line in a lookup; say "drop" and its units leave the pool.

| WOCAT item (what the compiler rates) | Our variable | Units | Judgement | My view |
| --- | --- | --- | --- | --- |
| Risk of production failure (increased … decreased) | food_security | 46 | A lower risk of crop failure is read as better food security. Proxy, not a measure of diets. | Keep — it is the closest WOCAT comes to the T5 priority, and it is tagged as a proxy |
| Harvesting / collection of water (reduced … improved) | water_access_deficit | 24 | Was wrongly mapped to groundwater recharge; now "more water collected = smaller access deficit". | Keep (fixed this round) |
| Above-ground biomass / carbon (decreased … increased) | carbon_sequestration | 35 | A compiler's sense that biomass grew, treated as a component of carbon. Bhutan and Bangladesh sheets rate things that are not net gains (organic matter moved within a terrace; higher cropping intensity). | Keep but as component weight only (already 0.7); or drop if you want carbon to rest on measured stocks only |
| Crop / animal / habitat diversity (decreased … increased) | biodiversity_outcome | 35 | Compilers rate diversity of crops or habitats, sometimes expected rather than observed. One rooftop-cistern sheet gives biodiversity +1 with no pathway. | Keep for plant/habitat diversity; drop the single rooftop unit as a QA item |

**Not mapped on purpose** (so you know what is missing): workload (routed to the operational-risk lane, not an effect), water quality (no chemistry behind it), wood production, land-use rights, community institutions, pest and disease, evaporation, salinity.

**Recommendation: keep all four**, carbon as component only.

## Decision 5 — conservation tillage inside the in-situ water-harvesting family

**At stake.** Whether ripper tillage, minimum tillage and mulching count as water harvesting when the tables are read.

**Context.** The family scheme you signed off lists "conservation tillage / mulching" as an in-situ sub-practice (the limiting factor is the same: hold the rain where it falls). Four WOCAT sheets now sit there (a Zambian ripper, Philippine and Kenyan small-scale tillage, South African basin tillage). Two things follow. The Philippine sheet is the only negative unit in the in-situ flood row. The Zambian sheet credits its yield gain "mostly" to early planting, not to water.

**Options.**

- **A — Keep (recommended).** Consistent with the family scheme and with the conservation-agriculture syntheses already queued for in-situ. Flag the two sheets as QA items.
- **B — Split a `conservation_tillage` family.** Cleaner reading for TTLs who think of water harvesting as structures, but it is a family-scheme change needing the MFL/Namita sign-off and would re-cut every in-situ row.

**Recommendation: A.** Revisit only if the conservation-agriculture literature round makes in-situ read like a tillage story.

## Confirmations — rules you are already living with since #277

These went in with the merge of #277 and are marked "pending ratification". No action needed unless one looks wrong to you; a "no" on any of them is a one-line revert.

| Rule | In plain terms | Why it exists | What changed because of it |
| --- | --- | --- | --- |
| Strength from the units that found an effect; nulls lower agreement only | A "no effect" study makes us *less sure*, not *less strong*. Before, four null drought units outvoted seven strong ones and the cell read "low". | Vote-counting practice separates consistency from size; the IPCC two-axis confidence already carries the nulls. | Water-harvesting drought: low → very high. Agroforestry drought: low → very high. |
| Measured direct results beat proxies | A soil-moisture gain cannot set the drought class when drought-year yield results exist. | Proxies are discounted in weight but weight never bounded the class. | Caught a high-rainfall infiltration unit setting an agroforestry drought class. |
| Yield, income and food security under a stated hazard count as hazard mitigation | A drought-year yield result is drought-impact evidence. Before, it only reached the production row. | Was the real cause of the "low drought" wall. | 37 crosswalk routes; only units that *state* the hazard enter (general yield evidence stays in T6). |
| Bundled-programme results vote at half weight | A watershed programme's income gain where the structures are one component among roads and loans. | Attribution is weaker than an isolated practice result. | Bank completion-report results still count, at half. |
| Contrast encodings (v1.6.2) | "0 kg/ha without, 300–400 with" and "two to three times" can now be encoded; before they were direction-only. | The contract had no way to carry a with/without pair or a spelled-out multiplier. | Nine water-harvesting units re-encoded as strong. |
| Cost cells split by what is counted | Per-hectare, per-household and per-structure costs no longer pool into one cell. | The same four cost figures were counted twice. | New per-structure and per-m³ cost bands (thresholds are scoping-grade guesses: USD 1 000 / 10 000 per structure; 5 / 50 per m³). |

## Not decisions — QA items for Namita and what comes next

**For Namita's review queue** (unit-level, reason-coded, reversible): a Somali WOCAT sheet whose flood rating contradicts its own comment; a Philippine flood rating with no comment; a Jordanian siltation rating that is an aspiration; a Burkinabè well-level hearsay unit; the Yemen spate cost that is per *irrigated* hectare; a rooftop-cistern biodiversity rating with no pathway; four earlier literature units with questionable signs. All listed in `methodology/effect_evidence_followups.md` §1e.

**Next work, in the order I would take it** (say if you want a different order):

1. Apply your answers above, re-run, re-check the prose (half a day).
2. The 24 agroforestry and forest-restoration WOCAT sheets already cached — same adapter, no new rules (an hour).
3. WOCAT cost tables (establishment and maintenance cost per unit) into the ordinal cost cells — one more adapter section.
4. Namita's OA-recovery queue (42 water-harvesting, 34 agroforestry, 14 economics sources) unblocks round 3 for all three NbS.

**Where the technical record lives:** PR #278 (adapter, run, gates), `methodology/search_protocol.md` §WOCAT (the handling rule), `schema/recipes/water_harvesting_conservation/T3T6_BENCHMARK.md` (generated vs seed rows).

## Decisions taken (Pete, 2026-10-06) and how they were applied

| # | Decision | Pete's reasoning | Applied as |
| --- | --- | --- | --- |
| 1 | **A — leave the weighted vote** | The flood "measurements" in the example are runoff and soil-loss proxies, not flood measurements, so a measured-beats-rated rule would rest on a false distinction; the existing downweighting is enough. | No change. QA note: units extracted as `flood_hazard` that actually measure runoff should be re-labelled `runoff_reduction` (proxy route) — Namita's queue. |
| 2 | **Keep field-practice coping ratings in the asset rows** | Pits do not survive floods: soil wets and collapses, pits infill and silt, lifespan shortens — that is damage to the works. | No change (the letter in the reply read "A"; the reasoning says keep — applied the reasoning; say if that is wrong). |
| 3 | **A — asset threat = physical damage only** | A dry cistern is a benefit shortfall, not a lost cistern. Separately: are household cisterns a nature-based solution at all? | WOCAT drought / heatwave coping ratings no longer feed asset rows (hazard lookup; existing units soft-dropped, `accepted_correction`); the four literature "ran dry / benefit limited" units re-tagged as effect units with direction *none*. The rooftop question is raised below. |
| 4 | **Rows 1–2 keep; rows 3–4 keep only with a stated mechanism** | A carbon or biodiversity tick with no pathway (a cistern rated +1 for biodiversity) is not evidence of a delivered result. | `requires_comment = true` on the four carbon / diversity fields in the impact lookup: a rating counts only when the compiler wrote a comment stating the mechanism; comment-less ones soft-dropped; the same principle extended to the emissions item (an emissions tick read as sequestration), not to the soil-organic-matter item, which compilers rate directly. |
| 5 | **A — keep conservation tillage in in-situ** | — | No change. Two sheets flagged for QA. |

**Open question raised by D3 — rooftop / household cisterns.** The `water_harvesting__rooftop` family comes from the original water-harvesting recipe (Benson's family scheme, `rooftop_harvesting` sub-practice). It is a built domestic water-supply technology, not a landscape process. Options: (a) remove the family from the NbS (scheme change — needs the family-scheme sign-off; its 22 WOCAT units and 8 Brazilian cistern units stay in the register, tagged); (b) keep it but exclude it from the generated T3/T6 and the opportunity space (`spatial_product_type = qualitative_only`), so it appears only in Module 6 hand-off material; (c) keep as is. My recommendation is (b) until the scheme is revisited: the Brazilian cistern evaluations are good evidence about drought-year water access that a TTL may still want to see, but they should not score as a landscape NbS.

**Rooftop decision (Pete, 2026-10-06): option (b).** The family registry already marks `rooftop_harvesting` as `qualitative_only` and "PARKED: settlement-driven, not a rural-landscape suitability surface" (Benson's scoping). The generated T3/T6 now honour that flag: any `qualitative_only` family's evidence stays in the register (30 units: 22 WOCAT cistern sheets, 8 Brazilian cistern evaluations) for Module 6 hand-off material but never sets a scored class or a row (`scripts/synthesise-t3t6.py`, `parked_families` in the run report).

## Decision 6 (Pete, 2026-10-07) — hazard-intensity discount (graded, not a cap)

**Pete:** "The drought labelling seems a little high — water harvesting can mitigate drought a bit, but it is not irrigation; it is not going to help you with late-onset or extreme drought." Then, on the first fix: "that is too extreme, I did not want a hard rule."

**What was wrong.** The drought class only looked at how big the benefit was *when there was one*. Studies that measured no benefit or a loss in a severe drought year (crops failing completely in Mozambique, conventional tillage beating no-till in Zimbabwe 1991/92, no millet gain in Burkina Faso's driest year, Brazilian stores running dry, consecutive drought years in Tunisia) only dented the agreement score; they could not move the class. So water harvesting read **very high** for drought.

**First attempt (rejected).** Any measured failure under the same hazard forced the cell down to **moderate**. Too blunt: one failed trial would have pinned a cell with twenty good measurements.

**Applied instead (this PR).** The class is scaled by *how much* of the measured same-hazard evidence found no benefit or a loss, by evidence weight. A tenth of the evidence failing barely moves a cell; a third takes very high to moderate; a majority takes it to low. The floor is **low**, never "none", because the direction vote still says the practice helps. Only measured studies that name the hazard count — practitioner ratings (WOCAT) and findings about other hazards do not. Each affected row says so in its statement and lists the failure studies and the share in its account, so it can be challenged.

**Effect on the tables.**

| Cell | Before | Now | Share of measured drought/flood evidence that found no benefit |
|---|---|---|---|
| Water harvesting · drought (all systems) | very high | **moderate** | 44 % |
| Water harvesting · drought · in-situ family | high | **low** | 65 % |
| Water harvesting · drought · runoff-catchment family | very high | **moderate** | 23 % |
| Water harvesting · flood (all) | moderate | **low** | 31 % |
| Agroforestry · drought · planted silvoarable | very high | **moderate** | 21–35 % |
| Forest restoration · all cells | — | unchanged | — |

No prose text changed (the prose describes the evidence, not the class, and its conditionality paragraphs already name these failures). Two new water-harvesting semi-arid / upper-middle-income scope rows got prose.

**To confirm or change:** reply "6 ok", or say what feels off (e.g. "in-situ low is too harsh") and the share-to-class step can be tuned.

## Decision 7 (Pete, 2026-10-07) — tag the severity of the hazard on the evidence

**Pete:** "Do we qualify the severity of the hazard in the table?" — we did not. Chosen: option 2, tag severity on the evidence, with the note that much evidence will not qualify it.

**What changed.** Every hazard-stated effect and asset unit now carries `hazard_severity`: the author's own description of the event the result was observed under — `mild` (dry spell, erratic rain, late onset) · `moderate` (a drought / dry / low-rainfall year, a flood, no stronger qualifier) · `severe` (severe, driest year of a series, consecutive drought years, stores dried up) · `extreme` (extreme, record, rainless season, complete failure season, return period of 1-in-20 or rarer) · `unspecified` (the default: ratings, general statements, pooled reviews, model averages). Each tag other than `unspecified` cites the exact words from the quote, and the build checks those words are really there. Nothing was inferred from rainfall numbers or from what a drought "must" have been.

**What the tags show (395 units tagged; 319 unspecified, 30 moderate, 20 severe, 18 extreme, 8 mild).** Water harvesting drought evidence: measured units span moderate (7), severe (4) and extreme (4) events; the WOCAT ratings are mostly unspecified, with four practitioner sheets describing dry spells. Agroforestry drought: most measured evidence (32 of 44) does not qualify the event; 8 moderate, 2 severe, 2 extreme. Forest restoration: 5 units, mostly moderate. So the honest statement for most cells will be "benefit observed in moderate events; little or no measured evidence at the severe or extreme end".

**Applied in the engine (PR after #287).** (a) The Decision 6 discount ignores failures tagged `mild` (a practice that cannot buffer a dry spell is a different finding; it still lowers agreement). Unspecified failures keep counting — most evidence is unspecified, and ignoring it would silently restore the old optimism. (b) Each T3 livelihood row's account reports gains and failures per severity (`severity_coverage`), and the statement says plainly how the severe end reads: *tested, gain* · *mostly no gain (n gains vs n failures)* · *no benefit* · *no measured evidence at severe or extreme*. Water harvesting drought (all systems) now reads: "moderately reduces the impact of drought … at severe or extreme drought the measured results mostly show no benefit (1 gain vs 7 failures)". Agroforestry drought: "no measured evidence at severe or extreme drought". No class moved: the only mild-tagged failures are practitioner ratings, which never discounted. T3 keeps one class per cell; the severity banding of the class itself (option 3) stays open for Module 5 to ask for.

**To confirm:** "7 ok", or name tags to re-check (the lane's ten least-certain calls are listed in the PR body).

## Decision 8 (2026-10-07) — two ontology gaps closed; one weighting question for you

**What was wrong.** Three follow-up sections listed the same gaps: evidence about *how much water a catchment yields* was filed under "water regulation" (flow buffering), and evidence about *how stable yields are across seasons* was filed under "crop yield" (the level). Both were parked with a note; neither could reach the right cell.

**Applied.** Two new variables, pending your ratification: `water_yield` (annual yield, baseflow, spring/stream discharge; 16 units re-labelled from water regulation — the Teo 2022 model, the Filoso 2017 systematic review, the IUFRO 2018 report, two World Bank watershed ICRs, the Peru trench review, the Ethiopian exclosure meta-analysis) and `yield_stability` (9 units re-labelled from crop yield — the Knapp 2018 and Rusinamhodzi 2011 conservation-agriculture meta-analyses, Morel 2024, Tosh 2026, Nasielski 2015). Routes: water yield → water-stress priority (direct) and → drought cell (proxy, needs a stated hazard); yield stability → production-gap priority (component) and → drought cell (proxy). Quotes, pages and ids unchanged; only the label moved.

**Effect.** No T3 class moved. One T6 cell moved: **forest restoration → water stress, moderate → strong positive** (also the two family rows). That is not good news — read on.

**The question (8a).** The forest-restoration water-stress cell now says "strongly reduces water stress". The positive side is twelve WOCAT compiler ratings plus **one modelled study (Teo 2022) split into four per-region scenario outputs**; the negative side is **three measured syntheses** (a 167-paper systematic review and two reports citing it) saying forest cover expansion usually *reduces* water yield. Because strength is read from the units that agree with the majority direction, and the water-yield route is now direct, the model's four regional numbers set the strength. The measured reviews only lower agreement (medium).

Options:
- **A — leave it.** The vote is honest about what is in the pool; the account and prose already say the measured syntheses point the other way. Cheapest, but the headline class misleads a reader who only sees the table.
- **B — modelled-only strength cap (recommended).** When no *measured* unit of the majority direction exists on a direct route, cap the class at moderate, the same way proxy-only cells are capped. Direction still comes from the whole vote; the model stays in. Forest-restoration water stress returns to moderate; nothing else in the current tables changes.
- **C — one finding, one unit.** Collapse per-region outputs of a single model run into one unit, so a study counts once. Fixes this case, but the regional values are genuinely different (11 % to 85 %) and the contract allows one unit per reported result.

**Parked, needs your call (8b).** 18 agroforestry units about *landslides* (Philpott 2008, Hurricane Stan) sit under erosion hazard because there is no landslide hazard in the T3 list. Adding one is a hazard-enum change (same as the sedimentation / extreme-rainfall decision). Say "add landslide as a livelihood hazard" or "asset-threat only" or "leave under erosion".

**To answer:** "8 ok, 8a B, 8b <choice>".

## Pete's answers, 2026-10-07 — and what was applied

**6 — "Are we capturing maladaptation?"** Partly, and now explicitly. Before: a study where the practice made things *worse* under the hazard counted as a failure (it discounted the class and lowered agreement), and a cell where harm is the majority reads `negative`. But a minority of harm findings disappeared into the agreement score; a reader of a `moderate` cell could not see that two sources measured a loss. Now every T3 livelihood row and every T6 priority row carries a **maladaptation signal**: the measured units (not ratings) that found harm, their count and their sources, and the statement says "measured HARM (maladaptation) in n sources — the practice worsened this outcome for some adopters". Today that fires on 31 water-harvesting rows, 37 agroforestry rows, 17 forest-restoration rows and 5 riparian rows. Nulls are not harm. Asset-threat rows (damage to the works) are a separate stream and untouched, as you said.

**7 — ok.** Applied (#288, #289).

**8 — ok, 8a B, plus "forest restoration does not occur on farmland".**
- *8a B, modelled-only strength cap* — applied: when a model is among the units that set a class's strength and no measured unit of the majority direction backs it, the class is capped at moderate (ratings beside the model do not lift the cap; one measurement does). **It does not change the forest-restoration water-stress cell**, which I had wrongly attributed to the Teo model alone: a measured Ethiopian exclosure study (Meaza 2022, baseflow 1.5 to 4 times that of cropland) also backs the strength, so the cell legitimately reads strong on its positive side. What is really at issue there is the vote: twelve WOCAT compiler ratings plus two studies say more water, three measured syntheses say less. That is the grey-literature positive bias you flagged earlier and your D1 choice to keep the weighted vote. The account and prose name the disagreement; the class follows the majority. If you want the syntheses to outweigh the ratings, that is a D1 reversal — say so and it becomes a rule (e.g. measured syntheses set direction when they disagree with ratings).
- *Effect locus* — applied. Every family now carries where the farmer feels the effect (`schema/lookups/effect_locus.csv`): **forest restoration = off-site for all families** (your rule: never on the plot; downstream water, flood, microclimate, wider societal benefit), agroforestry = on-farm, water harvesting in-field / micro-catchment / terracing = on-farm, ponds-dams-spate-tanks = mixed, riparian = mixed. Every forest-restoration T3 row is stamped `landscape_scale_only = true` and its statement ends "This is an OFF-SITE effect for farmers: the practice is not on their land, so the benefit arrives downstream or at landscape / societal scale, not on the plot"; mixed rows say "part of this effect is off-site". Module 2 / Module 5 can read the flag directly.
- *8b landslide* — still open (no answer yet): livelihood hazard · asset-only · leave under erosion.

**PICOS — B.** Agreed; applied in the next PR (a `comparator = existing_forest` tag on the existing-forest and forest-loss studies; they stay in the protection / mangrove family rows and leave the roll-up and the planting / regeneration rows).

## 8b (Pete, 2026-10-07): B — landslide is an asset-threat-only hazard. Applied.

`landslide` joins sedimentation and extreme rainfall as a hazard that can damage the works but has no livelihood cell. The nine WOCAT "landslide: copes well / not well" ratings that had been filed under extreme rainfall now form landslide asset-threat rows: water harvesting low (terracing, ponds and dams); forest restoration moderate overall, high for assisted regeneration (compilers rate the regenerating stands as coping poorly), low for planting. The fifteen effect studies about whether forest or shade *reduces* landslides stay under erosion with a note saying so; a livelihood landslide cell (option A) would need an M2 landslide hazard layer and is parked.

## D6 confirmed · D1 revisited (Pete, 2026-10-07)

**D6 — "ok".** The graded drought discount stays.

**D1 — "synthesis should be higher weighted than practitioner ratings, the latter will be biased probably."** Applied as a study-design weight, read from `schema/lookups/design_weights.csv`: meta-analysis × 1.5, review × 1.25, randomised trial × 1.2, observational / quasi-experimental / model × 1.0, case study × 0.9, expert judgement × 0.6, **practitioner (WOCAT compiler) rating × 0.5**. It multiplies the existing quality weights (source tier, how the claim was made, grey-literature haircut), so a rating now counts for roughly a quarter of a measured synthesis of the same tier. Direction and strength both feel it.

What moved (25 rows): drought cells for water harvesting (mixed crop–livestock, terracing) and agroforestry rose from low to moderate because the meta-analyses in them now outweigh the ratings; agroforestry fire rose from negative to low; forest-restoration active planting → biodiversity flipped to moderate negative (the plantation-vs-natural-regeneration syntheses now carry the cell); forest-restoration and agroforestry poverty and erosion roll-ups shifted one class. The forest-restoration water-stress cell that raised the question did **not** move: with the ratings halved it is still carried by a measured Ethiopian exclosure study and the Teo 2022 model against the three syntheses — the account now shows the weight behind each side so you can see that.

