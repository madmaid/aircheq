import lxml.etree
import requests

from ... import config
from . import base

class InvalidAreaKeyError(Exception):
    pass

class Recorder(base.Recorder):
    FILEEXT = '.m4a'

    def __init__(self, program):
        super().__init__(program)
        req = requests.get(config.NHK_STREAM_URLS_API)
        root = lxml.etree.fromstring(req.content)

        for areakey in root.xpath("//data/areakey"):
            if str(config.NHK_API_AREA) == areakey.text:
                url = areakey.xpath("../{}hls".format(program.channel))[0].text

                
                self.command = "ffmpeg -i {m3u8url} -to {duration} -c copy {output}".format_map({
                        "m3u8url": url,
                        "duration": self.duration,
                        'output': self.save_path + self.FILEEXT,
                    }).split(" ")

                return
        raise InvalidAreaKeyError
