
from . import base

class Recorder(base.Recorder):
    URL = "rtmp://fms-base1.mitene.ad.jp/agqr/aandg22"
    def __init__(self, program, movie=True):
        """
        duration: int of millisec
        """

        super().__init__(program, movie)

        self.command = (
        "rtmpdump -r {url} --live --stop {duration} -o {output}"
        ).format_map({
            'url': self.URL,
            'duration': self.duration,
            'output': self.save_path,
        }).split(' ')

