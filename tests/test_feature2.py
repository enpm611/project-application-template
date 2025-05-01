import unittest
from unittest.mock import patch, mock_open
import json
from feature2 import LabelCommentGraph

# Sample issues to mock data for all feature2 tests
sample_issues = [
    {
        "labels": ["kind/bug", "area/ui"],
        "created_date": "2022-01-01T00:00:00Z",
        "events": [{"event_type": "commented"}, {"event_type": "closed"}]
    },
    {
        "labels": ["kind/feature", "area/api"],
        "created_date": "2023-01-01T00:00:00Z",
        "events": [{"event_type": "commented"}, {"event_type": "commented"}]
    },
    {
        "labels": ["kind/bug"],
        "created_date": "2022-05-01T00:00:00Z",
        "events": []
    }
]

class TestLabelCommentGraph(unittest.TestCase):

    # Setup mock data before each test using patch
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps(sample_issues))
    def setUp(self, mock_file):
        self.graph = LabelCommentGraph("dummy_path.json")

    # Ensure 3 issues are loaded from valid JSON
    def test_load_issues_success(self):
        self.assertEqual(len(self.graph.issues), 3)

    # Verify behavior when JSON file is missing
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_issues_file_not_found(self, mock_file):
        graph = LabelCommentGraph("missing.json")
        self.assertEqual(graph.issues, [])

    # Verify behavior when JSON content is invalid
    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    def test_load_issues_json_decode_error(self, mock_file):
        graph = LabelCommentGraph("bad.json")
        self.assertEqual(graph.issues, [])

    # Check correct comment counts are attributed per label
    def test_analyze_comments_by_label(self):
        result = self.graph.analyze_comments_by_label()
        self.assertEqual(result["kind/bug"], 1)
        self.assertEqual(result["kind/feature"], 2)
        self.assertEqual(result["area/ui"], 1)
        self.assertEqual(result["area/api"], 2)

    # Verify top label for each year is returned correctly
    def test_analyze_most_used_labels_by_year(self):
        result = self.graph.analyze_most_used_labels_by_year("area/")
        self.assertEqual(result[2022], ("area/ui", 1))
        self.assertEqual(result[2023], ("area/api", 1))

    # Check if specific label's trend over years is computed properly
    def test_analyze_specific_label_over_years(self):
        result = self.graph.analyze_specific_label_over_years("kind/bug")
        self.assertEqual(result[2022], 2)

    # Ensure bar chart for label comment distribution is plotted
    @patch("matplotlib.pyplot.show")
    def test_plot_results(self, mock_show):
        data = self.graph.analyze_comments_by_label()
        self.graph.plot_results(data, top_n=2)
        self.assertTrue(mock_show.called)

    # Ensure bar chart of most-used labels per year is plotted
    @patch("matplotlib.pyplot.show")
    def test_plot_most_used_by_year(self, mock_show):
        data = self.graph.analyze_most_used_labels_by_year("area/")
        self.graph.plot_most_used_by_year(data, "Test Title")
        self.assertTrue(mock_show.called)

    # Ensure line chart of label trend over time is plotted
    @patch("matplotlib.pyplot.show")
    def test_plot_label_trend_over_years(self, mock_show):
        trend = self.graph.analyze_specific_label_over_years("kind/feature")
        self.graph.plot_label_trend_over_years(trend, "kind/feature")
        self.assertTrue(mock_show.called)


if __name__ == "__main__":
    unittest.main()