import unittest
from datetime import datetime
from src.label_comment_graph import LabelCommentGraph  # Adjust this import based on your project structure

class TestLabelCommentGraph(unittest.TestCase):

    def setUp(self):
        # Inject test issues manually to avoid file dependency
        self.graph = LabelCommentGraph(json_path=None)
        self.graph.issues = [
            {
                "labels": ["kind/bug", "area/ui"],
                "events": [{"event_type": "commented"}, {"event_type": "closed"}],
                "created_date": "2022-04-15T10:00:00Z"
            },
            {
                "labels": ["kind/feature"],
                "events": [{"event_type": "commented"}, {"event_type": "commented"}],
                "created_date": "2023-01-10T12:30:00Z"
            },
            {
                "labels": ["kind/bug", "area/backend"],
                "events": [],
                "created_date": "2022-06-20T18:45:00Z"
            }
        ]

    def test_analyze_comments_by_label(self):
        result = self.graph.analyze_comments_by_label()
        self.assertEqual(result["kind/bug"], 2)  # 1 issue with 1 comment, 1 with 0
        self.assertEqual(result["kind/feature"], 2)  # 1 issue with 2 comments
        self.assertEqual(result["area/ui"], 1)
        self.assertEqual(result["area/backend"], 0)

    def test_analyze_most_used_labels_by_year(self):
        result = self.graph.analyze_most_used_labels_by_year("area/")
        self.assertIn(2022, result)
        self.assertEqual(result[2022][0], "area/ui")  # Both labels occur once, so any could appear
        self.assertEqual(result[2022][1], 1)

    def test_analyze_specific_label_over_years(self):
        bug_trend = self.graph.analyze_specific_label_over_years("kind/bug")
        self.assertEqual(bug_trend, {2022: 2})

        feature_trend = self.graph.analyze_specific_label_over_years("kind/feature")
        self.assertEqual(feature_trend, {2023: 1})

    def test_handle_missing_created_date(self):
        self.graph.issues.append({
            "labels": ["kind/bug"],
            "events": [{"event_type": "commented"}]
        })
        result = self.graph.analyze_specific_label_over_years("kind/bug")
        self.assertEqual(result[2022], 2)  # Should not increment because of missing date

    def test_empty_issue_list(self):
        self.graph.issues = []
        self.assertEqual(self.graph.analyze_comments_by_label(), {})
        self.assertEqual(self.graph.analyze_most_used_labels_by_year("kind/"), {})
        self.assertEqual(self.graph.analyze_specific_label_over_years("kind/bug"), {})


if __name__ == "__main__":
    unittest.main()
