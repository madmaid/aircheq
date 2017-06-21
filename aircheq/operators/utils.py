# coding: utf-8
import time
import datetime
import logging
import collections
import pathlib

from .. import config

LOG_FORMAT = logging.Formatter("{asctime} - {levelname:8s} - {message}", style="{")

CRAWLER_LOG = logging.FileHandler(config.LOG_DIR.joinpath("crawler.log"))
CRAWLER_LOG.setFormatter(LOG_FORMAT)

RECORDER_LOG = logging.FileHandler(config.LOG_DIR.joinpath("recorder.log"))
RECORDER_LOG.setFormatter(LOG_FORMAT)

KANJI_WEEKDAYS = ['月', '火', '水', '木', '金', '土', '日']

def weekday_to_date(kanji_weekday, start_day=None):
    """
    KANJI_WEEKDAYS -> datetime.date in 7days from start_day.
    if start_day is not specified, start from datetime.now()
    """
    start_day = start_day or datetime.datetime.now()

    weekdays = dict(zip(KANJI_WEEKDAYS, range(7)))
    dates = [ start_day + datetime.timedelta(days=days) for days in weekdays.values() ]
    for date in dates:
        if date.weekday() == weekdays[kanji_weekday]:
            return date

def datetime_to_time(dt):
    return time.mktime(dt.timetuple())

def get_coming_weekday(wday_num):
    """
    wday_num -> datetime object coming weekday taken as argument from today.
    """
    weekdays = collections.deque(range(7))

    today = datetime.date.today()
    if today.weekday() == wday_num:
        return today + datetime.timedelta(days=7)

    weekdays.rotate(-today.weekday())
    return today + datetime.timedelta(days=weekdays.index(wday_num))

def time_intervals(timedelta, first_time=None):
    first_time = first_time or datetime.datetime.now()

    yield first_time

    exec_time = first_time
    while True:
        exec_time += timedelta
        yield exec_time
