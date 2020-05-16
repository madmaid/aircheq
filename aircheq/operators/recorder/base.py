import sys
import logging
import subprocess
import os.path
import pathlib
import datetime
import re
import string

from ..utils import (jst_now, naive_to_JST)
from ... import config

class Recorder(object):
    def __init__(self, program, movie=False):
        self.logger = logging.getLogger("aircheq-recorder")

        self.FILENAME_TEMPLATE = "{channel}_{title}_{start:%Y%m%d_%H%M}"
        self.program = program

        # TODO: replace os.path with pathlib
        if os.path.exists(os.path.abspath(config.RECORDED_DIR)):
            save_dir = config.RECORDED_DIR
        else:
            # TODO: change default directory
            save_dir = './'

        self.save_dir = pathlib.PosixPath(save_dir).absolute()


    @staticmethod
    def validate_filepath(s):
        return s.translate(str.maketrans(
                    # all puncts are replaced with underscore
                    { punct: "_" for punct in string.punctuation + ' ' }
                ))



    def record(self):
        #TODO: log (incl. stdout)
        self.logger.info("Start Recording: {id}".format(id = self.program.id))
        try:
            self.process = subprocess.run(
                    self.command,
                    stdout=subprocess.DEVNULL,
                    check=True)

        except subprocess.CalledProcessError as e:
            self.logger.error("Recording Command Error: {}".format(e))
        except:
            self.logger.error("Unexpected Error until Recording: {}".format(sys.exc_info()[0]))
        else:
            self.logger.info("Finish Recording: {}".format(self.program.id))

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
        dur = naive_to_JST(self.program.end) - jst_now() + datetime.timedelta(seconds=10)
        return int(dur.total_seconds())


