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