# fileencoding=utf-8
import logging
import time
import datetime
import sched

import sqlalchemy.exc

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from . import parsers
from . import reserve
from . import utils
from .parsers import model
from .parsers.model import Program
from .. import config

engine = create_engine(config.GUIDE_DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

def fetch_all():
    for parser in parsers.modules:
        for program in parser.get_programs():
            yield program

def task():
    logger = logging.getLogger("aircheq-crawler")
    logger.info("Start Crawl")
    del_session = Session(autocommit=True)
    with del_session.begin():

        del_session.query(Program).delete()

    del_session.close()

    # try to fetch resources
    interval = datetime.timedelta(seconds=300) # 5min
    now = datetime.datetime.now
    for dt in utils.time_intervals(interval, first_time=now()):
        programs = list(fetch_all())    # in order to prevent too long transaction
        if programs == []:
            logger.warning("Programs not found")
        else:
            break

    session = Session(autocommit=True)
    with session.begin():

        session.add_all(programs)

    session.close()
    logger.info("Finished Crawl")
    reserve.reserve_all(Session)

def main():
    logger = logging.getLogger("aircheq-crawler")
    sch = sched.scheduler(time.time)
    task() # crawl at launch

    ESTIMATED_TIME = datetime.time(5, 10)
    combine = datetime.datetime.combine
    if datetime.datetime.now() < combine(datetime.date.today(), ESTIMATED_TIME):
        estimated_date = datetime.date.today()
    else:
        estimated_date = utils.get_coming_weekday(0)

    # Monday 5AM
    first_time = combine(estimated_date, ESTIMATED_TIME) 

    for dt in utils.time_intervals(datetime.timedelta(days=1), first_time=first_time):
        sch.enterabs(utils.datetime_to_time(dt), 1, task)
        logger.info("Next Crawl is scheduled at {}".format(dt))
        sch.run()
