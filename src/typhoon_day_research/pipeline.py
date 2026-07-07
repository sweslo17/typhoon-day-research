from __future__ import annotations

import csv
import datetime as dt
import json
from dataclasses import asdict
from pathlib import Path

from typhoon_day_research.analysis.elections import write_election_timing_outputs
from typhoon_day_research.analysis.summary import render_stop_count_svg, summarize_decisions
from typhoon_day_research.articles.medium import render_medium_series
from typhoon_day_research.features.elections import Election
from typhoon_day_research.modeling.baseline import TyphoonDayBaseline
from typhoon_day_research.models import DgpaDecision, PipelineArtifacts, WppsBundle
from typhoon_day_research.parsers.dgpa import (
    decode_html_bytes,
    parse_chinese_roc_date,
    parse_decision_table,
    roc_date_to_date,
)


SAMPLE_DGPA_HTML = """
<table border="1">
  <tr><td>區域</td><td>縣巿名稱</td><td>是否停止辦公上課情形</td></tr>
  <tr><td rowspan="6">北部地區</td><td>基隆巿</td><td>今天停止辦公、停止上課。</td></tr>
  <tr><td>台北巿</td><td>今天停止辦公、停止上課。</td></tr>
  <tr><td>台北縣</td><td>今天停止辦公、停止上課。</td></tr>
  <tr><td>桃園縣</td><td>今天停止辦公、停止上課。</td></tr>
  <tr><td>新竹巿</td><td>今天照常辦公、照常上課。</td></tr>
  <tr><td>新竹縣</td><td>今天下午停止辦公、停止上課。</td></tr>
  <tr><td rowspan="3">南部地區</td><td>台南巿</td><td>今天照常辦公、高中及高中以下停止上課。</td></tr>
  <tr><td>高雄巿</td><td>今天照常辦公、國中以下停止上課。</td></tr>
  <tr><td>屏東縣</td><td>今天照常辦公、國中以下停止上課。</td></tr>
</table>
"""


