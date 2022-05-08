# fileencoding=utf-8
import logging
import time
import datetime
import sched
import traceback
import typing

from requests import HTTPError
from sqlalchemy import (and_, or_)
from sqlalchemy.engine import create_engine

from . import parsers
from . import reserve
from . import utils

from .utils import jst_now
from .parsers import model
from .parsers.model import (Program, Service, Channel)
from .parsers.base import APIKeyError
from .. import userconfig
from ..dbconfig import (create_session, start_session)

logger = logging.getLogger(__name__)


def fetch_all_programs(Session, config: userconfig.ConfigLoader):
    logger.debug("Try to fetch resources")
    try:
        for module in parsers.modules:
            for program in module.Parser(config).get_programs():
                with start_session(Session) as session:
                    channel = session.query(Channel).filter_by(
                        name=program.channel).one_or_none()

                program.channel_id = channel.id
                yield program

    except HTTPError as e:
        logger.error("Fetch Error: {}".format(traceback.format_exc()))
        raise e
    except APIKeyError as e:
        logger.error("API Key Error: {}".format(traceback.format_exc()))
        raise e
    except KeyError as e:
        logger.error("JSON KeyError: {}".format(traceback.format_exc()))
        raise e
    except IndexError as e:
        logger.error("Index Error: {}".format(traceback.format_exc()))
        raise e
    except Exception as e:
        logger.error("Unknown Error: {}".format(traceback.format_exc()))
        raise e


def fetch_all_channels(Session, config: userconfig.ConfigLoader):

    for parser_name in parsers.__all__:

        with start_session(Session) as session:
            service = session.query(Service).filter_by(
                name=parser_name).one_or_none()

        module = getattr(parsers, parser_name)
        for name, name_jp in module.Parser(config).get_channels().items():
            channel = Channel()
            channel.name = name
            channel.name_jp = name_jp
            channel.service_id = service.id
            yield channel


def persist_all_channels(Session, config: userconfig.ConfigLoader):
    channels = tuple(fetch_all_channels(Session, config))

    if channels is None or channels == tuple():
        logger.warning("Skipped adding channels to DB: No resources found")
        return

    for channel in channels:
        with start_session(Session) as session:
            stored = session.query(Channel).filter_by(
                name=channel.name).one_or_none()
            if stored is None:
                session.add(channel)


def store_all_services(Session):
    # aircheq stores services to db half-manually from aircheq.operator.parser.__init__
    for parser_name in parsers.__all__:
        with start_session(Session) as session:
            service = session.query(Service).filter_by(
                name=parser_name).one_or_none()
            if service is None:
                service = Service()
                service.name = parser_name
                session.add(service)


def persist_all_programs(Session, config):
    # fetch resources
    programs = tuple(fetch_all_programs(Session, config))

    if programs is None or programs == tuple():
        logger.warning("Skipped adding programs to DB: No resources found")
        return

    now = jst_now()

    gonna_record = and_(
        Program.is_reserved == True,
        Program.start < now,
        Program.end > now
    )
    criteria = or_(Program.is_recording == True, gonna_record)

    future_programs = tuple(p for p in programs if p.start > now)
    now_onair = tuple(p for p in programs if p.start < now and p.end > now)

    def has_same(targets, p): return any(p.is_same_with(r) for r in targets)

    with start_session(Session) as session:
        recordings = session.query(Program).filter(criteria)
        non_recordings = tuple(
            p for p in now_onair if not has_same(recordings, p))

        session.add_all(non_recordings)
        session.add_all(future_programs)


def delete_unused_programs(Session):

    now = jst_now()
    future = Program.start > now
    non_recorded = and_(
        Program.end < now,
        Program.is_recorded == False,
    )
    non_recording = and_(
        Program.start < now,
        Program.end > now,
        Program.is_reserved == False,
        Program.is_recording == False,
    )

    criteria = or_(
        future,
        non_recorded,
        non_recording,
    )

    with start_session(Session) as session:
        session.query(Program).filter(criteria).delete()


def task(Session, config: userconfig.ConfigLoader):
    logger.debug("Crawl started")

    delete_unused_programs(Session)
    logger.debug("Unused programs deleted")

    # crawl
    persist_all_channels(Session, config)

    persist_all_programs(Session, config)

    logger.debug("Crawl finished")

    # reserve by rule
    reserve.reserve_all(Session)
    logger.debug("Reservation Finished ")


def task_with_retry(
        Session,
        config: userconfig.ConfigLoader,
        max_count=5,
        retry_interval=datetime.timedelta(seconds=300)
):
    sch = sched.scheduler(time.time)
    for dt, count in zip(utils.time_intervals(retry_interval, first_time=jst_now()), range(0, max_count)):
        sch.enterabs(utils.datetime_to_time(dt), 1, lambda: task(Session, config))
        try:
            sch.run()
        except APIKeyError as e:
            logger.error("abort.")
            return
        except Exception as e:
            logger.warning("retry: {}".format(traceback.format_exc()))
            continue    # retry
        else:
            logger.debug("crawl done.")
            return


def execute(config_pathes: userconfig.AircheqDir):
    #  config_pathes = userconfig.AircheqDir()
    config = userconfig.TomlLoader(config_pathes)

    engine = create_engine(userconfig.get_db_url(config), echo=False)
    Session = create_session(engine)

    # initialize
    utils.init_logger(config_pathes.log_dir.joinpath("crawler.log").resolve())
    store_all_services(Session)
    task_with_retry(Session, config)  # crawl at launch

    # launch scheduler
    sch = sched.scheduler(time.time)
    upnext = jst_now().replace(minute=10)
    if upnext < jst_now():
        upnext += datetime.timedelta(hours=1)

    for dt in utils.time_intervals(datetime.timedelta(hours=1), first_time=upnext):
        sch.enterabs(
                utils.datetime_to_time(dt),
                1,
                lambda: task_with_retry(Session, config)
        )
        logger.debug("Next Crawl is scheduled at {}".format(dt))
        sch.run()
