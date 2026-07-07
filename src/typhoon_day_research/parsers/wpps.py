from __future__ import annotations

import ast
import datetime as dt
import re

from typhoon_day_research.models import ForecastRow, ForecastTable, WppsBundle
from typhoon_day_research.parsers._html import parse_tables, strip_tags


ASSIGNMENT_RE = re.compile(
    r"WPPS_HTM\.(?P<key>\w+)\s*=\s*(?P<body>.*?);"
    r"(?=\s*(?:WPPS_HTM\.|WPPS_MAP\.|$))",
    re.DOTALL,
)
STRING_RE = re.compile(r"'((?:\\.|[^'])*)'")
ISSUE_RE = re.compile(r"發布時間：(?P<year>\d{2,3})年(?P<month>\d{2})月(?P<day>\d{2})日(?P<hour>\d{1,2})時(?P<minute>\d{2})分")


def parse_wpps_js(js: str) -> WppsBundle:
    tables: dict[str, ForecastTable] = {}
    for match in ASSIGNMENT_RE.finditer(js):
        key = match.group("key")
        html = _join_js_strings(match.group("body"))
        if "<table" not in html:
            continue
        tables[key] = _parse_forecast_table(key, html)
    return WppsBundle(tables=tables)


def parse_mm_range(value: str) -> tuple[int | None, int | None]:
    cleaned = strip_tags(value).replace("毫米", "").strip()
    if cleaned in {"", "-", "--"}:
        return None, None
    if cleaned.startswith("<"):
        numbers = re.findall(r"\d+", cleaned)
        return (0, int(numbers[0])) if numbers else (None, None)
    numbers = [int(number) for number in re.findall(r"\d+", cleaned)]
    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    return None, None


def _join_js_strings(body: str) -> str:
    parts: list[str] = []
    for token in STRING_RE.findall(body):
        literal = "'" + token + "'"
        try:
            parts.append(ast.literal_eval(literal))
        except (SyntaxError, ValueError):
            parts.append(token.replace("\\'", "'").replace("\\/", "/").replace("\\n", "\n"))
    return "".join(parts)


def _parse_forecast_table(key: str, html: str) -> ForecastTable:
    text = strip_tags(html)
    issue_time = _parse_issue_time(text)
    title = text.split("發布時間：", 1)[0].strip()
    rows: list[ForecastRow] = []
    for table in parse_tables(html):
        for cells in table:
            if len(cells) < 3 or cells[0] in {"分區", "區域"}:
                continue
            plain_min, plain_max = parse_mm_range(cells[1])
            mountain_min, mountain_max = parse_mm_range(cells[2])
            rows.append(
                ForecastRow(
                    area=cells[0],
                    plain_min_mm=plain_min,
                    plain_max_mm=plain_max,
                    mountain_min_mm=mountain_min,
                    mountain_max_mm=mountain_max,
                    raw_plain=cells[1],
                    raw_mountain=cells[2],
                )
            )
    return ForecastTable(key=key, issue_time=issue_time, rows=rows, title=title)


def _parse_issue_time(text: str) -> dt.datetime | None:
    match = ISSUE_RE.search(text)
    if not match:
        return None
    return dt.datetime(
        int(match.group("year")) + 1911,
        int(match.group("month")),
        int(match.group("day")),
        int(match.group("hour")),
        int(match.group("minute")),
    )
