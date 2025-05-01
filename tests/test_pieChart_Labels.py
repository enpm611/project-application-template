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

    # ADDED FOR SECOND TRIAL
    # labels list has non-strings (Expected to FAIL: AttributeError)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_analyze_label_distribution_with_non_string_labels(self, mock_get_issues):
        mock_get_issues.return_value = [
            MagicMock(labels=[None, 123, True])
        ]
        analysis = LabelPieChartAnalysis()
        with self.assertRaises(AttributeError):
            analysis.analyze_label_distribution("kind/")

    # Negative values in pie chart counts (Expected to FAIL: ValueError)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_plot_pie_chart_with_negative_counts(self, mock_get_issues):
        mock_get_issues.return_value = []
        analysis = LabelPieChartAnalysis()
        label_counter = Counter({"kind/bug": -5, "kind/feature": -3})
        with self.assertRaises(ValueError):
            analysis.plot_pie_chart(label_counter, "Negative Counts Test")

    # Zero total pie chart again (Expected to pass safely)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_plot_pie_chart_with_zero_total(self, mock_get_issues):
        mock_get_issues.return_value = []
        analysis = LabelPieChartAnalysis()
        label_counter = Counter()
        try:
            analysis.plot_pie_chart(label_counter, "Zero Total Test")
        except ZeroDivisionError:
            self.fail("plot_pie_chart crashed with ZeroDivisionError")

    # DataLoader throws exception (Expected to FAIL: constructor crash)
    @patch('pieChart_Labels.DataLoader.get_issues', side_effect=Exception("Fake failure"))
    def test_DataLoader_crash_handling(self, mock_get_issues):
        with self.assertRaises(Exception):
            LabelPieChartAnalysis()

    # AGGRESSIVE
    # Labels are dict instead of list (Expected to FAIL or behave oddly)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_labels_are_dict_instead_of_list(self, mock_get_issues):
        mock_get_issues.return_value = [
            MagicMock(labels={"kind/bug": 1})
        ]
        analysis = LabelPieChartAnalysis()
        with self.assertRaises(Exception):
            analysis.analyze_label_distribution("kind/")

    # Issue.labels is dict (Expected to FAIL: TypeError)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_issue_labels_are_dict(self, mock_get_issues):
        mock_get_issues.return_value = [
            MagicMock(labels={"kind/bug": 1})
        ]
        analysis = LabelPieChartAnalysis()
        with self.assertRaises(TypeError):
            analysis.analyze_label_distribution("kind/")

    # Labels contain non-strings (Expected to FAIL: AttributeError)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_issue_labels_contain_non_strings(self, mock_get_issues):
        mock_get_issues.return_value = [
            MagicMock(labels=[123, None, True])
        ]
        analysis = LabelPieChartAnalysis()
        with self.assertRaises(AttributeError):
            analysis.analyze_label_distribution("kind/")

    # label_counter with negative counts (Expected to FAIL: ValueError)
    @patch('pieChart_Labels.DataLoader.get_issues')
    def test_label_counter_with_negative_counts(self, mock_get_issues):
        mock_get_issues.return_value = []
        analysis = LabelPieChartAnalysis()
        label_counter = Counter({"kind/bug": -10, "kind/feature": -5})
        try:
            analysis.plot_pie_chart(label_counter, "Negative Counts Test")
        except ValueError as e:
            self.assertIn("Wedge sizes 'x' must be non negative values", str(e))

if __name__ == '__main__':
    unittest.main()