import unittest
import os
import importlib
import config


class TestConfig(unittest.TestCase):

    def setUp(self):
        # Reset config module state before each test
        importlib.reload(config)

    def tearDown(self):
        # Clean up environment variables after each test
        keys_to_remove = [
            "TEST_PARAM",
            "TEST_JSON",
            "TEST_SET",
            "NON_EXISTENT",
            "DOES_NOT_EXIST"
        ]
        for key in keys_to_remove:
            if key in os.environ:
                del os.environ[key]

    

    def test_get_parameter_from_env_string(self):
        os.environ["TEST_PARAM"] = "123"
        result = config.get_parameter("TEST_PARAM")
        self.assertEqual(result, 123)

    def test_get_parameter_from_env_json_prefix(self):
        os.environ["TEST_JSON"] = "json:[1,2,3]"
        result = config.get_parameter("TEST_JSON")
        self.assertEqual(result, [1, 2, 3])

    def test_get_parameter_default_value(self):
        result = config.get_parameter("NON_EXISTENT", default="fallback")
        self.assertEqual(result, "fallback")

    def test_get_parameter_missing_no_default(self):
        result = config.get_parameter("DOES_NOT_EXIST")
        self.assertIsNone(result)

   
    # convert_to_typed_value tests
 

    def test_convert_valid_json(self):
        value = config.convert_to_typed_value("[1,2,3]")
        self.assertEqual(value, [1, 2, 3])

    def test_convert_invalid_json(self):
        value = config.convert_to_typed_value("not_json")
        self.assertEqual(value, "not_json")

    def test_convert_non_string(self):
        value = config.convert_to_typed_value(123)
        self.assertEqual(value, 123)

    def test_convert_none(self):
        value = config.convert_to_typed_value(None)
        self.assertIsNone(value)

    # set_parameter tests
    

    def test_set_parameter_string(self):
        config.set_parameter("TEST_SET", "hello")
        self.assertEqual(os.environ["TEST_SET"], "hello")

    def test_set_parameter_non_string(self):
        config.set_parameter("TEST_SET", [1, 2])
        self.assertTrue(os.environ["TEST_SET"].startswith("json:"))

  

    def test_overwrite_from_args(self):
        class Args:
            def __init__(self):
                self.param1 = "value1"
                self.param2 = None  # should be ignored

        args = Args()
        config.overwrite_from_args(args)

        self.assertEqual(os.environ.get("param1"), "value1")
        self.assertIsNone(os.environ.get("param2"))

  
   

    def test_init_config_no_file(self):
        # Force no config file found
        original = config._get_default_path
        config._get_default_path = lambda: None

        importlib.reload(config)
        result = config.get_parameter("ANY_PARAM")

        self.assertIsNone(result)

        
        config._get_default_path = original