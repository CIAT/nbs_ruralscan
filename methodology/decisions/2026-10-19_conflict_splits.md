# Six "conflicting" rows: the full case for and against splitting each

**For:** Pete. **Needs:** one answer per numbered item — "split" or "leave" (or a question).
**Background:** your conflicting-evidence outcome flagged 30 rows. The prose audit found six where
the two sides may be answering *different questions*, so the conflict could be an artefact of
pooling — the pattern you already fixed once by splitting water stress from catchment yield.
"Split" means the same treatment: a separate target or route per question, each side getting its
own class. "Leave" means the row stays a stated conflict with the separator named in its prose.
Nothing is hidden either way; the question is what a Task Team Leader reads first.

---

## 1. Water harvesting × production, highland tropics (and the cross-family twin)

**What the row says now:** conflicting. 16 units, weighted agreement 0.65 — this one only just
tips into conflict.

**The positive side (10 units, weight ~2.0):** stone bunds, tied ridging, mulching and minimum
tillage each raise grain yield against untreated land in the Ethiopian synthesis (Adimassu);
tied ridging raises maize in the Kenyan trial's long rains, with and without inputs; young bench
terraces out-yield adjacent sloping fields.

**The negative side:** the *same Ethiopian synthesis* finds fanya juu and soil bunds REDUCE grain
yield, the authors attributing it to high-rainfall areas (their own words: physical structures in
high-rainfall areas, probably waterlogging), plus first-years-after-construction losses.

**The separator:** in Adimassu's own table the losing practices sit at roughly 1030–1454 mm
rainfall and the winning ones at 695–1139 mm. So practice and rainfall co-vary: bunds in wet
highlands lose, water-concentrating structures in drier settings win. This is not disagreement
about one thing — it is two different practice-by-climate situations.

**What a split would look like:** not a new target — a *scope* split. The evidence already carries
sub-practice (family) and the engine already emits family rows. The clean fix is tagging the bund
units with their stated rainfall band so the AEZ scope rows separate them, or accepting the
authors' high-rainfall attribution as a context override.

**My view: split — cheapest of the six**, because it needs no new ontology; the separator is
already in the data. The cross-family twin (35 units, agreement 0.64) resolves the same way.

---

## 2. Water harvesting, in-situ × water quality

**What the row says now:** conflicting. 7 units, agreement 0.56.

**The positive side (6):** five WOCAT compiler ratings that pits and bunds reduce downstream
siltation, plus a measured reduction in nitrogen lost in runoff behind graded soil bunds.

**The negative side (1):** minimum tillage INCREASED total nitrogen lost in runoff in the same
Ethiopian synthesis.

**The separator:** different practice (tillage vs structures) and different pollutant (nutrient vs
sediment).

**My view: leave, but fix the real problem instead.** One opposing unit out of seven should not
have produced a conflict at all — it did because the five practitioner ratings carry the 0.5
design weight, so one measured negative nearly balances five rated positives. That is your design
weighting working as ratified. If anything, the question is whether minimum tillage belongs in the
in-situ water-harvesting family at all; that is a FAM question, not a split.

---

## 3. Forest restoration, cross-family × water stress

**What the row says now:** conflicting. 3 units, agreement 0.54.

**The positive side (2):** infiltration capacity improves after forest cover expansion in 83% of
cases in the Filoso vote-count, plus an expert statement that infiltration and recharge recover.

**The negative side (1):** the SAME Filoso paper's vote-count for groundwater levels and recharge:
down in 67% of cases.

**The separator:** one paper, two different physical quantities. Water enters the soil more easily
(infiltration up) while the water table still falls, because the trees transpire the gain before
it reaches the aquifer. Both findings are true simultaneously; pooling them manufactures a
conflict the source itself does not contain.

**What a split would look like:** route `soil_permeability` (infiltration) and
`groundwater_recharge_potential` to different homes. Recharge arguably belongs with your
catchment-water-yield target — it is the same "what is left for others" question one step
underground. Infiltration stays local.

**My view: split — the clearest case of the six.** One route change, no new target needed if
recharge joins catchment water yield.

---

## 4. Forest restoration, active planting × biodiversity

**What the row says now:** conflicting. 8 units, agreement 0.51 — a genuine knife edge.

**The negative side (4):** plantations hold fewer species than natural regeneration of the same
stand, fewer than uncut control forest, and a synthesis of ten global reviews finds plantations
poorer; planting can reduce biodiversity where forests would regenerate anyway.

**The positive side (4):** three WOCAT compiler ratings from ONE technology sheet (plant, animal
and habitat diversity all rated up), plus a measured Thai framework-species result: 36 tree
species naturally recruited beneath an 8-year-old planting.

**The separator:** the comparator. The losses are planting measured against what nature would do
(regeneration, intact forest). The gains are planting on land with no such alternative — degraded
sites, bare dunes. In other words: planting is bad where regeneration was possible and good where
it was not. That is a siting rule, not a contradiction.

**My view: this is the most decision-relevant conflict in the tables and I would NOT split it
mechanically.** The honest fix is a comparator tag (planting-vs-regeneration as its own
comparison, like your existing-forest rule) — but the three WOCAT ratings from a single sheet
carrying half the positive weight is the weaker problem. A reviewer pass on this row is worth
more than a schema change. Suggest: leave as conflict, prose already states the siting rule;
revisit after the sign batch.

---

## 5. Agroforestry, boundary planting × drought

**What the row says now:** conflicting. 3 units, agreement 0.52.

**The sides:** live fences supply livestock fodder during drought when pasture is scarce
(positive, second-hand); crop yield losses are GREATER near shelterbelts in dry years because
trees compete for water (negative, second-hand); and the largest-weight unit is an explicit "no
clear consensus" null from a review.

**The separator:** different outcome (fodder vs crop yield) and different sub-practice (live
fence vs shelterbelt) — but all three units are second-hand and the review's own conclusion IS
"no consensus".

**My view: leave.** The conflict label is accurate here — the field itself is conflicted, and the
best unit in the row says so in words. A split would dignify three second-hand units with two
rows. If boundary-planting drought matters for a pilot, the fix is acquiring the primaries.

---

## 6. Wetland × heat

**What the row says now:** conflicting. 4 units, agreement 0.54, essentially one flux-tower study.

**The sides:** restored wetlands run 2.1–5.1 °C cooler than drained farmland by DAY (positive);
the same sites run 0.7–3.6 °C warmer at NIGHT and up to 2.3 °C warmer in spring and autumn
(negative). Plus one second-hand statement about intact wetlands.

**The separator:** time of day and season, within a single study.

**My view: leave as conflict for now.** Day and night heat are genuinely different stresses (crop
heat is a daytime problem; livestock and human heat strain is substantially a night problem), so
a split would be defensible — but it would need day-heat and night-heat as separate targets fed by
one study. One more measured source would tell us whether the pattern generalises before we build
ontology on it.

---

## Suggested one-line answer

"splits: 1, 3" matches my reading. Add 4 if you want the planting-vs-regeneration comparator
built now rather than after the review batch; say "leave all" if you would rather every one stay
a stated conflict until more evidence lands.
