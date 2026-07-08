from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "data" / "processed" / "dgpa_decisions.csv"
OUT_DIR = ROOT / "reports" / "analysis"


def main() -> int:
    rows = list(csv.DictReader(DECISIONS.open("r", encoding="utf-8")))
    stopped = [row for row in rows if float(row["stopped_score"]) > 0]
    month_counts = Counter(row["notice_date"][5:7] for row in stopped)
    year_counts = Counter(row["notice_date"][:4] for row in stopped)

    render_bar_svg(
        [(month, month_counts[month]) for month in [f"{idx:02d}" for idx in range(1, 13)]],
        OUT_DIR / "month_distribution.svg",
        "停止上班上課訊號月份分布",
        label_suffix="月",
    )
    render_bar_svg(
        year_counts.most_common(10),
        OUT_DIR / "year_top.svg",
        "停止上班上課訊號年份高峰",
        label_suffix="年",
    )
    return 0


def render_bar_svg(items: list[tuple[str, int]], path: Path, title: str, label_suffix: str) -> None:
    width = 860
    row_height = 34
    height = 78 + row_height * len(items)
    max_count = max((count for _, count in items), default=1)
    bars: list[str] = []
    for idx, (label, count) in enumerate(items):
        y = 56 + idx * row_height
        bar_width = int(600 * count / max_count)
        bars.append(f'<text x="24" y="{y + 18}" font-size="15">{label}{label_suffix}</text>')
        bars.append(f'<rect x="105" y="{y}" width="{bar_width}" height="22" fill="#2D7DD2" />')
        bars.append(f'<text x="{118 + bar_width}" y="{y + 17}" font-size="14">{count}</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<text x="24" y="32" font-size="22" font-weight="700">{title}</text>
{''.join(bars)}
</svg>
"""
    path.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
