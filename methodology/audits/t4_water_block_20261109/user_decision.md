# Water-harvesting decisions, 9 November 2026

## 1. Catchment area

Pete approved holding the shared 1 ha minimum. The held mapping retains Kadam et al. (2012), Table 6, as quantitative siting evidence by structure. Farm ponds use a contributing area of 1–2 ha, check dams use >25 ha, and percolation tanks use 25–40 ha. The table leaves gully-plug area unspecified. Its linked conditions on slope, runoff, stream order, land use and soil remain part of each profile. The former shared bound and its derived uncertainty are archived with the mapping. [Verified source review](../t4_drainage_density_hold_20261109/next_catchment_area_decision.json)

The registry includes percolation tanks as groundwater-recharge structures in the runoff-catchment family. A tank impounds runoff and allows infiltration. Classifying a particular intervention as an NbS also requires an ecosystem protection, management or restoration action that benefits people and biodiversity. Kadam's area specification supports siting. It does not establish those ecological outcomes. [IUCN definition of nature-based solutions](https://inbs.iucn.org/understand/nbs-definition/)

## 2–3. Clay content

The two evidence records retain each study’s clay intervals, scores, source scale, modelling purpose and criterion weights. Kahinda et al. (2008), Table 4, PDF page 3, reports separate in-field and external-catchment harvesting columns. The comparison uses its in-field column. Krois & Schulte (2014), Table 4, PDF page 9, reports terrace and bund siting. Table 5, PDF page 10, reports the weights. The evidence IDs are `ev_wh_clay_content_kahinda08_1` and `ev_wh_soil_texture_krois14_1`.

For a given clay percentage, each paper contributes once. Kahinda uses ranks 1–5. Krois assigns 1, 3, 5, 7 and 9 to five ordered classes with clay ranges. Convert those scores to positions 1–5 using `(score + 1) / 2`, then take the arithmetic mean of the two studies’ positions. This descriptive average assumes equal spacing between adjacent ranks. The soil-texture weights of 0.17 (Kahinda in-field) and 0.15 (Krois) measure soil texture’s importance within each study’s model.

| Clay content | Kahinda in-field rank | Krois source score | Mean rank (1–5) |
|---|---:|---:|---:|
| 2% | 2–1 as printed | 3 | 1.5–2 |
| 10% | 4 | 7 | 4 |
| 20% | 5 | 9 | 5 |
| 50% or exactly 55% | 3 | 5 | 3 |
| Above 55% | 1 | 1 | 1 |

Above 55%, Kahinda calls the soil least suitable and Krois calls it “Not suitable”. Krois assigns no clay range to its separate “Restricted” category (score 0). The evidence records now encode the published categories. The existing family recipe mappings still carry their previous 55% bounds. The comparison expresses relative preference across the two study contexts. The full table leaves the mean blank wherever a source skips an interval or gives overlapping classes at an endpoint. [Full interval comparison](clay_rank_comparison.csv)
