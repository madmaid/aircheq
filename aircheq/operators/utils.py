# coding: utf-8
import time
import datetime
import logging
import collections
import pathlib

import pytz


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
    first_time = first_time or jst_now()

    yield first_time

    exec_time = first_time
    while True:
        exec_time += timedelta
        yield exec_time

def naive_to_JST(dt):
    tz_tokyo = pytz.timezone("Asia/Tokyo")
    if getattr(dt, "tzinfo", None) != tz_tokyo:
        return tz_tokyo.localize(dt)
    return dt

def jst_now():
    return datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))

def init_logger(logpath):
    LOG_FORMAT = logging.Formatter("{asctime} - {levelname:8s} - {message}", style="{")
    logger = logging.getLogger("aircheq")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(logpath)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(LOG_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(LOG_FORMAT)
    console.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    # logger.addHandler(console)

    return logger

