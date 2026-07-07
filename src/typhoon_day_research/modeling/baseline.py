from __future__ import annotations

import datetime as dt
import math

from typhoon_day_research.features.elections import Election, election_features_for_date
from typhoon_day_research.models import PredictionResult


class TyphoonDayBaseline:
    """Transparent baseline method, not a black-box statistical claim."""

    def __init__(self, elections: list[Election] | None = None) -> None:
        self.elections = elections or []

    def predict(
        self,
        county: str,
        target_date: dt.date,
        max_gust_mps: float,
        mean_wind_mps: float,
        rainfall_24h_mm: float,
        storm_radius_within_4h: bool,
    ) -> PredictionResult:
        election_features = election_features_for_date(target_date, self.elections) if self.elections else None
        contributions: dict[str, float] = {"base": -2.5}

        if storm_radius_within_4h:
            contributions["storm_radius_within_4h"] = 1.0
        if mean_wind_mps >= 14.0:
            contributions["mean_wind_ge_7_beaufort"] = 1.1
        elif mean_wind_mps >= 10.8:
            contributions["mean_wind_ge_6_beaufort"] = 0.45
        if max_gust_mps >= 24.5:
            contributions["gust_ge_10_beaufort"] = 1.1
        elif max_gust_mps >= 20.8:
            contributions["gust_ge_9_beaufort"] = 0.6
        if rainfall_24h_mm >= 200:
            contributions["rainfall_24h_ge_200mm"] = 0.9
        elif rainfall_24h_mm >= 80:
            contributions["rainfall_24h_ge_80mm"] = 0.4

        if election_features:
            if election_features.next_year_presidential:
                contributions["next_year_presidential"] = 0.35
            if election_features.same_year_presidential:
                contributions["same_year_presidential"] = 0.2
            if election_features.same_year_local:
                contributions["same_year_local"] = 0.25
            if election_features.next_year_local:
                contributions["next_year_local"] = 0.15
            if (
                election_features.days_until_next_major_election is not None
                and election_features.days_until_next_major_election <= 180
            ):
                contributions["major_election_within_180_days"] = 0.2

        logit = sum(contributions.values())
        probability = 1 / (1 + math.exp(-logit))
        risk_level = "high" if probability >= 0.75 else "medium" if probability >= 0.4 else "low"
        explanation = (
            f"{county} on {target_date.isoformat()}: estimated typhoon-day probability "
            f"{probability:.1%} ({risk_level}). This is an interpretable baseline, not an official forecast."
        )
        return PredictionResult(
            county=county,
            target_date=target_date,
            probability=round(probability, 4),
            risk_level=risk_level,
            feature_contributions=contributions,
            explanation=explanation,
        )

