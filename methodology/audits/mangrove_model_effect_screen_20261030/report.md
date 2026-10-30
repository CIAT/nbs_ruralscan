# Worthington effect/referral screen — 2026-10-30

Follow-up to the bounded mangrove model-source work. Read cached Worthington and
Spalding (2018), PDF pages 14–27, covering carbon, coastal protection, fisheries and
protected areas. Applied extraction skill v1.9.2 and effect/direction contracts to
screen admissibility. This is **screening and referral accounting, not completed
effect extraction**. No new search, source registration, EV units or human approvals.

## Findings

- Carbon: potential mature stocks combine biomass gains with soil gains and avoided
  losses. The report explicitly says they are not direct carbon gains. Do not map
  these totals or tonnes C/ha to VONT's annual `carbon_sequestration` rate. Two original
  carbon modelling sources need identity verification and acquisition.
- Coastal protection: the fitted model covers about 12.5 million currently protected
  people versus over 18 million in its parent model. The report explicitly forbids
  direct extrapolation to restorable areas. Neither population counts nor global
  avoided-damage totals are local restoration effect sizes. Narrative mechanisms
  and benefit timing remain candidates, with source lineage still to resolve.
- Fisheries: counts measure recruitment, not catch or income. Finfish include juveniles;
  invertebrates include all post-settlement year classes. Regional coverage differs,
  and West African invertebrate values are missing, not zero. No matching recruitment
  outcome found in current VONT. Preserve rather than force a proxy mapping.
- Internal conflicts: fisheries prose says 39 species (32+7), Table 6.1 caption says
  40. Headline restoration benefit is rounded to 60 trillion; components are 23+40
  trillion. Do not silently reconcile either discrepancy.
- Protected areas: loss differences are confounded by designation timing. Degradation
  differences are associations, not causal restoration effects. Regional reversals
  remain in retained tables. Protected areas can host restoration; their presence is
  not evidence of a universal exclusion mask. Governance and external-pressure
  passages remain explicit M2b/M6 pointers.

## Coverage and hand-off

`inventory.json` retains 27 items: 20 claim/figure dispositions plus all seven
text-extracted tables (4.1, 4.2, 5.1, 6.1, 6.2, 7.1, 7.2), including headers and rows.
Photo/caption pages 17, 23 and 27 are identified. Maps were not digitised; table cell
geometry has not been visually validated, so retained text is not admitted evidence.

Five distinct cited-source referrals are staged in the inventory: Hutchison carbon,
Sanderman soil carbon, Spalding coastal defence, Losada risk reduction, and Hutchison
fisheries enhancement. No exact title substring matches were found in current SRC or
acquisition queue. This is a bounded deduplication check, not authoritative identity
verification. No DOI invented, no queue acquisition claim. Guidance/synthesis sources
must themselves be traced to original studies; five referrals do not mean five
independent effect studies.

Next executable work: verify and acquire the five referrals using the discovery and
identity gates, then stage supported effects with their original lineage. Keep stock,
protected-population and fish-recruitment ontology questions visible. Existing five
Worthington T4/operational records remain unaltered and source remains in progress.

## Validation and learning

All 27 anchors match the current cached PDF directly using PyMuPDF; artifact SHA256
recorded. Inventory JSON parses; seven tables and five referrals accounted for.
`git diff --check` passes. No registers, generated outputs, ledger, reviewer decisions,
sweep metrics or global learning cursor changed. No extraction sweep occurred, so no
sweep-completion or metric-improvement claim. Existing proxy, context, secondary-source
and no-mechanism rules explain the holds; no new ruleset change needed.
