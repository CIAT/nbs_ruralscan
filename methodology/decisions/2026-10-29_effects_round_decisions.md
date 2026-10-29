# Effects round 2026-10-29: five decisions for Pete

**Answered 2026-10-29 (Pete):** 1: out by default, in only if a water-harvesting capture
structure is included; 2: OUT ("how is plastic mulch going to be nature based?"); 3: ok;
4: ok; 5: ok. Applied in catalogue #52 (ruleset v1.9.2): 26 no-till units and 9 plastic-mulch
units soft-dropped, asset-index route and 12 scorecard labels ratified, labour bands added.

Five questions are left from the effects round (#489). The others are already settled; see
"Already settled" at the end. Each one takes a letter. Answer in one line, for example
`1 B, 2 A, 3 yes, 4 yes, 5 A`.

---

## 1. No-till with residue cover: is it water harvesting?

**What is at stake.** 26 water-harvesting units from six sources. They stay or go together.

**The conflict.** Two of your rulings point opposite ways for this one case:

- **Ruling 2 (10-19):** "CA bundles with residue cover" stay in water harvesting. Minimum
  tillage *alone* is out.
- **Ruling A (10-21, catalogue #31):** zero- and minimum-tillage arms yield *no*
  water-harvesting unit. Only capture structures count (basins, pits, zai, tied ridges,
  bunds, half-moons).

No-till plus residue cover is caught in between. It has soil cover, so ruling 2 keeps it.
It has no capture structure, so ruling A drops it. The lanes applied ruling A to new papers
(Kassie 2015 and Thierfelder & Wall 2010 gave no units) but the register already holds 26
such units from earlier rounds.

**Example.** Bruelle 2014, Madagascar: upland rice sown with no tillage into a dead mulch of
maize and legume residues gave higher and steadier yields than ploughed plots. There is no
basin, pit or ridge. The residue holds the rain where it falls.

**Units affected:** Bruelle 2014 (7), FAO 2011 CA climatic-risk modelling (7), Thierfelder 2026
(5, riplines + residue), Dalton 2014 (4, zero tillage + residue), Arslan 2015 (2, cited), FAO
SLM in Practice 2011 (1).

**Options.**

- **A. In.** Residue cover is an in-situ water-harvesting mechanism, so no-till + residue
  stays. Ruling A then covers tillage *without* cover only. The 26 units stay; Kassie 2015 and
  Thierfelder & Wall 2010 get extracted.
- **B. Out.** Water harvesting needs a capture structure. The 26 units are soft-dropped
  (`wrong_practice`, restorable). Mulching *without* no-till (e.g. Sime 2015 stalk mulch)
  stays, as D5 ruled.
- **C. In, but bundled.** Keep them as water harvesting tagged `attribution=bundled` with
  tillage as a co-practice, so each counts at the 0.6 bundle weight.

**Recommendation: C.** The residue does capture water, but no-till changes several things
at once. A bundle tag credits the cover without letting the whole CA package count as
water harvesting.

---

## 2. Plastic-film mulch on ridge-furrows (Mo 2017)

**What is at stake.** 8 units from one paper, and a rule for future plastic-mulch papers.

**The question.** Ridge-furrow planting is a micro-catchment, so it is water harvesting.
Mo 2017 always pairs it with a polyethylene film over the ridges. The film is not
nature-based. The two lanes treated the same case differently: lane A dropped Wang 2016's
plastic-film arms as "not an NbS"; lane B kept Mo 2017 tagged `bundled`.

**Example.** Maize yield +90 to 95% and higher net income on ridge-furrow + film versus flat
planting. But the film also draws down deep soil water and soil carbon during the season,
and the film is a large part of the input cost.

**Options.**

- **A. Out.** Plastic film is not an NbS; any arm that needs it gives no unit. Mo 2017's 8
  units are soft-dropped, matching lane A's call on Wang 2016.
- **B. Bundled.** Keep them tagged `bundled` (current), at the 0.6 bundle weight.
- **C. Keep only the harms.** Keep the deep-water and soil-carbon draw-down as cautions. Drop
  the yield and income gains the film inflates.

**Recommendation: A.** The yield gain cannot be separated from the film. A World Bank NbS
scoping tool should not credit polyethylene mulch.

---

## 3. Household asset index as a poverty measure

**What is at stake.** 8 units (7 from Kimwanga 2026, Malawi forest co-management, 1 from
Coulibaly 2016). They feed the forest-restoration rural-poverty row.

**The question.** A route was added so a household asset index counts toward `rural_poverty`
as a **proxy** (weight 0.7, like income). It needs your ratification; it is marked
"pete (pending)".

**Example.** Kimwanga 2026: asset index +5.4% in Vwaza (significant). Under rainfall shocks
it rose in two sites and fell in one (Mua-Livulezi −2.8, significant).

**Answer:** yes (keep the route) / no (remove it; the 8 units stay in the register, unrouted).

**Recommendation: yes.** Assets are a standard welfare measure. The proxy weight already
discounts them below direct income.

---

## 4. In-situ or ex-situ: the scorecard's draft labels

**What is at stake.** The small in-situ / ex-situ tag on each scorecard chip (your request of
10-24). These 12 rows set it per NbS × problem. They are marked "draft (Pete to approve)" in
`schema/lookups/scorecard_locus.csv`:

| NbS | problem | label | why |
|---|---|---|---|
| all | water-table depletion | landscape | recharge is shared across the catchment |
| all | carbon | public good | no farm-level beneficiary |
| all | biodiversity | landscape | habitat and connectivity beyond the plot |
| water harvesting | flood | landscape | bunds and dams cut peaks downstream |
| water harvesting | erosion | on farm | holds soil on the adopter's plot |
| water harvesting | drought | on farm | water serves the adopter's crops |
| water harvesting | food insecurity | on farm | measured in adopting households |
| water harvesting | rural poverty | on farm | measured in adopting households |
| riparian buffer | flood | landscape | attenuates peaks downstream |
| riparian buffer | erosion | both | holds the field edge and traps sediment |
| mangrove | flood | landscape | protection lands on the coast behind the stand |
| mangrove | rural poverty | both | fishery income on the stand, protection behind it |

Everything not listed falls back to the NbS default in `effect_locus.csv` (for example, forest
restoration is always off-site).

**Answer:** yes (approve all) / list the rows to change.

**Recommendation: yes.**

---

## 5. Size bands for labour (man-days per hectare)

**What is at stake.** Today one unit (Bucagu 2013, Rwanda: Tephrosia intercropping needed 30
man-days/ha less than farmer practice) has no size class, because labour has no band. It
shows on 4 cost rows. Future SWC papers report labour often.

**Draft bands.** Anchored on the establishment labour the corpus itself reports for SWC
structures:

| class | man-days per ha | anchor in our evidence |
|---|---|---|
| small | under 50 | grass strips or live hedges: 30–50 (Roose 2006) |
| moderate | 50 to 200 | stone bunds 50–80 over 5 years (Roose 2006); half-moons about 80 (Roose 1994) |
| large | over 200 | bench terraces with walls: 700–1,500 (Roose 2006) |

The same bands read a saving: Bucagu's 30 man-days/ha saved = a small saving. As with the
cost bands, these are scoping-grade; adjust the thresholds, not the mechanism.

**Options.** A: approve as drafted. B: change the thresholds (give numbers). C: no labour bands.

**Recommendation: A.**

---

## Already settled (no answer needed)

- **Supplemental irrigation from harvested runoff.** You ruled this on 10-19
  (`wh_supplemental_irrigation` = A+C): it is water harvesting, tagged bundled with
  irrigation. The lanes asked again because their briefs did not carry the ruling. Applied
  to 27 units (Barron 2005, Fox 2003 and 2005, Waqas 2025, Biazin 2012, Dile 2013). The lane
  brief now names the ruling.
- **The four held second-hand readings.** All four were checked against the primaries:
  - Malan's −15% (credited to Kassie 2008) is not in Kassie 2008.
  - Forbes's 20% belongs to a different reforested area in Reid & Page 2003.
  - Wei 2016's yield figures are Adgo 2013's, credited to the wrong countries.
  - Three were dropped as drifted readings; the fourth (Taillardat, co-cited) was linked to
    its Wilson 2009 primary instead of dropped.
- **Adoption rate.** The 49 units were dropped per your answer today, each with a review-log
  entry.
- **Marginal P values.** 0.05 ≤ P < 0.10 counts as not significant (catalogue #51). No
  existing unit had to change: five candidates were checked and all are significant at 5%.
