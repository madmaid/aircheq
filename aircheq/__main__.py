# fileencoding: utf-8
import datetime
import time
import sched
import multiprocessing

import logging
from logging import getLogger


import sqlalchemy.exc

from sqlalchemy import or_, and_
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from .operators import reserve
from .operators import crawler
from .operators import utils
from .operators import recorder
from . import config, dbconfig
from .operators.parsers import model
from .operators.parsers.model import Program 

engine = create_engine(config.GUIDE_DATABASE_URL, echo=False)
Session = dbconfig.create_session(engine)

# TODO: make this configable
MONITOR_INTERVAL = 3 #sec

def create_recorder(program):
    r = getattr(recorder, program.service)
    return r.Recorder(program)

def task():
    logger = getLogger("aircheq-recorder")
    session = Session(autocommit=True)
    with session.begin():
        criteria = and_(
                Program.is_reserved == True,
                Program.end > datetime.datetime.now(),
                Program.is_recorded != True)

        # Recording
        for p in session.query(Program).filter(criteria):
            by_start = p.start - datetime.datetime.now()
            # start process before 3 secs from Program.start
            if by_start < datetime.timedelta(seconds=MONITOR_INTERVAL):

                p.is_recorded = True
                r = create_recorder(p)

                process = multiprocessing.Process(target=r.record, name=p.id)

                msg = "Create Process: {}, {}".format(process, p.service)
                logger.info(msg)

                process.start()
    session.close()

def record_reserved():
    # initialize
    sch = sched.scheduler(time.time)
    # main loop
    for dt in utils.time_intervals(datetime.timedelta(seconds=MONITOR_INTERVAL)):
        sch.enterabs(utils.datetime_to_time(dt), 1, task)
        sch.run()

if __name__ == '__main__':
    crawler_logger = getLogger("aircheq-crawler")
    crawler_logger.addHandler(utils.CRAWLER_LOG)
    crawler_logger.setLevel(logging.INFO)

    recorder_logger = getLogger("aircheq-recorder")
    recorder_logger.addHandler(utils.RECORDER_LOG)
    recorder_logger.setLevel(logging.INFO)

    # create tables
    if not engine.dialect.has_table(engine, Program.__tablename__):
        model.Base.metadata.create_all(bind=engine)
    if not engine.dialect.has_table(engine, reserve.Rule.__tablename__):
        reserve.Base.metadata.create_all(bind=engine)

    _crawler = multiprocessing.Process(target=crawler.main, name='crawler')
    _recorder = multiprocessing.Process(target=record_reserved, name='recorder')

    crawler_logger.info("Start Crawler")
    _crawler.start()

    recorder_logger.info("Start Watching DB")
    _recorder.start()
