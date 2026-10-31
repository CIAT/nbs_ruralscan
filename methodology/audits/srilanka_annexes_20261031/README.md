# Sri Lanka mangrove annexes: T4 coverage review, 31 October 2026

## Result

Screened the native text of PDF150–194 of the existing 194-page national guide:
45 previously index-only pages. All annex forms and their continuations are accounted
for in `page_inventory.json`. PDF160/171/172/174 were also visually inspected. This
closes the annex text-screening gap, not full extraction or full-image review.

The cumulative page ledger now leaves **76 index-only pages**. Existing source status
remains in progress. No SRC, EV, acquisition queue, analytical table, review decision,
progress stage or generated JSON changed. T3/T6 and operational extraction remain out
of scope. No new discovery or independent source vote is claimed.

## T4 findings

**Variable use:** Form3 requests water pH/salinity/temperature and soil salinity/
temperature/aerobic-layer depth, plus a count of soil cores. This is an assessment
measurement protocol, not proof that a suitability model uses these variables. No
weights, class scores, response directions or calibration are supplied.

**Species choice:** Form1A explicitly recommends avoiding invasive species and species
absent from local healthy mangrove patches (PDF160). This is locally referenced planting
composition guidance, retained in the inventory, not a whole-site hard exclusion. Its
nearest-reference stratum supplies no distance cutoff. The taxonomic lists in the four
flora sheets and the identification key are not species tolerance envelopes.

**Numeric calibration:** none recovered. Transect width/length, suggested sampling share,
three repeated measurements, ten randomly selected seedlings and example nursery
counts describe field methods or bookkeeping. They must not become minimum restoration
areas, planting densities, establishment limits, measured survival rates or effect units.

## Source inconsistencies

1. Form5 item1.d asks for **soil pH** and points to Form3 (PDF174). Form3 places its sole
   pH column under **Water** (PDF171). Visual inspection confirms the grouping. Both
   statements are retained; no silent water-to-soil mapping or inferred missing column.
2. Form3 instructions finish with “Method of approved analysis is as follows:” (PDF172),
   but no method follows before Form4 (PDF173). The visually checked page is blank below
   that instruction. No analysis method or salinity unit is inferred.

The guide's measurement vocabulary remains distinct from VONT: water/soil temperature
is not mean annual air temperature; aerobic-layer depth is not depth to bedrock; salinity
cannot silently become soil electrical conductivity. Form2's settlement and ownership
fields establish neither a statutory mask nor a measured operational-risk relationship.

## Coverage accounting

- Annex1, PDF150–154: germination biology and four figure captions; nursery identification.
  Germination drawings were not digitised or interpreted as environmental envelopes.
- Form1A, PDF156–160: all four flora sheets, added-species instruction, strata, sampling
  and density example. Literal botanical spellings remain in native anchors.
- Form1B, PDF161–169: eight fauna sheets and instructions; blank survey records.
- Forms2/3/4, PDF170–173: threats, environmental measurements and nursery bookkeeping.
- Form5, PDF174–178: all eleven checklist items, seven planning categories, plot details,
  scheduling and authorization; no completed project data.
- Form6, PDF179: seedling baseline morphology and sampling.
- Annex3, PDF180–181: twenty numbered identification couplets; no taxonomic repair.
- PDF182–186: acknowledgements. PDF187–194: sparse back matter/contact text; image-only
  content has not been excluded through exhaustive visual review.

Historical inventories remain unchanged; `page_coverage.json` is a new cumulative
snapshot for this source. The earlier mudflat contradiction and species-triangle image
hold remain unresolved. The next substantive gap is the unreviewed ecological section,
not another pass over these blank annex forms.

## Validation and retrospective

All 45 pages have a disposition and exact native text; six selected claims match their
PDF page anchors. Four rendered-page hashes record visual checks. PDF hash recorded;
remaining-page count reconciles with the previous coverage snapshot. No executable
code or evidence was changed, so full schema regeneration and an extraction-sweep
metric would add no validation of this bounded document assessment.

Coordinating-agent adversarial review checked model-use versus measurement, proxy
substitution, species versus practice scope and numeric provenance. Existing rules
cover the findings; no new defect class or ruleset change is asserted. Human approvals
and global feedback-learning cursor remain untouched.
