import unittest
from unittest.mock import MagicMock, patch
import math
import tkinter as tk
import matplotlib
matplotlib.use("Agg")
from utils.data_extractors import (
    parse_time_to_minutes,
    bucket_values,
    extract_label_counts,
    extract_author_counts,
    UNIT_MAP,
)
from gui.flexible_bucket_gui import BucketRow, FlexibleXUnitApp
from utils.plot_utils import gui_bar_chart

class TestResolutionApp(unittest.TestCase):
    def setUp(self):
        self.parent = MagicMock()
        self.app = MagicMock()
        self.row = BucketRow(self.parent, self.app, 0)

        # Properly mock Entry and Combobox get()
        self.row.start_val.get = MagicMock(return_value="5")
        self.row.start_unit.get = MagicMock(return_value="minutes")
        self.row.end_val.get = MagicMock(return_value="10")
        self.row.end_unit.get = MagicMock(return_value="minutes")

    def test_parse_minutes(self):
        self.assertEqual(parse_time_to_minutes("5 minutes"), 5)

    def test_parse_hours(self):
        self.assertEqual(parse_time_to_minutes("2 hours"), 120)

    def test_parse_days(self):
        self.assertEqual(parse_time_to_minutes("1 day"), 1440)

    def test_parse_invalid(self):
        self.assertEqual(parse_time_to_minutes("abcd"), 0)

    def test_bucket_regular(self):
        values = [5, 30, 100]
        ranges = [(0, 10), (20, 50), (90, 150)]
        self.assertEqual(bucket_values(values, ranges), [1, 1, 1])

    def test_bucket_empty(self):
        self.assertEqual(bucket_values([], [(0, 10)]), [0])

    def test_get_range_normal(self):
        result, label = self.row.get_range()
        self.assertEqual(result, (5, 10))
        self.assertEqual(label, "5 minutes - 10 minutes")

    def test_get_range_infinite(self):
        self.row.end_val.get = MagicMock(return_value="")
        self.row.end_unit.get = MagicMock(return_value="+")

        result, label = self.row.get_range()
        self.assertEqual(result, (5, float('inf')))
        self.assertIn('+', label)

    def test_get_range_invalid_start_value(self):
        self.row.start_val.get = MagicMock(return_value="abc")

        with self.assertRaises(ValueError):
            self.row.get_range()

    @patch('tkinter.Tk')
    @patch('matplotlib.backends.backend_tkagg.FigureCanvasTkAgg')
    @patch('matplotlib.pyplot')
    def test_add_and_update(self, mock_plt, mock_canvas, mock_tk):
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        root = mock_tk()
        # app = FlexibleXUnitApp(root)
        issues = [{"id": 1, "resolution_time": 5}, {"id": 2, "resolution_time": 10}]  # Mock issues
        app = FlexibleXUnitApp(root, issues)


        initial = len(app.bucket_rows)
        app.add_bucket_row("0", "minutes", "10", "minutes")
        self.assertEqual(len(app.bucket_rows), initial + 1)

        app.update_plot()

    @patch('tkinter.Tk')
    @patch('matplotlib.backends.backend_tkagg.FigureCanvasTkAgg')
    @patch('matplotlib.pyplot')
    def test_update_with_invalid_bucket(self, mock_plt, mock_canvas, mock_tk):
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        root = mock_tk()
        # app = FlexibleXUnitApp(root)
        issues = [{"id": 1, "resolution_time": 5}, {"id": 2, "resolution_time": 10}]  # Mock issues
        app = FlexibleXUnitApp(root, issues)


        # Make first bucket invalid
        first_bucket = app.bucket_rows[0]
        first_bucket.start_val.get = MagicMock(return_value="abc")
        first_bucket.start_unit.get = MagicMock(return_value="minutes")
        first_bucket.end_val.get = MagicMock(return_value="10")
        first_bucket.end_unit.get = MagicMock(return_value="minutes")

        with patch('tkinter.messagebox.showerror') as mock_error:
            app.update_plot()
            mock_error.assert_called()

    def test_parse_time_to_minutes_no_match(self):
        self.assertEqual(parse_time_to_minutes("not a time"), 0)

    @patch('tkinter.Tk')
    @patch('matplotlib.backends.backend_tkagg.FigureCanvasTkAgg')
    @patch('matplotlib.pyplot')
    def test_update_plot_empty_bucket(self, mock_plt, mock_canvas, mock_tk):
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        root = mock_tk()
        # app = FlexibleXUnitApp(root)
        issues = [{"id": 1, "resolution_time": 5}, {"id": 2, "resolution_time": 10}]  # Mock issues
        app = FlexibleXUnitApp(root, issues)

        app.bucket_rows.clear()  # remove all buckets

        try:
            app.update_plot()
            worked = True
        except Exception:
            worked = False
        self.assertTrue(worked)

    @patch('tkinter.Tk')
    @patch('matplotlib.backends.backend_tkagg.FigureCanvasTkAgg')
    @patch('matplotlib.pyplot')
    def test_update_plot_with_exception(self, mock_plt, mock_canvas, mock_tk):
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        root = mock_tk()
        # app = FlexibleXUnitApp(root)
        issues = [{"id": 1, "resolution_time": 5}, {"id": 2, "resolution_time": 10}]  # Mock issues
        app = FlexibleXUnitApp(root, issues)


        app.bucket_rows[0].start_val.get = MagicMock(side_effect=Exception("mock error"))

        with patch('tkinter.messagebox.showerror') as mock_error:
            app.update_plot()
            mock_error.assert_called()

    @patch('tkinter.Tk')
    @patch('matplotlib.backends.backend_tkagg.FigureCanvasTkAgg')
    @patch('matplotlib.pyplot')
    def test_bucketrow_delete(self, mock_plt, mock_canvas, mock_tk):
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        root = mock_tk()
        # app = FlexibleXUnitApp(root)
        issues = [{"id": 1, "resolution_time": 5}, {"id": 2, "resolution_time": 10}]  # Mock issues
        app = FlexibleXUnitApp(root, issues)


        original_count = len(app.bucket_rows)
        first_bucket = app.bucket_rows[0]
        first_bucket.delete()

        self.assertEqual(len(app.bucket_rows), original_count - 1)

class TestDataExtractors(unittest.TestCase):
    def test_extract_label_counts(self):
        issues = [{"labels": ["kind/bug", "kind/feature", "other"]}]
        result = extract_label_counts(issues)
        self.assertEqual(result["kind/bug"], 1)
        self.assertEqual(result["kind/feature"], 1)
        self.assertNotIn("other", result)

    def test_extract_author_counts(self):
        issues = [
            {"events": [{"author": "alice"}, {"author": "bob"}, {"author": "alice"}]},
            {"events": [{"author": "bob"}]},
        ]
        result = extract_author_counts(issues)
        self.assertEqual(result["alice"], 2)
        self.assertEqual(result["bob"], 2)

class TestPlotUtils(unittest.TestCase):

    @patch("utils.plot_utils.FigureCanvasTkAgg")
    def test_gui_bar_chart(self, mock_canvas_class):
        mock_canvas_instance = mock_canvas_class.return_value
        mock_canvas_instance.get_tk_widget.return_value = MagicMock()

        root = tk.Tk()
        root.withdraw()  # Prevent actual GUI from showing

        labels = ["Fast", "Slow"]
        counts = [2, 3]
        fig, ax, canvas = gui_bar_chart(root, labels, counts, "X", "Y", "Title")

        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        self.assertTrue(mock_canvas_class.called)
        root.destroy()

if __name__ == "__main__":
    unittest.main()