def run_sample_pipeline(out_dir: Path) -> PipelineArtifacts:
    out_dir.mkdir(parents=True, exist_ok=True)
    medium_dir = out_dir / "medium"
    medium_dir.mkdir(parents=True, exist_ok=True)

    decisions = parse_decision_table(
        SAMPLE_DGPA_HTML,
        notice_date=roc_date_to_date("90.07.30"),
        notice_pid="7004",
        source_url="https://www.dgpa.gov.tw/information?uid=374&pid=7004",
    )

    decisions_csv = out_dir / "sample_decisions.csv"
    write_decisions_csv(decisions, decisions_csv)

    summary_md = out_dir / "summary.md"
    summary_md.write_text(summarize_decisions(decisions), encoding="utf-8")

    stop_count_svg = out_dir / "stop_count.svg"
    render_stop_count_svg(decisions, stop_count_svg)

    model = TyphoonDayBaseline(
        elections=[Election(date=dt.date(2024, 1, 13), type="presidential", name="第16任總統副總統選舉", scope="national")]
    )
    prediction = model.predict(
        county="臺北市",
        target_date=dt.date(2023, 8, 3),
        max_gust_mps=28,
        mean_wind_mps=15,
        rainfall_24h_mm=240,
        storm_radius_within_4h=True,
    )
    prediction_json = out_dir / "prediction.json"
    prediction_json.write_text(json.dumps(asdict(prediction), ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    for draft in render_medium_series():
        (medium_dir / f"{draft.slug}.md").write_text(draft.markdown, encoding="utf-8")

    return PipelineArtifacts(
        decisions_csv=decisions_csv,
        summary_md=summary_md,
        stop_count_svg=stop_count_svg,
        prediction_json=prediction_json,
        medium_dir=medium_dir,
    )


def write_decisions_csv(decisions: list[DgpaDecision], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "notice_pid",
                "notice_date",
                "county",
                "work_status",
                "class_status",
                "period",
                "stopped_score",
                "raw_text",
                "source_url",
            ],
        )
        writer.writeheader()
        for row in decisions:
            writer.writerow(
                {
                    "notice_pid": row.notice_pid,
                    "notice_date": row.notice_date.isoformat(),
                    "county": row.county,
                    "work_status": row.work_status,
                    "class_status": row.class_status,
                    "period": row.period,
                    "stopped_score": row.stopped_score,
                    "raw_text": row.raw_text,
                    "source_url": row.source_url,
                }
            )


def read_decisions_csv(path: Path) -> list[DgpaDecision]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return [
            DgpaDecision(
                notice_pid=row["notice_pid"],
                notice_date=dt.date.fromisoformat(row["notice_date"]),
                county=row["county"],
                raw_text=row["raw_text"],
                work_status=row["work_status"],
                class_status=row["class_status"],
                period=row["period"],
                source_url=row.get("source_url", ""),
            )
            for row in csv.DictReader(file)
        ]


def build_dataset_from_raw(raw_dir: Path, decisions_csv: Path) -> list[DgpaDecision]:
    notice_index = _read_notice_index(raw_dir / "notices.csv")
    attachment_dir = raw_dir / "attachments"
    decisions: list[DgpaDecision] = []

    for attachment_path in sorted([*attachment_dir.glob("*.html"), *attachment_dir.glob("*.htm")]):
        pid = attachment_path.stem.split("_", 1)[0]
        html = decode_html_bytes(attachment_path.read_bytes())
        notice = notice_index.get(pid, {})
        notice_date = _notice_date(notice, html)
        source_url = notice.get("url", "")
        decisions.extend(
            parse_decision_table(
                html,
                notice_date=notice_date,
                notice_pid=pid,
                source_url=source_url,
            )
        )

    write_decisions_csv(decisions, decisions_csv)
    return decisions


def analyze_decisions_csv(decisions_csv: Path, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    decisions = read_decisions_csv(decisions_csv)
    summary_md = out_dir / "summary.md"
    stop_count_svg = out_dir / "stop_count.svg"
    summary_md.write_text(summarize_decisions(decisions), encoding="utf-8")
    render_stop_count_svg(decisions, stop_count_svg)
    return summary_md, stop_count_svg


def analyze_decisions_with_elections_csv(
    decisions_csv: Path,
    elections: list[Election],
    out_dir: Path,
) -> tuple[Path, Path, Path, Path]:
    summary_md, stop_count_svg = analyze_decisions_csv(decisions_csv, out_dir)
    decisions = read_decisions_csv(decisions_csv)
    election_csv, election_md = write_election_timing_outputs(decisions, elections, out_dir)
    return summary_md, stop_count_svg, election_csv, election_md


def write_wpps_forecast_csv(bundle: WppsBundle, path: Path, table_key: str = "Fcst24hPrecipTable") -> int:
    table = bundle.tables.get(table_key)
    if table is None:
        raise KeyError(f"WPPS table not found: {table_key}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "table_key",
                "issue_time",
                "area",
                "plain_min_mm",
                "plain_max_mm",
                "mountain_min_mm",
                "mountain_max_mm",
                "raw_plain",
                "raw_mountain",
            ],
        )
        writer.writeheader()
        for row in table.rows:
            writer.writerow(
                {
                    "table_key": table.key,
                    "issue_time": table.issue_time.isoformat() if table.issue_time else "",
                    "area": row.area,
                    "plain_min_mm": row.plain_min_mm,
                    "plain_max_mm": row.plain_max_mm,
                    "mountain_min_mm": row.mountain_min_mm,
                    "mountain_max_mm": row.mountain_max_mm,
                    "raw_plain": row.raw_plain,
                    "raw_mountain": row.raw_mountain,
                }
            )
    return len(table.rows)


def _read_notice_index(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as file:
        return {row["pid"]: row for row in csv.DictReader(file)}


def _notice_date(notice: dict[str, str], html: str) -> dt.date:
    if notice.get("event_date"):
        return dt.date.fromisoformat(notice["event_date"])
    if notice.get("published_date"):
        return dt.date.fromisoformat(notice["published_date"])
    return parse_chinese_roc_date(html) or dt.date(1900, 1, 1)
