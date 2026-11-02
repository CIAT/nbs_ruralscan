# Stanturf et al. (2014): independent T4 extraction review

Source: *Contemporary forest restoration: A review emphasizing function*, Forest Ecology and Management 331, 292–323. Supplied 32-page PDF. Native page + 291 = journal page. Date 2026-11-02, extraction ruleset v1.9.2 and T4 review contract v1.6.16.

## Outcome

One unapproved candidate staged: `ev_fr_regeneration_stanturf_function_2014_20261102`, native page 3 / journal 294, for `forest_restoration__passive_regeneration × regeneration_potential`. This is secondary evidence attributed to Benjamin, Domon and Bouchard (2005), not an independent trial by Stanturf. The explicit passive-recolonization sentence resolves the family ambiguity left by the IUFRO conclusion. Appropriate naturally dispersed source plants favour recovery; the passage also names initial seral-species composition as a co-limiter. No distance, density, score, weight, or executable response function is justified.

The direction `increasing` describes increasing effective regeneration capacity/source availability, not increasing distance to source plants. The card context states this explicitly. `regeneration_potential` remains a pending-review ontology entry; it is not FMNR living rootstock. The quote retains the full paragraph contrasting active, passive and hybrid reconstruction, while the supplementary exact excerpt isolates the passive statement. Neither the hybrid approach nor the active soil treatments are being assigned to this family.

No existing SRC entry matched Benjamin, Domon or Bouchard in the read-only lookup. `lineage_of` and `attribution` preserve the full title/citation from native page 23. No DOI was guessed. The cited primary has not been read in this batch, so no primary country or experimental result is imported. Source identity, acquisition, index and central admission were subsequently completed by the orchestrator; see README.md and central_validation.json. No register, git or human-approval writes were made.

## Coverage

All 32 native pages are accounted for: substantive main text on 1–22 read, including references beginning on 22; pages 23–32 screened as bibliography, not treated as primary evidence. Tables 1 and 2, every continuation, and all 16 figures were inspected. Page images checked at native 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16 and 18. Renders are in this staging directory. MuPDF emitted structure-tree warnings while rendering; images rendered successfully and relevant text/labels were visually legible.

- `table1_rows.json`: 57 operation/method rows spanning native 4–6. The first page-6 text continues the preceding row's references, not a new criterion. Repeated operations under different objectives are retained, not counted as independent evidence.
- `table2_cells.json`: all nine initial-prescription cells, three degradation states × three landscape positions, native 8. Longleaf-pine ecosystem prescriptions are species/region-specific, not general forest-restoration suitability classes.
- `table_page_text.json`: complete native text for the table pages, preserving parent headers, conditions, citations and continuations alongside normalized row inventories.
- `figures.json`: 16 figures, locators and source captions/context; all images inspected. Schematics describe treatment choices, not suitability colours or weights.
- `claim_inventory.json`: 33 substantive claim/value groups, with directions, values, locators and holds/referrals.
- `page_coverage.json`: page-level dispositions and image coverage.

Counts: one staged qualitative family-resolved candidate; zero newly demonstrated practice-level suitability calculations; zero executable calibrated functions. No independent-study count is claimed. Species-level design use is separately documented for the Alabama Pinus palustris example (native 16).

## Findings that must survive central admission

### Seed supply: family ambiguity resolved, independent lineage still required

Native 3 §2.2 explicitly says passive approaches rely on recolonization of open land by natural dispersal and can be limited by proximity to appropriate source plants and initial seral composition. This supports the staged family assignment without defaulting all natural regeneration to passive. Benjamin et al. (2005) remains the cited-primary lineage. WRI and IUFRO material cannot be counted as additional independent empirical validation merely because the wording is compatible.

Native 12 gives an important, more specific value: a dispersed planting scheme under the southern-US Wetlands Reserve Program used widely spaced, heavy-seeded Quercus plantings and expected light-seeded species to fill in. The authors say success was only where intact stands were nearby, generally within 100 m, citing Stanturf (2001, 2009) and Nuttle and Haefner (2005). Retain 100 m in the raw inventory; do not lose it because calibration is incomplete. It is not a universal passive-regeneration `abs_max`, nor a no-planting ANR criterion. The method is a hybrid planting/infill design, and “generally” does not establish an absolute boundary. Fig.10B likewise shows natural regeneration adjacent to existing forest within effective dispersal distance with planting elsewhere; it is contextual corroboration, not another study.

### Competition: a clear ANR mechanism, but no exact ontology entry

