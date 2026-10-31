# Mini-Buoy handbook: T4 companion review, 31 October 2026

## Result

Recovered the 18-page handbook from the same immutable repository commit inspected in
`../mangrove_code_20261029/`. Verified its opening title, author/date on PDF18, exact Git
blob identity and matching local corpus/team-library copies. Cloud synchronization is
not verified. The PDF remains an unregistered companion artifact; no queue, SRC, EV,
T4/T3/T6 table, progress stamp or human decision changed.

The handbook **does not resolve the code's lower suitability cutoff**. PDF14 repeats a
warning below 100 minutes/day, but PDF15 lists Southeast Asian species groups in bands
10–100 and below 10 minutes/day. A general exclusion below 100 would reject conditions
that the same guide recommends for some species. Preserve this conflict; do not choose
one rule or count handbook and code as independent studies.

## Use, direction and calibration

- **Use:** instrument-supported site assessment, with either known target conditions or
  a reference site where the target species recently colonised or restoration succeeded.
  Both inundation per day and per event are used. Current exposure and consecutive
  inundation-free periods are additional diagnostics.
- **Direction:** inundation at the target should not exceed the suitable reference under
  the given conditions (PDF15). This is a conditional comparison, not a globally decreasing
  hydroperiod function. Higher concurrent 75th-percentile current velocity than reference
  warrants investigation (PDF16), not an unconditional exclusion.
- **Calibration:** four species bands are preserved together in `claims.json`, including
  literal spelling, units, region and cited Van Loon 2007 lineage. Daily and per-event
  duration remain distinct. No response scores, endpoint closure, species optimum or
  global practice-level thresholds are inferred. The dry-window metric is consecutive
  days, not percent time flooded, and refers to pioneer natural recruitment.

## Handbook versus pinned code

Code artifact: `R shiny app mangrove restoration GITHUB.R`, commit
`01c86d95bc7d8197d1606de6e6ba187a43edfd4b`, lines 421–433 (target) and
812–824 (reference). Previous audit records its hash and locators.

| Diagnostic | Handbook PDF14 | Code | Consequence |
|---|---|---|---|
| Tidal-pattern warning | exceeds 24 hours; prose says per day | mean event duration >=1,440 minutes | Metric wording and exact boundary differ; measurement check, not biological limit |
| Short deployment | shorter than 15 days | <=15 days | Exactly 15 days differs; PDF8 separately recommends more than 15, preferably 30 |
| Velocity detection | 75th percentile same as median; around 0.1 m/s detection floor | absolute percentile-minus-median <=0.01 m/s | Equality description differs from numerical tolerance; these are not the same as the absolute detection floor |
| Low/high current | low <=15 cm/s, high >15 | low <0.15 m/s, otherwise high | Exactly 15 cm/s classified differently; high does not itself mean unsuitable |
| Daily duration | warning >800 or <100 minutes/day | same strict boundaries | Agrees with code but conflicts with PDF15 species guidance below 100 |
| Dry window | below one day suggests unsuitable | message “No WoO detected” below one day | PDF16 qualifies pioneer recruitment and measurement-season dependence |

`boundary_checks.json` evaluates the literal expressions for four illustrative cases.
It does not run R or validate biological predictions. No upstream code was changed.

## Coverage and limitations

All 18 pages were read as text. PDF14–15 were also rendered and inspected visually to
check the warning prose and all four species rows. Twelve exact-page excerpts preserve
assessment claims, method context, authorship and references. Pages 4–12 concern apparatus,
programming, deployment and export; their settings and material dimensions are not
suitability thresholds. The screenshot summary/difference tables on PDF14–15 are example
outputs (eight indicators), not input-response calibration. Their individual numeric
observations were not transcribed as evidence. PDF13 links the app and repository;
PDF17 cites Balke 2011 and Van Loon 2007. The “LINK TO PUBLICATION” label on PDF3 has no
URI annotation in this artifact. No unidentified associated paper was treated as read.

The earlier raw-dataset and dedicated-code admission holds remain in force. This PDF
adds reviewable companion provenance, but it cannot itself settle primary calibration,
transferability, or code identity/admission policy. No new source completion claimed.

## Adversarial assessment and retrospective

Coordinating-agent assessment; no independent reviewer or human approval claimed.
The main defect prevented is promoting a tool's broad screening message into a universal
T4 hard threshold despite species-specific contradictory guidance. Existing rules on
scope, conflicting source values, lineage and proxy metrics cover this; no ruleset change
or empty extraction-sweep metric is warranted. Human-review and learning cursors remain
unchanged. These findings narrow the original code audit's calibration hold.

Validation: source title and Git blob match; local library/cache bytes match; all 12
quotes match their PDF pages; four species rows retained; literal code-boundary checks
pass. Shared evidence and generated files are untouched.
