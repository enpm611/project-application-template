import unittest
from unittest.mock import patch
from types import SimpleNamespace
from label_activity_analysis import LabelActivityAnalysis


class TestLabelActivity(unittest.TestCase):

    @patch("label_activity_analysis.DataLoader")
    def test_basic_run(self, mock_loader):
        fake_issue = SimpleNamespace(
            labels=["bug"],
            events=[]
        )

        mock_loader.return_value.load_data.return_value = [fake_issue]

        LabelActivityAnalysis().run()


    @patch("label_activity_analysis.DataLoader")
    def test_no_issues(self, mock_loader):
        mock_loader.return_value.load_data.return_value = []

        LabelActivityAnalysis().run()


    @patch("label_activity_analysis.DataLoader")
    @patch("label_activity_analysis.config.get_parameter")
    def test_with_label_filter(self, mock_config, mock_loader):
        mock_config.return_value = "bug"

        issues = [
            SimpleNamespace(labels=["bug"], events=[]),
            SimpleNamespace(labels=["feature"], events=[])
        ]

        mock_loader.return_value.load_data.return_value = issues

        LabelActivityAnalysis().run()


    @patch("label_activity_analysis.DataLoader")
    @patch("label_activity_analysis.config.get_parameter")
    def test_label_not_found(self, mock_config, mock_loader):
        mock_config.return_value = "nonexistent"

        issues = [
            SimpleNamespace(labels=["bug"], events=[])
        ]

        mock_loader.return_value.load_data.return_value = issues

        LabelActivityAnalysis().run()


    @patch("label_activity_analysis.DataLoader")
    def test_event_types(self, mock_loader):
        issues = [
            SimpleNamespace(
                labels=["bug"],
                events=[
                    SimpleNamespace(event_type="closed"),
                    SimpleNamespace(event_type="opened"),
                    SimpleNamespace(event_type=None)
                ]
            )
        ]

        mock_loader.return_value.load_data.return_value = issues

        LabelActivityAnalysis().run()


    def test_injected_issues(self):
        issues = [
            SimpleNamespace(labels=["bug"], events=[])
        ]

        LabelActivityAnalysis(issues=issues).run()