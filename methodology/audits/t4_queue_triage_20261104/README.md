# T4 review queue triage — 4 November 2026

Baseline: cba78e24c9b0. Read-only queue inventory plus one source-checked answer; no new extraction, analytical changes or human approval.

The live local clarification service initially reported 312 resolved groups, 29 answer-ready groups and 18 needing investigation. These are clarification groups, not evidence-unit totals or a percentage of completed review. Seventeen investigation groups are prior Codex audit referrals; one is Peter's wetland scope question.

## Completed

Qiu 2020: checked cached primary PDF title and pages 1, 3 and 4, including sections 2.3.1–2.3.5. The source concerns rehabilitation of former marsh converted to cropland. It is not evidence for constructed treatment wetlands. The existing EV record already names restoration_rewetting and operational_risk. Added a fingerprint-validated answer to the existing followup store, with artifact hash and explicit human decision question. No EV field or reviewer decision changed. The local service now exposes this answer as needs_judgement, leaving 17 investigation groups and the original 29 answer-ready groups.

## Next bounded correction batch

Ten water-harvesting audit referrals from the preceding High-tier stocktake remain unapproved and are enumerated in water_harvesting_queue.json. This inventory does not install synthesis blocks or mark them resolved.

1. Vema: three records. Inspect input memberships and joint rules together; preserve reported values but remove any unsupported independent absolute-limit interpretation through the audited correction workflow. Drainage-line restriction and incomplete public rule-set coverage remain explicit.
2. Singh/Jha: seven records. Separate Table 6 structure-placement conditions from Table 3 local index components, account for source lineage, and preserve storage versus recharge differences. Do not merge conflicting permeability directions into one curve.
3. Review remaining 17 AI audit referrals against source and current corrected record before providing answers. Do not auto-close them because earlier audit prose says corrected.

No fresh discovery, new source registration, human approval, family regrouping or T3/T6 work was performed. Rooftop, homegardens and plantation display issues belong to the separate dashboard handover; methodological eligibility remains governed by recorded decisions and issue #547.

## CI correction

The initial wetland follow-up used an ad hoc key and `needs_judgement`, which the coverage gate rejected. Re-keyed with the canonical evidence_id|reviewer|note digest and set follow-up status to `resolved` (the source question is answered). This is distinct from evidence approval: reviewer_ok remains false, Peter's query remains open, and the clarification service presents the answer for human review. No Keep/Drop decision is written.

The clarification replay unit test now replaces the generator with a recording stub and asserts regeneration of the temporary schema was requested. Its minimal fixture tests event replay, not real-corpus generation; production validation remains unchanged.

Coverage validation also now checks stored follow-up identities and field fingerprints against all EV records, because the existing answer store is shared across practices. The requirement to discover missing agroforestry follow-ups remains scoped to agroforestry; adding a wetland answer does not create a new full-corpus follow-up requirement. The 63 recovery/clarification tests pass after this fix.
