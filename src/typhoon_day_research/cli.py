from __future__ import annotations

import argparse
import datetime as dt
import json
from dataclasses import asdict
from pathlib import Path

from typhoon_day_research.articles.medium import render_medium_series
from typhoon_day_research.features.elections import Election, load_elections_csv
from typhoon_day_research.modeling.batch import predict_batch_from_csv
from typhoon_day_research.modeling.baseline import TyphoonDayBaseline
from typhoon_day_research.parsers.wpps import parse_wpps_js
from typhoon_day_research.pipeline import (
    analyze_decisions_with_elections_csv,
    build_dataset_from_raw,
    run_sample_pipeline,
    write_wpps_forecast_csv,
)
from typhoon_day_research.sources.dgpa import fetch_history_pages, fetch_notice_details_and_attachments


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="typhoon-day-research")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sample = subparsers.add_parser("run-sample")
    sample.add_argument("--out-dir", type=Path, default=Path("reports/generated"))

    fetch = subparsers.add_parser("fetch-dgpa")
    fetch.add_argument("--raw-dir", type=Path, default=Path("data/raw/dgpa"))
    fetch.add_argument("--pages", type=int, default=49)
    fetch.add_argument("--notice-limit", type=int, default=None)

    build = subparsers.add_parser("build-dataset")
    build.add_argument("--raw-dir", type=Path, default=Path("data/raw/dgpa"))
    build.add_argument("--out", type=Path, default=Path("data/processed/dgpa_decisions.csv"))

    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("--decisions-csv", type=Path, default=Path("data/processed/dgpa_decisions.csv"))
    analyze.add_argument("--out-dir", type=Path, default=Path("reports/analysis"))
    analyze.add_argument("--elections", type=Path, default=Path("data/manual/election_calendar.csv"))

    wpps = subparsers.add_parser("parse-wpps")
    wpps.add_argument("--input", type=Path, default=Path("data/raw/cwa/WPPS-Data.js"))
    wpps.add_argument("--out", type=Path, default=Path("data/processed/cwa_wpps_forecast.csv"))
    wpps.add_argument("--table-key", default="Fcst24hPrecipTable")

    predict = subparsers.add_parser("predict")
    predict.add_argument("--county", required=True)
    predict.add_argument("--target-date", required=True)
    predict.add_argument("--max-gust-mps", type=float, required=True)
    predict.add_argument("--mean-wind-mps", type=float, required=True)
    predict.add_argument("--rainfall-24h-mm", type=float, required=True)
    predict.add_argument("--storm-radius-within-4h", action="store_true")
    predict.add_argument("--elections", type=Path, default=Path("data/manual/election_calendar.csv"))
    predict.add_argument("--out", type=Path, default=Path("reports/generated/prediction_cli.json"))

    predict_batch = subparsers.add_parser("predict-batch")
    predict_batch.add_argument("--input", type=Path, default=Path("data/manual/taipei_typhoon_week_scenario.csv"))
    predict_batch.add_argument("--elections", type=Path, default=Path("data/manual/election_calendar.csv"))
    predict_batch.add_argument("--out", type=Path, default=Path("reports/generated/prediction_week_taipei.json"))

    drafts = subparsers.add_parser("drafts")
    drafts.add_argument("--out-dir", type=Path, default=Path("reports/medium"))

    args = parser.parse_args(argv)
    if args.command == "run-sample":
        artifacts = run_sample_pipeline(args.out_dir)
        print(json.dumps({key: str(value) for key, value in asdict(artifacts).items()}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "fetch-dgpa":
        fetch_history_pages(args.raw_dir, pages=args.pages)
        fetch_notice_details_and_attachments(args.raw_dir, limit=args.notice_limit)
        print(f"Fetched DGPA pages into {args.raw_dir}")
        return 0
    if args.command == "build-dataset":
        decisions = build_dataset_from_raw(args.raw_dir, args.out)
        print(json.dumps({"decisions_csv": str(args.out), "rows": len(decisions)}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "analyze":
        elections = load_elections_csv(args.elections) if args.elections.exists() else _fallback_elections()
        summary_md, stop_count_svg, election_csv, election_md = analyze_decisions_with_elections_csv(
            args.decisions_csv, elections, args.out_dir
        )
        print(
            json.dumps(
                {
                    "summary_md": str(summary_md),
                    "stop_count_svg": str(stop_count_svg),
                    "election_timing_csv": str(election_csv),
                    "election_timing_md": str(election_md),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "parse-wpps":
        rows = write_wpps_forecast_csv(parse_wpps_js(args.input.read_text(encoding="utf-8")), args.out, args.table_key)
        print(json.dumps({"forecast_csv": str(args.out), "rows": rows}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "predict":
        elections = load_elections_csv(args.elections) if args.elections.exists() else _fallback_elections()
        model = TyphoonDayBaseline(elections=elections)
        result = model.predict(
            county=args.county,
            target_date=dt.date.fromisoformat(args.target_date),
            max_gust_mps=args.max_gust_mps,
            mean_wind_mps=args.mean_wind_mps,
            rainfall_24h_mm=args.rainfall_24h_mm,
            storm_radius_within_4h=args.storm_radius_within_4h,
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(args.out)
        return 0
    if args.command == "predict-batch":
        elections = load_elections_csv(args.elections) if args.elections.exists() else _fallback_elections()
        model = TyphoonDayBaseline(elections=elections)
        results = predict_batch_from_csv(args.input, model)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(args.out)
        return 0
    if args.command == "drafts":
        args.out_dir.mkdir(parents=True, exist_ok=True)
        for draft in render_medium_series():
            (args.out_dir / f"{draft.slug}.md").write_text(draft.markdown, encoding="utf-8")
        print(args.out_dir)
        return 0
    return 1


def _fallback_elections() -> list[Election]:
    return [
        Election(date=dt.date(2024, 1, 13), type="presidential", name="第16任總統副總統選舉", scope="national"),
        Election(date=dt.date(2026, 11, 28), type="local", name="地方公職人員選舉", scope="local"),
    ]


if __name__ == "__main__":
    raise SystemExit(main())
