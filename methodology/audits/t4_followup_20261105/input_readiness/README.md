# Matching spatial inputs for the four reviewed wetland profiles

5 November 2026. Bounded input-fitness assessment following merged PR #595. No new evidence units, dataset intake, bindings, scores, family definitions or eligibility approvals are created here. Candidate datasets below are discovery pointers only. The four policy-controlled binding holds remain in force.

## Input requirements

| Profile | Required spatial quantity | Input route and acceptance check | What cannot substitute |
|---|---|---|---|
| Creation water distance | Horizontal distance in metres to a frequently flowing stream capable of supplying the eligible site | Hydrography with documented flow permanence, supplemented by local water-supply knowledge; retain source vertical/topographic delivery context. Derive distance from verified features before aggregation. Record time period, feature completeness, projection and positional uncertainty. | MERIT upstream drainage area is not flow permanence or water availability. JRC water presence alone does not establish stream flow or deliverable supply. |
| Former-wetland farmland water depth | Mean lowest groundwater depth below ground in cm, with the source's low-water statistic and hydrological-year definition documented | National/local groundwater model or observations with documented temporal aggregation, ground datum, sign and validated error. Require an observed drained-former-wetland farmland eligibility mask. Confirm source statistic before deriving from a generic time series. | Annual mean groundwater depth, height above drainage, terrain wetness, or an arbitrary dry-season snapshot. Coarse global monthly groundwater depth is not automatically fit for 30/80/160 cm bands. |
| Groundwater seepage | Annual-average vertical flux from the first aquifer toward the phreatic water table, mm/day; negative upward, positive downward | Local/national groundwater model matching the flux interface, averaging period and sign convention. Preserve original sign and document any conversion. Source input represents 2013–2019. Qualitative classes only until normalized scores are explicitly approved. | Recharge, surface runoff, canal flow, groundwater abstraction or groundwater depth. Correct units alone do not establish matching physics. |
| Restoration habitat distance | Horizontal distance in metres to the union of existing riparian habitat and open water, among eligible restoration sites | Current observed riparian-habitat extent plus open-water extent; document habitat definition, date, coverage and registration. Derive distance to the combined geometry. Inspect positional uncertainty before interpreting the narrow 90–120 m band. | Distance to generic rivers alone; surface-water extent alone; assumed riparian vegetation buffered from rivers. |

These are input checks, not new suitability thresholds. No universal positional-error tolerance or groundwater-error cutoff is invented. A dataset ID or nominal grid size cannot certify fitness. Applicability/eligibility masks require their own traceable definitions; the profile's prose scope does not implement a spatial mask.

## Native source check

Brouwer et al. (2026), cached source `page_nl_paludiculture_crop_suitability_model`, §2.2 (PDF pp. 2–3) describes 250 m national groundwater-model inputs and mean low-water conditions; Table 1 contains the reviewed classes. §2.5.3 (PDF p. 5) identifies Dutch LHM inputs representative of 2013–2019 and an annual-average seepage flux. The flux interface is first aquifer to phreatic water table (§2.2 continuation on p. 3).

Temporal-definition caveat: §2.2 describes three lowest-water months; §2.5.3 describes three lowest levels in a hydrological year. The approved review used the former wording. An input provider must reconcile these definitions rather than silently deriving a new statistic from monthly data. This note does not change the approved class boundaries or substitute a different statistic.

Source-local 250 m resolution is not a validation of global 250 m data or of finer resampled grids. The Dutch inputs are an existence proof for the required type of data, not a pilot-country binding.

## Candidate checks against primary documentation

- **MERIT Hydro:** approximately 90 m flow direction, upstream drainage area, channel width and permanent-water mask are documented. Inference: these do not establish the reviewed supply criterion or riparian vegetation extent. Retain as hydrography context, not automatic replacement for either distance input. [Earth Engine producer catalog](https://developers.google.com/earth-engine/datasets/catalog/MERIT_Hydro_v1_0_1).
- **JRC GSW v1.4:** 30 m surface-water occurrence and seasonality; potential open-water component only. It does not supply the required riparian-habitat component. [Earth Engine producer catalog](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater).
- **JRC newer release:** producer documents 1984–2024 summaries, corrections to older occurrence/seasonality processing, and spatially varying registration offsets when combining Landsat collections. Monthly recurrence also has a documented unresolved issue. Therefore do not silently upgrade the existing v1.4 registry row or select an occurrence/permanence cutoff. Pin version and inspect local alignment before use. [Producer update notes](https://global-surface-water.appspot.com/download), checked 5 November 2026.
- **GLOBGM v1.1:** published monthly global groundwater head/depth at approximately 1 km. Authors report mean water-table-depth bias of 3.6 m after calibration, with depth-weighted bias 32.5 m. Inference: published validation does not establish discrimination of these sub-metre wetland classes in a target AOI. Candidate background information; not an accepted substitute or local error estimate. [Primary model paper, abstract and §2.1](https://esd.copernicus.org/articles/17/1201/2026/).

## Routing decision

Keep all four existing binding holds. Do not add generic BIND fallbacks: `distance_to_waterbody` is shared with other families and currently resolves to MERIT/JRC candidates, whereas these two reviewed profiles require different feature semantics. A family/profile-specific input contract or explicit local input is needed before activation. No change to unrelated riparian bindings is authorized by this check.

Next review proceeds through the evidence queue while these documented input requirements remain open. This assessment does not certify absence of every suitable dataset worldwide, and does not require a new broad literature sweep.

## Export defect and correction

Checking the developer package exposed a second binding path: recipe generation preserved the matching-input holds, but developer export independently resolved the shared variable through BIND and offered MERIT for both distance profiles. Selecting a response could therefore conceal the unresolved measurement requirement.

Developer export now preserves the reviewed adaptation and original source relationship on each function option; explicit matching-input requirements suppress dataset/asset fallback and remain blockers after selection. Readiness lists the input requirement separately from defined response logic. Unrelated bindings and function payloads retain their existing behavior. No evidence, analytical CSV, scientific score or scope is changed.

Validation: all four wetland package rows retain null dataset/asset and explicit input holds; source/adaptation provenance survives export. Package input/output hashes verify. Regression checks include both distance profiles after explicit selection, malformed requirements and unrelated binding behavior. Review triage exactly reconciles to 647 pending register records; no new human decisions are applied.
