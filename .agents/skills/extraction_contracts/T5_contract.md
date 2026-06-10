# Extraction Contract — T5 (Opportunity Space Variables)

Use this contract as instruction when extracting evidence units intended to support **T5** registry rows.

## Target Objective
T5 represents the opportunity-space layers that reflect World Bank TTL priorities (climate hazards, people & production, equity & inclusion). We extract justifications for why these variables serve as valid targeting metrics.

---

## 1. Required Variables & Fields

For each extracted priority variable, map to the following parameters:

### `mcda_role` (Enum)
Classify based on the priority's role:
* `priority` — Used directly in the MCDA hotspots overlay to rank candidate sites (M4).
* `descriptor` — Not scored in MCDA, but carried for descriptive overlay and narrative intersection (e.g. total population).

### `theme` (Enum)
Must map exactly to one of:
* `climate_hazard` (e.g. drought hazard, flood hazard)
* `nbs_response` (e.g. carbon sequestration potential)
* `people_production` (e.g. rural poverty, production gap)
* `equity_inclusion` (e.g. GESI, IPLC lands)
* `context` (descriptors like farm size, agricultural value)

---

## 2. In-Paper Evidence Guidelines

1. **Selection Justification**: Extract quotes explaining *why* a variable was chosen as a priority proxy (e.g. "We select poverty headcount as it represents the population with the lowest adaptive capacity").
2. **Spatial Grain Validity**: Look for mentions of the spatial grain at which the priority differentiates context (admin1 level, grid level, national flag).
3. **Proximate-over-Distal Verification**: Ensure that the variable represents a proximate indicator of target vulnerability or benefit rather than a distal, compound-uncertainty indicator.
