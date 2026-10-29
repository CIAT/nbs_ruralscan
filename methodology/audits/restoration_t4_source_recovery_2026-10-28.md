# Restoration T4: targeted source-component recovery

28 October 2026. Follow-up to merged PR #465, starting from `9928c1f`.

## Outcome

The two priority recovery attempts did **not** recover numeric calibration tables. They narrowed the blockers and verified source identities. This is component recovery for known sources, not a new discovery or extraction sweep. No SRC, EV, recipe, review, search-completion or progress record changed. The first-pass packages and their zero-approved-function state remain unchanged.

Machine-readable results: [metadata checks](../../pipeline/t4_audit/source_recovery_2026-10-28/metadata_checks.json), [recovery results](../../pipeline/t4_audit/source_recovery_2026-10-28/recovery_results.json), [exact search queries](../../pipeline/t4_audit/source_recovery_2026-10-28/recovery_queries.json).

## Aduana-Alcantara et al. (2023)

The [publisher article page](https://www.nepjol.info/index.php/josem/article/view/55200) provides one PDF. Direct HTTP retrieval failed, but the browser download succeeded. The downloaded nine-page PDF has SHA-1 `ce9981bc0cd102e1ae2ee09069c38f054cc7eaa4`, exactly matching the team stocktake artifact inspected in the first pass. This establishes that the earlier omission was not caused by a damaged local download.

PDF page 4 (printed page 86) was rendered and visually checked again: it refers to Table 2, then displays the WLC explanation and Figure 3, without the parameter table. The byte identity carries forward the prior all-page inventory: Table 1 is also referenced but absent; Figure 2 is a numbering gap whose contents are unknown. Do not assume what Figure 2 contained.

The repository's `verify_metadata._crossref` and `_overlap` functions round-tripped the publisher DOI against the exact title, with title overlap 1.0. The authoritative citation is recorded in `metadata_checks.json`. This verification is an audit record, **not** a queue/SRC promotion or a claim that central intake has been completed.

A [ResearchGate author-upload landing page](https://www.researchgate.net/publication/371169046_Mangrove_Land_Suitability_Assessment_Using_Weighted_Linear_Combination_A_Case_Study_of_La_Union_Province_Coastline_Philippines) surfaced in search. Its file was not downloaded or version-compared. A human check may find an alternate version; no assertion is made that it lacks the missing material.

**Exact missing-material request, prepared but not sent:**

> Please provide Table 2 containing the parameter-specific suitability classes/cutpoints, units and cited sources for your 2023 La Union mangrove WLC paper. The publisher's nine-page PDF refers to Table 2 on printed page 86 but does not include it. Please also clarify the missing Table 1 and Figure 2 numbering. A corrected publisher PDF or author-held original with the table caption, class legend and any notes would allow us to retain the source-specific rules without inferring thresholds.

Existing four-variable use and assumed equal weighting remain in the first-pass inventory. No inferred normalized weights, class scores or universal temperature/elevation thresholds are added.

## Oliveira et al. (2026)

The existing 12-page main PDF remains available in the team library/cache. Its DOI and title also round-trip exactly through the repository metadata verifier. The main PDF's Appendix A, PDF page 10, points back to the article DOI rather than identifying a separate supplement URL.

The [publisher article](https://www.sciencedirect.com/science/article/pii/S0301479726008340) returned HTTP 403 through retrieval tools; the browser displayed a human CAPTCHA. The challenge was not attempted. Targeted title/author/PDF, supplementary-material, ResearchGate and repository/Zenodo searches did not yield a verified supplement download. The local technical/data mirror filename search found no matching supplement; this is not an exhaustive file-content search.

Unpaywall returned HTTP 200, `is_oa=false`, `oa_status=closed`, and no OA locations. This describes its record for the main article; it does **not** establish supplement availability. No new `paywalled` status is assigned. ResearchGate/Academia and author-held versions still require human checking; no negative claim is inferred from search results.

**Exact download task:** open the publisher article in a human browser and save the supplementary material containing sections 2 and 3 and Figures S1–S3. Preserve its original filename, article association and source URL. If publisher access still fails, request that supplement from the corresponding author. The main article is already held; do not request another institutional download of the main PDF as a substitute.

Any recovered file must pass the established format adapter, title/article identity, team-library and locator checks before extraction. A spreadsheet or other unsupported format remains paused rather than being treated as a PDF table. The existing conditional slope claim remains held; missing supplement access cannot justify an unconditional ceiling.

## Verification and next executable work

- Both Crossref title matches: 1.0; canonical citations saved.
- Publisher/stocktake Aduana PDFs: identical SHA-1 and nine pages.
- Page 4 visual check agrees with the first-pass missing-table finding.
- All three recovery JSON files parse and distinguish attempts from successful recovery.
- No analytical code, schema, evidence or approvals changed; no spatial run or test-suite claim is made for this documentation-only follow-up.

The next useful input for these two numeric holds is the actual missing table/supplement, not another synthesis run. Other recovered stocktake papers can undergo their separate metadata/intake and reading passes in parallel; this report does not mark that work complete. No author or team message was sent.
