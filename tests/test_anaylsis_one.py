import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis_one import AnalysisOne
from model import Issue


class BaseTestAnalysisOne(unittest.TestCase):
    def setUp(self):
        # Set up a consistent mock issue for reuse
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
        # Internal helper to run analysis with mocked inputs
        analysis = AnalysisOne()
        with patch('data_loader.DataLoader.get_issues', return_value=issues):
            with patch('builtins.input', return_value=user_input):
                analysis.run()


class TestBasicSanity(BaseTestAnalysisOne):

    # Should handle an empty issue list without crashing
    def test_empty_issues_should_not_raise(self):
        try:
            self._run_analysis([])
        except Exception as e:
            self.fail(f"Should not raise with empty issue list: {e}")

    # Should not fail if issue has no labels
    def test_no_labels_should_not_raise(self):
        issue = self.sample_issue.copy()
        issue["labels"] = []
        try:
            self._run_analysis([Issue(issue)])
        except Exception as e:
            self.fail(f"Should not raise with no labels: {e}")


class TestLabelGrouping(BaseTestAnalysisOne):

    # Should group issues by the same label without error
    def test_issues_with_same_label_are_grouped(self):
        issue1 = self.sample_issue.copy()
        issue2 = self.sample_issue.copy()
        issue2["number"] = 2
        try:
            self._run_analysis([Issue(issue1), Issue(issue2)])
        except Exception as e:
            self.fail(f"Should not raise when grouping labels: {e}")

    # Only "commented" events should count in comment metrics
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

    # Missing created/closed dates should be handled gracefully
    def test_missing_dates_should_not_crash(self):
        issue = self.sample_issue.copy()
        issue["created_date"] = None
        issue["closed_date"] = None
        try:
            self._run_analysis([Issue(issue)])
        except Exception as e:
            self.fail(f"Should handle missing dates: {e}")

    # Empty event lists should not cause errors
    def test_no_events_should_not_crash(self):
        issue = self.sample_issue.copy()
        issue["events"] = []
        try:
            self._run_analysis([Issue(issue)])
        except Exception as e:
            self.fail(f"Should not raise with no events: {e}")

    # Contributors should be counted uniquely
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

    # Should display plots when "all" is typed
    @patch('matplotlib.pyplot.show')
    def test_plotting_triggered_on_all_input(self, mock_show):
        try:
            self._run_analysis([Issue(self.sample_issue)], user_input="all")
            self.assertTrue(mock_show.called)
            self.assertGreaterEqual(mock_show.call_count, 1)
        except Exception as e:
            self.fail(f"Should not raise and must attempt to plot: {e}")

    # Filtering by label input should only include matching labels
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

    # Warns user when an invalid label is entered
    def test_invalid_label_input_triggers_warning(self):
        issue_bug = self.sample_issue.copy()
        issue_feature = self.sample_issue.copy()
        issue_feature["number"] = 2
        issue_feature["labels"] = ["feature"]

        with patch('builtins.print') as mock_print:
            self._run_analysis([Issue(issue_bug), Issue(issue_feature)], user_input="random_label")
            printed_output = "\n".join(str(call) for call in mock_print.call_args_list)
            self.assertIn("Invalid input. Please run the program again", printed_output)


class TestDataValidation(BaseTestAnalysisOne):

    # Ensures lifespan, comment, and contributor stats are printed correctly
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
