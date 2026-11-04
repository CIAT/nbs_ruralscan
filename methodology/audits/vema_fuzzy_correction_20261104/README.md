# Vema fuzzy-input correction — 4 November 2026

Three existing, unapproved T4 records corrected under v1.9.2. No new source, EV unit, discovery claim or human approval. Original extraction ruleset stamps remain; correction version is recorded in context. Full before/after rows and PDF hash are in corrections.json.

## Source reading and correction

Read PDF pages 1, 3–5 and 7–8; visually inspected Figure 1 and Table 2 on PDF p4. Canonical historical source ID is singh_2019_fuzzy_wh_structure_rainfed, but opening title/authors identify Vema, Sudheer and Chaubey (2019), DOI 10.1016/j.agwat.2019.03.028. Do not duplicate this source under a corrected author label.

Table 2 reports three trapezoidal input classes for each of slope, permeability and runoff CN. All nine classes (36 parameter positions) are retained. Removed seven misleading standalone output-bound fields: slope opt_low/opt_high/abs_max, permeability opt_high/abs_max, runoff abs_min/opt_low (seven fields total). These numbers are retained inside their proper input classes, not deleted from the evidence.

Direction is preserved separately: p3 supports lower slope and permeability for surface storage; p7 favors medium/high runoff for storage and low runoff for recharge. These are scoped qualitative preferences, not universal independent responses. P4's medium-runoff example yields high check-dam/farm-pond suitability with low slope/permeability, disproving the necessity of the previous high-CN cutoff. All inputs receive equal importance in the source's joint rules; no numeric MCDA weight is inferred.

The source describes 27 joint rules but prints four examples on p4; no complete executable rule base was verified in this pass. Mamdani aggregation and output defuzzification (pp4–5) separate input membership from final suitability. Check dams require drainage lines (p8): raster applicability is not installed area. Storage/recharge and NbS eligibility remain explicit scope constraints.

## Additional source ambiguity

P3's worked 8% slope example says low/medium membership 0.2/0.8. Table 2's low [0,0,5,10] and medium [5,10,20,30] yield 0.4/0.6 under the stated trapezoids. Literal table parameters are retained; no repair or executable calibration is asserted.

## Review question

Keep these records as evidence of model use, complete input classes and conditional qualitative surface-storage directions, with joint-rule and transfer holds? They must not authorize independent absolute suitability cutoffs. Three VERIFY-FLAG markers surface this question. Existing reviewer_ok=false and review states are unchanged.

## Bounded retrospective

Defect: input-class membership endpoints had been promoted into unconditional output suitability limits. Existing skill requirements already distinguish model use, direction and calibration and prohibit rank/class endpoints becoming absolute limits. No novel rule or ruleset bump is claimed. Three of three targeted records corrected; nine of nine input classes retained; zero independently executable suitability functions established. This is an audited correction, not a new extraction sweep. Global learning cursor and progress ledger are unchanged; no whole-corpus quality improvement is inferred.
