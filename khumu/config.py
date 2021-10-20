from configparser import ConfigParser
from os import path
import os
from pprint import pprint

import yaml

config_file_name = f'{path.join(path.dirname(path.realpath(__file__)), "..", "config")}/{os.getenv("KHUMU_ENVIRONMENT", "DEFAULT").lower()}.yaml'

with open(config_file_name, "r") as f:
    CONFIG = yaml.load(f, yaml.SafeLoader)

def load_database_config():
    database_config = CONFIG.get("database")
    return {"default": database_config}