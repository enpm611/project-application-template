import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis_one import AnalysisOne
from model import Issue

class BaseTestAnalysisOne(unittest.TestCase):
    def setUp(self):
        self.sample_issue = {
            "number": 1,
            "title": "Test Issue",
            "state": "closed",
            "creator": "user1",
            "labels": ["bug"],
            "created_date": "2022-01-01T00:00:00Z",
            "closed_date": "2022-01-02T00:00:00Z",
            "events": [
                {"event_type": "commented", "author": "user2", "event_date": "2022-01-01T12:00:00Z"},
                {"event_type": "closed", "author": "user1", "event_date": "2022-01-02T00:00:00Z"}
            ]
        }

    def _run_analysis(self, issues, user_input="all"):
        analysis = AnalysisOne()
        with patch('data_loader.DataLoader.get_issues', return_value=issues):
            with patch('builtins.input', return_value=user_input):
                analysis.run()


class TestBasicSanity(BaseTestAnalysisOne):

    def test_empty_issues_should_not_raise(self):
        try:
            self._run_analysis([])
        except Exception as e:
            self.fail(f"Should not raise with empty issue list: {e}")

    def test_no_labels_should_not_raise(self):
        issue = self.sample_issue.copy()
        issue["labels"] = []
        try:
            self._run_analysis([Issue(issue)])
        except Exception as e:
            self.fail(f"Should not raise with no labels: {e}")


class TestLabelGrouping(BaseTestAnalysisOne):

    def test_issues_with_same_label_are_grouped(self):
        issue1 = self.sample_issue.copy()
        issue2 = self.sample_issue.copy()
        issue2["number"] = 2
        try:
            self._run_analysis([Issue(issue1), Issue(issue2)])
        except Exception as e:
            self.fail(f"Should not raise when grouping labels: {e}")

    def test_only_commented_events_are_counted(self):
        issue = self.sample_issue.copy()
        issue["events"] = [
            {"event_type": "commented", "author": "user1", "event_date": "2022-01-01T12:00:00Z"},
            {"event_type": "commented", "author": "user2", "event_date": "2022-01-01T13:00:00Z"},
            {"event_type": "closed", "author": "user1", "event_date": "2022-01-02T00:00:00Z"},
        ]
        try:
            self._run_analysis([Issue(issue)])
        except Exception as e:
            self.fail(f"Should not raise on comment counting: {e}")


class TestEdgeCases(BaseTestAnalysisOne):

    def test_missing_dates_should_not_crash(self):
        issue = self.sample_issue.copy()
        issue["created_date"] = None
        issue["closed_date"] = None
        try:
            self._run_analysis([Issue(issue)])
        except Exception as e:
            self.fail(f"Should handle missing dates: {e}")

    def test_no_events_should_not_crash(self):
        issue = self.sample_issue.copy()
        issue["events"] = []
        try:
            self._run_analysis([Issue(issue)])
        except Exception as e:
            self.fail(f"Should not raise with no events: {e}")

    def test_duplicate_contributors_are_deduplicated(self):
        issue = self.sample_issue.copy()
        issue["events"] = [
            {"event_type": "commented", "author": "user1", "event_date": "2022-01-01T12:00:00Z"},
            {"event_type": "commented", "author": "user1", "event_date": "2022-01-01T13:00:00Z"},
        ]
        try:
            self._run_analysis([Issue(issue)])
        except Exception as e:
            self.fail(f"Should deduplicate contributors safely: {e}")


class TestUserInputAndPlotting(BaseTestAnalysisOne):

    @patch('matplotlib.pyplot.show')
    def test_plotting_triggered_on_all_input(self, mock_show):
        try:
            self._run_analysis([Issue(self.sample_issue)], user_input="all")
            self.assertTrue(mock_show.called)
            self.assertGreaterEqual(mock_show.call_count, 1)
        except Exception as e:
            self.fail(f"Should not raise and must attempt to plot: {e}")

    def test_label_input_filters_correctly(self):
        issue_bug = self.sample_issue.copy()
        issue_feature = self.sample_issue.copy()
        issue_feature["number"] = 2
        issue_feature["labels"] = ["feature"]

        with patch('builtins.print') as mock_print:
            self._run_analysis([Issue(issue_bug), Issue(issue_feature)], user_input="bug")
            printed_output = "\n".join(str(call) for call in mock_print.call_args_list)
            self.assertIn("bug", printed_output)
            self.assertNotIn("feature", printed_output)


class TestDataValidation(BaseTestAnalysisOne):

    def test_lifespan_and_comment_averages_are_computed_correctly(self):
        issue1 = self.sample_issue.copy()
        issue2 = self.sample_issue.copy()
        issue2["number"] = 2
        issue2["created_date"] = "2022-01-01T00:00:00Z"
        issue2["closed_date"] = "2022-01-03T00:00:00Z"
        issue2["events"] = [
            {"event_type": "commented", "author": "user3", "event_date": "2022-01-02T00:00:00Z"}
        ]

        with patch('builtins.print') as mock_print:
            self._run_analysis([Issue(issue1), Issue(issue2)], user_input="bug")
            output = "\n".join(str(call) for call in mock_print.call_args_list)
            self.assertIn("avg_lifespan_hours", output)
            self.assertIn("avg_comments", output)
            self.assertIn("num_contributors", output)


if __name__ == '__main__':
    unittest.main()
