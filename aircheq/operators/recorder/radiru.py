import urllib.parse
import lxml.etree
import requests

from . import base
from ... import config

class InvalidAreaKeyError(Exception):
    pass

class Recorder(base.Recorder):
    PLAYER_URL = "http://www3.nhk.or.jp/netradio/files/swf/rtmpe.swf"
    STREAM_URLS_API= "http://www3.nhk.or.jp/netradio/app/config_pc_2016.xml"
    def __init__(self, program):
        super().__init__(program)

        req = requests.get(self.STREAM_URLS_API)
        root = lxml.etree.fromstring(req.content)

        for areakey in root.xpath("//data/areakey"):
            if str(config.NHK_API_AREA) == areakey.text:
                url = areakey.xpath("../{}".format(program.channel))[0].text

                parsed_url = urllib.parse.urlsplit(url)

                self.stream_url = parsed_url.scheme + "://" + parsed_url.netloc
                self.app = 'live'
                self.playpath = parsed_url.path.replace("/live/", "")
                self.command = (
                    "rtmpdump -r {stream_url} -y {playpath} -a {app}" + " " +
                    "--swfVfy {player_url} --stop {duration} --live -o {output}"
                    ).format_map({
                        "stream_url": self.stream_url,
                        "playpath": self.playpath,
                        "app": self.app,
                        "player_url": self.PLAYER_URL,
                        "duration": self.duration,
                        'output': self.save_path,
                    }).split(" ")

                return
        raise InvalidAreaKeyError
