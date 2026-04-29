import unittest
from unittest.mock import patch
from types import SimpleNamespace
from contributor_activity_analysis import ContributorActivityAnalysis


class TestContributorActivityFullCoverage(unittest.TestCase):

    @patch("contributor_activity_analysis.DataLoader")
    def test_no_issues(self, mock_loader):
        mock_loader.return_value.load_data.return_value = []
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.config.get_parameter")
    def test_user_no_activity(self, mock_config, mock_loader):
        mock_config.return_value = "userX"

        issues = [
            SimpleNamespace(creator="user1", events=[])
        ]

        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.config.get_parameter")
    def test_user_created_no_events(self, mock_config, mock_loader):
        mock_config.return_value = "user1"

        issues = [
            SimpleNamespace(creator="user1", events=[])
        ]

        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.config.get_parameter")
    def test_user_events_no_event_type(self, mock_config, mock_loader):
        mock_config.return_value = "user1"

        issues = [
            SimpleNamespace(
                creator="user2",
                events=[SimpleNamespace(author="user1", event_type=None)]
            )
        ]

        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.config.get_parameter")
    def test_user_full_activity(self, mock_config, mock_loader):
        mock_config.return_value = "user1"

        issues = [
            SimpleNamespace(
                creator="user1",
                events=[
                    SimpleNamespace(author="user1", event_type="opened"),
                    SimpleNamespace(author="user1", event_type="closed"),
                ]
            )
        ]

        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.config.get_parameter")
    def test_global_stats(self, mock_config, mock_loader):
        mock_config.return_value = None

        issues = [
            SimpleNamespace(
                creator="user1",
                events=[SimpleNamespace(author="user2")]
            ),
            SimpleNamespace(
                creator="user2",
                events=[]
            )
        ]

        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    def test_injected_issues(self):
        issues = [
            SimpleNamespace(
                creator="user1",
                events=[SimpleNamespace(author="user1", event_type="opened")]
            )
        ]

        ContributorActivityAnalysis(issues=issues).run()
