# Agroforestry T4 v0.1.1

Presentation update; T4 rules, source assignments and weights unchanged from v0.1.0.

Open [rule table](index.html). Theme and variable group now have separate columns. Numeric rules have plotted source bands with shared axis ranges within each measurement unit; no interpolation or automatic pooling. Open endpoints, unbounded tails and unknown scores remain explicit. Plots show retained source responses; a separate existing threshold is still the runtime default until source selection.

Weight column exposes equal numeric defaults (0.2), unweighted gates, and available within-study relative-importance ratios. These diagnostic ratios do not replace runtime weights. Different source model variants remain separate.

[Practice vocabulary](practice_vocabulary.csv) comes directly from FAM: Agroforestry → suitability system → named practice. This registry is the current configured vocabulary; family-scheme sign-off remains pending in methodology/families/agroforestry.md. Registry membership is not evidence that each rule applies to every listed practice.

Five numeric rows retain unassigned system applicability. Haile's parkland evidence does not establish planted versus regenerated trees; Chuma's responses are regional; Ahmad's NDVI model covers mixed agroforestry systems. Blanket planted-silvoarable assignment is not adopted. A labelled transfer sensitivity scenario can be considered separately without rewriting source evidence.

See [release scope and remaining integration limits](../README.md). Rebuild plots using `uv run --no-project --with matplotlib python scripts/plot-t4-release.py`, then `PYTHONPATH=src python3 scripts/release-t4-first-pass.py`.
