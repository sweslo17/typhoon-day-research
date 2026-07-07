import unittest

from typhoon_day_research.articles.medium import render_medium_series


class MediumArticleTests(unittest.TestCase):
    def test_render_medium_series_contains_required_story_arc(self):
        drafts = render_medium_series()
        titles = [draft.title for draft in drafts]

        self.assertGreaterEqual(len(drafts), 5)
        self.assertIn("颱風假的科學", titles[0])
        self.assertTrue(any("選舉" in draft.markdown for draft in drafts))
        self.assertTrue(any("預測" in draft.markdown for draft in drafts))
        self.assertTrue(any("模型不是神諭" in draft.markdown for draft in drafts))


if __name__ == "__main__":
    unittest.main()

