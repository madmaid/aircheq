from ... import userconfig
from . import base

config = userconfig.TomlLoader()
class Recorder(base.Recorder):
    def __init__(self, program, movie=True):
        """
        duration: int of millisec
        """

        super().__init__(program, movie)
        stream_url = config["agqr"]["stream_url"]

        rtmp_template = "rtmpdump -r {url} --live --stop {duration} -o {output}"
        hls_template = "ffmpeg -i {url} -c copy -t {duration} {output}"

        if stream_url.split(".")[-1] == "m3u8":
            cmd_template = hls_template 
            file_ext = ".m2ts"
        else:
            cmd_template = rtmp_template
            file_ext = "flv"
        self.command = cmd_template.format_map({
            'url': stream_url,
            'duration': self.duration_from_now(),
            'output': str(self.get_save_path(self.program.start)) + file_ext,
        }).split(' ')

