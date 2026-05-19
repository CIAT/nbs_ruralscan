---
name: Variable Card
about: Author or update a Variable Card for a specific NbS recipe
title: "[Variable Card] <variable name> in <NbS>"
labels: ["variable-card", "methodology"]
assignees: []
---

## Variable

**Name (display):** <!-- e.g. Land slope -->
**ID (snake_case):** <!-- e.g. slope -->
**NbS this card is for:** <!-- e.g. agroforestry -->
**Theme:** <!-- topographic · climatic · soil · lulc · socio-econ · hazard -->

## Cluster status

- [ ] Default cluster representative for this theme
- [ ] Represented by another variable (specify):
- [ ] Standalone (no correlated variables in this AOI)

## Six slots

### 1. What it is

<!-- One-sentence plain-language definition. -->

### 2. Why it's included (NbS-specific)

<!-- 1-3 sentences on why this variable matters for THIS NbS specifically. -->

### 3. How to read it

<!-- Interpretation: what high/low values mean for suitability. Include ranges if known. -->

### 4. What it represents (correlation cluster)

<!-- Variables it stands for, with correlation values. Populated after first AOI run. -->

### 5. Where it comes from

<!-- Dataset name, source, hosting status, GEE asset ID if applicable, native resolution. -->

### 6. Membership function preview

<!-- Type (sigmoid · linear · Gaussian · bell · inverted sigmoid · trapezoidal_fuzzy · ecocrop · ranked_classes) and parameters. -->

## Definition of done

- [ ] All six slots populated
- [ ] References cited
- [ ] Membership function diagram added to recipe page
- [ ] PR raised using PR template
