import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import config

class TestConfig(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment by resetting the module-level _config variable
        and initializing a fake JSON string for testing purposes.
        """
        config._config = None
        self.fake_json = '{"param1": "value1", "param2": 123, "param3": true}'

    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data='{"test_key": "test_value"}')
    def test_init_config_reads_file(self, mock_open, mock_isfile):
        """
        Test that the _init_config function reads the configuration file correctly
        and initializes the _config variable with the file's contents.
        """
        config._config = None
        with patch("config._get_default_path", return_value="config.json"):
            config._init_config()
            self.assertEqual(config._config["test_key"], "test_value")

    @patch("os.path.isfile", return_value=False)
    def test_init_config_handles_missing_file(self, mock_isfile):
        """
        Test that the _init_config function handles the case where the configuration
        file is missing by initializing the _config variable as an empty dictionary.
        """
        config._config = None
        with patch("config._get_default_path", return_value=None):
            config._init_config()
            self.assertEqual(config._config, {})

    @patch.dict(os.environ, {"MY_PARAM": "json:123"}, clear=True)
    def test_get_parameter_from_env(self):
        """
        Test that the get_parameter function retrieves the value of a parameter
        from the environment variables, converting it to the appropriate type.
        """
        config._config = {"MY_PARAM": "should_not_use"}
        self.assertEqual(config.get_parameter("MY_PARAM"), 123)

    def test_get_parameter_from_config(self):
        """
        Test that the get_parameter function retrieves the value of a parameter
        from the _config dictionary when it is not found in the environment variables.
        """
        config._config = {"FOO": "bar"}
        self.assertEqual(config.get_parameter("FOO"), "bar")

    def test_get_parameter_missing_with_default(self):
        """
        Test that the get_parameter function returns the default value when the
        requested parameter is missing from both the environment variables and _config.
        """
        config._config = {}
        self.assertEqual(config.get_parameter("missing", default="fallback"), "fallback")

    def test_convert_to_typed_value(self):
        """
        Test that the convert_to_typed_value function correctly converts string
        representations of values to their appropriate types (e.g., int, bool).
        """
        self.assertEqual(config.convert_to_typed_value("123"), 123)
        self.assertEqual(config.convert_to_typed_value("true"), True)
        self.assertEqual(config.convert_to_typed_value("not_json"), "not_json")
        self.assertEqual(config.convert_to_typed_value(None), None)

    def test_set_parameter_with_string(self):
        """
        Test that the set_parameter function correctly sets a string value
        in the environment variables.
        """
        config.set_parameter("SET_PARAM", "plain")
        self.assertEqual(os.environ["SET_PARAM"], "plain")

    def test_set_parameter_with_object(self):
        """
        Test that the set_parameter function correctly sets an object value
        as a JSON string in the environment variables.
        """
        config.set_parameter("SET_JSON", {"x": 1})
        self.assertTrue(os.environ["SET_JSON"].startswith("json:"))

    def test_overwrite_from_args_with_items(self):
        """
        Test that the overwrite_from_args function correctly overwrites parameters
        using the items() method of the provided arguments object.
        """
        args = MagicMock()
        args.items.return_value = [("paramX", 42)]
        with patch.object(config, "set_parameter") as mock_set: 
            config.overwrite_from_args(args)
            mock_set.assert_called_with("paramX", 42)

    def test_overwrite_from_args_with_iteritems(self):
        """
        Test that the overwrite_from_args function correctly overwrites parameters
        using the iteritems() method of the provided arguments object.
        """
        args = MagicMock()
        args.iteritems.return_value = [("paramX", 42)]
        with patch.object(config, "set_parameter") as mock_set:
            config.overwrite_from_args(args)
            mock_set.assert_called_with("paramX", 42)

    @patch("os.getcwd")
    @patch("os.path.isfile")
    def test_get_default_path_finds_file(self, mock_isfile, mock_getcwd):
        """
        Test that the _get_default_path function correctly identifies the path
        to the configuration file by checking multiple directory levels.
        """
        mock_getcwd.return_value = "/tmp/a/b/c"
        mock_isfile.side_effect = [False, False, True]
        with patch("os.path.abspath", side_effect=lambda x: x):
            path = config._get_default_path()
            self.assertTrue(path.endswith("config.json"))

