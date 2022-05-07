# fileencoding: utf-8
import datetime
import time
import sched
import multiprocessing

import pathlib
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
from .operators import (reserve, crawler, recorder as recorder_modules)
from .operators.parsers import model
from .operators.parsers.model import (Program, Service, Channel)


MONITOR_INTERVAL = 5  # sec

logger = logging.getLogger(__name__)


def create_recorder(config: userconfig.ConfigLoader, program: Program):
    r = getattr(recorder_modules, program.service)
    return r.Recorder(config, program)
def finalize(Session, program: Program):
    with start_session(Session) as session:
        _program = session.merge(program)
        session.add(_program)

        _program.is_recorded = True
        _program.is_recording = False
        _program.is_reserved = False


def record(Session, recorder: recorder_modules.base.Recorder, program: Program):
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
        finalize(Session, program)
    except Exception as e:
        logger.error("Stopped recording by Unexpected: {pid}, {err}".format(
            pid=_program.id, err=e)
        )
    finalize(Session, program)


def record_reserved(
        Session,
        config: userconfig.ConfigLoader,
        monitor_interval: int = MONITOR_INTERVAL
):
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

            r = create_recorder(config, p)


            process = multiprocessing.Process(
                target=record, args=(Session, r, p), name=p.id)
            process.start()

            msg = "Create Process: {}, {}".format(process, p.service)
            logger.debug(msg)


def monitor_reserved(
        Session,
        config: userconfig.ConfigLoader,
        log_dir: pathlib.Path,
        monitor_interval: int = MONITOR_INTERVAL
):
    logger = init_logger(log_dir.joinpath("recorder.log").resolve())
    logger.debug("Start Watching DB")

    # initialize
    sch = sched.scheduler(time.time)
    # main loop
    for dt in time_intervals(datetime.timedelta(seconds=monitor_interval)):
        sch.enterabs(datetime_to_time(dt), 1,
                     lambda: record_reserved(Session, config, monitor_interval))
        sch.run()


def create_tables(engine):
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

    config_pathes = userconfig.AircheqDir(config_dir)
    config = userconfig.TomlLoader(config_pathes)
    # mkdir config/
    #  userconfig.make_default_config_dir()

    # migrate DB
    engine = create_engine(userconfig.get_db_url(config), echo=False)
    Session = dbconfig.create_session(engine)
    dbconfig.migrate_to_head(engine, config)
    create_tables(engine)

    # create main processes
    _crawler = multiprocessing.Process(
        target=crawler.execute, args=(config_pathes, ), name='crawler')
    recorder = multiprocessing.Process(
        target=monitor_reserved,
        args=(
            Session, config, config_pathes.log_dir
        ),
        name='recorder'
    )

    _crawler.start()

    recorder.start()


if __name__ == '__main__':
    main()
