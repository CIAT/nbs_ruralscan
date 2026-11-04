# Independent FAO drylands chapter-4 scope/intake review

Date: 2026-11-04. Source: `fao_fp175_drylands_restoration_2015`. Authorized main-paper PDF pages 63–81 only; p82 is blank. Read all authorized native pages, opening pp1–4 and authorship/method pp11–13. Inspected rendered p72 from the parallel inventory. Extraction ruleset v1.9.4 and T4 contract apply. No source registration, evidence ingestion or reviewer approval performed here.

## Intake

`pdf_title_error` returns None; queue title-only identity gate returns None. The actual opening title, authors, year and FAO Forestry Paper 175 match the queue. This is the full 172-page document, not a bibliography hit or wrong chapter. ISBN 978-92-5-108912-5. The recommended citation appears on PDF p4.

Local cache and existing team-library PDF are byte-identical: SHA256 `b9321da036f238439e069a0b24a2ede46c3662c68d7969a663e96fc7399dcc88`. Library path is recorded in `intake_checks.json`. The registered publisher URL is on fao.org, redirecting currently to openknowledge.fao.org; both browser retrieval and HTTP request returned 403. This is a current retrieval restriction, not a paywall finding. Original queue records publisher-domain acquisition and the team artifact remains accessible. Do not replace the verified existing PDF with an HTML error response.

Source-specific SRC proposal: `source_kind=grey_lit`, `source_category=grey`, `venue_type=institutional_report`, `method_type=expert`, `region=Global drylands`, no invented country, income group or grid resolution. PDF p11 explicitly describes desk research and two international expert workshops; pp12–13 describe technical/external review. Proposed benchmark medium reflects credible qualitative agency guidance without calibrated establishment evidence; final rubric judgement remains the orchestrator's. Do not label empirical/modelled merely because examples occur. Copyright p4 allows non-commercial reuse with attribution, not blanket CC-BY. Keep source `pending` on promotion; this chapter is not a whole-source sweep.

## PDF72 / printed50: assisted natural regeneration prerequisite

1. **Practice scope:** section heading and definition explicitly establish assisted natural regeneration (ANR), so `forest_restoration__assisted_regeneration` is justified. No default passive-family assignment and no active-planting claim.
2. **Variable use:** the manual recommends retaining natural seed supply as a conditional prerequisite; it does not run a spatial suitability model. A model_use record must say guidance/criterion recommendation, not model use demonstrated.
3. **Canonical variable:** `regeneration_potential` fits natural propagule availability. Do not map live seed trees to `rootstock_presence`: that VONT entry is living-stump/rootstock/FMNR-specific, and M2b policy flags it as feasibility detail. Do not map the count/existence of individual seed trees to `landscape_forest_cover` or nearest `distance_to_forest`.
4. **Direction:** retain categorical support for mature healthy seed trees in or close to the restoration area. No measured monotonic response, optimum shape or calibrated declining curve. A cue supporting a necessary condition does not prove increasing suitability per additional tree or per metre.
5. **Numbers:** preserve the literal 50–100 m in a separate anchored reported-value hold. Its target is closest **seed trees**, species dependent, not forest edge; the source does not name species or provide a universal endpoint. Do not convert into 0.05–0.1 km bounds for distance_to_forest. Do not invent a taxon to make generic species dependence a species-specific EV row.
6. **Lineage:** the numeric recommendation is attributed to Heidelberg et al. (2011). Retain secondary attribution and primary-verification hold. No additional independent vote from FAO and its cited primary.
7. **Routing:** qualitative availability of viable natural propagules can be retained as an unreviewed structural scoping candidate because it selects whether assisted natural regeneration is applicable. The condition of individual seed trees, dispersal distance, stump-shoot management and implementation effort remain feasibility/M6 detail. Do not reactivate all FMNR rootstock rules as T4 from this passage.
8. **Claim wording:** the source states ANR is usually cheaper/more efficient **provided** seed trees exist. Do not claim it proves ANR universally impossible without nearby seed trees; the next sentence also mentions stump shoots. Capture the seed-source qualification without erasing vegetative regeneration alternatives.
9. **Other p72 quantities:** 3–20 years is recovery duration, not rainfall/suitability calibration. Browsing goats/sheep versus cattle/grass removal describes animal-specific management effects; no blanket grazing mask. The West African parkland example is agroforestry, not proof of forest-restoration applicability for all associated claims.

## Independent omission and inappropriate-addition checklist across authorized chapter

