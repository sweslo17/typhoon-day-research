from __future__ import annotations

import csv
from pathlib import Path

from typhoon_day_research.features.elections import Election, election_features_for_date
from typhoon_day_research.models import DgpaDecision


ELECTION_GROUPS = [
    "same_year_presidential",
    "same_year_local",
    "next_year_presidential",
    "next_year_local",
    "major_election_within_180_days",
    "off_cycle",
]


def summarize_election_timing(decisions: list[DgpaDecision], elections: list[Election]) -> dict[str, dict[str, float]]:
    summary = {
        group: {"rows": 0, "stopped_signal_rows": 0, "stopped_signal_rate": 0.0}
        for group in ELECTION_GROUPS
    }
    for decision in decisions:
        for group in _groups_for_decision(decision, elections):
            summary[group]["rows"] += 1
            if decision.stopped_score > 0:
                summary[group]["stopped_signal_rows"] += 1
    for values in summary.values():
        rows = values["rows"]
        values["stopped_signal_rate"] = round(values["stopped_signal_rows"] / rows, 4) if rows else 0.0
    return summary


def write_election_timing_outputs(
    decisions: list[DgpaDecision],
    elections: list[Election],
    out_dir: Path,
) -> tuple[Path, Path]:
    summary = summarize_election_timing(decisions, elections)
    csv_path = out_dir / "election_timing.csv"
    md_path = out_dir / "election_timing.md"
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["group", "rows", "stopped_signal_rows", "stopped_signal_rate"])
        writer.writeheader()
        for group in ELECTION_GROUPS:
            writer.writerow({"group": group, **summary[group]})
    md_path.write_text(_render_markdown(summary), encoding="utf-8")
    return csv_path, md_path


def _groups_for_decision(decision: DgpaDecision, elections: list[Election]) -> list[str]:
    features = election_features_for_date(decision.notice_date, elections)
    groups: list[str] = []
    if features.same_year_presidential:
        groups.append("same_year_presidential")
    if features.same_year_local:
        groups.append("same_year_local")
    if features.next_year_presidential:
        groups.append("next_year_presidential")
    if features.next_year_local:
        groups.append("next_year_local")
    if features.days_until_next_major_election is not None and features.days_until_next_major_election <= 180:
        groups.append("major_election_within_180_days")
    if not groups:
        groups.append("off_cycle")
    return groups


def _render_markdown(summary: dict[str, dict[str, float]]) -> str:
    lines = [
        "# 選舉時序與颱風假探索統計",
        "",
        "這份表是探索性統計，不是因果推論。總統大選若在隔年一月，前一年颱風季會被標記為 `next_year_presidential`。",
        "各 group 是非互斥標籤，因此 rows 不應加總解讀。",
        "",
        "| group | rows | stopped_signal_rows | stopped_signal_rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for group in ELECTION_GROUPS:
        values = summary[group]
        lines.append(
            f"| `{group}` | {values['rows']} | {values['stopped_signal_rows']} | {values['stopped_signal_rate']:.2%} |"
        )
    return "\n".join(lines) + "\n"
