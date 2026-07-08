from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

from typhoon_day_research.modeling.baseline import TyphoonDayBaseline
from typhoon_day_research.models import PredictionResult


def predict_batch_from_csv(path: str | Path, model: TyphoonDayBaseline) -> list[PredictionResult]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return [
        model.predict(
            county=row["county"],
            target_date=dt.date.fromisoformat(row["target_date"]),
            max_gust_mps=float(row["max_gust_mps"]),
            mean_wind_mps=float(row["mean_wind_mps"]),
            rainfall_24h_mm=float(row["rainfall_24h_mm"]),
            storm_radius_within_4h=_parse_bool(row["storm_radius_within_4h"]),
        )
        for row in rows
    ]


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "是"}
