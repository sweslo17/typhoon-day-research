import unittest

from typhoon_day_research.parsers.dgpa import (
    classify_decision_text,
    parse_decision_table,
    parse_history_list,
    roc_date_to_date,
)


class DgpaParserTests(unittest.TestCase):
    def test_roc_date_to_date_handles_dot_format(self):
        self.assertEqual(roc_date_to_date("90.07.30").isoformat(), "2001-07-30")
        self.assertEqual(roc_date_to_date("115.06.29").isoformat(), "2026-06-29")

    def test_parse_history_list_extracts_notice_links_and_event_dates(self):
        html = """
        <div class="news-list">
          <dl><a href="information?uid=374&amp;pid=7004"><dt>90.07.30</dt>
          <dd><p>90年07月30日天然災害停止辦公及上課情形</p></dd></a></dl>
        </div>
        """
        notices = parse_history_list(html, base_url="https://www.dgpa.gov.tw/")
        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0].pid, "7004")
        self.assertEqual(notices[0].event_date.isoformat(), "2001-07-30")
        self.assertEqual(notices[0].url, "https://www.dgpa.gov.tw/information?uid=374&pid=7004")

    def test_classify_decision_text_detects_full_half_and_school_only(self):
        full = classify_decision_text("今天停止辦公、停止上課。")
        afternoon = classify_decision_text("今天下午停止辦公、停止上課。")
        school_only = classify_decision_text("今天照常辦公、高中及高中以下停止上課。")

        self.assertEqual(full.work_status, "stopped")
        self.assertEqual(full.class_status, "stopped")
        self.assertEqual(full.period, "full_day")
        self.assertEqual(afternoon.period, "afternoon")
        self.assertEqual(school_only.work_status, "normal")
        self.assertEqual(school_only.class_status, "partial_school")

    def test_classify_decision_text_handles_standard_threshold_language(self):
        reached = classify_decision_text("今天已達停止上班及上課標準。")
        not_reached = classify_decision_text("尚未列入警戒區。 明天未達停止上班及上課標準。")
        not_alerted = classify_decision_text("尚未列入警戒區。")

        self.assertEqual(reached.work_status, "stopped")
        self.assertEqual(reached.class_status, "stopped")
        self.assertEqual(not_reached.work_status, "normal")
        self.assertEqual(not_reached.class_status, "normal")
        self.assertEqual(not_alerted.work_status, "normal")
        self.assertEqual(not_alerted.class_status, "normal")

    def test_parse_decision_table_extracts_county_rows(self):
        html = """
        <table border="1">
          <tr><td>區域</td><td>縣巿名稱</td><td>是否停止辦公上課情形</td></tr>
          <tr><td rowspan="2">北部地區</td><td>基隆巿</td><td>今天停止辦公、停止上課。</td></tr>
          <tr><td>新竹縣</td><td>今天下午停止辦公、停止上課。</td></tr>
        </table>
        """
        rows = parse_decision_table(html, notice_date=roc_date_to_date("90.07.30"), notice_pid="7004")
        self.assertEqual([row.county for row in rows], ["基隆市", "新竹縣"])
        self.assertEqual(rows[0].work_status, "stopped")
        self.assertEqual(rows[1].period, "afternoon")


if __name__ == "__main__":
    unittest.main()
