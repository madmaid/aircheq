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

        CMD_TEMPLATE = "ffmpeg -i {m3u8url} -c copy -t {duration} -f mp4 -bsf:a aac_adtstoasc file:{output}"
        for areakey in root.xpath("//data/areakey"):
            # TODO: support all area at a time
            if str(config.NHK_API_AREA) == areakey.text:
                url = areakey.xpath("../{channel}hls".format(channel=program.channel))[0].text
                self.command = CMD_TEMPLATE.format_map({
                        "m3u8url": url,
                        "duration": self.duration_from_now(),
                        'output': str(self.get_save_path(self.program.start)) + self.FILEEXT,
                    }).split(" ")
                return
        raise InvalidAreaKeyError
