import unittest
from unittest.mock import patch
import sys

from run import parse_args, main


class TestRunArgs(unittest.TestCase):

    def test_parse_args_valid(self):
        test_args = ["run.py", "--feature", "2"]
        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            self.assertEqual(args.feature, "2")  # string, not int

    def test_parse_args_with_optional(self):
        test_args = ["run.py", "--feature", "1", "--user", "bob", "--label", "bug"]
        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            self.assertEqual(args.user, "bob")
            self.assertEqual(args.label, "bug")

    def test_parse_args_missing_required(self):
        test_args = ["run.py"]
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit):
                parse_args()


class TestRunMain(unittest.TestCase):

    @patch("run.IssueTrendAnalysis")
    @patch("run.load_data")
    def test_feature_issue_trend(self, mock_load, mock_analysis):
        test_args = ["run.py", "--feature", "1"]
        with patch.object(sys, 'argv', test_args):
            main()

        mock_analysis.assert_called()

    @patch("run.LabelActivityAnalysis")
    @patch("run.load_data")
    def test_feature_label_activity(self, mock_load, mock_analysis):
        test_args = ["run.py", "--feature", "2"]
        with patch.object(sys, 'argv', test_args):
            main()

        mock_analysis.assert_called()

    @patch("run.ContributorActivityAnalysis")
    @patch("run.load_data")
    def test_feature_contributor_activity(self, mock_load, mock_analysis):
        test_args = ["run.py", "--feature", "3"]
        with patch.object(sys, 'argv', test_args):
            main()

        mock_analysis.assert_called()

    def test_invalid_feature(self):
        test_args = ["run.py", "--feature", "999"]
        with patch.object(sys, 'argv', test_args):
            main()  # should hit "Invalid feature" branch