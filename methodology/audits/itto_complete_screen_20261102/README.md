# ITTO: consolidated T4 source screening

2 November 2026. Source `itto_flr_guidelines_ps24_2020`; ruleset v1.9.2 and T4 review contract v1.6.16. This completes source-wide reading and disposition, combining the earlier bounded audits with the remaining guidance, bibliography and cases. It does **not** complete evidence intake, human review or synthesis.

## Result

All142 PDF pages now have coverage records; all18 case studies, seven tables and four figures are accounted for. Four low-text/OCR alerts are resolved by visual inspection:81 and135 are photographs;140 and141 are blank except running furniture. No analytical text was recovered from those pages. The unchanged deterministic index has142 pages and table extraction enabled; all-variable, full-table retrieval was refreshed in local staging.

Fourteen candidate records retain ecological statements, source-specific planning use, species observations and cross-NbS pointers. These are **not14 independent studies, approved claims or EV rows**. One earlier ITTO habitat safeguard remains in EV, unchanged. No new EV rows or executable functions were generated. SRC remains in_progress because scoped intake and mapping holds remain; no searched/extracted/verified/reviewed completion stamp was advanced.

The earlier audits remain historical records. Their then-unswept page lists are superseded for **reading coverage only** by page_coverage.csv. All old evidence, reviews and source metadata are preserved.

## What the complete reading adds

GE28 (PDF38) explicitly links stronger seasonal climate, exposure and low fertility to greater restoration difficulty. Each named factor is retained separately with the full source sentence. This broad FLR statement covers more than a single forest family, and the raw terms do not identify rainfall variability, aspect/wind, SOC or CEC. Missing calibration is not the reason to discard direction: the inventory retains it while preventing an unsupported proxy or family assignment.

GE14 (PDF33) calls for replenishing soil organic matter. SOM is not SOC. Its native/non-native species guidance also remains a design safeguard, not a spatial invasive-cover mask.

Case3 (PDF90–92) retains all five named native taxa and their reported successful open or sheltered settings. These observations do not establish comparative preferences. The explicit increasing-growth response to thinning is retained as a treatment response, without equating thinning to canopy cover or irradiance. Mycorrhizal associations and possible poor AMF inoculum also remain species-context evidence. No taxa were silently converted to practice-level rules.

Case12 (PDF116–119) genuinely uses soil types, slope classes, terrain features and weed competition in land classification and silvicultural planning. This use is retained with unknown suitability direction and absent class boundaries. The production-plantation/restoration distinction remains material under the existing family ruling. Its joint fire/soil-degradation barrier to natural regeneration is retained without splitting it into unsupported independent effects.

Case13 (PDF120–121) links nearby seeds/propagules with potential regeneration after Eucalyptus harvest. Sources of propagules need not be mapped forest; no distance_to_forest substitution or generic passive-restoration rule is admitted.

Case15 (PDF126) reports different silvopastoral designs at0–2000m and above2000m. Both regimes are retained as an agroforestry follow-up, not a forest/mangrove rule or exclusion above2000m. Product moisture in the cocoa case is likewise not soil moisture or a climatic envelope.

Case1’s level-terrain/access preference explicitly minimizes planting and monitoring costs. It remains operational context, not an ecological slope limit. Region elevations, rainfall, crop slopes, contractual stocking counts, project durations and treatment spacings remain context/design values throughout the case inventory.

## Source conflicts and attribution

source_issues.json preserves five issues:

- General guidance against non-native planting contrasts with cases using exotics. Normative recommendations and reported practices are not merged into invented agreement.
- Several communal-restoration lessons cite Case3 although matching content is in Case9. Original case pages govern attribution.
- A lesson labels Case13 as Malaysia/Thailand, although Case13 is Brazil; Malaysia/Thailand is Case7.
- Case15 reports44,100 participants alongside3,250 as79.3%; the source values are inconsistent. No number was silently corrected or extracted as effect evidence.
- Green table cells signify intervention purpose or contribution to a guiding element, not suitability grades or confidence weights.

No downstream unit was created from the problematic summaries. These are source issues, not edits to historical reviews.

## Tables, figures and tools

The table/figure inventory accounts for every object listed in the source contents. Table1 has26 entries, all inventoried; Table2’s12 cells and Table5’s32 rows retain their earlier detailed audits. Table4 is a project-cycle example. Tables6/7 are purpose/contribution matrices: all18 case rows and32 guiding-element rows are classified, but individual matrix cells are not recoded as evidence. Figure1 is an area schematic; Figures2–4 are conceptual/process diagrams. None supplies a calibrated suitability curve.

Tools remain in scope as follow-up material. Table1 and the bibliography identify ROAM, ROOT, RESTS, Spotlight, forest monitoring tools and InVEST; cases identify Apremavi’s geographic portal and the South Ecuador research database. tools_followup.json distinguishes these leads, existing queue identity and required next checks. No codebase, current service availability, algorithm or licence was verified in this source-reading pass. Dataset intake remains paused. No new discovery search or acquisition is claimed.

## Validation, review and retrospective

Run the included verify_audit.py against the hydrated PDF. It checks142 unique pages, previous and new native-text anchors, all18 non-overlapping case ranges,26 Table1 entries, seven tables/four figures,14 held candidate quotes, visual resolution of the four low-text pages, and unchanged source identity. A complete page inventory is not proof of correct interpretation, so semantic dispositions are explicit.

Coordinating-agent adversarial review challenged both over-extraction and lost information: qualitative directions retained; unknown measurements not proxied; species scope preserved; prior habitat evidence linked rather than duplicated; plantation, agroforestry and operational claims kept distinct. No independent or human approval is claimed.

This was a source-screening completion, not an extraction sweep. No sweep metrics, learnings cursor or ledger stage was advanced. Existing defect rules cover proxy substitution, site-context thresholds, table semantics and attribution; no new global rule change is justified by this pass. Full-corpus generation was not rerun because analytical CSVs and generated outputs were unchanged. Repository lint/format, whitespace and audit validation are the relevant checks.

## Remaining work, now bounded

Reading is complete. Remaining work is claim-specific: resolve raw-variable/family mappings, obtain any required primary-source detail for species/treatment claims, and decide which retained candidates can enter the appropriate lane. Candidate records name the actual obstacle; absence of numeric calibration alone is never an exclusion reason. Existing habitat safeguard still awaits human review. Other sessions retain ownership of T3/T6.
