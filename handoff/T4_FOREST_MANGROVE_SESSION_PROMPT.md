# New-session prompt: forest and mangrove T4

Copy the text below into a new session in the `CIAT/nbs_ruralscan` project.

---

Build a reviewable, reproducible T4 first pass for two priorities:

1. Reforestation/afforestation, using the existing `forest_restoration` recipe and
   `forest_restoration__active_planting` family. Keep passive regeneration, assisted
   regeneration, protection/CBFM and production plantations distinct. Inventory their
   relevant existing evidence, but prioritise active planting rather than expanding
   this task into all forest management.
2. Mangrove restoration, its own NbS `mangrove_restoration`, currently one approved
   family `mangrove_restoration__tidal_coastal`. Keep establishment method explicit
   (planting versus ecological/hydrological restoration). Do not transfer terrestrial
   forest thresholds or invent a new mangrove family without my approval.

Use agents for extraction and adversarial review. Make substantial progress before
stopping. Fix clear technical defects autonomously; genuine methodological ambiguity
requires my approval. This task explicitly authorises T4 work despite the earlier
pause within effect-extraction lanes. Pilot/runtime implementation stays with Diego
and Brayden. Do not message them unless I ask.

Start by checking latest main and the adversarial pipeline audit at
`methodology/audits/pipeline_adversarial_2026-10-28.md`. Confirm its hardening changes
are merged before relying on them; otherwise report the dependency and use an isolated
branch containing them. Do not work from a stale clone or overwrite pending reviews.
Read `AGENTS.md`, current extraction/synthesis skills, T4 review contract, generation
method, current FAM, crop-scope and roll-up policies. At audit time, ruleset was v1.8.0;
use the actual current version and snapshot. The forest document's old mangrove F4
proposal is superseded by the signed standalone mangrove scheme.

First reconcile existing assets: scoping-review papers, discovery logs/SRCH, acquisition
queue, SRC, EV, code/tool sources, source-table inventories and review history. Report
what exists, what is incomplete and what is genuinely missing. Do not equate an empty
approval flag with “nobody reviewed this”; inspect decisions/history before requesting
repeat review. Audit baseline had 210 active forest T4/operational records and 39 active
mangrove records, all without a true approval flag; these are scope-wide counts, not
active-planting-only counts or a new review assignment. Mangrove had no T4 recipe CSV.
Recompute these facts; do not copy them as current progress.

Review existing papers before new discovery. Inventory every relevant table row,
continuation, figure and supplement. Capture variable use, suitability direction,
reported values/classes/units, categorical requirements, source weights and weighting
methods. Preserve parent criteria, sibling sets, depth/time context and denominators
needed to interpret relative importance. Inspect actual tool parameters/code, not only
README summaries. Log bounded searches only for remaining gaps, covering stocktake,
updated literature, grey literature and tools with exact protocol/count provenance.
Known sources used in another scope need canonical-source reuse tracking; do not
silently discard their new work as duplicates or create extra votes from copied papers.

Use the deterministic cached-source pipeline and staging gates. Subagents write staging
only; central orchestration validates and appends. Require verified metadata and artifact
identity, team-accessible sources, native verbatim quotes and exact locators. Scans,
chapter identity, unsupported section anchors and missing supplements stay explicit holds.
Do not infer source quality, practice applicability or numeric calibration from a title.
Species envelopes remain separate from practice-level rules. Observed site ranges stay
low-priority context; neither site observations nor map minima/maxima create cutoffs.

Compile through evidence corpus → versioned logic/policies → authoritative T4 CSV →
generated developer contract. Run isolated trial synthesis first. Harmonise only
compatible scopes, quantities and units; preserve reported classes, genuine gaps,
conflicting boundaries and independent source lineage. Do not fill missing tails or
assign unreported scores without a recorded decision. Keep source profiles and approved
pools inspectable side by side. A species/community parameter proposal is not approval
to merge single-species envelopes into a general restoration function.

Report studies using each variable/group, direction evidence and calibrated contributors
separately. Show denominators and review status. Use Pete’s 28 October approved convention: raw n/N headline support, with quality-weighted
support shown separately only when complete screened membership and tiers are known.
Leave unknown denominators blank. Keep source-quality weights, within-study relative
importance and runtime MCDA weights distinct. No agroforestry weight vector or mask
carries into these recipes automatically. Any new aggregation/weighting, ecological
transfer, afforestation safeguard or family-split choice needs my approval.

Include categorical land-use/host requirements and hard exclusions. Include soft access,
tenure, labour, finance and other operational evidence in a separate operational module,
not in the core suitability score. Never treat native non-forest ecosystems as suitable
for afforestation solely because they have low tree cover. Resolve any actual mask or
safeguard proposal explicitly from evidence and approved project policy. Mangrove
hydrology/elevation inputs must retain vertical reference, inundation regime and spatial
support where reported; incompatible measures cannot be pooled by name alone.

Keep everything reviewable in the existing dashboard. No new parallel dashboard or
separate “approve the answer” workflow. Review cards show source context, extracted rule,
intended use, importance and remaining decision; answers return on the same evidence card.
Do not grant human approval. Reconcile once, then ask only necessary shared questions.

Deliver through a GitHub PR: evidence coverage/accounting, reviewed or explicitly held
numeric and categorical rules, dataset requirements/bindings, reproducible developer
CSV/JSON, function visualisations, weighting diagnostics, exact methodology and regeneration
commands, conformance tests and a short genuine-ambiguity list. Use recipe-specific handoff
notes or neutral templates; no copied agroforestry decisions. A developer export must
reproduce the audited recipe, retain unknowns and pass manifest verification. Leave spatial
pilot testing to Diego/Brayden. Run the retrospective and update progress only for work
actually completed; never advance a feedback cursor beyond the feedback inspected.
