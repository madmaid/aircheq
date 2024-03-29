import sys
import logging
import subprocess
import os.path
import pathlib
import datetime
import re
import string

from ..utils import (jst_now, naive_to_JST)
from ... import userconfig


logger = logging.getLogger(__name__)


class Recorder(object):
    FILENAME_TEMPLATE = "{channel}_{title}_{start:%Y%m%d_%H%M}"

    def __init__(self, config, program, movie=False):
        self.config = config
        self.program = program

        recorded_dir = (
            pathlib.Path(
                self.config["general"]["recorded_dir"]
            ).expanduser().absolute()
        )
        if recorded_dir.exists():
            self.save_dir = recorded_dir
        else:
            self.save_dir = pathlib.Path('./').absolute()

    @staticmethod
    def validate_filepath(s: str) -> str:
        return s.translate(str.maketrans(
            # all puncts are replaced with underscore
            {punct: "_" for punct in string.punctuation + ' '}
        ))

    def record(self):
        logger.debug("Start Recording: {program.id} {program.service}".format(
            program=self.program
        ))
        try:
            self.process = subprocess.run(
                self.command,
                stdout=subprocess.DEVNULL,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error("Recording Command Error: {}".format(e))
        except:
            logger.error(
                "Unexpected Error until Recording: {}".format(sys.exc_info()[0])
            )
        else:
            logger.debug("Finish Recording: {}".format(self.program.id))

    def get_save_path(self, start):
        name = self.FILENAME_TEMPLATE.format_map({
            "channel": self.program.channel,
            "title": self.program.title,
            "start": start,
        })

        filename = self.validate_filepath(name)
        save_path = pathlib.PosixPath.joinpath(self.save_dir, filename)

        if os.path.exists(str(save_path.absolute())):
            return self.get_save_path(jst_now())

        return save_path

    def duration_from_now(self):
        dur = naive_to_JST(self.program.end) - jst_now() + \
            datetime.timedelta(seconds=10)
        return int(dur.total_seconds())

    def get_ffmpeg_cmd(self):
        DEFAULT_CMD = "ffmpeg"

        return self.config["general"]["ffmpeg"] or DEFAULT_CMD

    def get_rtmpdump_cmd(self):
        DEFAULT_CMD = "rtmpdump"
        return self.config["general"]["rtmpdump"] or DEFAULT_CMD
