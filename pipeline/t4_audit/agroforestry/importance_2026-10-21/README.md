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
