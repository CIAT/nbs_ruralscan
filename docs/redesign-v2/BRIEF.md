# Rural NbS Scan — v1b design brief (direction A: "Atlas")

Status: exploration, 31 Oct 2026. Not published. Three prototype screens + one
alternative-direction sketch, for Pete's visual decision. No analytical rules,
schema or backend. All numbers are labelled example values.

## What this is
A visual explanation of a scoping method for World Bank TTLs. Not a production
dashboard. Six stages in locked order:
Setup → Opportunity Space → Project Risk → Priority Hotspots → NbS Comparison → Next Steps.
Keep these method distinctions visibly separate: suitability (can the NbS
establish) · livelihood need (M2, who needs it) · NbS response (what evidence
says it does) · investment risk (M2b, hazard to the project; a filter/flag,
never summed). Hard legal exclusions ≠ low suitability ≠ unknown data ≠ context.
Residents are not beneficiaries. Overlap is not compatibility. Linear practices
report km of zone, not installed hectares.

## Root failures of v0/v1 (what the redesign must fix)
1. Fixture pattern: v1 tiles 12 authored values with `(gi/3*3+gj/4*7)%12` →
   periodic blocks. v0 used radial blobs + per-cell hash → salt-and-pepper.
   Fix the data, not the paint: coherent seeded multi-octave value noise.
2. Chrome before content: version bar + header + scope strip + tabs + sub-tabs
   eat ~35% of the first viewport. Map is one tile among many equal cards.
3. No primary question per screen; sidebars of toggles + 3 columns of charts.
4. Typography: mono eyebrows, small chips, abbreviations (VH/H/M/L/X), no scale.
5. Cartography: heavy black outline, hatched ocean, labels fighting data,
   detached legend, percentage labels inside every district.
6. Caveats as content: "illustrative" repeated 3–4× per screen.
7. Landing opens on a form ("What should this project improve?") before any
   background.

## Direction A — "Atlas" (build this)
Each stage is a chapter spread: a question, one dominant figure, a reading
column, then optional depth. The page reads top-to-bottom like an atlas plate
with marginalia; it is operated only where operation teaches something.

### Page anatomy (every stage)
1. **Stage bar** (sticky, 48px): project name left · six-stage stepper centre
   (number + name, current filled, done ticked, next outlined) · "Technical
   configuration" ghost button right. Nothing else.
2. **Scope line** (one quiet line under the bar, 13px): "Showing · Agroforestry
   (planted silvoarable) · classes Very high + High · Sierra Leone · 5 km cells ·
   Baseline 1995–2014 · Example data". Each item is a link that opens the
   configuration drawer at that item. This replaces the v0 coloured strip.
3. **Chapter head**: small-caps eyebrow "Stage 02 · Opportunity space" ·
   display question (36–44px) · one-sentence "what you do here" · one-sentence
   "what you take away". Max 65ch.
4. **Plate**: the dominant figure, full content width (max 1200px), ratio
   ~ 3:2. Map plates carry title block top-left inside the plate (title,
   subtitle, scope), legend bottom-left inside, scale + north bottom-right,
   source line under the plate in 12px. One plate per stage; variants are
   switched with a segmented control ABOVE the plate (max 3 options).
5. **Reading column**: beside or under the plate, 3–4 short numbered notes
   "How to read this" + 2–3 key figures as a quiet definition list (not tiles).
6. **Go deeper**: accordion rows (closed by default), each with a one-line
   summary. Technical config lives in the right-hand drawer, not here.
