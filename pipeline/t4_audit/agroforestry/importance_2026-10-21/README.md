# Within-study variable importance audit

Bounded diagnostic: three existing papers, five alternative representations, 72 variable comparisons. Does not modify EV approval, T4 suitability functions or runtime weights.

Rebuild from repository root:

```sh
PYTHONPATH=src python3 scripts/report-t4-importance.py
```

Input: `source_weight_trees.csv`. Outputs: `comparison.csv`, `results.json`, and `docs/review/t4-importance-comparison.html`. Source PDFs remain in the existing team corpus; hashes identify the versions inspected. The generator verifies hashes when PDFs are locally available.

Source reconstruction:
- Singh 2026 Table 2, PDF p8: all 15 factors, both RF importance and printed relative weights. Flat model; weights attributed to Singh 2022. Printed relative weights total 99%. These are two representations of one model, not independent votes.
- Nath 2021 Table 2, PDF p11; weighted-overlay methods pp10–11: five top-level groups; complete nested weights. Rooting conditions contain four equally weighted inputs, not additional topsoil/subsoil group levels. pH enters nutrient and rooting branches; additive contributions aggregate separately for each depth. 26 leaf paths become 24 distinct inputs.
- Haile 2024 Table 3, PDF pp4–5, versus Table 5 p9: conflicting five-criterion weight sets. Both use the five equal nutrient subweights from Table 4 pp5–6. Table 5 totals 99.9%. Alternatives retained separately; no settled choice.

Every original input remains in the comparison denominator, including access variables outside structural T4. Audit variable names preserve source distinctions and do not establish new canonical ontology mappings. Positive RF importance is compared on its own scale, not pooled numerically with expert/AHP weights.

Open decisions: Haile table conflict; compatibility and independence for any later cross-study synthesis. Source ratio calculations themselves do not resolve geographic transferability, response-function conflicts, or runtime weight selection.

## Candidate comparison follow-up

`candidate_scenarios.csv` declares model variants and the common-variable subset. `scripts/report-t4-candidate-weights.py` generates `candidate_results.json` and `docs/review/t4-candidate-weights.html`. Pooling uses medians of hierarchy-adjusted ratios, then normalises within the explicitly declared subset. One representation per lineage is enforced; missing variables hold rather than changing the panel silently.

This is a two-variable transfer sensitivity experiment across regional models, not a claim that their full models, agroforestry families or ecological responses are interchangeable. Slope and annual rainfall share definitions and source direction. Their numeric suitability curves are not pooled here. Mean temperature has only two-model coverage. Soil variables need depth alignment; distinct moisture/access measures are not merged.

Direction evidence is the existing bounded-review manifest: Singh claims (Table 1 p4), Nath table_rows (Table 2 p11), Haile table_rows (slope p7 and rainfall p5). Each reports decreasing slope/increasing precipitation; these inspection counts do not confer human approval. Eligible denominator here is the three reconstructed models, not the full evidence corpus.

Haile §3.2 and Table 5 p9 identify the computed AHP weights. Column-normalise the printed 5×5 matrix and average rows: [34.5511,29.5367,18.9507,10.4772,6.4842]%. These approximately reproduce Table 5, not Table 3. Paper does not establish which set produced the final map, so Table 5 is provisional for diagnostics only. Table 3 sensitivity remains visible.

## Family evidence coverage

`PYTHONPATH=src python3 scripts/report-t4-family-coverage.py` generates `family_coverage.json` and `docs/review/t4-family-coverage.html` directly from EV/SRC CSV and configured T4 CSV. This makes the system applicability gap visible beside the importance scenarios. It does not run synthesis or assign shared regional evidence to named families.

Counts include only active general-practice structural evidence. DOI/source identity deduplicates records, but is not a guarantee of independent publication lineage. Human-reviewed counts mean at least one retained approved record in the cell, not approval of every claim. Explicit model use, canonical response direction and observed presence are separate counts. Species/crop and operational evidence are outside general-practice counts; configured crop-host mappings remain visible separately. Direction disagreement within a paper counts as one conflict, not two votes. Missing canonical direction is not proof of no response.

Current inventory has 60 family-variable cells across six represented system columns. FMNR annual rainfall retains seven reviewed source identities, including five explicitly typed observed-presence sources; no rainfall mapping is currently configured. These records must not be converted to hard establishment limits merely to fill a table cell. Current T4 mapping evidence references were checked: none refer directly to dropped or missing evidence IDs.

## Two-level Nath importance summary (2026-10-23)

`nath_concept_mapping.csv` explicitly maps every source path to a theme and variable. `report-t4-importance.py` produces `nath_consolidated.json` and the two-level table in the existing importance report. The complete source tree remains unchanged. Repeated nutrient/rooting and topsoil/subsoil contributions are summed, not averaged. This yields 19 model variables, including seven soil variables whose weights total 20%. pH totals 4%; SOC totals 2%. Their ratios to the mean consolidated variable weight (1/19) are 0.76 and 0.38. Original hierarchy-adjusted ratios retain the original tree benchmark.

This diagnostic does not merge depth-specific suitability functions, select a cross-paper runtime weight, or add source votes. Eight Nath clarification records now explain the result directly in the normal review queue. Drainage-code interpretation and incompatible source class boundaries remain separate unresolved issues.

## Ahmad 2018 recovered model-use chain (2026-10-23)

Tables 1/2 and Figures 2/8 (PDF pp4/8) explicitly connect SOC to agroforestry suitability through soil fertility. Five soil inputs each receive 20% of soil fertility; soil fertility receives 45.8% of the final overlay. Slope 17.2%, wetness 22.6%, NDVI 14.4% complete the model. The eight-input tree is now inventoried: SOC nominal allocation 9.16%, hierarchy benchmark ratio 1.832, flat eight-input ratio 0.7328.

These products describe nominal allocations through weighted stages. Soil fertility is reclassified before final overlay, so they are not output sensitivities or equivalent single-stage runtime weights. No automatic pooling with the existing three-paper candidate panel. Six variants now represent four papers; inherited lineage still prevents counting Singh's two representations twice.
