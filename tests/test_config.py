import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import config

class TestConfig(unittest.TestCase):

    def setUp(self):
        # Reset config state and prepare sample JSON
        config._config = None
        self.fake_json = '{"param1": "value1", "param2": 123, "param3": true}'

    # Ensure configuration is loaded from a valid JSON file
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data='{"test_key": "test_value"}')
    def test_init_config_reads_file(self, mock_open, mock_isfile):
        with patch("config._get_default_path", return_value="config.json"):
            config._init_config()
            self.assertEqual(config._config["test_key"], "test_value")

    # Handle missing configuration file by falling back to empty config
    @patch("os.path.isfile", return_value=False)
    def test_init_config_handles_missing_file(self, mock_isfile):
        with patch("config._get_default_path", return_value=None):
            config._init_config()
            self.assertEqual(config._config, {})

    # Read parameter from environment and cast to type using "json:" syntax
    @patch.dict(os.environ, {"MY_PARAM": "json:123"}, clear=True)
    def test_get_parameter_from_env(self):
        config._config = {"MY_PARAM": "should_not_use"}
        self.assertEqual(config.get_parameter("MY_PARAM"), 123)

    # Fallback to _config dictionary if parameter is not in environment
    def test_get_parameter_from_config(self):
        config._config = {"FOO": "bar"}
        self.assertEqual(config.get_parameter("FOO"), "bar")

    # Return default if parameter is not in either _config or environment
    def test_get_parameter_missing_with_default(self):
        config._config = {}
        self.assertEqual(config.get_parameter("missing", default="fallback"), "fallback")

    # Validate conversion of strings into appropriate types
    def test_convert_to_typed_value(self):
        self.assertEqual(config.convert_to_typed_value("123"), 123)
        self.assertEqual(config.convert_to_typed_value("true"), True)
        self.assertEqual(config.convert_to_typed_value("not_json"), "not_json")
        self.assertEqual(config.convert_to_typed_value(None), None)

    # Set string value directly to environment
    def test_set_parameter_with_string(self):
        config.set_parameter("SET_PARAM", "plain")
        self.assertEqual(os.environ["SET_PARAM"], "plain")

    # Serialize complex object to JSON and prefix with "json:" when setting
    def test_set_parameter_with_object(self):
        config.set_parameter("SET_JSON", {"x": 1})
        self.assertTrue(os.environ["SET_JSON"].startswith("json:"))

    # Use items() method from argparse.Namespace to override parameters
    def test_overwrite_from_args_with_items(self):
        args = MagicMock()
        args.items.return_value = [("paramX", 42)]
        with patch.object(config, "set_parameter") as mock_set: 
            config.overwrite_from_args(args)
            mock_set.assert_called_with("paramX", 42)

    # Use iteritems() method if items() is not available on args
    def test_overwrite_from_args_with_iteritems(self):
        args = MagicMock()
        args.iteritems.return_value = [("paramX", 42)]
        with patch.object(config, "set_parameter") as mock_set:
            config.overwrite_from_args(args)
            mock_set.assert_called_with("paramX", 42)

    # Locate config.json by walking up the directory tree
    @patch("os.getcwd")
    @patch("os.path.isfile")
    def test_get_default_path_finds_file(self, mock_isfile, mock_getcwd):
        mock_getcwd.return_value = "/tmp/a/b/c"
        mock_isfile.side_effect = [False, False, True]
        with patch("os.path.abspath", side_effect=lambda x: x):
            path = config._get_default_path()
            self.assertTrue(path.endswith("config.json"))

