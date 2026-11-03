# Integrated fire management: bounded stocktake reconciliation

3 November 2026. **Six original stocktake papers reconciled; four retained as intervention-planning method candidates, one hazard/priority referral and one monitoring-infrastructure referral.** This closes the requested six-paper methods pass. It does not complete global fire-management discovery, adopt new families, validate treatment effects or generate T4 rules.

The practical recommendation is two provisional families: **ecological fire-regime management** and **ecologically compatible vegetation/fuel management**. See [family proposal](../../families/integrated_fire_management.md). Wildfire hazard is a reason to investigate management, not proof that burning is appropriate. In fire-sensitive ecosystems the relevant intervention may be avoiding damaging fire, protecting/restoring vegetation or modifying fuels; do not infer a prescribed-fire opportunity from a hazard map.

## Scope, provenance and exact search

Discovery skill v1.8.1 applied as a bounded stock reconciliation, not a fresh search. Exact query:

```text
NbS_Practice == 'Integrated fire management' in reference/stocktake/peer_reviewed_benchmarked.csv
```

Six returned, six screened, four included as method candidates. All six PDFs were already in the shared stocktake library. No PDF acquisition or citation chase was necessary. **Six DOI/title identities** were round-trip checked with the repository Crossref metadata helper and matched to opening PDF text. `source_manifest.json` stores canonical metadata, native PDF page counts, SHA-256 hashes, and team-library-relative paths. Wang's truncated stocktake DOI was replaced only in this audit with the complete publisher DOI; historical stocktake files remain unchanged.

`criteria.csv` contains 53 criterion/group records. Native PDF page references refer to these exact hashed copies. This is targeted methods/table review, not an exhaustive extraction of every page, bibliography or supplement. Numeric values are retained as source context, not approved rules. No EV, SRC, FAM, recipe, review decision or progress-ledger completion was written.

| Process | Actual work | Status |
|---|---|---|
| Stock | Six existing records, local full texts, identity and method reconciliation | Bounded pass complete; not search saturation |
| Updated literature | No new search | Not run; no zero-yield claim |
| Grey literature | No new search | Not run; no zero-yield claim |
| Tools/code | Tool use and availability statements in six papers checked | No repository or executable audit; no code-validation claim |

`protocols.json`, `screening.json` and `candidates.json` retain the actual inspected set. Candidate family lists are deliberately empty: the new practice/families are proposals, not registered identifiers. Central registration and extraction remain pending a scope/family decision; this is not a completed SRCH/ledger lane. No unsupported file type was ingested.

## Six source dispositions

| Source | What the primary method actually supports | Disposition and limits |
|---|---|---|
| Nepal et al. 2023, Southern US | Bayesian network comparing enhanced prescribed-fire investment with business as usual; fuel, fire potential/intensity, recent climate, smoke, population vulnerability, carbon and water-service risk. Native pp. 6–10, Figs. 3–4. | Include strategic investment method. Approximate halving of fuel over a 5–10-year investment horizon is a modeled decision assumption, not measured treatment effectiveness. The 1,000-ha units and >=25% forest classification domain are not global burn eligibility thresholds. |
| Rodrigues et al. 2022, Catalonia | Occurrence × initial-attack success zoning, refined by modeled transmission to communities. Zones distinguish comprehensive management, ignition prevention, intensive fuel management and fire reintroduction. Native pp. 3–7; Fig. 4 visually inspected. | Include zoning/management-method candidate. Fire reintroduction is conditional on ecological/social appropriateness and control prospects; high-risk zones are not automatically prescribed-fire zones. Road proximity has different ignition and suppression roles. |
| Rodríguez-Fernández et al. 2025, Portugal | Four criterion groups, 17 subcriteria, locally elicited priority-function endpoints and AHP weights across 2,429 management units. Native pp. 4–9; all Table 1–3 entries on p. 8 visually checked. | Include vegetation/fuel-treatment prioritisation. Explicitly prescriptive, not predictive. Local endpoints are not treatment eligibility or ecological thresholds. Suppression/access criteria belong in operational context. |
| Sakti et al. 2022, Indonesia | Five-input wildfire susceptibility index plus carbon-stock and gas-emission indices; 1-km composite priority ranking. Native pp. 4–9, Tables 1–2/input descriptions and equations. | Hazard/priority referral. Does not identify an ecologically appropriate intervention or establish prescribed-fire applicability. Preserve Indonesian relevance without pretending it validates treatment in tropical forests or peatlands. |
| Wang et al. 2025, China | Terrain visibility, road access and costs for monitoring-point location; AHP-weighted objectives and improved genetic algorithm. Native pp. 5–9. | Outside NbS intervention evidence; retain M6 monitoring referral. Actual DOI is `10.1371/journal.pone.0338090`; actual weighting is AHP, not stocktake FUCOM. Do not repurpose tower-site suitability as vegetation-treatment suitability. |
| Nocentini et al. 2024, Everglades | Ecotype-specific time-since-fire, habitat/species constraints, resource protection, invasive plants, hydrology and logistical scheduling. Native pp. 6–14; complete Table 1 across pp. 9–12 visually checked. | Include ecological-fire scheduling method. Reviewed copy is Research Square v1 preprint. Explicitly excludes mangroves. Local return-interval preferences and burn-priority scores are not global prescriptions. Simulation against target return intervals is not independent field validation. |

