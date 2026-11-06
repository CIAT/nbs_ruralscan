# Ranchi NDVI: qualitative retention and modern recipe interpretation

6 November 2026. Pete: "yes keep", with a request to signal NDVI's proxy use in older
papers and assess modern tree-cover datasets. Evidence `ev_af_ndvi_ranchi2017_20261105`.
Ahmad et al., online 2017 / volume 2019: Table 4 (PDF11 / printed541), Figure 4 and
vegetation discussion (PDF6 / printed536). The source uses NDVI for vegetation greenness,
density/vigour and erosion-related interpretation; it does not establish tree cover alone.

## Approved evidence decision

Retain regional model-use and local qualitative direction. Preserve very dense/dense
(high), medium/poor (moderate), nil (marginal), with no numeric NDVI boundaries and the
prose/table discrepancy (marginal prose says low to nil). No global greener-is-better
rule, numeric score, exclusion of degraded land or family transfer is approved.

## Recipe interpretation requested by Pete

Where the intended property is **tree cover**, prefer a fit-for-purpose direct tree-cover
or canopy-cover product over an NDVI proxy; describe that proxy as superseded for this
particular purpose after the replacement is reviewed. Retain source provenance as NDVI.
Where the intended property is **vegetation greenness, condition or seasonality**, retain
that distinct measurement; tree cover does not automatically replace it. For Ranchi,
the original mixed vegetation/erosion meaning must be resolved before any substitution.
This is a conditional recipe-design preference, not blanket deprecation of NDVI, an
ontology alias, a new dataset binding or permission to copy NDVI response classes onto
canopy cover. Product date, AOI accuracy, canopy definition, sparse trees, plantations
and tree crops must fit the intended question. Categorical tree cover, canopy percentage
and canopy height are distinct properties.

Producer documentation checked 6 November 2026:
- USGS describes NDVI as vegetation greenness/density/plant-health information:
  https://www.usgs.gov/landsat-missions/landsat-normalized-difference-vegetation-index
- ESA WorldCover supplies 10 m land-cover maps for 2020/2021 and separate NDVI composites:
  https://esa-worldcover.org/en/data-access
  These demonstrate distinct products, not approval of WorldCover as a quantitative
  canopy-percentage layer or proof that 2021 data are sufficiently current for any AOI.

These references inform implementation interpretation only; no SRC/EV intake is implied.
Existing v1.9.6 T4 contract already requires explicit proxy meaning and reviewed transfer.

## Application status

Human Keep is recorded in `pending_ranchi_review_export.csv`; register application awaits
completion of the review batch. Preserve `scoping_candidate`, original NDVI variable and
source payload. Source-payload fingerprint (all fields except reviewer_ok, review_state,
attribution):
365888e15b1df572e6255217827ce93791cd5717e8071ec61088c127e8a76a6a
