# Discovery log — Agroforestry · F3 Silvopastoral · T4 (Suitability)

- **NbS / family:** `agroforestry` / `agroforestry__silvopastoral` (F3)
- **Table:** T4 (suitability rules)
- **Run:** `silvopastoral_t4_2026-08` · **date:** 2026-08-04 · **by:** Pete/Claude
- **Ruleset:** v1.4.1
- **Scope of this run:** targeted discovery + screening only. **No extraction** — evidence
  units are parked until the queued paywalled PDFs are acquired (see acquisition queue).

## Why this run

F3 already carried ~110 EV rows tagged `agroforestry__silvopastoral`, but all from the
**generic (family-agnostic) net** — there was **no targeted F3 SRCH row**, so per the search
protocol F3 was *"covered by the generic net, not targeted"*, never *searched=done*. PR #204
synthesised **0** silvopastoral T4 rows. This run runs the four discovery processes
specifically for F3 × T4 and logs the protocol.

## The four processes (PRISMA-lite)

| process | channel | retrieved | screened | included |
|---|---|---|---|---|
| **stock** | OpenAlex title.search, seminal/high-cite slice | 454 (focused net) | 18 | 3 |
| **updated_lit** | OpenAlex recent slice + suitability-mapping method | 454 | 18 | 4 |
| **grey** | WebSearch EN (extension/authority orgs) | 8 | 8 | 3 |
| **tool** | GitHub + WebSearch | 7 | 2 | 1 |

### Search strings (verbatim)

- **OpenAlex (stock + updated_lit):**
  `title.search: (silvopasture OR silvopastoral OR silvopastoril OR sylvopastoral OR silvipastoril) AND (suitability OR suitable OR potential OR establishment OR density OR stocking OR forage OR grazing OR shade OR slope OR aridity OR rainfall)`
  `sort=cited_by_count:desc`. Practice net alone = 3,203; T4-focused net = **454**.
- **grey (WebSearch):** `silvopasture silvopastoral system establishment guidelines tree density stocking rate suitability manual FAO CIPAV WOCAT`
- **tool (WebSearch + GitHub):** `silvopasture land suitability mapping GIS tool GitHub grazing agroforestry site selection model`

### Screening funnel

`frame · source_type · relevance · credibility_six_axis · saturation_stop`. Inclusion: F3
silvopasture practice **explicit** in the source (PICOS); claim bears on T4 suitability
(biophysical envelope + grazing/forage/stocking **system_constraint**). Excluded:
per-species tree-growth envelopes, low-tier/predatory venues, constrained-AOI site
descriptors, uncacheable sources.

## Screened-in candidates (→ extraction later)

**stock (closed-access → acquisition queue):**
1. `peri_patagonia_waterbalance_2002` — Silvopastoral systems NW Patagonia II: water balance
   (DOI 10.1023/A:1020269432671). T4 water/aridity envelope. **queued.**
2. `pasture_tree_density_atlantic_2007` — Pasture production under tree species & densities,
   Atlantic silvopasture (DOI 10.1007/s10457-007-9032-2). T4 tree-density→forage. **queued.**
3. `shrestha_alavalapati_2003` — Potential for silvopasture adoption, S-central Florida
   (DOI 10.1016/j.agsy.2003.09.004). Seminal but adoption/economic (→ T6-leaning); noted, not
   queued this run.

**updated_lit (OA — auto-cacheable via hydrate/ingest at extraction):**
4. SciELO `s0103-90162010000500014` — soil bulk density & Brachiaria biomass in silvopasture
   (gold OA). T4 soil/density.
5. AGEE `agee.2016.08.026` — forage dry mass vs tree arrangement, Piatã grass (bronze OA). T4.
6. EJA `eja.2020.126029` — microclimate/canopy of shaded palisadegrass (hybrid). T4 shade.
7. ERL `10.1088/1748-9326/adab09` — social-ecological suitability of agroforestry (incl.
   silvopasture), US Midwest (gold OA). T4 method/criteria; companion to the tool below.

**grey (OA PDFs — cacheable):**
8. Center for Agroforestry *Agroforestry Training Manual 2025*, Ch.4 Silvopasture.
9. UF/IFAS **FR145** — *Establishment of Silvopasture in Existing Pastures* (density 100–450
   trees/acre; site conditions).
10. OSU Extension **EM8989** — *Silvopasture: An Agroforestry Practice*.

**tool (interrogate code — file:line + commit):**
11. `saraheb3/AgroforestrySuitability_GEE` @ `af338e8` (MIT). PICOS confirmed:
    `gee_script/Agroforestry-Suitability-Map:79` → `practice==3 = silvopasture`; the
    silvopasture branch gates applicability to CDL pasture (class 176) ∧ non-forest — a
    `system_constraint` rule (silvopasture where grazing land already exists). Per-species
    tree-growth scripts **excluded** (species envelopes). Dataset = US CDL/NASS →
    temperate-US **context caveat**; `claim_basis=expert_assertion`.

## Gaps / caveats for next iteration

- **LMIC context thin.** Confirmed sources skew Brazil/Patagonia (peer-reviewed) and US
  extension (grey/tool). **CIPAV / Latin-American intensive-silvopastoral (ISPS)** material
  — the strongest LMIC-grounded density/stocking source (fodder shrubs 4,000–40,000/ha;
  trees 100–600/ha) — was referenced but not located as a citable artefact. Targeted CIPAV /
  WOCAT / FAO-TECA search is the top follow-up.
- Six-axis **context axis** should downweight the US-extension and US-CDL tool rules for
  LMIC scoping; the *logic* (pasture-land gate; density→forage tradeoff; water balance)
  transfers even where the datasets don't.

## Cross-references

- SRCH rows: `agroforestry__T4__{stock,updated_lit,grey,tool}__agroforestry__silvopastoral__2026-08-04`
- Acquisition queue: `pipeline/acquisition_queue.csv` (2 pending, `Namita-J`).
- Ledger: `agroforestry · T4 · {4 cats} · agroforestry__silvopastoral` → searched=done,
  screened=done, verified=not_started.