7. **Next stage** footer: one sentence + button.
Caveat policy: ONE example-data marker inside each plate ("Example data —
authored surface, not a pilot result") and one line under it. Nowhere else on
the screen. Method limits go in the reading notes as reading, not warnings.

### Tokens (put in `v1b.css` :root; both themes; also dark)
- Paper `#f7f7f4` (cool-grey bias, NOT cream) · ink `#1f2a26` · ink-2 `#51605a`
  · rule `#d9ddd9` · surface `#ffffff`.
- Accent (UI only, links, current step): deep teal `#0f6e63`.
- Suitability ramp (4 classes, light→dark): `#d8ebdc #93c7a3 #3f9a6e #136c47`.
  Low = `#e3e8e4`-ish; Unknown = dotted `#eceeec`; Excluded = diagonal hatch
  `#b7bdb9` on paper; Outside scope = paper.
- Need/priority ramp (plum): `#ead9e6 #c79fbf #9a5b8e #5e2a58`.
- Hazard: fire `#c4542a`, flood `#2c6e9b`, both `#6b4a8f`.
- Ocean `#eef2f3`; neighbouring land `#f1f1ee`; ADM0 line `#6f7a75` 1px;
  ADM2 line `#aab3ae` 0.6px; labels `#51605a`.
- Type: display `Newsreader` (serif, 500/600, text-wrap balance); body + UI
  `Source Sans 3`; data & map labels `Source Sans 3` with tabular-nums; small
  caps labels letter-spacing .06em. Google Fonts link + fallback stacks.
- Scale: 13 / 15 / 17 / 22 / 28 / 40. Line-height 1.5 body. Radius 4px max;
  shadows none; borders not cards. Controls: 36px tall, 1px rule, 4px radius.

### Cartography spec
- Reuse `docs/sle_geo.js` (geoBoundaries gbOpen v6) and the projection /
  grid code pattern in `docs/sle_map.js` (copy what you need into
  `docs/redesign/v1b-map.js`; do not edit the originals).
- Cells drawn as crisp 5 km squares (no smoothing, no rounding, no blur). Cell
  edges visible only at zoom; at plate size use fill only (no stroke).
- Layer order: ocean · neighbouring land · cells · ADM2 lines · ADM0 line ·
  water bodies (if any) · cities (3 dots: Freetown, Bo, Kenema; small) ·
  ADM2 labels (small caps, halo 2px paper) · plate title block · legend ·
  scale + north.
- Legend: horizontal swatches with words (Very high · High · Moderate · Low ·
  Excluded · Unknown), 12px, inside plate, white 85% panel.
- Admin view: choropleth of share-of-cells by district, 5 equal-interval
  bins, labels only for the top 3 districts (name + %), others name only.
  Keep cell view available in the same plate via the segmented control
  ("5 km cells" | "District summary") — admin view never hides cells.
- Small-area inset: a 20×20 km box near Bo showing 5 km cells over a 100 ha
  vector exclusion parcel (hatched) — demonstrates raster grain vs small
  vector honestly (Bank "small vectors" question). Place as an inset frame
  bottom-right of the Project Risk plate or as a second small plate.

### Synthetic surface spec (`v1b-fixture.js`)
- Seeded value noise (hash-based lattice + smoothstep interpolation),
  3 octaves (wavelengths ≈ 90 km, 40 km, 18 km; amplitudes 1, .5, .25),
  per theme: `suit` (plus macro gradient: SE uplands higher, north drier,
  coastal strip lower), `need` (east + north higher), `fire` (north/east),
  `flood` (coast + river-like SW–NE low band), `slope` (SE + NE).
- Classes: suit quantiles → VH 15 % · H 25 % · M 30 % · L 30 %. Exclusions:
  urban discs around the 3 cities (r 8–12 km), coastal mangrove/wetland band
  (coast < 6 km on the SW shore), two "protected area" blobs (NE and SE,
  ~30 km) — all coherent shapes. Unknown: one cloud-gap polygon in the north
  (~ 4 % of cells). Everything deterministic from seed 20261031.
- Expose `FIXTURE.cells[] = {lon,lat,x,y,w,h,adm2,suit,suitClass,need,
  needClass,fire,flood,slope,excluded:reason|null,unknown}` and per-district
  roll-ups (count by class, share VH+H, residents = authored integer).
- Header comment: SYNTHETIC EXAMPLE SURFACE — no thresholds, weights or
  evidence; not derived from any schema table.

## Screens to prototype (direction A)
### 1 `01-setup.html` — Landing / Setup
Above the fold: eyebrow "Rural NbS Scan · method demonstrator" · headline
"Where could nature-based solutions pay off for rural people?" · 2–3
sentences: the problem (TTLs scope investments before feasibility; need to
know where which NbS fits, who is there, what the evidence says) · who it is
for · what you leave with (an opportunity map, a hotspot shortlist, a
practice comparison, a draft scoping brief — all scoping grade).
Then a **method strip**: six small plates in a row (thumbnail map or glyph
per stage, stage number, 4-word label, one-line question) — this IS the
navigation explanation. Then "What this is / is not" as two short columns
(scoping vs feasibility; demonstrator vs final UI; example data vs pilot
result). Then "Start the walkthrough" → a compact three-step setup:
(1) challenge + 2–3 objectives (chips, example preselected: Climate
resilience + Livelihoods), (2) practices (3 example practices, radio-style
cards with a 1-line footprint type), (3) geography + climate (Sierra Leone ·
5 km · Baseline / SSP2-4.5 2050). Side note: "Technical configuration"
explains dataset choice vs rule tuning as two separate things, opened from
the drawer. Footer → "Open Stage 02".
### 2 `02-opportunity.html` — map-heavy
Question: "Where could planted silvoarable agroforestry establish?" Plate:
suitability cells, segmented control [5 km cells | District summary | Change
to 2050]. Reading notes: classes; what excluded/unknown mean; cells vs
farms; 2050 is a shift of the envelope not a prediction. Key figures: VH+H
area (ha, nominal) · share of country · districts with > 50 % · excluded ha
by reason (3 rows). Go deeper: "Why is a cell excluded?" (reason list with
source type) · "Hard exclusions vs low suitability vs unknown" · "Soft
operational factors are not here (→ Stage 03)". Include the small-area
inset on this plate OR on 03 — pick 02 if it fits.
Also render a second plate state for **Project Risk** in the same file
(anchor `#risk`) if cheap: hazards segmented [Fire | Flood | Both] over the
SELECTED opportunity cells only; outside-scope cells in paper. This gives Pete
the raster-and-admin pair in one screen.
### 3 `05-comparison.html` — compact comparison + budget
Question: "Which practices deserve closer investigation?" One table, three
practice rows, columns: footprint (VH+H ha as a proportional bar, with
"zone km" for the linear practice) · overlap with need (share) · what it
addresses (3–4 problem rows with strength glyph + confidence word, e.g.
"Drought · moderate benefit · medium confidence") · indicative cost band
(establishment $/ha range, source class) · affordable area at the budget.
Budget box ABOVE the table: amount · currency · year · "establishment only /
with 3-yr maintenance" toggle; results update the last column live. Five
Bank indicators as a short crosswalk under the table (indicator · what the
scan can report · what it cannot). Single footer line for units/denominators.
### 4 `direction-b.html` — alternative, grey-box only
"Workbench": persistent left rail (six stages vertical), map canvas filling
the viewport, right inspector drawer (scope, layers, config), bottom
"reading" strip. Grey boxes + labels + one real map plate. ~1 screen. Show
why it reads as a product dashboard.

## Files
`docs/redesign/` : `v1b.css` · `v1b-map.js` · `v1b-fixture.js` ·
`01-setup.html` · `02-opportunity.html` · `05-comparison.html` ·
`direction-b.html` · `index.html` (links + one-paragraph intro). Plain HTML,
no frameworks, no CDNs except Google Fonts. Pages must render from
`file://` and from `python3 -m http.server` in `docs/`. Mobile (390 px) must
not scroll sideways; the plate stacks above the reading column.

## Don'ts
No new thresholds/weights presented as method. No live MCDA implication
(objective chips change labels only). No BCR/NPV/payback. No "beneficiaries".
No emoji. No tiles-of-big-numbers grids. No colour-coded chips VH/H/M/L —
use words. No disclaimer banners. Keep tab order. Don't edit any file
outside `docs/redesign/` and don't run git.

---
# Round 2 — carry direction A through stages 03, 04, 06 (31 Oct 2026, Pete: proceed with A)

Same tokens, anatomy, cartography and surface. Same don'ts. One plate per
stage. Build:

## `03-risk.html` — Project risk (move the #risk plate out of 02 into its own page; 02 keeps only the suitability plate and its "Open Stage 03" footer)
- Question: "Which of these places would put the planting itself at risk?"
  Do-line: screen the opportunity space for hazards to the investment during
  the establishment period. Take-away: a flag on each place, never a change
  to suitability or need.
- Plate: segmented [Fire | Flood | Both] over SELECTED opportunity cells
  only; outside-scope cells in paper. Second control under the plate:
  "District summary" toggle (share of opportunity cells flagged, top 3
  labelled). Three hazard classes (High · Moderate · Low) + "outside".
- **Trade-off control (Bank asked where the TTL makes this call):** a
  two-option segmented control titled "What should a flag do?" —
  "Keep flagged places and show the flag" (default) · "Remove High-flag
  places from the shortlist". A one-line consequence updates live:
  "Shortlist keeps 2,742,500 ha; 410,000 ha carry a High fire flag" vs
  "Shortlist drops to 2,332,500 ha". Numbers come from FIXTURE roll-ups.
- Reading notes (4): risk to the investment (M2b) vs need (M2) — kept
  separate, never summed; young trees are the exposed asset — the
  establishment period is 5 years here; a flag is exposure, not a loss
  rate, and there is no overall risk score; what an NbS mitigates and what
  damages it are independent questions.
- Key figures: opportunity ha · High fire ha · High flood ha · both ·
  share of opportunity flagged.
- Go deeper (3): "Levers a project can change" — road access, market
  access, tenure, extension, finance, each with status "Local verification
  required" (not spatial, not scored); "What the establishment evidence
  says" — one source-class line per practice (practitioner guidance /
  review), no quotes, no numbers; "Why there is no overall risk rating".
