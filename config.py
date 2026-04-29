import logging
logger = logging.getLogger(__name__)

import json
import os

_config = None


def _init_config(path=None):
    global _config
    if _config is not None:
        return

    filepath = _get_default_path()
    if filepath is None:
        logger.info('Initializing empty config')
        _config = {}
    else:
        try:
            with open(filepath, 'r') as fin:
                _config = json.loads(fin.read())
        except Exception:
            logger.info('Failed to load config file, using empty config')
            _config = {}


def _get_default_path():
    basepath = os.getcwd()
    filename = "config.json"
    prev_path = None

    while (basepath != prev_path) and not os.path.isfile(os.path.abspath(os.path.join(basepath, filename))):
        prev_path = basepath
        basepath = os.path.abspath(os.path.join(basepath, '..'))

    if basepath == prev_path:
        logger.info("Could not find config file.")
        return None
    else:
        config_path = os.path.abspath(os.path.join(basepath, filename))
        logger.info(f"Loading config from {config_path}")
        return config_path


def get_parameter(parameter_name, default=None):
    _init_config()

    if parameter_name in os.environ:
        value = os.environ.get(parameter_name)
        if isinstance(value, str) and value.startswith("json:"):
            value = value[5:]
        return convert_to_typed_value(value)

    if parameter_name not in _config:
        if default is not None:
            return default
        logger.info(f"Config parameter {parameter_name} is not specified")
        return None
    else:
        return _config[parameter_name]


def convert_to_typed_value(value):
    if value is None:
        return value

    try:
        if isinstance(value, str):
            return json.loads(value)
        else:
            return value
    except Exception:
        return value


def set_parameter(name, value):
    _init_config()
    if isinstance(value, str):
        os.environ[name] = value
    else:
        os.environ[name] = "json:{0}".format(json.dumps(value))


def overwrite_from_args(args):
    for name, value in vars(args).items():
        if value is not None:
            set_parameter(name, value)