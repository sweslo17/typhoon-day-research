import datetime as dt
import unittest

from typhoon_day_research.features.elections import Election
from typhoon_day_research.modeling.baseline import TyphoonDayBaseline


class BaselineModelTests(unittest.TestCase):
    def test_high_weather_risk_and_upcoming_election_scores_above_low_risk(self):
        model = TyphoonDayBaseline(
            elections=[
                Election(date=dt.date(2024, 1, 13), type="presidential", name="總統", scope="national")
            ]
        )

        high = model.predict(
            county="臺北市",
            target_date=dt.date(2023, 8, 3),
            max_gust_mps=28,
            mean_wind_mps=15,
            rainfall_24h_mm=240,
            storm_radius_within_4h=True,
        )
        low = model.predict(
            county="臺北市",
            target_date=dt.date(2023, 8, 3),
            max_gust_mps=8,
            mean_wind_mps=3,
            rainfall_24h_mm=20,
            storm_radius_within_4h=False,
        )

        self.assertGreater(high.probability, low.probability)
        self.assertGreaterEqual(high.probability, 0.75)
        self.assertIn("next_year_presidential", high.feature_contributions)


if __name__ == "__main__":
    unittest.main()

