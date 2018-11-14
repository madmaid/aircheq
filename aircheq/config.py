# fileencoding: utf-8

import os.path
import pathlib
import sys
import importlib.util
import importlib.machinery

SKEL = """
import pathlib

CONFIG_DIR = pathlib.Path.home().joinpath(pathlib.Path(".aircheq/"))

####################
# RECORDED_DIR
# put a directory path for recorded files

RECORDED_DIR = 'pathlib.Path.home().joinpath("recorded/')

####################
# GUIDE_DATABASE_URL
# put an URL for SQLAlchemy

db_path = pathlib.Path.home().joinpath(pathlib.PurePath('.config/aircheq/db/guide.db'))
GUIDE_DATABASE_URL = 'sqlite:///' + str(db_path)

####################
# Preference for log

LOG_DIR = CONFIG_DIR.joinpath("logs/")
RTMPDUMP_LOG_PATH = LOG_DIR.joinpath("rtmpdump.log")


####################
# Preference for Radiko

RADIKO_TOOLS_DIR = CONFIG_DIR.joinpath("utils/radiko/")
RADIKO_PLAYER_URL = "http://radiko.jp/apps/js/flash/myplayer-release.swf"
RADIKO_WEEKLY_FROM_CHANNEL_URL = "http://radiko.jp/v3/program/station/weekly/{station_id}.xml"
RADIKO_CHANNELS_FROM_AREA_URL = "http://radiko.jp/v3/station/list/{area_id}.xml"
####################
# NHK_API_AREA
# put an area code as str, refer to http://api-portal.nhk.or.jp/doc-request#explain_area

# NHK_API_AREA = str(130) 

####################
# NHK_API_KEY 
# put NHK API key as str here 

# NHK_API_KEY = 'PUT_NHK_API_KEY_AS_STR_HERE'
"""

CONFIG_DIR = pathlib.Path.home().joinpath(pathlib.Path(".aircheq/"))

def make_unexist_dir(path_obj):
    if not path_obj.exists():
        path_obj.mkdir()

def make_config_skel(path):
    with path.open(mode='w') as conf:
        conf.write(SKEL)
    return

def make_default_config_dir(config_dir):
    db_dir = config_dir.joinpath(pathlib.Path('db/'))
    logs_dir = config_dir.joinpath(pathlib.Path('logs/'))
    utils_dir = config_dir.joinpath(pathlib.Path('utils/'))
    radiko_tools_dir = utils_dir.joinpath(pathlib.Path('radiko/'))

    dirs = [ config_dir, db_dir, utils_dir, logs_dir, radiko_tools_dir ]

    for d in dirs:
        make_unexist_dir(d)

    skel_path = config_dir.joinpath(pathlib.Path('config.py.skel'))
    make_config_skel(skel_path)

# mkdir 
make_default_config_dir(CONFIG_DIR)

class ConfigLoader(object):
    def __init__(self, module):
        self.module = module

    def __getattr__(self, name):
        try:
            return getattr(self.module, name)
        except AttributeError:
            loader = importlib.machinery.SourceFileLoader('user_config', os.path.join(CONFIG_DIR, "config.py"))
            user_config = loader.load_module()
            return getattr(user_config, name)

sys.modules[__name__] = ConfigLoader(sys.modules[__name__])
