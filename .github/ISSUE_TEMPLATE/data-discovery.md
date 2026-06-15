---
name: Data Discovery & Ingestion
about: Discover, screen, and register literature, grey reports, and modeling/CBA tools for an NbS recipe table
title: "[Data Discovery] <NbS name> × <Table ID>"
labels: ["methodology", "documentation"]
assignees: []
---

## Objective

**Target NbS:** <!-- e.g. agroforestry -->
**Target Table/Step:** <!-- e.g. T3 (hazard mitigation), T4 (suitability), or T6 (scorecard) -->
**Focus Area:** <!-- e.g. drought and heat stress hazard evidence -->

## Discovery Plan

### 1. Programmatic Academic Query (OpenAlex)
*   **Search String (Title-only disjoined):**
    <!-- e.g. display_name.search:agroforestry AND (drought OR shade) -->
*   **Target Portal:** OpenAlex

### 2. Targeted Institutional Database Interrogations
Identify which specific portals will be queried and the search methods:
*   [ ] **WOCAT SLM Database (wocat.net)**:
    - *Method/Filters:* <!-- e.g., Filter by Technology Group = Agroforestry and Climate Adaptation -->
*   [ ] **FAO TECA Portal (teca.apps.fao.org)**:
    - *Method/Keywords:* <!-- e.g., SALT, agroforestry hazard mitigation -->
*   [ ] **World Bank Documents & Reports (documents.worldbank.org)**:
    - *Method/Filters:* <!-- e.g., Sector = Agriculture, keyword = agroforestry, hazard = drought -->
*   [ ] **Specialist Research Centers (ICRAF, CIFOR, WRI, University databases)**:
    - *Method/Keywords:* <!-- e.g., centerforagroforestry.org for riparian buffer design guidelines -->

---

## Screening & Ingestion Checklist

- [ ] **Formulate Organization-Neutral Queries**: Ensure web and database searches focus on functional terms, avoiding hardcoded organization filters in the search engine query.
- [ ] **Run Queries & Collect Candidates**: Ingest raw returns and list potential candidates.
- [ ] **Apply Six-Axis Credibility Rubric**: Evaluate each candidate for:
  1. *Evidence Strength* (empirical validation, study type)
  2. *Methodological Transparency* (open code/data)
  3. *Authority & Venue* (reputable peer-review or institutional standard)
  4. *Context Relevance & Transferability* (LMIC income group and AEZ alignment)
  5. *Recency* (newer papers preferred unless seminal)
  6. *Seminality & Influence* (citations, industry standard)
- [ ] **Compile PRISMA-lite Discovery Log**: Write or update the markdown log under `methodology/discovery_logs/<nbs>_<table>.md`.
- [ ] **Register Final Inclusions**:
  - [ ] Add approved sources to `schema/registers/SRC_source_register.csv`
  - [ ] Add atomic evidence rows to `schema/registers/EV_evidence_register.csv`
  - [ ] Map evidence IDs to recipe files (e.g., `T3_nbs_hazard_farming.csv` or `T4_suitability_rules.csv`)
- [ ] **Recompile Dashboard Data**: Run the schema generator:
  `python3 src/nbs_ruralscan/schema_tools/generate.py schema`
- [ ] **Run Alignment Verification**: Verify registry consistency:
  `python3 src/nbs_ruralscan/schema_tools/check_alignment.py`
- [ ] **Verify Test Suite**: Run `uv run pytest` and ensure all tests pass.
- [ ] **PR raised using PR template**
