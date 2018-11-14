# aircheq
Recorder for Japanese streaming radio service

## Dependencies
* Python >= 3.6
* Node v8
* Webpack (as a global package)
* RTMPDump (as a global package)
* swfextract (as a global package)

## Installation
    pip install -rrequirements.txt
    cd aircheq/web/aircheq_wui/
    npm install
    webpack

## Configuration
    $EDITOR ~/.aircheq/config.py
```python

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
RADIKO_STATIONS_FROM_AREA_URL = "http://radiko.jp/v3/station/list/{area_id}.xml"
####################
# NHK_API_AREA
# put an area code as str, refer to http://api-portal.nhk.or.jp/doc-request#explain_area

# NHK_API_AREA = str(130) 

####################
# NHK_API_KEY 
# put NHK API key as str here 

# NHK_API_KEY = 'PUT_NHK_API_KEY_AS_STR_HERE'
"""
```

## Execution
```bash
    cd /path/to/project_root/
    python -m aircheq   # Start Operator
    python -m aircheq.web # Start Web Server
```
