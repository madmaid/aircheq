#! /usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import urllib.parse
import logging
import lxml.etree
import requests

from ... import userconfig
from .. import auth
from . import base

logger = logging.getLogger(__name__)
config = userconfig.TomlLoader()
class Recorder(base.Recorder):
    PLAYER_URL = config["radiko"]["player_url"]
    def __init__(self, program):
        super().__init__(program)

        plurl = config["radiko"]["playlist_url"]
        xml_plurl = config["radiko"]["stream_xml_url"]

        if plurl is None and xml_plurl is None:
            logger.error("No Radiko stream url found")
            return

        if plurl is not None:
            # HLS
            self.auth = auth.RadikoHLSAuth()
            self.authtoken = self.auth.authtoken

            self._init_hls(plurl, program)

        else:
            # RTMP
            self.auth = auth.RadikoRTMPAuth()
            self.authtoken = self.auth.get_authtoken()

            self._init_rtmp(xml_plurl.format_map({
                "station_id": program.channel
            }))

    def _get_stream_url_with_retry(self, playlist_url, extractor, headers=dict()):
        logger.debug("try to fetch stream url")
        RETRY_MAX = 5
        for count in range(RETRY_MAX):
            try:
                res = requests.get(playlist_url, headers=headers)
                return extractor(res)
            except Exception as err:
                logger.error(err)
            logger.warning(f"retry to fetch stream url (count: {count})")
        logger.error("reached max times to retry")
        raise err


    def _init_rtmp(self, playlist_url):
        EXT = ".flv"

        extractor = lambda res: lxml.etree.fromstring(res.content).xpath('//url/item/text()')[0]
        stream_url_full = self._get_stream_url_with_retry(playlist_url, extractor)

        parsed_url = urllib.parse.urlparse(stream_url_full)
        url_parts = parsed_url.path.strip('/').split('/')

        self.stream_url = parsed_url.scheme + '://' + parsed_url.netloc
        self.app = url_parts[0] + '/' + url_parts[1]
        self.playpath = url_parts[2]



        cmd = ('rtmpdump -r {stream_url} --app {app} --playpath {playpath} -W' + ' ' +
            '{player_url} -C S:"" -C S:"" -C S:"" -C S:{authtoken}' + ' ' +
            '--stop {duration} --live -o {output}')

        self.command = cmd.format_map({
                "stream_url": self.stream_url,
                "app": self.app,
                "playpath": self.playpath,
                "player_url": self.PLAYER_URL,
                "authtoken": self.authtoken,
                "duration": self.duration_from_now(),
                "output": str(self.get_save_path(self.program.start)) + EXT
            }).split(" ")



    def _init_hls(self, playlist_url, program):
        EXT = ".aac"
        headers = {
                "X-Radiko-Authtoken": self.authtoken
        }
        _plurl = playlist_url.format_map({
                    "station_id": program.channel,
                    "start": program.start,
                    "end": program.end,
        })
        extractor = lambda res: [s for s in res.content.decode().splitlines() if s.endswith(".m3u8")][0]
        url = self._get_stream_url_with_retry(_plurl, extractor, headers)

        cmd = ("ffmpeg -headers 'X-Radiko-Authtoken:{authtoken}' -i {stream_url}" +
                " " + "-t {duration} -acodec copy {output}")

        self.command = cmd.format_map({
            "stream_url": url,
            "duration": self.duration_from_now(),
            "output": str(self.get_save_path(self.program.start)) + EXT,
            "authtoken": self.authtoken,
        }).split(" ")

    def _init_timefree(self, playlist_url, program):
        EXT = ".aac"
        headers = {
                "X-Radiko-Authtoken": self.authtoken
        }
        _plurl = playlist_url.format_map({
                    "station_id": program.channel,
                    "start": program.start,
                    "end": program.end,
        })
        extractor = lambda res: [s for s in res.content.decode().splitlines() if s.endswith(".m3u8")][0]
        url = self._get_stream_url_with_retry(_plurl, extractor, headers)

        cmd = ("ffmpeg -headers 'X-Radiko-Authtoken:{authtoken}' -i {stream_url}" + 
                " " + "-acodec copy {output}")

        self.command = cmd.format_map({
            "stream_url": url,
            "output": str(self.get_save_path(self.program.start)) + EXT,
            "authtoken": self.authtoken,
        }).split(" ")
