---
name: "source-command-extract-evidence"
description: "Extract Evidence-Register units for one variable x suitability family from the ingested corpus (T4 method)"
version: "v1.6.16"
---

<!-- ruleset version v1.6.16 — log: methodology/RULESET_VERSIONS.md · snapshots: .agents/skills/_versions/.
     Bump + snapshot on any change to the screening funnel, defect catalogue, or discovery protocol.
     Stamp the version on SRCH.ruleset_version + EV.ruleset_version. -->


# source-command-extract-evidence

Use this skill when the user asks to run the migrated source command `extract-evidence`.

## Command Template

Run the T4 evidence-extraction step (methodology/T4_generation_method.md section 5): turn ingested
source passages into atomic, provenance-bearing Evidence-Register units -- never PDF -> threshold.

Inputs: a canonical variable, a suitability family, optionally a source set (ask if missing).

Workflow:
1. Canonical variable(s) + aliases + min_meaningful_resolution_m from the Variable Ontology; the family
   target spec; tiers from the benchmarked CSV (Source Register).
2. **Coverage check before deduplication**: existing records do not prove a table row is fully extracted. Check variable use, direction, reported values and numeric calibration separately under `../extraction_contracts/T4_review_contract.md`. Only skip a demonstrably complete pair:
     from nbs_ruralscan.recipe.evidence import already_extracted
     # Check for each variable in the set
     existing = already_extracted(sid, variable)
     if existing:
       print(f"SKIP {sid} × {variable} — already extracted: {existing}")
       # skip only if all supported dimensions are already captured; otherwise supplement with provenance
   Report skipped pairs so the user knows what was cached.
3. Ingest + retrieve (deterministic):
     from nbs_ruralscan.ingest import build_index, load_index, save_index
     from nbs_ruralscan.recipe.evidence import package_for_extraction, package_for_extraction_multi, EvidenceUnit, validate_units, save_units
     idx = load_index(sid) or build_index(pdf, source_id=sid)

     # Single variable extraction:
     bundle = package_for_extraction(idx, "slope", aliases=["terrain slope","gradient"])
     
     # Paper-first multi-variable extraction (saves context tokens by bundling):
     vars_spec = [
         {"variable": "slope", "aliases": ["gradient"]},
         {"variable": "annual_precipitation", "aliases": ["rainfall"]},
     ]
     bundle = package_for_extraction_multi(idx, vars_spec)
     
   Work ONLY from bundle["passages"] (page-stamped). Flag needs_ocr_pages; never guess.
4. Emit one EvidenceUnit per atomic claim. For multi-variable extraction, extract all variables in the same pass.
5. validate_units(units) must return {} before save_units(units, path).
6. Report units, conflicts, anything pending (OCR / figure-only).

Hard rules: quote+page mandatory; null when the source is silent (no inference). Tag use_role
(structural_suitability=T4 | operational_risk=M2b Stream-B enabling-env | dataset=T1);
**climate_risk / nbs_effect / priority_need are DEFERRED (2026-09) — do NOT emit them.** T3/T6
were removed from the extraction exercise (over-scoped; see `schema/registers/_deferred/README.md`
for the archive + restore path). Evidence that would have been T3 (hazard mitigation), T6
(effect/cost) or T5 material is simply not extracted — don't relabel it into a live role.
evidence_type (only literature_relationship/expert carry shape params); claim_basis; claim_scope
(species/crop claims need taxon and must NOT define a practice row). Set lineage_of when a value is
cited from another source. Capture exclusion/failure thresholds too. No silent unit harmonisation.

Per-table extraction contracts for the deferred tables (T3/T6) are archived under
[.agents/skills/_versions/v1.4.2/contracts/](file:///Users/pstewarda/Documents/rprojects/nbs_ruralscan/.agents/skills/_versions/v1.4.2/contracts/)
(T5's remains at [.agents/skills/extraction_contracts/T5_contract.md](file:///Users/pstewarda/Documents/rprojects/nbs_ruralscan/.agents/skills/extraction_contracts/T5_contract.md)
but priority_need emission is likewise deferred).

Reference: methodology/examples/t4_slice_agroforestry_F1_slope.md (the gold standard to reproduce).

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
> 3. **Direction without calibration is retained evidence** (Pete, 2026-10-21; supersedes earlier advice). A supported “higher is better” contributes directional evidence even without cutoffs. Flag numeric calibration as incomplete; do not reject the whole claim. Raw-variable map extrema alone do not establish suitability direction. Follow `../extraction_contracts/T4_review_contract.md`.



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
   paper measures a proxy, say so in `raw_name` and pick the closest canonical id with
   `extraction_confidence` lowered — never silently relabel.
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
   suitability. (Carbon/biomass belonged to T6 effects and fuel/biomass to T3 hazard, but
   those tables are deferred — such material is now simply NOT extracted, never relabelled
   into T4.) Record `claim_basis` + `selection_justification`; if you can't say
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
    observation, drop it (genuine outcomes belonged to T6, which is deferred — do not
    extract them). Deterministically
    triaged by `schema_tools/check_scope.py` `site_context` (frame/occurrence − criterion −
    generalisation; tuned to 6/6 of the 2026-07 FMNR site-context drops, 0 rule false-positives).
17. **Relationship shape params MUST use the canonical keys** `abs_min`·`opt_low`·`opt_high`·
    `abs_max` (+ `unit`) — never free-form (`range_min`, `precip_mm_low`, `optimum_low_mm`,
    `sahelian_zone_min`, `low_density_per_ha`…). The T4 synthesiser reads only the canonical
    keys, so a real range under a free-form key is **silently invisible** — the family emits 0
    T4 rows despite genuine consensus (2026-07 FMNR: a rainfall envelope agreed across 7
    sources was lost this way). A range/optimum → `{"abs_min":…, "opt_low":…, "opt_high":…,
    "abs_max":…, "unit":"…"}`; a single floor/ceiling → the one bound; a categorical class is
    not a shape param (leave it descriptive). `recipe.synthesis.normalize_shape_keys` maps the
    common aliases as a safety net, but emit canonical directly.
18. **SLICE quotes programmatically from `page.get_text()` — never retype them** (2026-09
    riparian sweep). The verbatim guardrail verifies against the SAME text layer, so a quote
    built by slicing the page string (whitespace collapsed, line-break hyphens re-joined —
    both no-ops under `_norm`; ligatures ﬁ/ﬀ kept as-is) passes by construction. Retyped
    quotes silently normalise glyphs and die at the gate. Corollary: **two-column PDFs can
    interleave columns in the text layer** — if a claim's sentence does not survive
    contiguously in `page.get_text()`, it CANNOT be quoted; report it as a blocker (with
    page + what it says) instead of forcing a stitched quote (defect #5). A sentence that
    straddles a page break is likewise unquotable.

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

36. **Weight-only extraction is incomplete when the table also gives direction.** Read and apply [T4 extraction and adversarial review contract](../extraction_contracts/T4_review_contract.md) before extraction or verification. Assess variable use, suitability direction and numeric calibration independently; inventory every table row. Existing records do not justify skipping missing supported dimensions. Reviewers check omissions as well as invented values. Direction-only evidence remains non-executable until calibration is supported.


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
    `_versions/v1.6.17/contracts/DIRECTION_ADDENDUM.md`.

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

