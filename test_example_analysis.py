import unittest
from unittest.mock import patch
from types import SimpleNamespace
from example_analysis import ExampleAnalysis


class TestExampleAnalysis(unittest.TestCase):

    @patch("example_analysis.DataLoader")
    def test_run(self, mock_loader):
        fake_issue = SimpleNamespace(
            creator="user1",
            events=[]
        )

        mock_loader.return_value.get_issues.return_value = [fake_issue]

        ExampleAnalysis().run()