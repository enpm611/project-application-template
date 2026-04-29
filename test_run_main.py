import unittest
from unittest.mock import patch


class TestRunMain(unittest.TestCase):

    @patch("sys.argv", ["run.py", "--feature", "1"])
    def test_run_feature_1(self):
        from run import main
        main()  # just verify it runs

    @patch("sys.argv", ["run.py", "--feature", "2"])
    def test_run_feature_2(self):
        from run import main
        main()

    @patch("sys.argv", ["run.py", "--feature", "3"])
    def test_run_feature_3(self):
        from run import main
        main()