from ... import config
from . import base

class Recorder(base.Recorder):
    FILEEXT = '.flv'
    def __init__(self, program, movie=True):
        """
        duration: int of millisec
        """

        super().__init__(program, movie)

        self.command = (
        "rtmpdump -r {url} --live --stop {duration} -o {output}"
        ).format_map({
            'url': config.AGQR_STREAM_URL,
            'duration': self.duration,
            'output': self.save_path + self.FILEEXT,
        }).split(' ')

