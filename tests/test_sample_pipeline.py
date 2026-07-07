import tempfile
import unittest
from pathlib import Path

from typhoon_day_research.pipeline import (
    SAMPLE_DGPA_HTML,
    analyze_decisions_csv,
    build_dataset_from_raw,
    run_sample_pipeline,
)


class SamplePipelineTests(unittest.TestCase):
    def test_run_sample_pipeline_writes_core_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            artifacts = run_sample_pipeline(out_dir)

            self.assertTrue(artifacts.decisions_csv.exists())
            self.assertTrue(artifacts.summary_md.exists())
            self.assertTrue(artifacts.prediction_json.exists())
            self.assertTrue(artifacts.medium_dir.exists())
            self.assertGreater(artifacts.decisions_csv.stat().st_size, 100)

    def test_build_dataset_from_raw_dgpa_attachments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "raw" / "dgpa"
            attachment_dir = raw_dir / "attachments"
            attachment_dir.mkdir(parents=True)
            (raw_dir / "notices.csv").write_text(
                "pid,title,published_date,event_date,url\n"
                "7004,90年07月30日停止上班上課公告,2001-07-30,2001-07-30,"
                "https://www.dgpa.gov.tw/information?uid=374&pid=7004\n",
                encoding="utf-8",
            )
            (attachment_dir / "7004_1.html").write_text(SAMPLE_DGPA_HTML, encoding="utf-8")

            dataset_csv = root / "outputs" / "decisions.csv"
            decisions = build_dataset_from_raw(raw_dir, dataset_csv)
            summary_md, svg_path = analyze_decisions_csv(dataset_csv, root / "outputs")

            self.assertEqual(len(decisions), 9)
            self.assertTrue(dataset_csv.exists())
            self.assertTrue(summary_md.exists())
            self.assertTrue(svg_path.exists())
            self.assertIn("臺北市", dataset_csv.read_text(encoding="utf-8"))
            self.assertIn("停止上班上課", summary_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