| Pages | Material that must be inventoried | Correct treatment |
|---|---|---|
| 63–64 | Stakeholder participation, baseline lists of climate, soil, geomorphology, land cover, biodiversity, socioeconomic capacity | M6/process guidance; listing datasets is not evidence of calibrated variable use in a model. Social barriers are not structural masks. |
| 65 | Low-degradation protection/ANR before planting; runoff hotspots for plant impact; reference ecosystems | Retain strategy-selection rationale as directional/context hold if no current degradation VONT matches. Runoff hotspot is benefit targeting, not proof of establishment feasibility. Do not discard solely because no thresholds; do not force proxy mapping. |
| 66 | Box 4.1 three approach rows; governance requirements | Account protection, ANR and planting rows separately. Box summarizes approaches, not establishment parameters. Governance belongs operational/M6; protection family remains parked. |
| 67–68 | Box 4.2 across-page continuation: wind erosion, soil fertility, rainfall erosion, vegetative strips | Four rows must survive inventory. Dune fixation, farmland strips, fertilizer/yield examples and integrated practices are separate interventions/effects. Acacia albida density 50/ha and manure equivalence are not forest-restoration density suitability. |
| 69–70 | Grazing guidance, rain variability, animal controls; Box 4.3 pastoralist hub | Management and pastoral ecosystem context; do not manufacture livestock thresholds. No blanket exclusion of grazing from all restoration. |
| 71–72 | Integrated fire management and fire-adapted communities | Hazard/asset-resilience management, not a single universal fire-frequency cutoff or zero-fire policy. |
| 72–73 | ANR plus FMNR split | P72 ANR prerequisite above. P73 explicitly farmland FMNR, living stumps/roots/seedbank, rights and enrichment planting; hold outside this forest-restoration batch rather than copying to ANR by section adjacency. |
| 73–74 | Five species-selection criteria: social preference, soil protection/improvement, hydrological balance, biodiversity conservation, economic production | Species-selection/M6 guidance; do not convert generic matching requirements to whole-practice establishment curves or invent species. Economic/social preference routes operational, not T4 core. |
| 75–77 | Native versus invasive species, provenance/genetics, connectivity/diversity, nursery materials and water | Distinguish species/genotype choice and implementation from broad restoration applicability. Connectivity argument chiefly resilience/benefit design; no distance function. Do not infer commercial plantation scope from poplar trial. |
| 78–79 | Plant timing, pit dimensions by texture, density–rainfall rule, assisted watering; Box 4.4 begins | Site preparation and seedling establishment details/M6. 250 mm → 250 plants/ha is illustrative dune-fixation design, not minimum rain for forest restoration. Synthetic mulch exception is not NbS endorsement. |
| 79–81 | Box 4.4 continuation: microcatchments; terraces; macrocatchments; floodwater; fog/condensation devices; treated wastewater; rooftop/courtyard | Account every row, including displaced rooftop row p81. Terrace slopes 4–50%, short <4%, long >0.5% are explicit off-practice numerical holds; not forest-restoration slope calibration. Microcatchment 10–500 m² and macrocatchment 2–200 ha are structures/catchment dimensions, not forest opportunity thresholds. Rooftop remains out of landscape scope. Plastic waterbox device does not authorize synthetic NbS. |
| 81 | Fire, drought, weeds, livestock, termites; pruning/thinning | Implementation and asset risk; retain pointers, not blanket hard ecological masks. |

Chapter case-study references 7–27 and cited works point outside the authorized page slice. Mark them deferred; do not claim the examples have been independently read or the full book swept. There are no calibrated forest-establishment functions in this bounded reading. This does not mean the chapter contains no useful evidence: the qualitative ANR condition and preserved strategy/species/site-management guidance remain useful with correct routing.

## Review status

This review independently establishes intake and source-scope criteria. At the time written, the parallel extractor's final units and claim inventory were not yet present, so no claim is made that those artifacts passed adversarial review. Any final staged unit must still pass native quotation, source, VONT/FAM, context, number and role gates. No human approval granted.

## Provisional six-axis credibility assessment (source-level, not approval)

- Evidence strength: qualitative expert synthesis and illustrative secondary case studies; no chapter-level causal evaluation or calibrated model. Medium/low for numeric transfer; useful for criterion rationale.
- Methodological transparency: p11 identifies desk research and two workshops; pp11–13 name contributors/reviewers. No systematic search, explicit inclusion funnel or claim-level uncertainty framework identified in the authorized chapter. Medium.
- Authority and venue: FAO Forestry Paper, institutional publication with internal and external technical review. High institutional authority, not journal peer review.
- Context and transferability: explicitly global drylands, multiple African/Asian/other examples relevant to LMIC restoration; context-dependent species and moisture conditions limit transfer. Broad relevance does not establish a sampled modal income group.
- Recency: 2015 publication, eleven years before this recovery. Durable restoration principles remain relevant; no current-status assertions inferred. No evidence here establishing `is_seminal`.
- Seminality: not independently assessed in this bounded task; do not stamp from FAO branding or citation count guesses.
- Independence/COI discount: funding/coordination from FAO, Turkish bodies and EU with diverse expert input (pp11–14). No commercial product validation claimed; named commercial devices in Box 4.4 are examples, not independently validated or endorsed by this intake. Broad agency mandate and program examples warrant avoiding inflated performance confidence.

Overall proposed benchmark `medium`: strong authority and context, limited direct empirical calibration. No automatic weight or runtime MCDA effect follows from this assessment.

## Adversarial review of completed staging

Subsequently inspected `inventory/units.json` (one candidate) and all 72 `claims.json` dispositions against the independent chapter read. No missing major criterion, box row or page continuation found. All four Box 4.2 rows and the p81 rooftop continuation are accounted for; explicit terrace and rainfall/density values remain held outside forest-restoration calibration.

The single unit correctly maps assisted regeneration to `regeneration_potential`; `model_use.used=false`, `scoping_candidate`, `reviewer_ok=false`, cited-secondary attribution and 50–100 m reported-value hold are appropriate. Its relationship says seed trees **support** ANR and explicitly forbids an implemented mask or curve. Minor clarification requested from extractor: context should state the condition qualifies cheaper/more-efficient ANR and does not establish impossibility without seed trees; the next sentence retains stump shoots as an alternative contribution. This avoids an overly strong interpretation of the inventory's “prerequisite” wording. No numerical or scope promotion requested.

This is AI semantic/omission review, not human approval or central provenance admission.
