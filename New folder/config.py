import logging
logger = logging.getLogger(__name__)

import json
import os

'''
Handles the loading of the config file as well as the access of specific
config parameters.
'''

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
        with open(filepath, 'r') as fin:
            _config = json.loads(fin.read())


def _get_default_path():
    """
    Searches for the config file by traversing up the directory
    tree since the depth of the path is different between different
    operating systems.
    """
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
    """
    Main function to access config parameters.
    Preference is given to environment variables, and then to the config file.
    """
    _init_config()
    if parameter_name in os.environ:
        value = os.environ.get(parameter_name)
        if value.startswith("json:"):
            value = value[5:]
        return convert_to_typed_value(value)
    if parameter_name not in _config:
        if default:
            return default
        logger.info(f"Config parameter {parameter_name} is not specified")
        return None
    else:
        return _config[parameter_name]


def convert_to_typed_value(value):
    """
    Parses parameter values and converts them to their
    respective type. This is necessary as Helm Chart Secrets
    are always expressed as strings.
    """
    if value is None:
        return value

    try:
        if isinstance(value, str):
            return json.loads(value)
        else:
            # We only need to convert string values
            # Others are already in their target type
            return value
    except:
        # if the above doesn't work, it's a string
        return value


def set_parameter(name, value):
    """
    Sets a config parameter so that it can be accessed from anywhere
    in the application.
    """
    _init_config()
    if isinstance(value, str):
        os.environ[name] = value
    else:
        os.environ[name] = "json:{0}".format(json.dumps(value))


def overwrite_from_args(args):
    """
    Writes command line paramters into the config so any parameter
    can be accessed the same way through the config. It adds any parameters
    that are missing and overwrites parameters that already exist.
    """
    try:
        for name, value in vars(args).iteritems():
            if value is not None:
                set_parameter(name, value)
    except:
        pass

    try:
        for name, value in vars(args).items():
            if value is not None:
                set_parameter(name, value)
    except:
        pass
