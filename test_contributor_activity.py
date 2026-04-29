import unittest
from unittest.mock import patch
from types import SimpleNamespace
from contributor_activity_analysis import ContributorActivityAnalysis


class TestContributorActivity(unittest.TestCase):

    @patch("contributor_activity_analysis.DataLoader")
    def test_basic_run(self, mock_loader):
        issues = [
            SimpleNamespace(
                creator="user1",
                events=[SimpleNamespace(author="user1")]
            )
        ]
        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    def test_multiple_creators(self, mock_loader):
        issues = [
            SimpleNamespace(creator="user1", events=[]),
            SimpleNamespace(creator="user2", events=[])
        ]
        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    def test_with_event_authors(self, mock_loader):
        issues = [
            SimpleNamespace(
                creator="user1",
                events=[
                    SimpleNamespace(author="user2"),
                    SimpleNamespace(author="user3")
                ]
            )
        ]
        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    def test_missing_creator(self, mock_loader):
        issues = [
            SimpleNamespace(
                creator=None,
                events=[]
            )
        ]
        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

  
    @patch("contributor_activity_analysis.DataLoader")
    def test_empty_issues(self, mock_loader):
        mock_loader.return_value.load_data.return_value = []
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    def test_multiple_events_and_counts(self, mock_loader):
        issues = [
            SimpleNamespace(
                creator="user1",
                events=[
                    SimpleNamespace(author="user2"),
                    SimpleNamespace(author="user2"),
                    SimpleNamespace(author="user3")
                ]
            ),
            SimpleNamespace(
                creator="user2",
                events=[
                    SimpleNamespace(author="user1"),
                    SimpleNamespace(author=None)
                ]
            )
        ]
        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    def test_issue_with_no_events(self, mock_loader):
        issues = [
            SimpleNamespace(
                creator="user1",
                events=[]
            )
        ]
        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()

    @patch("contributor_activity_analysis.DataLoader")
    def test_all_none_values(self, mock_loader):
        issues = [
            SimpleNamespace(
                creator=None,
                events=[SimpleNamespace(author=None)]
            )
        ]
        mock_loader.return_value.load_data.return_value = issues
        ContributorActivityAnalysis().run()