### Credibility and transferability

These are method dispositions, not new official benchmark assignments. Inherited stocktake tiers are Medium for five articles and Low for the preprint. The following six-axis assessment explains how they should be used:

| Source | Evidence strength | Transparency | Authority/venue | Context/transfer | Recency/version | Seminality and independence |
|---|---|---|---|---|---|---|
| Nepal | Expert-conditioned model and sensitivity, no independent causal efficacy test | Network, inputs and linked model described | Peer-reviewed; USDA authorship | Southern US, regional calibration; no LMIC demonstration | 2023 article | Not established as seminal here; utility depends on expert assumptions, not independent validation of treatment benefit |
| Rodrigues | Observed ignition/attack model training and cross-validation; simulated transmission | Predictor, scenario and zoning workflow explicit | Peer-reviewed Safety Science | Mediterranean Spain; operational capability context specific | 2022 article | Reuses earlier component models; do not count every component as independent efficacy evidence |
| Rodríguez-Fernández | Participatory consensus/sensitivity, visual checks rather than outcome prediction | All 17 endpoints and weights available; aggregation ambiguities below | Peer-reviewed Frontiers; tool-developer affiliations present | Portugal; stakeholder preferences not globally transferable | 2025 article | No seminality claim; software-author involvement is not independent product validation |
| Sakti | Composite-index consistency analysis, not intervention trial | Index equations and datasets described; harmonisation limitations | Peer-reviewed Remote Sensing | Indonesia gives tropical context; no direct treatment validation | 2022 article | Shared/co-varying proxies do not become independent votes; no seminality claim |
| Wang | Algorithm/scenario performance for infrastructure objectives | Objective functions and comparisons explicit | Peer-reviewed PLOS One | China; tower network rather than NbS | 2025 article | Computational optimisation does not validate NbS outcomes; no seminality claim |
| Nocentini | Manager-designed model and simulated return-interval matching | Detailed criteria table; local/sensitive inputs not all reproducible | Preprint v1, practitioner/research collaboration | Everglades ecotypes/species; no tropical-forest or LMIC extrapolation | May 2024 v1; later-version status not investigated | Not independent field validation; no seminality claim |

No source warrants a high-confidence global practice-response curve from this bounded review. Four intervention-linked sources are US/European; the Indonesian paper is hazard/priority only. **LMIC ecological-treatment transfer remains an explicit gap**, not evidence of no local practices.

## Criteria routing

