import pathlib
import shutil
import logging
import typing
from abc import ABCMeta
from dataclasses import dataclass

from collections import defaultdict

import toml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_DIR = pathlib.Path.home().joinpath(pathlib.Path(".aircheq/"))
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR.joinpath("config.toml")
#  LOG_DIR = CONFIG_DIR.joinpath("logs/")


@dataclass
class AircheqDir:
    config_dir: pathlib.Path

    @property
    def config_path(self) -> pathlib.Path:
        return self.config_dir.joinpath("config.toml")

    @property
    def db_dir(self) -> pathlib.Path:
        return self.config_dir.joinpath('db/')

    @property
    def log_dir(self) -> pathlib.Path:
        return self.config_dir.joinpath('logs/')

    @property
    def utils_dir(self) -> pathlib.Path:
        return self.config_dir.joinpath('utils/')

    @property
    def radiko_tools_dir(self) -> pathlib.Path:
        return self.utils_dir.joinpath('radiko/')

    def make_default_config_dir(self):

        dirs = (
            self.config_dir,
            self.db_dir,
            self.utils_dir,
            self.logs_dir,
            self.radiko_tools_dir
        )

        # find then mkdir
        for d in dirs:
            if not d.exists():
                d.mkdir()

    def make_config_skel(self):
        skelpath = pathlib.Path(__file__).parent.joinpath(
            "../config.toml.skel")
        dst = self.config_dir.joinpath("config.toml")
        if not dst.exists():
            shutil.copy(skelpath, dst)


class LoadingConfigFailedError(Exception):
    pass




@dataclass
class ConfigLoader(metaclass=ABCMeta):
    config_pathes: AircheqDir
    config: typing.Optional[dict] = None

    def __new__(cls, *args, **kwargs):
        dataclass(cls)
        return super().__new__(cls)

    def __getitem__(self, key):
        return self._dict_to_defaultdict(self.config).get(key, None)

    def _dict_to_defaultdict(self, d):
        if not isinstance(d, dict):
            return d
        else:
            return defaultdict(lambda: None, {
                k: self._dict_to_defaultdict(v) for k, v in d.items()
            })


class GeneralConfig(typing.TypedDict):
    recorded_dir: str
    ffmpeg: str
    log_dir: str


class DbConfig(typing.TypedDict):
    guide_dialect: str
    guide_path: str


class RadikoConfig(typing.TypedDict):
    tools_dir: str
    playlist_url: str
    weekly_from_channel_url: str
    channels_from_area_url: str
    stream_xml_url: str
    auth1_url: str
    auth2_url: str
    auth_key: str


class AgqrConfig(typing.TypedDict):
    guide_url: str
    stream_url: str


class RadiruConfig(typing.TypedDict):
    area: int
    api_key: str
    api_url: str
    stream_xml_url: str


class UserConfig(typing.TypedDict):
    general: GeneralConfig
    db: DbConfig
    radiko: RadikoConfig
    agqr: AgqrConfig
    radiru: RadiruConfig


class TomlLoader(ConfigLoader):
    def __getitem__(self, key):
        if self.config is None:
            try:
                self.config = toml.load(self.config_pathes.config_path)

            except FileNotFoundError:
                logger.fatal("Config file not found")
                raise LoadingConfigFailedError()

            except toml.TomlDecodeError:
                logger.fatal("Invalid config")
                raise LoadingConfigFailedError()

        return self._dict_to_defaultdict(self.config).get(key, None)


def get_db_url(config: ConfigLoader) -> str:

    db_dialect = config["db"]["guide_dialect"]
    db_path = pathlib.Path(config["db"]["guide_path"]).expanduser().absolute()

    db_url = db_dialect + ":///" + str(db_path)
    return db_url
