# fileencoding: utf-8

import os.path
import pathlib
import sys
import importlib.util


def mkdir_unexists(path_obj):
    if not path_obj.exists():
        path_obj.mkdir()

def make_config_skel(path):
    skel = """
import pathlib

####################
# RECORDED_DIR
# put a directory path for recorded files

# RECORDED_DIR = ''

####################
# GUIDE_DATABASE_URL
# put an URL for SQLAlchemy

# db_path = pathlib.Path.home().joinpath(pathlib.PurePath('.config/aircheq/db/guide.db'))
# GUIDE_DATABASE_URL = 'sqlite:///' + str(db_path)

####################
# NHK_API_AREA
# put an area code as str, refer to http://api-portal.nhk.or.jp/doc-request#explain_area

# NHK_API_AREA = str(130) 

####################
# NHK_API_KEY 
# put here NHK API key as str

# NHK_API_KEY = '' 
"""
    with path.open(mode='w') as conf:
        conf.write(skel)
    return

def make_config_dir(config_dir):
    db_dir = config_dir.joinpath(pathlib.Path('db/'))
    logs_dir = config_dir.joinpath(pathlib.Path('logs/'))
    utils_dir = config_dir.joinpath(pathlib.Path('utils/'))
    radiko_tools_dir = utils_dir.joinpath(pathlib.Path('radiko/'))

    dirs = [ config_dir, db_dir, utils_dir, logs_dir, radiko_tools_dir ]

    for d in dirs:
        mkdir_unexists(d)

    skel_path = config_dir.joinpath(pathlib.Path('config.py.skel'))
    make_config_skel(skel_path)


class ConfigLoader(object):
    def __getattribute__(self, name):
        spec = importlib.util.spec_from_file_location('config', os.path.join(CONFIG_DIR, "config.py"))
        user_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_config)
        return getattr(user_config, name)

def load_userconfig(config_dir):
    spec = importlib.util.spec_from_file_location('config', os.path.join(config_dir, "config.py"))

    user_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(user_config)
    return user_config



CONFIG_DIR = pathlib.Path.home().joinpath(pathlib.Path(".aircheq/"))

make_config_dir(CONFIG_DIR)

# load user config
user_config = load_userconfig(CONFIG_DIR)

# Preference for log
LOG_DIR = CONFIG_DIR.joinpath('logs/')
RTMPDUMP_LOG_PATH = LOG_DIR.joinpath(pathlib.PurePosixPath('rtmpdump.log'))

# Preference for Recorded Files
SAVE_DIR = user_config.RECORDED_DIR

# preference for sqlalchemy DB
GUIDE_DATABASE_URL = user_config.GUIDE_DATABASE_URL

# Preference for Radiko
RADIKO_TOOLS_DIR = os.path.join(CONFIG_DIR, 'utils/radiko/')

# Preference for NHK
NHK_API_AREA = user_config.NHK_API_AREA
NHK_API_KEY = user_config.NHK_API_KEY
