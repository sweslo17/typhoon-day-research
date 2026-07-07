from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class DecisionStatus:
    work_status: str
    class_status: str
    period: str


@dataclass(frozen=True)
class DgpaNotice:
    pid: str
    title: str
    published_date: dt.date
    event_date: dt.date
    url: str


@dataclass(frozen=True)
class DgpaDecision:
    notice_pid: str
    notice_date: dt.date
    county: str
    raw_text: str
    work_status: str
    class_status: str
    period: str
    source_url: str = ""

    @property
    def stopped_score(self) -> float:
        work = 1.0 if self.work_status == "stopped" else 0.0
        classes = 1.0 if self.class_status == "stopped" else 0.5 if self.class_status == "partial_school" else 0.0
        period = 0.5 if self.period in {"morning", "afternoon", "evening"} else 1.0
        return max(work, classes) * period


@dataclass(frozen=True)
class ForecastRow:
    area: str
    plain_min_mm: int | None
    plain_max_mm: int | None
    mountain_min_mm: int | None
    mountain_max_mm: int | None
    raw_plain: str
    raw_mountain: str


@dataclass(frozen=True)
class ForecastTable:
    key: str
    issue_time: dt.datetime | None
    rows: list[ForecastRow]
    title: str = ""


@dataclass(frozen=True)
class WppsBundle:
    tables: dict[str, ForecastTable]


@dataclass(frozen=True)
class ElectionFeatureSet:
    same_year_presidential: bool
    same_year_local: bool
    next_year_presidential: bool
    next_year_local: bool
    days_until_next_major_election: int | None
    next_election_type: str | None
    election_cycle: str


@dataclass(frozen=True)
class PredictionResult:
    county: str
    target_date: dt.date
    probability: float
    risk_level: str
    feature_contributions: dict[str, float]
    explanation: str


@dataclass(frozen=True)
class ArticleDraft:
    title: str
    slug: str
    markdown: str


@dataclass(frozen=True)
class PipelineArtifacts:
    decisions_csv: Path
    summary_md: Path
    stop_count_svg: Path
    prediction_json: Path
    medium_dir: Path
    extra_files: list[Path] = field(default_factory=list)

