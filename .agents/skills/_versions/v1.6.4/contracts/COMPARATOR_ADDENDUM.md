# v1.6.4 addendum — comparator tag (2026-10-07)

Applies on top of `T3_T6_extraction_contract.md` (PICOS). Units stamped `ruleset_version = v1.6.4`; earlier units stay valid and are back-tagged in place.

## `context.comparator = existing_forest`

Set on an `nbs_effect` unit whose source measures **what existing forest does, or what its loss costs** — not what a restoration practice delivered:

* forest-vs-cleared or forest-cover contrasts (flood, landslide, erosion, local temperature, diets near forest);
* existing-mangrove protection measurements and models (storm-surge, wave attenuation, people / property protected "if current mangroves were lost");
* forest-harvest / conversion studies (`framing = loss`).

NOT set on: restoration, planting, regeneration or forestation studies (including forestation effects on water yield), community-forest-management outcome studies (deforestation under CFM, CFUG income), restoration cost studies, planted-mangrove measurements.

## Synthesis (PICOS B, Pete 2026-10-07)

`schema/lookups/comparator_policy.csv` says, per NbS × comparator: `rollup_included` (false) and `home_family`. Tagged units are **kept out of the NbS roll-up row and out of every family row except their own**; a tagged `cross_family` unit is pooled into `home_family` (protection / community forestry — the practice that keeps existing forest standing). They stay in the register and in the family row where the evidence is defensible.
