import unittest
from unittest.mock import patch, mock_open
from data_loader import DataLoader


class TestDataLoader(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='[]')
    def test_load_empty(self, mock_file):
        data = DataLoader("fake.json").get_issues()
        self.assertEqual(data, [])

    @patch("builtins.open", new_callable=mock_open, read_data='[{"state": "open"}]')
    def test_load_valid(self, mock_file):
        data = DataLoader("fake.json").get_issues()
        self.assertEqual(len(data), 1)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_file_not_found(self, mock_file):
        data = DataLoader("missing.json").get_issues()
        self.assertEqual(data, [])

    @patch("builtins.open", new_callable=mock_open, read_data='invalid json')
    def test_invalid_json(self, mock_file):
        data = DataLoader("bad.json").get_issues()
        self.assertEqual(data, [])