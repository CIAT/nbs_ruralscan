# IUFRO restoration guidance: bounded T4 review, 2 November 2026

**Outcome: retain ecological claims and resolve the report's role, without adding unsupported or duplicate evidence cards.** This completes the remaining main-report accounting for the IUFRO lead from [primary-guidance recovery](../t4_primary_guidance_20261102/README.md). It does not complete its cited primary sources or 15 separately published case studies.

The source is Stanturf et al. (2015), *Forest Landscape Restoration as a Key Component of Climate Change Mitigation and Adaptation*, IUFRO World Series 34. The acquired publisher PDF has 75 native pages; native page 6 is printed page 3. Its immutable hash, team-library referral path and deterministic index checks are in `source_manifest.json`. No new discovery search, source promotion, EV ingestion, human approval or synthesis occurred.

## What this changes

The earlier recovery read the stoplight chapter and left the ecological chapters open. This audit accounts for every page and all ten numbered tables: **279 feature/activity row occurrences**, including continuations. These are inventory rows, not independent studies or admitted evidence. Chapters 4–5 received independent adversarial review against the original table images. The remaining tables, two numbered figures, three boxes, stoplight diagram and low-text pages have explicit dispositions.

- **Seed sources and dispersal:** native page 65 explicitly warns that natural regeneration can fail where seed sources are outside effective dispersal range. Favourable seed availability is retained as a `regeneration_potential` candidate. The passage does not resolve passive versus assisted regeneration and gives no distance or density threshold. This is a family/lineage hold, not rejection for lack of calibration.
- **Competing vegetation and grazing:** native page 37 supplies negative directions for regeneration under competition and uncontrolled grazing. These are retained raw properties. Neither has a matching competition/herbivory-pressure variable in the current ontology; livestock-system presence, NDVI and regeneration potential are not interchangeable proxies.
- **Shared guidance:** Table 4.1 explicitly attributes ecological conditions to **IUCN and WRI (2014)**, whose bibliography entry is ROAM. Do not silently change that attribution to Hanson et al. (2015), or count a new independent WRI vote. The seed paragraph also mixes natural regeneration, nursery supply and ANR enrichment; this project's ANR family excludes planting.
- **Global opportunity rules:** native pages 30–31 retain population bands and remoteness criteria from Minnemeyer (2011)/Laestadius (2012). These define global restoration types, not local biological suitability. The caption's density-within-radius definition and prose's distance-from-settlements wording remain distinct.
- **Species tools:** native page 51 points to species/provenance mapping. The bibliography separates Kindt (2014), a conference abstract, from Kindt (2015), the Vegetationmap4africa-based Google Earth species distribution project. Their code/docs are follow-up seeds, not already reviewed tool implementations or practice-level climate envelopes.

## Stoplight findings

Source colours do not have one stable analytical meaning. The diagram distinguishes implementation status from future priority. Tables 6.2–6.4 describe priority, stakeholder judgement and alternatives; no colour is a calibrated establishment score.

Two source inconsistencies are now explicit: native page 55 describes Table 6.1 in desirability terms, while the actual native-page-56 header/legend says implementation level; the same prose describes Table 6.5 as positive/negative/neutral benefits, while its native-page-60 legend says In place/Partly in place/Not in place. Native page 50 also points resistance/resilience readers to Table 5.3 although the corresponding activity rows are in Table 5.2. Use actual page/table anchors and retain the ambiguity. Hypothetical colour cells are neither measured effects nor validated suitability classes.

## Coverage and retained work

| File | Content |
|---|---|
| `page_coverage.json` | All 75 native pages; bibliography is a targeted reference screen, not acquisition of every citation |
| `ecological_activity_rows.json` | 153 rows across Tables 4.1 and 5.1–5.3, including all continuations |
| `other_table_rows.json` | Six rows of Table 2.1 and 24 activity rows in each of five stoplight examples |
| `claim_inventory.json` | 13 page-linked claim/hold groups, raw directions and reported population/radius/timing values |
| `asset_inventory.json` | Figures, boxes, diagram and unreviewed case-study supplement |
| `followup_seeds.json` | Six title-only leads; no unverified DOI or acquisition claim |
| `adversarial.md` | Independent omissions, scope, direction and calibration review |

All 11 low-text pages were visually checked: covers, blank pages or decorative separators, not missing analytical tables. Machine indexing found 23 table fragments; that is not the number of numbered tables. Photographic site examples are not establishment thresholds. Policy/funding amounts are historical 2015 context, not current advice. Economic, operational and effect material stays as page-linked referrals for the relevant lanes; this batch does not alter T3/T6 work.

**Counts:** zero new EV; zero demonstrated practice-level suitability models; zero calibrated T4 functions; zero approvals. Supported qualitative directions remain visible in the inventory. No SRC is marked swept and no whole-family progress or search completion is claimed.

## Next substantive batch

Prioritise the original **Stanturf et al. (2014), Contemporary forest restoration: A review emphasizing function**, for the actual regeneration barriers and practice boundaries. Pair it with the **Laestadius/Minnemeyer atlas method** to resolve what the reported population/land-cover rules were designed to do. Keep **Vegetationmap4africa/Kindt** in a separate species-tool assessment, inspecting actual implementation before extracting model-use claims. These are proposed follow-ups, not work already completed.
