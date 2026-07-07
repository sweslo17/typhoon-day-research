import datetime as dt
import unittest

from typhoon_day_research.analysis.elections import summarize_election_timing
from typhoon_day_research.features.elections import Election
from typhoon_day_research.models import DgpaDecision


class ElectionAnalysisTests(unittest.TestCase):
    def test_summarize_election_timing_counts_next_year_presidential(self):
        decisions = [
            DgpaDecision(
                notice_pid="1",
                notice_date=dt.date(2023, 7, 24),
                county="臺北市",
                raw_text="今天停止辦公、停止上課。",
                work_status="stopped",
                class_status="stopped",
                period="full_day",
            ),
            DgpaDecision(
                notice_pid="2",
                notice_date=dt.date(2025, 7, 24),
                county="臺北市",
                raw_text="今天照常辦公、照常上課。",
                work_status="normal",
                class_status="normal",
                period="full_day",
            ),
        ]
        elections = [
            Election(date=dt.date(2024, 1, 13), type="presidential", name="總統選舉", scope="national"),
            Election(date=dt.date(2026, 11, 28), type="local", name="地方選舉", scope="local"),
        ]

        summary = summarize_election_timing(decisions, elections)

        self.assertEqual(summary["next_year_presidential"]["rows"], 1)
        self.assertEqual(summary["next_year_presidential"]["stopped_signal_rows"], 1)
        self.assertEqual(summary["next_year_presidential"]["stopped_signal_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
