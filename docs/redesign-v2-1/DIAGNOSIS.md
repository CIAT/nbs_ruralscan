# Wireframe redesign — diagnosis and two directions

31 October 2026 · for Pete's visual decision · exploration only (not published,
no analytical change, T4–Diego wiring stays deferred).

## What you decide
Pick a visual direction (A or B, or a hybrid) from the rendered prototypes in
this folder. Nothing is rolled across the six stages until you choose. Merged
PRs and passing checks on v1 are not treated as visual approval.

## Sources used, kept separate
- **Stakeholder comments (authoritative):** feedback sheet rows from Laurent,
  Dinara, Pete (28 Oct); Bank written follow-ups (small vectors, five
  indicators, hydrology boundary, budget box, need-vs-risk trade-off); Pete's
  direct chat verdicts ("strange landing page", "the maps look shit").
- **Simulated agent reviews (advisory only):** V01–V17 from the 28 Oct audit.
  Used for method-consistency checks, never as stakeholder requests.

## Five root failures (why v0 and v1 both read badly)

1. **The map data is the problem before the map style is.**
   v1's fixture tiles twelve authored values with `(gi/3·3 + gj/4·7) mod 12`,
   so the raster repeats in blocks across the country (the rejected orange
   block map). v0 used radial gradients plus a per-cell hash, which gives
   salt-and-pepper speckle. No palette fixes a surface that looks authored.
   v1's "district summary" default hid the problem instead of fixing it.
   Fix: one coherent seeded noise surface (large, medium, fine wavelengths)
   with macro gradients; exclusions as real shapes (urban discs, coastal
   wetland band, two protected-area blobs); unknown as one cloud-gap. Cells
   stay crisp 5 km squares. District view is a roll-up of the same cells and
   sits beside the cells, never instead of them.

2. **Chrome before content.** Version bar + app header + coloured scope strip
   + stage tabs + sub-tabs consume about a third of the first screen. The map
   then shares the remaining space with three equal-weight sidebars. Nothing
   is dominant, so nothing explains.
   Fix: one 48 px stage bar, one quiet scope line, then the chapter question
   and one dominant plate.

3. **No primary question per stage.** Each tab is a grid of panels (levers,
   exclusions, context, fingerprint, risk, response, archetype) competing at
   equal weight. Dinara's "overloaded" and Pete's "cognitive burden extremely
   high" are the same finding.
   Fix: chapter anatomy — question · plate · how-to-read notes · go-deeper
   accordion · next stage. Technical configuration lives in a drawer.

4. **Typography and labelling.** Monospace eyebrows, 10 px chips, VH/H/M/L/X
   abbreviations, mixed label cases, no type scale. v1 replaced chips with
   paragraphs, which traded density for wall-of-text.
   Fix: a six-step scale, a serif display face for questions, one sans for
   everything else, words instead of codes, tabular numerals.

5. **Caveats as content.** "Illustrative", "mock", "not pilot results" appear
   three to four times per screen, in banners, strips and footers. Readers
   stop reading them, and they crowd out the method limits that matter
   (cells are not farms; residents are not beneficiaries; overlap is not
   compatibility).
   Fix: one example-data marker inside each plate, one source line under it.
   Method limits become reading notes.

Cartography specifics behind failure 1: heavy black country outline over a
hatched ocean; district labels in the same weight and colour as city labels;
Freetown in bold black competing with data; legend detached from the plate;
a percentage label inside every district; green data on a green-grey base.

## Direction A — "Atlas" (recommended)
Each stage is an atlas plate with marginalia: a question, one dominant map or
table, a reading column, optional depth. The page is read top to bottom and
operated only where operation teaches something (switch cells/district, switch
hazard, enter a budget).

- Fits the brief: Pete's "visual representation of a methodological approach",
  "sections rather than cognitive overload", "not a generic geospatial dash".
- Fits the audience: TTLs read it once in a meeting; it should read like a
  well-made report page, not a GIS console.
- Cost: lowest. Static plates, little state, easy to keep honest.
- Risk: can feel passive; mitigated by real segmented controls on the plate
  and the budget box, and by the technical drawer for people who want levers.

## Direction B — "Workbench"
Persistent left rail of six stages, map canvas filling the viewport, right
inspector drawer for scope/layers/config, reading strip along the bottom.

- Fits: people who expect a tool; multi-practice and multi-layer comparison
  is natural; everything is always one click away.
- Cost: higher. State management across stages; density creeps back; every
  screen needs the full layer stack.
- Risk: it is a production-dashboard idiom, which the proposal does not
  commit to and which Pete flagged as the pattern to avoid. It also invites
  the Bank to read it as a product promise.

Rendered as a grey-box composition (`direction-b.html`) so the difference is
visible, not argued.

## Recommendation
Direction A, borrowing one element from B: the right-hand configuration
drawer, opened from the scope line, for dataset choice and rule inspection
(kept secondary, as Pete asked). Decide after viewing the three A screens.

## What the prototypes do and do not show
- Show: landing/setup, opportunity space (cells, district, 2050; project-risk
  hazard state), compact comparison with budget box and the five Bank
  indicators; mobile stacking.
- Do not show: Hotspots, Next Steps, the drawer internals, save/load, AI
  entry points. These follow the chosen direction.
- Every number is an authored example. No threshold, weight or evidence row
  was created; nothing reads the schema.

## How to answer
Reply with one of: "A", "B", "A with …", or a list of what you dislike in the
renders. Specific is better than polite: "the map ramp is too pale", "the
question is too big", "the comparison table needs the overlap column first".
