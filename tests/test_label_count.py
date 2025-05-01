import unittest
from unittest.mock import patch

from scripts import label_count


class TestLabelCountRun(unittest.TestCase):

    @patch("scripts.label_count.load_json")
    @patch("scripts.label_count.logger")
    @patch("scripts.label_count.bar_chart")
    def test_valid_kind_labels(self, mock_chart, mock_logger, mock_load_json):
        mock_load_json.return_value = [
            {"labels": ["kind/bug", "kind/feature", "other"]},
            {"labels": ["kind/bug", 123, None]},
        ]
        label_count.run()
        mock_chart.assert_called_once()
        mock_logger.info.assert_any_call("Starting Label Count Analysis...")
        self.assertTrue(
            any(
                "unique 'kind/' labels" in str(call)
                for call in mock_logger.info.call_args_list
            )
        )

    @patch("scripts.label_count.load_json")
    @patch("scripts.label_count.logger")
    @patch("scripts.label_count.bar_chart")
    def test_no_kind_labels(self, mock_chart, mock_logger, mock_load_json):
        mock_load_json.return_value = [
            {"labels": ["other", "notkind/value"]},
            {"labels": ["misc"]},
        ]
        label_count.run()
        mock_chart.assert_called_once_with(
            [],
            [],
            "Label Name",
            "Number of Issues",
            "Number of Issues for Each Label Type Starting with 'kind/'",
        )
        mock_logger.warning.assert_called_with(
            "No labels starting with 'kind/' were found."
        )

    @patch("scripts.label_count.load_json")
    @patch("scripts.label_count.logger")
    @patch("scripts.label_count.bar_chart")
    def test_labels_not_list(self, mock_chart, mock_logger, mock_load_json):
        mock_load_json.return_value = [{"labels": "kind/bug"}, {"labels": None}, {}]
        label_count.run()
        mock_chart.assert_called_once_with(
            [],
            [],
            "Label Name",
            "Number of Issues",
            "Number of Issues for Each Label Type Starting with 'kind/'",
        )
        mock_logger.warning.assert_called_once()

    @patch("scripts.label_count.load_json")
    @patch("scripts.label_count.logger")
    @patch("scripts.label_count.bar_chart")
    def test_invalid_label_types(self, mock_chart, mock_logger, mock_load_json):
        mock_load_json.return_value = [
            {"labels": [None, 123, ["kind/bug"], {"label": "kind/feature"}]}
        ]
        label_count.run()
        mock_chart.assert_called_once_with(
            [],
            [],
            "Label Name",
            "Number of Issues",
            "Number of Issues for Each Label Type Starting with 'kind/'",
        )
        mock_logger.warning.assert_called_once()

    @patch(
        "scripts.label_count.load_json", side_effect=FileNotFoundError("File not found")
    )
    @patch("scripts.label_count.logger")
    def test_json_file_not_found(self, mock_logger, mock_load_json):
        label_count.run()
        mock_logger.error.assert_called_once()
        self.assertIn("File not found", str(mock_logger.error.call_args))

    @patch("scripts.label_count.load_json", side_effect=ValueError("Invalid JSON"))
    @patch("scripts.label_count.logger")
    def test_json_decode_error(self, mock_logger, mock_load_json):
        label_count.run()
        mock_logger.error.assert_called_once()
        self.assertIn("Invalid JSON", str(mock_logger.error.call_args))


if __name__ == "__main__":
    unittest.main()
