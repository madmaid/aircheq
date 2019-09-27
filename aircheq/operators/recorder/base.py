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

        FILENAME_TEMPLATE = "{channel}_{title}_{start:%Y%m%d_%H%M}"
        name = FILENAME_TEMPLATE.format_map(vars(program))
        validate = lambda s: s.translate(str.maketrans(
            # all puncts are replaced with underscore
            { punct: "_" for punct in string.punctuation + ' ' }
        ))
        
        filename = validate(name) 

        # TODO: replace os.path with pathlib
        if os.path.exists(os.path.abspath(config.RECORDED_DIR)):
            save_path = config.RECORDED_DIR
        else:
            # TODO: change default directory
            save_path = './'

        self.save_path = os.path.abspath(os.path.join(save_path, filename))

        self.duration = int((program.duration + datetime.timedelta(seconds=3)).total_seconds())

        self.id = program.id


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



