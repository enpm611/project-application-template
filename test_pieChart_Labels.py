from typing import Counter
import unittest
from unittest.mock import patch, MagicMock
import matplotlib
matplotlib.use('Agg')  # Prevent GUI issues with matplotlib during tests

from pieChart_Labels import LabelPieChartAnalysis

class TestLabelPieChartAnalysis(unittest.TestCase):

    def setUp(self):
        # Setting up sample mock issues with proper labels
        self.mock_issues = [
            MagicMock(labels=["kind/bug", "status/triaged", "area/packaging"]),
            MagicMock(labels=["kind/feature", "status/needs info"]),
            MagicMock(labels=["kind/bug", "area/dependencies"]),
        ]

    # Normal case: valid issues and labels (Expected to pass)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_run_analysis_normal(self, mock_get_issues):
        mock_get_issues.return_value = self.mock_issues
        analysis = LabelPieChartAnalysis()
        try:
            analysis.run()
        except Exception as e:
            self.fail(f"LabelPieChartAnalysis.run() raised Exception unexpectedly: {e}")

    # Empty issues list (Expected to pass)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_run_analysis_empty_issues(self, mock_get_issues):
        mock_get_issues.return_value = []
        analysis = LabelPieChartAnalysis()
        try:
            analysis.run()
        except Exception as e:
            self.fail(f"LabelPieChartAnalysis.run() failed with empty issues: {e}")

    # No matching labels present (Expected to pass)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_run_analysis_no_matching_labels(self, mock_get_issues):
        mock_issues = [
            MagicMock(labels=["random_label", "miscellaneous"]),
            MagicMock(labels=["test123"])
        ]
        mock_get_issues.return_value = mock_issues
        analysis = LabelPieChartAnalysis()
        try:
            analysis.run()
        except Exception as e:
            self.fail(f"LabelPieChartAnalysis.run() failed with non-matching labels: {e}")

    # Labels are malformed: None and string (Expected to pass but behavior can be odd)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_run_analysis_malformed_labels(self, mock_get_issues):
        mock_issues = [
            MagicMock(labels=None),
            MagicMock(labels="kind/bug")  # Wrong: string not list
        ]
        mock_get_issues.return_value = mock_issues
        analysis = LabelPieChartAnalysis()
        try:
            analysis.run()
        except Exception as e:
            self.fail(f"LabelPieChartAnalysis.run() crashed with malformed labels: {e}")

    # ADDED FOR MORE TESTS
    # Labels contain non-string types (Expected to FAIL: AttributeError)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_issue_with_non_string_labels(self, mock_get_issues):
        mock_issues = [
            MagicMock(labels=[123, True, None])
        ]
        mock_get_issues.return_value = mock_issues
        analysis = LabelPieChartAnalysis()
        with self.assertRaises(AttributeError):
            analysis.analyze_label_distribution("kind/")

    # Labels are a single string instead of list (Expected to pass weirdly)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_issue_labels_as_string(self, mock_get_issues):
        mock_issues = [
            MagicMock(labels="kind/bug")
        ]
        mock_get_issues.return_value = mock_issues
        analysis = LabelPieChartAnalysis()
        try:
            analysis.analyze_label_distribution("kind/")
        except Exception as e:
            self.fail(f"analyze_label_distribution crashed when labels was string: {e}")

    # Empty Counter in pie chart (Expected to pass safely)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_plot_pie_chart_zero_total(self, mock_get_issues):
        mock_get_issues.return_value = []
        analysis = LabelPieChartAnalysis()
        label_counter = Counter()
        try:
            analysis.plot_pie_chart(label_counter, "Zero Total Test")
        except ZeroDivisionError:
            self.fail("plot_pie_chart raised ZeroDivisionError on empty data")

if __name__ == '__main__':
    unittest.main()