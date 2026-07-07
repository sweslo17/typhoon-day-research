from __future__ import annotations

from collections import Counter
from pathlib import Path

from typhoon_day_research.models import DgpaDecision


def summarize_decisions(decisions: list[DgpaDecision]) -> str:
    county_counts = Counter(row.county for row in decisions if row.stopped_score > 0)
    total = len(decisions)
    stopped = sum(1 for row in decisions if row.stopped_score > 0)
    lines = [
        "# 颱風假研究資料包摘要",
        "",
        f"- 決策列數：{total}",
        f"- 有停止上班上課訊號列數：{stopped}",
        "",
        "## 縣市停止上班上課次數",
        "",
    ]
    for county, count in county_counts.most_common():
        lines.append(f"- {county}: {count}")
    lines.extend(
        [
            "",
            "## 方法提醒",
            "",
            "- 早期公告有縣市改制與局部鄉鎮文字，分析時需保留原文並建立標準化欄位。",
            "- 選舉時序不可只看同年，隔年一月總統大選也可能與前一年颱風季相鄰。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_stop_count_svg(decisions: list[DgpaDecision], path: Path) -> None:
    counts = Counter(row.county for row in decisions if row.stopped_score > 0)
    items = counts.most_common(10)
    width = 760
    row_height = 34
    height = 80 + row_height * max(len(items), 1)
    max_count = max(counts.values(), default=1)
    bars: list[str] = []
    for idx, (county, count) in enumerate(items):
        y = 56 + idx * row_height
        bar_width = int(520 * count / max_count)
        bars.append(f'<text x="24" y="{y + 20}" font-size="15">{county}</text>')
        bars.append(f'<rect x="160" y="{y}" width="{bar_width}" height="22" fill="#247BA0" />')
        bars.append(f'<text x="{170 + bar_width}" y="{y + 17}" font-size="14">{count}</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<text x="24" y="32" font-size="22" font-weight="700">縣市停止上班上課樣本排行</text>
{''.join(bars)}
</svg>
"""
    path.write_text(svg, encoding="utf-8")
