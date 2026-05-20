#!/usr/bin/env bash
# One-time label setup for the NbS Rural Scan repo.
# Requires GitHub CLI (`gh`) installed and authenticated.
# Run from the repo root: bash .github/setup-labels.sh

set -e

REPO="CIAT/nbs_ruralscan"

echo "Setting up labels for $REPO..."

# Helper: create or update a label
add_label() {
  local name=$1
  local color=$2
  local desc=$3
  gh label create "$name" --color "$color" --description "$desc" --repo "$REPO" 2>/dev/null \
    || gh label edit "$name" --color "$color" --description "$desc" --repo "$REPO"
}

# Type labels (blue family)
add_label "recipe"        "0c447c" "Per-NbS recipe authoring or update"
add_label "variable-card" "0c447c" "Variable Card authoring or update"
add_label "module-spec"   "0c447c" "Module spec sheet (M0-M6)"
add_label "pilot"         "0c447c" "Phase 3 pilot implementation"
add_label "methodology"   "3c3489" "Cross-cutting methodology"
add_label "app"           "3c3489" "GEE App design or implementation"
add_label "bug"           "8c2e0e" "Something is broken"
add_label "documentation" "5f5e5a" "Documentation and READMEs"

# Module labels (green family)
add_label "M0-setup"             "085041" "Module 0 — Setup & Scope"
add_label "M1-suitability"       "1f7a4d" "Module 1 — Suitability → Opportunity Space"
add_label "M2-climate-risk"      "27500a" "Module 2 — Rural Climate Risk"
add_label "M3-characterisation"  "27500a" "Module 3 — Opportunity Space Characterisation"
add_label "M4-hotspots"          "27500a" "Module 4 — TTL Hotspots (MCDA)"
add_label "M5-scorecard"         "72243e" "Module 5 — NbS Scorecard & Response"
add_label "M6-handoff"           "633806" "Module 6 — Implementation Hand-off"

# NbS labels (earth tones — add more as recipes are authored)
add_label "agroforestry"      "4ca57c" "Agroforestry NbS"
add_label "water-harvesting"  "c4b04a" "Water Harvesting & Conservation NbS"
add_label "forest-restoration" "1f7a4d" "Forest Restoration / ANR"
add_label "riparian-buffer"   "0c447c" "Riparian Buffers / Floodplain Management"

# Phase labels (orange family)
add_label "phase-2-methodology" "c98a3a" "Phase 2 — Methodology Development"
add_label "phase-3-pilot"       "b87f33" "Phase 3 — Piloting"

# Status labels (red/grey family)
add_label "blocked"      "8c2e0e" "Blocked on something external"
add_label "needs-review" "c98a3a" "PR or content waiting on review"
add_label "up-for-grabs" "5f5e5a" "Anyone on the team can pick this up"

# Priority labels
add_label "priority-high"   "8c2e0e" "Address this week"
add_label "priority-medium" "c98a3a" "Address this month"
add_label "priority-low"    "5f5e5a" "Address eventually"

echo "Done. Labels visible at https://github.com/$REPO/labels"