- Footer → Open Stage 04.

## `04-hotspots.html` — Priority hotspots
- Question: "Where does the opportunity meet the project's priorities?"
  Do-line: overlay the need layers chosen for the objectives on the
  opportunity space. Take-away: a hotspot shortlist by cell and by district.
- Top strip under the chapter head: "Selected priorities · Climate
  resilience + Livelihoods (set in Stage 01)" with the three example need
  layers they bring (drought exposure · rural poverty · food insecurity)
  as plain words, and one sentence: these frame which layers are shown;
  the example preset does not re-weight anything.
- Plate: segmented [Need | Hotspots | District summary]. Need = plum ramp
  (4 classes) over opportunity cells; Hotspots = two-colour: hotspot
  (opportunity ∩ High/Very-high need) in deep plum, opportunity-not-hotspot
  in the pale suitability green, outside in paper; District summary = share
  of opportunity cells that are hotspots, 5 bins, top 3 labelled.
- Side card inside the reading column, quiet, titled "National context":
  "Gender inequality index 0.61 (example). One value for the whole country:
  it describes the setting, it cannot rank districts." No map toggle.
- Reading notes (4): a hotspot is an intersection, not a sum; need layers
  are proxies at 5 km, one representative per correlated cluster; people
  in hotspot cells live there — they are not beneficiaries; the district
  view summarises, it does not locate sites.