- **Candidate applicability (T4 concept):** existing ecosystem/vegetation identity, fire-regime compatibility, and presence of a treatable fuel/vegetation system. Nocentini's domain and Rodrigues's ecological qualification support keeping this gate separate from priority. Numeric global gates are not supplied by this batch.
- **Ecological need/management priority (M4):** departure from locally appropriate fire regime, time since fire, modifiable fuel structure, spread/transmission leverage, habitat management objectives and values protected. Higher priority does not mean safer burning.
- **Hazard/exposure (M2):** drought, weather anomalies, ignition likelihood, burn intensity and exposed people/ecosystem services. Do not add the same risk proxy repeatedly through multiple indices.
- **Operational feasibility/project-risk context (M2b/M6):** access, slope as suppression difficulty, water points, control capability, smoke/receptor concerns, treatment-unit logistics, local permissions and delivery capacity. These do not define the ecological T4 envelope.
- **Outside NbS practice footprint:** monitoring towers, detection networks, fire trucks and hard suppression infrastructure. Useful supporting services, not hectares of NbS.

Time since fire is not a universal increasing suitability curve: a recent burn can lower priority or harm a specific habitat, and a fire-sensitive ecosystem can remain outside prescribed-fire scope regardless of elapsed time. Nocentini's source-specific species schedules are retained in the inventory rather than generalized.

## Numeric and implementation holds

1. **Nocentini Table 1:** pine-rockland time-since-fire schedule gives 6–7 years and >8 years, leaving year 8 unspecified. Keep gap; do not interpolate. Ecotype-specific 30% terms are alternatives, not three additive inputs. Negative species scores are deliberate source values. The dry/intermediate/wet ranking is restoration-management priority based on multi-year mean water depth, not safe ignition conditions. Its data-availability statement says public data, but p. 13 describes sensitive cultural sites and unpublished recent fire records; reproducibility is therefore qualified.
2. **Rodríguez-Fernández Tables 1–3:** “min–max” means endpoints of minimum-to-maximum priority, including descending raw values. Suppression subweights total 0.995 as printed; preserve rather than silently repair. Equations/prose describe inverse Spearman weighting while saying greater agreement gains weight; implementation needs checking before reuse. Stakeholder consensus and stable sensitivity are not validation of ecological benefit.
3. **Nepal:** approximate 50% fuel reduction is an assumed intervention scenario. Input ranges, index scales, forest-cover domain and vulnerability weights are not transferable eligibility thresholds. Network sensitivity is not evidence that burning everywhere with large modeled utility is feasible.
4. **Sakti:** quantile classes are data-dependent. Carbon products/compartments and correlated hazard/emission proxies need harmonisation review before adopting the composite. Table 1 gives ERA5 resolution as 30 km while p. 5 says 270 km; population resolution is 100 m in Table 1 but approximately 1 km in p. 6 prose. These conflicting source specifications must be resolved before dataset binding. No treatment-effect or intervention-applicability claim is derived.
5. **Rodrigues:** <10 ha initial-attack success and >50 ha escaped-fire labels are training definitions, not treatment-unit rules; 40 m grids and extreme-weather/concurrent-fire scenarios are model design choices.
6. **Wang:** the stocktake method/DOI discrepancy is material; use verified primary identity and infrastructure routing, not the original extracted variable list.

## Tools and reproducibility

Netica 6.07 and the linked Nepal model, FlamMap/R/caret in Rodrigues, EMDS/CDP/ArcGIS and supplementary Python aggregation in Rodríguez-Fernández, ArcGIS workflows in Sakti/Nocentini, and Wang's optimisation algorithm are **named method dependencies**, not audited codebases. Nepal p. 25 reference 51 identifies a Zenodo model/data companion; Nocentini p. 31 lists a Word supplement. These were not acquired or executed. A new model-file format requires its own intake/locator rule before ingestion; no adapter was improvised. Sakti p. 23 reports data available upon request; no contact was made.

## Closeout and next decision

Six fixed sources have source-linked dispositions and retained criteria. Stop here: no seventh paper, no implied literature saturation. Review the two-family proposal as one scope decision. The next implementation step, if adopted, is one coordinated schema/recipe change followed by evidence-first extraction and explicit local-context holds—not six individual source PRs or a fire-hazard map relabelled as NbS opportunity.
