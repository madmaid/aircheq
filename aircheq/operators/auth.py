#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import pathlib
import subprocess
import base64
import logging

import io

import requests

from .. import userconfig

logger = logging.getLogger(__name__)
HTTP_ERR_MSG = 'Failed getting Radiko authorization: {step}'


class RadikoAuth:
    def get_area(self):
        self.get_authtoken()
        return self.area


class RadikoRTMPAuth(RadikoAuth):
    AUTH1_URL = "https://radiko.jp/v2/api/auth1_fms"
    AUTH2_URL = "https://radiko.jp/v2/api/auth2_fms"

    def __init__(self, config):

        self.config = config
        self.player_url = self.config["radiko"]["player_url"]
        self.player_path = (
            pathlib.Path(self.config["radiko"]["tools_dir"])
            .joinpath('player').expanduser().absolute()
        )
        self.key_path = (
            pathlib.Path(self.config["radiko"]["tools_dir"])
            .joinpath('key').expanduser().absolute()
        )

        self.headers = {
            'pragma': 'no-cache',
            'X-Radiko-App': 'pc_ts',
            'X-Radiko-App-Version': '4.0.0',
            'X-Radiko-User': 'test-stream',
            'X-Radiko-Device': 'pc'
        }

    def gen_partialkey(self, offset, keylength):
        try:
            should_get_key = (not os.path.exists(self.key_path)
                              or os.path.getsize(self.key_path == 0))
        except:
            raise

        if should_get_key:
            self.get_key()

        with open(self.key_path, 'rb') as key:
            key.seek(offset)
            partial_key = base64.b64encode(key.read(keylength))
        return partial_key

    def auth_fms(self):
        auth1_fms = requests.post(
            self.AUTH1_URL, headers=self.headers, cookies=dict())
        try:
            auth1_fms.raise_for_status()
        except requests.HTTPError as e:
            logger.error(HTTP_ERR_MSG)
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

        auth2_fms = requests.post(
            self.AUTH2_URL, headers=auth2_headers, cookies=dict())
        try:
            auth2_fms.raise_for_status()
        except requests.HTTPError as e:
            logger.error(HTTP_ERR_MSG)
            raise e

        content = auth2_fms.content.decode('utf-8')
        self.area = content.split(',')[0].replace("\r\n", "")

    def get_player(self):
        req = requests.get(self.player_url)
        try:
            req.raise_for_status()
        except requests.HTTPError as e:
            logger.error(HTTP_ERR_MSG)

        with open(self.player_path, 'wb') as player:
            player.write(req.content)

    def get_key(self):
        if not os.path.exists(self.player_path):
            self.get_player()

        cmd = "swfextract -b 12 {player_path} -o {key_path}".format_map({
            "player_path": self.player_path,
            "key_path": self.key_path,
        }).split(" ")
        subprocess.run(cmd, check=True)

    def get_authtoken(self):
        if not os.path.exists(self.key_path):
            self.get_key()
        self.auth_fms()
        return self.authtoken


class RadikoHLSAuth(RadikoAuth):
    def __init__(self, config):
        self.config = config
        self.get_authtoken()

    def get_authtoken(self):
        auth1_url = self.config["radiko"]["auth1_url"]
        headers = {
            'X-Radiko-App': 'pc_html5',
            'X-Radiko-App-Version': '0.0.1',
            'X-Radiko-User': 'dummy_user',
            'X-Radiko-Device': 'pc'
        }
        auth1_res = requests.get(auth1_url, headers=headers)
        try:
            auth1_res.raise_for_status()
        except requests.HTTPError as e:
            logger.error(HTTP_ERR_MSG.format("auth1"))
            raise e

        offset = int(auth1_res.headers['X-Radiko-KeyOffset'])
        keylength = int(auth1_res.headers['X-Radiko-KeyLength'])
        authtoken = auth1_res.headers["X-Radiko-AuthToken"]

        authkey = io.StringIO(self.config["radiko"]["auth_key"])
        authkey.seek(offset)
        partial_key = base64.b64encode(authkey.read(keylength).encode("utf-8"))

        auth2_headers = headers
        auth2_headers.update({
            "X-Radiko-AuthToken": authtoken,
            "X-Radiko-PartialKey": partial_key,
        })

        auth2_url = self.config["radiko"]["auth2_url"]
        auth2_res = requests.get(auth2_url, headers=auth2_headers)

        try:
            auth2_res.raise_for_status()
        except requests.HTTPError as e:
            logger.error(HTTP_ERR_MSG.format("auth2"))
            raise e

        self.authtoken = authtoken
        self.area = auth2_res.text.split(',')[0]
