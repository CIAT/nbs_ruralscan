# Mangrove restoration — suitability-family scheme

**Status:** signed off by Pete Steward, 2026-10-19 (team lead; not yet MFL). Promoted to its own
NbS by Pete: "on mangroves these will be a separate category of restoration in the project and
the worldbank team want to include these for pilot." MFL domain review (Sarah Jones, Chris
Kettle, Evert Thomas, Hannes Gaisberger) still welcome and may amend the scheme, but it no
longer blocks use.

## Why its own NbS, not a forest-restoration family

The dominant limiting factors differ in kind, not degree, from terrestrial forest: tidal position
and hydroperiod, salinity, coastal geomorphology (accreting vs eroding shoreline), propagule
supply. None of the terrestrial families' suitability logic (rainfall envelope, slope, soil depth)
transfers. The evidence base is also distinct — coastal protection, surge and wave attenuation,
silvo-aquaculture — and the World Bank team wants it pilotable on its own.

## The scheme, deliberately one family to start

| family | subpractices | dominant limiting factor | spatial product |
|---|---|---|---|
| `mangrove_restoration__tidal_coastal` | Mangrove planting; Ecological mangrove restoration (EMR — hydrological/tidal re-establishment with natural recruitment) | tidal position / hydroperiod · salinity · coastal geomorphology | area_suitability |

Both subpractices establish or re-establish mangrove on the same tidal envelope; what differs is
the METHOD (plant vs restore hydrology and let propagules arrive), and the evidence says method is
the main determinant of success — the Vietnamese record holds measured accretion where siting and
establishment worked and a whole province's planting washed out where they did not. Method is
therefore carried per unit (`practice_as_described`), not as separate suitability families, until
the evidence shows the two need different suitability surfaces.

**Open question for MFL:** should EMR split out as its own family once suitability evidence
arrives? Its limiting factor arguably adds hydrological connectivity (can the tide be restored at
all), which is closer to the wetland `floodplain_wetland_reconnection` logic.

## What moved at the promotion (2026-10-19)

149 evidence units and 26 sources re-homed from `forest_restoration__mangrove_coastal`; recipes
split (mangrove T3 11 rows / T6 17 on 117 pooled effect units); comparator policy (existing and
reference mangrove stands), effect locus (`mixed`: protection lands behind the stand, fishery and
silvo-aquaculture value can accrue on it) and review-page vocabulary carried over. Three
predominantly-mangrove World Bank evaluations previously skipped on practice grounds (Vietnam,
Mexico, Guinea-Bissau) are now in scope for a dedicated extraction lane.

## Reading the practice definition (T0)

The [mangrove T0](../../schema/recipes/mangrove_restoration/T0_nbs_registry.csv)
uses the stocktake's Forest & Tree Systems catalogue group (`tree_based`). The
tidal-coastal family defines its suitability. Landscape is the unit of planning.
The `all` farming-system entry allows any adjoining farming system to be considered.
The restoration footprint still depends on local coastal conditions.

The `long_horizon` economic profile reflects the time and continuing care needed
to restore a functioning stand. The Bangladesh afforestation case reports negative
short-term and positive long-term returns to establishment and maintenance
(WOCAT technology 4300). Blue-carbon projects can qualify for crediting under a
recognised standard once they demonstrate eligibility and verified removals.
The `moderate` evidence rating describes this broad practice profile. Su et al.
(2021) synthesised restoration outcomes across studies, but recovery varied by
the function assessed, stand age and comparator. Individual effects and costs
carry their own confidence and transfer assessments in T3, T6 and T6E.

Three operational inputs remain open. The timing objects in T0 have null values.
The CSV leaves the recurrent cost class empty, and its typed JSON omits that field.

| Required input | Evidence and use |
|---|---|
| Establishment period | Lewis (2005, section 5) describes 15–30 years for secondary succession where tides and propagule supply permit natural recovery. That interval measures recovery of a forest. Specify the local establishment endpoint and vulnerability window before using M2b's establishment-period adjustment. |
| Time to benefit | Fisheries, hydrological function and soil carbon change over different periods. Choose the benefit and its measurable endpoint before specifying a time range. See Beeston et al. (2023), section 5 on monitoring. |
| Recurrent cost class | WOCAT reports annual maintenance costs of USD 241.07/ha in Bangladesh (technology 4300) and USD 20/ha in the Philippines (technology 578). T6E preserves the cost basis and income-group scope. Set a local class from the intervention's maintenance plan and cost context. |

T0 also leaves the optional upfront cost range empty. Read
[T6E](../../schema/recipes/mangrove_restoration/T6E_economic_profile.csv) for
establishment costs by income group. The source register records the studies and
guidance named in T0's primary references.
