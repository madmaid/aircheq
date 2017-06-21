#! /usr/bin/python
# -*- coding: utf-8 -*-
import requests
import os
import pathlib
import subprocess
import base64
import logging

from .. import config
from . import utils


class RadikoAuth(object):
    HTTP_ERR_MSG = '''
        failed getting auth2_fms, check that your internet connection is available
        '''
    PLAYER_URL = "http://radiko.jp/apps/js/flash/myplayer-release.swf"
    AUTH1_URL = "https://radiko.jp/v2/api/auth1_fms"
    AUTH2_URL = "https://radiko.jp/v2/api/auth2_fms"

    def __init__(self, logger=logging.getLogger()):
        self.logger = logger
        self.PLAYER_PATH = os.path.join(config.RADIKO_TOOLS_DIR, 'player')
        self.KEY_PATH = os.path.join(config.RADIKO_TOOLS_DIR, 'key')

        self.headers = {
                'pragma': 'no-cache',
                'X-Radiko-App': 'pc_ts',
                'X-Radiko-App-Version': '4.0.0',
                'X-Radiko-User': 'test-stream',
                'X-Radiko-Device': 'pc'
                }

    def gen_partialkey(self, offset, keylength):
        try:
            should_get_key = ( not os.path.exists(self.KEY_PATH) 
                            or os.path.getsize(self.KEY_PATH == 0))
        except:
            raise
                
        if should_get_key:
            self.get_key()


        with open(self.KEY_PATH, 'rb') as key:
            key.seek(offset)
            partial_key = base64.b64encode(key.read(keylength))
        return partial_key

    def auth_fms(self):
        auth1_fms = requests.post(self.AUTH1_URL, headers=self.headers, cookies=dict())
        try:
            auth1_fms.raise_for_status()
        except requests.HTTPError as e:
            self.logger.error(self.HTTP_ERR_MSG)
            raise e

        OFFSET = int(auth1_fms.headers['x-radiko-keyoffset'])
        KEYLENGTH = int(auth1_fms.headers['x-radiko-keylength'])
        partialkey = self.gen_partialkey(OFFSET, KEYLENGTH)

        auth2_headers = self.headers.copy()
        auth2_headers.update({
                'X-Radiko-AuthToken': auth1_fms.headers['x-radiko-authtoken'],
                'X-Radiko-PartialKey': partialkey
                })
        self.authtoken = auth1_fms.headers['x-radiko-authtoken']

        auth2_fms = requests.post(self.AUTH2_URL, headers=auth2_headers, cookies=dict())
        try:
            auth2_fms.raise_for_status()
        except requests.HTTPError as e:
            self.logger.error(self.HTTP_ERR_MSG)
            raise e

        content = auth2_fms.content.decode('utf-8')
        self.area = content.split(',')[0].replace("\r\n", "")

    def get_player(self):
        req = requests.get(self.PLAYER_URL)
        try:
            req.raise_for_status()
        except requests.HTTPError as e:
            self.logger.error(self.HTTP_ERR_MSG)

        with open(self.PLAYER_PATH, 'wb') as player:
            player.write(req.content)

    def get_key(self):
        if not os.path.exists(self.PLAYER_PATH):
            self.get_player()

        cmd = "swfextract -b 12 {PLAYER_PATH} -o {KEY_PATH}".format_map({
                "PLAYER_PATH": os.path.abspath(self.PLAYER_PATH),
                "KEY_PATH": self.KEY_PATH,
            }).split(" ")
        subprocess.run(cmd, check=True)

    def get_authtoken(self):
        if not os.path.exists(self.KEY_PATH):
            self.get_key()
        self.auth_fms()
        return self.authtoken

    def get_area(self):
        self.get_authtoken()
        return self.area