Native 13 explains that desirable overstory species may be producing seed but new seedlings cannot establish through dense competing groundcover/understory. It then defines ANR as mechanically controlling competitors around desirable seedlings by cutting or matting, citing Hardwick (1997), Friday (1999), and Shono (2007). This is stronger and more family-specific than the generic IUFRO competition statement.

Retain a negative competition-pressure direction and the treatment-response mechanism. No matching competition-pressure variable/metric exists in the reviewed VONT. Do not substitute NDVI, canopy cover, land-cover class, regeneration potential, or “invasive presence” for the raw property. Native/invasive status is not identical to competition intensity. Native 13's labour, repeated-growing-season treatment and small-area/resource qualifications are implementation feasibility, not a hard ecological area limit.

### Grazing/herbivory: do not force a general practice criterion

The source's clear herbivory passages concern underplanted light-demanding Quercus (native 13, Dey 2012) and undesirable species-composition legacies (native 16, Nuttle 2013). Table 1 includes fencing/pressure removal as operations. These do not establish a generic livestock-density threshold for passive forest regeneration. Retain species/context and exact metric holds; no proxy map or new structural unit is recommended.

### Light, soil and fire directions are conditional

Native 13 explicitly balances too little light against excess light favouring competitors and exposing seedlings to high temperatures, inadequate soil moisture, evaporative demand and frost. This is a species/treatment-dependent tradeoff, not globally increasing suitability with canopy removal.

Native 10 describes soil fertility, pH, symbionts and seasonal outplanting moisture/temperature; native 16 notes that residual agricultural fertility/pH can favour invasive plants. No generic monotonic soil-fertility or pH response is justified. SOM amelioration is not interchangeable with soil organic carbon. Soil-moisture timing is not annual rainfall.

Native 17 explains both necessary fire in fire-adapted ecosystems and damage from altered fire regimes. Fire frequency, severity and regime must remain distinct; one global fire-hazard decline rule would discard this context. Fire-duff and burn-interval numbers are examples, not establishment thresholds.

### Two image-only or misparsed numerical traps

1. Native 18 / journal 309 says mangrove forests are inundated **≤30% of the time** by tidal waters, citing Lewis (2005). Native PDF text yields `630%`. Page image confirms the inequality and value. Retain image-verification provenance and the raw text discrepancy; do not silently rewrite the artifact or emit 630%. This cited ecological statement is not yet a calibrated hard exclusion: primary review, time basis, mangrove-family semantics and applicability are unresolved. “Modifying slope ... to appropriate height above mean sea level” concerns landform/elevation adjustment, not a slope-angle cutoff.
2. Figure 14, native 15, has image-only **100%, 75%, 40%, 15% retention** under aggregated and dispersed arrangements. These are illustrative harvest-retention levels, not high/medium/low suitability scores, land-cover eligibility thresholds or optimum retention. Values are preserved in both figure and claim inventories.

### Species and design values retained without practice transfer

Table 2's moderate/very/severe degradation states and xeric/sub-xeric sandhills, flatwoods/wet lowlands, and montane/mesic uplands govern Pinus palustris restoration before summer burning in the southeastern USA, adapted from Brockway (2005). Aristida stricta establishment appears in severe prescriptions. This is species/ecosystem treatment logic, not a universal forest-restoration envelope.

Other retained values include cutting/whip/pole sizes (native 7), shale depth and stand age (Fig.3), Larix migration 200 km (Fig.4), 20–30 framework species (native 11), often <5 ha FMNR farms (native 12), and 1/4/50-year fire intervals for 90-year-old Pinus palustris stands (Fig.16). None defines broad practice suitability. The paper's named species-climate maps, Target Plant Concept and planting-stock requirements belong to species selection or Module 6.

### Remaining non-T4 content is visible

Thinning, deadwood, habitat and biodiversity mechanisms (native 14–16), drought resistance (native 19), mangrove/riparian hydrology (native 17–18), monitoring indicators/tools (native 20), and financial/social/tenure material (native 21–22) remain explicit effect, species, operational or M6 pointers. The GIS examples on native 21 prioritize benefits/resources; they are not evidence that this review ran a T4 suitability calculation. No T3/T6 extraction was performed in this lane.

## Validation and remaining approval question

`EvidenceUnit` construction and `validate_units` passed with no violations. Main and supplementary quotes are exact substrings of native page 3 and page 3 was visually checked. These checks do not replace orchestrator provenance/identity/index and central guardrails. The staged row is `reviewer_ok=false`, v1.9.2, with no numeric shape parameters.

Recommended review question: retain the explicitly passive, source-proximity/seral-composition criterion as qualitative regeneration evidence with Benjamin (2005) attribution and unresolved numerical calibration? Approval would retain evidence, not approve a distance threshold or universal transfer. No approval has been granted by this reviewer.
