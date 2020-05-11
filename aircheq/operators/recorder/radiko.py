#! /usr/bin/python
# -*- coding: utf-8 -*-

import urllib.parse
from logging import getLogger

import lxml.etree
import requests

from ... import config
from .. import auth
from . import base

logger = getLogger("aircheq-recorder")
class Recorder(base.Recorder):
    PLAYER_URL = config.RADIKO_PLAYER_URL 
    FILEEXT = ".flv"
    def __init__(self, program):
        super().__init__(program)
        self.auth = auth.RadikoAuth(logger=logger)
        self.authtoken = self.auth.get_authtoken()

        ch_xml_url = config.RADIKO_STREAM_XML_URL.format(station_id=program.channel)

        logger.info("try to fetch stream url")
        RETRY_MAX = 5
        for count in range(RETRY_MAX):
            try:
                channel_xml = requests.get(ch_xml_url)
                stream_url_full = lxml.etree.fromstring(channel_xml.content).xpath('//url/item/text()')[0]
            except Exception as err:
                logger.error(err)
                if count == RETRY_MAX - 1:
                    raise err
            else:
                break
            logger.info("retry to fetch stream url")


        parsed_url = urllib.parse.urlparse(stream_url_full)
        url_parts = parsed_url.path.strip('/').split('/')

        self.stream_url = parsed_url.scheme + '://' + parsed_url.netloc
        self.app = url_parts[0] + '/' + url_parts[1]
        self.playpath = url_parts[2]

        self.command = (
            'rtmpdump -r {stream_url} --app {app} --playpath {playpath} -W' + ' ' +
            '{player_url} -C S:"" -C S:"" -C S:"" -C S:{authtoken}' + ' ' +
            '--stop {duration} --live -o {output}'
             ).format_map({
                "stream_url": self.stream_url,
                "app": self.app,
                "playpath": self.playpath,
                "player_url": self.PLAYER_URL,
                "authtoken": self.authtoken,
                "duration": self.duration_from_now(),
                "output": str(self.get_save_path(self.program.start)) + self.FILEEXT
            }).split(" ")
