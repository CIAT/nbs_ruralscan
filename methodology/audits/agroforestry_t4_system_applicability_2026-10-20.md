# Agroforestry T4: system applicability source review

20 October 2026. Reviewer: Codex source review, authorized by Pete. This resolves mapping scope; it does not manufacture source-specific validation.

## Decisions and primary-source locators

### ahmad_2018

Cached source: `.cache/corpus/ahmad_2018.pdf`; PDF pages [8, 9, 10].

Broad regional agroforestry model; explicitly includes agrisilviculture and silvopastoral systems.

Use slope and SOC as conditional planted-tree/crop scoping priors. Paper also discusses silvopastoral systems; no automatic F3 response or FMNR transfer.

Source phrase (line-wrap/ligature normalization): “The various agroforestry systems such as Agri-horti-silviculture, Agri-silviculture, silvi-pastoral and agro-silvi-pastoral can be significantly applied seeing the site condition of land.”

### nath_2021

Cached source: `.cache/corpus/nath_2021.pdf`; PDF pages [11, 19, 20].

Broad regional agroforestry land suitability, explicitly not targeted to any species or agroforestry model.

Use slope, SOC and pH as conditional planted-tree/crop scoping priors. Retain rainfall and temperature only as Eastern Indian Himalayan regional profiles. Do not apply generic climate exclusions to FMNR, or treat tea examples as a crop-specific F5 envelope.

Source phrase (line-wrap/ligature normalization): “without targeting any specific species or agroforestry model”

### haile_2024

Cached source: `.cache/corpus/haile_2024.pdf`; PDF pages [2, 9].

Traditional parkland agroforestry; validation also describes parkland.

Parkland established; planting versus natural retention/regeneration not established. Keep F1/F2 assignment unresolved and exclude from combined planted-system pools.

Source phrase (line-wrap/ligature normalization): “Parkland agroforestry is practiced in most part of Genale sub-basin”

### yadav_2024

Cached source: `.cache/corpus/yadav_2024.pdf`; PDF pages [5, 6, 7].

Tree-species climate/soil clusters, not three agroforestry systems.

Reclassify temperature evidence to species_specific; retain all three source groups in species lane, exclude from practice T4.

Source phrase (line-wrap/ligature normalization): “suitability maps of tree species grouped according to climate, soil, and topography”

### singh_2026

Cached source: `.cache/corpus/singh_2026.pdf`; PDF pages [4, 5, 8, 11].

Wadi/agro-horti-forestry, bund/boundary plantings, intercropping, home gardens and block plantings; intervention mapping uses crop intensity.

Retain F1 pH assignment for planted trees with crops. Boundary component still needs F4 geometry; no numeric-only expansion into F4 or homegardens. Pool pH with Nath as an India-derived scoping prior, retaining uncertainty and regional profiles.

Source phrase (line-wrap/ligature normalization): “Bund plantations and intercropping are prescribed in single cropping agricultural lands”

### mushtaq_2023

Cached source: `.cache/corpus/mushtaq_2023.pdf`; PDF pages [1, 17].

Mulberry-tree production study; >1200 mm statement is secondary generic agroforestry discussion, citing Ahmad 2019.

Remove F5 shaded-perennial assignment from this generic rainfall statement. Retain as cross-family secondary context with unresolved score; do not infer a crop-under-shade requirement or use it as an independent numeric response.

Source phrase (line-wrap/ligature normalization): “Agroforestry-friendly climates are characterized by mean annual precipitation exceeding 1200 mm”

## Compatibility and transfer

Slope and SOC: Ahmad + Nath. pH: Nath + Singh. All three pools are explicitly scoped to planted-tree/crop scoping responses derived from regional Indian models. These are a conservative system-use decision from broad land suitability evidence, not proof of universal physiological limits. F1 is the only activated target; source discussion of F3/F4/F5 does not automatically create executable responses there.

The compiler retains each source profile; source quality weights remain tier × claim basis × grey discount. At every value, output records median bounds, source spread, coverage and contributing source origins. Exact half-weight ties and zero-versus-positive conflicts remain unknown. Single-source tails are flagged. Climate responses are not pooled across regions.

The existing standalone F1 slope threshold remains a distinct response; generic ordinal bands are preserved alongside it, not substituted or blended into that threshold. Both source-profile and pool selection remain explicit.

## Genuine outstanding issues

Haile parkland establishment pathway remains unspecified; cannot equate parkland with FMNR. Haile pH and Nath NDVI retain printed contradictions; Nath aridity scale still needs authoritative conversion. Ahmad canopy evidence actually refers to NDVI. Mushtaq generic favourable rainfall lacks a class score and is not a shaded-perennial constraint. FMNR study climate domains remain observations, not establishment cutoffs.

Yadav temperature groups were a scope error, now corrected to the species lane. They are not pending practice-family assignment.
