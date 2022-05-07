import lxml.etree
import requests

from ... import userconfig
from . import base

class InvalidAreaKeyError(Exception):
    pass

class Recorder(base.Recorder):
    FILEEXT = '.m4a'

    def __init__(self, config, program):
        super().__init__(config, program)
        req = requests.get(self.config["radiru"]["stream_xml_url"])
        root = lxml.etree.fromstring(req.content)

        cmd_template = (self.get_ffmpeg_cmd() +
                " " + "-nostdin"
                " " + "-reconnect 1 -reconnect_streamed 1" +
                " " + "-reconnect_delay_max 2" +

                " " + "-i {m3u8url} -c copy -t {duration} -f mp4 -bsf:a aac_adtstoasc file:{output}")

        for areakey in root.xpath("//data/areakey"):
            # TODO: support all area at a time
            if str(self.config["radiru"]["area"]) == areakey.text:
                url = areakey.xpath("../{channel}hls".format(channel=program.channel))[0].text
                self.command = cmd_template.format_map({
                        "m3u8url": url,
                        "duration": self.duration_from_now(),
                        'output': str(self.get_save_path(self.program.start)) + self.FILEEXT,
                    }).split(" ")
                return
        raise InvalidAreaKeyError
