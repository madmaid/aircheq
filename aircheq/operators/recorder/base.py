import sys
import logging
import subprocess
import os.path
import datetime
import re
import string

from ... import config

class Recorder(object):
    def __init__(self, program, movie=False):
        self.logger = logging.getLogger("aircheq-recorder")

        # TODO: considering filename format from config
        # name_format = config.FIMENAME_FORMAT

        formatter = "{channel}_{title}_{start:%Y%m%d_%H%M}"
        name = formatter.format_map(vars(program))
        validate = (lambda s:
            # all puncts are replaced with underscore
            s.translate( {punct: "_" for punct in string.punctuation} ).replace(" ", "_")
        )
        valid_name = validate(name) 
        filename = valid_name + ".flv"


        # TODO: replace os.path with pathlib
        if os.path.exists(os.path.abspath(config.SAVE_DIR)):
            save_path = config.SAVE_DIR
        else:
            # TODO: change default directory
            save_path = './'

        self.save_path = os.path.abspath(os.path.join(save_path, filename))

        self.duration = int((program.duration + datetime.timedelta(seconds=3)).total_seconds())

        self.id = program.id
        self.movie = movie


    def record(self):
        #TODO: log (incl. stdout)
        self.logger.info("Start Recording: {id}".format(id = self.id))
        try:
            self.process = subprocess.run(
                    self.command,
                    stdout=subprocess.DEVNULL,
                    check=True)

        except subprocess.CalledProcessError as e:
            self.logger.error("Recording Command Error: {}".format(e))
        except:
            self.logger.error("Unexpected Error: {}".format(sys.exc_info()[0]))
        else:
            self.logger.info("Finish Recording: {}".format(self.id))

    def detect_audio_codec(self):
        ffmpeg_cmd = "ffmpeg -i {save_path}".format(save_path=self.save_path).split(" ")

        ffmpeg_result = subprocess.run(ffmpeg_cmd, stderr=subprocess.STDOUT)
        for line in ffmpeg_result.stderr.readlines():
            target = "Audio:\s+"
            search = re.search(target, line)
            if search is not None:
                return re.split(target, line)[-1]

    def split(self):
        self.audio_codec = self.detect_audio_codec()
        self.split_command = "ffmpeg -i {input} -acodec copy -map 0:1 {output}".format_map({
                "input": self.save_path,
                "output": self.save_path + '.' + self.audio_codec
            }).split(' ')
        self.ffmpeg = subprocess.check_call(self.split_command)
