from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Generic project identifiers.
type AoiId = str
type NbsId = str
type PilotId = str

# Run configuration.
type AnalysisResolutionM = Literal[10000, 5000, 1000, 500, 100]
type ClimateRiskMode = Literal["hazard-exposure", "hazard-exposure-vulnerability"]

# Climate risk schema vocabulary.
type RiskComponent = Literal["hazard", "exposure", "sensitivity", "adaptive_capacity"]

# Scenario configuration.
type ClimatePathway = Literal["ssp126", "ssp245", "ssp370", "ssp585"]
type TimeHorizon = Literal[2030, 2050]


@dataclass(frozen=True)
class YearPeriod:
    """Inclusive year range used to aggregate climate data."""

    start_year: int
    end_year: int


TIME_HORIZON_PERIODS: dict[TimeHorizon, YearPeriod] = {
    2030: YearPeriod(2021, 2040),
    2050: YearPeriod(2041, 2060),
}


@dataclass(frozen=True)
class FutureScenario:
    """Future climate scenario requested in addition to the required baseline run."""

    pathway: ClimatePathway
    horizon_year: TimeHorizon

    @property
    def label(self) -> str:
        return f"{self.pathway}_{self.horizon_year}"

    @property
    def period(self) -> YearPeriod:
        return TIME_HORIZON_PERIODS[self.horizon_year]


@dataclass(frozen=True)
class RunConfig:
    """Configuration recorded in pipeline/outputs/<pilot_id>/run_config.json."""

    pilot_id: PilotId
    nbs_id: NbsId
    aoi_id: AoiId
    resolution_m: AnalysisResolutionM
    future_scenarios: tuple[FutureScenario, ...] = ()
    climate_risk_mode: ClimateRiskMode = "hazard-exposure"
