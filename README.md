# aircheq
Recorder for Japanese streaming radio service

## Dependencies
* Python >= 3.6
* Node v8
* Webpack (as a global package)
* RTMPDump (as a global package)
* swfextract (as a global package)

* NHK API KEY

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
RADIKO_CHANNELS_FROM_AREA_URL = "http://radiko.jp/v3/station/list/{area_id}.xml"
RADIKO_STREAM_XML_URL = "http://radiko.jp/v2/station/stream/{station_id}.xml"


####################
# Preference for AGQR 

AGQR_GUIDE_URL = "http://agqr.jp/timetable/streaming.html"
AGQR_STREAM_URL = "rtmp://fms-base2.mitene.ad.jp/agqr/aandg22"

####################
# Preference for NHK

# NHK_API_AREA
# put an area code as str, refer to http://api-portal.nhk.or.jp/doc-request#explain_area

# NHK_API_AREA = str(130) 

# NHK_API_KEY 
# put NHK API key as str here 

# NHK_API_KEY = 'PUT_NHK_API_KEY_AS_STR_HERE'

NHK_API_URL = "https://api.nhk.or.jp/v2/pg/list/{area}/{service}/{date}.json?key={apikey}"
NHK_STREAM_URLS_API= "http://www.nhk.or.jp/radio/config/config_web.xml"
"""
```

## Execution
```bash
    cd /path/to/project_root/
    python -m aircheq   # Start Operator
    python -m aircheq.web # Start Web Server
```
