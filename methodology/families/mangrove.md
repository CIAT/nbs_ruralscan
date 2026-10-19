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
