## Common extraction defects (2026-06 learnings — avoid these)

Quote-verbatim does NOT mean the structured fields are faithful. Two adversarial verify
waves found ~34-51% of numeric units defective. Recurring patterns to avoid:

> **⚠ TOP HUMAN-FLAGGED DEFECTS — 2026-08 retrospective (27 QA decisions triaged).** No new
> defect type, but three *existing* ones still dominate the human queue — the checks catch them
> late; you must not produce them in the first place:
> 1. **Study-context extracted as a suitability rule** (`off_scope`/`site_context`, #16). Reviewer
>    verbatim: *"STUDY CONTEXT NOT SUITABILITY!!!! AGAIN!!!"* — a paper's own site rainfall/temp/soil,
>    a figure caption, a "FMNR was done in region X" descriptor is **n=1 context, never a generalising
>    rule.** This is the single most-repeated complaint. If in doubt, DROP it.
> 2. **Table cell with no caption/header** (`insufficient_context`, #14). Reviewer verbatim: *"the table
>    has no caption, I cannot interpret without it."* Quoting an isolated cell is useless — the quote
>    MUST carry the table caption + the row/column header that name what the number is. If you can't
>    get them, flag `insufficient_context`, don't guess.
> 3. **Direction without calibration is retained evidence** (Pete, 2026-10-21; supersedes earlier advice). A supported “higher is better” contributes directional evidence even without cutoffs. Flag numeric calibration as incomplete; do not reject the whole claim. Raw-variable map extrema alone do not establish suitability direction. Follow `../../extraction_contracts/T4_review_contract.md`.



1. **Smuggled numbers** — every value in `relationship` MUST appear in the SAME quote.
   Do not import discount rates, time horizons, study counts (n), I² heterogeneity,
   table-header units, or cross-row range endpoints from elsewhere in the paper.
   (Deterministically caught by `schema_tools/check_numbers.py`.)
2. **Lowest-rank-class misread as exclusion** — in AHP/land-suitability tables, the
   bottom class (score 1 / "Low") is NOT a hard `abs_min`/`abs_max`. Only encode an
   absolute limit when the text says excluded/unsuitable, not merely low-scoring.
3. **Unit-from-quote-only** — if the quoted cell shows "873.60" with the unit in a
   header row not in the quote, do not assert `unit`. Quote the header too, or omit unit.
4. **Proxy ≠ canonical variable** — SOM≠soil_organic_carbon, NDVI≠tree_canopy_cover,
   soil-moisture≠soil_drainage, frost-free-period / LST ≠ mean_annual_temperature. If the
   paper measures a proxy, retain `raw_name` and map only to a semantically matching VONT ID.
   If none exists, retain the claim in the source inventory with an ontology hold. Do not
   choose a merely similar variable or use low confidence to excuse a wrong mapping.
5. **Contiguous single-passage quotes only** — never stitch text across passages/pages
   (fails the page-level guardrail).
6. **Family**: general cross-cutting envelope claims → `agroforestry__cross_family`, not a
   default to F1. Family-specific only when the paper's system is that family.
7. **cited_secondary REQUIRES `attribution`** (whose finding) — synthesis de-dups on it.
8. **Section-scope: a T4 quote must be a SUITABILITY claim** (2026-06-18 — 86% of QA drops
   were `off_scope`). Do NOT extract a `structural_suitability` value from a section that is
   not suitability reasoning: study-site / characteristics tables, methods / study-area
   descriptions, carbon·CO2·biomass accounting, or generic intros / problem statements. A
   verbatim number near a variable name is not a threshold if the section isn't analysing
   suitability. (In an authorised effect lane, actual NbS outcome claims route to `nbs_effect`,
   with XW determining T3/T6 consumers; never relabel effects into T4.) Record `claim_basis` + `selection_justification`; if you can't say
   why it's a suitability claim, don't extract it. Deterministically triaged by
   `schema_tools/check_scope.py`. **Source-scope:** also confirm the paper is about the NbS
   *practice* — a reforestation / forest-restoration / carbon-only paper is not agroforestry
   suitability; scope-flag it at screening rather than mapping its rows to a family.
9. **Quote context — never an isolated cell** (2026-06-18 — ~11% of units were <=10 words).
   The quote must carry the full threshold SENTENCE plus the table caption/header that
   defines the variable & unit. A bare cell ("30-40 pt", "873.60", "5.1-8.5") can't prove
   it's a suitability claim, what the number means, or species-vs-practice scope — and is
   where table-garble / smuggled-unit / species-envelope defects hide. If the value is a
   per-species table row, it's a species envelope (`claim_scope=species`), not a practice
   row. Triaged by `schema_tools/check_quote.py`.
10. **Soft enabling-environment ≠ T4 structural suitability → `wrong_table`** (2026-06-23,
    RE-RATIFIED, reverses 2026-06-22). `market_access`/`accessibility_travel_time` ·
    `market_value_chain` · `tenure_security` · `extension_governance` ·
    `finance_credit_access` · `labour_availability` · `distance_to_road` are **soft,
    investment-addressable** factors → they belong to the **M2b Stream-B operational-risk
    filter + Module-6 next-steps, NOT T4**. Do NOT emit them as `use_role=structural_suitability`.
    Only HARD legal masks (protected areas, water bodies, urban) stay in T4. (~13 such rows
    flagged in 2026-06-23 QA.) Extract with **`use_role=operational_risk`** (the M2b enum
    member, 2026-06-23) — synthesised into a flagged `operational_constraint` recipe section,
    kept OUT of the T4 suitability surface (var_support/selection use structural only).
11. **Wrong practice ≠ agroforestry → `wrong_practice`** (PICOS, deterministically caught by
    `schema_tools/check_picos.py`). Reforestation, afforestation, pure forestry/plantation,
    "climate-smart agriculture"/CSA umbrella, generic forest restoration are NOT agroforestry.
    The practice must be EVIDENCED in the source — don't borrow the AF tag from the sweep's
    focus, a demo dataset, or a file title. No AF/silvo signal in the source → blank `nbs_id`.
12. **Capture the relationship — don't drop the curve → `relationship_missed`** (2026-06-23).
    When a source gives a suitability *relationship* (membership curve, monotonic decline with
    distance, "very high = fine texture, high = fine-to-coarse", a min/opt/max band), that
    directionality IS the evidence — encode it in `relationship`. Capturing the variable name
    but losing the curve is a BIG miss (singh26: distance/precip/MAT/slope/soil-texture/
    soil-drainage relationships all dropped). Read the membership/classification logic.
13. **Speculation ≠ evidence → `speculative_evidence`** ("may still deter", "could
    potentially", "we assume", "is a reflection", hand-wavy assumed causation — not measured
    or used in the analysis). **Values that give no usable rule → `unusable_value`**
    (2026-07, was `uninterpretable_weight`): a bare "5" is uninterpretable ("5 out of what?") —
    the quote/`attribution` must carry the scale (e.g. "0–10", "region-specific HUC default") and
    what is weighted; land_cover with no class list (which classes in/out) is likewise
    unreviewable (deterministically flagged by `check_scope.py` `land_cover_no_classes`). **No caption/context, or a
    failed table screengrab → `insufficient_context`**: flag for the human, don't guess.
14. **Constrained-AOI framing → `constrained_aoi`** (2026-06-24, general principle). A source
    that scopes the NbS onto a *subset* of land **understates where the NbS is actually
    feasible** and misrepresents the opportunity-space extent. Classic case: **land-capability
    / land-use-capacity classifications** (USDA-LCC-style, e.g. INAB Guatemala) that assign
    agroforestry as a **residual / "marginal land"** bucket — what's left after prime
    agriculture and protection forest. Agroforestry is *also* feasible on good land, so the
    source's thresholds describe "where it was *allocated*", not "where it *can go*". This is a
    FRAMING bias of an otherwise on-topic source (distinct from `off_scope`, which is the wrong
    section, and `wrong_practice`, which is the wrong NbS). **Down-weight; NEVER use such a
    source to set the AOI / opportunity-space extent or a global threshold** — at most a
    qualitative, region-flagged vote (`claim_basis=expert_assertion`). Watch for it in any
    land-allocation / capability / zoning scheme.
15. **Species-specific evidence → TAG + KEEP, never drop → `species_envelope`** (2026-07). A
    per-species / per-cultivar claim is real evidence — it is NOT deleted, it is **routed**. Set
    **`claim_scope=species_specific`** (or `crop_specific`) **+ a `taxon`** (e.g. `Faidherbia
    albida`); `synthesis.py` then keeps it OUT of the practice-level T4 suitability surface but
    RETAINS it in the register for a future species-level layer. **crop vs species (2026-07):
    `crop_specific` = a CULTIVATED cash/food crop** (coffee, cocoa, mulberry, banana, citrus,
    groundnut, cereals, cultivated food trees e.g. breadfruit/Tahitian-chestnut/tropical-almond);
    **`species_specific` = a tree grown for timber/service/fodder OR a wild-harvested tree even
    if it fruits** (baobab/Adansonia, sandalwood/Santalum, Faidherbia, merbau). The
    product + cultivation decide, NOT tree-vs-not. The defect is the **mis-tag**:
    leaving a species claim as `claim_scope=practice_technology`, so it leaks into practice
    suitability (12 of 29 July `species_envelope` drops were this). **The article title /
    citation (and abstract, where available) is itself a signal** — a source titled for one
    species is likely species-specific throughout; scope-flag it at screening. On QA, the fix
    for such a row is to **retag (claim_scope + taxon) and KEEP — reviewers must not drop it.**
    Deterministically triaged by `schema_tools/check_species.py` (quote/citation names a taxon
    but claim_scope=practice_technology).
16. **A single study's SITE CONTEXT is not a suitability RULE → `site_context`** (2026-07; the
    #1 recurring reviewer complaint — sharpens #8 from "wrong section" to "wrong *kind of
    claim*"). A `structural_suitability` unit must encode a **rule that GENERALISES** — a
    threshold / range / gradient / requirement / comparison across suitable-vs-unsuitable land
    ("FMNR needs living stumps"; "grows better on sandier soils"; "suitable 250–600 mm"). A
    lone report of the STUDY'S OWN LOCATION is **n=1 context** — it answers *"where did you
    work?"*, not *"where does the practice work?"* — and must NOT be extracted as suitability.
    The tell: "the study area is 900 mm / 28 °C / Lixisol / 30 trees·ha⁻¹", a figure caption
    ("Extended Figure 1: counts for croplands >300 mm"), or a region descriptor ("the Sahel
    covers 320 000 km²… arid ecosystems, 200–600 mm"). **A range or a number in the sentence
    does NOT make it a rule** — a context sentence routinely states the region's rainfall
    band; the FRAMING (study/figure/region) is what disqualifies it. **"Constrain by observed
    distribution" does NOT license this**: that principle is a *run-time DATASET-gating layer*
    (mask by a MapSPAM / EO host-distribution map, chosen via BIND), **not** a licence to
    encode one paper's site measurement as a T4 threshold. If a value is only a single-site
    observation, retain it as source context rather than a suitability rule. Actual
    NbS outcomes may enter an authorised effect lane; do not hard-delete existing evidence. Deterministically
    triaged by `schema_tools/check_scope.py` `site_context` (frame/occurrence − criterion −
    generalisation; tuned to 6/6 of the 2026-07 FMNR site-context drops, 0 rule false-positives).
17. **Preserve the reported relationship before compiling.** For an explicit envelope,
    use `abs_min`, `opt_low`, `opt_high`, `abs_max` and source unit. Do not reinterpret low
    suitability as exclusion or complete a missing class during extraction. Preserve ordinal
    classes, category labels, interval closure, source scores and literal units in the supported
    relationship/report-value structures; categorical evidence is not discarded as prose.
    Supported direction without numbers remains direction evidence. Compilation/harmonisation
    applies documented conventions separately and carries evidence IDs and assumptions.
    Unknown encodings require a visible hold, never silent loss. See T4 review contract.
18. **SLICE quotes programmatically from `page.get_text()` — never retype them** (2026-09
    riparian sweep). The verbatim guardrail verifies against the SAME text layer, so a quote
    built by slicing the page string (whitespace collapsed, line-break hyphens re-joined —
    both no-ops under `_norm`; ligatures ﬁ/ﬀ kept as-is) passes by construction. Retyped
    quotes silently normalise glyphs and die at the gate. Corollary: **two-column PDFs can
    interleave columns in the text layer** — if a claim's sentence does not survive
    contiguously in `page.get_text()`, the text-only gate cannot verify it. Preserve a
    page/image locator and a pending image-verification item, rather than losing the claim
    or forcing a stitched quote. Page-spanning claims need separate anchored excerpts and
    continuation accounting. The staging gate does not pretend to verify image-only cells.

19. **Do not let the quote SPAN open on a trend / study-site clause -> `span_bleed`** (2026-09
    forest-restoration sweep). A span that starts a sentence or two before the criterion
    ("forest cover increased in the landscape... To generate the regeneration potential, this
    radius of 5 km was maintained") trips `check_scope` on the OPENING clause and gets
    auto-quarantined, even though the rule it carries is sound. Start the slice AT the
    criterion sentence; include the mechanism only if it sits inside the same span. Detected
    deterministically: `check_scope` now emits the advisory `span_bleed` (carrying the
    original signal in `section_signal`) when a section signal fires but the quote also
    contains explicit decision language, and `quarantine.py` does NOT auto-drop it -- the
    reviewer RE-SLICES instead of dropping. **The narrowness is the point**: a quantified
    RESULT with no decision language ("98.1% of cells ... occur within 300 m of a forest
    edge") is not a span bleed, stays hard-flagged, and needs a human to judge whether a
    measured result may stand as a suitability claim at all.

20. **Numbers in explanatory TEXT count too -> `smuggled_number`** (2026-09 deep pass). The
    number-provenance rule covers every number anywhere in `relationship`, including inside
    `direction`, `scale` and `weight_scale` strings. Glosses are where smuggling now hides:
    significance levels copied from a table footnote outside the span ("p<0.05"), a weight
    range from another sentence ("weights ranged 1 to 1.5"), a value the paper writes in
    words ("one hundred and fifty metres" glossed as "150 m"), even publication years in a
    cross-reference ("agreeing with Karimi 2019"). Eleven units in the deep pass tripped
    `check_numbers` this way and pushed `numberprov_rate_pct` UP for the first time in
    seven sweeps. Keep glosses number-free unless the number is verbatim inside the quote;
    cite other sources by author, not year. The staging checker now reads strings too.

21. **Fixed-form practice databases (WOCAT) -> `observed_presence`, never thresholds; the header
    travels with the value** (2026-09 round 2; ruleset v1.6.0). A WOCAT technology sheet's
    'Natural environment' ticks say where ONE documented case is applied. Emit them as
    `evidence_type=scoping_candidate`, `claim_basis=expert_assertion`, relationship
    `{"type": "observed_presence", "observed_classes": [...], "observed_min"/"observed_max", "unit"}`,
    NEVER `abs_min`/`abs_max` (#16: one case is not a limit). The engine keeps these out of
    support and threshold synthesis (every sheet carries the same fields, so as votes they are
    100% by construction). Quote the CLIMATE block (header -> rainfall -> agro-climatic zone) or
    the TERRAIN & SOIL block ('Slope' -> last soil field) so the field labels are always in the
    quote (Pete 2026-07: "the table has no caption, I cannot interpret"), and leave the free-text
    'Specifications on climate' prose OUT (it is a site descriptor and trips `study_site`). Put
    the technology name in `justification_quote` and `attribution`. Take the PDF from
    `wocat.net/en/database/technologies/<id>/pdf/` - the legacy qcat `/summary/<id>/` endpoint
    uses a different id scheme and returns the WRONG sheet (caught by the title check).
    **DOI-less sources** (grey literature, WOCAT) may be extracted only when the queue row has
    `title_verified=true` (`verify_metadata.py verify-titles`) and was downloaded from the
    publisher's own domain.

22. **Process metadata NEVER goes in `relationship` -> `context.note`** (2026-10-07 retro). Run
    dates, ruleset stamps, supersession pointers (`superseded_by=…`), review-backlog tags and
    "strength pass" notes are pipeline bookkeeping, not claims; inside `relationship.note` they
    read as smuggled numbers (159 ISO-date + 62 citation-year false flags in the October
    effect rounds). Put them in `context.note` prefixed `process:`. `check_numbers` now ignores
    ISO dates, evidence-id references and the WOCAT adapter's questionnaire references
    (`QT 6.1`, `−3…+3 scale`) wherever they sit, but publication years in a claim still count.

23. **Ex-ante project documents are NOT effect evidence -> `speculative_evidence`** (Pete
    2026-10-01, encoded 2026-10-07). A Project Appraisal Document, proposal, design note or
    results framework states what a project *will* do ("will support…", target values).
    Extract only ex-post MEL (ICR / IEG / PPAR / impact evaluations) for `nbs_effect`; a PAD
    may be registered as a source for T4 scoping context, never for T3/T6. 37 agroforestry
    PAD units were dropped under this code.

24. **A quote is a sentence or a table ROW — never a whole table** (2026-10-12, Pete). Catalogue
    #9 forbids the bare cell; this is the opposite end. Swallowing an entire table hides which
    row the claim came from and lets `check_numbers` pass on numbers belonging to other rows
    (caught on a Malawi food-security unit whose quote was all of Table 2). Quote the row plus
    its header and caption; `check_quote` flags anything over 160 words (320 when the quote
    carries its English translation).

25. **Prefer the primary over the second-hand reading** (2026-10-12, Pete: "use the publications
    referenced not a secondary interpretation"). A `cited_secondary` unit is a pointer, not a
    destination: name the primary in `lineage_of` so `scripts/log-primary-references.py` can put
    it on the acquisition list, and replace the unit once the original is in hand.

26. **`outcome_raw` carries no number the quote does not** (2026-10-13 retro). The number check
    walks the WHOLE `relationship` dict, so a study descriptor written into `outcome_raw` —
    buffer width, exceedance probability, project length, bank height, a comparator figure
    quoted from elsewhere in the paper — flags exactly like a smuggled magnitude, and real
    smuggling then hides in the noise. The riparian/wetland round passed its own staging gate
    and the next build flagged 23% of its units this way, all descriptors. `outcome_raw` says
    WHAT was measured and against what; the descriptor goes in `context.note`, which is not a
    claim surface (same split as #22). Number WORDS count too ("ten per cent" is 10), so
    rewording round a digit does not help. The staging gate now runs the same whole-dict check
    as `check_numbers`, so a lane cannot pass a file the build will flag.

27. **A decaying service is not a harm** (2026-10-16 retro). "Sediment retention diminishing
    after 10 years" was encoded `direction = negative` on an erosion variable and made a row
    read "wetland management INCREASES erosion risk" — but the source measured a trapping
    SERVICE weakening with age, not the practice adding erosion to anyone's land. Encode a
    weakening benefit as what it is: the service variable with the decay stated in
    `outcome_raw` (and a `timescale_of_effect`), never as the opposite harm. The same trap
    exists for "removal efficiency declined", "protection weakened", "survival fell over
    time". If the outcome the cell asks about was never measured, the unit does not belong
    in that cell.

28. **A baseline is not an effect** (2026-10-16 retro; extends #23). A baseline survey
    reports treatment and comparison areas BEFORE the intervention does anything, so its
    treatment-vs-comparison differences are sampling design, not effects — a "no difference
    at baseline" must not enter an effect cell as a null vote. Extract baseline documents
    only for context (and for the later endline's lineage); the endline carries the effect.

29. **A spread is not a sign → `unusable_value`** (2026-10-19 retro). A range of cost (or
    outcome) estimates across implementers, sites or methods — "rehabilitation cost varied
    from X to Y depending on the agency" — is DISPERSION, not a direction. One such unit was
    encoded `direction = positive` on a cost variable and read as "the practice increases
    costs". If the quote states only a spread, leave `direction = none` and put the range in
    `economic_value_range` (gates permitting) or `outcome_raw`; a direction needs a stated
    comparison or trend, not a min and a max.

30. **An annualised establishment cost is not a recurrent cost** (2026-10-19 retro). Route a
    cost by WHAT THE MONEY BUYS — initial works vs ongoing maintenance — never by its
    denominator alone. A paper that annualises capital restoration cost over a horizon
    ("$ ha−1 y−1, cost divided by years") still reports an ESTABLISHMENT cost; the usd_per_ha_yr
    unit must not push it into the recurrent-cost cell. Recurrent = the paper names ongoing
    operations (monitoring, maintenance, replanting share); say which in `outcome_raw`.

31. **A tillage implement is not a capture structure** (2026-10-21, Pete ripping ruling A).
    Ripping / rip lines, zero and minimum tillage are reduced tillage — NOT water harvesting
    (ruling 2), even where a paper calls conservation farming "a water harvesting strategy".
    Capture structures are basins, pits, zai, tied ridges, bunds, half-moons. A pooled arm
    that cannot separate basins from ripping is ingested `attribution=bundled` with tillage as
    a co-practice; ripping-alone and no-tillage-labelled arms yield NO water-harvesting unit.
    Never let a lane brief decide a practice-boundary question — raise it for a ruling.

32. **Second-hand readings drift; the primary wins** (2026-10-21 retro, extends #25). Three
    of Arslan 2015's cited findings misstated their primaries (a significant reversal
    reported as "no benefit", a vanished effect that never existed, a budget on the wrong
    baseline). When a primary is acquired, list the second-hand units it supersedes; the
    orchestrator drops them with the primary named in the reason.

The trustworthy gates are CENTRAL: the verbatim+page guardrail (`validate_sources.py`),
`check_numbers.py`, `check_scope.py`, `check_quote.py`, `check_picos.py` (wrong-practice),
`check_species.py` (species mis-tag), `quarantine.py` (auto-soft-deletes off-scope +
wrong-practice on build, reversible), and the adversarial relationship-verify. A subagent's
own self-check is advisory — do not rely on it. After a sweep, the learning loop is only
honest if feedback is incorporated: `learnings.py` tracks `review_log` vs adjustments and
the build flags unprocessed review decisions (run `/sweep-retro` → encode → `learnings.record`).

## T4 completeness recovery (v1.6.14)

31. Inventory each source table before extraction: list variables, class counts, pages and image-only cells. Read the following page for continuations; preserve separate page quotes and explicit continuation links. A successfully retrieved paragraph does not establish table completeness.
32. Reconcile every scoping-review paper to SRC and an explicit disposition. Track human table/figure/missing-data flags by evidence ID and exact note until resolved; never infer closure from reviewer_ok.
33. Check approved numeric class payloads against executable T4. Unknown encodings must fail coverage or carry an explicit hold, never silently become qualitative. Image-read model weights retain page, image checksum and human-review status; weights are not suitability thresholds.

Enforcement: schema_tools.t4_coverage in CI; numeric compiler checks expected class counts and continuation compatibility. Inventory checks detect regression in documented tables, not every unknown omission in a PDF.


## Main-paper extraction accounting (v1.6.15)

34. **Screening is not extraction.** Before calling a source swept, account for its pages, tables, figures and referenced supplements in a claim inventory. Each relevant claim needs an EV ID or an explicit destination/exclusion reason with page and retained values. A zero-T4 paper still requires this accounting. Distinguish completed main-paper extraction from deferred supplemental datasets; never infer completion from SRC presence or zero admitted thresholds. Check expected EV IDs and routes in CI.
35. **Species-selection use is not practice-level agreement.** A tool may use rainfall/pH to select species without calibrating an agroforestry establishment curve. Retain method-use evidence as dataset records with `context.model_use.scope=species_selection`; count separately from practice-level and named-species/crop calibrations. Do not invent a taxon for generic query logic. Preserve restoration-priority weights outside suitability even when the paper calls its result suitable.


## Complete directional evidence and review (v1.6.16)

36. **Weight-only extraction is incomplete when the table also gives direction.** Read and apply [T4 extraction and adversarial review contract](../../extraction_contracts/T4_review_contract.md) before extraction or verification. Assess variable use, suitability direction and numeric calibration independently; inventory every table row. Existing records do not justify skipping missing supported dimensions. Reviewers check omissions as well as invented values. Direction-only evidence remains non-executable until calibration is supported.


## Direction on the variable as named (v1.6.17)

37. **Direction is the movement of the variable as NAMED, with its verbatim cue** (2026-10-23, Pete: a
    unit "reduced erosion … commonly documented" showed `erosion_hazard · negative`, which reads as
    "bad"). The coding was right (erosion went down) but nothing made that checkable, and the habit of
    thinking "benefit = positive" flips hazard, cost and deficit variables. Before coding, read the
    variable's row in `schema/lookups/variable_direction_sense.csv`; state "<variable> went up / down
    according to '<cue>'"; then emit `relationship.direction` AND `relationship.direction_cue` (the
    shortest verbatim phrase carrying the movement, sliced from the quote). `check_direction.py` flags a
    missing or non-verbatim cue and a cue that moves the other way; the build fails if an effect variable
    has no sense row or a crosswalk polarity disagrees with it. Full rule:
    `.agents/skills/extraction_contracts/DIRECTION_ADDENDUM.md`.

38. **A season is not a hazard; a mimic is not the practice** (2026-10-23 AF fix round, Pete).
    Three recurring T3 mis-tags, each pivotal in a roll-up: (a) an ordinary DRY SEASON ("saison
    sèche", "época seca", "estío") is not a drought — leave `context.hazard_type` blank unless the
    source names a drought / deficit year / El Niño event; the unit stays as T6 evidence. (b)
    General shade or wind-speed benefit with no event (cattle shade, winter desiccation behind a
    windbreak) is not heat-stress or storm mitigation — no `hazard_type`. (c) An experiment that
    MIMICS the practice (artificial shade nets for shade trees) is not the practice: PICOS fails
    on I, do not extract (or drop `wrong_practice`). Also: a bundled programme in which the NbS is
    only "an option in some communities" is a marginal component — exclude, don't discount.

39. **No mechanism, no unit** (Pete 2026-10-24). An effect unit must state HOW the practice changes
    the outcome — a physical or economic pathway through THIS practice (bunds hold runoff → soil
    moisture; regenerated trees → fodder; less ploughing → labour saved; sediment trapped behind
    the structure). A bare rating, a restated rating ("improved", "increased"), an observation
    with no cause, credit to another practice (tree nurseries enabled by sand dams) or an invalid
    pathway (harvested annual-crop CO2 uptake counted as storage) is not evidence of an effect.
    The WOCAT adapter now skips every impact rating without a compiler comment
    (`wocat_impact_map.csv requires_comment = true`), and a commented rating still needs the
    mechanism check before it is registered. Applied retroactively: 438 bare WOCAT ratings and
    the commented ones that failed the check were soft-dropped (reviewer `ai_mechanism_rule`).


## Pipeline integrity (v1.7.0)

40. **Acquired is not extracted, and a record is not coverage.** Source promotion starts
    `pending`. A completed source inventory must account for all relevant rows, continuations,
    figures and supplements before `swept`; no automatic completion from SRC/EV presence.
41. **Identity and locators precede payload checks.** New staged evidence requires a registered
    source, matching verified queue identity, a non-empty quote, a positive integer PDF page
    or supported snapshot locator, correct family/NbS, and no self-granted review approval.
    Page zero, wrong-paper caches and changed duplicate IDs are errors, not skips.
42. **Search metadata describes the search that ran.** Supply the actual ruleset/date, preserve
    complete queries and exact table tags. Counts before queue deduplication differ from newly
    acquired sources. A candidate labelled paywalled is not proof of exhaustive OA recovery.
43. **Reviewer feedback is content, not a row count.** Changed notes/decisions on an existing
    evidence × reviewer pair must reopen learning work. Only record a full retrospective
    after reading its complete feedback set; a partial audit must not advance the whole cursor.
44. **Make weights reviewable.** Retain original weight, method, scale, complete parent criterion
    set, branch/depth and source locator. A derived global weight must show multiplication and
    denominator. Relative-to-equal-share importance is computed only for a complete comparable
    criterion set. Do not combine topsoil/subsoil or parent/child weights by silently summing.
    Consolidation is an explicit synthesis decision; preserve raw distinctions for audit.

Body-only title matches may be bibliography entries. Hold for explicit chapter identity review; never mark a whole PDF verified because it cites the wanted paper. Code sources must resolve to immutable commits and retain distinct artifact identities per repository/path/revision.


## Adversarial pipeline checks — v1.8.0 (2026-10-28)

45. **Metadata identity is not artifact identity.** A verified DOI cannot validate an unrelated
PDF. Match the opening title before cache publication, source promotion and staged ingestion.
Keep scans/chapters as explicit identity holds; never relabel the failure as paywalled.
46. **Translation and supplementary text cannot manufacture provenance.** The native quote
must be a substantive source anchor. Verify rationale/selection quotations on their own pages;
an empty native substring or a translated-only claim cannot pass.
47. **Portable typed evidence.** Reject duplicate JSON keys, NaN/infinity, Boolean numeric
parameters and non-string IDs. Invalid later rows cannot partly append an earlier batch.
48. **Duplicate identity is not duplicate work.** Rediscovery in a new NbS/table/family
requires tracked reuse, not deletion as redundant. Preserve canonical source identity and
independent-study counts. Existing pipe-delimited NbS scopes are exact tokens, not substrings.
49. **Compilation cannot reassign scope.** Target family and crop must match admitted evidence;
dropped records remain excluded even through lower-level APIs. Ambiguous/cyclic lineage is a
hold. Unit conversion cannot merge distinct breakpoints or pool unlike native units.

These checks harden existing evidence rules; they grant no new ecological transfer, human
approval, class completion, aggregation policy or runtime weights. See the adversarial audit.

## Operational-risk (M2b) evidence — Pete's review 2026-10-22/23

50. **An operational-risk unit names a factor that limits or enables implementation, with
cause and effect in the quote.** From Pete's review of the operational units (2026-10-22/23,
41 drops):
- `adoption_rate` is an outcome of the enabling environment, not an operational-risk factor.
  Never emit it as `use_role=operational_risk` (`schema/lookups/m2b_variable_policy.csv`,
  decision `exclude`; the ingest gate refuses it). Record what limits adoption instead
  (tenure, labour, finance, extension), when the quote says so.
- Quote the main text, not the abstract: the finding is restated with its conditions in the body.
- Practice-specific implementation detail (rootstock, planting material, restorable patch
  size, grazing regime) is feasibility, not scoping (`flag` in the lookup): leave a deferred
  pointer for Module 6.
- A policy document that mentions a factor, a figure that describes the study context
  (e.g. "85% of farmers hold no title"), or a chain of inference is not evidence that the
  factor limits the practice. The quote must say it does.
- A second-hand claim keeps `claim_basis=cited_secondary` with the original in `lineage_of` (#32).

51. **Significance uses the 5% convention** (Pete 2026-10-29). A result with 0.05 ≤ P < 0.10 is
`significance=ns` even when the authors call it significant at their 10% level; keep its
direction and record the authors' P value and wording in `context.note`. The ns weight
discount applies. Example: Kidane 2019 basin net returns, KS test P = 0.08.
