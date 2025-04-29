import unittest
from unittest.mock import patch, MagicMock
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis_one import AnalysisOne
from model import Issue, Event

class TestAnalysisOne(unittest.TestCase):
    def setUp(self):
        # Create mock Issues
        issue_data = {
            "number": 1,
            "title": "Test Issue 1",
            "state": "closed",
            "creator": "user1",
            "labels": ["bug"],
            "created_date": "2022-01-01T00:00:00Z",
            "closed_date": "2022-01-02T00:00:00Z",
            "events": [
                {
                    "event_type": "commented",
                    "author": "user2",
                    "event_date": "2022-01-01T12:00:00Z"
                },
                {
                    "event_type": "closed",
                    "author": "user1",
                    "event_date": "2022-01-02T00:00:00Z"
                }
            ]
        }
        self.mock_issues = [Issue(issue_data)]

#region Basic sanity checks
    # ❎ Empty issues list (4/29: failed)
    @patch('data_loader.DataLoader.get_issues')
    def test_run_analysis_empty_issues(self, mock_get_issues):
        mock_get_issues.return_value = []
        analysis = AnalysisOne()
        try:
            with patch('builtins.input', return_value='all'):
                analysis.run()
        except Exception as e:
            self.fail(f"LabelPieChartAnalysis.run() failed with empty issues: {e}")

    
    # ❎ No labels present (4/29: failed)
    @patch('data_loader.DataLoader.get_issues')
    def test_run_analysis_no_labels(self, mock_get_issues):
        issue_data = {
            "number": 1,
            "title": "Test Issue 1",
            "state": "closed",
            "creator": "user1",
            "labels": [],
            "created_date": "2022-01-01T00:00:00Z",
            "closed_date": "2022-01-02T00:00:00Z",
            "events": [
                {
                    "event_type": "commented",
                    "author": "user2",
                    "event_date": "2022-01-01T12:00:00Z"
                },
                {
                    "event_type": "closed",
                    "author": "user1",
                    "event_date": "2022-01-02T00:00:00Z"
                }
            ]
        }

        mock_get_issues.return_value = [Issue(issue_data)]

        analysis = AnalysisOne()
        try:
            with patch('builtins.input', return_value='all'):
                analysis.run()
        except Exception as e:
            self.fail(f"AnalysisOne.run() raised an exception: {e}")
#endregion

#region Label grouping and statistics - Makes sure the analysis works as intended
    # ✅ Check that multiple issues with the same label are grouped
    @patch('data_loader.DataLoader.get_issues')
    def test_run_analysis_correct_grouping_by_label(self, mock_get_issues):
        issue_data = [{
            "number": 1,
            "title": "Test Issue 1",
            "state": "closed",
            "creator": "user1",
            "labels": ["bug"],
            "created_date": "2022-01-01T00:00:00Z",
            "closed_date": "2022-01-03T00:00:00Z",
            "events": [
                {
                    "event_type": "commented",
                    "author": "user2",
                    "event_date": "2022-01-01T12:00:00Z"
                },
                {
                    "event_type": "closed",
                    "author": "user1",
                    "event_date": "2022-01-02T00:00:00Z"
                }
            ]
        },
        {
            "number": 2,
            "title": "Test Issue 2",
            "state": "closed",
            "creator": "user1",
            "labels": ["bug"],
            "created_date": "2022-01-01T00:00:00Z",
            "closed_date": "2022-01-02T00:00:00Z",
            "events": [
                {
                    "event_type": "commented",
                    "author": "user2",
                    "event_date": "2022-01-01T12:00:00Z"
                },
                {
                    "event_type": "closed",
                    "author": "user1",
                    "event_date": "2022-01-02T00:00:00Z"
                }
            ]
        }]

        mock_get_issues.return_value = [Issue(data) for data in issue_data]

        analysis = AnalysisOne()
        try:
            with patch('builtins.input', return_value='all'):
                analysis.run()
        except Exception as e:
            self.fail(f"AnalysisOne.run() raised an exception: {e}")

    # ✅ Ensure it only counts events where event_type == "commented"
    @patch('data_loader.DataLoader.get_issues')
    def test_run_analysis_comment_counting(self, mock_get_issues):
        issue_data = {
            "number": 1,
            "title": "Test Issue 1",
            "state": "closed",
            "creator": "user1",
            "labels": ["bug"],
            "created_date": "2022-01-01T00:00:00Z",
            "closed_date": "2022-01-03T00:00:00Z",
            "events": [
                {
                    "event_type": "commented",
                    "author": "user2",
                    "event_date": "2022-01-01T12:00:00Z"
                },
                {
                    "event_type": "commented",
                    "author": "user1",
                    "event_date": "2022-01-02T00:00:00Z"
                }
            ]
        }
        mock_get_issues.return_value = [Issue(issue_data)]

        analysis = AnalysisOne()
        try:
            with patch('builtins.input', return_value='all'):
                analysis.run()
        except Exception as e:
            self.fail(f"AnalysisOne.run() raised an exception: {e}")
