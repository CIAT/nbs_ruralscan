# Singh/Jha bounded correction — 4 November 2026

Seven existing, unapproved T4 records corrected. No new source registration or evidence units; no human decisions, family definitions or analytical recipe rows changed. Historical extraction stamps retained; context records correction ruleset v1.9.2. Full before/after rows and artifact hashes are in corrections.json.

## Native-table findings

Singh et al. (2017), DOI 10.1016/j.jclepro.2016.11.163, is held under historical canonical ID mahmoud_2016_mcda_gis_wh_recharge. Opening identity checked; do not duplicate the source because its ID is misleading. Read PDF pp1,3,6,11,12 and visually inspected Tables 1–3 and 6. Jha et al. (2014) opening title and Table 1/p7 were checked against the shared-library artifact and discovery manifest; Jha remains pending formal source intake.

Table 6 columns specify:

| Structure | Slope | Soil | Land cover | Stream order |
|---|---|---|---|---|
| Farm pond | <3% | Fine textured | Agriculture | Not specified |
| Ground percolation tank | <3% | Coarse textured | Wasteland and degraded forest | Not specified |
| Stream percolation tank | <5% | Coarse textured | Not specified | 2nd/3rd |
| Check dam | <15% | Fine textured | Not specified | 2nd/3rd |

The prior soil-texture record reversed fine/coarse assignments. Native table columns establish the correction. Four Table-6 EV rows now preserve each structure's conditions; the family-wide 15% slope ceiling and generic stream-order bounds are removed. Land-cover rules are restricted to the relevant columns, not pooled across the family.

Table 3 is a different analytical step: local RWH potential ranking. All 14 feature classes and their assigned/normalized weights are retained, separately from three thematic weights. Restored drainage density >1.00 km/km², Very Low, assigned 1.5, normalized 0.061, which the previous quote and encoding omitted. Removed unsupported optimum fields and 10% absolute slope maximum: 5–10% is Low, and no >10% class is printed. No exclusion is inferred from absence. Runoff coefficient uses its original scale; it is not curve number. Source prints descending intervals 0.4–0.3 and 0.3–0.2; retain them explicitly rather than silently repairing endpoint conventions.

Directions retained for the local potential index: slope decreasing, drainage density decreasing, runoff coefficient increasing. Source theme weights 0.348, 0.261 and 0.391 are not runtime MCDA weights. Section 3.4/p11 establishes expert-assigned weights, WLC and micro-watershed drainage density. Placement in section 3.6/p12 is a separate Boolean operation, with stream-based structures restricted to drainage corridors; raster zones do not measure installed area.

## Lineage and transfer

Table 6 explicitly cites Jha 2014. Primary Table 1/p7 agrees on fine soils for ponds/check dams and uses “light textured” for percolation tanks; Singh uses “coarse textured”. Jha names degraded forest for ground tanks; Singh adds wasteland. These differences are preserved. They are not independent votes for a universal rule. Because Jha is not yet registered, attribution and primary comparison are recorded without inventing a dangling lineage_of ID. Later intake must connect the existing attribution to the canonical source and must not count the inherited rules twice.

## Review and retrospective

All seven remain reviewer_ok=false, with VERIFY-FLAG markers requesting human review of corrected interpretations. Ten water-harvesting referrals (these seven plus Vema's three) now have audited corrections; this completes the bounded correction batch, not human QA or the 36-group extraction inventory.

Defects are already covered by the current extraction contract: native column alignment, complete table coverage, source weights versus executable scores, and lineage-aware independence. No new extraction sweep or global quality trend is claimed. Progress ledger and global learning cursor remain unchanged. New source intake, full Jha extraction and unreviewed candidate methods remain separate tasks.
