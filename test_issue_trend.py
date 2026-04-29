import unittest
from unittest.mock import patch
from types import SimpleNamespace
from issue_trend_analysis import IssueTrendAnalysis


class TestIssueTrend(unittest.TestCase):

    @patch("issue_trend_analysis.DataLoader")
    def test_basic_run(self, mock_loader):
        fake_issue = SimpleNamespace(
            state=SimpleNamespace(value="open"),
            labels=["bug"],
            events=[],
            created_date=None
        )

        mock_loader.return_value.load_data.return_value = [fake_issue]

        IssueTrendAnalysis().run()