#endregion

#region Edge cases
    # ❎ Ensure lifespan is set to None if dates are missing (4/29: failed)
    @patch('data_loader.DataLoader.get_issues')
    def test_run_analysis_issues_with_missing_dates(self, mock_get_issues):
        issue_data = {
            "number": 1,
            "title": "Test Issue 1",
            "state": "closed",
            "creator": "user1",
            "labels": ["bug"],
            "created_date": None,
            "closed_date": None,
            "events": [
                {
                    "event_type": "commented",
                    "author": "user1",
                    "event_date": "2022-01-01T12:00:00Z"
                }
            ]
        }
        mock_get_issues.return_value = [Issue(issue_data)]

        analysis = AnalysisOne()
        try:
            with patch('builtins.input', return_value='all'):
                analysis.run()
        except Exception as e:
            self.fail(f"AnalysisOne.run() raised an exception: {e}")

    # ✅ Make sure contributor and comment counts don’t crash on empty
    @patch('data_loader.DataLoader.get_issues')
    def test_run_analysis_issues_with_no_events(self, mock_get_issues):
        issue_data = {
            "number": 1,
            "title": "Test Issue 1",
            "state": "closed",
            "creator": "user1",
            "labels": ["bug"],
            "created_date": "2022-01-01T00:00:00Z",
            "closed_date": "2022-01-03T00:00:00Z",
            "events": []
        }
        mock_get_issues.return_value = [Issue(issue_data)]

        analysis = AnalysisOne()
        try:
            with patch('builtins.input', return_value='all'):
                analysis.run()
        except Exception as e:
            self.fail(f"AnalysisOne.run() raised an exception: {e}")

    # ✅ Check contributor deduplication works
    @patch('data_loader.DataLoader.get_issues')
    def test_run_analysis_issues_with_duplicate_contributors(self, mock_get_issues):
        issue_data = {
            "number": 1,
            "title": "Test Issue 1",
            "state": "closed",
            "creator": "user1",
            "labels": ["bug"],
            "created_date": "2022-01-01T00:00:00Z",
            "closed_date": "2022-01-03T00:00:00Z",
            "events": [
                {
                    "event_type": "commented",
                    "author": "user1",
                    "event_date": "2022-01-01T12:00:00Z"
                },
                {
                    "event_type": "commented",
                    "author": "user1",
                    "event_date": "2022-01-02T00:00:00Z"
                }
            ]
        }
        mock_get_issues.return_value = [Issue(issue_data)]

        analysis = AnalysisOne()
        try:
            with patch('builtins.input', return_value='all'):
                analysis.run()
        except Exception as e:
            self.fail(f"AnalysisOne.run() raised an exception: {e}")
#endregion

#region Check user input
    # ✅ Check input works
    @patch('builtins.input', return_value='all')
    @patch('matplotlib.pyplot.show')
    @patch('data_loader.DataLoader.get_issues')
    def test_plotting_triggered_on_all_input(self, mock_get_issues, mock_show, mock_input):
        mock_get_issues.return_value = self.mock_issues  # Assumes self.mock_issues is defined in setUp()

        analysis = AnalysisOne()

        try:
            analysis.run()

            # Check if plotting was attempted
            self.assertTrue(mock_show.called)
            self.assertGreaterEqual(mock_show.call_count, 1)
        except Exception as e:
            self.fail(f"AnalysisOne.run() raised an exception: {e}")
#endregion

if __name__ == '__main__':
    unittest.main()
