# Krois terracing runoff coefficient

On 7 November 2026 Pete approved retaining the full Krois table and source weight and applying the calibration hold to `water_harvesting__terracing__runoff_potential_index`.

Krois and Schulte mapped potential terrace and bund sites in the Ronquillo watershed in Peru. Their 30 m runoff coefficient is the estimated proportion of design-storm rainfall that becomes direct runoff under wet antecedent conditions. Table 4 (PDF p. 9) ranks this criterion as follows.

| Printed coefficient range | Suitability | Source score |
|---|---|---:|
| >0.9 | Optimal | 9 |
| 0.6–0.9 | High | 7 |
| 0.3–0.6 | Moderate | 5 |
| 0–0.3 | Marginal | 3 |

The authors print dashes for the unsuitable and restricted runoff classes. Table 5 (PDF p. 10) gives runoff coefficient an AHP criterion weight of **0.14**. The held mapping carries the complete source profile, including its six criterion weights, alongside the decision. The recipe's configured weight is 0.2.

The inherited single-bound response omitted the lower three ranks and treated 0.9 as an optimum. The recipe archives this former response and its derived uncertainty of ±20% under the calibration decision. Future synthesis needs an explicit score convention and treatment of the shared boundaries at 0.3 and 0.6. Dataset matching remains a separate requirement.

The [source review](../t4_calibration_hold_applied_20261106/next_terracing_decision.json) records the source and evidence fingerprints, native page excerpts, table inspection and measurement context. This decision applies to the terracing mapping. The [next dashboard review](next_stream_order_decision.json) covers runoff-catchment stream order.
