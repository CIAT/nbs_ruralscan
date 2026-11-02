# Independent adversarial review: DENR FMB Technical Bulletin 27

Reviewer: independent extraction-review agent. Date: 2026-11-02. Ruleset: v1.9.2; T4 review contract v1.6.16. No human approval granted.

## Verdict

The two staged claims have correct primary image anchors and can remain qualitative, unapproved T4 evidence, subject to the wording corrections and coverage conditions below. No numerical T4 function is supported. This review does not validate source-register publication or ingestion gates, which remain orchestrator responsibilities.

## Checks performed

Read extraction skill, full T4 review contract and defect catalogue; checked VONT and FAM mappings. Visually inspected all 15 rendered pages, with close reading of pages 1–4, 6 and 11–12. Read derivative text pages 4–12. Independently rendered original and derivative at 100 dpi: all 15 pixel buffers were byte-identical and every render hash matched the manifest. Both PDF SHA-256 values matched the manifest. This verifies unchanged images at that rendering resolution, not universal OCR accuracy. Pages 13–15 remain image-only in the derivative; reviewed their content type and headings, not every economic cell.

Opening image page 1 identifies Technical Bulletin No. 27 and the full Procedures and Costings in the Application of Assisted Natural Regeneration title; date stamp is July 1, 2019. Page 2 matches the land-cover quote and its heading. Page 3 matches the complete ideal-site and alternative-treatment quote, including 600–700 wildlings/ha, height 15–200 cm, relatively well spread, below-600 reforestation and above-700 enrichment planting. The unusual above-700 route is genuinely printed; do not reverse or silently correct it.

## Must fix before final reporting

1. **Lineage certainty in both context.note fields.** “Same Philippine ANR guidance lineage as WOCAT Approach 1971” claims established common provenance, while attribution correctly says independent empirical support is not established. This bulletin's reference list does not cite WOCAT. Unless separately documented genealogy proves the stronger statement, use “Overlapping Philippine ANR guidance; independence from WOCAT Approach 1971 remains unresolved; do not count as independent validation.” Preserve the conservative deduplication hold.
2. **Distinguish the source's ANR definition from the registry boundary.** Both practice_as_described fields say optional augmentation planting is a separate intervention. The source includes augmentation within ANR (page 1 definition, page 2 final paragraph, page 6 instructions, page 7 optional-cost row). FAM excludes planting from this project's assisted-regeneration family. State explicitly that the *extraction* isolates liberation/protection of existing regenerants and holds the source's optional planting component outside that family; do not imply the source itself makes that separation.
3. **Coverage conditions before any complete/swept claim.** Add page-linked dispositions for each of the four unextracted section-D bullets and each Annex C taxon. In particular, retaining only the open/degraded-forest bullet cannot stand as complete section-D coverage. Annex C cannot be dismissed wholesale as “species list”: it contains actual environmental-tolerance statements. Explicit species-lane holds are sufficient in this bounded practice-level batch, but those statements must remain retrievable.

## Independent assessments

- **Variable use:** two explicit expert site-selection criteria, not two fitted-model uses. land_cover is categorical host context; regeneration_potential is a broad qualitative mapping to existing regenerants. VONT regeneration_potential itself remains pending_review and categorical. Neither supports a verified spatial model. Preserve this distinction in counts.
- **Direction:** zero resolved directions on the canonical variables. land-cover classes have no monotonic ordering. The source's ideal density range belongs to wildling density, not the categorical regeneration_potential variable. Current unclear values are appropriate; raw ideal-range information is retained in context and must not be lost.
- **Calibration:** zero executable functions. No abs_min/abs_max or opt_low/opt_high, score, weight, interpolation, or general exclusion is justified. Density, height, vigour and spread are joint field criteria. No smuggled density calibration found.
- **Scope/transfer:** Philippines expert guidance, assisted-regeneration subset only. Open/degraded *forest lands* does not authorize conversion of intact natural grasslands or all open land. Protected areas are not automatically eligible against applicable legal masks. No family reassignment from below/above-density treatment suggestions. Human approval remains false.

## Required dispositions and explicit holds

- Page 2 section D bullet 2: protection-forest / watershed-cover development is management purpose; retain a purpose/mapping hold rather than treating it as an EO cover class.
- Page 2 section D bullet 3: national parks, game refuges, nature reserves and similar reservations are actual source eligibility suggestions. Keep a legal-context conflict/transfer hold; neither globally exclude nor globally permit from this passage alone.
- Page 2 section D bullet 4: production forests where ANR is economical/expeditious, including nurse-tree establishment, combine purpose, economics and practice scope. Hold outside general land-cover classes.
- Page 2 section D bullet 5: near/adjacent ecotones is a real spatial criterion. Retain raw criterion with ontology/proximity-definition hold; do not silently replace ecotone with forest edge or assign a distance cutoff.
- Pages 2–3 section F: consultations/claimants, mapping and biophysical assessment are procedural guidance. No numerical climate, soil or terrain rules supplied. Figure 1 is a site illustration of forest patches/seed-source trees, not a quantified forest-distance curve.
- Pages 4–5: weeding, grass suppression, rainy-season timing, rocky-substrate technique adaptation and thinning are implementation instructions. No regional rainfall, soil-depth or rock-fraction threshold follows. Preserve M6 pointers.
- Page 6: firebreak dimensions, greenbreak species, fencing where grazing occurs, rainy-season augmentation, 2 m × 3 m spacing and 3–5-year canopy target are implementation/design content. Do not convert to structural suitability; planting remains family-scope hold. Any effect extraction requires its separately authorized lane.
- Pages 7–8 and 13–15: costs/work rates, references, Annex D with/without augmentation and Annex E May-2019 wage rates are economics/M6 referrals. Image-only economic-table hold is justified. No economic extraction performed.
- Page 9 Annex A: empty monitoring template and stem-quality codes, not observed outcomes or suitability classes.
- Page 10 Annex B: 10 named frequently occurring regenerant examples; occurrence/identification context, not climatic envelopes. Preserve printed nomenclature pending taxonomy checks.
- Page 11 Annex C Acacia auricauliformis (printed spelling): explicit pH as low as 3 on mine sites and as high as 9 on sand. Retain as species-specific reported tolerance/occurrence with those substrate qualifiers; never general ANR pH 3–9, never automatic abs limits. Primary attribution/taxonomy remains unresolved.
- Page 11 Annex C Acacia mangium: explicit low-nutrient, acidic/degraded-soil tolerance; retain species-lane pointer, no practice-level soil calibration.
- Page 12 Annex C Eucalyptus camaldulensis: poor-soil tolerance, inability to grow in shade, dry/moist/wet soil preference and drought tolerance are species-specific statements, not regeneration-practice envelopes; keep each claim visible in a species hold.
- Remaining Annex C taxa (Acacia farnesiana, Adenanthera pavonina, Cinchona pubescens, Chromolaena odorata, Delonix regia, Haematoxylum campechianum, Melaleuca quinquenervia, Piper aduncum, Prosopis juliflorae, Triplaris cumingiana): descriptions, morphology, occurrence and uses. Preserve individual dispositions. All 13 Annex C taxa are introduced as invasive alien plants; this is warning/control context, not a recommendation to establish them.

## Summary counts

Two staged practice-level expert criteria; zero verified spatial-model uses; zero resolved canonical-variable directions; zero calibrated functions; zero human approvals. The same source's ecological species statements remain separate held work, not omitted evidence or extra practice votes.
