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

####################
# RECORDED_DIR
# put a directory path for recorded files

# RECORDED_DIR = ''

####################
# GUIDE_DATABASE_URL
# put an URL for SQLAlchemy

db_path = pathlib.Path.home().joinpath(pathlib.PurePath('.config/aircheq/db/guide.db'))
GUIDE_DATABASE_URL = 'sqlite:///' + str(db_path)

####################
# NHK_API_AREA
# put an area code as str, refer to http://api-portal.nhk.or.jp/doc-request#explain_area

NHK_API_AREA = str(130) # Tokyo

####################
# NHK_API_KEY 
# put here NHK API key as str

NHK_API_KEY = 'INPUT_YOUR_NHK_API_KEY_HERE' 
```

## Execution
```bash
    cd /path/to/project_root/
    python -m aircheq   # Start Operator
    python -m aircheq.web # Start Web Server
```
