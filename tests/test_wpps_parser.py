import unittest
import tempfile
from pathlib import Path

from typhoon_day_research.parsers.wpps import parse_wpps_js
from typhoon_day_research.pipeline import write_wpps_forecast_csv


class WppsParserTests(unittest.TestCase):
    SAMPLE_JS = r"""
        var WebInfo = ['Fcst24hPrecipTable'];
        var WPPS_HTM = {'Fcst24hPrecipTable':''}
        WPPS_HTM.Fcst24hPrecipTable = ''+
          '<h3>颱風各地區24小時雨量預測<span class="notes">發布時間：115年06月26日16時00分(正報)</span></h3>'+
          '<table><thead><tr><th>分區</th><th>平地</th><th>山區</th></tr></thead><tbody>'+
          '<tr><td>臺北市</td><td>50 - 100</td><td>50 - 100</td></tr>'+
          '<tr><td>高雄市</td><td>250 - 450</td><td>250 - 450</td></tr>'+
          '</tbody></table>';
        """
    SAMPLE_JS_WITH_ENTITY = r"""
        WPPS_HTM.Fcst24hPrecipTable = ''+
          '<h3>颱風各地區24小時雨量預測<span class="notes">發布時間：115年06月26日16時00分(正報)</span></h3>'+
          '<table><tbody>'+
          '<tr><td>蘭嶼綠島</td><td>&nbsp;</td><td>80 - 150</td></tr>'+
          '<tr><td>澎湖縣</td><td>50 - 100</td><td>-</td></tr>'+
          '</tbody></table>';
        WPPS_MAP.WindMap_1 = {};
        """

    def test_parse_wpps_js_extracts_precipitation_forecast_rows(self):
        bundle = parse_wpps_js(self.SAMPLE_JS)
        self.assertIn("Fcst24hPrecipTable", bundle.tables)
        table = bundle.tables["Fcst24hPrecipTable"]
        self.assertEqual(table.issue_time.isoformat(), "2026-06-26T16:00:00")
        self.assertEqual(table.rows[0].area, "臺北市")
        self.assertEqual(table.rows[1].plain_max_mm, 450)

    def test_write_wpps_forecast_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "forecast.csv"
            rows = write_wpps_forecast_csv(parse_wpps_js(self.SAMPLE_JS), path)

            self.assertEqual(rows, 2)
            self.assertTrue(path.exists())
            content = path.read_text(encoding="utf-8")
            self.assertIn("issue_time", content)
            self.assertIn("高雄市", content)
            self.assertIn("450", content)

    def test_parse_wpps_js_does_not_stop_at_html_entity_semicolon(self):
        bundle = parse_wpps_js(self.SAMPLE_JS_WITH_ENTITY)
        table = bundle.tables["Fcst24hPrecipTable"]

        self.assertEqual(len(table.rows), 2)
        self.assertEqual(table.rows[0].area, "蘭嶼綠島")
        self.assertEqual(table.rows[1].area, "澎湖縣")


if __name__ == "__main__":
    unittest.main()
