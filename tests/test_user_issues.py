import unittest
from unittest.mock import patch, MagicMock
import scripts.user_issues


class TestUserIssues(unittest.TestCase):

    @patch("scripts.user_issues.bar_chart")
    @patch("scripts.user_issues.logger")
    @patch("scripts.user_issues.load_json")
    def test_run_with_valid_data(self, mock_load_json, mock_logger, mock_bar_chart):
        mock_data = [
            {"events": [{"author": "alice"}, {"author": "bob"}]},
            {"events": [{"author": "alice"}, {"author": "carol"}]},
        ]
        mock_load_json.return_value = mock_data

        scripts.user_issues.run()

        mock_load_json.assert_called_once_with("poetry.json")
        self.assertTrue(mock_logger.info.called)
        mock_bar_chart.assert_called_once()

        authors, counts, *_ = mock_bar_chart.call_args[0]
        self.assertEqual(authors, ("alice", "bob", "carol"))
        self.assertEqual(counts, (2, 1, 1))

    @patch("scripts.user_issues.logger")
    @patch("scripts.user_issues.load_json", side_effect=Exception("file error"))
    def test_run_with_json_load_failure(self, mock_load_json, mock_logger):
        scripts.user_issues.run()
        mock_logger.error.assert_called_once()
        self.assertIn("Error loading JSON", mock_logger.error.call_args[0][0])

    @patch("scripts.user_issues.bar_chart")
    @patch("scripts.user_issues.logger")
    @patch("scripts.user_issues.load_json")
    def test_run_with_no_authors(self, mock_load_json, mock_logger, mock_bar_chart):
        mock_data = [
            {"events": [{"actor": "xyz"}]},  # No "author"
            {"events": [{}]},  # Empty dict
            {"events": [{"author": None}]}  # Null author
        ]
        mock_load_json.return_value = mock_data

        scripts.user_issues.run()

        mock_logger.warning.assert_called_once_with("No author events found in the dataset.")
        mock_bar_chart.assert_not_called()

    @patch("scripts.user_issues.bar_chart")
    @patch("scripts.user_issues.logger")
    @patch("scripts.user_issues.load_json")
    def test_run_with_empty_author_counts(self, mock_load_json, mock_logger, mock_bar_chart):
        # Artificial case where top_authors = []
        mock_data = [{"events": []}]  # No events → empty defaultdict
        mock_load_json.return_value = mock_data

        scripts.user_issues.run()

        mock_logger.warning.assert_called_once_with("No author events found in the dataset.")
        mock_bar_chart.assert_not_called()


if __name__ == "__main__":
    unittest.main()