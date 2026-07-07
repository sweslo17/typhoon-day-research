from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from typhoon_day_research.models import ElectionFeatureSet


@dataclass(frozen=True)
class Election:
    date: dt.date
    type: str
    name: str
    scope: str


def load_elections_csv(path: Path) -> list[Election]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return [
            Election(
                date=dt.date.fromisoformat(row["date"]),
                type=row["type"],
                name=row["name"],
                scope=row["scope"],
            )
            for row in csv.DictReader(file)
        ]


def election_features_for_date(target_date: dt.date, elections: list[Election]) -> ElectionFeatureSet:
    ordered = sorted(elections, key=lambda item: item.date)
    same_year = [item for item in ordered if item.date.year == target_date.year]
    next_year = [item for item in ordered if item.date.year == target_date.year + 1]
    upcoming = [item for item in ordered if item.date >= target_date]
    next_election = upcoming[0] if upcoming else None

    if any(item.date >= target_date for item in same_year):
        cycle = "same_year"
    elif next_year:
        cycle = "next_year"
    else:
        cycle = "off_cycle"

    return ElectionFeatureSet(
        same_year_presidential=any(item.type == "presidential" for item in same_year),
        same_year_local=any(item.type == "local" for item in same_year),
        next_year_presidential=any(item.type == "presidential" for item in next_year),
        next_year_local=any(item.type == "local" for item in next_year),
        days_until_next_major_election=(next_election.date - target_date).days if next_election else None,
        next_election_type=next_election.type if next_election else None,
        election_cycle=cycle,
    )

