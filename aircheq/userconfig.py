import os
import pathlib
import shutil
import logging 

from collections import defaultdict

import toml

logger = logging.getLogger(__name__)

CONFIG_DIR = pathlib.Path.home().joinpath(pathlib.Path(".aircheq/"))
CONFIG_PATH = CONFIG_DIR.joinpath("config.toml")
LOG_DIR = CONFIG_DIR.joinpath("logs/")

def make_config_skel(path):
    skelpath = pathlib.Path(__file__).parent.joinpath("../config.toml.skel")
    dst = path.parent.joinpath("config.toml")
    if not dst.exists():
        shutil.copy(skelpath, dst)

def make_default_config_dir(config_dir):
    db_dir = config_dir.joinpath(pathlib.Path('db/'))
    logs_dir = config_dir.joinpath(pathlib.Path('logs/'))
    utils_dir = config_dir.joinpath(pathlib.Path('utils/'))
    radiko_tools_dir = utils_dir.joinpath(pathlib.Path('radiko/'))

    dirs = ( config_dir, db_dir, utils_dir, logs_dir, radiko_tools_dir )

    # find then mkdir
    for d in dirs:
        if not d.exists():
            d.mkdir()

    skel_path = config_dir.joinpath("config.toml.skel")
    make_config_skel(skel_path)

class LoadingConfigFailedError(Exception):
    pass


class TomlLoader:
    def __init__(self, config_path=None, config=None):
        self.config_path = config_path or CONFIG_PATH
        self.config = config

    def __getitem__(self, key):
        if self.config is None:
            try:
                self.config = toml.load(self.config_path)

            except FileNotFoundError as e:
                logger.fatal("Config file not found")
                raise LoadingConfigFailedError()

            except toml.TomlDecodeError as e:
                logger.fatal("Invalid config")
                raise LoadingConfigFailedError()

        return self.__dict_to_defaultdict(self.config).get(key, None)

    def __dict_to_defaultdict(self, d):
        return d if not isinstance(d, dict) else defaultdict(lambda: None,
                { k: self.__dict_to_defaultdict(v) for k, v in d.items() })

def get_db_url():
    config = TomlLoader()

    db_dialect = config["db"]["guide_dialect"]
    db_path = pathlib.Path(config["db"]["guide_path"]).expanduser().absolute()

    db_url = db_dialect + ":///" + str(db_path)
    return db_url
