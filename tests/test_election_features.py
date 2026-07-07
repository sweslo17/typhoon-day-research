import datetime as dt
import unittest

from typhoon_day_research.features.elections import Election, election_features_for_date


class ElectionFeatureTests(unittest.TestCase):
    def test_features_capture_same_year_and_following_year_election_timing(self):
        elections = [
            Election(date=dt.date(2024, 1, 13), type="presidential", name="總統", scope="national"),
            Election(date=dt.date(2026, 11, 28), type="local", name="地方", scope="local"),
        ]

        before_presidential = election_features_for_date(dt.date(2023, 7, 24), elections)
        same_year_local = election_features_for_date(dt.date(2026, 7, 24), elections)

        self.assertEqual(before_presidential.next_election_type, "presidential")
        self.assertTrue(before_presidential.next_year_presidential)
        self.assertLess(before_presidential.days_until_next_major_election, 200)
        self.assertTrue(same_year_local.same_year_local)
        self.assertEqual(same_year_local.election_cycle, "same_year")


if __name__ == "__main__":
    unittest.main()

