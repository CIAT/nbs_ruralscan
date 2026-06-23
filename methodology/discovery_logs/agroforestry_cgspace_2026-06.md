# Agroforestry — CGSpace (CGIAR DSpace) discovery (2026-06)

**Channel:** grey/lit · CGSpace open DSpace REST API (`cgspace.cgiar.org/server/api`, no auth). **Run:** `cgspace_af_2026-06`. PRISMA-lite, read-only discovery + screening.

## Why CGSpace
CGIAR's institutional repository — the home of ICRAF/CIFOR/Alliance outputs. Open DSpace API (`/discover/search/objects?query=…`); PDFs via item → bundles → ORIGINAL bitstream → `/content`.

## Queries (4) + screening
- "agroforestry land suitability mapping criteria"; "agroforestry suitability soil slope rainfall classes"; "silvopastoral/silvopasture land suitability"; "land evaluation agroforestry FAO suitability classes S1 S2". ~20 unique items screened.

## Finding — **no acquirable, on-scope, AF-suitability-threshold study** (honest null)
The acquirable ∩ on-AF-practice ∩ real-suitability-rules intersection is empty on CGSpace:
- **Paywalled (metadata-only):** the strongest threshold candidate — *Quantification of Land Potential for Scaling Agroforestry in South Asia* (`10568/113409`, FAO criteria, soil/climate/topo classes) — has **no ORIGINAL bitstream** on CGSpace; full text behind the Springer DOI (10.1007/s42489-020-00045-0). Can't cache → can't register. **Deferred:** retry via an OA copy (OpenAlex/Unpaywall).
- **Off-scope (acquired + screened, then dropped):** *Biophysical characterization: SI-MFS sites, Ethiopia* (`10568/135324`, open PDF) reads as **methods / study-site characterization** ("3. Data and methods… topography of the study site was characterized… slope maps generated using DEM"), not AF suitability *rules*. The slope/rainfall are site descriptors — the off-scope defect (`check_scope` study_site). Not extracted; cache removed.
- **Wrong-NbS / restoration (don't-lump):** FLR Lake Ziway Ethiopia (`132558`), Land Restoration Chad (`117682`), degraded-land prioritization Colombia (`110304`), NbS Dolo Ado (`155265`) — restoration/NbS-broad, AF is one of several land uses.
- **Targeting frameworks → TOOL candidates (not EV):** silvopastoral spatial-targeting reports — N Laos (`10568/169649`), Ghana small-ruminant (`10568/180294`) — are *targeting methods* (like ROAM/ESI-IBSTI), better suited to the TOOL register than threshold-EV.

## Conclusion
**0 EV extracted.** CGSpace skews to reports / restoration-potential / targeting frameworks; few apply explicit AF suitability classes with variable thresholds (query 4: none apply FAO S1–N with cutoffs). The **OpenAlex peer-reviewed** channel remains the productive one for AF thresholds. **Next:** (a) chase an OA copy of `10568/113409`; (b) register the silvopastoral targeting reports in the TOOL register if wanted; (c) WOCAT (token-walled) for SLM-tech grey.
