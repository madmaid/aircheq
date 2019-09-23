# fileencoding=utf-8
import logging
import time
import datetime
import sched
import traceback


from requests import HTTPError
from sqlalchemy import and_
from sqlalchemy.engine import create_engine

from . import parsers
from . import reserve
from . import utils

from .parsers import model
from .parsers.model import (Program, Service, Channel, )
from .. import config, dbconfig

engine = create_engine(config.GUIDE_DATABASE_URL, echo=False)
Session = dbconfig.create_session(engine)
logger = logging.getLogger("aircheq-crawler")


def fetch_with_error_collection(fetch_generator):
    def inner():
        logger.info("Try to fetch resources")
        try:
            yield from fetch_generator()    # pre-fetch to prevent too long transaction
        except HTTPError as e:
            logger.warning("Fetch Error: {}".format(traceback.format_exc()))
            raise e
        except KeyError as e:
            logger.warning("JSON KeyError: {}".format(traceback.format_exc()))
            raise e
        except IndexError as e:
            logger.warning("Index Error: {}".format(traceback.format_exc()))
            raise e
        except Exception as e:
            logger.warning("Unknown Error: {}".format(traceback.format_exc()))
            raise e
    return inner

@fetch_with_error_collection
def fetch_all_programs():
    for parser in parsers.modules:
        for program in parser.get_programs():
            session = Session(autocommit=True)

            with session.begin():
                channel = session.query(Channel).filter_by(name=program.channel).one()
            session.close()

            program.channel_id = channel.id
            yield program


def fetch_all_channels():

    for parser_name in parsers.__all__:

        session = Session(autocommit=True)
        with session.begin():
            service = session.query(Service).filter_by(name=parser_name).one()
        session.close()

        parser = getattr(parsers, parser_name)
        for name, name_jp in parser.get_channels().items():
            channel = Channel()
            channel.name = name
            channel.name_jp = name_jp
            channel.service_id = service.id
            yield channel

def persist_all_channels():
    channels = tuple(fetch_all_channels())

    if channels is None or channels == tuple():
        logger.warning("Skipped adding channels to DB: No resources found")
        return

    for channel in channels:
        session = Session(autocommit=True)
        with session.begin():
            stored = session.query(Channel).filter_by(name=channel.name).one_or_none()
            if stored is None:
                session.add(channel)
        session.close()


def store_all_services():
    # aircheq stores services to db half-manually from aircheq.operator.parser.__init__
    for parser_name in parsers.__all__:
        session = Session(autocommit=True)
        with session.begin():
            service = session.query(Service).filter_by(name=parser_name).one_or_none()
            if service is None:
                service = Service()
                service.name = parser_name
                session.add(service)
        session.close()


def persist_all_programs():
    # fetch resources
    programs = tuple(fetch_all_programs())

    if programs is None or programs == tuple():
        logger.warning("Skipped adding programs to DB: No resources found")
        return

    inserted = tuple(p for p in programs if p.end > utils.jst_now())
    session = Session(autocommit=True)
    with session.begin():

        session.add_all(inserted)

    session.close()

def delete_unused_programs():
    del_session = Session(autocommit=True)
    with del_session.begin():

        del_session.query(Program).filter_by(is_recorded=False).delete()

    del_session.close()

def task():
    logger.info("Crawl started")

    delete_unused_programs()
    logger.info("Unused programs deleted")

    # crawl
    persist_all_channels()
    
    persist_all_programs()

    logger.info("Crawl finished")

    # reserve by rule
    reserve.reserve_all()
    logger.info("Reservation Finished ")

def task_with_retry(max_count=5, retry_interval=datetime.timedelta(seconds=300)):
    now = utils.jst_now
    sch = sched.scheduler(time.time)
    for dt, count in zip(utils.time_intervals(retry_interval, first_time=now()), range(0, max_count)):
        sch.enterabs(utils.datetime_to_time(dt), 1, task)
        try:
            sch.run()
        except Exception as e:
            logger.warning("retry: {}".format(traceback.format_exc()))
            continue    # retry
        else:
            return


def main():
    # initialize
    store_all_services()
    task_with_retry() # crawl at launch

    # launch scheduler
    sch = sched.scheduler(time.time)
    now = utils.jst_now
    upnext =  now().replace(minute=10) 
    if upnext < now():
        upnext += datetime.timedelta(hours=1)

    for dt in utils.time_intervals(datetime.timedelta(hours=1), first_time=upnext):
        sch.enterabs(utils.datetime_to_time(dt), 1, task_with_retry)
        logger.info("Next Crawl is scheduled at {}".format(dt))
        sch.run()
