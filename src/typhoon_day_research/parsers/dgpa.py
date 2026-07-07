from __future__ import annotations

import datetime as dt
import re
from html import unescape
from urllib.parse import parse_qs, urljoin, urlparse

from typhoon_day_research.models import DecisionStatus, DgpaDecision, DgpaNotice
from typhoon_day_research.parsers._html import parse_tables, strip_tags


CHINESE_DATE_RE = re.compile(r"(?P<year>\d{2,3})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日")


def roc_date_to_date(value: str) -> dt.date:
    parts = [int(part) for part in re.findall(r"\d+", value)]
    if len(parts) < 3:
        raise ValueError(f"Cannot parse ROC date: {value!r}")
    return dt.date(parts[0] + 1911, parts[1], parts[2])


def parse_chinese_roc_date(value: str) -> dt.date | None:
    match = CHINESE_DATE_RE.search(value)
    if not match:
        return None
    return dt.date(
        int(match.group("year")) + 1911,
        int(match.group("month")),
        int(match.group("day")),
    )


def parse_history_list(html: str, base_url: str) -> list[DgpaNotice]:
    notices: list[DgpaNotice] = []
    pattern = re.compile(
        r'<a\s+href="(?P<href>information\?uid=374&amp;pid=(?P<pid>\d+))".*?'
        r"<dt>(?P<published>.*?)</dt>.*?<p>(?P<title>.*?)</p>",
        re.DOTALL,
    )
    for match in pattern.finditer(html):
        title = strip_tags(match.group("title"))
        published = roc_date_to_date(strip_tags(match.group("published")))
        event_date = parse_chinese_roc_date(title) or published
        href = unescape(match.group("href"))
        notices.append(
            DgpaNotice(
                pid=match.group("pid"),
                title=title,
                published_date=published,
                event_date=event_date,
                url=urljoin(base_url, href),
            )
        )
    return notices


def parse_notice_attachment_links(html: str, base_url: str) -> list[str]:
    links: list[str] = []
    for href in re.findall(r'href="([^"]*FileConversion\?[^"]+)"', html):
        links.append(urljoin(base_url, unescape(href)))
    return links


def classify_decision_text(text: str) -> DecisionStatus:
    normalized = normalize_text(text)
    negative_threshold_phrases = [
        "未達停止上班及上課標準",
        "未達停止辦公及上課標準",
        "未達停止辦公上課標準",
    ]
    positive_threshold_phrases = [
        "已達停止上班及上課標準",
        "已達停止辦公及上課標準",
        "已達停止辦公上課標準",
    ]
    explicit_text = normalized
    for phrase in negative_threshold_phrases:
        explicit_text = explicit_text.replace(phrase, "")

    period = "full_day"
    if "下午" in normalized:
        period = "afternoon"
    elif "上午" in normalized:
        period = "morning"
    elif "晚上" in normalized or "晚間" in normalized:
        period = "evening"

    work_status = "unknown"
    if has_any(normalized, negative_threshold_phrases) or "尚未列入警戒區" in normalized:
        work_status = "normal"
    if has_any(normalized, positive_threshold_phrases):
        work_status = "stopped"
    if has_any(explicit_text, ["照常辦公", "照常上班"]):
        work_status = "normal"
    if has_any(explicit_text, ["停止辦公", "停止上班"]):
        work_status = "stopped"
    if has_any(explicit_text, ["照常辦公", "照常上班"]) and has_any(explicit_text, ["停止辦公", "停止上班"]):
        work_status = "partial"

    class_status = "unknown"
    if has_any(normalized, negative_threshold_phrases) or "尚未列入警戒區" in normalized:
        class_status = "normal"
    if has_any(normalized, positive_threshold_phrases):
        class_status = "stopped"
    if has_any(explicit_text, ["照常上課"]):
        class_status = "normal"
    if has_any(explicit_text, ["高中", "國中", "國小", "以下停止上課", "停止到校"]):
        class_status = "partial_school"
    if "停止上課" in explicit_text and class_status != "partial_school":
        class_status = "stopped"
    if "照常上課" in explicit_text and "停止上課" not in explicit_text:
        class_status = "normal"

    return DecisionStatus(work_status=work_status, class_status=class_status, period=period)


def parse_decision_table(html: str, notice_date: dt.date, notice_pid: str, source_url: str = "") -> list[DgpaDecision]:
    rows: list[DgpaDecision] = []
    for table in parse_tables(html):
        if not table or not _looks_like_decision_table(table):
            continue
        for cells in table[1:]:
            county, decision_text = _extract_county_decision(cells)
            if not county or not decision_text:
                continue
            status = classify_decision_text(decision_text)
            rows.append(
                DgpaDecision(
                    notice_pid=notice_pid,
                    notice_date=notice_date,
                    county=normalize_county_name(county),
                    raw_text=decision_text,
                    work_status=status.work_status,
                    class_status=status.class_status,
                    period=status.period,
                    source_url=source_url,
                )
            )
    return rows


def infer_pid_from_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if "pid" in query:
        return query["pid"][0]
    if "filename" in query:
        return query["filename"][0].rsplit("/", 1)[-1]
    return parsed.path.rsplit("/", 1)[-1]


def decode_html_bytes(content: bytes) -> str:
    for encoding in ("utf-8", "big5", "cp950"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def normalize_text(text: str) -> str:
    return text.replace("臺", "台").replace("，", "、").replace(" ", "")


def normalize_county_name(name: str) -> str:
    return (
        name.strip()
        .replace("巿", "市")
        .replace("台", "臺")
        .replace("臺北縣", "新北市(改制前臺北縣)")
        .replace("臺中縣", "臺中市(改制前臺中縣)")
        .replace("臺南縣", "臺南市(改制前臺南縣)")
        .replace("高雄縣", "高雄市(改制前高雄縣)")
    )


def has_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def _looks_like_decision_table(table: list[list[str]]) -> bool:
    first_rows = " ".join(" ".join(row) for row in table[:2])
    return "縣市" in first_rows or "縣市名稱" in first_rows or "縣巿名稱" in first_rows


def _extract_county_decision(cells: list[str]) -> tuple[str, str]:
    useful = [cell for cell in cells if cell and cell not in {"區域"}]
    if len(useful) >= 3:
        return useful[1], useful[2]
    if len(useful) >= 2:
        return useful[0], useful[1]
    return "", ""
