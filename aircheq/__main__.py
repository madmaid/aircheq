# fileencoding: utf-8
import datetime
import time
import sched
import multiprocessing

import logging


import sqlalchemy.exc

from sqlalchemy import or_, and_, inspect
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker


from . import (userconfig, dbconfig)
from .args import create_argparser
from .dbconfig import start_session
from .operators import (reserve, crawler, recorder)
from .operators.utils import (jst_now, time_intervals, init_logger, datetime_to_time)
from .operators.parsers import model
from .operators.parsers.model import (Program, Service, Channel)

engine = create_engine(userconfig.get_db_url(), echo=False)
Session = dbconfig.create_session(engine)

MONITOR_INTERVAL = 5 #sec

logger = logging.getLogger(__name__)

def create_recorder(program):
    r = getattr(recorder, program.service)
    return r.Recorder(program)

def finalize(program):
    with start_session(Session) as session:
        _program = session.merge(program)
        session.add(_program)

        _program.is_recorded = True
        _program.is_recording = False
        _program.is_reserved = False


def record(recorder, program):
    with start_session(Session) as session:
        _program = session.merge(program)
        session.add(_program)

        _program.is_reserved = False
        _program.is_recording = True
        _program.is_recorded = False

    try:
        recorder.record()

    except KeyboardInterrupt:
        logger.warning("Stopped recording by KeyboardInterrupt: {}".format(_program.id))
        finalize(program)
    except Exception as e:
        logger.error("Stopped recording by Unexpected: {pid}, {err}".format(
            pid=_program.id, err=e)
        )
    finalize(program)


def record_reserved(monitor_interval=None):
    if monitor_interval is None:
        monitor_interval = MONITOR_INTERVAL
    criteria = and_(
        Program.end > jst_now(),
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
        # start process before 5 secs from Program.start
        if by_start < datetime.timedelta(seconds=monitor_interval):


            r = create_recorder(p)

            process = multiprocessing.Process(target=record, args=(r, p), name=p.id)
            process.start()

            msg = "Create Process: {}, {}".format(process, p.service)
            logger.debug(msg)


def monitor_reserved(monitor_interval=None):
    logger = init_logger(userconfig.LOG_DIR.joinpath("recorder.log").resolve())
    logger.debug("Start Watching DB")

    if monitor_interval is None:
        monitor_interval = MONITOR_INTERVAL
    # initialize
    sch = sched.scheduler(time.time)
    # main loop
    for dt in time_intervals(datetime.timedelta(seconds=monitor_interval)):
        sch.enterabs(datetime_to_time(dt), 1, record_reserved)
        sch.run()

def create_tables():
    program_tables = (Program, Service, Channel)

    table_exists = lambda table_name: inspect(engine).has_table(table_name)
    new_models = [t.__table__ for t in program_tables if not
            table_exists(t.__tablename__)]
    if new_models != []: 
        model.Base.metadata.create_all(bind=engine, tables=new_models)

    if not table_exists(reserve.Rule.__tablename__):
        reserve.Base.metadata.create_all(bind=engine)



def main():
    argparser = create_argparser()
    args = argparser.parse_args()

    if args.config_dir is not None:
        config_dir = args.config_dir.expanduser()
    else:
        config_dir = userconfig.DEFAULT_CONFIG_DIR
    # mkdir config/
    userconfig.make_default_config_dir()

    # migrate DB
    dbconfig.migrate_to_head(engine)
    create_tables()


    # create main processes
    _crawler = multiprocessing.Process(target=crawler.main, name='crawler')
    _recorder = multiprocessing.Process(target=monitor_reserved, name='recorder')

    _crawler.start()

    _recorder.start()

if __name__ == '__main__':
    main()