- Key figures: hotspot ha · share of opportunity · residents in hotspot
  cells (fictional, labelled) · top 3 districts with share.
- Go deeper (3): "How need layers are chosen" (thematic group → correlation
  cluster → one representative; others kept visible); "Why national data
  cannot rank districts"; "Change priorities" (opens the drawer, which for
  now is a static list of two presets).
- Footer → Open Stage 05.

## `06-next.html` — Next steps
- Question: "What must feasibility confirm before anyone invests?"
  Do-line: take the shortlist into a scoping brief and a hand-off. Take-
  away: a brief you can paste into a concept note, and the list of what
  this scan could not check.
- Plate = the **scoping brief**, rendered as a document page (A4 proportion
  card on the paper background): title "Scoping brief — planted
  silvoarable agroforestry, Sierra Leone (example)"; scope line; three
  short prose paragraphs — opportunity area (ha, share, districts), hotspots
  and project-risk flags (ha, top districts, flagged share), indicative cost
  and affordable area at the Stage-05 budget — each paragraph ends with its
  qualification in the same voice (nominal cells, example surface, costs
  undiscounted from mixed sources); a small map thumbnail (hotspots) with
  legend; "Assumptions" list (6 lines); "Questions for feasibility" list
  (6 lines: local prices, tenure and FPIC, parcel-level exclusions,
  hydrology, adoption, baseline design). Buttons: "Copy brief text" (works,
  clipboard) · "Download example map (PNG)" (links to a static PNG you
  render from the hotspot plate and save as docs/redesign/example-map.png).
- Below the plate, "What happens next — outside this tool", three columns
  with the same quiet definition-list treatment: Local co-production
  (partners validate included AND excluded areas, rights and FPIC,
  delivery arrangements, adoption); Feasibility studies (hydrology, site
  design, costs, safeguards, cost–benefit); Monitoring baseline (indicators,
  responsibilities, contribution vs attribution). Label each column
  "Not a stage of this scan".
- Reading column lead note (Evert's concern, keep its force): scoping gives
  the shape of the problem and the opportunity; implementing without
  bottom-up refinement with partners carries a high risk of poor return.
  Then: what can be reused (maps, figures, assumptions) vs what must be
  re-done locally.
- Two ghost buttons, bottom of reading column, labelled "(concept)":
  "Draft the brief with AI" · "Ask the evidence base". No live service.
- Footer → "Back to Stage 01" and "Open the overview".

## Housekeeping
- 01-setup.html: method strip thumbnails for 03, 04, 06 become real
  (fire plate, hotspot plate, brief glyph); stepper links go to the new
  files; nothing else changes on 01, 02, 05 except removing the #risk
  section from 02 and fixing its footer link.
- index.html: list all six pages.
- Render and eyeball desktop + mobile as before; fix what reads badly.
