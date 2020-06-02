# aircheq
Recorder for Japanese streaming radio service

## Dependencies

### Required
* Python >= 3.7
* poetry
* ffmpeg (as a global package)

* NHK API KEY (need to register)

### Optional 
* RTMPDump (as a global package)
* swfextract (as a global package)
* webpack (as a global package, to build WUI from source)

## Install
    cd /path/to/project_root/
    poetry install

## Run
```bash
    cd /path/to/project_root/
    poetry run python -m aircheq        # Start Operator
    poetry run python -m aircheq.web    # Start Web Server
```
you need to configure `~/.aircheq/config.toml`
also see the section configure.

## Configure

to run, you need to set NHK API key.
edit the configuration file
```bash
    $EDITOR ~/.aircheq/config.toml
```
```toml
[radiru]
area = YOUR_AREA_CODE_AS_A_NUMBER
# eg.
# area = 130

api_key = 'PUT_NHK_API_KEY_AS_STR_HERE'
```
you can also change a path where recorded saved
```toml
[general]
recorded_dir = "/path/to/your/recorded/directory"
```

## Migrate from config.py to config.toml
```bash
    cd /path/to/project_root/
    poetry run python -m aircheq.cli migrate-config ~/.aircheq/config.py  ~/.aircheq/config.toml
```

## (Optional) build WUI from source
    # install wui requirements 
    cd aircheq/web/aircheq_wui/
    npm install
    webpack
