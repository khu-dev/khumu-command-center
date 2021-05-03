from configparser import ConfigParser
from os import path
import os
from pprint import pprint

import yaml

config_file_name = f'{path.join(path.dirname(path.realpath(__file__)), "..", "config")}/{os.getenv("KHUMU_ENVIRONMENT", "DEFAULT").lower()}.yaml'
CONFIG = dict()
with open(config_file_name, "r") as f:
    CONFIG = yaml.load(f, yaml.SafeLoader)

def load_database_config():
    database_config = CONFIG.get("database")
    c = dict()
    if database_config.get("engine"): c["ENGINE"] = database_config.get("engine")
    if database_config.get("name"): c["NAME"] = database_config.get("name")
    if database_config.get("user"): c["USER"] = database_config.get("user")
    if database_config.get("username"): c["USERNAME"] = database_config.get("username")
    if database_config.get("password"): c["PASSWORD"] = database_config.get("password")
    if database_config.get("host"): c["HOST"] = database_config.get("host")
    if database_config.get("port"): c["PORT"] = int(database_config.get("port"))

    return {"default":c}
