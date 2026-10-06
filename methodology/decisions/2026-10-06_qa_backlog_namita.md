# Effect-evidence QA backlog for Namita (water harvesting + agroforestry)

2026-10-06 · prepared for Namita Joshi (QA/QC lead) · reviewed by Pete

## What this is

The water-harvesting and agroforestry T3/T6 tables are now generated from about 1 400 effect and asset-vulnerability units (papers, project evaluations, WOCAT technology sheets). The AI prose writers read every row against its units and flagged the units below as doubtful. None of them has been changed; each needs a human decision.

**Where to do it.** Dashboard → QA/QC → set the *Evidence type* pill to **T3/T6** and the practice to water harvesting (or agroforestry). The flagged units are in the **AI-flagged** queue; each card shows the quote, the page or sheet section, the encoded relationship and the flag note. Decide **keep** (confirmed_pass / false_flag), **drop** (with the reason code), or **query** (send it back with a note). "Apply & submit to main" files your decisions as a PR.

**How to decide.** Read the quote, not the note. The question is always: does the quote support the encoded direction, number and variable for this practice? If not, drop with the reason that fits. Drops are soft (reversible) and leave the row in the register.

## The items (20)

| # | Unit | What looks wrong | Likely decision |
| --- | --- | --- | --- |
| 1 | Somalia gully works, downstream flooding (WOCAT 7778) | Rated as flooding *increased*, but the compiler's comment says reduced — a mis-tick on the sheet | drop (table_error) |
| 2 | Philippines tillage, flood impacts (WOCAT 1021) | Rated worse, no comment, no pathway | drop (insufficient_context) unless the sheet explains |
| 3 | Jordan marab, downstream siltation (WOCAT 5770) | "Reduced siltation is desired" — an aspiration rated as an effect | drop (speculative_evidence) |
| 4 | Burkina Faso water collection (WOCAT 1528) | Hearsay about well levels and rainfall | keep or drop on reading |
| 5 | Yemen spate investment cost | Cost per *irrigated* hectare pooled with cost per hectare restored | re-tag unit or drop from that cell |
| 6 | Sand dams: 67 % could not supply one household (Ritchie 2021) | Coded "no effect"; it is a negative finding | re-sign negative |
| 7 | Andean terraces, soil moisture (Willems 2021) | Only the positive half of a quote that also reports no advantage for narrow benches | widen the quote / add the null |
| 8 | Larger sand dams raise flood risk (Ritchie 2021) | A design trade-off, not evidence that sand dams worsen floods | re-tag or drop |
| 9 | Zaï food security (Kaboré 2004) | Coded negative; the quote describes families still in deficit in dry years, not the practice lowering food security | re-sign none or drop |
| 10 | Niger banquettes, economic return (Heusch 1995) | Coded positive for a return of about 1 % | check sign |
| 11 | Karnataka cost (ICR 2020) | Tagged cost reduction but encodes an absolute construction cost | re-tag or drop |
| 12 | Volta small reservoirs, cost (Venot 2012) | Tagged cost reduction but is a spread of rehabilitation costs by implementer, no magnitude | drop or re-encode |
| 13 | Uttarakhand runoff +1.5 % (ICR 2022) | Kept as a null result while the same page says most watersheds show less runoff | decide which statement the unit carries |
| 14 | Himachal check dams, cost per m³ (ICR 2017) | Per m³ of masonry, banded as if per m³ of water stored | re-tag the unit |
| 15 | Tunisia catchment, 50 % less runoff over 71 floods (Roose 2006) | Encoded as a direct flood measurement; it measures runoff (Pete's point on proxies) | re-tag runoff_reduction |
| 16 | Philippines tillage, soil loss (WOCAT 1021) | The only negative unit in the in-situ flood row | check the sheet |
| 17 | Zambia Magoye ripper, crop production (WOCAT 1719) | Compiler credits the gain "mostly" to early planting | drop as not attributable |
| 18 | Bhutan stone bunds, soil organic matter (WOCAT 6891) | Organic matter moves within the terrace; rated as a gain | keep with note, or drop |
| 19 | Bangladesh bench terraces, emissions (WOCAT 4284) | Reduced emissions credited to higher cropping intensity, not storage | keep or drop |
| 20 | Yemen spate income and return (ICR 2012, two units) | Already dropped as ex-ante appraisal projections | confirm the drop |

Two further items need no decision from you but are worth knowing: WOCAT "per structure" costs run from a 3–4 m fascine line to a 5 100 m² haffir, so the per-structure median is coverage, not a unit cost; several family cost rows rest on a single sheet and read as such (limited evidence).

## Reason codes you will use

`table_error` (the source's own table or tick is wrong) · `wrong_variable` (right quote, wrong variable or sign) · `quote_too_narrow` · `insufficient_context` · `speculative_evidence` (aspiration or projection, not an observation) · `unusable_value` · `confirmed_pass` / `false_flag` (keep).

Technical record: `methodology/decisions/2026-10-06_qa_backlog_items.csv` (flags applied with these notes), `methodology/effect_evidence_followups.md` §1e.
