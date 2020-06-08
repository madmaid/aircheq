import lxml.etree
import requests

from ... import userconfig
from . import base

config = userconfig.TomlLoader()
class InvalidAreaKeyError(Exception):
    pass

class Recorder(base.Recorder):
    FILEEXT = '.m4a'

    def __init__(self, program):
        super().__init__(program)
        req = requests.get(config["radiru"]["stream_urls_api"])
        root = lxml.etree.fromstring(req.content)

        CMD_TEMPLATE = (self.get_ffmpeg_cmd() +
                " " + "-nostdin"
                " " + "-reconnect 1 -reconnect_streamed 1" +
                " " + "-reconnect_delay_max 2" +

                " " + "-i {m3u8url} -c copy -t {duration} -f mp4 -bsf:a aac_adtstoasc file:{output}")

        for areakey in root.xpath("//data/areakey"):
            # TODO: support all area at a time
            if str(config["radiru"]["area"]) == areakey.text:
                url = areakey.xpath("../{channel}hls".format(channel=program.channel))[0].text
                self.command = CMD_TEMPLATE.format_map({
                        "m3u8url": url,
                        "duration": self.duration_from_now(),
                        'output': str(self.get_save_path(self.program.start)) + self.FILEEXT,
                    }).split(" ")
                return
        raise InvalidAreaKeyError
