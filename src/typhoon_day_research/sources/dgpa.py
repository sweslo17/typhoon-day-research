from __future__ import annotations

import csv
import ssl
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from typhoon_day_research.parsers.dgpa import decode_html_bytes, parse_history_list, parse_notice_attachment_links


DGPA_BASE_URL = "https://www.dgpa.gov.tw/"


def fetch_url(url: str, timeout: int = 30) -> bytes:
    try:
        with urlopen(url, timeout=timeout, context=_ssl_context(relaxed_strict=False)) as response:
            return response.read()
    except URLError as exc:
        if not _is_missing_subject_key_identifier_error(exc):
            raise
        with urlopen(url, timeout=timeout, context=_ssl_context(relaxed_strict=True)) as response:
            return response.read()


def _ssl_context(relaxed_strict: bool) -> ssl.SSLContext:
    context = ssl.create_default_context()
    if relaxed_strict and hasattr(ssl, "VERIFY_X509_STRICT"):
        context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return context


def _is_missing_subject_key_identifier_error(exc: URLError) -> bool:
    reason = getattr(exc, "reason", exc)
    return isinstance(reason, ssl.SSLCertVerificationError) and "Missing Subject Key Identifier" in str(reason)


def fetch_history_pages(raw_dir: Path, pages: int = 49, delay_sec: float = 0.1) -> list[Path]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for page in range(1, pages + 1):
        url = f"{DGPA_BASE_URL}informationlist?uid=374&page={page}"
        path = raw_dir / f"history_page_{page:02d}.html"
        if not path.exists():
            path.write_bytes(fetch_url(url))
            time.sleep(delay_sec)
        paths.append(path)
    return paths


def fetch_notice_details_and_attachments(raw_dir: Path, limit: int | None = None, delay_sec: float = 0.1) -> None:
    pages = sorted(raw_dir.glob("history_page_*.html"))
    notices = []
    for page in pages:
        notices.extend(parse_history_list(decode_html_bytes(page.read_bytes()), base_url=DGPA_BASE_URL))
    if limit is not None:
        notices = notices[:limit]
    _write_notices_csv(raw_dir / "notices.csv", notices)
    detail_dir = raw_dir / "details"
    attachment_dir = raw_dir / "attachments"
    detail_dir.mkdir(exist_ok=True)
    attachment_dir.mkdir(exist_ok=True)
    for notice in notices:
        detail_path = detail_dir / f"{notice.pid}.html"
        if not detail_path.exists():
            detail_path.write_bytes(fetch_url(notice.url))
            time.sleep(delay_sec)
        detail_html = decode_html_bytes(detail_path.read_bytes())
        for idx, link in enumerate(parse_notice_attachment_links(detail_html, base_url=DGPA_BASE_URL), start=1):
            attachment_path = attachment_dir / f"{notice.pid}_{idx}.html"
            if not attachment_path.exists():
                attachment_path.write_bytes(fetch_url(link))
                time.sleep(delay_sec)


def _write_notices_csv(path: Path, notices: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["pid", "title", "published_date", "event_date", "url"])
        writer.writeheader()
        for notice in notices:
            writer.writerow(
                {
                    "pid": notice.pid,
                    "title": notice.title,
                    "published_date": notice.published_date.isoformat(),
                    "event_date": notice.event_date.isoformat(),
                    "url": notice.url,
                }
            )
