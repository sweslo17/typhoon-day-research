from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


CODIS_BASE_URL = "https://codis.cwa.gov.tw/"


def fetch_station_list() -> dict:
    with urlopen(f"{CODIS_BASE_URL}api/station_list", timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_station_observations(
    station_id: str,
    station_type: str,
    start: str,
    end: str,
    report_type: str = "report_date",
) -> dict:
    data = urlencode(
        {
            "date": start[:10],
            "type": report_type,
            "stn_ID": station_id,
            "stn_type": station_type,
            "start": start,
            "end": end,
            "starttime": start,
            "endtime": end,
        }
    ).encode("utf-8")
    request = Request(f"{CODIS_BASE_URL}api/station", data=data, method="POST")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

