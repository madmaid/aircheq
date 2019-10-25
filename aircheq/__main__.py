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


from . import (config, dbconfig)
from .dbconfig import start_session
from .operators import (reserve, crawler, utils, recorder)
from .operators.parsers import model
from .operators.parsers.model import (Program, Service, Channel)

engine = create_engine(config.GUIDE_DATABASE_URL, echo=False)
Session = dbconfig.create_session(engine)

# TODO: make this configable
MONITOR_INTERVAL = 3 #sec

def create_recorder(program):
    r = getattr(recorder, program.service)
    return r.Recorder(program)

def record(recorder, program):

    try:
        with start_session(Session) as session:
            _program = session.merge(program)
            session.add(_program)

            _program.is_reserved = False
            _program.is_recording = True
            _program.is_recorded = False

        recorder.record()

    except KeyboardInterrupt:
        logger = getLogger("aircheq-recorder")
        logger.warning("Stopped by KeyboardInterrupt: {}".format(_program.id))
    finally:
        with start_session(Session) as session:
            _program = session.merge(program)
            session.add(_program)


            _program.is_recorded = True
            _program.is_recording = False
            _program.is_reserved = False


def record_reserved():
    logger = getLogger("aircheq-recorder")
    criteria = and_(
        Program.end > utils.jst_now(),
        or_(
            and_(
                Program.is_reserved == True,
                Program.is_recorded == False,
                Program.is_recording == False,
                Program.is_manual_reserved == False
            ), 
            and_(
                Program.is_recorded == False,
                Program.is_recording == False,
                Program.is_manual_reserved == True

            ), 
        )
    )
    with start_session(Session) as session:
        reserved = session.query(Program).filter(criteria).all()

    # Recording
    for p in reserved:
        by_start = p.start - datetime.datetime.now()
        # start process before 3 secs from Program.start
        if by_start < datetime.timedelta(seconds=MONITOR_INTERVAL):


            r = create_recorder(p)

            process = multiprocessing.Process(target=record, args=(r, p), name=p.id)

            msg = "Create Process: {}, {}".format(process, p.service)
            logger.info(msg)

            process.start()

def monitor_reserved():
    # initialize
    sch = sched.scheduler(time.time)
    # main loop
    for dt in utils.time_intervals(datetime.timedelta(seconds=MONITOR_INTERVAL)):
        sch.enterabs(utils.datetime_to_time(dt), 1, record_reserved)
        sch.run()

def create_tables():
    # create tables
    program_tables = (Program, Service, Channel)

    table_exists = lambda t: engine.dialect.has_table(engine, t.__tablename__)
    new_models = [t.__table__ for t in program_tables if not table_exists(t)]
    if new_models != []: 
        model.Base.metadata.create_all(bind=engine, tables=new_models)

    if not table_exists(reserve.Rule):
        reserve.Base.metadata.create_all(bind=engine)



def main():
    dbconfig.migrate_to_head(engine)


    crawler_logger = getLogger("aircheq-crawler")
    crawler_logger.addHandler(utils.CRAWLER_LOG)
    crawler_logger.setLevel(logging.INFO)

    recorder_logger = getLogger("aircheq-recorder")
    recorder_logger.addHandler(utils.RECORDER_LOG)
    recorder_logger.setLevel(logging.INFO)

    create_tables()


    _crawler = multiprocessing.Process(target=crawler.main, name='crawler')
    _recorder = multiprocessing.Process(target=monitor_reserved, name='recorder')

    crawler_logger.info("Start Crawler")
    _crawler.start()

    recorder_logger.info("Start Watching DB")
    _recorder.start()

if __name__ == '__main__':
    main()
