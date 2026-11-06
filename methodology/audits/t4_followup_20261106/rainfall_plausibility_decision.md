# Ranchi rainfall: qualitative retention and numeric plausibility hold

6 November 2026. Evidence `ev_af_annual_precipitation_ranchi2017_20261105`;
Ahmad, Goparaju and Qayum, online 2017 / journal volume 2019, Table 4,
PDF p. 11 / printed p. 541. Generic regional agroforestry; no specific family assigned.

Pete approved qualitative retention and explicitly required agents/skills to flag
scientifically implausible published classes before recipe use. The paper maps
agroforestry suitability using an interpolated 1993–2002 mean annual rainfall layer.
Published classes: >1,170 mm highly suitable, 1,170–1,150 mm moderately suitable,
<1,150 mm marginally suitable; no rainfall-unsuitable class. Endpoint inclusion is
not resolved. The moderate band is only 20 mm wide. This flags an unsupported
calibration distinction, not proof of a transcription error or that the paper is wrong.
No quantified uncertainty or independent validation of that boundary is established
in this review; no error magnitude is invented.

Keep source model-use and its locally wetter-favoured direction. Preserve source
numbers in context only. Do not compile cutoffs, normalize classes to 0–1, infer
an unsuitable dry tail, widen bands or transfer them across regions/families.
`scoping_candidate` remains unchanged; qualitative approval does not permit numeric
promotion. Applied via normal review helper; only reviewer approval and attribution
changed, all source payloads and other records preserved.

Instruction response: extraction ruleset v1.9.6, catalogue defect 55, shared T4 review
contract, synthesis skill, methodology and AGENTS now require numeric plausibility
review. Check narrow bands against measurement support and known uncertainty,
false precision, unjustified transitions, proxy semantics and transfer. No universal
20 mm rejection threshold, automated scientific-validity claim or corpus-wide
restamping. Existing learnings cursor is not advanced over unrelated unread feedback.

Isolated approved-only compilation keeps the Ranchi claim `selection_only`. The only
agroforestry T4 CSV change is annual-precipitation source support from 5 to 6; existing
response parameters, scores, weights, mapping IDs and dataset bindings are unchanged.
This is one additional source of qualitative use, not numeric threshold validation.

Generated family JSON/report refresh also reconciles previously stale outputs with
existing CSV content (Haile continuation and soil-input review metadata). Independent
review confirmed changed family response parameters match authoritative CSV. These
are not new decisions in this review. The active instruction snapshot and staging
ruleset acceptance checks pass; scientific plausibility remains a human/agent review
requirement, not an automated ecological-validity test.

Validation: 1,270 tests passed; Ruff lint/format and core type checks passed; generated
JSON check found zero stale files; schema structure and T4 coverage returned zero
errors. Generic skill validation accepts synthesis; extraction retains its existing
project-specific `version` frontmatter, checked by repository ruleset/snapshot tests
rather than the generic validator (which does not allow that field).
